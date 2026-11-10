#!/usr/bin/env bash
# Regressions-Suite (PLAN 5.3). cwd = GR, MSYS2 MINGW64 (WS/tools/msys.ps1).
#
#   bash tools/ff6/regress.sh --quick | --full [--no-regen] [--no-build] [--update]
#
# Schritte: Regen -> Build -> je Route: Lauf ohne Gamepad und ohne Echtzeitbremse
# (validation/regress.ini), Tripwire-Suche im Log, Skript-Ereignisse und Dump-Hashes
# gegen validation/expected/<route>.toml (tools/ff6/regress_check.py), Vergleich gegen
# die Referenz-Dumps WS/work/ref/<rNN> (compare_dumps.py, PPU-Writes: compare_ppuw.py; nur wenn
# vorhanden), Miss-Report.
# Ausgabe: PASS/FAIL-Tabelle. Logs: WS/work/logs/regress_*, Dumps: WS/work/regress/<rNN>.
# Exit 0 nur, wenn alles gruen ist (Regel: kein Commit auf main bei roter Schnell-Suite).
#
#   --quick     Schnell-Suite (Routen aus QUICK; r09 folgt mit seiner Phase)
#   --full      alle Routen in validation/routes
#   --no-regen  src/gen nicht neu erzeugen
#   --no-build  nicht bauen
#   --update    Erwartungen neu schreiben (braucht Eintrag in validation/CHANGELOG.md)
set -uo pipefail

GR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WS="$(cd "$GR/.." && pwd)"
cd "$GR"

QUICK=(r01_boot_title r03_field_walk r04_menu_tour r05_first_battle)
SUITE=""; REGEN=1; BUILD=1; UPDATE=()
while [ $# -gt 0 ]; do
  case "$1" in
    --quick) SUITE=quick ;;
    --full) SUITE=full ;;
    --no-regen) REGEN=0 ;;
    --no-build) BUILD=0 ;;
    --update) UPDATE=(--update) ;;
    -h|--help) sed -n '2,/^set -uo/p' "$0" | sed -n 's/^# \{0,1\}//p'; exit 0 ;;
    *) echo "regress.sh: unbekannter Schalter: $1" >&2; exit 2 ;;
  esac
  shift
done
[ -n "$SUITE" ] || { echo "regress.sh: --quick oder --full angeben" >&2; exit 2; }
if [ "$SUITE" = quick ]; then
  ROUTES=("${QUICK[@]}")
