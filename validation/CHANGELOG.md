# Erwartungs-Changelog

Jede Änderung an `validation/expected/*.toml` (Ereignisse, Dump-Hashes) braucht hier einen
begründeten Eintrag (PLAN 5.3). Erzeugt werden die Erwartungen mit
`bash tools/ff6/regress.sh --quick --update`; geprüft ohne `--update`.

## 2026-11-06: r13_battle_commands2 erstmals gesetzt (szenengekeyt), `interpreted` von r05 und r06 neu
- `r13_battle_commands2.toml` neu: 22 Dumps, 130 Ereignisse, 17070 Frames, Lauf 39 s. Nur in `--full`. Zweiter Teil der Kampfbefehle (Lore, X-Magic, Morph, Revert, Runic, Capture, Jump, Control, Mimic, GP Rain, Rage, Row, Def), docs/STATUS.md „Route r13 Kampfbefehle, zweiter Teil“. 0 ROM-Misses, 4 geduldet, WRAM-Allowlist 261, interpretiert 170 110 922.
- Referenzvergleich gegen `work/ref/r13` (snes9x): alle 22 Dumps WRAM, VRAM, CGRAM, OAM, FB gleich, PPU-Write-Strom 22/22 gleich. Gegen snes9x nur szenengekeyt (PLAN Phase 8, Entscheidung 2026-11-05).
- `masks.toml`: 41 r05-Kampfmasken klassenweise um die r13-Tags ergänzt (`c01`-`c17`, `c_victory`, `c_msg1`-`c_msg3`, `c_after`), neuer Abschnitt r13 mit 178 Bereichen, 11 Bildrechtecken und 3 HDMA-Duldungen. Die r13-Tags sind eigene Namen, damit die r06-Masken (Tags `m01` usw.) nicht auf r13 greifen und umgekehrt; für r01-r12 ändert sich nichts.
- Miss-Runde: 3 Goto-Landungen aus der InitCmdSelectTbl von Hand (`InitLoreSelect`, `InitRageSelect`, `InitXMagicInput`), 6 Aufrufziele generiert (2809 → 2815). `src/gen` `fd76e7288a82faca` → `5bba91971854d0de` (32559 Roots, 37273 Varianten, 17061 AOT, 20212 LLE).
- `interpreted` neu, nur gemeldet: r05 144 401 549 → 144 401 172, r06 164 605 612 → 164 590 811 (die neuen AOT-Funktionen laufen dort kompiliert). Ereignisse und alle Hashes der 9 alten Erwartungen unverändert, die 7 anderen Dateien bytegleich.
- `regress.sh --full --update` grün (515 s), danach ohne `--update` 984 PASS, 0 FAIL (10 Routen, 447 s ohne Regen und Build). Logs `work/logs/r13_full_update.txt`, `r13_full_check.txt`.

## 2026-11-05: Pin-Wechsel snesrecomp `7b570a032de3` (OPT und plp), r06 `slot` und `interpreted` neu
- Pin `a76eb19a0d9d` → `7b570a032de3` (Patches 0011 Mode-2-Offset-per-Tile, 0012 lokale Dispatch unter `php`), docs/STATUS.md „Pin-Session 11-05 (OPT und plp)“.
- `r06_battle_commands.toml`: Bild-Hash von `slot` neu. Die Slot-Maske (Rechteck 74-181/163-210) ist aus `masks.toml` entfernt; mit 0011 ist das Bild gleich der Referenz `work/ref/r06` (0 Pixel Abweichung, alle 20 Dumps und PPU-Write-Ströme gleich). Alle anderen Dump-Hashes aller Routen bytegleich, Ereignisse unverändert.
- r05 und r06: geduldete Misses 11 → 6 und 9 → 4 (Sperre von `ValidateSpellList` aufgehoben; `ValidateSpellList`, `InitChars`, `InitBattle` AOT, Landungen C25704/C2570E entfallen; `miss_allowlist.toml` entsprechend), discoveries 272 → 267 und 270 → 265. 0 ROM-Misses in allen Routen.
- `interpreted` in allen 9 Routen neu: r01 19 173 642 → 19 173 704, r02 172 007 297 → 172 065 392, r03 130 101 727 → 130 160 058, r04 203 690 522 → 203 749 558, r05 144 346 121 → 144 401 549, r06 164 578 053 → 164 605 612, r10 167 737 344 → 167 794 565, r11 132 614 949 → 132 671 125, r12 142 419 448 → 142 475 479. Die Mehrarbeit liegt im Sound-Treiber: Eintritt von `ExecSound` (C50131-C50170) und Warteschleife von `InterruptSPC` (C505BF-C505C5) laufen nach Rückgaben an den Interpreter öfter interpretiert zu Ende, seit `PlaySong` als lokales Ziel in `ExecSound_ext` liegt (Ursache nicht abschließend belegt). Dafür entfallen Teile von `InitBattle` (C22402-C2240A).
- `src/gen` `a34a08df34089aac` → `fd76e7288a82faca` (32487 Roots, 37201 Varianten, 17025 AOT, 20176 LLE; Overrides 2809 generiert plus 40 von Hand, neu `ValidateSpellList`, `TfrGameSfxPtrs`, Funktionsgrenze `PlaySong`).

