# ff6 dbginfo Notes (ff6-en.dbg, ld65 dbgfile version 2.0)
Vorläufiger Ort (GR existiert noch nicht), in Phase 3 nach GR\docs\ff6_dbginfo_notes.md verschieben.
Stichprobe 2026-10-28, Build cc65 V2.19.

Datei: 76 MB; info: seg=163, scope=6930, sym=183776, span=529876, line=400800, type=51.

## Ergebnisse
1. `.addr`-Tabellen (EventCmdTbl @ C0:98C4, BattleEventCmdTbl @ C1:FDBE): JA, typisiert.
   Jeder Eintrag ist ein eigener `span` (size=2) mit `type=2` (Typ-Wert `80014100`) an
   seg-relativem Offset; daneben ein untypisierter Gesamt-Span (EventCmdTbl: size 406, 203 Einträge).
2. Instruktions-Spans: KEIN `type` (Größe 1 bis 4, z. B. in ClearDlgTextTiles). 268914 von 529876 Spans untypisiert
   (enthält Instruktionen und Gesamt-/Zeilenspans).
3. `scope type=scope` mit `size`: 5824 Scopes, davon nur 773 mit `size` (und `span=`);
   430 mit `sym=`. Procs mit Code (z. B. ClearDlgTextTiles size=34) haben `size` + `span`-Liste;
   leere/Namespace-Scopes nicht. Scope id=0 ist Modul-Wurzel (size/span je Segment).

## Typ-Tabelle (Größe -> Typ-ID, Wert), nach Häufigkeit
- 1 byte: type 1 (`800120`), 145596x
- 2 byte: type 16 (`800220`) 48939x; type 2 (`80014100`, .addr) 20954x; type 0 (`800121`) 16571x
- 3 byte: type 24 (`80014200`) 8741x (vermutl. .faraddr); type 7 (`800320`) 6103x
- 16 byte: type 5 (`801020`) 6421x
Typ-IDs sind buildabhängig → nicht fest verdrahten, über `type`-Records (`val`) auflösen.
Die Deutung 2=.addr, 24=.faraddr ist aus Größe + Position abgeleitet, nicht in ca65-Doku geprüft.

## Offen
- Typ-Wert-Kodierung (ca65 Typstring) gegen cc65-Doku/Quelle verifizieren, bevor Abschnitt 3.3 sie nutzt.
