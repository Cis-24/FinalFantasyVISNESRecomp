# Battle dispatch coverage (11-11)

Measured with the reference interpreter of the co-sim (B) replaying the input and poke logs of r05, r06, r13 and r14,
with a temporary counter at the dispatch site and target PCs (work copy of the driver, not versioned). Sites and
targets come from the authority export (`dispatches` with a site in banks C1 and C2: 72 sites, 1187 site and target
pairs, 1079 distinct target addresses). A target counts as reached when its first instruction ran at least once in any of the four routes.
Result over r05, r06, r13 and r14: 489 of 1187 pairs reached (425 of 1079 distinct addresses), 698 pairs not. 15 sites never ran at all.

Update after r15 (monsters act, guards and a Magitek armor): 429 of 1079 distinct addresses, i.e. +4 (`AICondTbl`, `DoNextAICmd`, one more in `C2367D` and one in `ExecGfxCmd`). Most monsters need a route of their own because their scripts, animations and damage differ, so the remaining gap shrinks slowly per route; the party was kept alive by choosing weak formations (a strong one wiped the party in four rounds).

Update after r16 (Terra casts 28 spells in two battles): 466 of 1079 distinct addresses, i.e. +37 (`ExecAnimType` 15, `magic_code00` 10, `set_magic_code` 6, `UpdateStatus` 2, `DoTargetEffect` 2, `magic_code03_a` 2, `UpdateCircleShape` 2). Spells 28 to 53 are not cast: after spell 42 Terra's ATB gauge stayed nearly empty (no menu in 6000 frames, cause not examined) and a third battle did not finish.

Update after r17 (spells 28 to 53): 526 of 1079 distinct addresses, i.e. +60. Spell 42 is Berserk: it lands on Terra, who then has no menu (she attacks on her own), which was the stall seen after spell 42 in r16; Warp (51) leaves the battle; Death is probabilistic, so a spell that kills in one timeline can miss in another.

The unreached targets are resolved and generated like all others, but no run has exercised them. The large groups are
spell and attack animation scripts (`magic_code00`, `set_magic_code`, `ExecAnimType`, `ExecEventAnimCmd`), the target
and attacker effect handlers (`DoTargetEffect`, `DoAttackerEffect`), the monster AI (`AIRand3`, `CheckAITarget`,
`GetBattleVar`, `DoNextAICmd`, `RandCharAction`; the guards never act in the routes) and level up (`DoLevelUp`).

