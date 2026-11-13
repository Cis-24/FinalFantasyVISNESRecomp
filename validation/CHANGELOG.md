# Expectations changelog

Every change to `validation/expected/*.toml` (events, dump hashes) needs a justified
entry here (PLAN 5.3). The expectations are written with
`bash tools/ff6/regress.sh --quick --update` and checked without `--update`.

## 2026-11-13: New route r23_battle_blitz, expectation `r23_battle_blitz.toml` added, existing expectations unchanged
- `validation/routes/r23_battle_blitz.txt`: one battle against the Narshe guards in which Terra (Fight with Man Eater, Blitz, Item, Lore) enters all eight Blitz codes (Pummel, Aura Bolt, Suplex, Fire Dance, Mantra, Air Blade, Bum Rush, and Spiraler last, which removes her), uses an Elixir with the target cursor moved right, left, left and right, and the battle ends through the dead status poke on the guards followed by the Spiraler action. It reaches 21 further dispatch targets (758 to 779 of 1079, `docs/battle_dispatch_coverage.md`); the four sites of `key_target_left` and `key_target_right` run for the first time. No snes9x reference.
- 18 ROM misses in the first full run (14 call gaps, 4 goto landings), all in the target cursor code that no route had run: resolved by 13 hand entries in `tools/ff6/symbols_overrides.toml` (the callees `key_target_left`, `key_target_right`, `GetTargetCursorPosition`, `GetAttackerCursorPosition`, `get_no`, `get_mon_length`, `SelectMonsterLeft`, `SelectMonsterRight`, `get_r_mon_set`, and the four landings of the normal battle type as function boundaries), all entered with M1X0 as observed; `src/gen` `cd7bbb3b0d44000d`. Then 0 ROM misses, no tripwires.
- Co-sim A vs B (A rebuilt from the new `src/gen`): no lasting divergence over 25395 checkpoints (196 transients). `regress.sh --full --update` rewrote the other expectations without a diff, 719 PASS, 0 FAIL (log `work/logs/r23_full_update2.txt`).
- No other expectation changed.

## 2026-11-13: New route r22_battle_effects, expectation `r22_battle_effects.toml` added, existing expectations unchanged
- `validation/routes/r22_battle_effects.txt`: three battles against the Narshe guards for the special effect handlers (`DoAttackerEffect`, `DoTargetEffect`) and the tools table of `CalcItemEffect`. Each member carries a weapon with a special effect in each hand (15 weapons over the three battles), Terra casts all 24 lores (Aqua Rake a second time as the ending of battle 1), uses the eight tools and Elixir, Megalixir, Super Ball, Magicite and Smoke Bomb. Battle 1 ends with Exploder (Terra has Life 3 by poke and is raised) and Aqua Rake, battle 2 with Pep Up and a released Vicks, battle 3 with the Smoke Bomb escape. It reaches 68 further dispatch targets (690 to 758 of 1079, `docs/battle_dispatch_coverage.md`), 21 of them in `DoAttackerEffect` and 13 in `DoTargetEffect`. No snes9x reference.
- Co-sim A vs B: no lasting divergence over 65948 checkpoints (398 transients). An earlier version that ended battle 1 with Exploder on the last guard at 1 HP split for good at the victory song transfer (checkpoint 44168), see docs/STATUS.md, "Co-sim: split at a victory song transfer (11-13)"; that ending is not in the route.
- 0 ROM misses, no tripwires, no recomp change; `src/gen` stays `2d2de2700d93203d`. `regress.sh --full --update` rewrote the other expectations without a diff, 716 PASS, 0 FAIL for the version before the battle 1 change (log `work/logs/r22_full_update.txt`) and 714 PASS, 0 FAIL with `--no-regen --no-build` for the final one (`work/logs/r22_full_update2.txt`).
- No other expectation changed.

## 2026-11-13: New route r21_battle_summons, expectation `r21_battle_summons.toml` added, existing expectations unchanged
- `validation/routes/r21_battle_summons.txt`: Terra summons all 27 espers through the esper window of the Magic menu in three battles against the Narshe guards (the first esper of each battle equipped via `$161E`, the others set in the battle state as `ValidateSpellList` fills it at init); Shoat and Odin end battles 1 and 2, battle 3 ends with Ragnarok, Raiden and one Fight. Co-sim A vs B: no lasting divergence over 55353 checkpoints (634 transients). It reaches 79 further dispatch targets (611 to 690 of 1079, `docs/battle_dispatch_coverage.md`), most of them in the animation scripts. No snes9x reference.
- 0 ROM misses, no tripwires, no recomp change; `src/gen` stays `2d2de2700d93203d`. `regress.sh --full --update` rewrote the other expectations without a diff, 713 PASS, 0 FAIL (log `work/logs/r21_full_update.txt`).
- Battles 1 and 3 start after a wait of 30 frames, battle 2 after 40: with 30 the co-sim diverges for good at the start of battle 2 (the battle start phase, see docs/STATUS.md, "r17 battle start phase").
- No other expectation changed.

