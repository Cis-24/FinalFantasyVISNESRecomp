#!/usr/bin/env bash
# Disassembly-Authority pipeline (PLAN 3.1): export -> ingest -> emit -> audit -> short report.
# Run in MSYS2 MINGW64 with cwd = game repo (GR). Needs the ff6 build: bash ../tools/build_disasm.sh
# Everything generated lands in ../work (never versioned); authority JSON holds ROM bytes.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

WS=$(cd .. && pwd)
ROM=${SNESRECOMP_ROM:-$WS/rom/Final Fantasy III (USA).sfc}
FF6=$WS/ff6
DBG=$FF6/build/en/rom/ff6-en.dbg
IMG=$FF6/build/en/rom/ff6-en.sfc
OUT=$WS/work/authority
OVERLAY=$WS/work/cfg-overlay
EMIT=$WS/work/gen-candidate
AUDIT_GEN=$WS/work/gen-audit
SNES=snesrecomp/tools
PY=${PYTHON:-python}

for f in "$DBG" "$IMG" "$ROM"; do [ -f "$f" ] || { echo "authority.sh: missing $f" >&2; exit 1; }; done
mkdir -p "$OUT" "$WS/work/logs"
# Reused output dirs are refused by the framework; they live under work/ only.
rm -rf "$OVERLAY" "$EMIT" "$AUDIT_GEN" "$OUT/audit.json" "$OUT/ff6-en.authority.json"

echo "== 1/4 export =="
"$PY" -I tools/ff6/export_ca65_authority.py --dbg "$DBG" --source-root "$FF6" --rom "$ROM" --assembled-rom "$IMG" \
  --out-authority "$OUT/ff6-en.authority.json" --out-symbols tools/ff6/symbols_import.toml \
  --out-report "$OUT/export_report.txt" --sites tools/ff6/dispatch_sites.toml \
  --overrides tools/ff6/symbols_overrides.toml --out-merged "$OUT/symbols.merged.toml" || true

echo "== 2/4 ingest =="
"$PY" "$SNES/ingest_disassembly_authority.py" --rom "$ROM" --authority "$OUT/ff6-en.authority.json" \
  --cfg-dir recomp --out-dir "$OVERLAY" > "$WS/work/logs/authority_ingest.log" 2>&1 || { tail -n 20 "$WS/work/logs/authority_ingest.log"; exit 1; }

echo "== 3/4 emit (cfg-roots, entry modes) =="
"$PY" "$SNES/v2_emit.py" --rom "$ROM" --cfg-dir "$OVERLAY" --out-dir "$EMIT" --source-root src \
  --cfg-roots --disassembly-entry-modes > "$WS/work/logs/authority_emit.log" 2>&1 || { tail -n 20 "$WS/work/logs/authority_emit.log"; exit 1; }

echo "== 4/4 audit =="
"$PY" "$SNES/audit_disassembly.py" --rom "$ROM" --authority "$OUT/ff6-en.authority.json" --cfg-dir "$OVERLAY" \
  --source-root src --out-dir "$AUDIT_GEN" --report "$OUT/audit.json" --disassembly-entry-modes \
  > "$WS/work/logs/authority_audit.log" 2>&1 || echo "audit exit $? (findings; see report)"
[ -f "$OUT/audit.json" ] || { tail -n 20 "$WS/work/logs/authority_audit.log"; exit 1; }

"$PY" -I tools/ff6/authority_report.py --export "$OUT/export_report.txt" --audit "$OUT/audit.json" \
  --manifest "$EMIT/program_manifest.json" --baseline src/gen/program_manifest.json | head -n 40
