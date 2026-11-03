#!/usr/bin/env python3
"""Uebertraegt ROM-Misses (call_gap) aus einem Lauf als emit-Promotionen in
tools/ff6/symbols_overrides.toml (generierter Block) und synchronisiert symbols.toml.

Aufruf: python tools/ff6/promote_misses.py [--callees [--dispatch-leaves]] work/run/<r> [work/run/<r2> ...]

--callees: zusaetzlich die Ziele aller `unproven_call_at_<site>_to_<ziel>_m<M>x<X>`-Gruende
der Miss-Varianten (src/gen/program_manifest.json) promoten; sie machen die Variante
sonst LLE-only (unbelegte Callee-Exit-Breite). Zusaetzlich der Abschluss ueber alle
`lle_exact`-Direktaufrufe (direct_call/direct_tail_call) blockierter Varianten, soweit deren
Zielvariante noch nie analysiert wurde (nicht beobachtet, aber statisch belegt).

--dispatch-leaves: zusaetzlich die `lle_exact`-Sprungtabellenziele (static_dispatch) der
Blaetter dieser Kette promoten, also AOT-faehiger Callees ohne bewiesene Exit-Breite. Nur
diese Blaetter, nicht alle Dispatch-Ziele blockierter Varianten (das bricht den Boot,
s. docs/STATUS.md).

Ziel = Miss-Ziel, entry_m/entry_x = beobachtetes M/X (haeufigstes je Ziel). Unbekannte
Ziele bekommen den Namen Sub_<PC24>. Goto-Landungen (goto_gap) werden nicht promotet,
sondern aufgelistet: sie brauchen eine Funktionsgrenze, keinen Einstieg. WRAM-Ziele
bleiben Interpreter. Der Block wird bei jedem Aufruf aus allen uebergebenen Laeufen neu
geschrieben; er ersetzt keine handgepflegten Eintraege davor.

Ziele mit `emit = false` im handgepflegten Teil werden nie promotet (auch nicht ueber den
Callee-Abschluss) und fallen aus dem Block. Sonst wuerde der Block, der in symbols_sync.py
nach dem Handteil kommt, die Sperre ueberschreiben.
"""
import json, os, re, subprocess, sys, tomllib

GR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OVR = os.path.join(GR, "tools", "ff6", "symbols_overrides.toml")
BEGIN = "# >>> BEGIN promote_misses (generiert, nicht von Hand aendern)"
END = "# <<< END promote_misses"


