#!/usr/bin/env python3
"""Vergleicht den PPU-Write-Strom eines Dumps gegen die Referenz (PLAN Phase 6, Field-IRQ/HDMA).

Aufruf: python tools/ff6/compare_ppuw.py <ref_dir> <run_dir> <tag> [--show N]
Exit 0: gleich bis auf die unten erklaerten INFO-Punkte. Exit 1: echte Abweichung.

Referenz: <tag>.ppuw.tsv des gepatchten snes9x (frame vcounter hcounter addr value source).
Recomp:   <tag>.ppuw.tsv aus state_dump.c (frame line addr value source).

Geprueft werden nur Anzeigeregister, also $2100-$2133 ohne die Datenports (die Inhalte stecken in
den VRAM-/CGRAM-/OAM-Dumps), plus HDMAEN. Beide Dateien gelten fuer genau ein Feld: VBlank-Writes
zuerst, dann die sichtbaren Zeilen.

Abgeglichen wird, welche Zeile ein Write zuerst betrifft:
  HDMA in der Referenz bei V    -> Zeile V+1 (H-Blank nach Zeile V)
  HDMA im Recomp bei line L     -> Zeile L, der Schritt vor der Schleife (L=0) -> Zeile 1
  CPU in der Referenz bei V<225 -> Zeile V+1 (der Journal-Replay arbeitet zeilenweise)
  CPU in der Referenz bei V>=225-> vor dem Feld (Zeile 0)
  CPU im Recomp: Reihenfolge aus `cpu` (line -1), Zeile aus `replay`

INFO statt Abweichung:
  Ein HDMA-Schritt im Recomp hinter dem HDMAEN-Write des IRQ. Das Journal ist zeilengenau: Der IRQ
  schreibt bei V=215 vor dem H-Blank, im Recomp gilt das erst fuer Zeile 216. Harmlos, solange die
  betroffene Zeile im Force-Blank liegt; das wird geprueft, sonst ist es eine Abweichung.

  Ein CPU-Write bis zu 3 Zeilen versetzt zur Referenz. Generierter Code rechnet einem geraden Block
  alle Zyklen am Blockanfang an; ein Write mitten im Block sieht daher dessen Endzeit (FF6 DoTfr in
  TfrBGAnimGfx: 484 Zyklen, $2100 = $80 zwei Zeilen spaeter). Ein NMI, der ueber V=0 hinauslaeuft,
  landet so auf der anderen Seite der Feldgrenze. Ob das sichtbar wird, entscheidet der
  Framebuffer-Vergleich in compare_dumps.py.

  $211B/$211C/... ausserhalb von Mode 7 auf beliebiger Zeile. Das Menue nutzt sie als Multiplizierer
  ($2134); ohne Mode 7 wirken sie nicht aufs Bild, die Zeile sagt nur, wie schnell die CPU dorthin kam.
  Reihenfolge und Werte bleiben geprueft.

  Gleiche HDMAEN-Writes direkt hintereinander zaehlen einmal. HDMAEN ist ein einfaches Register (kein
  Doppel-Write wie die Scroll- und Mode-7-Register), ein zweiter gleicher Write aendert nichts. FF6
  schreibt ihn als Nebeneffekt: `stz hMDMAEN` bzw. `sta hMDMAEN` mit 16-Bit-A trifft $420B und $420C,
  je DMA-Block einmal. Wie viele Bloecke ein NMI faehrt, haengt an der Animationsphase (Field:
  TfrObjGfxSub waehlt die Objektgruppe ueber $47 & 3, field/obj.asm:2749; Kampf: Figurengrafik,
  btlgfx/interrupt.asm:885). Der Inhalt steckt im VRAM-Dump.

Einzelne HDMA-Werte lassen sich mit [[ppuw]] in validation/masks.toml dulden (reg, first, last, tags,
reason): Der Recomp liest HDMA-Daten am Feldende, nicht zur Strahlzeit. Aendert die CPU sie mitten im
Feld, sieht er den neueren Wert. Struktur und Reihenfolge bleiben geprueft.
"""
import argparse, json, os, sys, tomllib

