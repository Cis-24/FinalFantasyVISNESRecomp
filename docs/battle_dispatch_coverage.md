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

Update after r25 (random actions of a muddled member, Shock, Health, Possess, running away and the target cursor in the back, pincer and side attack, three battles): 843 of 1079 distinct addresses, i.e. +32; 939 of 1187 pairs reached, 2 of 72 sites never run (4 before). Both `RandCmdTbl` sites of `RandCharAction` run for the first time and reach all their targets: each random action of a muddled Terra runs the entry of each of her four commands, and her battle command list is poked twice so that all ten entries are dispatched (the Rage and Dance entries `C205D1` and `C2059C` had been reached before through the Rage and Dance status of r13 and r06, so they add pairs but no address). The four sites of `key_target_left` and `key_target_right` are fully reached (+10: the back, pincer and side types on the character and the monster side); `UpdateTargetCursors` gained four entries (6 unreached). Further: the command handlers of Shock, Health and Possess (`C2171A`, `C2171E`, `C217E5`, through `ExecCmd_C213D3` and `BattleCmdNoEffect`) and of running away (`C220DE`), Possess in `DoAttackerEffect` (`C24095`) and `DoTargetEffect` (`C23B98`), the run animation (`ExecAnimType` `C2EE30`) and one more `ExecAnimType` entry (`C2EACB`), `ShowAttackName` `C23694`, `set_magic_code` `C1DB64` and `DlgTextCmd` `C15F0C`. The two sites never run are `FightAttack` (`C21673`) and `CalcMagicEffect` (`C2473D`). The table is re-measured over r05, r06 and r13 to r25.

Update after r26 (Umaro's attacks, Bushido levels 4 to 6 and a Rage with Charm, one battle) and r04 (the menu tour, measured for the first time): 865 of 1079 distinct addresses, i.e. +22; 961 of 1187 pairs reached, no site left that never ran (2 before). `FightAttack` (`UmaroAttackTbl`, `C21673`) runs for the first time and reaches Tackle, Throw and Storm (Wedge's slot carries actor 13 with Blizzard Orb and Rage Ring; Fight was reached before through the normal entry). `DoAttackerEffect` gained Quadra Slam and Empowerer (6 unreached), `DoTargetEffect` Stunner and Charm (the second Rage attack of Nightshade; 7 unreached); the rest are animation script entries of these attacks (`magic_code00` 5, `set_magic_code` 3, `ExecAnimType` 2, `ExecEventAnimCmd` 1) and two `UpdateTargetCursors` entries. `CalcMagicEffect` (`C2473D`) is called from the field menu only (a spell or a restorative item used there, `field_menu.asm` and `item.asm`), so none of the battle routes could reach it; r04 casts Cure and uses a Tonic in the menu and reaches both targets. r04 is measured up to frame 16800, just before its `reset`: B cannot replay a console reset, and the script's frame counter starts again at the reset. The table is re-measured over r04, r05, r06 and r13 to r26.

The unreached targets are resolved and generated like all others, but no run has exercised them. The large groups are
spell and attack animation scripts (`magic_code00`, `set_magic_code`, `ExecAnimType`, `ExecEventAnimCmd`), the target
and attacker effect handlers (`DoTargetEffect`, `DoAttackerEffect`), the monster AI (`AIRand3`, `CheckAITarget`,
`GetBattleVar`, `DoNextAICmd`; the guards never act in the routes).