## 2026-11-05: r06_battle_commands erstmals gesetzt (szenengekeyt)
- `r06_battle_commands.toml` neu: 20 Dumps, 128 Ereignisse, 16554 Frames, Lauf 40 s. Nur in `--full`. 0 ROM-Misses, 9 geduldet, WRAM-Allowlist 261, interpretiert 164 578 053.
- Die Route lag in `validation/routes_pending/`. Geändert, damit die Szene auf beiden Seiten gleich bleibt (docs/STATUS.md, „r06 szenengekeyt gegen die Referenz“): Tanz Love Sonata statt Wind Song (kein Hintergrund-/Stolper-Wurf zur Ausführungszeit), Vicks' ATB danach auf 0, vor m13 auf die laufende Hauptschleife warten, im Schluss Sap von Wache 0 entfernen, drei Meldungen statt vier.
- Referenzvergleich gegen `work/ref/r06` (neu, snes9x-Lauf `r06L4`): alle 20 Dumps WRAM, VRAM, CGRAM, OAM, FB gleich, PPU-Write-Strom 20/20 gleich. Gegen snes9x nur szenengekeyt (PLAN Phase 8, Entscheidung 2026-11-05).
- `masks.toml`: 41 r05-Kampfmasken klassenweise um die r06-Tags ergänzt, neuer Abschnitt r06 mit 98 Bereichen, 5 Bildrechtecken und 3 HDMA-Duldungen. Darunter das Rechteck der Slot-Walzen wegen eines Framework-Fehlers im Mode-2-Offset-per-Tile (Maske entfällt mit dem Fix in der nächsten Pin-Session; dann ändert sich der fb-Hash von `slot`). Für die anderen Routen ändert sich nichts.
- Die 8 anderen Erwartungen bytegleich, auch `interpreted`. `regress.sh --full --update` und ohne `--update` grün, `src/gen` unverändert `a34a08df34089aac`.

## 2026-11-05: r05_first_battle erstmals gesetzt, r05 in der Schnell-Suite
- `r05_first_battle.toml` neu: 9 Dumps, 52 Ereignisse, 14006 Frames, Lauf 34 s. Die Route lag in `validation/routes_pending/`, bis ihre 14 ROM-Misses aufgelöst waren. Jetzt 0 ROM-Misses, 11 geduldet (4 Field wie r03, 7 Folgen der `ValidateSpellList`-Sperre), WRAM-Allowlist 261, interpretiert 144 346 121.
- Auflösung: Exit-Breiten aus dem Quelltext für die 7 Aufrufer von `CheckStatus` (pea-Parameter), `ExecAttack` (pea/rts-Schleife), `ExecSelfAttack` und `AIRand3` (pla/pla) in `recomp/bankc2.cfg`; `ExecSelfAttack` als Funktionsgrenze, die Goto-Landungen `InitMagitekSelect`, `MoveAnimDownLeft`, `MoveAnimLeft` als Funktionsgrenzen (`symbols_overrides.toml`, 18 Einträge von Hand, 2791 generiert). `CheckBattleEnd` neu in `miss_allowlist.toml` (Kette über CheckFinalBattle und RestartBattle zur gesperrten `ValidateSpellList`).
- Referenzvergleich gegen `work/ref/r05`: alle 9 Dumps WRAM, VRAM, CGRAM, OAM, FB gleich (Masken aus Abschnitt r05), PPU-Write-Strom 9/9 gleich.
- Die 7 anderen Erwartungen bytegleich, auch `interpreted`. `src/gen` jetzt `51b90d5a148671da` (32111 Roots, 16775 AOT, 20050 LLE).
- `QUICK` = r01 + r03 + r04 + r05.

