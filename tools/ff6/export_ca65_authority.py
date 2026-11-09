#!/usr/bin/env python3
"""Export disassembly authority from the ff6 ca65/ld65 build (PLAN 3.2-3.5).

Inputs: ld65 debug file (dbginfo 2.0), the ff6 source tree, the owned ROM and the
freshly assembled image (must be byte-identical). Instruction lengths come from
the dbginfo spans, never from a decoder.

Outputs (all under work/ or tools/, none contain more than needed):
  --out-authority   snesrecomp disassembly authority v1 JSON (contains ROM bytes: NEVER commit)
  --out-symbols     TOML [[func]] list (names/addresses only)
  --out-report      text report: unknown spans, conflicts, label cross-check
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SCHEMA = "snesrecomp disassembly authority v1"

# Opcode length table, one 16-character row per high nibble. Digits are fixed byte
# counts; 'M'/'X' are immediates whose size depends on the accumulator / index width
# (2 bytes when 8-bit, 3 when 16-bit).
OPLEN = "".join([
    "222222221M113334", "2222222213113334", "32422222" "1M113334", "2222222213113334",
    "12223222" "1M113334", "2222322213114334", "12322222" "1M113334", "2222222213113334",
    "22322222" "1M113334", "2222222213113334", "X2X22222" "1M113334", "2222222213113334",
    "X2222222" "1M113334", "2222222213113334", "X2222222" "1M113334", "2222322213113334",
])
assert len(OPLEN) == 256, len(OPLEN)

MNEMONICS = set("""adc and asl bcc bcs beq bit bmi bne bpl bra brk brl bvc bvs clc cld cli clv cmp
cop cpx cpy dec dex dey eor inc inx iny jml jmp jsl jsr lda ldx ldy lsr mvn mvp nop ora pea pei
per pha phb phd phk php phx phy pla plb pld plp plx ply rep rol ror rti rtl rts sbc sec sed sei
sep sta stp stx sty stz tax tay tcd tcs tdc trb tsb tsc tsx txa txs txy tya tyx wai wdm xba xce
ina dea swa tad tda tas tsa bge blt""".split())
DATA_DIRS = {".byte", ".byt", ".word", ".addr", ".faraddr", ".dword", ".dbyt", ".lobytes",
             ".hibytes", ".bankbytes", ".res", ".incbin", ".asciiz", ".tag", ".align", ".literal"}
# Opcodes after which execution never falls through to the next byte.
TERMINATORS = {0x40, 0x4C, 0x5C, 0x60, 0x6B, 0x6C, 0x7C, 0x80, 0x82, 0xDC, 0xDB}
WIDTH_BREAK = {0xC2, 0xE2, 0x28, 0xFB}                 # rep sep plp xce
PREFIX_STOP = TERMINATORS | WIDTH_BREAK | {0x20, 0x22, 0xFC}   # jsr/jsl/jsr(abs,x) end the prefix
M_OPS = {0x09, 0x29, 0x49, 0x69, 0x89, 0xA9, 0xC9, 0xE9}
X_OPS = {0xA0, 0xA2, 0xC0, 0xE0}

KV = re.compile(r'(\w+)=("[^"]*"|[^,]*)')
LABEL_PREFIX = re.compile(r'^\s*(?:@?\w+|):{1,2}\s*')
IDENT = re.compile(r'^[A-Za-z][A-Za-z0-9_]*$')


def kv(rest):
    return {k: v.strip('"') for k, v in KV.findall(rest)}


def parse_dbg(path):
    """Return dict with files, segs (ROM only), spans (ROM only), lines, scopes, syms."""
    d = dict(files={}, segs={}, spans={}, lines={}, line_loc={}, scopes={}, syms=[], mods={},
             ram_segs=set(), ram_spans=set(), ram_lines=set())
    with open(path, encoding="utf-8", errors="replace") as f:
        for raw in f:
            tag, _, rest = raw.rstrip("\n").partition("\t")
            if tag == "file":
                r = kv(rest); d["files"][int(r["id"])] = r["name"]
            elif tag == "mod":
                r = kv(rest); d["mods"][int(r["id"])] = dict(name=r["name"], file=int(r.get("file", -1)))
            elif tag == "seg":
                r = kv(rest)
                if "ooffs" in r and int(r["start"], 0) < 0xC00000:    # RAM-resident code (7E/7F) stays interpreted
                    d["ram_segs"].add(int(r["id"]))
                if "ooffs" in r and int(r["start"], 0) >= 0xC00000:
                    d["segs"][int(r["id"])] = dict(name=r["name"], start=int(r["start"], 0),
                                                   size=int(r["size"], 0), ooffs=int(r["ooffs"]))
            elif tag == "span":
                r = kv(rest); seg = int(r["seg"])
                if seg in d["ram_segs"]:
                    d["ram_spans"].add(int(r["id"]))
                if seg in d["segs"]:
                    d["spans"][int(r["id"])] = dict(seg=seg, start=int(r["start"]),
                                                    size=int(r["size"]), typed="type" in r)
            elif tag == "line":
                r = kv(rest)
                d["line_loc"][int(r["id"])] = (int(r["file"]), int(r["line"]))
                if "span" in r:
                    d["lines"][int(r["id"])] = (int(r["file"]), int(r["line"]), int(r.get("type", 0)),
                                                [int(s) for s in r["span"].split("+")])
            elif tag == "scope":
                r = kv(rest)
                d["scopes"][int(r["id"])] = dict(name=r["name"], type=r.get("type", ""), mod=int(r.get("mod", 0)),
                                                 parent=int(r["parent"]) if "parent" in r else None,
                                                 spans=[int(s) for s in r["span"].split("+")] if "span" in r else [])
            elif tag == "sym":
                r = kv(rest)
                if r.get("type") == "lab" and "seg" in r and int(r["seg"]) in d["segs"]:
                    d["syms"].append(dict(name=r["name"], val=int(r["val"], 0), scope=int(r.get("scope", 0)),
                                          ref=[int(x) for x in r["ref"].split("+")] if "ref" in r else []))
    # The dbg lists line records before seg/span records, so RAM lines are known only now.
    for fid, ln, _lt, sps in d["lines"].values():
        if d["ram_spans"].intersection(sps):
            d["ram_lines"].add((d["files"].get(fid, "").lstrip("./"), ln))
    return d


class Sources:
    def __init__(self, root):
        self.root, self.cache = Path(root), {}

    def text(self, name, line):
        lines = self.cache.get(name)
        if lines is None:
            p = self.root / name
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines() if p.exists() else []
            self.cache[name] = lines
        return lines[line - 1] if 1 <= line <= len(lines) else ""


def statement(text):
    text = text.split(";", 1)[0]
    while True:
        m = LABEL_PREFIX.match(text)
        if not m or not m.group(0).strip():
            break
        text = text[m.end():]
    return text.strip()


OP_ALIASES = set()          # statements that emit instructions (inx2, asl4, ldaflg, clrflg ...)
DATA_ALIASES = set()        # statements that emit data (bg_pos ...)
OP_WRAPPERS = set()         # macros whose first parameter is the operation they emit (opflg, op_pos)
OP_ALIAS_DEF = re.compile(r'^\.define\s+(\w+)\s+op_n\s+(\w+)\s*,', re.I)
WRAPPED_ALIAS_DEF = re.compile(r'^\.define\s+(\w+)\s+(\w+)\s+(\.?\w+)', re.I)
MAC_DEF = re.compile(r'^\s*\.mac(?:ro)?\s+(\w+)\s*(.*)$', re.I)
MAC_END = re.compile(r'^\s*\.endmac(?:ro)?\b', re.I)
CONTROL = re.compile(r'^\.(if\w*|else\w*|endif|local|assert|warning|error|out|set)\b', re.I)


def macro_files(root):
    """Macro sources: src/common/*.inc and every *.mac under src (e.g. menu/menu.mac)."""
    src = Path(root) / "src"
    return sorted(set((src / "common").glob("*.inc")) | set(src.rglob("*.mac")))


def load_op_aliases(root):
    """Fill OP_ALIASES, DATA_ALIASES and OP_WRAPPERS from the macro sources.

    - `.define x op_n <mnemonic>, N` (inx2, asl4, nop3 ...): code.
    - A `.mac` whose first parameter is `op` or `prefix` emits that operation (opflg, op_pos,
      make_bitmask, array_op): a statement using it is classified by its first argument.
    - `.define x <wrapper> <op>` (ldaflg = opflg lda #, bg_pos = op_pos .addr): code or data
      by <op>.
    - A `.mac` whose body statements (assembler control lines aside) are all code (clrflg):
      code; all data (window_pos): data. Repeated until nothing changes, since macros use
      each other.
    Returns the code aliases (also kept in OP_ALIASES)."""
    OP_ALIASES.clear()
    DATA_ALIASES.clear()
    OP_WRAPPERS.clear()
    macros, defines = {}, []
    for p in macro_files(root):
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        i = 0
        while i < len(lines):
            m = MAC_DEF.match(lines[i])
            if m:
                params = [x.strip().lower() for x in m.group(2).split(";", 1)[0].split(",") if x.strip()]
                body = []
                i += 1
                while i < len(lines) and not MAC_END.match(lines[i]):
                    body.append(lines[i])
                    i += 1
                macros[m.group(1).lower()] = (params, body)
            else:
                defines.append(lines[i])
            i += 1
    OP_WRAPPERS.update(n for n, (params, _) in macros.items() if params and params[0] in ("op", "prefix"))
    for line in defines:
        m = OP_ALIAS_DEF.match(line)
        if m and m.group(2).lower() in MNEMONICS:
            OP_ALIASES.add(m.group(1).lower())
            continue
        m = WRAPPED_ALIAS_DEF.match(line)
        if m and m.group(2).lower() in OP_WRAPPERS:
            op = m.group(3).lower()
            if op in MNEMONICS:
                OP_ALIASES.add(m.group(1).lower())
            elif op in DATA_DIRS:
                DATA_ALIASES.add(m.group(1).lower())
    changed = True
    while changed:
        changed = False
        for name, (_, body) in macros.items():
            if name in OP_ALIASES or name in DATA_ALIASES or name in OP_WRAPPERS:
                continue
            stmts = [statement(b) for b in body]
            kinds = {text_kind(s) for s in stmts if s and not CONTROL.match(s)}
            if kinds == {"code"}:
                OP_ALIASES.add(name)
                changed = True
            elif kinds == {"data"}:
                DATA_ALIASES.add(name)
                changed = True
    return set(OP_ALIASES)


def text_kind(text):
    words = statement(text).split(None, 2)
    if not words:
        return "other"
    w = words[0].lower()
    if w in OP_WRAPPERS and len(words) > 1:
        w = words[1].rstrip(",").lower()      # the operation passed to the wrapper
    if w in MNEMONICS or w in OP_ALIASES:
        return "code"
    if w in DATA_DIRS or w in DATA_ALIASES:
        return "data"
    return "other"


def instruction_size_ok(op, size):
    n = OPLEN[op]
    if n in "MX":
        return size in (2, 3)
    return size == int(n)


def finest_spans(dbg):
    """Span ids without the macro/aggregate spans that merely contain finer spans."""
    segs, spans = dbg["segs"], dbg["spans"]
    pos = {}
    for sid, sp in spans.items():
        pc = segs[sp["seg"]]["start"] + sp["start"]
        pos.setdefault(pc, set()).add(sp["size"])
    keys = sorted(pos)
    from bisect import bisect_left
    keep = []
    for sid, sp in spans.items():
        pc, end = segs[sp["seg"]]["start"] + sp["start"], segs[sp["seg"]]["start"] + sp["start"] + sp["size"]
        container = False
        for i in range(bisect_left(keys, pc), len(keys)):
            pc2 = keys[i]
            if pc2 >= end:
                break
            if any(sz2 < sp["size"] and pc2 + sz2 <= end for sz2 in pos[pc2]) or (pc2 > pc and any(pc2 + sz2 <= end for sz2 in pos[pc2])):
                container = True
                break
        if not container:
            keep.append(sid)
    return keep


def enclosing_spans(spans, segs):
    """Lookup of spans that contain a given span (aggregate/macro spans), nearest first."""
    from bisect import bisect_right
    order = sorted((segs[sp["seg"]]["start"] + sp["start"], sp["size"], sid) for sid, sp in spans.items())
    keys = [o[0] for o in order]

    def find(sid):
        sp = spans[sid]
        a = segs[sp["seg"]]["start"] + sp["start"]
        e = a + sp["size"]
        out = []
        for i in range(bisect_right(keys, a) - 1, max(bisect_right(keys, a) - 600, -1), -1):
            pc, size, t = order[i]
            if t != sid and pc <= a and pc + size >= e and size > sp["size"]:
                out.append(t)
        return out
    return find


def build(dbg, srcs, rom):
    segs, spans = dbg["segs"], dbg["spans"]
    load_op_aliases(srcs.root)
    find_enclosing = enclosing_spans(spans, segs)
    by_span = {}
    for lid, (fid, ln, lt, sp) in dbg["lines"].items():
        for s in sp:
            if s in spans:
                by_span.setdefault(s, []).append((fid, ln, lt))
    rep = dict(unknown=[], conflicts=[], uncovered=0, containers=0)
    rows = {}                         # pc24 -> record
    for sid in finest_spans(dbg):
        sp = spans[sid]
        seg = segs[sp["seg"]]
        pc = seg["start"] + sp["start"]
        off = seg["ooffs"] + sp["start"]
        size = sp["size"]
        if size <= 0 or off + size > len(rom):
            continue
        kinds, src = set(), None
        for fid, ln, lt in by_span.get(sid, []):
            name = dbg["files"].get(fid, "?")
            k = text_kind(srcs.text(name.lstrip("./") if name.startswith("./") else name, ln))
            if k != "other":
                kinds.add(k)
            if src is None or lt != 2:
                src = f"{name}:{ln}"
        via = ""
        if not kinds and not sp["typed"]:
            # Macro-expanded bytes: the leaf span has no readable statement of its own, so use
            # the invocation / macro-body lines of the spans that contain it.
            outer = set()
            for t in find_enclosing(sid):
                for fid, ln, lt in by_span.get(t, []):
                    k = text_kind(srcs.text(dbg["files"].get(fid, "?").lstrip("./"), ln))
                    if k != "other":
                        outer.add(k)
            if len(outer) == 1:
                kinds, via = outer, " (via enclosing span)"
        if sp["typed"] and "code" in kinds:
            kind = "unknown"
        elif sp["typed"]:
            kind = "data"
        elif kinds == {"code"}:
            kind = "code"
        elif kinds == {"data"}:
            kind = "data"
        else:
            kind = "unknown"
        prev = rows.get(pc)
        if prev and prev["kind"] != kind:
            rep["conflicts"].append(f"{pc:06X} classified both {prev['kind']} and {kind}")
            kind = "unknown"
        rows[pc] = dict(kind=kind, size=size, off=off, src=(src or "?") + via, seg=seg["name"])

    instructions, entries_src = [], {}
    pcs = sorted(rows)
    # Data runs inside code segments directly after a fall-through instruction are not
    # provably data (BIT-skip trick, hand-coded opcodes): demote them to unknown.
    prev_code = None
    for pc in pcs:
        r = rows[pc]
        if r["kind"] == "code":
            op = rom[r["off"]]
            if not instruction_size_ok(op, r["size"]) or (pc & 0xFFFF) + r["size"] > 0x10000:
                rep["conflicts"].append(f"{pc:06X} {r['src']} length {r['size']} vs opcode {op:02X}")
                r["kind"] = "unknown"
                prev_code = None
                continue
            prev_code = (pc, op)
        elif r["kind"] == "data":
            if prev_code and r["seg"].endswith(("_code", "_code_far")) and prev_code[0] + rows[prev_code[0]]["size"] == pc \
                    and prev_code[1] not in TERMINATORS:
                r["kind"] = "unknown"
                r["why"] = "data after fall-through instruction in code segment"
            prev_code = None
        else:
            prev_code = None

    data = []
    for pc in pcs:
        r = rows[pc]
        end = pc + r["size"]
        if r["kind"] == "code":
            instructions.append(dict(pc24=f"0x{pc:06X}", bytes=rom[r["off"]:r["off"] + r["size"]].hex(), source=r["src"]))
        elif r["kind"] == "data":
            bank_end = ((pc >> 16) + 1) << 16
            if data and int(data[-1]["end_pc24"], 0) == pc and (pc & 0xFFFF):
                data[-1]["end_pc24"] = f"0x{min(end, bank_end):06X}"
            else:
                data.append(dict(start_pc24=f"0x{pc:06X}", end_pc24=f"0x{min(end, bank_end):06X}"))
        else:
            rep["unknown"].append((pc, r["size"], r["src"], r.get("why", "unclassified")))
    return rows, instructions, data, rep


def find_entries(dbg, rows, rom):
    """Entry points with proven M and X from the linear instruction prefix (PLAN 3.4)."""
    starts = set()
    for sc in dbg["scopes"].values():
        if sc["type"] == "scope" and sc["spans"]:
            addrs = [dbg["segs"][dbg["spans"][s]["seg"]]["start"] + dbg["spans"][s]["start"]
                     for s in sc["spans"] if s in dbg["spans"]]
            if addrs:
                starts.add(min(addrs))
    entries, partial = [], 0
    for pc in sorted(starts):
        m = x = None
        cur = pc
        while cur in rows and rows[cur]["kind"] == "code":
            r = rows[cur]
            op = rom[r["off"]]
            if op in M_OPS and m is None:
                m = 1 if r["size"] == 2 else 0
            if op in X_OPS and x is None:
                x = 1 if r["size"] == 2 else 0
            if (m is not None and x is not None) or op in PREFIX_STOP:
                break
            cur += r["size"]
        if m is not None and x is not None:
            entries.append(dict(pc24=f"0x{pc:06X}", m=m, x=x))
        elif m is not None or x is not None:
            partial += 1
    return entries, partial


def scope_path(dbg, sid):
    parts = []
    while sid is not None and sid in dbg["scopes"]:
        n = dbg["scopes"][sid]["name"]
        if n:
            parts.append(n)
        sid = dbg["scopes"][sid]["parent"]
    return list(reversed(parts))


def collect_symbols(dbg, rows):
    """Procs plus referenced global labels that sit on authoritative instruction starts."""
    funcs, taken = [], {}
    for sc in sorted(dbg["scopes"].values(), key=lambda s: s["name"]):
        if sc["type"] != "scope" or not sc["spans"] or not IDENT.match(sc["name"]):
            continue
        addrs = [dbg["segs"][dbg["spans"][s]["seg"]]["start"] + dbg["spans"][s]["start"]
                 for s in sc["spans"] if s in dbg["spans"]]
        if addrs:
            pc = min(addrs)
            if rows.get(pc, {}).get("kind") == "code":
                taken.setdefault(pc, sc["name"])
    for s in dbg["syms"]:
        if IDENT.match(s["name"]) and rows.get(s["val"], {}).get("kind") == "code" \
                and not s["name"].startswith("LOCAL") and s["val"] not in taken:
            path = scope_path(dbg, s["scope"])
            if len(path) <= 1:                       # module/global scope only
                taken[s["val"]] = s["name"]
    names = {}
    for pc, name in taken.items():
        names.setdefault(name, []).append(pc)
    for pc in sorted(taken):
        name = taken[pc]
        if len(names[name]) > 1:                     # duplicate in several modules
            name = f"{name}_{pc:06X}"
        funcs.append(dict(name=name, addr=f"{pc & 0xFFFF:04x}", bank=pc >> 16,
                          emit=name.endswith("_ext") or name.endswith("_Ext")))
    return funcs


def toml_funcs(funcs, header):
    out = [header.rstrip() + "\n"]
    for f in funcs:
        out.append("[[func]]\nname = \"%s\"\naddr = \"%s\"\nbank = 0x%02x\nemit = %s\n"
                   % (f["name"], f["addr"], f["bank"], "true" if f["emit"] else "false"))
    return "\n".join(out)


def merge_overrides(funcs, overrides_path):
    """Overrides win by (bank, addr). Returns the merged list."""
    if not overrides_path or not Path(overrides_path).exists():
        return funcs
    try:
        import tomllib
    except ImportError:                              # pragma: no cover
        import tomli as tomllib
    ov = tomllib.loads(Path(overrides_path).read_text(encoding="utf-8")).get("func", [])
    merged = {(f["bank"], f["addr"]): f for f in funcs}
    for o in ov:
        merged[(o["bank"], o["addr"].lower())] = {**merged.get((o["bank"], o["addr"].lower()), {}), **o}
    return [merged[k] for k in sorted(merged)]


def label_crosscheck(dbg, rows):
    """`@xxxx:` source labels carry the original 16-bit address (PLAN 3.2)."""
    bad, n = [], 0
    for s in dbg["syms"]:
        m = re.fullmatch(r"@([0-9a-fA-F]{4})", s["name"])
        if m:
            n += 1
            if int(m.group(1), 16) != s["val"] & 0xFFFF:
                bad.append(f"{s['name']} != {s['val'] & 0xFFFF:04X}")
    return n, bad


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if p and Path(p).exists() else None


def export(dbg_path, source_root, rom_path, assembled_path, out_authority, out_symbols,
           out_report, overrides=None, ca65=None, source_commit=None, sites=None, out_merged=None):
    rom = Path(rom_path).read_bytes()
    if len(rom) % 0x8000 == 0x200:
        rom = rom[0x200:]
    assembled = Path(assembled_path).read_bytes()
    if assembled != rom:
        raise SystemExit("assembled image differs from --rom; refusing to export")
    dbg = parse_dbg(dbg_path)
    srcs = Sources(source_root)
    rows, instructions, data, rep = build(dbg, srcs, rom)
    entries, partial = find_entries(dbg, rows, rom)
    imported = collect_symbols(dbg, rows)
    funcs = merge_overrides(imported, overrides)
    dispatches, dsites, dropped = [], 0, []
    if sites:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import dispatch_sites
        dispatches, dsites, dropped = dispatch_sites.build_dispatches(dispatch_sites.load(sites), dbg, rows, rom)
    n_lab, bad_lab = label_crosscheck(dbg, rows)
    auth = dict(schema=SCHEMA, rom_sha256=hashlib.sha256(rom).hexdigest(), instructions=instructions,
                entries=entries, data_regions=data, dispatches=dispatches,
                unknown_source_spans=[[f"{pc:06X}", n, s, why] for pc, n, s, why in rep["unknown"]],
                provenance=dict(source_commit=source_commit, assembled_sha256=hashlib.sha256(assembled).hexdigest(),
                                dbg_sha256=sha256_file(dbg_path), ca65_sha256=sha256_file(ca65),
                                exporter_sha256=sha256_file(__file__), format="ca65-dbginfo-2.0"))
    for p in (out_authority, out_symbols, out_report):
        Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(out_authority).write_text(json.dumps(auth, indent=1) + "\n", encoding="utf-8")
    Path(out_symbols).write_text(toml_funcs(funcs, "# Generated by tools/ff6/export_ca65_authority.py - do not edit.\n"),
                                 encoding="utf-8")
    lines = [f"instructions {len(instructions)}", f"data_regions {len(data)}", f"entries {len(entries)} (partial M/X only: {partial})",
             f"funcs {len(funcs)}", f"unknown spans {len(rep['unknown'])}", f"conflicts {len(rep['conflicts'])}",
             f"@xxxx labels checked {n_lab}, mismatches {len(bad_lab)}",
             f"dispatches {len(dispatches)} from {dsites} sites, {len(dropped)} targets dropped", ""]
    lines += ["dropped: " + d for d in dropped[:200]]
    lines += ["conflict: " + c for c in rep["conflicts"][:100]]
    lines += ["label: " + b for b in bad_lab[:50]]
    lines += [f"unknown {pc:06X} len {n} {s} ({why})" for pc, n, s, why in rep["unknown"][:300]]
    Path(out_report).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return auth, rep


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for n in ("dbg", "source-root", "rom", "assembled-rom", "out-authority", "out-symbols", "out-report"):
        ap.add_argument("--" + n, required=True, type=Path)
    ap.add_argument("--overrides", type=Path)
    ap.add_argument("--ca65", type=Path)
    ap.add_argument("--sites", type=Path, help="tools/ff6/dispatch_sites.toml")
    ap.add_argument("--out-merged", type=Path, help="symbols.toml candidate (import + overrides)")
    a = ap.parse_args()
    commit = None
    try:
        commit = subprocess.check_output(["git", "-C", str(a.source_root), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        pass
    auth, rep = export(a.dbg, a.source_root, a.rom, a.assembled_rom, a.out_authority, a.out_symbols,
                       a.out_report, a.overrides, a.ca65, commit, a.sites, a.out_merged)
    print(f"{len(auth['instructions'])} instructions, {len(auth['data_regions'])} data regions, "
          f"{len(auth['entries'])} entries, {len(auth['dispatches'])} dispatches, {len(rep['unknown'])} unknown, {len(rep['conflicts'])} conflicts")
    return 1 if rep["conflicts"] else 0


if __name__ == "__main__":
    sys.exit(main())
