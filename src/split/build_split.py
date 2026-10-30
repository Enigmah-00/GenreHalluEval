"""Build the GenreHalluEval split package (exploratory split experiment, decided by Mahdi on 2026-10-27, after the
confirmatory Dataset 2 result).

The 250 questions of GenreHalluEval v1.1 are split in two halves, stratified by our genre (25 + 25 per genre,
seed 2026):
  - learn half (125 questions, 625 answers): every pool judge judges every answer with AND without the passage, and
    names the genre of every question. Every routing choice is learned here (src/split/make_split_lock.py).
  - test half (125 questions, 625 answers): each question is judged in one condition, half with the passage and half
    without (13 or 12 per genre; 63 + 62 questions). Used only to test the routes learned on the learn half.
Pool (Mahdi, 2026-10-27): deepseek-r1-14b, gemma4-31b, gpt-oss-20b, qwen3.5-27b, tigerllm-9b (TigerLLM with the
Bangla prompts genre_bn_v1 / judge_bn_v1 / judge_noctx_bn_v1, as in its Bangla-prompt BenHalluEval run). Not run:
llama3.1-8b, mistral-nemo-12b, qwen2.5-32b, gemma2-27b. Cells need 20+ questions (a half has 25 per genre).

Outputs (never overwritten): data/final/GenreHalluEval-split-v1/ and release/kaggle-split/GenreHalluEval-split.zip.
Usage: python3 -I src/split/build_split.py <project_root> [--out <dir>]   (--out: for local tests only)
"""
import csv
import hashlib
import json
import random
import shutil
import sys
import zipfile
from pathlib import Path

root = Path(sys.argv[1])
test_out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
NAME = "GenreHalluEval-split"
SRC = root / "data/final/GenreHalluEval-v1.1"
OUT = Path(test_out) if test_out else root / "data/final/GenreHalluEval-split-v1"
if OUT.exists():
    sys.exit(f"{OUT} already exists. A package is never overwritten; make a new version.")
SEED = 2026
CODE = {"History, Politics & Education": "HISTORY", "Arts, Culture & Sports": "ARTS", "Science & Technology": "SCIENCE",
        "Geography & Places": "GEOGRAPHY", "Religion": "RELIGION", "Other": "OTHER"}
ORDER = ["HISTORY", "ARTS", "SCIENCE", "GEOGRAPHY", "RELIGION"]
POOL = ["deepseek-r1-14b", "gemma4-31b", "gpt-oss-20b", "qwen3.5-27b", "tigerllm-9b"]
LANGUAGE = {m: "bn" if m == "tigerllm-9b" else "en" for m in POOL}
PROMPTS = {"en": ["genre_v1", "judge_v1", "judge_noctx_v1"], "bn": ["genre_bn_v1", "judge_bn_v1", "judge_noctx_bn_v1"]}

# the source package must be the frozen v1.1
want = dict(l.split()[::-1] for l in open(SRC / "checksums.sha256", encoding="utf-8") if l.strip())
for name in ("items.csv", "questions.csv"):
    assert hashlib.sha256((SRC / name).read_bytes()).hexdigest() == want[name], f"{name} differs from v1.1"
items = list(csv.DictReader(open(SRC / "items.csv", encoding="utf-8")))
questions = {r["question_id"]: r for r in csv.DictReader(open(SRC / "questions.csv", encoding="utf-8"))}
genre = {q: CODE[r["genre"]] for q, r in questions.items()}
assert sorted(set(genre.values())) == sorted(ORDER) and all(sum(g == x for g in genre.values()) == 50 for x in ORDER)

# ---- the split: 25 + 25 questions per genre; in the test half 13 or 12 with the passage (alternating by genre) ----
rng = random.Random(SEED)
half, test_cond = {}, {}
for i, g in enumerate(ORDER):
    qs = sorted(q for q in questions if genre[q] == g)
    rng.shuffle(qs)
    for q in qs[:25]:
        half[q] = "learn"
    test = qs[25:]
    for q in test:
        half[q] = "test"
    rng.shuffle(test)
    k = 13 if i % 2 == 0 else 12
    for j, q in enumerate(test):
        test_cond[q] = "context" if j < k else "no_context"

cols = ["item_id", "question_id", "condition", "answer_type", "design_label", "genre", "genre_status", "context",
        "question", "answer", "source"]
