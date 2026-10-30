#!/bin/bash
# Local test of the two GenreHalluEval notebooks and the scoring script, with the fake ("mock") model. No GPU needed.
# Uses the real package (data/final/GenreHalluEval-v1.1); the fake model's verdicts mean nothing.
# Usage: bash src/dataset2/test_notebooks.sh <project_root> <empty_test_dir>
set -u
ROOT=$1; T=$2
rm -rf "$T"
python3 -I "$ROOT/src/dataset2/make_notebooks.py" "$ROOT" > /dev/null
export BENCH_DATA_DIR="$ROOT/data/final/GenreHalluEval-v1.1"
R() { BENCH_NOTEBOOK=$1 python3 -I "$ROOT/src/bench/run_notebook_locally.py" "$ROOT" "${@:2}" 2>&1 | grep -v "calls/s"; }
SHOW="^\[|^route|^LLMs asked|Done|PARTIAL|TIME BUDGET|Traceback|Error|Stop"
echo "=== 1 routed pilot"; R genrehallueval_routed.ipynb "$T/routed" RUN_MODE='"pilot"' | grep -E "$SHOW"
echo "=== 2 routed full, tiny time budget: must stop cleanly"; R genrehallueval_routed.ipynb "$T/stop" TIME_BUDGET_HOURS=0.0000001 | grep -E "TIME BUDGET|PARTIAL"
echo "=== 3 routed full, resumed from the pilot's output added as a nested input"
I="$T/input/datasets/me/routed-v1"; mkdir -p "$I" && cp -r "$T/routed/runs" "$I/runs"
BENCH_INPUT_DIR="$T/input" R genrehallueval_routed.ipynb "$T/routed_full" | grep -E "already done|Done|PARTIAL|Traceback" | sort | uniq -c
echo "=== 4 single best full"; R genrehallueval_single_best.ipynb "$T/single" | grep -E "$SHOW"
echo "=== 5 compare (PREVIEW, design labels)"
python3 -I "$ROOT/src/dataset2/compare_routes.py" "$ROOT" --routed "$T/routed_full/genrehallueval__routed__full__outputs.zip" \
  --single "$T/single/genrehallueval__single_best__full__outputs.zip" --out "$T/compare" \
  | grep -E "^\| R vs A|^\| (D|E|F) vs A, all|Determinism|saved|Traceback|Error"
