#!/usr/bin/env bash
# FF6 differential co-simulation (PLAN 5.2, snesrecomp docs/COSIM.md). DEV/DIAGNOSTICS ONLY.
# cwd = GR, MSYS2 MINGW64 (WS/tools/msys.ps1). Changes nothing in the snesrecomp submodule.
#
#   bash tools/ff6/cosim/cosim.sh build [a|b|ab]
#   bash tools/ff6/cosim/cosim.sh gate1|gate2|gate3a|gate3b|gate4a|gate4b [MAX]
#   bash tools/ff6/cosim/cosim.sh avb|avbram [MAX]
#   bash tools/ff6/cosim/cosim.sh route <route.txt> [MAX]
#
# A = the game exe built with SNES_COSIM=ON in build-cosim/ (beam frame driver, headless via the
#     SDL dummy drivers, EnableAudio = 0, deterministic audio consumer SNES_COSIM_AUDIO=1).
# B = snesrecomp/cosim/ref_driver.c (interp816 over the runner devices) with
#     tools/ff6/cosim/ref_driver_ff6.patch (frame cut at V=225, bus-weighted master clocks,
#     refresh, DMA time; see CMakeLists.txt), built into WS/work/cosim/ref-build.
#     Standalone: ref-build/ff6_cosim_ref.exe <rom> --frames N [--no-render], WRAM at the last
#     frame cut to the file in FF6_REF_WRAM_OUT.
# Gates: 1 = A vs A, 2 = B vs B, 3a/3b = one WRAM byte flipped after cp 20 (must halt at cp 21
# with only 'ram' split), 4a/4b = hash-vs-byte audit every 25 checkpoints. avb compares the full
# state, avbram only the 128 KiB WRAM. Logs: WS/work/logs/cosim_<mode>.txt, stride 1 frame.
# For avb/avbram: COSIM_A_ENV="K=V ..." adds A-side environment, COSIM_B_ENV="K=V ..." B-side
# environment (the diagnostic modes of ref_driver_ff6.patch), COSIM_ARGS="..." adds coordinator
# options (e.g. "--compare cpu,ram --transient-grace 30").
# route: A-vs-B with the input of a route script. A plays the script; B replays A's joypad 1
# mask per frame. Pass 1 runs the script on A against A2 (gate 1 over the route) and logs A's
# mask whenever it changes (FF6_COSIM_INPUT_LOG, src/game_rtl.c) to WS/work/cosim/input_<r>.txt;
# pass 2 runs the script on A again against B, which replays that file (FF6_REF_INPUT_FILE),
# and compares WRAM with route_cmp.py: differences in the dead stack (at or below S) count as
# equal, live ones as transient up to GRACE checkpoints (default 120). The script copy
# (WS/work/cosim/route_<r>.txt) drops poke and dump lines: the pokes only align a route with
# snes9x and B cannot replay them, and A and A2 would write their dumps into one directory.
# MAX defaults to the frame of the script's quit in pass 1 minus 2 (A exits at quit).
# COSIM_A_ENV and COSIM_B_ENV apply to pass 2, ROUTE_CMP_ARGS="..." adds route_cmp.py options
# (e.g. "--watch 0x131E,0x47 --watch-range 3640-3700"), ROUTE_REUSE_INPUT=1 skips pass 1 when
# its input log and log file exist. Logs: cosim_route1_<r>.txt and cosim_route_<r>.txt in
# WS/work/logs.
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

if [ "$mode" = route ]; then
  # The route path is relative to GR (the cwd here) or absolute.
  RT=${2:-}; MAX=${3:-}
  [ -f "$RT" ] || { echo "usage: cosim.sh route <route.txt> [MAX]"; exit 2; }
  RT=$(realpath "$RT")
else
  MAX=${2:-4000}
fi
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
# Extra A-side environment for avb/avbram, e.g. COSIM_A_ENV="SNES_COSIM_ACCURATE_APU=1".
for kv in ${COSIM_A_ENV:-}; do AENV+=(--a-env "$kv"); done
BENV=()
for kv in ${COSIM_B_ENV:-}; do BENV+=(--b-env "$kv"); done
AAENV=(--a-env SNES_COSIM_AUDIO=1 --b-env SNES_COSIM_AUDIO=1)
INJ=(--max 200 --inject ram:1000:255 --inject-at 20)
# saves/save.srm is relative to the cwd: every run starts with empty SRAM.
RUN="$W/run_$mode"; rm -rf "$RUN"; mkdir -p "$RUN"; cd "$RUN"
export SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
LOG="$LOGS/cosim_$mode.txt"
# The coordinator leaves its children running when it stops with FATAL; stop only co-sim
# processes (exe paths under build-cosim or work/cosim).
stop_cosim() {
  powershell -NoProfile -Command "Get-Process | Where-Object { \$_.Path -match 'build-cosim|work\\\\cosim' } | Stop-Process -Force -Confirm:\$false" 2>/dev/null
}
summary() {
  grep -a -e 'injected' -e 'no divergence' -e 'no UNMASKED' -e 'FIRST DIVERGENCE' -e 'that split' \
    -e 'AUDIT-FAIL' -e 'FATAL' -e 'clk/label' -e 'halted at' "$1" | head -8 | cut -c1-200
}

