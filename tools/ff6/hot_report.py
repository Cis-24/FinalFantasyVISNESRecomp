#!/usr/bin/env python3
"""Heisse Funktionen: wo der Interpreter in den Routen wirklich laeuft (PLAN Phase 6, COVERAGE_FEEDBACK.md).

Aufruf: python tools/ff6/hot_report.py <lauf-verzeichnis>... [--top N] [--json DATEI]

Liest aus jedem Lauf die `costs` des Coverage-Captures (exklusive Instruktionen und Gastzyklen je PC, M/X)
und ordnet sie ueber recomp/symbols.toml Funktionen zu. WRAM-Code (7E/7F) wird getrennt gezaehlt, er bleibt
per Konstruktion im Interpreter. Fuer jede ROM-Funktion nennt der Bericht den Stand im Programm-Manifest
(`src/gen/program_manifest.json`): die gesehene Eintrittsvariante und, falls sie nicht AOT ist, den Grund.
Der Bericht aendert nichts; er ist die Arbeitsliste fuer `emit = true`.
"""
import argparse, bisect, glob, json, os, sys, tomllib

GR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SYMBOLS = os.path.join(GR, "recomp", "symbols.toml")
MANIFEST = os.path.join(GR, "src", "gen", "program_manifest.json")
MAX_SPAN = 0x2000


def load_symbols():
    with open(SYMBOLS, "rb") as f:
        funcs = tomllib.load(f).get("func", [])
    syms = {}
    for x in funcs:
        syms[(int(x["bank"]) << 16) | int(x["addr"], 16)] = (x["name"], x.get("emit", True))
    keys = sorted(syms)
    return syms, keys


