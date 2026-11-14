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

Update after r20 (six boss battles with scripted dialog): 611 of 1079 distinct addresses, i.e. +48; 695 of 1187 pairs reached, 8 of 72 sites never run. `AIRand3` is fully reached except for a few conditions; `GetBattleVar` runs now (12 of 14 targets unreached), `CheckAITarget` has 14 unreached. The attack and target effect handlers and the animation scripts (`magic_code00`, `ExecAnimType`, `set_magic_code`) are still the large gap: the bosses use few of them, so the next gain is in spells and summons that monsters and the party cast. The table is re-measured over r05, r06 and r13 to r20.

Update after r21 (summons, all 27 espers cast by Terra in three battles): 690 of 1079 distinct addresses, i.e. +79; 774 of 1187 pairs reached, 8 of 72 sites never run. The animation scripts gained most: `magic_code00` is down from 92 to 62 unreached, `ExecAnimType` from 81 to 53, `set_magic_code` from 32 to 23; `DoAttackerEffect` gained the special effects of Golem and Sonic Dive (`C23F65`, `C241F6`), `DoTargetEffect` those of Palidor and Metamorph (`C23934`, `C23A3C`). The esper window adds the open, select and close states (`UpdateMenuWindow` `C14F9B`, `C14FA8`; `UpdateMenuInput` `C182B3`, `C1571F`), three list text commands (`ListTextCmd_16`, `_03`, `_1a`) and one circle shape (`UpdateCircleShape` `C2D627`, vertical oval). The rest of the effect handlers needs enemy attacks with special effects and items. The table is re-measured over r05, r06 and r13 to r21.

Update after r22 (special effects of weapons, tools, items and lores in three battles): 758 of 1079 distinct addresses, i.e. +68; 843 of 1187 pairs reached, 8 of 72 sites never run. `DoAttackerEffect` is down from 37 to 16 unreached and `DoTargetEffect` from 34 to 21: the weapon effects (Thief Knife, Valiant Knife, the MP critical entry of Rune Edge, which Ogre Nix also enters, Drainer, Soul Sabre, Ogre Nix, Atma Weapon, Tempest, Heal Rod, Dice, Scimitar, Assassin, Sniper), the lores (Step Mine, L? Pearl, Blow Fish, Revenge, Reflect???, ForceField, Dischord, Rippler, Stone, Pep Up, Exploder), the tools (Debilitator, Air Anchor) and the items (Elixir, Megalixir, Super Ball, Magicite, Smoke Bomb). The tools table of `CalcItemEffect` is fully reached (+6). Still unreached in the two effect tables: Man Eater, Sabin's Blitzes Suplex, Spiraler and Mantra, Leap, the target side of Reflect??? (a target with Reflect) and the monster special attacks (Launcher, Bababreath, Possess, Escape, Quadra Slam, Flare Star, Mind Blast, N. Cross, Empowerer, Discard, Engulf, R. Polarity, Wallchange, Evil Toot, Charm, Tapir, Seize, Overcast, Love Token, Phantasm, Stunner, Targetting, Fallen One, the half and quarter damage effects); the second MP critical effect is unused in the ROM. The table is re-measured over r05, r06 and r13 to r22.