| Function | Site | Site hits | Targets | Unreached |
|---|---|---|---|---|
| ExecAnimType | 0xC2E8D4 | 461 | 125 | 35 |
| magic_code00 | 0xC1C884 | 25919 | 141 | 34 |
| CheckAITarget | 0xC21F85 | 165 | 21 | 13 |
| set_magic_code | 0xC1D9E3 | 209892 | 126 | 12 |
| GetBattleVar | 0xC21E64 | 18 | 14 | 11 |
| ExecEventAnimCmd | 0xC2C085 | 668 | 18 | 11 |
| AIRand3 | 0xC21A96 | 620 | 28 | 7 |
| DoTargetEffect | 0xC23886 | 703 | 45 | 7 |
| UpdateBattleBG | 0xC2B27E | 289842 | 8 | 7 |
| DoAttackerEffect | 0xC23E85 | 578 | 44 | 6 |
| ExecGfxCmd | 0xC1956B | 2644 | 20 | 5 |
| UpdateMenuInput | 0xC15529 | 290579 | 64 | 5 |
| GetMPCost | 0xC24FB1 | 3 | 6 | 4 |
| CheckBattleEnd | 0xC247F8 | 1 | 6 | 4 |
| UpdateTargetCursors | 0xC1B76F | 580 | 34 | 4 |
| magic_code06_b | 0xC1F4BE | 1373 | 8 | 4 |
| magic_code06_b | 0xC1F4CE | 6083 | 8 | 4 |
| magic_code06_b | 0xC1F4EA | 1929 | 8 | 4 |
| magic_code06_b | 0xC1F4FA | 3932 | 8 | 4 |
| IncColor | 0xC1FDB0 | 341 | 13 | 4 |
| DlgTextCmd | 0xC15E51 | 531 | 16 | 4 |
| print_code_chg | 0xC16704 | 523111 | 18 | 4 |
| ExecCmd_C213D3 | 0xC213FE | 674 | 45 | 3 |
| BattleCmdNoEffect | 0xC2155D | 13 | 45 | 3 |
| UpdateEquip_C20E77 | 0xC20F2D | 667 | 6 | 3 |
| ExecBtlGfx_ext | 0xC10005 | 165216 | 14 | 3 |
| DoNextAICmd | 0xC21B02 | 974 | 15 | 2 |
| UpdateCircleShape | 0xC2D53E | 1616 | 9 | 2 |
| UpdateMenuWindow | 0xC14512 | 272053 | 28 | 2 |
| mon_mode_chg_main | 0xC2E6C1 | 168 | 6 | 2 |
| ShowAttackName | 0xC2367D | 235 | 8 | 1 |
| InitBattleType | 0xC22E77 | 44 | 3 | 1 |
| InitCmdList | 0xC253D6 | 47 | 5 | 1 |
| UpdateStatus | 0xC243AC | 187 | 18 | 1 |
| UpdateStatus | 0xC243BF | 66 | 8 | 1 |
| UpdateStatus | 0xC243D7 | 78 | 12 | 1 |
| DoLevelUp | 0xC260F1 | 75 | 9 | 1 |
| InitWeaponType | 0xC1C270 | 198 | 5 | 1 |
| DlgTextCmd_12 | 0xC15EED | 67 | 4 | 1 |
| ListTextCmd | 0xC16411 | 6709 | 16 | 1 |
| DrawCharSlotInfo | 0xC167CC | 378620 | 4 | 1 |
| DrawCharSlot4Info | 0xC16814 | 378620 | 7 | 1 |
| UpdateSprites | 0xC127B5 | 289798 | 2 | 1 |
| RandCharAction | 0xC20493 | 7 | 9 | 0 |
| RandCharAction | 0xC2049F | 7 | 5 | 0 |
| ApplyDmg | 0xC21300 | 575 | 2 | 0 |
| FightAttack | 0xC21673 | 11 | 4 | 0 |
| CalcMaxHPMP_C2283C | 0xC2284D | 266 | 4 | 0 |
| CalcItemEffect | 0xC22B13 | 8 | 7 | 0 |
| InitTarget | 0xC22701 | 1195 | 4 | 0 |
| CalcMagicEffect | 0xC2473D | 2 | 2 | 0 |
| UpdateCmdList | 0xC252D2 | 185 | 5 | 0 |
| ValidateSpellList | 0xC256F3 | 2277 | 3 | 0 |
| UpdateStatus | 0xC243EF | 34 | 4 | 0 |
| EquipStatusMod | 0xC244A4 | 705 | 3 | 0 |
| DecCounters | 0xC25ADE | 9418 | 3 | 0 |
| DecCounters | 0xC25AE5 | 48141 | 4 | 0 |
| magic_code03_a | 0xC1F393 | 3884 | 8 | 0 |
| magic_code03_a | 0xC1F39F | 17883 | 8 | 0 |
| key_target_left | 0xC1773F | 6 | 3 | 0 |
| key_target_left | 0xC17747 | 8 | 4 | 0 |
| key_target_right | 0xC17756 | 6 | 3 | 0 |
| key_target_right | 0xC1775E | 8 | 4 | 0 |
| InitCmdSelect | 0xC17CDE | 302 | 16 | 0 |
| CalcMonsterPos | 0xC11604 | 44 | 4 | 0 |
| UpdateCharText | 0xC144CB | 271682 | 6 | 0 |
| UpdateCharText | 0xC144E2 | 277546 | 4 | 0 |
| InitThrowSelect | 0xC1587F | 8 | 5 | 0 |
| InitToolsSelect | 0xC158BB | 80 | 5 | 0 |
| set_s_mess_poi | 0xC2BB15 | 33 | 2 | 0 |
| TfrCharText | 0xC2AC79 | 289798 | 4 | 0 |
| player_pat_chr_set | 0xC136F5 | 68 | 4 | 0 |
