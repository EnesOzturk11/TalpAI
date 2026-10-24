#!/usr/bin/env bash
# Run the five hand-in runs in parallel.   usage: ./run_all.sh [out_dir] [extra sim.py args...]
set -euo pipefail
cd "$(dirname "$0")"
OUT="${1:-runs}"; shift || true
export SSL_CERT_FILE="${SSL_CERT_FILE:-/etc/ssl/cert.pem}"
PY=.venv/bin/python
mkdir -p "$OUT/logs"
run() { "$PY" -I code/sim.py --name "$1" --type "$2" --seed "$3" --out "$OUT" "${@:4}" > "$OUT/logs/$1.log" 2>&1 || { echo "FAILED: $1 (see $OUT/logs/$1.log)"; return 1; }; }
run plan_1 plan 1 "$@" &
run plan_2 plan 2 "$@" &
run nodecision_1 nodecision 1 "$@" &
run nodecision_2 nodecision 2 "$@" &
run plan_nosurprises plan_nosurprises "${NOSURP_SEED:-1}" "$@" &
wait
tail -qn1 "$OUT"/logs/*.log
"$PY" -I code/compare.py "$OUT"
