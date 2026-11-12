# Battle dispatch coverage (11-11)

Measured with the reference interpreter of the co-sim (B) replaying the input and poke logs of r05, r06, r13 and r14,
with a temporary counter at the dispatch site and target PCs (work copy of the driver, not versioned). Sites and
targets come from the authority export (`dispatches` with a site in banks C1 and C2: 72 sites, 1187 site and target
pairs, 1079 distinct target addresses). A target counts as reached when its first instruction ran at least once in any of the four routes.
Result over r05, r06, r13 and r14: 489 of 1187 pairs reached (425 of 1079 distinct addresses), 698 pairs not. 15 sites never ran at all.

Update after r15 (monsters act, guards and a Magitek armor): 429 of 1079 distinct addresses, i.e. +4 (`AICondTbl`, `DoNextAICmd`, one more in `C2367D` and one in `ExecGfxCmd`). Most monsters need a route of their own because their scripts, animations and damage differ, so the remaining gap shrinks slowly per route; the party was kept alive by choosing weak formations (a strong one wiped the party in four rounds).

Update after r16 (Terra casts 28 spells in two battles): 466 of 1079 distinct addresses, i.e. +37 (`ExecAnimType` 15, `magic_code00` 10, `set_magic_code` 6, `UpdateStatus` 2, `DoTargetEffect` 2, `magic_code03_a` 2, `UpdateCircleShape` 2). Spells 28 to 53 are not cast: after spell 42 Terra's ATB gauge stayed nearly empty (no menu in 6000 frames, cause not examined) and a third battle did not finish.

Update after r17 (spells 28 to 53): 526 of 1079 distinct addresses, i.e. +60. Spell 42 is Berserk: it lands on Terra, who then has no menu (she attacks on her own), which was the stall seen after spell 42 in r16; Warp (51) leaves the battle; Death is probabilistic, so a spell that kills in one timeline can miss in another.

Update after r18 (level ups): 535 of 1079 distinct addresses, i.e. +9 (all nine targets of `DoLevelUp`); 611 of 1187 site and target pairs reached, 11 of 72 sites never run. The table below is re-measured over r05, r06, r13, r14, r15, r16, r17 and r18 (site hits summed over the routes). The top remaining groups are `magic_code00` (94 unreached), `ExecAnimType` (84), the attacker and target effect handlers (40 and 37), `set_magic_code` (32) and the monster AI conditions (`AIRand3`, `CheckAITarget`, `GetBattleVar`, `DoNextAICmd`), which need monsters that act on their own.

Update after r19 (monster AI and enemy attacks, five battles chosen by scanning the AI scripts): 563 of 1079 distinct addresses, i.e. +28; 643 of 1187 pairs reached, 9 of 72 sites never run. `AIRand3` (AI conditions) is down from 27 to 17 unreached, `CheckAITarget` from 21 to 17. `GetBattleVar` (AI variable commands) is still never run, and the attacker and target effect handlers barely moved: the monsters of r19 attack almost only with Fight. Their remaining targets need bosses (conditions 2 to 9, 12, 17, 22 and 26 are used by monsters above id 255 only), whose battles open with long scripted dialog; a probe of Ultros (battle 387) stalled behind it. The table is re-measured over r05, r06 and r13 to r19.

The unreached targets are resolved and generated like all others, but no run has exercised them. The large groups are
spell and attack animation scripts (`magic_code00`, `set_magic_code`, `ExecAnimType`, `ExecEventAnimCmd`), the target
and attacker effect handlers (`DoTargetEffect`, `DoAttackerEffect`), the monster AI (`AIRand3`, `CheckAITarget`,
`GetBattleVar`, `DoNextAICmd`, `RandCharAction`; the guards never act in the routes) and level up (`DoLevelUp`).

