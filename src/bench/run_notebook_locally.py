"""Run the benchmark notebook's code cells locally with the fake ("mock") model, to test it before Kaggle.

Usage: python3 -I src/bench/run_notebook_locally.py <project_root> <out_dir> [KEY=VALUE ...]
  (set BENCH_NOTEBOOK=benchmark_bangla_prompts.ipynb to test the Bangla-prompt notebook)
  KEY=VALUE overrides a line of the settings cell, e.g. RUN_MODE='"full"' TIME_BUDGET_HOURS=0.0005
"""
import json
import os
import re
import sys
from pathlib import Path

root, out = Path(sys.argv[1]), Path(sys.argv[2])
overrides = dict(a.split("=", 1) for a in sys.argv[3:])
nb = json.loads((root / "notebooks" / os.environ.get("BENCH_NOTEBOOK", "benchmark_one_llm.ipynb")).read_text(encoding="utf-8"))
os.environ.update(BENCH_DATA_DIR=os.environ.get("BENCH_DATA_DIR", str(root / "data/final/benhallueval-qa-v1.3")),
                  BENCH_OUT_DIR=str(out),
                  BENCH_BACKEND_OVERRIDE="mock")
ns = {"__name__": "__main__"}
for n, cell in enumerate(c for c in nb["cells"] if c["cell_type"] == "code"):
    src = "".join(cell["source"])
    for key, value in overrides.items():
        src, k = re.subn(rf"^{key} = .*?(\s+#.*)?$", f"{key} = {value}", src, flags=re.M)
        if n == 0:
            assert k == 1, key
    exec(compile(src, f"<cell {n}>", "exec"), ns)
