"""Import one model's Kaggle outputs zip (<model>__<mode>__outputs.zip) into the project, check it, and rebuild the
Kaggle results package.

Usage: python3 -I src/bench/import_run.py <project_root> <outputs.zip>

- Copies runs/*.jsonl to runs/ and results/<model>/<mode>/* to results/<model>/<mode>/. A file that already exists
  is only replaced if the new one contains every line of the old one (a resumed run log grows; it never changes).
- Keeps the original zip (it holds the Ollama server log) in runs/kaggle_outputs/.
- Checks: the dataset checksums match the package; the run is not partial; every call has status ok; one setup per
  log; no prompt longer than the context window; the Ollama log says "truncated = 0" for every request.
- Warns (does not fail) if the Ollama version differs from the pinned OLLAMA_VERSION or from earlier models.
- Rebuilds results/overview.md (all models side by side, src/bench/overview.py) and release/kaggle-runs/ (all models'
  runs and results, without server logs) for the private Kaggle dataset "BenHalluEval-QA judge runs".
- Prints the facts for docs/runlog.md.
"""
import collections
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

root, src = Path(sys.argv[1]), Path(sys.argv[2])
PACKAGE = root / "data/final/benhallueval-qa-v1.3"
problems, warnings = [], []

z = zipfile.ZipFile(src)
names = z.namelist()
for n in names:
    if n.startswith("/") or ".." in Path(n).parts:
        sys.exit(f"unsafe path in zip: {n}")
manifest_name = next(n for n in names if n.endswith("/manifest.json"))
manifest = json.loads(z.read(manifest_name))
model, mode = manifest["model_key"], manifest["run_mode"]

# ---------- checks ----------
package_sums = dict(reversed(l.split("  ", 1)) for l in (PACKAGE / "checksums.sha256").read_text().splitlines() if l)
# the data files and the prompt files this run actually used (English or Bangla prompts)
CHECKED = ["items.csv", "genre_blind200.csv"] + [f"prompts/{pid}.txt" for pid in manifest["prompt_ids"].values()]
for f in sorted(set(CHECKED)):
    if manifest["dataset_checksums"].get(f) != package_sums.get(f):
        problems.append(f"{f}: the run used a different file than the package")
if manifest["partial"]:
    problems.append("the run is PARTIAL: resume it before importing")
for stage, counts in manifest["status_counts"].items():
    bad = {k: v for k, v in counts.items() if k not in ("ok", "capped", "too_long")}
    if bad:
        problems.append(f"{stage}: statuses {counts}")
    if counts.get("capped"):                    # reasoning models: thinking hit the output cap -> no_answer (rule)
        warnings.append(f"{stage}: {counts['capped']} replies capped (thinking hit the output limit; counted as no_answer)")
    if counts.get("too_long"):                  # prompt longer than the model's context: skipped, never cut (rule)
        warnings.append(f"{stage}: {counts['too_long']} prompts too long for the model's context (skipped, never cut; "
                        "counted as no_answer)")

stats = {}
for n in names:
    if n.startswith("runs/") and n.endswith(".jsonl"):
        recs = [json.loads(l) for l in z.read(n).decode("utf-8").splitlines() if l.strip()]
        setups = {r["setup_hash"] for r in recs}
        if len(setups) != 1:
            problems.append(f"{n}: {len(setups)} setups mixed")
        too_long = sum((r["prompt_tokens"] or 0) >= r["num_ctx"] for r in recs if r["status"] != "too_long")
        if too_long:
            problems.append(f"{n}: {too_long} prompts reach the context window")
        ts = sorted(r["timestamp"] for r in recs)
        stats[Path(n).name] = dict(
            calls=len(recs), unique=len({r["key"] for r in recs}),
            run_mode=dict(collections.Counter(r["run_mode"] for r in recs)),
            no_answer=sum(r["parsed"] == "no_answer" for r in recs),
            prompt_tokens=sum(r["prompt_tokens"] or 0 for r in recs), max_prompt=max(r["prompt_tokens"] or 0 for r in recs),
            output_tokens=sum(r["output_tokens"] or 0 for r in recs), first=ts[0][:16], last=ts[-1][:16],
            replies=dict(collections.Counter(r["parsed"] for r in recs).most_common()))

trunc = collections.Counter()
for n in names:
    if n.endswith(".log"):
        with z.open(n) as f:
            for line in f:
                m = re.search(rb"truncated = (\d+)", line)
                if m:
                    trunc[int(m.group(1)) > 0] += 1
if trunc[True]:
    problems.append(f"the Ollama log reports {trunc[True]} truncated prompts")

# ---------- same software for every model (golden rule 6) ----------
def ollama_version(version_id):
    m = re.match(r"ollama (\S+);", version_id or "")
    return m.group(1).rstrip(";") if m else None