learn_rows, test_rows = [], []
for r in sorted(items, key=lambda x: x["item_id"]):
    q = r["question_id"]
    row = {k: r[k] for k in cols}
    row["context"] = questions[q]["passage"]
    if half[q] == "learn":
        for c in ("context", "no_context"):
            learn_rows.append(dict(row, condition=c))
    else:
        test_rows.append(dict(row, condition=test_cond[q]))

OUT.mkdir(parents=True)
(OUT / "prompts").mkdir()
for lang, pids in PROMPTS.items():
    for pid in pids:
        src = SRC / "prompts" / f"{pid}.txt" if lang == "en" else root / "prompts" / f"{pid}.txt"
        shutil.copyfile(src, OUT / "prompts" / f"{pid}.txt")
for name, rows in (("learn_items.csv", learn_rows), ("test_items.csv", test_rows)):
    with open(OUT / name, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
with open(OUT / "split.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["question_id", "genre", "genre_status", "half", "test_condition"])
    for q in sorted(questions):
        w.writerow([q, genre[q], questions[q]["genre_status"], half[q], test_cond.get(q, "")])
(OUT / "pool.json").write_text(json.dumps(dict(
    experiment="GenreHalluEval split experiment (exploratory; added after the confirmatory Dataset 2 result)",
    decided="2026-10-27 by Mahdi Hasan Qurishi, before any split run",
    source=dict(package="GenreHalluEval v1.1", items_csv_sha256=want["items.csv"], questions_csv_sha256=want["questions.csv"]),
    seed=SEED, pool=POOL, prompt_language=LANGUAGE, prompt_ids=PROMPTS,
    not_run=["llama3.1-8b", "mistral-nemo-12b", "qwen2.5-32b", "gemma2-27b"],
    min_cell_questions=20,
    labels="agreed passage labels (data/labels/dataset2/passage_labels_agreed_v1.csv), used in both conditions",
    rules="as lock v1/v2: A = lowest overall BHS; best genre guesser = highest agreement with our genre; judge x genre "
          "table; own-genre cells; R = best path; ties -> lower overall BHS; but cells need 20+ questions"),
    indent=1) + "\n", encoding="utf-8")
n = lambda rows, c: sum(r["condition"] == c for r in rows)
(OUT / "README.md").write_text(f"""# GenreHalluEval split (exploratory)

Made by `src/split/build_split.py` from GenreHalluEval v1.1 (seed {SEED}; stratified by our genre).

- `learn_items.csv`: the learn half, {len(learn_rows) // 10} questions; every answer appears twice, once per condition
  ({len(learn_rows)} rows). Every pool judge judges every row; every pool LLM names the genre of every question.
- `test_items.csv`: the test half, {len({r['question_id'] for r in test_rows})} questions, {len(test_rows)} answers;
  each question in one condition: with the passage {n(test_rows, 'context') // 5} questions ({n(test_rows, 'context')}
  answers), without it {n(test_rows, 'no_context') // 5} ({n(test_rows, 'no_context')} answers).
- `split.csv`: the half and test condition of every question. `pool.json`: the pool, the prompt language per model
  (TigerLLM: Bangla) and the rules, fixed before any run.
- `prompts/`: the English prompts of every run, and the Bangla prompts of TigerLLM's Bangla-prompt run.
- `lock_split_v1.json` (added after the learn run, by `src/split/make_split_lock.py`): the routes for the test half.

Item and question ids are those of GenreHalluEval v1.1. Labels are not in this package.
""", encoding="utf-8")
(OUT / "dataset-metadata.json").write_text(json.dumps(dict(
    title=NAME, id="YOUR_KAGGLE_USERNAME/genrehallueval-split", subtitle="GenreHalluEval split experiment (learn/test)",
    isPrivate=True, licenses=[dict(name="other")]), indent=2) + "\n", encoding="utf-8")


def write_checksums(out):
    with open(out / "checksums.sha256", "w", encoding="utf-8") as f:
        for p in sorted(x for x in out.rglob("*") if x.is_file() and x.name != "checksums.sha256"):
            f.write(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out)}\n")


def write_zip(out, zpath):
    zpath.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(x for x in out.rglob("*") if x.is_file()):
            z.write(p, Path(NAME) / p.relative_to(out))


write_checksums(OUT)
zpath = (OUT.parent / f"{NAME}.zip") if test_out else root / "release/kaggle-split" / f"{NAME}.zip"
write_zip(OUT, zpath)
print(f"wrote {OUT}: learn {len(learn_rows)} rows ({len(learn_rows) // 10} questions), test {len(test_rows)} answers "
      f"(context {n(test_rows, 'context')}, no_context {n(test_rows, 'no_context')})")
print("zip:", zpath)
