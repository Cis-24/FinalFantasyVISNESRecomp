#!/usr/bin/env python3
"""Vergleicht zwei Dump-Verzeichnisse (Referenz vs. Recomp) fuer ein Tag.

Aufruf: python tools/ff6/compare_dumps.py work/ref/r01 work/run/r01 title
        [--masks validation/masks.toml] [--fb-tol N]

Verglichen werden WRAM, VRAM, CGRAM, OAM (nur wenn beide Seiten die Datei haben) und
der Framebuffer (24-bit BMP, Kanalabweichung > --fb-tol zaehlt). Maskierte Bereiche
stehen mit Begruendung in validation/masks.toml. Exit 1 bei unmaskierten Abweichungen.

Renderer-Rundung: Meldet die Referenz `fb_core_pixel_format = RGB565` (Stock-snes9x),
wird der Framebuffer im nativen 5-Bit-SNES-Farbraum verglichen (je Kanal >> 3). Die
8-Bit-Erweiterung des 6-Bit-Gruens weicht sonst um 1-2 Stufen von der des Recomp ab
(Nachweis 2026-10-29, docs/STATUS.md). --fb-8bit erzwingt den 8-Bit-Vergleich.

Gruen und Farbmathe: snes9x rechnet Halb-Addition in RGB565, also mit 6 Bit Gruen samt dem
erweiterten Bit (g5 >= 16 setzt es). Bei ungerader Summe liegt die Referenz dann eine Stufe ueber
dem 5-Bit-Ergebnis. Tags in [[fb_green]] (validation/masks.toml) dulden genau das: nur Gruen,
Referenz genau +1.

CGRAM hat 15 Bit. Der Recomp speichert Bit 15 so, wie der Gast es schreibt, snes9x loescht es;
verglichen werden deshalb nur die 15 Bit.

Nur Standardbibliothek (kein PIL), laeuft also auch mit dem MINGW64-Python.
"""
import argparse, json, os, struct, sys, tomllib

GR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MASKS = os.path.join(GR, "validation", "masks.toml")


def load_masks(path=MASKS):
    if not os.path.exists(path):
        return []
    with open(path, "rb") as f:
        masks = tomllib.load(f).get("mask", [])
    for m in masks:
        if not m.get("reason"):
            sys.exit(f"compare_dumps: Maske ohne Begruendung: {m}")
    return masks


def green_tags(path=MASKS):
    """Tags, deren Framebuffer den Gruen-Rest der snes9x-Farbmathe duldet."""
    if not os.path.exists(path):
        return set()
    with open(path, "rb") as f:
        entries = tomllib.load(f).get("fb_green", [])
    for e in entries:
        if not e.get("reason"):
            sys.exit(f"compare_dumps: fb_green ohne Begruendung: {e}")
    return {t for e in entries for t in e["tags"]}


FB_W = 256   # Framebuffer-Breite der Dumps (FF6 nutzt kein Hires)


def mask_ranges(masks, kind, tag):
    """(start, end) inklusiv aller Masken fuer Dateiart und Dump-Tag.

    fb-Masken duerfen statt start/end ein Rechteck `rect = [x0, y0, x1, y1]` (inklusiv) angeben;
    es wird in einen Bereich je Bildzeile aufgeloest.
    """
    out = []
    for m in masks:
        if m["file"] != kind or (m.get("tags") and tag not in m["tags"]):
            continue
        if "rect" in m:
            x0, y0, x1, y1 = m["rect"]
            out += [(y * FB_W + x0, y * FB_W + x1) for y in range(y0, y1 + 1)]
        else:
            out.append((m["start"], m["end"]))
    return out


def read_bmp(path):
    """24-bit-BMP ohne Kompression -> (Breite, Hoehe, Pixel [(r, g, b)] zeilenweise von oben)."""
    data = open(path, "rb").read()
    if data[:2] != b"BM":
        sys.exit(f"compare_dumps: kein BMP: {path}")
    off = struct.unpack_from("<I", data, 10)[0]
    w, h, _, bpp, comp = struct.unpack_from("<iiHHI", data, 18)
    if bpp != 24 or comp != 0:
        sys.exit(f"compare_dumps: nur 24-bit-BMP ohne Kompression: {path} ({bpp} bit, comp {comp})")
    stride = (w * 3 + 3) & ~3
    rows = range(abs(h) - 1, -1, -1) if h > 0 else range(abs(h))
    px = []
    for r in rows:
        base = off + r * stride
        px.extend((data[base + 3 * x + 2], data[base + 3 * x + 1], data[base + 3 * x])
                  for x in range(w))
    return w, abs(h), px


