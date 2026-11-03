#!/usr/bin/env python3
"""Sucht die Promotionen, die den Boot brechen: Praefix-Bisektion (ddmin-artig) zwischen
einem guten und einem schlechten tools/ff6/symbols_overrides.toml (generierter Block).

Aufruf (MSYS2 MINGW64, cwd = GR, SNESRECOMP_ROM in C:/-Form):
  python tools/ff6/bisect_promotions.py <good.toml> <bad.toml> <tag> [--fest k1,k2,..] [--prefix N]

Kandidaten = Eintraege von bad, die in good fehlen (Reihenfolge wie im Block). Je Test:
good + Teilmenge schreiben -> symbols_sync -> regen -> Build -> Route r01; "gut" = Exit 0.
Annahme: mehr Promotionen reparieren nichts. Gesucht wird das kleinste Praefix, das bricht;
dessen letztes Element ist notwendig ("fest"), danach wird im Rest davor weitergesucht, bis
die festen Elemente allein brechen. Fortsetzen: --fest mit den bisher festen Schluesseln
(bbaaaa, klein), --prefix mit der Laenge des noch offenen Praefixes.
Logs: ../work/logs/bisect_<tag>_<n>.log, Laeufe: ../work/run/<tag>_<n>.
Am Ende bleibt die zuletzt getestete Menge in symbols_overrides.toml: zuruecksetzen!
"""
import os, re, subprocess, sys

GR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.path.join(os.path.dirname(GR), "work")
OVR = os.path.join(GR, "tools", "ff6", "symbols_overrides.toml")
BEGIN = "# >>> BEGIN promote_misses (generiert, nicht von Hand aendern)"
END = "# <<< END promote_misses"
EXE = os.path.join(GR, "build", "FinalFantasyViSNESRecomp.exe")   # CreateProcess braucht absolut
ROUTE = "validation/routes/r01_boot_title.txt"


def split(path):
    t = open(path, encoding="utf-8").read()
    head, block = t[:t.index(BEGIN)], t[t.index(BEGIN) + len(BEGIN):t.index(END)]
    ents = []
    for chunk in block.split("[[func]]")[1:]:
        a = re.search(r'addr = "([0-9a-f]{4})"', chunk).group(1)
        b = re.search(r"bank = 0x([0-9a-f]{2})", chunk).group(1)
        ents.append((b + a, "[[func]]" + chunk.rstrip() + "\n\n"))
    return head, ents


def main():
    args = sys.argv[1:]
    opts = {a: args[i + 1] for i, a in enumerate(args) if a in ("--fest", "--prefix")}
    pos = [a for i, a in enumerate(args) if a not in opts and (i == 0 or args[i - 1] not in opts)]
    if len(pos) != 3:
        sys.exit(__doc__)
    good_path, bad_path, tag = pos
    rom = os.environ["SNESRECOMP_ROM"]
    head, good = split(good_path)
    _, bad = split(bad_path)
    gk = {k for k, _ in good}
    new = [e for e in bad if e[0] not in gk]
    fest = opts.get("--fest", "")
    fest = [k for k in fest.split(",") if k]
    culprits = [e for e in new if e[0] in fest]
    items = [e for e in new[:int(opts.get("--prefix", len(new)))] if e[0] not in fest]
    print(f"gut {len(good)}, schlecht {len(bad)}, neu {len(new)}, fest {len(culprits)}, offen {len(items)}",
          flush=True)
    n = [0]
    cache = {}

    def fails(ents, label):
        key = frozenset(k for k, _ in ents)
        if key in cache:
            return cache[key]
        n[0] += 1
        t = f"{tag}_{n[0]}"
        open(OVR, "w", encoding="utf-8", newline="\n").write(
            head + BEGIN + "\n" + "".join(x for _, x in ents) + END + "\n")
        env = dict(os.environ)
        with open(os.path.join(WORK, "logs", f"bisect_{t}.log"), "w") as lf:
            for cmd in (["python", "tools/ff6/symbols_sync.py"], ["bash", "tools/regen.sh"],
                        ["cmake", "--build", "build"]):
                if subprocess.call(cmd, cwd=GR, stdout=lf, stderr=subprocess.STDOUT, env=env):
                    print(f"{t} {label}: FEHLER in {cmd}", flush=True)
                    sys.exit(2)
            r = os.path.join(WORK, "run", t)
            os.makedirs(r, exist_ok=True)
            renv = dict(env, SNESRECOMP_COVERAGE_DIR=r, SNESRECOMP_DUMP_DIR=r,
                        SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
            try:
                rc = subprocess.call([EXE, "--no-launcher", "--rom", rom, "--script", ROUTE], cwd=GR,
                                     stdout=lf, stderr=subprocess.STDOUT, env=renv, timeout=400)
            except subprocess.TimeoutExpired:
                rc = -1
        cache[key] = rc != 0
        print(f"{t} {label}: {len(ents)} Eintraege, rc={rc} -> {'SCHLECHT' if rc else 'gut'}", flush=True)
        return cache[key]

    cache[frozenset(k for k, _ in good + culprits + items)] = True   # Startannahme: bricht
    while items:
        base = good + culprits
        lo, hi = 0, len(items)
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if fails(base + items[:mid], f"Praefix {mid}/{len(items)} + {len(culprits)} fest"):
                hi = mid
            else:
                lo = mid
        c = items[hi - 1]
        culprits.append(c)
        items = items[:hi - 1]
        print(f"fest: {c[0]} {c[1].splitlines()[1]} (offen jetzt --prefix-Laenge {len(items)})", flush=True)
        if fails(good + culprits, f"nur {len(culprits)} feste"):
            break
    print("Menge:", ",".join(c[0] for c in culprits), flush=True)
    ck = {c[0] for c in culprits}
    ok = not fails(good + [e for e in new if e[0] not in ck], "alles ohne Menge")
    print(f"Gegenprobe alles ohne Menge: {'bootet' if ok else 'bricht AUCH'}", flush=True)


if __name__ == "__main__":
    main()
