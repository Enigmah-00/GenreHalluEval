#!/bin/bash
# Local test of the GenreHalluEval split experiment with the fake ("mock") model, end to end: package, learn notebook
# (two sessions), lock, both test notebooks, scoring. No GPU needed; the fake model's verdicts mean nothing.
# Everything is written under <empty_test_dir>; the real package, lock and zip are not touched.
# Usage: bash src/split/test_split.sh <project_root> <empty_test_dir>
set -u
ROOT=$1; T=$2
rm -rf "$T"; mkdir -p "$T"
python3 -I "$ROOT/src/split/build_split.py" "$ROOT" --out "$T/pkg" | tail -2
python3 -I "$ROOT/src/split/make_split_notebooks.py" "$ROOT"
export BENCH_DATA_DIR="$T/pkg"
R() { BENCH_NOTEBOOK=$1 python3 -I "$ROOT/src/bench/run_notebook_locally.py" "$ROOT" "${@:2}" 2>&1 | grep -v "calls/s"; }
SHOW="^\[|^route|^LLMs asked|^pool|^models in|Golden|Done|PARTIAL|TIME BUDGET|Traceback|Error|Stop|no_answer \||^\| "
echo "=== 1 learn pilot"; R split_learn.ipynb "$T/learn_pilot" RUN_MODE='"pilot"' | grep -E "Golden|^models in|Done|PARTIAL|Traceback|Error"
echo "=== 2 learn: tiny time budget, must stop cleanly"; R split_learn.ipynb "$T/stop" TIME_BUDGET_HOURS=0.0000001 | grep -E "TIME BUDGET|PARTIAL"
echo "=== 3 learn full, two sessions"
R split_learn.ipynb "$T/learnA" 'MODELS_THIS_RUN=["deepseek-r1-14b"]' | grep -E "^models in|Done|PARTIAL|Traceback|Error"
R split_learn.ipynb "$T/learnB" 'MODELS_THIS_RUN=["gemma4-31b", "qwen3.5-27b", "gpt-oss-20b", "tigerllm-9b"]' | grep -E "$SHOW"
echo "=== 4 lock from both learn zips"
python3 -I "$ROOT/src/split/make_split_lock.py" "$ROOT" "$T"/learnA/*.zip "$T"/learnB/*.zip --package "$T/pkg" \
  --lock-dir "$T/lock" --zip "$T/GenreHalluEval-split.zip" | grep -E "^- A|^- Pool|^lock|Traceback|Error"
echo "=== 4b a second lock must be refused"
python3 -I "$ROOT/src/split/make_split_lock.py" "$ROOT" "$T"/learnA/*.zip "$T"/learnB/*.zip --package "$T/pkg" \
  --lock-dir "$T/lock" --zip "$T/x.zip" 2>&1 | tail -1
echo "=== 5 routed test"; R split_routed.ipynb "$T/routed" | grep -E "^route|^LLMs asked|Done|PARTIAL|Traceback|Error|Stop"
echo "=== 6 single best test"; R split_single_best.ipynb "$T/single" | grep -E "^route|Done|PARTIAL|Traceback|Error|Stop"
echo "=== 7 compare (PREVIEW, design labels)"
python3 -I "$ROOT/src/dataset2/compare_routes.py" "$ROOT" --routed "$T"/routed/ghesplit_test__routed__full__all__outputs.zip \
  --single "$T"/single/ghesplit_test__single_best__full__all__outputs.zip --package "$T/pkg" --items test_items.csv \
  --dataset ghesplit_test --out "$T/compare" | grep -E "^\| R vs A|^\| (no_)?context \| A|Determinism|saved|Traceback|Error"
