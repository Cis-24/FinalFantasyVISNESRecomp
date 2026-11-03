#!/usr/bin/env python3
"""Prueft einen Routenlauf gegen validation/expected/<route>.toml (Teil von regress.sh).

Aufruf: python tools/ff6/regress_check.py <route> <run_dir> <run_log> <miss_report>
        [--update]

Geprueft werden:
  - Skript-Ereignisse (`script f=...`-Zeilen des Laufs: until-Frames, dumps, quit),
  - SHA-256 je Dump (wram/vram/cgram/oam/sram/fb.bgrx); maskierte Bytes aus
    validation/masks.toml werden vorher auf 0 gesetzt (fb-Masken: Pixelindex, 4 Byte),
  - Miss-Zahlen (Zeile `Discoveries:` aus dem miss_report-Text). Abweichende Zahlen
    werden nur gemeldet; ROM-Misses entscheidet der Exit-Code von miss_report.py.
Ausgabe: Tabellenzeilen fuer regress.sh. Exit 1 bei abweichenden Ereignissen/Hashes.
--update schreibt die Erwartung neu; die Aenderung braucht einen begruendeten Eintrag
in validation/CHANGELOG.md.
"""
import argparse, hashlib, os, re, sys, tomllib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compare_dumps import GR, load_masks, mask_ranges  # noqa: E402

EXPECTED = os.path.join(GR, "validation", "expected")
KINDS = (("wram", "wram.bin", 1), ("vram", "vram.bin", 1), ("cgram", "cgram.bin", 1),
         ("oam", "oam.bin", 1), ("sram", "sram.bin", 1), ("fb", "fb.bgrx", 4))
MISS_RE = re.compile(r"Discoveries: (\d+) \(ROM-Misses (\d+), ROM-Allowlist (\d+), "
                     r"WRAM-Allowlist (\d+)\)")
INTERP_RE = re.compile(r"Interpretiert: (\d+) Instr\.")


def row(route, check, ok, detail=""):
    print(f"{route:<16} {check:<16} {ok:<5} {detail}")


def events(log):
    out = []
    for line in open(log, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line.startswith("script f=") and line[7:] not in out:
            out.append(line[7:])
    return out


def dump_hashes(run_dir, masks):
    tags = sorted(f[:-len(".wram.bin")] for f in os.listdir(run_dir) if f.endswith(".wram.bin"))
    out = {}
    for tag in tags:
        h = {}
        for kind, suffix, unit in KINDS:
            p = os.path.join(run_dir, f"{tag}.{suffix}")
            if not os.path.exists(p):
                continue
            data = bytearray(open(p, "rb").read())
            for s, e in mask_ranges(masks, kind, tag):
                data[s * unit:(e + 1) * unit] = bytes(((e + 1) - s) * unit)
            h[kind] = hashlib.sha256(data).hexdigest()
        out[tag] = h
    return out


def miss_counts(report):
    text = open(report, encoding="utf-8", errors="replace").read()
    m, i = MISS_RE.search(text), INTERP_RE.search(text)
    if not m:
        return {}
    c = dict(zip(("discoveries", "rom", "allowlist", "wram"), map(int, m.groups())))
    if i:
        c["interpreted"] = int(i.group(1))
    return c


def write_expected(path, route, ev, hashes, miss):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# Erwartung fuer Route {route} (tools/ff6/regress.sh, regress_check.py --update).\n"
                "# Hashes: SHA-256 der Dumps, maskierte Bytes (validation/masks.toml) auf 0.\n"
                "# Aenderung nur mit begruendetem Eintrag in validation/CHANGELOG.md.\n")
        f.write("events = [\n" + "".join(f'  "{e}",\n' for e in ev) + "]\n")
        f.write("\n[miss]  # nur gemeldet, nicht entscheidend\n")
        for k, v in miss.items():
            f.write(f"{k} = {v}\n")
        for tag, h in hashes.items():
            f.write(f"\n[dump.{tag}]\n")
            for k, v in h.items():
                f.write(f'{k} = "{v}"\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("route"); ap.add_argument("run_dir"); ap.add_argument("run_log")
    ap.add_argument("miss_report")
    ap.add_argument("--update", action="store_true")
    a = ap.parse_args()
    ev = events(a.run_log)
    hashes = dump_hashes(a.run_dir, load_masks())
    miss = miss_counts(a.miss_report)
    path = os.path.join(EXPECTED, f"{a.route}.toml")
    if a.update:
        os.makedirs(EXPECTED, exist_ok=True)
        write_expected(path, a.route, ev, hashes, miss)
        row(a.route, "Erwartung", "NEU", os.path.relpath(path, GR).replace(os.sep, "/") +
            " geschrieben (CHANGELOG-Eintrag noetig)")
        return
    if not os.path.exists(path):
        row(a.route, "Erwartung", "FAIL", "fehlt (erst --update, dann CHANGELOG)")
        sys.exit(1)
    with open(path, "rb") as f:
        exp = tomllib.load(f)
    bad = 0
    if ev == exp.get("events", []):
        row(a.route, "Ereignisse", "PASS", "; ".join(ev[:2]) + (" ..." if len(ev) > 2 else ""))
    else:
        bad += 1
        row(a.route, "Ereignisse", "FAIL", f"erwartet {exp.get('events')}")
        row("", "", "", f"bekommen {ev}")
    exp_dumps = exp.get("dump", {})
    for tag in sorted(set(hashes) | set(exp_dumps)):
        got, want = hashes.get(tag, {}), exp_dumps.get(tag, {})
        diff = sorted(k for k in set(got) | set(want) if got.get(k) != want.get(k))
        if diff:
            bad += 1
        row(a.route, f"Hashes {tag}", "FAIL" if diff else "PASS",
            ("abweichend: " + ", ".join(diff)) if diff else ", ".join(got))
    want_miss = exp.get("miss", {})
    changed = [f"{k} {want_miss.get(k)}->{miss.get(k)}" for k in sorted(set(miss) | set(want_miss))
               if miss.get(k) != want_miss.get(k)]
    row(a.route, "Miss-Zahlen", "INFO" if changed else "PASS",
        ("geaendert: " + ", ".join(changed)) if changed else
        f"ROM {miss.get('rom')}, geduldet {miss.get('allowlist')}, WRAM {miss.get('wram')}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