## 2026-11-13: New route r20_battle_bosses, expectation `r20_battle_bosses.toml` added, existing expectations unchanged
- `validation/routes/r20_battle_bosses.txt`: six boss battles (battle ids 387, 452, 444, 462, 440, 460 of `BattleMonsters`; Ultros, Sr. Behemoth, Umaro and three more) in which the bosses run their AI scripts and dialog while the party's ATB is held at 0 and A is pressed once a second; Ultros is then beaten with Fights, the others get the dead status by poke. One ROM miss (`WaitDlgScroll`, `C15E1C`, call gap from the dialog page wait) resolved by a hand entry in `symbols_overrides.toml`; `src/gen` `2d2de2700d93203d`. Co-sim A vs B: no lasting divergence over 39097 checkpoints (296 transients). No tripwires, `regress.sh --full --update` 710 PASS, all old expectations byte-identical. No snes9x reference. +48 dispatch targets (611 of 1079, see `docs/battle_dispatch_coverage.md`).

## 2026-11-12: New route r19_battle_monsters, expectation `r19_battle_monsters.toml` added, existing expectations unchanged
- `validation/routes/r19_battle_monsters.txt`: five battles (battle ids 235, 64, 17, 38, 158 of `BattleMonsters`) of monsters whose AI scripts use conditions, commands and targets that r05 to r18 never ran, with the party at 9999 HP in battle and level and experience reset before each battle. Co-sim A vs B: no lasting divergence over 21473 checkpoints (281 transients). 0 ROM misses, no tripwires, `regress.sh --full --update` 707 PASS, all old expectations byte-identical. No snes9x reference. +28 dispatch targets (563 of 1079, see `docs/battle_dispatch_coverage.md`).

## 2026-11-12: New route r18_battle_levelup, expectation `r18_battle_levelup.toml` added, existing expectations unchanged
- `validation/routes/r18_battle_levelup.txt`: three battles in which the party (level 1, a little experience set by poke) levels up at the victory with an esper equipped, so `CheckLevelUp`, `DoLevelUp` and the esper bonus table (`GenjuBonusTbl`, hit 0 times before) run: Siren, Terrato, Bahamut; Crusader, Ramuh, Ifrit; Odin, Maduin, Phantom. Co-sim A vs B: no lasting divergence over 14799 checkpoints. 0 ROM misses, no tripwires, `regress.sh --full --update` 704 PASS, all old expectations byte-identical. No snes9x reference. A wait of 30 frames precedes each battle (battle start phase, see docs/STATUS.md).

