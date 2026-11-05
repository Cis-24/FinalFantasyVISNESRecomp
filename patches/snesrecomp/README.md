# Lokale snesrecomp-Patches

Der snesrecomp-Pin (`framework_pins.txt`, Gitlink `snesrecomp`) zeigt auf das Ende des
Branchs `ff6/patches`. Der Branch liegt nicht im Upstream-Repo, sondern im Fork, auf den
`.gitmodules` zeigt. Die Patches bauen aufeinander auf:

| Patch | Basis | Commit | Tree |
|---|---|---|---|
| `0001-fix-power-on-the-dsp-register-mirror-with-snes9x-s-i.patch` | `147b55e252dcb3e7680a99c7c2f50e7183891844` | `0df8f701976b046f239f2f8e28a61e676fcad12a` | `28940d0d6adfd98fd240177dbb4225e161aff167` |
| `0002-fix-read-the-jmp-abs-pointer-from-bank-0-in-codegen.patch` | `0df8f701976b046f239f2f8e28a61e676fcad12a` (0001) | `0e747f99fc55c4027a5daf10b306beac8d4922ac` | `a066da8556b870e053343eef699eaae85ad0756d` |
| `0003-fix-let-a-parked-rdnmi-poll-read-the-flag-before-the.patch` | `0e747f99fc55c4027a5daf10b306beac8d4922ac` (0002) | `8961e6c6cbeec277c6dfbd8286339746460f285c` | `1df6e4f91d530b1b8dd6769772112f0d918e222b` |
| `0004-fix-build-the-ppu-mosaic-table-on-the-line-that-need.patch` | `8961e6c6cbeec277c6dfbd8286339746460f285c` (0003) | `b068f69834d49426552416edf4d04dd6df160405` | `7c8a9180499894ebea4f2b4796e319b2cedd69cf` |
| `0005-fix-start-hdma-at-v-0-of-the-field-being-drawn.patch` | `b068f69834d49426552416edf4d04dd6df160405` (0004) | `e9bcbf328c7095b0cf472d42f990c7b8fa9a7b1b` | `36c06c10d9ddee64b60067b2def486a2d122318f` |
| `0006-fix-give-the-render-walk-each-line-s-dma-channel-reg.patch` | `e9bcbf328c7095b0cf472d42f990c7b8fa9a7b1b` (0005) | `c2d515ccd146fc8e17673c1cb9bea9d503b2d6b1` | `60d4a424b5a3ffad03a4ad8cf25d48b24362d000` |
| `0007-fix-count-the-vertical-mosaic-block-from-the-first-v.patch` | `c2d515ccd146fc8e17673c1cb9bea9d503b2d6b1` (0006) | `3526b299a19ddc1670c6ec3e2849b65273edcaa5` | `c3c0b7e83880d8b92f46d9a51f3778fc6f71276c` |
| `0008-fix-take-the-field-s-raster-baseline-from-the-end-of.patch` | `3526b299a19ddc1670c6ec3e2849b65273edcaa5` (0007) | `d35131ba8b5c1cfea05ea18768deb24818a9b52c` | `c0e6e32b244447b9a1ec42be3da162aa626d1ffc` |
| `0009-fix-apply-the-last-drawn-raster-line-before-the-walk.patch` | `d35131ba8b5c1cfea05ea18768deb24818a9b52c` (0008) | `23ede2b7438ca83c31a3fb55376abf9a7901ca9b` | `028b8f1a9184061e1e0d43f549177f9ffb188f27` |
| `0010-fix-sync-the-beam-on-hvbjoy-instead-of-the-polling-t.patch` | `23ede2b7438ca83c31a3fb55376abf9a7901ca9b` (0009) | `a76eb19a0d9dd2da14a1451f7fc1c4dd771c2ed5` | `1b2415154bd82be86b9b81280658ff197d6a4492` |
| `0011-fix-read-the-mode-2-offset-per-tile-rows-at-bg3vofs-.patch` | `a76eb19a0d9dd2da14a1451f7fc1c4dd771c2ed5` (0010) | `a77cd7eae8fbb46d2e39f019444cb1ddee777a37` | `f4b54b3d9f8aeb7ba76549f85f7ce57907bc5797` |
| `0012-fix-keep-a-jmp-abs-x-dispatch-local-while-its-path-h.patch` | `a77cd7eae8fbb46d2e39f019444cb1ddee777a37` (0011) | `7b570a032de317772c0cf518d305fe27aed3c611` (Branch `ff6/patches`) | `91c7d8f498a585e786886ba3ff01d90387773180` |

Pin ist der Commit von 0012.

0001: DSP-Registerspiegel startet mit den Einschaltwerten von snes9x 1.63
(`initial_regs`), damit FF6 frame-gleich zur snes9x-Referenz bootet. Hintergrund und
Prüfung: `docs/STATUS.md`, Abschnitt „Framework-Patch DSP-Einschaltwerte“.

0002: Codegen liest den Zeiger von `JMP (abs)` (Opcode `$6C`) aus Bank 0 statt aus PB
(Zielbank bleibt PB). Ohne den Fix springt der AOT-Event-Dispatch `jmp ($002a)` in C0 ins
Leere. Hintergrund und Prüfung: `docs/STATUS.md`, Abschnitte „Event-Engine-AOT-Bruch:
Ursache“ und „Framework-Patch JMP (abs) aus Bank 0“.