## 2026-11-03: Kampf-Promotionen und r05 (pending), keine Erwartung geändert
- 2789 generierte Promotionen (vorher 1649), AOT 8670 → 16649, `src/gen` `87c89a729aa3c41d`. `ValidateSpellList` von Hand gesperrt (Framework-Fehler, docs/STATUS.md). Alle 7 Erwartungen (r01-r04, r10-r12) bytegleich, `regress.sh --full` ohne `--update` 816 PASS, `--quick` grün (183 s).
- `masks.toml`: neuer Abschnitt r05 (52 Einträge, nur r05-Tags), `rect` für Bildmasken; `b_dlg_north`, `b_after`, `b_dlg_next` in 16 r03-Field-Masken ergänzt. Für die anderen Tags ändert sich nichts.
- `compare_ppuw.py` fasst gleiche HDMAEN-Writes direkt hintereinander zusammen; das ändert für r01-r12 kein Ergebnis.
- `miss_allowlist.toml`: 6 Einträge als Folge der Sperre. r05 bekommt noch keine Erwartung: Die Route liegt in `validation/routes_pending/`, bis ihre 14 ROM-Misses aufgelöst sind.

## 2026-11-02: r12_menu_scroll erstmals gesetzt
- `r12_menu_scroll.toml` neu: 112 Dumps, 13670 Frames, Lauf 39 s. Die Route scrollt Item-, Magie-, Waffen- und Shop-Verkaufsliste mit einem Dump in jedem Frame der Scroll-Animation und hält die Richtungstasten (Wiederholrate). Nur in `--full`. 0 ROM-Misses, 2 geduldet, WRAM-Allowlist 261.
- Referenzvergleich gegen `work/ref/r12`: alle 112 Dumps WRAM, VRAM, CGRAM, OAM, FB gleich, PPU-Write-Strom 112/112 gleich (HDMA je Zeile, auch die BG1-Scroll-Tabelle `$7E:9849` in jedem Animationsbild).
- `masks.toml`: neuer Abschnitt r12 mit 6 Bereichen. Ohne Masken wichen nur `$0630-2`, `$F230-2`, `$10D1`, `$10E7` und der tote Stack unter MenuLoop ab. `$CF`, `$0228`, Spielzeit, Frame- und Wartezähler sind gleich: Die Route läuft auf beiden Seiten ohne Lag-Unterschied.
- Die 6 anderen Erwartungen bytegleich. `regress.sh --full` ohne `--update` 816 PASS, `--quick` grün (164 s), `src/gen` unverändert `17164c920592a4a6`.

## 2026-11-02: r04_menu_tour erstmals gesetzt, r04 in der Schnell-Suite
- `r04_menu_tour.toml` neu: 101 Dumps, 20636 Frames, Lauf 48 s. Die Route lag in `validation/routes_pending/`, bis ihre 184 ROM-Misses aufgelöst waren (Dispatch-Liste Menü: Resolver-Fix `MaxHPMPTbl`, Task-Dispatch `C31203`, Site `C33D40`, 1649 Promotionen). Jetzt 0 ROM-Misses, 2 geduldet, WRAM-Allowlist 261.
- Referenzvergleich gegen `work/ref/r04`: alle 101 Dumps WRAM, VRAM, CGRAM, OAM, FB gleich (Masken aus Abschnitt r04 in `masks.toml`), PPU-Write-Strom 101/101 gleich, SRAM nach beiden Speichervorgängen und nach dem Laden gleich.
- Die 5 anderen Erwartungen bytegleich, auch `interpreted`. `src/gen` jetzt `17164c920592a4a6` (8670 AOT statt 7424).
- `QUICK` = r01 + r03 + r04, 162 s mit Regen und Build.

## 2026-11-02: Pin-Wechsel snesrecomp `9745cb9c45c3`, keine Erwartung geändert
- Alle 5 Erwartungen (r01, r02, r03, r10, r11) bytegleich, `regress.sh --full` ohne `--update` grün (169 PASS). `src/gen` unverändert `7fc218bf3df4c2ff`, die Fixes liegen nur in `runner/src`.
- r04_menu_tour bekommt noch keine Erwartung: Die Route bleibt in `validation/routes_pending/`, bis ihre 184 ROM-Misses aufgelöst sind.

## 2026-10-31: r11_doors erstmals gesetzt
- `r11_doors.toml` neu: 6 Dumps, 12709 Frames, Lauf rund 30 s. Tür-Übergänge über die echten Trigger, je Long und Short hin und zurück. Nur in `--full`.
- Die 4 anderen Erwartungen bytegleich, `src/gen` unverändert `a7426f6f5321c606`.
- Referenzvergleich gegen `work/ref/r11`: alle 6 Dumps WRAM, VRAM, CGRAM, OAM, FB je 0 unmaskiert. 0 ROM-Misses, 4 geduldet, WRAM-Allowlist 261.
- `masks.toml`: Die 6 Tags stehen in denselben Listen wie die r10-Tags (`$1245-6`, `$021B-E`, `$0630-2`, `$F230-2`, toter Stack, BG3-Streifen in `[[ppuw]]`). Nur diese Bereiche wichen ab. Für die anderen Tags ändert sich nichts.