else
  ROUTES=(); for f in validation/routes/*.txt; do ROUTES+=("$(basename "$f" .txt)"); done
fi

export SNESRECOMP_ROM="${SNESRECOMP_ROM:-$WS/rom/Final Fantasy III (USA).sfc}"
EXE=build/FinalFantasyViSNESRecomp.exe
CFG="$GR/validation/regress.ini"
LOGS="$WS/work/logs"; RUNS="$WS/work/regress"
mkdir -p "$LOGS" "$RUNS"
FAIL=0
row() { printf '%-16s %-16s %-5s %s\n' "$1" "$2" "$3" "$4"; [ "$3" = FAIL ] && FAIL=1; return 0; }
gen_hash() { find src/gen -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -c1-16; }

T0=$SECONDS
if [ $REGEN = 1 ]; then
  if bash tools/regen.sh --rom "$SNESRECOMP_ROM" > "$LOGS/regress_regen.log" 2>&1; then
    row suite Regen PASS "src/gen $(gen_hash), $((SECONDS - T0)) s"
  else
    row suite Regen FAIL "Log work/logs/regress_regen.log"
  fi
fi
if [ $BUILD = 1 ] && [ $FAIL = 0 ]; then
  T1=$SECONDS
  if cmake --build build > "$LOGS/regress_build.log" 2>&1; then
    row suite Build PASS "$((SECONDS - T1)) s"
  else
    row suite Build FAIL "Log work/logs/regress_build.log"
  fi
fi
[ $FAIL = 0 ] && [ ! -x "$EXE" ] && row suite Build FAIL "$EXE fehlt"
PRE=$FAIL

for r in "${ROUTES[@]}"; do
  [ $PRE = 0 ] || break
  short=${r%%_*}; R="$RUNS/$short"; LOG="$LOGS/regress_$r.log"; MISS="$LOGS/regress_${r}_miss.txt"
  rm -rf "$R"; mkdir -p "$R"
  T1=$SECONDS
  # cwd = Laufverzeichnis: saves/save.srm liegt relativ zur cwd. Jede Route startet so mit
  # leerem SRAM; ein neues Spiel schreibt dort hinein und wuerde sonst die naechste Route aendern.
  ( cd "$R" && SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy SNESRECOMP_DUMP_DIR="$R" \
    SNESRECOMP_COVERAGE_DIR="$R" SNESRECOMP_TIER2_CAPTURE=1 \
    timeout 600 "$GR/$EXE" --no-launcher --rom "$SNESRECOMP_ROM" --config "$CFG" \
      --script "$GR/validation/routes/$r.txt" ) > "$LOG" 2>&1
  rc=$?
  quit=$(grep -o 'exit: script quit after [0-9]* frames' "$LOG" | head -1)
  if [ $rc = 0 ] && [ -n "$quit" ]; then
    row "$r" Lauf PASS "${quit#exit: }, $((SECONDS - T1)) s"
  else
    row "$r" Lauf FAIL "rc=$rc, Log work/logs/regress_$r.log"; continue
  fi
  # dispatch-oob: a dispatch value missing from a generated switch (always on since
  # snesrecomp patch 0015); unresolved-abandon: an unresolved transfer whose handler
  # was skipped. Both print one line per site on its first hit.
  trip=$(grep -ciE 'tripwire|stack_drift|offrails|off-rails|\[dispatch-oob\]|\[unresolved-abandon\]' "$LOG")
  [ "$trip" = 0 ] && row "$r" Tripwires PASS "0 Meldungen" || row "$r" Tripwires FAIL "$trip Meldungen im Log"

  cp "$R"/finalfantasyvi/*.json* "$R"/ 2>/dev/null
  python tools/ff6/miss_report.py "$R" --top 10 --log "$LOG" > "$MISS" 2>&1
  mrc=$?
  [ $mrc = 0 ] && row "$r" Miss-Report PASS "$(grep -o 'ROM-Misses [0-9]*' "$MISS")" \
               || row "$r" Miss-Report FAIL "rc=$mrc, work/logs/regress_${r}_miss.txt"

  python tools/ff6/regress_check.py "$r" "$R" "$LOG" "$MISS" "${UPDATE[@]}" > "$LOGS/regress_${r}_check.txt"
  crc=$?
  cat "$LOGS/regress_${r}_check.txt"; [ $crc = 0 ] || FAIL=1

  REF="$WS/work/ref/$short"
  if [ -d "$REF" ]; then
    for w in "$R"/*.wram.bin; do
      tag=$(basename "$w" .wram.bin)
      [ -f "$REF/$tag.wram.bin" ] || { row "$r" "Referenz $tag" SKIP "keine Referenz-Dumps"; continue; }
      out="$LOGS/regress_${r}_ref_$tag.txt"
      if python tools/ff6/compare_dumps.py "$REF" "$R" "$tag" > "$out" 2>&1; then
        row "$r" "Referenz $tag" PASS "$(grep -E '^(wram|vram|cgram|oam|fb):' "$out" | cut -d' ' -f1-2 | tr '\n' ' ')"
      else
        row "$r" "Referenz $tag" FAIL "work/logs/regress_${r}_ref_$tag.txt"
      fi
      [ -f "$REF/$tag.ppuw.tsv" ] || continue
      out="$LOGS/regress_${r}_ppuw_$tag.txt"
      if python tools/ff6/compare_ppuw.py "$REF" "$R" "$tag" > "$out" 2>&1; then
        row "$r" "PPU-Writes $tag" PASS "$(grep -cE 'INFO' "$out") INFO, work/logs/regress_${r}_ppuw_$tag.txt"
      else
        row "$r" "PPU-Writes $tag" FAIL "work/logs/regress_${r}_ppuw_$tag.txt"
      fi
    done
  else
    row "$r" Referenz SKIP "work/ref/$short fehlt"
  fi
done

[ $FAIL = 0 ] && row suite "$SUITE" PASS "$((SECONDS - T0)) s" || row suite "$SUITE" FAIL "$((SECONDS - T0)) s"
exit $FAIL
