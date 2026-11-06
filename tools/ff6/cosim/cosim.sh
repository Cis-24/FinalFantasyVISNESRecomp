#!/usr/bin/env bash
# FF6 differential co-simulation (PLAN 5.2, snesrecomp docs/COSIM.md). DEV/DIAGNOSTICS ONLY.
# cwd = GR, MSYS2 MINGW64 (WS/tools/msys.ps1). Changes nothing in the snesrecomp submodule.
#
#   bash tools/ff6/cosim/cosim.sh build [a|b|ab]
#   bash tools/ff6/cosim/cosim.sh gate1|gate2|gate3a|gate3b|gate4a|gate4b [MAX]
#   bash tools/ff6/cosim/cosim.sh avb|avbram [MAX]
#
# A = the game exe built with SNES_COSIM=ON in build-cosim/ (beam frame driver, headless via the
#     SDL dummy drivers, EnableAudio = 0, deterministic audio consumer SNES_COSIM_AUDIO=1).
# B = snesrecomp/cosim/ref_driver.c (interp816 over the runner devices), built from
#     tools/ff6/cosim/CMakeLists.txt into WS/work/cosim/ref-build.
# Gates: 1 = A vs A, 2 = B vs B, 3a/3b = one WRAM byte flipped after cp 20 (must halt at cp 21
# with only 'ram' split), 4a/4b = hash-vs-byte audit every 25 checkpoints. avb compares the full
# state, avbram only the 128 KiB WRAM. Logs: WS/work/logs/cosim_<mode>.txt, stride 1 frame.
set -u
GR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
WS="$(cd "$GR/.." && pwd)"
W="$WS/work/cosim"
LOGS="$WS/work/logs"
mkdir -p "$W" "$LOGS"
cd "$GR"
mode=${1:-help}

if [ "$mode" = build ]; then
  what=${2:-ab}; rc=0
  if [[ $what == *a* ]]; then
    if [ ! -f build-cosim/build.ninja ]; then
      cmake -S . -B build-cosim -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        -DCMAKE_PREFIX_PATH=/mingw64 -DCMAKE_C_COMPILER_LAUNCHER=ccache \
        -DSNES_COSIM=ON > "$LOGS/cosim_a_configure.txt" 2>&1 || { echo "A configure FAIL"; rc=1; }
    fi
    T=$SECONDS
    cmake --build build-cosim > "$LOGS/cosim_a_build.txt" 2>&1 \
      && echo "A build OK ($((SECONDS - T)) s)" \
      || { echo "A build FAIL"; tail -20 "$LOGS/cosim_a_build.txt"; rc=1; }
  fi
  if [[ $what == *b* ]]; then
    if [ ! -f "$W/ref-build/build.ninja" ]; then
      cmake -S tools/ff6/cosim -B "$W/ref-build" -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        > "$LOGS/cosim_b_configure.txt" 2>&1 || { echo "B configure FAIL"; rc=1; }
    fi
    T=$SECONDS
    cmake --build "$W/ref-build" > "$LOGS/cosim_b_build.txt" 2>&1 \
      && echo "B build OK ($((SECONDS - T)) s)" \
      || { echo "B build FAIL"; tail -20 "$LOGS/cosim_b_build.txt"; rc=1; }
  fi
  exit $rc
fi

MAX=${2:-4000}
ROM=$(cygpath -m "${SNESRECOMP_ROM:-$WS/rom/Final Fantasy III (USA).sfc}")
INI="$W/cosim.ini"
sed 's/^EnableAudio = 1/EnableAudio = 0/' validation/regress.ini > "$INI"
EXE_A=$(cygpath -m "$GR/build-cosim/FinalFantasyViSNESRecomp.exe")
EXE_B=$(cygpath -m "$W/ref-build/ff6_cosim_ref.exe")
A="$EXE_A --no-launcher --rom '$ROM' --config '$(cygpath -m "$INI")'"
B="$EXE_B '$ROM'"
# Second A instance with its own exe directory: two instances in one directory clash on the
# mod state ("mods: plan rejected: cannot write mod state", exit code 1).
A2DIR="$W/a2"; rm -rf "$A2DIR"; mkdir -p "$A2DIR"
cp -r build-cosim/FinalFantasyViSNESRecomp.exe build-cosim/SDL3.dll build-cosim/assets "$A2DIR/"
A2="$(cygpath -m "$A2DIR/FinalFantasyViSNESRecomp.exe") --no-launcher --rom '$ROM' --config '$(cygpath -m "$INI")'"
COORD="python $(cygpath -m "$GR/snesrecomp/tools/snes_cosim.py")"
AENV=(--a-env SNES_COSIM_AUDIO=1)
AAENV=(--a-env SNES_COSIM_AUDIO=1 --b-env SNES_COSIM_AUDIO=1)
INJ=(--max 200 --inject ram:1000:255 --inject-at 20)
# saves/save.srm is relative to the cwd: every run starts with empty SRAM.
RUN="$W/run_$mode"; rm -rf "$RUN"; mkdir -p "$RUN"; cd "$RUN"
export SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
LOG="$LOGS/cosim_$mode.txt"
case $mode in
  gate1)  $COORD --a-cmd "$A" --b-cmd "$A2" "${AAENV[@]}" --stride 1 --max "$MAX" ;;
  gate2)  $COORD --a-cmd "$B" --b-cmd "$B" --stride 1 --max "$MAX" ;;
  gate3a) $COORD --a-cmd "$A" --b-cmd "$A2" "${AAENV[@]}" --stride 1 "${INJ[@]}" ;;
  gate3b) $COORD --a-cmd "$B" --b-cmd "$B" --stride 1 "${INJ[@]}" ;;
  gate4a) $COORD --a-cmd "$A" --b-cmd "$A2" "${AAENV[@]}" --stride 1 --max "$MAX" --audit 25 ;;
  gate4b) $COORD --a-cmd "$B" --b-cmd "$B" --stride 1 --max "$MAX" --audit 25 ;;
  avb)    $COORD --a-cmd "$A" --b-cmd "$B" "${AENV[@]}" --stride 1 --max "$MAX" ;;
  avbram) $COORD --a-cmd "$A" --b-cmd "$B" "${AENV[@]}" --stride 1 --max "$MAX" --compare ram ;;
  *) echo "usage: cosim.sh build [a|b|ab] | gate1|gate2|gate3a|gate3b|gate4a|gate4b|avb|avbram [MAX]"
     exit 2 ;;
esac > "$LOG" 2>&1
rc=$?
# The coordinator leaves its children running when it stops with FATAL; stop only co-sim
# processes (exe paths under build-cosim or work/cosim).
powershell -NoProfile -Command "Get-Process | Where-Object { \$_.Path -match 'build-cosim|work\\\\cosim' } | Stop-Process -Force -Confirm:\$false" 2>/dev/null
echo "$mode rc=$rc log=work/logs/cosim_$mode.txt"
grep -e 'injected' -e 'no divergence' -e 'FIRST DIVERGENCE' -e 'that split' -e 'AUDIT-FAIL' \
  -e 'FATAL' -e 'clk/label' "$LOG" | head -8 | cut -c1-200
exit $rc