## 2026-10-31: Idle-Poll `C00566` deklariert, nur `interpreted` geändert
- `src/game_rtl.c`: Das Feld-`WaitVblank` (`lda $55 / beq`, reset.asm:780) steht in `kIdlePolls`. `src/gen` unverändert `a7426f6f5321c606`.
- In allen 4 Erwartungen ändert sich genau die Zeile `interpreted`: r01 19191836 → 19173642, r02 175195936 → 172007297, r03 133341722 → 130101727, r10 172558530 → 167737344. Ereignisse, alle Hashes und die `cpu_cycles` je Lauf sind gleich.

## 2026-10-31: Pin-Wechsel snesrecomp `3e17328d149d`, r10_field_modes erstmals gesetzt
- `r01_boot_title.toml`, `r02_new_game_to_narshe.toml`, `r03_field_walk.toml` bytegleich: Der Pin-Wechsel ändert keine Erwartung. `src/gen` unverändert `a7426f6f5321c606`, die Fixes liegen nur in `runner/src`.
- `r10_field_modes.toml` neu: 24 Dumps, 15678 Frames, Lauf 30 s. Die Route lag bis zum Pin in `validation/routes_pending/`, weil `m13d` und `m15f` ohne den Fix der DMA-Kanalregister rot sind.
- Referenzvergleich r10 gegen `work/ref/r10`: alle 24 Dumps WRAM, VRAM, CGRAM, OAM, FB je 0 unmaskiert. Grün-Rest in `m088`, `m185`, `m18a` über `[[fb_green]]` geduldet (Artefakt der Referenz). 0 ROM-Misses, 2 geduldet, WRAM-Allowlist 261.
- r10 läuft nur in `--full`, die Schnell-Suite bleibt r01 + r03.

## 2026-10-30: Referenz mit gepatchtem snes9x, CGRAM-Maske, drei neue Dispatch-Ziele
- `r01_boot_title.toml` bytegleich.
- `r02_new_game_to_narshe`: nur `interpreted` 175196581 → 175195936, weil `ObjCmd_c7/d5/fa` jetzt AOT sind. Ereignisse und alle Hashes gleich.
- `r03_field_walk`: `interpreted` 133342760 → 133341722 und die `cgram`-Hashes aller 6 Tags: Die neue Maske `$00BA-$00BB` (Eintrag `$5D` der Palettenanimation, Phase wie `$10E7`) setzt diese Bytes vor dem Hashen auf 0. Sonst unverändert, Ereignisse und die 5 anderen Hashes gleich.
- `src/gen` jetzt `a7426f6f5321c606` (8592 Roots, 4194 AOT, 5992 LLE).
- Die Referenzen `work/ref/r01..r03` stammen jetzt vom gepatchten Core (`toolchain/cores/snes9x_debug_libretro.dll`). Gegenprobe: alle WRAM-/VRAM-/SRAM-/FB-Dumps bitgleich zur Stock-Referenz. Neu verglichen: CGRAM, OAM (`compare_dumps.py`, Bit 15 ausgenommen), PPU-Write-Strom (`compare_ppuw.py`).

## 2026-10-30: r02_new_game_to_narshe und r03_field_walk erstmals gesetzt, r03 in der Schnell-Suite
- Stand: Pin `6f928388582a`, `src/gen` `f9343072b78737f0`, Lauf mit `validation/regress.ini`.
- r02: 10 Dumps, `control` bei Frame 18179 (Referenz 18191, Ladephasen im Recomp schneller; deshalb scene-keyed), `quit` bei 18179. ROM-Misses 0, geduldet 2, WRAM-Allowlist 263.
- r03: 6 Dumps, `quit` bei 12472. ROM-Misses 0, geduldet 4, WRAM-Allowlist 261.
- Referenzvergleich aller 16 Dumps gegen `work/ref/r02`, `r03`: WRAM 0 unmaskiert, VRAM 0, FB 0 (5 Bit). Masken in `validation/masks.toml`.
- Gegenprobe: Zweiter Lauf ohne `--update` besteht (Ereignisse, alle Hashes, Miss-Zahlen). `r01_boot_title.toml` blieb beim `--update` bytegleich.
- Schnell-Suite jetzt r01 + r03: 71 s (Regen 36 s, Build 3 s, r01 6 s, r03 23 s).

