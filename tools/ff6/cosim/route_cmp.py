"""FF6 co-sim A-vs-B over a route with a dead-stack rule (tools/ff6/cosim/cosim.sh route).

Steps A and B one frame at a time through the snesrecomp co-sim protocol (snes_cosim.py as a
library) and compares the WRAM hash at every frame cut. On a mismatch both sides dump WRAM
and each differing offset is classified:
  dead  inside the stack area $1508-$15FF and at or below the stack pointer of both sides.
        FF6 sets S = $15FF once at reset (field/reset.asm); $1500-$1507 hold the NMI and IRQ
        jumps. A byte at or below S is residue of an earlier push (a call, an interrupt
        frame, a handler's php) that the next push overwrites before anything reads it.
  beam  $0630-$0632: after its work the field loop latches the beam and stores the H and V
        counters and the highest V of the last 256 frames (field/reset.asm, a CPU load
        gauge). No code reads them for a decision; they show where in the frame the work
        ended. The V difference A minus B is counted per checkpoint. Also their copy at
        $F230-$F232: PushMode7Vars (world/init.asm) saves $0520-$0BFF to $7EF120 when the
        world module starts and PopMode7Vars copies it back.
  live  everything else.
A checkpoint with dead or beam differences only counts as equal. A run of checkpoints with live
differences is logged as TRANSIENT when it ends within --grace checkpoints; otherwise the
run halts with a report (differing ranges with both values, CPU of both sides).

  python route_cmp.py <snes_cosim dir> --a-cmd CMD --b-cmd CMD [--a-env K=V ...]
         [--b-env K=V ...] --max N [--grace G] [--dump-dir DIR]

Exit code 0 when no live divergence outlasts the grace, 1 when the run halts on one.
"""
import argparse
import os
import sys
import time

STACK_LO, STACK_HI = 0x1508, 0x15FF
BEAM = set(range(0x0630, 0x0633)) | set(range(0xF230, 0xF233))


def ranges(offs, gap=4):
    out = []
    for o in offs:
        if out and o - out[-1][1] <= gap:
            out[-1][1] = o
        else:
            out.append([o, o])
    return out


def diff_offsets(da, db):
    n = min(len(da), len(db))
    offs = []
    for base in range(0, n, 256):
        end = min(base + 256, n)
        if da[base:end] != db[base:end]:
            offs.extend(i for i in range(base, end) if da[i] != db[i])
    return offs