def ranges(idx, gap=16):
    out = []
    for i in idx:
        if out and i - out[-1][1] <= gap:
            out[-1][1] = i
        else:
            out.append([i, i])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref"); ap.add_argument("run"); ap.add_argument("tag")
    ap.add_argument("--masks", default=MASKS)
    ap.add_argument("--fb-tol", type=int, default=0)
    ap.add_argument("--fb-8bit", action="store_true")
    a = ap.parse_args()
    masks = load_masks(a.masks)
    bad = 0

    cache = {}

    def masked(kind, i):
        if kind not in cache:
            cache[kind] = mask_ranges(masks, kind, a.tag)
        return any(s <= i <= e for s, e in cache[kind])

    for kind in ("wram", "vram", "cgram", "oam"):
        pa, pb = (os.path.join(d, f"{a.tag}.{kind}.bin") for d in (a.ref, a.run))
        if not (os.path.exists(pa) and os.path.exists(pb)):
            print(f"{kind}: uebersprungen (fehlt: {'ref' if not os.path.exists(pa) else 'run'})")
            continue
        ra, rb = open(pa, "rb").read(), open(pb, "rb").read()
        n = min(len(ra), len(rb))
        if kind == "cgram":
            ra = bytes(v & 0x7f if i & 1 else v for i, v in enumerate(ra))
            rb = bytes(v & 0x7f if i & 1 else v for i, v in enumerate(rb))
        diff = [i for i in range(n) if ra[i] != rb[i] and not masked(kind, i)]
        print(f"{kind}: {len(diff)} Bytes unmaskiert abweichend" +
              ("" if len(ra) == len(rb) else f" (Laengen {len(ra)}/{len(rb)}!)"))
        if len(ra) != len(rb):
            bad += 1
        for s, e in ranges(diff)[:20]:
            print(f"   {s:#06x}-{e:#06x} ref={ra[s:e+1][:8].hex()} run={rb[s:e+1][:8].hex()}")
        bad += bool(diff)
    fa, fb = (os.path.join(d, f"{a.tag}.fb.bmp") for d in (a.ref, a.run))
    if os.path.exists(fa) and os.path.exists(fb):
        (wa, ha, pa_), (wb, hb, pb_) = read_bmp(fa), read_bmp(fb)
        if (wa, ha) != (wb, hb):
            print(f"fb: Groesse {(wa, ha)} != {(wb, hb)}"); bad += 1
        else:
            info = os.path.join(a.ref, f"{a.tag}.info.json")
            fmt = json.load(open(info)).get("fb_core_pixel_format") if os.path.exists(info) else None
            sh = 3 if fmt == "RGB565" and not a.fb_8bit else 0
            dp = [i for i, (p, q) in enumerate(zip(pa_, pb_))
                  if max(abs((u >> sh) - (v >> sh)) for u, v in zip(p, q)) > a.fb_tol
                  and not masked("fb", i)]
            green = 0
            if sh and a.tag in green_tags(a.masks):
                def only_green(i):
                    (r0, g0, b0), (r1, g1, b1) = ((c >> sh for c in px) for px in (pa_[i], pb_[i]))
                    return r0 == r1 and b0 == b1 and g0 == g1 + 1
                keep = [i for i in dp if not only_green(i)]
                green = len(dp) - len(keep)
                dp = keep
            print(f"fb: {len(dp)} Pixel abweichend (Toleranz {a.fb_tol}, "
                  f"{'5-Bit, Ref RGB565' if sh else '8-Bit'})"
                  + (f", {green} geduldet (Gruen +1, Farbmathe)" if green else ""))
            if dp:
                ys = [i // wa for i in dp]; xs = [i % wa for i in dp]
                print(f"   Bereich x {min(xs)}-{max(xs)}, y {min(ys)}-{max(ys)}")
            bad += bool(dp)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