## 2026-10-30: Pin-Wechsel snesrecomp `6f928388582a` (RDNMI-Poll, Mosaik-Tabelle, HDMA ab V=0), Erwartungen unverändert
- Keine Änderung an `validation/expected/r01_boot_title.toml`. r01 besteht ohne `--update` (Ereignisse, alle 6 Hashes, Miss-Zahlen, Referenz).
- `src/gen` unverändert `f9343072b78737f0`: Die Fixes liegen nur in `runner/src`, der Generator-Digest bleibt gleich.

## 2026-10-30: Miss-Runden r02/r03, Erwartungen unverändert
- `validation/expected/r01_boot_title.toml` unverändert, besteht ohne `--update` mit Pin `1933c214865e`. `src/gen` jetzt `f9343072b78737f0` (8568 Roots, 4188 AOT, 5974 LLE).
- `regress.sh` läuft je Route im Laufverzeichnis: Jede Route startet mit leerem SRAM (`saves/save.srm` liegt relativ zur cwd). Vorher änderte ein r02-Lauf den SRAM-Hash von r01.
- `regress.ini`: `NoSpriteLimits = 0`, ohne Wirkung auf r01.
- Masken für die Tags von r02/r03 in `validation/masks.toml`; Tag `title` unberührt.
- Noch keine Erwartungen für r02/r03: Beide laufen erst mit den Framework-Fixes (`patches/snesrecomp/pending/`, docs/STATUS.md).

## 2026-10-30: 609er-Abschluss übernommen, nur Miss-Zahlen geändert
- `symbols_overrides.toml`: 422 → 609 generierte Einträge (7816 Roots, 3800 AOT-Varianten), `src/gen` `f0cb03876c8bcd6e`.
- `r01_boot_title`: Ereignisse und alle 6 Hashes unverändert, Referenz `title` weiter WRAM 0, VRAM 0, FB 0 (5 Bit).
- Miss-Zahlen: geduldet 4 → 1 (nur LoadMap; ExecEvent, EventCmd_b2/a9 aufgelöst, Allowlist entsprechend gekürzt),
  Discoveries 155 → 152, interpretiert 19 191 984 → 19 191 836. ROM-Misses 0, WRAM-Allowlist 151.

## 2026-10-30: Pin-Wechsel snesrecomp `1933c214865e` (JMP (abs) aus Bank 0), Erwartungen unverändert
- Keine Änderung an `validation/expected`. r01_boot_title besteht ohne `--update` (Ereignisse, alle 6 Hashes, Miss-Zahlen, Referenz).
- `src/gen` jetzt `ffae6649e29d9db5` statt `101a4528892ffe06`. Der generierte Code ist bitgleich; geändert sind nur
  `build_digest` (`module_v2.c`) und `.snesrecomp-cache.json`, weil beide einen Digest über die Generator-Quellen
  enthalten. A/B-Beleg: `work/logs/pin_jmpfix_gen_ab.txt`.

## 2026-10-29: r01_boot_title erstmals gesetzt
- Stand: `phase/05-title` nach 30c61f9, snesrecomp `4dcec90f44eb` (DSP-Einschaltwerte), `src/gen` `101a4528892ffe06`
  (5000 Roots, 2910 AOT-Varianten, 3418 LLE). Lauf mit `validation/regress.ini`.
- Ereignisse: `$19 == 9` bei Frame 3442 (snes9x-Referenz 3442), `dump title` und `quit` bei 3472.
- Hashes `title`: wram (Stack `$1508-$15EC` maskiert, `validation/masks.toml`), vram, cgram, oam, sram, fb.bgrx.
- Gegenproben (`work/regress_crosscheck.sh`, Log `work/logs/regress_crosscheck.out`):
  - Gebremster Lauf `r01_dsppin_final` (DisableFrameDelay = 0, 58 s) besteht mit denselben Hashes,
    Ereignissen und Miss-Zahlen wie der ungebremste Suite-Lauf (5 s). Die Echtzeitbremse ändert
    das Ergebnis also nicht.
  - Lauf mit aktivem Gamepad (`r01_dsppin`) fällt durch: wram.
  - Lauf vor dem DSP-Patch (`r01_idle`, Titel bei 3654) fällt durch: Ereignisse.
- Referenzvergleich `title` gegen `work/ref/r01`: WRAM 0, VRAM 0, FB 0 (5 Bit).