| Function | Site | Site hits | Targets | Unreached |
|---|---|---|---|---|
| magic_code00 | 0xC1C884 | 11596 | 141 | 94 |
| ExecAnimType | 0xC2E8D4 | 178 | 125 | 83 |
| DoAttackerEffect | 0xC23E85 | 233 | 44 | 40 |
| DoTargetEffect | 0xC23886 | 252 | 45 | 37 |
| set_magic_code | 0xC1D9E3 | 82594 | 126 | 32 |
| AIRand3 | 0xC21A96 | 70 | 28 | 17 |
| CheckAITarget | 0xC21F85 | 3 | 21 | 17 |
| GetBattleVar | 0xC21E64 | 0 | 14 | 14 |
| ExecCmd_C213D3 | 0xC213FE | 252 | 45 | 13 |
| BattleCmdNoEffect | 0xC2155D | 3 | 45 | 13 |
| ExecEventAnimCmd | 0xC2C085 | 292 | 18 | 13 |
| UpdateTargetCursors | 0xC1B76F | 233 | 34 | 11 |
| IncColor | 0xC1FDB0 | 123 | 13 | 10 |
| UpdateMenuInput | 0xC15529 | 113679 | 64 | 10 |
| DoNextAICmd | 0xC21B02 | 129 | 15 | 8 |
| DlgTextCmd | 0xC15E51 | 198 | 16 | 8 |
| RandCharAction | 0xC20493 | 0 | 9 | 7 |
| UpdateBattleBG | 0xC2B27E | 113147 | 8 | 7 |
| ExecGfxCmd | 0xC1956B | 1086 | 20 | 7 |
| CalcItemEffect | 0xC22B13 | 2 | 7 | 6 |
| magic_code06_b | 0xC1F4EA | 1005 | 8 | 6 |
| magic_code06_b | 0xC1F4FA | 1906 | 8 | 6 |
| UpdateMenuWindow | 0xC14512 | 105650 | 28 | 6 |
| RandCharAction | 0xC2049F | 0 | 5 | 4 |
| GetMPCost | 0xC24FB1 | 3 | 6 | 4 |
| CheckBattleEnd | 0xC247F8 | 1 | 6 | 4 |
| UpdateEquip_C20E77 | 0xC20F2D | 288 | 6 | 4 |
| magic_code06_b | 0xC1F4BE | 536 | 8 | 4 |
| magic_code06_b | 0xC1F4CE | 2855 | 8 | 4 |
| key_target_left | 0xC17747 | 0 | 4 | 4 |
| key_target_right | 0xC1775E | 0 | 4 | 4 |
| UpdateCircleShape | 0xC2D53E | 653 | 9 | 4 |
| ListTextCmd | 0xC16411 | 4902 | 16 | 4 |
| print_code_chg | 0xC16704 | 204930 | 18 | 4 |
| FightAttack | 0xC21673 | 0 | 4 | 3 |
| UpdateStatus | 0xC243AC | 107 | 18 | 3 |
| UpdateStatus | 0xC243D7 | 40 | 12 | 3 |
| InitWeaponType | 0xC1C270 | 97 | 5 | 3 |
| key_target_left | 0xC1773F | 0 | 3 | 3 |
| key_target_right | 0xC17756 | 0 | 3 | 3 |
| ExecBtlGfx_ext | 0xC10005 | 67322 | 14 | 3 |
| ShowAttackName | 0xC2367D | 78 | 8 | 2 |
| CalcMagicEffect | 0xC2473D | 0 | 2 | 2 |
| mon_mode_chg_main | 0xC2E6C1 | 81 | 6 | 2 |
| InitBattleType | 0xC22E77 | 21 | 3 | 1 |
| InitCmdList | 0xC253D6 | 24 | 5 | 1 |
| UpdateStatus | 0xC243BF | 22 | 8 | 1 |
| DoLevelUp | 0xC260F1 | 75 | 9 | 1 |
| DlgTextCmd_12 | 0xC15EED | 35 | 4 | 1 |
| DrawCharSlotInfo | 0xC167CC | 147645 | 4 | 1 |
| DrawCharSlot4Info | 0xC16814 | 147645 | 7 | 1 |
| UpdateSprites | 0xC127B5 | 113126 | 2 | 1 |
| ApplyDmg | 0xC21300 | 215 | 2 | 0 |
| CalcMaxHPMP_C2283C | 0xC2284D | 126 | 4 | 0 |
| InitTarget | 0xC22701 | 512 | 4 | 0 |
| UpdateCmdList | 0xC252D2 | 86 | 5 | 0 |
| ValidateSpellList | 0xC256F3 | 1131 | 3 | 0 |
| UpdateStatus | 0xC243EF | 15 | 4 | 0 |
| EquipStatusMod | 0xC244A4 | 252 | 3 | 0 |
| DecCounters | 0xC25ADE | 3522 | 3 | 0 |
| DecCounters | 0xC25AE5 | 17934 | 4 | 0 |
| magic_code03_a | 0xC1F393 | 559 | 8 | 0 |
| magic_code03_a | 0xC1F39F | 7269 | 8 | 0 |
| InitCmdSelect | 0xC17CDE | 156 | 16 | 0 |
| CalcMonsterPos | 0xC11604 | 21 | 4 | 0 |
| UpdateCharText | 0xC144CB | 105441 | 6 | 0 |
| UpdateCharText | 0xC144E2 | 108575 | 4 | 0 |
| InitThrowSelect | 0xC1587F | 8 | 5 | 0 |
| InitToolsSelect | 0xC158BB | 16 | 5 | 0 |
| set_s_mess_poi | 0xC2BB15 | 3 | 2 | 0 |
| TfrCharText | 0xC2AC79 | 113126 | 4 | 0 |
| player_pat_chr_set | 0xC136F5 | 19 | 4 | 0 |