if [ "$mode" = route ]; then
  r=$(basename "$RT" .txt)
  RC="$W/route_$r.txt"; IN="$W/input_$r.txt"
  LOG1="$LOGS/cosim_route1_$r.txt"; LOG="$LOGS/cosim_route_$r.txt"
  grep -v -E '^[[:space:]]*(poke|pokefor|dump)([[:space:]]|$)' "$RT" > "$RC"
  SCR="--script '$(cygpath -m "$RC")'"
  if [ "${ROUTE_REUSE_INPUT:-0}" = 1 ] && [ -s "$IN" ] && [ -s "$LOG1" ]; then
    echo "pass 1 reused (ROUTE_REUSE_INPUT=1)"
  else
    rm -f "$IN"
    # Pass 1: A and A2 play the script, A logs its input. A exits at the script's quit (or
    # an until timeout), which ends the coordinator with FATAL; a divergence before that
    # means the scripted run is not deterministic.
    $COORD --a-cmd "$A $SCR" --b-cmd "$A2 $SCR" "${AAENV[@]}" \
      --a-env "FF6_COSIM_INPUT_LOG=$(cygpath -m "$IN")" --stride 1 --max 1000000 > "$LOG1" 2>&1
    stop_cosim
  fi
  END=$(grep -m1 -E -o 'script f=[0-9]+ (quit|until [0-9A-F]+ timed out)' "$LOG1")
  QF=$(echo "$END" | grep -o -E 'f=[0-9]+' | cut -c3-)
  echo "pass 1 (A vs A2): ${END:-no script end} | $(grep -c . "$IN" 2>/dev/null) input changes" \
       "| log=work/logs/cosim_route1_$r.txt"
  summary "$LOG1" | grep -v FATAL
  if grep -q 'FIRST DIVERGENCE' "$LOG1" || [ -z "$QF" ] || [ ! -s "$IN" ]; then
    echo "route $r: pass 1 FAIL"; exit 1
  fi
  MAX=${MAX:-$((QF - 2))}
  # Pass 2: A plays the script, B replays A's input; WRAM with the dead-stack rule of
  # route_cmp.py, live differences up to GRACE checkpoints count as transient.
  cd "$W"; rm -rf "$RUN"; mkdir -p "$RUN"; cd "$RUN"
  python "$(cygpath -m "$GR/tools/ff6/cosim/route_cmp.py")" \
    "$(cygpath -m "$GR/snesrecomp/tools")" --a-cmd "$A $SCR" --b-cmd "$B" "${AENV[@]}" \
    --b-env "FF6_REF_INPUT_FILE=$(cygpath -m "$IN")" "${BENV[@]}" --max "$MAX" \
    --grace "${GRACE:-120}" ${ROUTE_CMP_ARGS:-} > "$LOG" 2>&1
  rc=$?
  stop_cosim
  echo "route $r (A vs B, $MAX checkpoints) rc=$rc log=work/logs/cosim_route_$r.txt"
  grep -e 'LIVE' -e 'TRANSIENT' -e 'dead stack at' "$LOG" | head -12 | cut -c1-200
  grep -e '^  live:' -e 'cpu:' -e 'halted at' -e 'no live divergence' -e 'live divergence open' \
    -e 'FATAL' "$LOG" | cut -c1-240
  exit $rc
fi

case $mode in
  gate1)  $COORD --a-cmd "$A" --b-cmd "$A2" "${AAENV[@]}" --stride 1 --max "$MAX" ;;
  gate2)  $COORD --a-cmd "$B" --b-cmd "$B" --stride 1 --max "$MAX" ;;
  gate3a) $COORD --a-cmd "$A" --b-cmd "$A2" "${AAENV[@]}" --stride 1 "${INJ[@]}" ;;
  gate3b) $COORD --a-cmd "$B" --b-cmd "$B" --stride 1 "${INJ[@]}" ;;
  gate4a) $COORD --a-cmd "$A" --b-cmd "$A2" "${AAENV[@]}" --stride 1 --max "$MAX" --audit 25 ;;
  gate4b) $COORD --a-cmd "$B" --b-cmd "$B" --stride 1 --max "$MAX" --audit 25 ;;
  avb)    $COORD --a-cmd "$A" --b-cmd "$B" "${AENV[@]}" "${BENV[@]}" --stride 1 --max "$MAX" ${COSIM_ARGS:-} ;;
  avbram) $COORD --a-cmd "$A" --b-cmd "$B" "${AENV[@]}" "${BENV[@]}" --stride 1 --max "$MAX" --compare ram ${COSIM_ARGS:-} ;;
  *) echo "usage: cosim.sh build [a|b|ab] | gate1|gate2|gate3a|gate3b|gate4a|gate4b|avb|avbram [MAX]" \
          "| route <route.txt> [MAX]"
     exit 2 ;;
esac > "$LOG" 2>&1
rc=$?
stop_cosim
echo "$mode rc=$rc log=work/logs/cosim_$mode.txt"
summary "$LOG"
exit $rc