def main():
    args = sys.argv[1:]
    callees = "--callees" in args
    dispatch_leaves = "--dispatch-leaves" in args
    runs = [a for a in args if a not in ("--callees", "--dispatch-leaves")]
    if not runs:
        sys.exit(__doc__)
    with open(os.path.join(GR, "recomp", "symbols.toml"), "rb") as f:
        names = {(x["bank"] << 16) | int(x["addr"], 16): x["name"]
                 for x in tomllib.load(f)["func"]}
    best, skipped = {}, {}
    for r in runs:
        d = json.load(open(os.path.join(r, "ingest.json")))
        for x in d["discoveries"]:
            t = int(x["target_pc24"], 16)
            if 0x7E0000 <= t < 0x800000:
                continue
            if x["site_kind"] != "call_gap":
                skipped[t] = x["site_kind"]
                continue
            m = re.fullmatch(r"M(\d)X(\d)", x["entry_mx"])
            key = (t, int(m.group(1)), int(m.group(2)))
            best[key] = best.get(key, 0) + x["observed_hits"]
    if callees:
        manifest = json.load(open(os.path.join(GR, "src", "gen", "program_manifest.json")))
        nodes = manifest["nodes"]
        exits = set(manifest["exit_modes"]) | set(manifest["exit_mode_sets"])
        todo, seen = ["%06X:M%dX%d" % k for k in best], set()
        while todo:
            k = todo.pop()
            if k in seen:
                continue
            seen.add(k)
            n = nodes.get(k)
            if not n:
                continue
            nxt = []
            if n["disposition"] != "lle_only":
                # Blatt: AOT-faehig, Exit unbewiesen, weil Sprungtabellenziele LLE sind oder
                # (schon promotet, `aot_exact`) selbst noch lle_only; dann dort weitergehen.
                if not (dispatch_leaves and k not in exits):
                    continue
                for dmd in n.get("demands", []):
                    if dmd["resolution"] in ("lle_exact", "aot_exact") and dmd["kind"] == "static_dispatch":
                        t = dmd["target"]
                        nxt.append((t["pc24"], t["m"], t["x"]))
                n = {}
            for reason in n.get("reasons", []):
                c = re.fullmatch(r"unproven_call_at_[0-9A-F]{6}_to_([0-9A-F]{6})_m(\d)x(\d)", reason)
                if c:
                    nxt.append((int(c.group(1), 16), int(c.group(2)), int(c.group(3))))
            for dmd in n.get("demands", []):
                if dmd["resolution"] == "lle_exact" and dmd["kind"] in ("direct_call", "direct_tail_call"):
                    t = dmd["target"]
                    nxt.append((t["pc24"], t["m"], t["x"]))
            for (t, m, x) in nxt:
                if 0x7E0000 <= t < 0x800000:
                    continue
                kk = "%06X:M%dX%d" % (t, m, x)
                if kk not in nodes:                 # Variante nie analysiert: als Root anbieten
                    best[(t, m, x)] = best.get((t, m, x), 0) + 1
                else:
                    todo.append(kk)
    hand = open(OVR, encoding="utf-8").read()
    hand = hand[:hand.index(BEGIN)] if BEGIN in hand else hand
    locked = {(f["bank"] << 16) | int(f["addr"], 16)
              for f in tomllib.loads(hand).get("func", []) if f.get("emit") is False}
    chosen = {}
    for (t, m, x), h in best.items():
        if t in locked:
            continue
        if t not in chosen or h > chosen[t][2]:
            chosen[t] = (m, x, h)
    # Kumulativ: bereits promotete Ziele aus dem vorhandenen Block bleiben bestehen.
    old = open(OVR, encoding="utf-8").read()
    if BEGIN in old:
        block = old[old.index(BEGIN):]
        for f in tomllib.loads(block.replace(BEGIN, "").replace(END, "")).get("func", []):
            t = (f["bank"] << 16) | int(f["addr"], 16)
            if t not in locked:
                chosen.setdefault(t, (f["entry_m"], f["entry_x"], 0))
    lines = [BEGIN]
    for t in sorted(chosen):
        m, x, h = chosen[t]
        lines += ["[[func]]", f'name = "{names.get(t, "Sub_%06X" % t)}"',
                  f'addr = "{t & 0xFFFF:04x}"', f"bank = 0x{t >> 16:02x}", "emit = true",
                  f"entry_m = {m}", f"entry_x = {x}", f'note = "Miss-Promotion, {h} Treffer"', ""]
    lines.append(END)
    text = open(OVR, encoding="utf-8").read()
    if BEGIN in text:
        text = text[:text.index(BEGIN)].rstrip() + "\n"
    open(OVR, "w", encoding="utf-8", newline="\n").write(text.rstrip() + "\n\n" + "\n".join(lines) + "\n")
    print(f"{len(chosen)} Ziele promotet, {len(skipped)} Landungen uebersprungen:",
          ", ".join(f"{t:06X}" for t in sorted(skipped)))
    if locked:
        print(f"{len(locked)} Ziele von Hand gesperrt (emit = false):", ", ".join(f"{t:06X}" for t in sorted(locked)))
    subprocess.check_call([sys.executable, os.path.join(GR, "tools", "ff6", "symbols_sync.py")])


if __name__ == "__main__":
    main()