def fmt(offs, da, db, limit=12):
    rs = ranges(offs)
    parts = []
    for lo, hi in rs[:limit]:
        if hi - lo < 8:
            parts.append(f"{lo:05X}-{hi:05X} A={da[lo:hi + 1].hex()} B={db[lo:hi + 1].hex()}")
        else:
            parts.append(f"{lo:05X}-{hi:05X} ({hi - lo + 1} bytes)")
    if len(rs) > limit:
        parts.append(f"+{len(rs) - limit} more ranges")
    return "; ".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cosim_dir", help="directory of snesrecomp/tools/snes_cosim.py")
    ap.add_argument("--a-cmd", required=True)
    ap.add_argument("--b-cmd", required=True)
    ap.add_argument("--a-env", action="append", default=[])
    ap.add_argument("--b-env", action="append", default=[])
    ap.add_argument("--max", type=int, required=True, help="checkpoints (frames)")
    ap.add_argument("--grace", type=int, default=120,
                    help="longest run of live differences that still counts as transient")
    ap.add_argument("--dump-dir", default=".")
    ap.add_argument("--watch", default="",
                    help="comma list of WRAM offsets printed for A and B at every checkpoint "
                    "of --watch-range, with both CPUs (diagnostics)")
    ap.add_argument("--watch-range", default="", help="LO-HI checkpoints for --watch")
    args = ap.parse_args()
    watch = [int(x, 0) for x in args.watch.split(",") if x]
    w_lo, w_hi = (int(x) for x in args.watch_range.split("-")) if args.watch_range else (0, -1)

    sys.path.insert(0, args.cosim_dir)
    import snes_cosim as sc

    os.makedirs(args.dump_dir, exist_ok=True)
    path = {s: os.path.join(args.dump_dir, f"route_cmp_{s}.bin") for s in "AB"}
    a = sc.Side("A", 4500, args.a_cmd, 1, 0, args.a_env)
    b = sc.Side("B", 4501, args.b_cmd, 1, 0, args.b_env)
    a.connect()
    b.connect()
    print(f"connected: A:4500 B:4501, WRAM with the dead-stack rule "
          f"(${STACK_LO:04X}-${STACK_HI:04X} at or below S), grace {args.grace}", flush=True)

    t0 = time.time()
    live_start = None
    transients = []
    dead_cps = 0
    dead_seen = set()
    beam_cps = 0
    beam_dv = {}

    def tally():
        hist = ", ".join(f"{dv:+d}: {n}" for dv, n in sorted(beam_dv.items()))
        return (f"{len(transients)} transient(s)"
                + (f" at {[c for c, _ in transients]}" if transients else "")
                + f"; {dead_cps} checkpoint(s) with dead-stack or beam differences only"
                + f"; beam bytes differ at {beam_cps} checkpoint(s), V A-B {{{hist}}}")

    def snapshot():
        cpu = {s: side.cmd("cpu") for s, side in (("A", a), ("B", b))}
        for s, side in (("A", a), ("B", b)):
            r = side.cmd(f"dumpram {sc._host_path(path[s])}")
            if not r.startswith("ok"):
                sc.die(f"{s}: dumpram failed: {r!r}")
        da = open(path["A"], "rb").read()
        db = open(path["B"], "rb").read()
        return cpu, da, db

    for i in range(1, args.max + 1):
        ra, rb = sc.kv(a.cmd("step 1")), sc.kv(b.cmd("step 1"))
        if "cp" not in ra or "cp" not in rb:
            sc.die(f"unparseable step reply A={ra} B={rb}")
        cp = int(ra["cp"])
        if cp != int(rb["cp"]):
            sc.die(f"cp index skew: A={ra['cp']} B={rb['cp']}")
        sa, sb = sc.kv(a.cmd("sub")), sc.kv(b.cmd("sub"))
        if "ram" not in sa or "ram" not in sb:
            sc.die(f"sub without ram: A={sa} B={sb}")
        live = False
        if watch and w_lo <= cp <= w_hi:
            cpu, da, db = snapshot()
            vals = " ".join(f"{o:04X}={da[o]:02x}/{db[o]:02x}" for o in watch)
            print(f"  watch cp {cp}: {vals}\n    A {cpu['A']}\n    B {cpu['B']}", flush=True)
        if sa["ram"] != sb["ram"]:
            cpu, da, db = snapshot()
            s_a = int(sc.kv(cpu["A"]).get("S", "0"), 16)
            s_b = int(sc.kv(cpu["B"]).get("S", "0"), 16)
            top = min(s_a, s_b, STACK_HI)
            offs = diff_offsets(da, db)
            dead_offs = [o for o in offs if STACK_LO <= o <= top]
            beam_offs = [o for o in offs if o in BEAM]
            live_offs = [o for o in offs if not STACK_LO <= o <= top and o not in BEAM]
            if beam_offs:
                beam_cps += 1
                dv = da[0x0631] - db[0x0631]
                beam_dv[dv] = beam_dv.get(dv, 0) + 1
            if live_offs:
                live = True
                if live_start is None:
                    live_start = cp
                    print(f"  LIVE at cp {cp}: {fmt(live_offs, da, db)}", flush=True)
                elif cp - live_start >= args.grace:
                    print(f"\n=== LIVE DIVERGENCE from cp {live_start}, still live at cp {cp} "
                          f"(grace {args.grace}) ===")
                    print(f"  live: {fmt(live_offs, da, db, 40)}")
                    if dead_offs:
                        print(f"  dead stack: {fmt(dead_offs, da, db)}")
                    print(f"  A cpu: {cpu['A']}")
                    print(f"  B cpu: {cpu['B']}")
                    print(f"  A sub: cyc={sa.get('cyc')} mcyc={sa.get('mcyc')}")
                    print(f"  B sub: cyc={sb.get('cyc')} mcyc={sb.get('mcyc')}")
                    print(f"\nhalted at cp {cp} after {time.time() - t0:.0f}s; {tally()}")
                    a.close()
                    b.close()
                    return 1
            else:
                dead_cps += 1
                key = (tuple(tuple(r) for r in ranges(dead_offs)), bool(beam_offs))
                if key not in dead_seen and len(dead_seen) < 30:
                    dead_seen.add(key)
                    print(f"  dead stack at cp {cp} (S A={s_a:04X} B={s_b:04X}): "
                          f"{fmt(dead_offs, da, db) or '-'}"
                          + (f"; beam {fmt(beam_offs, da, db)}" if beam_offs else ""),
                          flush=True)
        if not live and live_start is not None:
            transients.append((live_start, cp - live_start))
            print(f"  TRANSIENT live divergence cp {live_start}-{cp - 1} "
                  f"({cp - live_start} checkpoint(s))", flush=True)
            live_start = None
        if i % 1000 == 0:
            print(f"  cp {cp} ({time.time() - t0:.0f}s)", flush=True)

    if live_start is not None:
        print(f"live divergence open since cp {live_start} at the last checkpoint; {tally()}")
        a.close()
        b.close()
        return 1
    print(f"no live divergence beyond grace in {args.max} checkpoints "
          f"({time.time() - t0:.0f}s); {tally()}")
    a.close()
    b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
