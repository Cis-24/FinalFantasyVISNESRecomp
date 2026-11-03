#!/usr/bin/env python3
"""recomp/symbols.toml = Kopf (alles vor dem ersten [[func]]) + symbols_import.toml
+ symbols_overrides.toml (Overrides gewinnen nach bank+addr).

Aufruf: python tools/ff6/symbols_sync.py
Jeder Override-Schluessel (emit, entry_m, entry_x, note, ...) wird uebernommen.

Namen aus C_CLASH bekommen in symbols.toml die Endung `_ff6`: Der Codegen legt je emittierter
Funktion einen Alias `void <Name>(CpuState *)` an, und diese Namen exportieren auch gelinkte
Bibliotheken (kernel32 CreateThread, gdi32 GetTextColor, user32 SetCursorPos; `nm` ueber die
Bibliotheken der Link-Zeile, 2026-11-03). promote_misses.py liest die Namen aus symbols.toml,
also landet der neue Name auch im generierten Block; der Import und die Overrides von Hand
behalten den Namen der Disassembly.
"""
import os, tomllib

C_CLASH = {"CreateThread", "GetTextColor", "SetCursorPos"}

GR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(GR, "recomp", "symbols.toml")
IMP = os.path.join(GR, "tools", "ff6", "symbols_import.toml")
OVR = os.path.join(GR, "tools", "ff6", "symbols_overrides.toml")


def funcs(path):
    with open(path, "rb") as f:
        return tomllib.load(f).get("func", [])


def fmt(v):
    return "true" if v is True else "false" if v is False else str(v) if isinstance(v, int) \
        else '"%s"' % str(v).replace("\\", "\\\\").replace('"', '\\"')


def main():
    head = open(OUT, encoding="utf-8").read()
    head = head[:head.index("\n[[func]]\nname")].rstrip() + "\n"
    merged = {(f["bank"], f["addr"].lower()): f for f in funcs(IMP)}
    for o in funcs(OVR):
        k = (o["bank"], o["addr"].lower())
        merged[k] = {**merged.get(k, {}), **o}
    out = [head]
    for k in sorted(merged):
        f = merged[k]
        name = f["name"] + "_ff6" if f["name"] in C_CLASH else f["name"]
        lines = ["[[func]]", f'name = "{name}"', f'addr = "{k[1]}"', f"bank = 0x{k[0]:02x}"]
        for key, v in f.items():
            if key not in ("name", "addr", "bank"):
                lines.append(f"{key} = {fmt(v)}")
        out.append("\n".join(lines) + "\n")
    new = "\n".join(out)
    if new != open(OUT, encoding="utf-8").read():
        open(OUT, "w", encoding="utf-8", newline="\n").write(new)
        print(f"symbols.toml aktualisiert ({len(merged)} Funktionen)")
    else:
        print(f"symbols.toml unveraendert ({len(merged)} Funktionen)")


if __name__ == "__main__":
    main()
