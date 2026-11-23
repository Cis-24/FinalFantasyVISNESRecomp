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

Update after r27 (monster attacks with special effects in six battles, the formation forced through `$11E0`): 878 of 1079 distinct addresses, i.e. +13; 974 of 1187 pairs reached. `DoAttackerEffect` gained Launcher, Bababreath and Escape (3 unreached, all used by no attack or weapon: `MORE_MP_CRIT`, `QUARTER_DMG`, `HALF_DMG`), `DoTargetEffect` Engulf, Bababreath, Evil Toot and Fallen One (3 unreached: Leap, which needs Gau on the Veldt; Tapir, which no monster AI script, rage, sketch or control list uses; Phantasm, one in three of Chadarnook's counter to a hit); the rest are animation script entries of these attacks (`ExecAnimType` 3, `magic_code00` 2) and one `GetBattleVar` entry. The table is re-measured over r04, r05, r06 and r13 to r27.

Update after r28 (dances on their own battle backgrounds, Rages, Magitek and curing items in six battles; the background is set in the battle event): 899 of 1079 distinct addresses, i.e. +21; 995 of 1187 pairs reached. `ExecAnimType` gained 13 (the dance steps Harvester, Antlion, Specter, Land Slide, Snare, Cave In and Snowball; Magitek Bio Blast, Confuser and X-Fer; the Rage attacks Slimer and Grav Bomb; the items Revivify, Eyedrop and Remedy), `magic_code00` 4 (`$80/$47` of Confuser, `$80/$49` of Virite, `$80/$4B` of Megazerk, `$80/$0F` of Grav Bomb), `DoTargetEffect` Tapir (the 1/16 step of Love Sonata), and one entry each of `set_magic_code`, `UpdateCircleShape` and `UpdateSprites`. Part of the gap left in the two animation tables is used by no animation in the ROM: the `ExecAnimType` types $02, $06, $0D, $1E, $21, $2B, $2C and $2E are the init function of no attack animation (`data/attack_anim_prop.asm`), and the `magic_code00` sub-commands $0D, $15, $1D, $2A, $2F, $30, $6E, $74 and $81 appear in no animation script (`btlgfx/attack_anim_script.asm`). The rest belongs to monster attacks (WaveCannon, Hyperdrive, H-Bomb, Soul Out, Clear, Fifty Gs, Revenger, Goner, TekBarrier, Delta Hit, Lode Stone, Scar Beam, the monster side of Shock Wave), the desperation attacks Mirager and TigerBreak (Locke and Sabin), the boss death, Chadarnook and block animations, and the event animations (Tritoch, the espers turning into magicite, the characters running). `UpdateBattleBG` (7 of 8 unreached) belongs to the backgrounds with an effect (clouds, river, trains, waterfall, Cyan's dream, the last Kefka battle), which the battle event can set the same way. The table is re-measured over r04, r05, r06 and r13 to r28.

Update after r29 (the seven battle backgrounds with an update function and the desperation attacks Mirager and TigerBreak, seven battles; the background is set in the battle event as in r28): 908 of 1079 distinct addresses, i.e. +9; 1004 of 1187 pairs reached. `UpdateBattleBG` is now fully reached (clouds `$07`, river `$0D`, train `$0F` (shared with `$21`), waterfall `$1F`, Magitek train car `$2C`, Cyan's dream `$2E`, final Kefka `$36`; the function for `$36` returns early unless the death animation runs), and `ExecAnimType` gained the init types `$66` (Mirager) and `$6E` (TigerBreak). Wedge and Vicks are made Locke and Sabin through their battle actor number (`$3ED8` + slot) for this; their animation scripts use no animation command that was not reached before. The table is re-measured over r04, r05, r06 and r13 to r29.

Update after r30 (monster attacks with an animation init or animation sub-commands of their own, six battles with the formation forced through `$11E0` as in r27: HeavyArmor, Powerdemon, IO, Hemophyte, Curley, Larry and Moe, Final Kefka): 921 of 1079 distinct addresses, i.e. +13; 1017 of 1187 pairs reached. `ExecAnimType` gained the init types `$20` (TekBarrier), `$73` (Soul Out), `$76` (WaveCannon), `$60` (Goner) and `$72` (Hyperdrive) (12 unreached), `magic_code00` the sub-commands `$66` (the monster side of Shock Wave), `$4C` and `$4D` (Delta Hit's triangle), `$56` and `$89` (Goner) (23 unreached), `set_magic_code` the monster palette subtraction `$b9` and `$bc` (9 unreached) and `ExecEventAnimCmd` its sound command (`C2C171`, from Final Kefka's battle event; 10 unreached). Left in the animation gap and reachable: H-Bomb (`$75`, only from Setzer's Slot), the boss death, Chadarnook, block and monster steal animations, and the event animations (`$79`, `$7A`); Clear (`$58`, `$48`) is used by no monster, rage, sketch or control list. The table is re-measured over r04, r05, r06 and r13 to r30.

The unreached targets are resolved and generated like all others, but no run has exercised them. The large groups are
spell and attack animation scripts (`magic_code00`, `set_magic_code`, `ExecAnimType`, `ExecEventAnimCmd`), the target
and attacker effect handlers (`DoTargetEffect`, `DoAttackerEffect`), the monster AI (`AIRand3`, `CheckAITarget`,
`GetBattleVar`, `DoNextAICmd`; the guards never act in the routes).

| Function | Site | Site hits | Targets | Unreached |
|---|---|---|---|---|
| magic_code00 | 0xC1C884 | 41608 | 141 | 23 |
| CheckAITarget | 0xC21F85 | 197 | 21 | 13 |
| ExecAnimType | 0xC2E8D4 | 650 | 125 | 12 |
| GetBattleVar | 0xC21E64 | 20 | 14 | 10 |
| ExecEventAnimCmd | 0xC2C085 | 1024 | 18 | 10 |
| set_magic_code | 0xC1D9E3 | 338676 | 126 | 9 |
| AIRand3 | 0xC21A96 | 724 | 28 | 7 |
| ExecGfxCmd | 0xC1956B | 3568 | 20 | 5 |
| UpdateMenuInput | 0xC15529 | 361033 | 64 | 5 |
| GetMPCost | 0xC24FB1 | 3 | 6 | 4 |
| CheckBattleEnd | 0xC247F8 | 2 | 6 | 4 |
| UpdateTargetCursors | 0xC1B76F | 750 | 34 | 4 |
| magic_code06_b | 0xC1F4BE | 2109 | 8 | 4 |
| magic_code06_b | 0xC1F4CE | 9136 | 8 | 4 |
| magic_code06_b | 0xC1F4EA | 3342 | 8 | 4 |
| magic_code06_b | 0xC1F4FA | 4504 | 8 | 4 |
| IncColor | 0xC1FDB0 | 532 | 13 | 4 |
| DlgTextCmd | 0xC15E51 | 802 | 16 | 4 |
| print_code_chg | 0xC16704 | 649464 | 18 | 4 |
| DoAttackerEffect | 0xC23E85 | 750 | 44 | 3 |
| ExecCmd_C213D3 | 0xC213FE | 877 | 45 | 3 |
| BattleCmdNoEffect | 0xC2155D | 32 | 45 | 3 |
| UpdateEquip_C20E77 | 0xC20F2D | 887 | 6 | 3 |
| ExecBtlGfx_ext | 0xC10005 | 184140 | 14 | 3 |
| DoNextAICmd | 0xC21B02 | 1209 | 15 | 2 |
| DoTargetEffect | 0xC23886 | 914 | 45 | 2 |
| UpdateMenuWindow | 0xC14512 | 337054 | 28 | 2 |
| mon_mode_chg_main | 0xC2E6C1 | 246 | 6 | 2 |
| ShowAttackName | 0xC2367D | 335 | 8 | 1 |
| InitBattleType | 0xC22E77 | 69 | 3 | 1 |
| InitCmdList | 0xC253D6 | 66 | 5 | 1 |
| UpdateStatus | 0xC243AC | 224 | 18 | 1 |
| UpdateStatus | 0xC243BF | 85 | 8 | 1 |
| UpdateStatus | 0xC243D7 | 79 | 12 | 1 |
| DoLevelUp | 0xC260F1 | 91 | 9 | 1 |
| InitWeaponType | 0xC1C270 | 244 | 5 | 1 |
| UpdateCircleShape | 0xC2D53E | 2607 | 9 | 1 |
| DlgTextCmd_12 | 0xC15EED | 116 | 4 | 1 |
| ListTextCmd | 0xC16411 | 7129 | 16 | 1 |
| DrawCharSlotInfo | 0xC167CC | 469524 | 4 | 1 |
| DrawCharSlot4Info | 0xC16814 | 469524 | 7 | 1 |
| RandCharAction | 0xC20493 | 7 | 9 | 0 |
| RandCharAction | 0xC2049F | 7 | 5 | 0 |
| ApplyDmg | 0xC21300 | 708 | 2 | 0 |
| FightAttack | 0xC21673 | 11 | 4 | 0 |
| CalcMaxHPMP_C2283C | 0xC2284D | 416 | 4 | 0 |
| CalcItemEffect | 0xC22B13 | 8 | 7 | 0 |
| InitTarget | 0xC22701 | 1556 | 4 | 0 |
| CalcMagicEffect | 0xC2473D | 2 | 2 | 0 |
| UpdateCmdList | 0xC252D2 | 254 | 5 | 0 |
| ValidateSpellList | 0xC256F3 | 2715 | 3 | 0 |
| UpdateStatus | 0xC243EF | 45 | 4 | 0 |
| EquipStatusMod | 0xC244A4 | 916 | 3 | 0 |
| DecCounters | 0xC25ADE | 11647 | 3 | 0 |
| DecCounters | 0xC25AE5 | 59955 | 4 | 0 |
| magic_code03_a | 0xC1F393 | 5308 | 8 | 0 |
| magic_code03_a | 0xC1F39F | 36079 | 8 | 0 |
| UpdateBattleBG | 0xC2B27E | 360321 | 8 | 0 |
| key_target_left | 0xC1773F | 6 | 3 | 0 |
| key_target_left | 0xC17747 | 8 | 4 | 0 |
| key_target_right | 0xC17756 | 6 | 3 | 0 |
| key_target_right | 0xC1775E | 8 | 4 | 0 |
| InitCmdSelect | 0xC17CDE | 351 | 16 | 0 |
| CalcMonsterPos | 0xC11604 | 69 | 4 | 0 |
| UpdateCharText | 0xC144CB | 336921 | 6 | 0 |
| UpdateCharText | 0xC144E2 | 343886 | 4 | 0 |
| InitThrowSelect | 0xC1587F | 8 | 5 | 0 |
| InitToolsSelect | 0xC158BB | 80 | 5 | 0 |
| set_s_mess_poi | 0xC2BB15 | 33 | 2 | 0 |
| TfrCharText | 0xC2AC79 | 360252 | 4 | 0 |
| UpdateSprites | 0xC127B5 | 360252 | 2 | 0 |
| player_pat_chr_set | 0xC136F5 | 68 | 4 | 0 |