## 2026-11-11: New route r17_battle_spells2, expectation `r17_battle_spells2.toml` added, existing expectations unchanged
- `validation/routes/r17_battle_spells2.txt`: Terra casts the magic list entries 28 to 53 that r16 does not (Berserk lands on her and ends a battle through her own attack, Warp leaves the battle), in three battles. Co-sim A vs B: no lasting divergence over 56722 checkpoints. It reaches 60 further dispatch targets (466 to 526 of 1079, `docs/battle_dispatch_coverage.md`). No snes9x reference (animation lengths differ through the reference's lag frames), so the comparison is SKIP.
- The route showed one ROM miss, `BattleEnd_01` (`C24897`, `goto_gap` from `C247F8`, the `CheckBattleEnd` table, reached by Warp); it is now a hand-maintained entry with `emit = true` in `symbols_overrides.toml`. `src/gen` is `ff9d9afb422b0846`; `regress.sh --full --update` rewrote the other expectations without a diff, 701 PASS, 0 FAIL, 0 ROM misses (log `work/logs/r17_full_update2.txt`).
- A wait of 30 frames precedes each battle start. Without it the co-sim diverges for good at the start of the second battle (see docs/STATUS.md, "r17 battle start phase").
- No other expectation changed.

## 2026-11-11: New route r16_battle_spells, expectation `r16_battle_spells.toml` added, existing expectations unchanged
- `validation/routes/r16_battle_spells.txt`: Terra casts the first 28 spells of the magic list in two battles against the Narshe guards. Co-sim A vs B: no lasting divergence over 52540 checkpoints. It reaches 37 dispatch targets that r05 to r15 never run (spell animation and effect handlers, see `docs/battle_dispatch_coverage.md`). No snes9x reference: the animations differ in length between the reference (lag frames) and the recomp, so the comparison is SKIP and the route is checked against the expectation and the co-sim only.
- The route showed one ROM miss, `MoveAnimDownRight` (`C1F3EF`, `goto_gap` from `C1F39F`); it is now a hand-maintained entry with `emit = true` in `symbols_overrides.toml` (function boundary for a JMP landing, as in r13). `src/gen` is `b0a1bf3ca911a070`; `regress.sh --full --update` rewrote the other expectations without a diff. `regress.sh --full`: 698 PASS, 0 FAIL, 0 ROM misses (log `work/logs/r16_full_update2.txt`).
- No other expectation changed.

## 2026-11-11: New route r15_battle_ai, expectation `r15_battle_ai.toml` added, existing expectations unchanged
- `validation/routes/r15_battle_ai.txt`: two battles (Narshe guards, Magitek armor) in which the monsters act from their AI scripts. Co-sim A vs B: no lasting divergence over 15938 checkpoints. It reaches 4 dispatch targets that r05 to r14 never run (`AICondTbl`, `DoNextAICmd` and two more, see `docs/battle_dispatch_coverage.md`). No snes9x reference (the monsters' random choices depend on the frame timing, which the reference's lag frames change), so the comparison is SKIP and the route is checked against the expectation and the co-sim only.
- No other expectation changed.

## 2026-11-11: New route r14_battle_types, expectation `r14_battle_types.toml` added, existing expectations unchanged
- `validation/routes/r14_battle_types.txt`: three battles with the battle type forced to back, pincer and side attack, plus Osmose (MP damage path of `ApplyDmg`). It reaches the dispatch targets `C21350` (`ApplyDmgTbl`), `C1149A`, `C114D7` and `C11533` (`CalcMonsterPosTbl`) that r05, r06 and r13 never take. Co-sim A vs B: no lasting divergence over 15037 checkpoints.
- The route showed one ROM miss, `GoToNextMenuState` (`C15A4A`, M1X0, `call_gap` from `C15D92`); it is now a hand-maintained entry with `emit = true` in `symbols_overrides.toml`. `src/gen` is `a81e03fe981b3e31`; all other expectations stayed byte-identical (`regress.sh --full --update` rewrote them without a diff).
- Reference `work/ref/r14` (snes9x, `work/ref_route.sh`) added: scene-keyed like r06 and r13. 49 existing WRAM, VRAM and OAM masks got the r14 tags where they fully cover the differing ranges (same classes: counters, RNG phase, ATB display, animation phase), the PPU write mask of the `*_after` dumps got the three tags, and new masks were added for ten framebuffer clusters (party sprite and ATB gauge phase) and two VRAM ranges (monster name window close phase in `side_victory`). `r14_battle_types.toml` hashes were rewritten for the changed masks; every other expectation stayed byte-identical. `regress.sh --full` 1022 PASS, 0 FAIL (log `work/logs/r14_ref_update.txt`).
- `regress.sh --full`: 658 PASS, 0 FAIL, 0 ROM misses in all 11 routes (log `work/logs/r14_full_update2.txt`).

## 2026-11-10: Pin change snesrecomp `6a4a988fad7d` (interrupt flags, dispatch misses, trace image), no expectation changed
- Pin `ddf6aebd6dab` → `6a4a988fad7d` (patch 0015), docs/STATUS.md "Pin session 11-10 (interrupt flags, dispatch misses, trace image)": the frame drivers set I and clear D after pushing the interrupt frame; a dispatch value missing from a generated switch is recorded and printed in every build (`[dispatch-oob]`); the trace build's frame history is configurable.
- All events, dump hashes and `interpreted` counts of the 10 expectations unchanged; `validation/expected` untouched. The interrupt handlers run in the interpreter either way and restore P with their RTI, so the new flags can only show in stack residue below S (the `php` of `CutsceneNMI` now pushes `$A5` instead of `$A1`, as the reference does). The dead stack below S is masked at the title, cutscene, field, menu and shop dumps; no other dump changed. No route prints a `[dispatch-oob]` or `[unresolved-abandon]` line. 0 ROM misses, tolerated misses and WRAM allowlists unchanged; all reference comparisons against snes9x green.
- Suite tooling: the tripwire search of `regress.sh` also counts `[dispatch-oob]` and `[unresolved-abandon]`, and `miss_report.py --log` lists them as skipped dispatches (exit 1).
- `src/gen` unchanged `9a2bfc279d2390cd` (the fix is in `runner/src` only).
- `regress.sh --full` with regen and build: 986 PASS, 0 FAIL, no INFO (log `work/logs/pin_diag_full_r1.txt`).

## 2026-11-09: Wound handler of `SetStatusTbl` dispatched, six battle masks removed, hashes and `interpreted` updated
- Cause, found with the co-sim over r05 (docs/STATUS.md "Co-sim: the skipped wound handler (11-09)"): the dispatch `jsr (SetStatusTbl,x)` in `UpdateStatus` (`C243AC`) had no case for entry 7, the wound handler `C24600`, so generated code skipped it whenever a monster died (the default arm only calls `cpu_trace_dispatch_oob`, a no-op without `SNESRECOMP_TRACE`). The exporter had left `C24600` unclassified because the handler starts with the macro `ldaflg`.
- Fix: `tools/ff6/export_ca65_authority.py` classifies instruction macros (wrappers with the operation as first parameter, their `.define` aliases, macros whose body is all code or all data). Export: unknown spans 371 → 1, 109516 → 109812 instruction starts, dropped dispatch targets 2 → 1 (only `MenuStateTbl[120]` stays, rightly). `recomp/disassembly-layout.json` rewritten; the only dispatch change is `C243AC` + `C24600`. `src/gen` `4d472f0215cc978e` → `9a2bfc279d2390cd` (32559 → 32632 roots, 37273 → 37326 variants, 17061 → 17082 AOT, 20212 → 20244 LLE).
- `masks.toml`: removed the masks on `$3A57` and `$3EF1-$3EF3` at `b_victory`/`b_msg1`-`b_msg3` (r05), `victory`/`msg1`-`msg3` (r06) and `c_victory`/`c_msg1`-`c_msg3` (r13). They held the deathrattle mask and the near-fatal bits of the dying guards; their reasons (turn status, lag of the periodic status check) were wrong, the bytes differed because the wound handler did not run. Without them all 12 dumps equal snes9x in WRAM.
- Dump hashes: the WRAM hashes of those 12 dumps (fewer masked bytes, and the handler now runs). Events and all other hashes unchanged. 0 ROM misses, tolerated misses and WRAM allowlists unchanged.
- `interpreted` updated, reported only: r05 141 613 565 → 141 613 024, r06 160 610 266 → 160 609 856, r13 165 655 690 → 165 656 510.
- `regress.sh --full` with regen and build before the update: 980 route checks PASS, 3 INFO (`interpreted`), no FAIL (the masked bytes hid the change). After removing the masks and `--update` (no regen, no build), without `--update`: 984 PASS, 0 FAIL. Logs `work/logs/macros_regress_full.txt`, `macros_full_update.txt`, `macros_full_check.txt`.

## 2026-11-09: Pin change snesrecomp `ddf6aebd6dab` (bus-accurate AOT pricing), events, hashes and `interpreted` updated
- Pin `7cd67ca3f5be` → `ddf6aebd6dab` (patch 0014: generated code prices every bus transfer at the speed of its address like the interpreter, the frame driver charges the interrupt entry, a `$420B` store checks the frame deadline), docs/STATUS.md "Pin session 11-08 (bus-accurate AOT pricing)". Generated code does less work per frame than before (a WRAM access in FastROM code costs 8 master clocks instead of 6), so loads end later and lag frames move.
- Events: from the intro on, every route reaches its scene keys 1 frame later (first at frame 3713, the end of a wait in the map $17 intro; caused by the data prices and the interrupt entry together, the `$420B` check alone changes nothing there). r01 unchanged (title at frame 3442). Battle and map loads take up to 7 frames more (r05 battle start +7). Route lengths: r02 18179 → 18182 frames, r04 20636 → 20657, r13 17070 → 17102.
- Dump hashes: r01, r03, r04, r05, r10, r11 and r12 unchanged. Changed: r02 `control`, `dlg8` (counter phases: event counter `$47`, animation queue pointer `$48`, palette animation counter `$10E7`, one palette color), r06 15 dumps from `m03` on and r13 12 dumps from `c06` on (the battle takes the same course, active character, menu state and zbe are equal at every menu; the reference's lag falls at other dumps: damage spread, animation phase of the previous action, zbe after the victory).
- Reference comparisons against snes9x: green for r01, r03, r04, r05, r10, r11, r12; at first red for r02 (`dlg8`, `control`), r06 (15 dumps) and r13 (12 dumps). Owner's decision 2026-11-09: the pin goes into the branch `fix/aot-bus-pricing` with a PR, the three routes are realigned there. Done with `validation/masks.toml` only (no route change; the masked dump hashes of these 29 dumps change with it and were written again with `--update`): the r03 counter-phase masks also for r02 `dlg8`/`control`; the r06/r13 battle masks extended class by class to the dumps where the lag now falls (r06 38 extended, 33 new, 2 image rectangles; r13 19 extended, 11 new), docs/STATUS.md "Pin session 11-08 (bus-accurate AOT pricing)". Then `regress.sh --full` green: 984 PASS, 0 FAIL (450 s, log `work/logs/pin_bus_full_check_masks.txt`).
- `interpreted` updated in all 10 routes, reported only: r01 19 201 566 → 19 190 024, r02 172 094 876 → 170 236 319, r03 130 190 603 → 128 169 079, r04 203 816 428 → 200 550 428, r05 144 418 687 → 141 613 565, r06 164 621 932 → 160 610 266, r10 167 823 442 → 164 976 811, r11 132 701 281 → 130 727 569, r12 142 506 305 → 139 924 393, r13 170 134 254 → 165 655 690.
- `src/gen` `5bba91971854d0de` → `4d472f0215cc978e` (analysis unchanged: 32559 roots, 37273 variants, 17061 AOT, 20212 LLE). 0 ROM misses, tolerated misses and WRAM allowlists unchanged.
- `regress.sh --full` before the update: 29 hash FAIL and 29 reference FAIL in r02, r06, r13, events FAIL in r02 to r13 (1 frame), 10 INFO (`interpreted`). After `--update`, without `--update`: 954 PASS, 29 FAIL (the reference comparisons above). Logs `work/logs/pin_bus_full_pre1.txt`, `pin_bus_full_update.txt`, `pin_bus_full_check.txt`.

## 2026-11-06: Pin change snesrecomp `7cd67ca3f5be` (APU timeline from reset), `interpreted` updated
- Pin `7b570a032de3` → `7cd67ca3f5be` (patch 0013: the SPC runs from reset instead of from the CPU's first port write, and the first frame after reset counts from reset to V=225 instead of a whole field), docs/STATUS.md "Pin session 11-06 (APU timeline from reset)". At every frame cut the SPC is now 3475 SPC cycles further than before, on the hardware timeline.
- All dump hashes and all events of the 10 expectations unchanged (r01: title at frame 3442 as before). All reference comparisons against snes9x (`work/ref/rNN`, PPU write streams included) green. 0 ROM misses, tolerated misses and WRAM allowlists unchanged.
- `interpreted` updated in all 10 routes, reported only: r01 19 173 704 → 19 201 566, r02 172 065 392 → 172 094 876, r03 130 160 058 → 130 190 603, r04 203 749 558 → 203 816 428, r05 144 401 172 → 144 418 687, r06 164 590 811 → 164 621 932, r10 167 794 565 → 167 823 442, r11 132 671 125 → 132 701 281, r12 142 475 479 → 142 506 305, r13 170 110 922 → 170 134 254. Where it goes in r01 (`work/pin_session/cost_diff.py` against the capture from 11-05, which is 62 instructions away from the old state): more in `ClearObjMap` (C05678-C0567C, +17 544), `Decompress_C0046C` (C00492-C004F2) and `LoadMapTiles` (C02924-C02928), fewer in the SPC wait of `InitSound` (C5004F-C50055, -1 839). The SPC handshakes end at other points inside the frame, so the boot work lies at other positions relative to the frame deadline at V=225, and other loop iterations finish interpreted after the handback (mechanism as in the entry of 2026-11-05, not proven per instruction).
- `src/gen` unchanged `5bba91971854d0de` (the fix is only in `runner/src`).
- `regress.sh --full` before the update: 974 route checks PASS, 10 INFO (`interpreted`), no FAIL. After `--update`, without `--update`: 984 PASS, 0 FAIL. Logs `work/logs/pin_apu_full_pre1.txt`, `pin_apu_full_update.txt`, `pin_apu_full_check.txt`.

## 2026-11-06: r13_battle_commands2 set for the first time (scene-keyed), `interpreted` of r05 and r06 updated
- `r13_battle_commands2.toml` new: 22 dumps, 130 events, 17070 frames, run 39 s. Only in `--full`. Second part of the battle commands (Lore, X-Magic, Morph, Revert, Runic, Capture, Jump, Control, Mimic, GP Rain, Rage, Row, Def), docs/STATUS.md "Route r13 battle commands, part two". 0 ROM misses, 4 tolerated, WRAM allowlist 261, interpreted 170 110 922.
- Reference comparison against `work/ref/r13` (snes9x): all 22 dumps WRAM, VRAM, CGRAM, OAM, FB equal, PPU write stream 22/22 equal. Against snes9x only scene-keyed (PLAN phase 8, decision 2026-11-05).
- `masks.toml`: 41 r05 battle masks extended class by class with the r13 tags (`c01`-`c17`, `c_victory`, `c_msg1`-`c_msg3`, `c_after`), new r13 section with 178 ranges, 11 image rectangles and 3 HDMA tolerances. The r13 tags have names of their own so that the r06 masks (tags `m01` etc.) do not apply to r13 and vice versa; nothing changes for r01-r12.
- Miss round: 3 goto landings from InitCmdSelectTbl by hand (`InitLoreSelect`, `InitRageSelect`, `InitXMagicInput`), 6 call targets generated (2809 → 2815). `src/gen` `fd76e7288a82faca` → `5bba91971854d0de` (32559 roots, 37273 variants, 17061 AOT, 20212 LLE).
- `interpreted` updated, reported only: r05 144 401 549 → 144 401 172, r06 164 605 612 → 164 590 811 (the new AOT functions run compiled there). Events and all hashes of the 9 old expectations unchanged, the other 7 files byte-identical.
- `regress.sh --full --update` green (515 s), then without `--update` 984 PASS, 0 FAIL (10 routes, 447 s without regen and build). Logs `work/logs/r13_full_update.txt`, `r13_full_check.txt`.

## 2026-11-05: Pin change snesrecomp `7b570a032de3` (OPT and plp), r06 `slot` and `interpreted` updated
- Pin `a76eb19a0d9d` → `7b570a032de3` (patches 0011 mode 2 offset-per-tile, 0012 local dispatch under `php`), docs/STATUS.md "Pin session 11-05 (OPT and plp)".
- `r06_battle_commands.toml`: new image hash for `slot`. The slot mask (rectangle 74-181/163-210) is removed from `masks.toml`; with 0011 the image equals the reference `work/ref/r06` (0 pixels differ, all 20 dumps and PPU write streams equal). All other dump hashes of all routes byte-identical, events unchanged.
- r05 and r06: tolerated misses 11 → 6 and 9 → 4 (block on `ValidateSpellList` lifted; `ValidateSpellList`, `InitChars`, `InitBattle` AOT, landings C25704/C2570E gone; `miss_allowlist.toml` updated to match), discoveries 272 → 267 and 270 → 265. 0 ROM misses in all routes.
- `interpreted` updated in all 9 routes: r01 19 173 642 → 19 173 704, r02 172 007 297 → 172 065 392, r03 130 101 727 → 130 160 058, r04 203 690 522 → 203 749 558, r05 144 346 121 → 144 401 549, r06 164 578 053 → 164 605 612, r10 167 737 344 → 167 794 565, r11 132 614 949 → 132 671 125, r12 142 419 448 → 142 475 479. The extra work is in the sound driver: the entry of `ExecSound` (C50131-C50170) and the wait loop of `InterruptSPC` (C505BF-C505C5) more often finish interpreted after returns to the interpreter, since `PlaySong` became a local target in `ExecSound_ext` (cause not conclusively proven). In exchange, parts of `InitBattle` (C22402-C2240A) drop out.
- `src/gen` `a34a08df34089aac` → `fd76e7288a82faca` (32487 roots, 37201 variants, 17025 AOT, 20176 LLE; overrides 2809 generated plus 40 by hand, new: `ValidateSpellList`, `TfrGameSfxPtrs`, function boundary `PlaySong`).

## 2026-11-05: r06_battle_commands set for the first time (scene-keyed)
- `r06_battle_commands.toml` new: 20 dumps, 128 events, 16554 frames, run 40 s. Only in `--full`. 0 ROM misses, 9 tolerated, WRAM allowlist 261, interpreted 164 578 053.
- The route was in `validation/routes_pending/`. Changed so that the scene stays the same on both sides (docs/STATUS.md, "r06 scene-keyed against the reference"): dance Love Sonata instead of Wind Song (no background or stumble roll at execution time), Vicks' ATB set to 0 afterwards, wait for the running main loop before m13, remove Sap from guard 0 at the end, three messages instead of four.
- Reference comparison against `work/ref/r06` (new, snes9x run `r06L4`): all 20 dumps WRAM, VRAM, CGRAM, OAM, FB equal, PPU write stream 20/20 equal. Against snes9x only scene-keyed (PLAN phase 8, decision 2026-11-05).
- `masks.toml`: 41 r05 battle masks extended class by class with the r06 tags, new r06 section with 98 ranges, 5 image rectangles and 3 HDMA tolerances. Among them the rectangle over the slot reels, because of a framework bug in mode 2 offset-per-tile (the mask goes away with the fix in the next pin session; the fb hash of `slot` changes then). Nothing changes for the other routes.
- The 8 other expectations byte-identical, including `interpreted`. `regress.sh --full --update` and the run without `--update` green, `src/gen` unchanged `a34a08df34089aac`.

## 2026-11-05: r05_first_battle set for the first time, r05 in the quick suite
- `r05_first_battle.toml` new: 9 dumps, 52 events, 14006 frames, run 34 s. The route was in `validation/routes_pending/` until its 14 ROM misses were resolved. Now 0 ROM misses, 11 tolerated (4 field ones as in r03, 7 caused by the `ValidateSpellList` block), WRAM allowlist 261, interpreted 144 346 121.
- Resolution: exit widths from the source for the 7 callers of `CheckStatus` (pea parameters), `ExecAttack` (pea/rts loop), `ExecSelfAttack` and `AIRand3` (pla/pla) in `recomp/bankc2.cfg`; `ExecSelfAttack` as a function boundary, the goto landings `InitMagitekSelect`, `MoveAnimDownLeft`, `MoveAnimLeft` as function boundaries (`symbols_overrides.toml`, 18 entries by hand, 2791 generated). `CheckBattleEnd` newly in `miss_allowlist.toml` (chain via CheckFinalBattle and RestartBattle to the blocked `ValidateSpellList`).
- Reference comparison against `work/ref/r05`: all 9 dumps WRAM, VRAM, CGRAM, OAM, FB equal (masks from the r05 section), PPU write stream 9/9 equal.
- The 7 other expectations byte-identical, including `interpreted`. `src/gen` now `51b90d5a148671da` (32111 roots, 16775 AOT, 20050 LLE).
- `QUICK` = r01 + r03 + r04 + r05.

## 2026-11-03: Battle promotions and r05 (pending), no expectation changed
- 2789 generated promotions (previously 1649), AOT 8670 → 16649, `src/gen` `87c89a729aa3c41d`. `ValidateSpellList` blocked by hand (framework bug, docs/STATUS.md). All 7 expectations (r01-r04, r10-r12) byte-identical, `regress.sh --full` without `--update` 816 PASS, `--quick` green (183 s).
- `masks.toml`: new r05 section (52 entries, r05 tags only), `rect` for image masks; `b_dlg_north`, `b_after`, `b_dlg_next` added to 16 r03 field masks. Nothing changes for the other tags.
- `compare_ppuw.py` merges identical HDMAEN writes that directly follow each other; this changes no result for r01-r12.
- `miss_allowlist.toml`: 6 entries as a consequence of the block. r05 gets no expectation yet: the route stays in `validation/routes_pending/` until its 14 ROM misses are resolved.

## 2026-11-02: r12_menu_scroll set for the first time
- `r12_menu_scroll.toml` new: 112 dumps, 13670 frames, run 39 s. The route scrolls the item, magic, weapon and shop sell lists with a dump in every frame of the scroll animation and holds the direction keys (repeat rate). Only in `--full`. 0 ROM misses, 2 tolerated, WRAM allowlist 261.
- Reference comparison against `work/ref/r12`: all 112 dumps WRAM, VRAM, CGRAM, OAM, FB equal, PPU write stream 112/112 equal (HDMA per line, including the BG1 scroll table `$7E:9849` in every animation frame).
- `masks.toml`: new r12 section with 6 ranges. Without masks only `$0630-2`, `$F230-2`, `$10D1`, `$10E7` and the dead stack below MenuLoop differed. `$CF`, `$0228`, play time, frame and wait counters are equal: the route runs without any lag difference on both sides.
- The 6 other expectations byte-identical. `regress.sh --full` without `--update` 816 PASS, `--quick` green (164 s), `src/gen` unchanged `17164c920592a4a6`.

## 2026-11-02: r04_menu_tour set for the first time, r04 in the quick suite
- `r04_menu_tour.toml` new: 101 dumps, 20636 frames, run 48 s. The route was in `validation/routes_pending/` until its 184 ROM misses were resolved (menu dispatch list: resolver fix `MaxHPMPTbl`, task dispatch `C31203`, site `C33D40`, 1649 promotions). Now 0 ROM misses, 2 tolerated, WRAM allowlist 261.
- Reference comparison against `work/ref/r04`: all 101 dumps WRAM, VRAM, CGRAM, OAM, FB equal (masks from the r04 section in `masks.toml`), PPU write stream 101/101 equal, SRAM equal after both saves and after loading.
- The 5 other expectations byte-identical, including `interpreted`. `src/gen` now `17164c920592a4a6` (8670 AOT instead of 7424).
- `QUICK` = r01 + r03 + r04, 162 s with regen and build.

## 2026-11-02: Pin change snesrecomp `9745cb9c45c3`, no expectation changed
- All 5 expectations (r01, r02, r03, r10, r11) byte-identical, `regress.sh --full` without `--update` green (169 PASS). `src/gen` unchanged `7fc218bf3df4c2ff`, the fixes are only in `runner/src`.
- r04_menu_tour gets no expectation yet: the route stays in `validation/routes_pending/` until its 184 ROM misses are resolved.

## 2026-10-31: r11_doors set for the first time
- `r11_doors.toml` new: 6 dumps, 12709 frames, run about 30 s. Door transitions through the real triggers, long and short, there and back. Only in `--full`.
- The 4 other expectations byte-identical, `src/gen` unchanged `a7426f6f5321c606`.
- Reference comparison against `work/ref/r11`: all 6 dumps WRAM, VRAM, CGRAM, OAM, FB 0 unmasked each. 0 ROM misses, 4 tolerated, WRAM allowlist 261.
- `masks.toml`: the 6 tags are in the same lists as the r10 tags (`$1245-6`, `$021B-E`, `$0630-2`, `$F230-2`, dead stack, BG3 stripe in `[[ppuw]]`). Only these ranges differed. Nothing changes for the other tags.

## 2026-10-31: Idle poll `C00566` declared, only `interpreted` changed
- `src/game_rtl.c`: the field `WaitVblank` (`lda $55 / beq`, reset.asm:780) is listed in `kIdlePolls`. `src/gen` unchanged `a7426f6f5321c606`.
- In all 4 expectations exactly the `interpreted` line changes: r01 19191836 → 19173642, r02 175195936 → 172007297, r03 133341722 → 130101727, r10 172558530 → 167737344. Events, all hashes and the `cpu_cycles` per run are equal.

## 2026-10-31: Pin change snesrecomp `3e17328d149d`, r10_field_modes set for the first time
- `r01_boot_title.toml`, `r02_new_game_to_narshe.toml`, `r03_field_walk.toml` byte-identical: the pin change changes no expectation. `src/gen` unchanged `a7426f6f5321c606`, the fixes are only in `runner/src`.
- `r10_field_modes.toml` new: 24 dumps, 15678 frames, run 30 s. The route was in `validation/routes_pending/` until the pin, because `m13d` and `m15f` are red without the fix for the DMA channel registers.
- Reference comparison r10 against `work/ref/r10`: all 24 dumps WRAM, VRAM, CGRAM, OAM, FB 0 unmasked each. Green remainder in `m088`, `m185`, `m18a` tolerated via `[[fb_green]]` (artifact of the reference). 0 ROM misses, 2 tolerated, WRAM allowlist 261.
- r10 runs only in `--full`, the quick suite stays r01 + r03.

## 2026-10-30: Reference with patched snes9x, CGRAM mask, three new dispatch targets
- `r01_boot_title.toml` byte-identical.
- `r02_new_game_to_narshe`: only `interpreted` 175196581 → 175195936, because `ObjCmd_c7/d5/fa` are now AOT. Events and all hashes equal.
- `r03_field_walk`: `interpreted` 133342760 → 133341722 and the `cgram` hashes of all 6 tags: the new mask `$00BA-$00BB` (entry `$5D` of the palette animation, phase like `$10E7`) sets these bytes to 0 before hashing. Otherwise unchanged, events and the other 5 hashes equal.
- `src/gen` now `a7426f6f5321c606` (8592 roots, 4194 AOT, 5992 LLE).
- The references `work/ref/r01..r03` now come from the patched core (`toolchain/cores/snes9x_debug_libretro.dll`). Cross-check: all WRAM, VRAM, SRAM and FB dumps bit-identical to the stock reference. Newly compared: CGRAM, OAM (`compare_dumps.py`, bit 15 excluded), PPU write stream (`compare_ppuw.py`).

## 2026-10-30: r02_new_game_to_narshe and r03_field_walk set for the first time, r03 in the quick suite
- State: pin `6f928388582a`, `src/gen` `f9343072b78737f0`, run with `validation/regress.ini`.
- r02: 10 dumps, `control` at frame 18179 (reference 18191, loading phases are faster in the recomp; hence scene-keyed), `quit` at 18179. ROM misses 0, tolerated 2, WRAM allowlist 263.
- r03: 6 dumps, `quit` at 12472. ROM misses 0, tolerated 4, WRAM allowlist 261.
- Reference comparison of all 16 dumps against `work/ref/r02`, `r03`: WRAM 0 unmasked, VRAM 0, FB 0 (5 bit). Masks in `validation/masks.toml`.
- Cross-check: a second run without `--update` passes (events, all hashes, miss counts). `r01_boot_title.toml` stayed byte-identical during `--update`.
- Quick suite now r01 + r03: 71 s (regen 36 s, build 3 s, r01 6 s, r03 23 s).

## 2026-10-30: Pin change snesrecomp `6f928388582a` (RDNMI poll, mosaic table, HDMA from V=0), expectations unchanged
- No change to `validation/expected/r01_boot_title.toml`. r01 passes without `--update` (events, all 6 hashes, miss counts, reference).
- `src/gen` unchanged `f9343072b78737f0`: the fixes are only in `runner/src`, the generator digest stays the same.

## 2026-10-30: Miss rounds r02/r03, expectations unchanged
- `validation/expected/r01_boot_title.toml` unchanged, passes without `--update` with pin `1933c214865e`. `src/gen` now `f9343072b78737f0` (8568 roots, 4188 AOT, 5974 LLE).
- `regress.sh` runs each route in its own run directory: every route starts with an empty SRAM (`saves/save.srm` is relative to the cwd). Before this, an r02 run changed the SRAM hash of r01.
- `regress.ini`: `NoSpriteLimits = 0`, no effect on r01.
- Masks for the r02/r03 tags in `validation/masks.toml`; tag `title` untouched.
- No expectations for r02/r03 yet: both only run with the framework fixes (`patches/snesrecomp/pending/`, docs/STATUS.md).

## 2026-10-30: Closure at 609 overrides adopted, only miss counts changed
- `symbols_overrides.toml`: 422 → 609 generated entries (7816 roots, 3800 AOT variants), `src/gen` `f0cb03876c8bcd6e`.
- `r01_boot_title`: events and all 6 hashes unchanged, reference `title` still WRAM 0, VRAM 0, FB 0 (5 bit).
- Miss counts: tolerated 4 → 1 (only LoadMap; ExecEvent, EventCmd_b2/a9 resolved, allowlist shortened accordingly),
  discoveries 155 → 152, interpreted 19 191 984 → 19 191 836. ROM misses 0, WRAM allowlist 151.

## 2026-10-30: Pin change snesrecomp `1933c214865e` (JMP (abs) from bank 0), expectations unchanged
- No change to `validation/expected`. r01_boot_title passes without `--update` (events, all 6 hashes, miss counts, reference).
- `src/gen` now `ffae6649e29d9db5` instead of `101a4528892ffe06`. The generated code is bit-identical; only
  `build_digest` (`module_v2.c`) and `.snesrecomp-cache.json` changed, because both contain a digest over the generator
  sources. A/B evidence: `work/logs/pin_jmpfix_gen_ab.txt`.

## 2026-10-29: r01_boot_title set for the first time
- State: `phase/05-title` after 30c61f9, snesrecomp `4dcec90f44eb` (DSP power-on values), `src/gen` `101a4528892ffe06`
  (5000 roots, 2910 AOT variants, 3418 LLE). Run with `validation/regress.ini`.
- Events: `$19 == 9` at frame 3442 (snes9x reference 3442), `dump title` and `quit` at 3472.
- Hashes `title`: wram (stack `$1508-$15EC` masked, `validation/masks.toml`), vram, cgram, oam, sram, fb.bgrx.
- Cross-checks (`work/regress_crosscheck.sh`, log `work/logs/regress_crosscheck.out`):
  - The throttled run `r01_dsppin_final` (DisableFrameDelay = 0, 58 s) passes with the same hashes,
    events and miss counts as the unthrottled suite run (5 s). So the real-time throttle does not change
    the result.
  - A run with an active gamepad (`r01_dsppin`) fails: wram.
  - A run before the DSP patch (`r01_idle`, title at 3654) fails: events.
- Reference comparison `title` against `work/ref/r01`: WRAM 0, VRAM 0, FB 0 (5 bit).