pinned = re.search(r'^OLLAMA_VERSION = "([^"]*)"', (root / "src/bench/make_notebook.py").read_text(), re.M).group(1)
this = ollama_version(manifest["model_version"])
others = {}
for mf in (root / "results").glob("*/*/manifest.json"):
    if mf.parent.parent.name != model:
        others[mf.parent.parent.name] = ollama_version(json.loads(mf.read_text())["model_version"])
if this and pinned and this != pinned:
    warnings.append(f"Ollama {this} was used, but the notebook pins {pinned} (OLLAMA_VERSION was not set on Kaggle?)")
diff_models = {k: v for k, v in others.items() if v and this and v != this}
if diff_models:
    warnings.append(f"Ollama {this} differs from earlier models: {diff_models}")

if manifest["partial"]:                         # never mix half-finished numbers into results/ or the overview
    print(f"NOT IMPORTED: {model} ({mode}) is PARTIAL. Resume it on Kaggle (add this version's output as input, "
          "same settings), then import the finished zip.")
    for k, v in stats.items():
        print(k, json.dumps(v))
    sys.exit(1)

# ---------- copy (never change an existing file; a run log may only grow) ----------
copied = []
for n in names:
    if not (n.startswith("runs/") or n.startswith("results/")) or n.endswith("/"):
        continue
    dst, data = root / n, z.read(n)
    if dst.exists():
        old = dst.read_bytes()
        if old == data:
            continue
        if n.startswith("runs/") and set(old.decode().splitlines()) <= set(data.decode().splitlines()):
            pass                                            # a resumed log: it only grew
        elif n.startswith("results/"):
            pass                                            # tables are recomputed from the logs
        else:
            sys.exit(f"{dst} exists with different content; not overwriting")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    copied.append(n)
keep = root / "runs/kaggle_outputs" / src.name
keep.parent.mkdir(parents=True, exist_ok=True)
if not keep.exists():
    shutil.copyfile(src, keep)

# ---------- the cross-model overview, then the Kaggle results package (all models so far) ----------
subprocess.run([sys.executable, "-I", str(root / "src/bench/overview.py"), str(root)], check=True)
pack = root / "release/kaggle-runs"
if pack.exists():
    shutil.rmtree(pack)
(pack / "benhallueval-qa-judge-runs").mkdir(parents=True)
out = pack / "benhallueval-qa-judge-runs"
shutil.copytree(root / "runs", out / "runs", ignore=shutil.ignore_patterns("kaggle_outputs", ".*"))
shutil.copytree(root / "results", out / "results", ignore=shutil.ignore_patterns(".*"))
models = sorted(p.name for p in (root / "results").iterdir() if p.is_dir())
(out / "README.md").write_text(
    "# BenHalluEval-QA judge runs (private)\n\n"
    "Raw outputs of the genre-aware judge study on BenHalluEval-QA v1.3 (Kaggle dataset `benhallueval-qa-bangla`).\n\n"
    "- `runs/benhallueval__<model>__<turn>__<prompt>.jsonl`: one line per model call (raw reply, parsed label, tokens,"
    " latency, setup fingerprint). Never edit.\n"
    "- `results/<model>/<mode>/`: the notebook's tables (CSV), `summary.json` and `manifest.json`.\n"
    "- Ollama server logs are not included (they are large); they are in each model's notebook output zip.\n\n"
    f"Models so far: {', '.join(models)}.\n\nAdd the next model with **New Version** on this dataset.\n", encoding="utf-8")
(out / "dataset-metadata.json").write_text(json.dumps({
    "title": "BenHalluEval-QA judge runs", "id": "YOUR_KAGGLE_USERNAME/benhallueval-qa-judge-runs",
    "subtitle": "Raw judge and genre outputs per model on BenHalluEval-QA v1.3 (Bangla)",
    "isPrivate": True, "licenses": [{"name": "other"}]}, indent=2) + "\n", encoding="utf-8")
zpath = pack / "benhallueval-qa-judge-runs.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zz:
    for p in sorted(out.rglob("*")):
        if p.is_file():
            zz.write(p, p.relative_to(out))

# ---------- report ----------
print(f"model {model} | mode {mode} | version {manifest['model_version']} | GPU {manifest['gpu']!r}")
print(f"session {manifest['started'][:16]} to {manifest['finished'][:16]} UTC | conditions {manifest.get('judge_conditions')}")
print("setup hashes:", manifest["setup_hash"])
for k, v in stats.items():
    print(k, json.dumps(v))
print(f"Ollama log: {sum(trunc.values())} requests checked, {trunc[True]} truncated")
print(f"copied {len(copied)} files; original zip kept at {keep.relative_to(root)}")
print(f"Kaggle results package: {zpath.relative_to(root)} (models: {', '.join(models)})")
print("PROBLEMS:" if problems else "all checks passed", *problems, sep="\n  ")
if warnings:
    print("WARNINGS:", *warnings, sep="\n  ")
sys.exit(1 if problems else 0)
