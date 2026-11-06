# Local snesrecomp patches

The snesrecomp pin (`framework_pins.txt`, gitlink `snesrecomp`) points at the tip of the
branch `ff6/patches`. The branch is not in the upstream repository but in the fork that
`.gitmodules` points to. The patches build on each other:

| Patch | Base | Commit | Tree |
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
| `0012-fix-keep-a-jmp-abs-x-dispatch-local-while-its-path-h.patch` | `a77cd7eae8fbb46d2e39f019444cb1ddee777a37` (0011) | `7b570a032de317772c0cf518d305fe27aed3c611` (branch `ff6/patches`) | `91c7d8f498a585e786886ba3ff01d90387773180` |

The pin is the commit of 0012.

0001: The DSP register mirror starts with the power-on values of snes9x 1.63
(`initial_regs`), so that FF6 boots frame-identical to the snes9x reference. Background and
verification: `docs/STATUS.md`, section "Framework patch: DSP power-on values".

0002: Codegen reads the pointer of `JMP (abs)` (opcode `$6C`) from bank 0 instead of PB
(the target bank stays PB). Without the fix, the AOT event dispatch `jmp ($002a)` in C0 jumps
into nowhere. Background and verification: `docs/STATUS.md`, sections "Event engine AOT break:
cause" and "Framework patch: JMP (abs) from bank 0".

0003: The beam driver lets a parked RDNMI poll (`lda`/`bit $4210`, `bpl`) read the flag before
the NMI. Without the fix, FF6 hangs in `EventCmd_f0/ef/f1`.

0004: The mosaic table is built per line whenever the size changes, instead of only on line 0,
which the beam driver never renders. Without the fix, FF6 crashes at the first mosaic (battle
transition).

0005: HDMA starts at V=0 of the field being drawn: VBlank entries of the journal before the init,
a full HDMA step in the H-blank of line 0. Without the fix, every table step lands 1 to 2 lines
too late.

Background and verification for 0003 to 0005: `docs/STATUS.md`, sections "Routes r02/r03" and
"Framework patches: field runtime".

0006: The raster journal also tracks the DMA channel registers (`$4300-$437F`); the render walk
sees the field's channel for each line and gives the guest its registers back afterwards. Without
the fix, FF6 writes the scroll table into VRAM every other frame on the two maps with a wavy BG2.

0007: The vertical mosaic block counts from the first visible line. Without the fix, every
block is off by 1 line.

Background and verification for 0006 and 0007: `docs/STATUS.md`, sections "Field IRQ/HDMA against
snesref" and "Framework patches: field modes".

0008: A field's raster baseline comes from the end of the render walk, i.e. after its HDMA,
instead of from the snapshot at V=225. Without the fix, two baselines alternate for a register
that only HDMA writes; in FF6's Item and Skills menus every other frame was black.

0009: `ppu_rasterRenderEnd` first applies the writes of the last drawn line (224). With 0008
they would otherwise be lost (FF6 sets `BG1SC` there; a bright stripe in the Skills overview).

0010: The beam driver puts the beam on the master clock (`snes_set_beam_on_master_clock`);
a `$4212` read then synchronizes it instead of advancing it by 64 cycles. Without the fix, the
NMI in FF6's menu started up to 3 lines late, and the color gradient of the Equip list was offset.

Background and verification for 0008 to 0010: `docs/STATUS.md`, section "Menu tour r04".

0011: The mode 2 renderer reads the offset-per-tile rows at BG3VOFS (H) and BG3VOFS + 8 (V),
and a V entry replaces BG1VOFS so that line y shows source line entry + y. The corrections
from snes9x (`- 1`, `+ 1`) apply there to BGnVOFS + 1 and 0-based lines; in the framework they
were one line off. Without the fix, the reels of the Slot battle command stood still.

0012: A `JMP (abs)`/`JMP (abs,X)` dispatch whose path holds a PHP stays inside the function
(local computed jump, targets carry the PHP history, including HiROM targets below $8000). The
Python decoder and the native analyzer do the same. Without the fix, `ValidateSpellList`, after
the `plp` in the split-off table targets, pulled `plx` with 16 bits, and the `rts` jumped into
the zero page.

Background and verification for 0011 and 0012: `docs/STATUS.md`, section "Pin session 11-05 (OPT and plp)".

## Rebuilding in a fresh clone

Normally `git submodule update --init` is enough, because the fork contains the pin commit.
If the fork is unreachable, the state can be rebuilt from the upstream repository and the
patches (cwd = repository root; point the submodule at the upstream repository first):

```bash
git -C snesrecomp switch -c ff6/patches 147b55e252dcb3e7680a99c7c2f50e7183891844
git -C snesrecomp am ../patches/snesrecomp/0001-*.patch ../patches/snesrecomp/0002-*.patch ../patches/snesrecomp/0003-*.patch ../patches/snesrecomp/0004-*.patch ../patches/snesrecomp/0005-*.patch ../patches/snesrecomp/0006-*.patch ../patches/snesrecomp/0007-*.patch ../patches/snesrecomp/0008-*.patch ../patches/snesrecomp/0009-*.patch ../patches/snesrecomp/0010-*.patch ../patches/snesrecomp/0011-*.patch ../patches/snesrecomp/0012-*.patch
git -C snesrecomp rev-parse HEAD^{tree}
```

The commit hashes differ (committer and date); the tree is what counts. It must be
`91c7d8f498a585e786886ba3ff01d90387773180` (intermediate states: see the table).