| Function | Site | Site hits | Targets | Unreached |
|---|---|---|---|---|
| magic_code00 | 0xC1C884 | 1835 | 141 | 116 |
| ExecAnimType | 0xC2E8D4 | 47 | 125 | 109 |
| set_magic_code | 0xC1D9E3 | 13627 | 126 | 45 |
| DoAttackerEffect | 0xC23E85 | 47 | 44 | 42 |
| DoTargetEffect | 0xC23886 | 52 | 45 | 41 |
| AIRand3 | 0xC21A96 | 0 | 28 | 28 |
| CheckAITarget | 0xC21F85 | 0 | 21 | 21 |
| ExecCmd_C213D3 | 0xC213FE | 47 | 45 | 19 |
| BattleCmdNoEffect | 0xC2155D | 3 | 45 | 19 |
| GetBattleVar | 0xC21E64 | 0 | 14 | 14 |
| DoNextAICmd | 0xC21B02 | 2 | 15 | 13 |
| UpdateStatus | 0xC243AC | 33 | 18 | 13 |
| ExecEventAnimCmd | 0xC2C085 | 82 | 18 | 13 |
| UpdateTargetCursors | 0xC1B76F | 47 | 34 | 11 |
| ExecGfxCmd | 0xC1956B | 246 | 20 | 11 |
| UpdateStatus | 0xC243D7 | 12 | 12 | 10 |
| IncColor | 0xC1FDB0 | 36 | 13 | 10 |
| UpdateMenuInput | 0xC15529 | 13846 | 64 | 10 |
| DoLevelUp | 0xC260F1 | 0 | 9 | 9 |
| UpdateCircleShape | 0xC2D53E | 52 | 9 | 8 |
| DlgTextCmd | 0xC15E51 | 55 | 16 | 8 |
| RandCharAction | 0xC20493 | 0 | 9 | 7 |
| UpdateBattleBG | 0xC2B27E | 13851 | 8 | 7 |
| GetMPCost | 0xC24FB1 | 0 | 6 | 6 |
| CheckBattleEnd | 0xC247F8 | 0 | 6 | 6 |
| CalcItemEffect | 0xC22B13 | 2 | 7 | 6 |
| UpdateStatus | 0xC243BF | 1 | 8 | 6 |
| magic_code06_b | 0xC1F4EA | 288 | 8 | 6 |
| magic_code06_b | 0xC1F4FA | 488 | 8 | 6 |
| UpdateMenuWindow | 0xC14512 | 12157 | 28 | 6 |
| RandCharAction | 0xC2049F | 0 | 5 | 4 |
| UpdateEquip_C20E77 | 0xC20F2D | 108 | 6 | 4 |
| magic_code06_b | 0xC1F4BE | 142 | 8 | 4 |
| magic_code06_b | 0xC1F4CE | 575 | 8 | 4 |
| key_target_left | 0xC17747 | 0 | 4 | 4 |
| key_target_right | 0xC1775E | 0 | 4 | 4 |
| ListTextCmd | 0xC16411 | 294 | 16 | 4 |
| print_code_chg | 0xC16704 | 24596 | 18 | 4 |
| player_pat_chr_set | 0xC136F5 | 0 | 4 | 4 |
| ShowAttackName | 0xC2367D | 19 | 8 | 3 |
| FightAttack | 0xC21673 | 0 | 4 | 3 |
| InitWeaponType | 0xC1C270 | 14 | 5 | 3 |
| key_target_left | 0xC1773F | 0 | 3 | 3 |
| key_target_right | 0xC17756 | 0 | 3 | 3 |
| ExecBtlGfx_ext | 0xC10005 | 3313 | 14 | 3 |
| mon_mode_chg_main | 0xC2E6C1 | 18 | 6 | 3 |
| InitBattleType | 0xC22E77 | 6 | 3 | 2 |
| CalcMagicEffect | 0xC2473D | 0 | 2 | 2 |
| UpdateStatus | 0xC243EF | 2 | 4 | 2 |
| DlgTextCmd_12 | 0xC15EED | 11 | 4 | 2 |
| InitCmdList | 0xC253D6 | 9 | 5 | 1 |
| EquipStatusMod | 0xC244A4 | 52 | 3 | 1 |
| magic_code03_a | 0xC1F393 | 129 | 8 | 1 |
| magic_code03_a | 0xC1F39F | 1085 | 8 | 1 |
| DrawCharSlotInfo | 0xC167CC | 17340 | 4 | 1 |
| DrawCharSlot4Info | 0xC16814 | 17340 | 7 | 1 |
| UpdateSprites | 0xC127B5 | 13845 | 2 | 1 |
| ApplyDmg | 0xC21300 | 44 | 2 | 0 |
| CalcMaxHPMP_C2283C | 0xC2284D | 36 | 4 | 0 |
| InitTarget | 0xC22701 | 103 | 4 | 0 |
| UpdateCmdList | 0xC252D2 | 26 | 5 | 0 |
| ValidateSpellList | 0xC256F3 | 99 | 3 | 0 |
| DecCounters | 0xC25ADE | 420 | 3 | 0 |
| DecCounters | 0xC25AE5 | 2205 | 4 | 0 |
| InitCmdSelect | 0xC17CDE | 37 | 16 | 0 |
| CalcMonsterPos | 0xC11604 | 6 | 4 | 0 |
| UpdateCharText | 0xC144CB | 12104 | 6 | 0 |
| UpdateCharText | 0xC144E2 | 12913 | 4 | 0 |
| InitThrowSelect | 0xC1587F | 8 | 5 | 0 |
| InitToolsSelect | 0xC158BB | 16 | 5 | 0 |
| set_s_mess_poi | 0xC2BB15 | 3 | 2 | 0 |
| TfrCharText | 0xC2AC79 | 13845 | 4 | 0 |
