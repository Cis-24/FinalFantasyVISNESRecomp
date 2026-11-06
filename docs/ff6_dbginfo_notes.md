# ff6 dbginfo notes (ff6-en.dbg, ld65 dbgfile version 2.0)
First written outside the game repository, which did not exist yet; it has since moved to `docs/`.
Sample taken 2026-10-28, build cc65 V2.19.

File: 76 MB; info: seg=163, scope=6930, sym=183776, span=529876, line=400800, type=51.

## Findings
1. `.addr` tables (EventCmdTbl @ C0:98C4, BattleEventCmdTbl @ C1:FDBE): YES, typed.
   Each entry is its own `span` (size=2) with `type=2` (type value `80014100`) at a
   segment-relative offset; next to them is an untyped span for the whole table (EventCmdTbl: size 406, 203 entries).
2. Instruction spans: NO `type` (size 1 to 4, e.g. in ClearDlgTextTiles). 268914 of 529876 spans are untyped
   (this includes instructions as well as whole-table and line spans).
3. `scope type=scope` with `size`: 5824 scopes, only 773 of them with `size` (and `span=`);
   430 with `sym=`. Procs with code (e.g. ClearDlgTextTiles size=34) have `size` and a `span` list;
   empty and namespace scopes do not. Scope id=0 is the module root (size/span per segment).

## Type table (size -> type ID, value), by frequency
- 1 byte: type 1 (`800120`), 145596x
- 2 byte: type 16 (`800220`) 48939x; type 2 (`80014100`, .addr) 20954x; type 0 (`800121`) 16571x
- 3 byte: type 24 (`80014200`) 8741x (probably .faraddr); type 7 (`800320`) 6103x
- 16 byte: type 5 (`801020`) 6421x
Type IDs depend on the build, so never hard-wire them; resolve them through the `type` records (`val`).
Reading 2 as .addr and 24 as .faraddr is inferred from size and position, not checked against the ca65 docs.

## Open
- Verify the type value encoding (ca65 type string) against the cc65 docs or source before section 3.3 relies on it.
