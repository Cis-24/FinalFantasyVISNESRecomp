# Final Fantasy VI Recomp

A native recompilation of **Final Fantasy VI** for the SNES (released in North
America as Final Fantasy III), built on
[snesrecomp](https://github.com/RetroPortingToolKit/snesrecomp).

The game's 65816 code is translated ahead of time into C and compiled into a
native executable. Code that cannot be proven statically still runs in the
framework's interpreter, so the port stays correct while more of it moves to
native code. Progress is checked against a reference emulator with scripted
input routes.

> **You must legally own a copy of the game.** No ROM data is distributed with
> this project, in the repository or in any release. The recompiled C is
> generated locally from your own copy and is never committed.

> This is an unofficial fan project. It is not affiliated with, endorsed or
> sponsored by Square Enix. FINAL FANTASY is a registered trademark of
> Square Enix Holdings Co., Ltd.

## Status

Work in progress; not yet playable from start to finish.

- Boots to the title screen and runs the intro, the field (walking, doors,
  map changes) and the main menu.
- Battles are the current work. The first battle and a battle with twelve
  commands (Fight, Magic, Summon, Item, Steal, SwdTech, Throw, Tools, Blitz,
  Sketch, Slot, Dance) run through to the victory and back to the field.

Validated routes (`validation/routes`): boot to title, new game to Narshe,
field walk, menu tour, first battle, battle commands, field modes, doors, menu
scrolling. Battles depend on lag frames (ATB and random numbers), so they are
compared against the reference per scene, with the timing dependent values
masked. Each route replays
fixed input and compares memory, video memory and the frame buffer at
checkpoints. Known and explained differences from the reference are masked in
`validation/masks.toml`, each with a reason.

## ROM identity

| | |
|---|---|
| File | `Final Fantasy III (USA).sfc` |
| Publisher | Square Soft |
| Developer | Square |
| Year | 1994 |
| Mapping | hirom |
| Region | USA (North America) |
| Coprocessor | none |
| CRC32 | `a27f1c7a` |
| SHA-256 | `0f51b4fca41b7fd509e4b8f9d543151f68efa5e97b08493e4b2a0c06f5d8d5e2` |

`tools/regen.sh` refuses to run against anything else, so a mismatched
revision fails immediately instead of producing subtly wrong output.

## Build

```sh
git submodule update --init --recursive
bash tools/regen.sh --rom /path/to/Final Fantasy III (USA).sfc
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
```

Development happens on Windows in an MSYS2 MINGW64 shell (GCC, CMake, Ninja).

The ROM does not have to live in the repository. Keeping it on your own
drive is the better habit, and `SNESRECOMP_ROM` sets the path once for a
shell. Without either, `tools/regen.sh` finds `Final Fantasy III (USA).sfc` at the repo root,
then the path the setup wizard recorded in `rom.cfg`; `.gitignore` blocks
both from ever being committed.

`tools/regen.sh` verifies the ROM, generates `src/gen/*.c`, and re-syncs
`recomp/funcs.h`. Re-run it whenever you change anything under `recomp/`.

## Run

```sh
./build/FinalFantasyViSNESRecomp                     # launcher picks the ROM
./build/FinalFantasyViSNESRecomp /path/to/Final Fantasy III (USA).sfc # or name it and skip the launcher
```

With no ROM on the command line the build opens the recomp-ui launcher: a ROM
picker with a verification badge, plus display / audio / input settings. Your
choice is cached in `rom.cfg` beside the executable, so the next launch opens
on it and "Skip launcher on boot" makes it immediate. If the launcher is not
built in (`--no-recomp-ui`), the host falls back to a native file picker.

Either way the ROM is checked against the digests above before anything boots:
a dump that could not have produced this build is refused at the door rather
than mis-executing ten frames in.

## Development

- `bash tools/ff6/regress.sh --quick` regenerates, builds and runs the quick
  suite; `--full` runs every validated route. Reference runs live outside the
  repository; without them the reference comparison is skipped.
- `python tools/ff6/miss_report.py <run>` lists code a run reached that has no
  native translation yet. These misses are resolved before anything new.
- `recomp/symbols.toml` names routines and decides which ones become native
  code; `tools/regen.sh` syncs it into the bank configs.
- `patches/snesrecomp/` documents the framework fixes this port depends on.
  The submodule points at a fork that carries them on the branch `ff6/patches`.
- `docs/STATUS.md` is the running development log.

Never synthesise a result to get past uncovered code, and never edit
`src/gen/` by hand. Fix the config or the framework and regenerate.

## Layout

| Path | What lives there |
|---|---|
| `recomp/` | Analysis input: `bank*.cfg`, `symbols.toml`, `disassembly-layout.json`, generated `funcs.h` |
| `rom_identity.txt` | ROM digests, read by the build, `tools/regen.sh` and CI |
| `src/` | Host code: `main.c`, `game_rtl.c` |
| `src/gen/` | Generated C. Never committed; regenerate locally |
| `snesrecomp/` | Framework submodule (owns `lib/recomp-net`, `lib/retcomm-rbengine`) |
| `recomp-ui/` | Launcher submodule |
| `tools/` | `regen.sh`, the ROM → C pipeline; `tools/ff6/` holds the project's own tools |
| `validation/` | Input routes, expected results, masks and the miss allowlist |
| `patches/snesrecomp/` | Framework fixes carried by the submodule fork |
| `scripts/` | `package_release.sh`, the player-facing zip |
| `framework_pins.txt` | Exact framework commits this project builds against |

## Multiplayer

Single player.

## Credits

- [snesrecomp](https://github.com/RetroPortingToolKit/snesrecomp), the
  recompilation framework, and the project template by Matthew Stanley.
- [recomp-ui](https://github.com/mstan/recomp-ui), the launcher.
- [everything8215/ff6](https://github.com/everything8215/ff6), the Final
  Fantasy VI disassembly (GPL-3.0). Function names, addresses, instruction
  boundaries and dispatch tables in this project come from building it.
- [snes9x](https://github.com/snes9xgit/snes9x), used locally as the
  reference emulator for validation. It is not distributed here.

## License

- This project's own source is under the PolyForm Noncommercial License 1.0.0
  in `LICENSE`.
- Data derived from the ff6 disassembly stays under the GNU General Public
  License v3.0 (`licenses/GPL-3.0.txt`): `recomp/symbols.toml`,
  `recomp/disassembly-layout.json`, the generated `symbols.toml` blocks in
  `recomp/bank*.cfg`, `tools/ff6/symbols_import.toml`,
  `tools/ff6/symbols_overrides.toml` and `tools/ff6/dispatch_sites.toml`.
- The framework carries its own terms (see `snesrecomp/LICENSE` and
  `snesrecomp/THIRD_PARTY_ATTRIBUTION.md`).
- None of these cover the game data, which is not distributed here.