PORTS = {0x2104, 0x2115, 0x2116, 0x2117, 0x2118, 0x2119, 0x2121, 0x2122}
MODE7_REGS = range(0x211B, 0x2121)
MASKS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                     "validation", "masks.toml")
SPLIT_SLACK = 3


def load_ppuw_masks(tag, path=MASKS):
    if not os.path.exists(path):
        return []
    with open(path, "rb") as f:
        entries = tomllib.load(f).get("ppuw", [])
    for e in entries:
        if not e.get("reason"):
            sys.exit(f"compare_ppuw: Maske ohne Begruendung: {e}")
    return [e for e in entries if tag in e["tags"]]


def display_reg(a):
    return a == 0x420C or (0x2100 <= a <= 0x2133 and a not in PORTS)


def rows(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            yield line.rstrip("\n").split("\t")


def load_ref(path):
    hdma, cpu = [], []
    for fr, v, h, a, val, src in rows(path):
        a = int(a, 16)
        if not display_reg(a):
            continue
        e = (int(v), int(h), a, int(val, 16))
        (hdma if src == "hdma" else cpu).append(e)
    return hdma, cpu


def load_run(path):
    hdma, cpu, replay = [], [], []
    for fr, line, a, val, src in rows(path):
        a = int(a, 16)
        if not display_reg(a):
            continue
        e = (int(line), a, int(val, 16))
        {"hdma": hdma, "cpu": cpu, "replay": replay}.get(src, cpu).append(e)
    return hdma, cpu, replay


def collapse_hdmaen(ws):
    """Gleiche HDMAEN-Writes direkt hintereinander auf einen kuerzen. ws: (adresse, wert)."""
    out = []
    for w in ws:
        if w[0] == 0x420C and out and out[-1] == w:
            continue
        out.append(w)
    return out, len(ws) - len(out)


def force_blank_from(entries):
    """Erste Zeile, ab der INIDISP Force-Blank setzt und bis Feldende haelt. entries: (zeile, wert)."""
    start = None
    for line, val in entries:
        if val & 0x80:
            if start is None:
                start = line
        else:
            start = None
    return start


def uses_mode7(ref_dir, tag):
    """BG-Modus der Referenz am Dump. Ohne regs.json gilt Mode 7 als an (keine zusaetzliche Duldung)."""
    path = os.path.join(ref_dir, tag + ".regs.json")
    if not os.path.exists(path):
        return True
    with open(path, encoding="utf-8", errors="replace") as f:
        return json.load(f)["ppu"]["bgmode"] == 7


def fmt(e):
    return f"Zeile {e[0]:3} ${e[1]:04X} = {e[2]:02X}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref_dir"); ap.add_argument("run_dir"); ap.add_argument("tag")
    ap.add_argument("--show", type=int, default=6)
    a = ap.parse_args()
    pr = os.path.join(a.ref_dir, a.tag + ".ppuw.tsv")
    pu = os.path.join(a.run_dir, a.tag + ".ppuw.tsv")
    if not (os.path.exists(pr) and os.path.exists(pu)):
        print(f"{a.tag}: uebersprungen (fehlt: {'ref' if not os.path.exists(pr) else 'run'})")
        return 0
    r_hdma, r_cpu = load_ref(pr)
    u_hdma, u_cpu, u_replay = load_run(pu)
    bad = 0

    # 1. CPU-Writes: gleiche Reihenfolge, gleiche Werte
    rc, r_dup = collapse_hdmaen([(x[2], x[3]) for x in r_cpu])
    uc, u_dup = collapse_hdmaen([(x[1], x[2]) for x in u_cpu])
    if r_dup != u_dup:
        print(f"cpu:   INFO: gleiche HDMAEN-Writes hintereinander zusammengefasst (ref {r_dup}, run {u_dup})")
    if rc == uc:
        print(f"cpu:   {len(rc)} Writes gleich")
    else:
        bad += 1
        i = next((k for k, (p, q) in enumerate(zip(rc, uc)) if p != q), min(len(rc), len(uc)))
        print(f"cpu:   ABWEICHUNG, {len(rc)} gegen {len(uc)} Writes, erste bei Index {i}")
        for k in range(i, min(i + a.show, max(len(rc), len(uc)))):
            p = f"${rc[k][0]:04X}={rc[k][1]:02X}" if k < len(rc) else "-"
            q = f"${uc[k][0]:04X}={uc[k][1]:02X}" if k < len(uc) else "-"
            print(f"   [{k}] ref {p}  run {q}")

    # 2. Split-Zeilen: alle CPU-Writes ausser HDMAEN (der geht nicht durch den Replay), VBlank = Zeile 0
    rs = [(x[0] + 1 if x[0] < 225 else 0, x[2], x[3]) for x in r_cpu if x[2] != 0x420C]
    us = u_replay
    moved = [(p, q) for p, q in zip(rs, us) if p != q]
    mode7 = uses_mode7(a.ref_dir, a.tag)
    if rs == us:
        print(f"split: {len(rs)} Writes auf gleichen Zeilen")
    elif len(rs) == len(us) and all(p[1:] == q[1:] and (abs(q[0] - p[0]) <= SPLIT_SLACK
                                                       or (p[1] in MODE7_REGS and not mode7)) for p, q in moved):
        print(f"split: {len(rs)} Writes, INFO: {len(moved)} zeilenversetzt, "
              + ", ".join(f"${p[1]:04X} Zeile {q[0]} statt {p[0]}" for p, q in moved[:a.show]))
    else:
        bad += 1
        print(f"split: ABWEICHUNG, {len(rs)} gegen {len(us)} Writes, ref {[fmt(x) for x in rs[:a.show]]}, "
              f"run {[fmt(x) for x in us[:a.show]]}")

    # 3. HDMA: je Zeile gleiche Writes in gleicher Reihenfolge
    rh = [(x[0] + 1, x[2], x[3]) for x in r_hdma]
    uh = [(x[0] if x[0] > 0 else 1, x[1], x[2]) for x in u_hdma]
    n = min(len(rh), len(uh))
    masks = load_ppuw_masks(a.tag)

    def tolerated(p, q):
        return p[:2] == q[:2] and any(p[1] in m["reg"] and m["first"] <= p[0] <= m["last"] for m in masks)

    known = sum(1 for k in range(n) if rh[k] != uh[k] and tolerated(rh[k], uh[k]))
    if known:
        print(f"hdma:  INFO: {known} Werte geduldet (validation/masks.toml, [[ppuw]])")
    i = next((k for k in range(n) if rh[k] != uh[k] and not tolerated(rh[k], uh[k])), n)
    if i < n:
        bad += 1
        print(f"hdma:  ABWEICHUNG bei Index {i} von {len(rh)}/{len(uh)}")
        for k in range(i, min(i + a.show, n)):
            print(f"   [{k}] ref {fmt(rh[k])}   run {fmt(uh[k])}")
    elif len(rh) == len(uh):
        print(f"hdma:  {len(rh)} Writes gleich")
    elif len(uh) > len(rh):
        # Nur der Schritt hinter dem IRQ-HDMAEN darf ueberstehen, und nur im Force-Blank.
        extra = uh[len(rh):]
        lines = sorted({x[0] for x in extra})
        ini = [(0, x[3]) for x in r_cpu if x[2] == 0x2100 and x[0] >= 225]
        ini += [(x[0] + 1, x[3]) for x in r_cpu if x[2] == 0x2100 and x[0] < 225]
        fb = force_blank_from(ini)
        if fb is not None and lines[0] >= fb and len(lines) == 1:
            print(f"hdma:  {len(rh)} Writes gleich, INFO: {len(extra)} Writes je Schritt hinter dem "
                  f"IRQ auf Zeile {lines[0]}, Force-Blank ab Zeile {fb}")
        else:
            bad += 1
            print(f"hdma:  ABWEICHUNG, {len(extra)} Writes zu viel auf Zeilen {lines}, Force-Blank ab {fb}")
    else:
        bad += 1
        print(f"hdma:  ABWEICHUNG, im Recomp fehlen {len(rh) - len(uh)} Writes, erste: {fmt(rh[len(uh)])}")

    print(f"{a.tag}: {'gleich' if not bad else 'ABWEICHUNG'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
