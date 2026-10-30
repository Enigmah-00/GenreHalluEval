#!/bin/bash
# Local test of GenreHalluEval v2 with the fake ("mock") model, end to end: package, learn notebook (three sessions),
# lock, both test notebooks, scoring. No GPU needed; the fake model's verdicts mean nothing.
# Everything is written under <empty_test_dir>; the real package, labels, lock and zip are not touched.
# Usage: bash src/genrehallueval_v2/test_v2.sh <project_root> <empty_test_dir>
set -u
ROOT=$1; T=$2
rm -rf "$T"; mkdir -p "$T"
python3 -I "$ROOT/src/genrehallueval_v2/build_v2.py" "$ROOT" 2.0 --out "$T/pkg" | tail -3
python3 -I "$ROOT/src/genrehallueval_v2/make_v2_notebooks.py" "$ROOT" | tail -1
export BENCH_DATA_DIR="$T/pkg"
R() { BENCH_NOTEBOOK=$1 python3 -I "$ROOT/src/bench/run_notebook_locally.py" "$ROOT" "${@:2}" 2>&1 | grep -v "calls/s"; }
echo "=== 1 learn pilot"; R ghe2_learn.ipynb "$T/learn_pilot" RUN_MODE='"pilot"' | grep -E "Golden|^models in|^learn:|Done|PARTIAL|Traceback|Error"
echo "=== 2 learn: tiny time budget, must stop cleanly"; R ghe2_learn.ipynb "$T/stop" TIME_BUDGET_HOURS=0.0000001 | grep -E "TIME BUDGET|PARTIAL"
echo "=== 3 learn full, three sessions"
R ghe2_learn.ipynb "$T/learnA" 'MODELS_THIS_RUN=["deepseek-r1-14b"]' | grep -E "^models in|Done|PARTIAL|Traceback|Error"
R ghe2_learn.ipynb "$T/learnB" 'MODELS_THIS_RUN=["gemma4-31b", "tigerllm-9b"]' | grep -E "^models in|Done|PARTIAL|Traceback|Error"
R ghe2_learn.ipynb "$T/learnC" 'MODELS_THIS_RUN=["qwen3.5-27b", "gpt-oss-20b"]' | grep -E "^models in|Done|PARTIAL|Traceback|Error|^\| "
echo "=== 4 lock from the three learn zips"
python3 -I "$ROOT/src/genrehallueval_v2/make_lock_v2.py" "$ROOT" "$T"/learnA/*.zip "$T"/learnB/*.zip "$T"/learnC/*.zip \
  --package "$T/pkg" --lock-dir "$T/lock" --zip "$T/GenreHalluEval-v2.zip" --labels "$T/labels.csv" \
  | grep -E "^- A|^- Pool|^- Cells|^lock|Own-genre|Traceback|Error"
echo "=== 4b a second lock must be refused"
python3 -I "$ROOT/src/genrehallueval_v2/make_lock_v2.py" "$ROOT" "$T"/learnA/*.zip --package "$T/pkg" \
  --lock-dir "$T/lock" --zip "$T/x.zip" --labels "$T/labels.csv" 2>&1 | tail -1
echo "=== 4c test plan into the test package"
python3 -I "$ROOT/src/genrehallueval_v2/add_test_plan.py" "$ROOT" --package "$T/pkg" --zip "$T/GenreHalluEval-v2.zip" \
  --labels "$T/labels.csv" | head -1
python3 -I "$ROOT/src/genrehallueval_v2/make_v2_notebooks.py" "$ROOT" | tail -1
for k in route_E route_F route_R; do
  echo "=== 5 $k"; R ghe2_$k.ipynb "$T/$k" | grep -E "^route|^LLMs asked|^A:|Done|PARTIAL|Traceback|Error|Stop"
done
echo "=== 6 single best"; R ghe2_single_best.ipynb "$T/single" | grep -E "^route|Done|PARTIAL|Traceback|Error|Stop"
echo "=== 7 compare (labels file of the test package)"
python3 -I "$ROOT/src/genrehallueval_v2/compare_v2.py" "$ROOT" --E "$T"/route_E/ghe2_test__route_E__full__all__outputs.zip \
  --F "$T"/route_F/ghe2_test__route_F__full__all__outputs.zip --R "$T"/route_R/ghe2_test__route_R__full__all__outputs.zip \
  --A "$T"/single/ghe2_test__single_best__full__all__outputs.zip --package "$T/pkg" --labels "$T/labels.csv" \
  --out "$T/compare" | grep -E "^## Main|^\| [EFR] vs A \| (no_)?context|^\| (no_)?context \| [AEFR] \||Routes recomputed|no verdict|Determinism|^- route|saved|Traceback|Error"