Update after r23 (Sabin's Blitzes, Man Eater and the target cursor in one battle): 779 of 1079 distinct addresses, i.e. +21; 866 of 1187 pairs reached, 4 of 72 sites never run (8 before). The four sites of `key_target_left` and `key_target_right` run for the first time (one target per site, that of the normal battle type, on the character and the monster side; the back, pincer and side targets need those battle types). `DoAttackerEffect` gained Suplex, Mantra and Spiraler (13 unreached), `DoTargetEffect` Man Eater and the Suplex target check (19 unreached); the rest are animation script entries of the Blitzes (`magic_code00` 4, `set_magic_code` 4, `magic_code06_b` 2, `ExecAnimType` 2). The table is re-measured over r05, r06 and r13 to r23.

Update after r24 (monster special attacks in six boss battles: Atma Weapon, the Tentacles, Doom, Goddess, Dullahan, Number 024): 811 of 1079 distinct addresses, i.e. +32; 899 of 1187 pairs reached, 4 of 72 sites never run. `DoTargetEffect` gained R.Polarity, Wall Change, Mind Blast, Reflect???, Seize, Discard, Overcast, Love Token and Targetting (10 unreached), `DoAttackerEffect` Flare Star, Mind Blast, N.Cross and Discard (9 unreached); the rest are animation script entries of these attacks (`magic_code00` 11, `ExecAnimType` 3) and AI entries (`AIRand3`, `GetBattleVar`, `CheckAITarget`, `ExecCmd_C213D3`, `BattleCmdNoEffect`, `UpdateStatus` one each). Of the remaining effect entries three are used by no attack or weapon (`MORE_MP_CRIT`, `QUARTER_DMG`, `HALF_DMG`); Leap and Possess need Gau on the Veldt and a ghost in the party; Charm (Goddess' sequence did not draw it), Engulf, Baba Breath, Evil Toot, Phantasm, Fallen One, Launcher and Escape are monster attacks; Tapir is a Love Sonata dance step; Quadra Slam, Empowerer and Stunner are Cyan's Bushido levels 4 to 6. The table is re-measured over r05, r06 and r13 to r24.

The unreached targets are resolved and generated like all others, but no run has exercised them. The large groups are
spell and attack animation scripts (`magic_code00`, `set_magic_code`, `ExecAnimType`, `ExecEventAnimCmd`), the target
and attacker effect handlers (`DoTargetEffect`, `DoAttackerEffect`), the monster AI (`AIRand3`, `CheckAITarget`,
`GetBattleVar`, `DoNextAICmd`, `RandCharAction`; the guards never act in the routes) and level up (`DoLevelUp`).

| Function | Site | Site hits | Targets | Unreached |
|---|---|---|---|---|
| magic_code00 | 0xC1C884 | 24508 | 141 | 39 |
| ExecAnimType | 0xC2E8D4 | 412 | 125 | 39 |
| set_magic_code | 0xC1D9E3 | 196534 | 126 | 16 |
| CheckAITarget | 0xC21F85 | 165 | 21 | 13 |
| ExecEventAnimCmd | 0xC2C085 | 593 | 18 | 12 |
| GetBattleVar | 0xC21E64 | 18 | 14 | 11 |
| DoTargetEffect | 0xC23886 | 646 | 45 | 10 |
| UpdateTargetCursors | 0xC1B76F | 532 | 34 | 10 |
| DoAttackerEffect | 0xC23E85 | 532 | 44 | 9 |
| RandCharAction | 0xC20493 | 0 | 9 | 7 |
| AIRand3 | 0xC21A96 | 620 | 28 | 7 |
| ExecCmd_C213D3 | 0xC213FE | 627 | 45 | 7 |
| BattleCmdNoEffect | 0xC2155D | 3 | 45 | 7 |
| UpdateBattleBG | 0xC2B27E | 269533 | 8 | 7 |
| ExecGfxCmd | 0xC1956B | 2407 | 20 | 5 |
| UpdateMenuInput | 0xC15529 | 270274 | 64 | 5 |
| DlgTextCmd | 0xC15E51 | 496 | 16 | 5 |
| RandCharAction | 0xC2049F | 0 | 5 | 4 |
| GetMPCost | 0xC24FB1 | 3 | 6 | 4 |
| CheckBattleEnd | 0xC247F8 | 1 | 6 | 4 |
| magic_code06_b | 0xC1F4BE | 1190 | 8 | 4 |
| magic_code06_b | 0xC1F4CE | 5541 | 8 | 4 |
| magic_code06_b | 0xC1F4EA | 1773 | 8 | 4 |
| magic_code06_b | 0xC1F4FA | 3398 | 8 | 4 |
| IncColor | 0xC1FDB0 | 320 | 13 | 4 |
| print_code_chg | 0xC16704 | 486696 | 18 | 4 |
| FightAttack | 0xC21673 | 0 | 4 | 3 |
| UpdateEquip_C20E77 | 0xC20F2D | 493 | 6 | 3 |
| key_target_left | 0xC17747 | 1 | 4 | 3 |
| key_target_right | 0xC1775E | 1 | 4 | 3 |
| ExecBtlGfx_ext | 0xC10005 | 154864 | 14 | 3 |
| DoNextAICmd | 0xC21B02 | 974 | 15 | 2 |
| ShowAttackName | 0xC2367D | 216 | 8 | 2 |
| CalcMagicEffect | 0xC2473D | 0 | 2 | 2 |
| key_target_left | 0xC1773F | 1 | 3 | 2 |
| key_target_right | 0xC17756 | 1 | 3 | 2 |
| UpdateCircleShape | 0xC2D53E | 1430 | 9 | 2 |
| UpdateMenuWindow | 0xC14512 | 253154 | 28 | 2 |
| mon_mode_chg_main | 0xC2E6C1 | 156 | 6 | 2 |
| InitBattleType | 0xC22E77 | 40 | 3 | 1 |
| InitCmdList | 0xC253D6 | 43 | 5 | 1 |
| UpdateStatus | 0xC243AC | 181 | 18 | 1 |
| UpdateStatus | 0xC243BF | 64 | 8 | 1 |
| UpdateStatus | 0xC243D7 | 76 | 12 | 1 |
| DoLevelUp | 0xC260F1 | 75 | 9 | 1 |
| InitWeaponType | 0xC1C270 | 182 | 5 | 1 |
| DlgTextCmd_12 | 0xC15EED | 62 | 4 | 1 |
| ListTextCmd | 0xC16411 | 6617 | 16 | 1 |
| DrawCharSlotInfo | 0xC167CC | 352272 | 4 | 1 |
| DrawCharSlot4Info | 0xC16814 | 352272 | 7 | 1 |
| UpdateSprites | 0xC127B5 | 269493 | 2 | 1 |
| ApplyDmg | 0xC21300 | 519 | 2 | 0 |
| CalcMaxHPMP_C2283C | 0xC2284D | 242 | 4 | 0 |
| CalcItemEffect | 0xC22B13 | 8 | 7 | 0 |
| InitTarget | 0xC22701 | 1095 | 4 | 0 |
| UpdateCmdList | 0xC252D2 | 168 | 5 | 0 |
| ValidateSpellList | 0xC256F3 | 2208 | 3 | 0 |
| UpdateStatus | 0xC243EF | 34 | 4 | 0 |
| EquipStatusMod | 0xC244A4 | 646 | 3 | 0 |
| DecCounters | 0xC25ADE | 8714 | 3 | 0 |
| DecCounters | 0xC25AE5 | 44627 | 4 | 0 |
| magic_code03_a | 0xC1F393 | 3654 | 8 | 0 |
| magic_code03_a | 0xC1F39F | 17004 | 8 | 0 |
| InitCmdSelect | 0xC17CDE | 285 | 16 | 0 |
| CalcMonsterPos | 0xC11604 | 40 | 4 | 0 |
| UpdateCharText | 0xC144CB | 252739 | 6 | 0 |
| UpdateCharText | 0xC144E2 | 258281 | 4 | 0 |
| InitThrowSelect | 0xC1587F | 8 | 5 | 0 |
| InitToolsSelect | 0xC158BB | 80 | 5 | 0 |
| set_s_mess_poi | 0xC2BB15 | 30 | 2 | 0 |
| TfrCharText | 0xC2AC79 | 269493 | 4 | 0 |
| player_pat_chr_set | 0xC136F5 | 68 | 4 | 0 |