0003: Der Beam-Driver lässt einen geparkten RDNMI-Poll (`lda`/`bit $4210`, `bpl`) vor dem NMI
das Flag lesen. Ohne den Fix hängt FF6 in `EventCmd_f0/ef/f1`.

0004: Die Mosaik-Tabelle entsteht je Zeile bei Größenwechsel statt nur in Zeile 0, die der
Beam-Driver nie rendert. Ohne den Fix stürzt FF6 beim ersten Mosaik ab (Kampfübergang).

0005: HDMA startet bei V=0 des gezeichneten Felds: VBlank-Einträge des Journals vor dem Init,
voller HDMA-Schritt im H-Blank von Zeile 0. Ohne den Fix liegt jede Tabellenstufe 1 bis 2 Zeilen
zu spät.

Hintergrund und Prüfung von 0003 bis 0005: `docs/STATUS.md`, Abschnitte „Routen r02/r03“ und
„Framework-Patches Field-Runtime“.

0006: Das Raster-Journal führt auch die DMA-Kanalregister (`$4300-$437F`); der Render-Walk sieht
je Zeile den Kanal des Felds und gibt dem Gast danach seine Register zurück. Ohne den Fix schreibt
FF6 auf den zwei Maps mit welligem BG2 jeden zweiten Frame die Scrolltabelle ins VRAM.

0007: Der vertikale Mosaik-Block zählt ab der ersten sichtbaren Zeile. Ohne den Fix liegt jeder
Block 1 Zeile versetzt.

Hintergrund und Prüfung von 0006 und 0007: `docs/STATUS.md`, Abschnitte „Field-IRQ/HDMA gegen
snesref“ und „Framework-Patches Field-Modi“.

0008: Die Raster-Baseline eines Felds kommt vom Ende des Render-Walks, also nach dessen HDMA,
statt aus dem Abzug bei V=225. Ohne den Fix wechseln sich bei einem Register, das nur HDMA
schreibt, zwei Baselines ab; in FF6s Item- und Skills-Menü war jedes zweite Bild schwarz.

0009: `ppu_rasterRenderEnd` wendet zuerst die Writes der letzten gezeichneten Zeile (224) an.
Mit 0008 gingen sie sonst verloren (FF6 setzt dort `BG1SC`, heller Streifen in der Skills-Übersicht).

0010: Der Beam-Driver stellt den Strahl auf die Master-Uhr (`snes_set_beam_on_master_clock`);
ein `$4212`-Read synchronisiert ihn dann, statt ihn um 64 Takte vorzustellen. Ohne den Fix
begann der NMI in FF6s Menü bis zu 3 Zeilen zu spät, der Farbverlauf der Equip-Liste lag versetzt.

Hintergrund und Prüfung von 0008 bis 0010: `docs/STATUS.md`, Abschnitt „Menü-Tour r04“.

0011: Der Mode-2-Renderer liest die Offset-per-Tile-Zeilen bei BG3VOFS (H) und BG3VOFS + 8 (V),
und ein V-Eintrag ersetzt BG1VOFS so, dass Zeile y die Quellzeile Eintrag + y zeigt. Die Korrekturen
aus snes9x (`- 1`, `+ 1`) gelten dort für BGnVOFS + 1 und 0-basierte Zeilen, im Framework lagen sie
eine Zeile daneben. Ohne den Fix standen die Walzen des Kampfbefehls Slot still.

0012: Ein `JMP (abs)`/`JMP (abs,X)`-Dispatch, dessen Pfad ein PHP hält, bleibt in der Funktion
(lokaler berechneter Sprung, Ziele mit der PHP-Historie, auch HiROM-Ziele unter $8000). Python-Decoder
und nativer Analyzer gleich. Ohne den Fix zog `ValidateSpellList` nach dem `plp` in den
abgespaltenen Tabellenzielen `plx` mit 16 Bit, und das `rts` sprang in die Zero Page.

Hintergrund und Prüfung von 0011 und 0012: `docs/STATUS.md`, Abschnitt „Pin-Session 11-05 (OPT und plp)“.

## Nachbau in einem frischen Klon

Normalerweise reicht `git submodule update --init`, weil der Fork den Pin-Commit enthält.
Ist der Fork nicht erreichbar, lässt sich der Stand aus dem Upstream-Repo und den Patches
nachbauen (cwd = Repo-Wurzel, Submodul vorher auf das Upstream-Repo zeigen lassen):

```bash
git -C snesrecomp switch -c ff6/patches 147b55e252dcb3e7680a99c7c2f50e7183891844
git -C snesrecomp am ../patches/snesrecomp/0001-*.patch ../patches/snesrecomp/0002-*.patch ../patches/snesrecomp/0003-*.patch ../patches/snesrecomp/0004-*.patch ../patches/snesrecomp/0005-*.patch ../patches/snesrecomp/0006-*.patch ../patches/snesrecomp/0007-*.patch ../patches/snesrecomp/0008-*.patch ../patches/snesrecomp/0009-*.patch ../patches/snesrecomp/0010-*.patch ../patches/snesrecomp/0011-*.patch ../patches/snesrecomp/0012-*.patch
git -C snesrecomp rev-parse HEAD^{tree}
```

Die Commit-Hashes weichen ab (Committer und Datum), maßgeblich ist der Tree. Er muss
`91c7d8f498a585e786886ba3ff01d90387773180` sein (Zwischenstände: siehe Tabelle).