def load_captures(run_dir):
    # Capture-Name endet auf _s<Nummer>; ohne die Ziffer passen auch Dump-Tags (back_south.info.json)
    found = sorted(glob.glob(os.path.join(run_dir, "*_s[0-9]*.json")))
    if not found:
        sys.exit(f"hot_report: kein Capture in {run_dir}")
    # Zeilen sind je Capture kumulativ; je Lauf zaehlt die letzte Session.
    with open(found[-1]) as f:
        return json.load(f), os.path.basename(found[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--json")
    a = ap.parse_args()
    syms, keys = load_symbols()

    def owner(pc):
        i = bisect.bisect_right(keys, pc) - 1
        return keys[i] if i >= 0 and keys[i] >> 16 == pc >> 16 else None

    per_func = {}
    totals = {"rom": [0, 0], "ram": [0, 0]}
    per_run = {}
    ram_pc = {}
    for run in a.runs:
        cap, name = load_captures(run)
        run_key = os.path.basename(os.path.normpath(run))
        rt = per_run.setdefault(run_key, {"rom": 0, "ram": 0})
        for c in cap["costs"]:
            if c.get("record_kind") != "instruction":
                continue
            pc = int(c["target_pc24"], 16)
            n, cyc = c["interpreted_instructions"], c["guest_cycles"]
            if 0x7E0000 <= pc < 0x800000:
                totals["ram"][0] += n; totals["ram"][1] += cyc; rt["ram"] += cyc
                ram_pc[pc] = ram_pc.get(pc, 0) + cyc
                continue
            totals["rom"][0] += n; totals["rom"][1] += cyc; rt["rom"] += cyc
            own = owner(pc)
            e = per_func.setdefault(own, {"insns": 0, "cycles": 0, "mx": {}, "runs": {}, "hot_pc": {}})
            e["insns"] += n
            e["cycles"] += cyc
            e["mx"][c["entry_mx"]] = e["mx"].get(c["entry_mx"], 0) + cyc
            e["runs"][run_key] = e["runs"].get(run_key, 0) + cyc
            e["hot_pc"][pc] = e["hot_pc"].get(pc, 0) + cyc

    total_cyc = totals["rom"][1] + totals["ram"][1]
    print(f"Laeufe: {', '.join(os.path.basename(os.path.normpath(r)) for r in a.runs)}")
    print(f"Interpretierte Zyklen: {total_cyc}  ROM {totals['rom'][1]} ({100*totals['rom'][1]/max(total_cyc,1):.1f} %)"
          f"  WRAM {totals['ram'][1]} ({100*totals['ram'][1]/max(total_cyc,1):.1f} %)")
    for k, v in per_run.items():
        s = v["rom"] + v["ram"]
        print(f"  {k}: ROM {v['rom']} ({100*v['rom']/max(s,1):.1f} %)  WRAM {v['ram']} ({100*v['ram']/max(s,1):.1f} %)")

    nodes = {}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            nodes = json.load(f)["nodes"]

    # Ein PC gilt als "AOT vorhanden", wenn der kleinste AOT-Knoten ihn einschliesst. Die Spanne ist eine
    # Naeherung; Tails weiten sie (C00008 reicht ueber ganz C0), deshalb zaehlen nur Knoten bis MAX_SPAN,
    # und der Knoten steht im Bericht und im JSON.
    aot = sorted((n["min_pc24"], n["max_pc24"], k) for k, n in nodes.items()
                 if n["disposition"] == "aot_eligible" and n.get("min_pc24") is not None)
    aot = [x for x in aot if x[2][0] in "CDEF" and x[1] - x[0] <= MAX_SPAN]
    starts = [x[0] for x in aot]

    def covering(pc):
        near = aot[bisect.bisect_left(starts, pc - MAX_SPAN):bisect.bisect_right(starts, pc)]
        return min((x for x in near if x[1] >= pc), key=lambda x: x[1] - x[0], default=None)

    rows = sorted(per_func.items(), key=lambda kv: -kv[1]["cycles"])
    out = []
    class_cycles = {"aot": 0, "kein_aot": 0}
    for own, e in rows:
        name, emit = syms[own] if own is not None else ("?", "?")
        mx = max(e["mx"], key=e["mx"].get)
        hot = max(e["hot_pc"], key=e["hot_pc"].get)
        node = nodes.get(f"{own:06X}:{mx}") if own is not None else None
        cov = covering(hot)
        cls = "aot" if cov else "kein_aot"
        class_cycles[cls] += e["cycles"]
        out.append({"addr": f"{own:06X}" if own is not None else None, "name": name, "emit": emit,
                    "cycles": e["cycles"], "insns": e["insns"], "mx": e["mx"], "runs": e["runs"],
                    "hot_pc": f"{hot:06X}", "hot_cycles": e["hot_pc"][hot], "class": cls,
                    "covered_by": cov[2] if cov else None,
                    "disposition": node["disposition"] if node else None,
                    "reasons": node.get("reasons", []) if node else []})
    print(f"\nROM nach Stand: AOT-Koerper vorhanden {class_cycles['aot']}, kein AOT-Koerper {class_cycles['kein_aot']}")
    for cls, title in (("aot", "AOT-Koerper vorhanden (Yield, Wartefunktion, Goto-Landung)"),
                       ("kein_aot", "kein AOT-Koerper (Kandidaten)")):
        sel = [r for r in out if r["class"] == cls]
        print(f"\nTop {min(a.top, len(sel))} {title}:")
        print(f"{'Zyklen':>11} {'%ROM':>6}  {'Adresse':<6} {'Funktion':<26} {'emit':<5} {'M/X':<5} heissester PC; Knoten; Grund")
        for r in sel[:a.top]:
            mx = max(r["mx"], key=r["mx"].get)
            print(f"{r['cycles']:>11} {100*r['cycles']/max(totals['rom'][1],1):>5.1f}%  "
                  f"{r['addr'] or '?':<6} {r['name'][:26]:<26} {str(r['emit']):<5} {mx:<5} "
                  f"{r['hot_pc']} ({100*r['hot_cycles']/max(r['cycles'],1):.0f} %); {r['covered_by'] or '-'}; "
                  f"{(r['reasons'] or [''])[0]}")
    print("\nHeisseste WRAM-PCs (Zyklen, % von WRAM):")
    for pc, cyc in sorted(ram_pc.items(), key=lambda kv: -kv[1])[:12]:
        print(f"  {pc:06X} {cyc:>11} {100*cyc/max(totals['ram'][1],1):>5.1f}%")
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"totals": totals, "per_run": per_run, "functions": out}, f, indent=1)


if __name__ == "__main__":
    main()
