#!/usr/bin/env python3
"""Miss-Report: wrappt tier2_ingest.py --json fuer einen Lauf.

Aufruf: python tools/ff6/miss_report.py work/run/<r> [--top N] [--capture-dir DIR]

Liest die Coverage-Captures (*.json/*.jsonl) aus dem Laufverzeichnis. Fehlen sie,
wird die neueste Session aus %LOCALAPPDATA%/snesrecomp-coverage/finalfantasyvi
(oder --capture-dir) dorthin kopiert. Ausgabe: Top-N ROM-Misses (Adresse, Symbol,
M/X, Grund, Treffer) und eine Zusammenfassung. Ziele in WRAM (7E/7F) gehoeren zur
Allowlist (RAM-Code laeuft im Interpreter) und werden nur gezaehlt. ROM-Misses aus
validation/miss_allowlist.toml (Ziel + M/X, je mit Begruendung) werden getrennt gelistet.
Exit 1, solange nicht geduldete ROM-Misses uebrig sind.

With --log <stderr log of the run>: also lists the skipped dispatches the runtime reports
there, one line per site on its first hit: `[dispatch-oob]` (a dispatch value missing from
a generated switch, always on since snesrecomp patch 0015) and `[unresolved-abandon]` (an
unresolved transfer abandoned without its handler). They are not in the coverage captures,
because no interpreter transfer happens. Each one also makes the exit code 1.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, tomllib

GR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INGEST = os.path.join(GR, "snesrecomp", "tools", "tier2_ingest.py")
MANIFEST = os.path.join(GR, "src", "gen", "program_manifest.json")
SYMBOLS = os.path.join(GR, "recomp", "symbols.toml")
ALLOWLIST = os.path.join(GR, "validation", "miss_allowlist.toml")


def load_allowlist():
    if not os.path.exists(ALLOWLIST):
        return {}
    with open(ALLOWLIST, "rb") as f:
        entries = tomllib.load(f).get("miss", [])
    for e in entries:
        if not e.get("reason") or not e.get("resolve"):
            sys.exit(f"miss_report: Allowlist-Eintrag {e.get('target', '?'):#x} ohne reason/resolve")
    return {(e["target"], e["mx"]): e for e in entries}


def load_symbols():
    with open(SYMBOLS, "rb") as f:
        funcs = tomllib.load(f).get("func", [])
    return {(int(x["bank"]) << 16) | int(x["addr"], 16): x["name"] for x in funcs}


SKIP_RE = re.compile(r"^\[(dispatch-oob|unresolved-abandon)\] first hit site=\$([0-9A-Fa-f]{6})"
                     r"(?: value=\$([0-9A-Fa-f]{1,6}))? frame=(-?\d+)")


def skipped_dispatches(lines):
    """(kind, site, value or None, frame) for each first-hit line of the runtime's stderr."""
    out = []
    for line in lines:
        m = SKIP_RE.match(line)
        if m:
            out.append((m[1], int(m[2], 16), int(m[3], 16) if m[3] else None, int(m[4])))
    return out


def ensure_captures(run_dir, capture_dir):
    # Capture-Name endet auf _s<Nummer>; ohne die Ziffer passen auch Dump-Tags (back_south.info.json)
    found = sorted(glob.glob(os.path.join(run_dir, "*_s[0-9]*.json")))
    if found:
        return [os.path.basename(p) for p in found]
    cap = capture_dir or os.path.join(
        os.environ.get("LOCALAPPDATA", ""), "snesrecomp-coverage", "finalfantasyvi")
    jsons = sorted(glob.glob(os.path.join(cap, "*.json")), key=os.path.getmtime)
    if not jsons:
        sys.exit(f"miss_report: keine Captures in {run_dir} oder {cap}")
    newest = jsons[-1]
    for p in (newest, newest[:-5] + ".jsonl"):
        if os.path.exists(p):
            shutil.copy(p, run_dir)
    return [os.path.basename(newest)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--capture-dir")
    ap.add_argument("--log", help="stderr log of the run: list skipped dispatches")
    a = ap.parse_args()
    run_dir = os.path.abspath(a.run_dir)
    caps = ensure_captures(run_dir, a.capture_dir)
    # Relativ aufrufen: Windows-Python kann die Pfade sonst nicht immer oeffnen.
    r = subprocess.run([sys.executable, "-I", INGEST, "--json", "--program-manifest",
                        os.path.relpath(MANIFEST, run_dir)] + caps,
                       cwd=run_dir, capture_output=True, text=True)
    if r.returncode:
        sys.exit("miss_report: tier2_ingest fehlgeschlagen:\n" + r.stderr[-1500:])
    d = json.loads(r.stdout)
    with open(os.path.join(run_dir, "ingest.json"), "w") as f:
        f.write(r.stdout)
    disc = d["discoveries"]
    ram = [x for x in disc if 0x7E0000 <= int(x["target_pc24"], 16) < 0x800000]
    allow = load_allowlist()
    allowed = [x for x in disc if x not in ram and (int(x["target_pc24"], 16), x["entry_mx"]) in allow]
    rom = [x for x in disc if x not in ram and x not in allowed]
    rom.sort(key=lambda x: -x["observed_hits"])
    print(f"Captures: {', '.join(caps)}")
    print(f"Interpretiert: {d['interpreted_instructions']} Instr., {d['interpreted_guest_cycles']} Zyklen")
    for w in d["warnings"]:
        print("WARNUNG:", w)
    print(f"Discoveries: {len(disc)} (ROM-Misses {len(rom)}, ROM-Allowlist {len(allowed)}, "
          f"WRAM-Allowlist {len(ram)})")
    syms = load_symbols()
    for x in allowed:
        t = int(x["target_pc24"], 16)
        print(f"  geduldet: {x['target_pc24']} {syms.get(t, '?'):<20} {x['entry_mx']} "
              f"- {allow[(t, x['entry_mx'])]['reason']}")
    reasons = {}
    for x in rom:
        k = (x["fallback_reason"], x["site_kind"])
        reasons[k] = reasons.get(k, 0) + 1
    for (fr, sk), n in sorted(reasons.items()):
        print(f"  {fr} / {sk}: {n}")
    print(f"Top {min(a.top, len(rom))} ROM-Misses:")
    for x in rom[:a.top]:
        t = int(x["target_pc24"], 16)
        print(f"  {x['target_pc24']} {syms.get(t, '?'):<28} {x['entry_mx']} "
              f"E{x['emulation']} {x['site_kind']:<8} hits={x['observed_hits']} "
              f"von {x['site_pc24']}")
    skipped = []
    if a.log:
        with open(a.log, encoding="utf-8", errors="replace") as f:
            skipped = skipped_dispatches(f)
        print(f"Skipped dispatches (run log): {len(skipped)}")
        for kind, site, value, frame in skipped:
            val = f" value=${value:06X}" if value is not None else ""
            print(f"  {kind} site=${site:06X}{val} first frame {frame}")
    sys.exit(1 if rom or skipped else 0)


if __name__ == "__main__":
    main()
