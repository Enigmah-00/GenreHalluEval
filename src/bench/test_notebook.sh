#!/bin/bash
# Local test of notebooks/benchmark_one_llm.ipynb with the fake ("mock") model. No GPU needed.
# Usage: bash src/bench/test_notebook.sh <project_root> <empty_test_dir>
set -u
ROOT=$1; T=$2
rm -rf "$T"
R() { python3 -I "$ROOT/src/bench/run_notebook_locally.py" "$ROOT" "$T" "$@" 2>&1; }
SHOW="^\[|Done|PARTIAL|Error|Stop|Traceback"
echo "=== 1 pilot, context only"; R JUDGE_CONDITIONS='["context"]' | grep -E "$SHOW" | grep -v "calls/s"
echo "=== 2 pilot, both conditions: genre and context reused, only no_context is new"
R | grep -E "$SHOW" | grep -v "calls/s"
echo "=== 3 full, tiny time budget: must stop cleanly"
R RUN_MODE='"full"' TIME_BUDGET_HOURS=0.0000001 | grep -E "already done|TIME BUDGET|PARTIAL"
echo "=== 4 full, resume: reuses the pilot's calls"; R RUN_MODE='"full"' | grep -E "already done|Done|PARTIAL|MAIN"
echo "=== 5 run again: nothing to do"; R RUN_MODE='"full"' | grep -E "already done|Done"
echo "=== 6 saved files"; ls "$T"/runs; ls "$T"/results/llama3.1-8b/full
echo "=== 7 setup conflict: must stop"
python3 -I -c "
import json,sys
p=sys.argv[1]; L=open(p,encoding='utf-8').read().splitlines(); r=json.loads(L[0]); r['setup_hash']='deadbeefdeadbeef'; L[0]=json.dumps(r,ensure_ascii=False)
open(p,'w',encoding='utf-8').write('\n'.join(L)+'\n')" "$T"/runs/benhallueval__llama3.1-8b__judge__judge_noctx_v1.jsonl
R RUN_MODE='"full"' | tail -1
echo "=== 8 resume from a dataset input (runs nested 4 folders deep), fresh output folder"
I="$T/fake_input/datasets/someone/deepseek-partial/llama3.1-8b__full__outputs"
mkdir -p "$I" && cp -r "$T/runs" "$I/runs"
python3 -I -c "
import json,sys
p=sys.argv[1]; L=open(p,encoding='utf-8').read().splitlines(); r=json.loads(L[0]); r['setup_hash']='6d1da993e5b9bf79'; L[0]=json.dumps(r,ensure_ascii=False)
open(p,'w',encoding='utf-8').write('\\n'.join(L)+'\\n')" "$I/runs/benhallueval__llama3.1-8b__judge__judge_noctx_v1.jsonl"
BENCH_INPUT_DIR="$T/fake_input" python3 -I "$ROOT/src/bench/run_notebook_locally.py" "$ROOT" "$T/fresh" RUN_MODE='"full"' 2>&1 | grep -E "resumed|already done|Done|Stop"
