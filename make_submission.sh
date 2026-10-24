#!/usr/bin/env bash
# Package runs + code + docs as team-01_submission.zip and run the official checker.   usage: ./make_submission.sh [runs_dir]
set -euo pipefail
cd "$(dirname "$0")"
RUNS="${1:-runs}"
STAGE=submission/team-01_submission
rm -rf submission && mkdir -p "$STAGE/code" "$STAGE/runs"
cp CLIENT_MEMO.md TEAM_DOC.md "$STAGE/"
cp -R code config data run_all.sh make_submission.sh "$STAGE/code/"
find "$STAGE/code" -name __pycache__ -prune -exec rm -rf {} +
for r in plan_1 plan_2 nodecision_1 nodecision_2 plan_nosurprises; do cp -R "$RUNS/$r" "$STAGE/runs/"; done
(cd submission && zip -qr team-01_submission.zip team-01_submission)
python3 -I yeni-case-5-sirket/check.py submission/team-01_submission.zip
