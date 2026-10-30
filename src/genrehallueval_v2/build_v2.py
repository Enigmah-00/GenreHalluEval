"""Build GenreHalluEval v2.0 (12 single genres x 100 questions) and its learn / test split (Mahdi, 2026-10-28/29).

Questions (1,200):
- 230 team-written questions kept from v1.1 (golds by Mahdi Hasan Qurishi, 4 hallucinations by Claude, as in v1.1),
  with Claude's single-genre draft (kept as drafted after the blind check, Mahdi 2026-10-29);
- 970 questions written by Claude from current sources (Bangla Wikipedia revisions, and the NCTB class 9-10 grammar
  book for 88 GRAMMAR questions), each with a gold and 4 hallucinations (F/C/S/I); 20% blind-checked by two
  annotators (data/labels/genrehallueval_v2/check_v1/).
Every genre has exactly 100 questions. item_id = <question_id>__p<position>; v1.1 ids are kept, new positions are
shuffled once per question (seed "2026:<question_id>"), as in v1.1.

Split (seed 2026), stratified by genre and, inside each genre, by origin (v1.1 / new):
- learn half: 50 questions per genre (600). Every pool judge judges every answer with AND without the passage, and
  every pool LLM names the genre of every question. Every routing choice is learned here (make_lock_v2.py).
- test half: the other 50 per genre (600). Each question is judged in one condition: 25 per genre with the passage
  and 25 without (300 + 300 questions). Used only to test the routes learned on the learn half.
Pool: deepseek-r1-14b, gemma4-31b, gpt-oss-20b, qwen3.5-27b with English prompts; tigerllm-9b with Bangla prompts.
Genre prompts genre_v2 / genre_bn_v2 (12 genres + Other); judge prompts unchanged. Cells need 50+ questions (golden
rule 5). Main tests: R vs A and F vs A, with and without the passage (4 tests, Holm over 4).

Labels (data/labels/genrehallueval_v2/labels_v2.0.csv): v1.1 answers keep their agreed passage labels (identical to
the design labels); new answers use the design label (gold = 0, F/C/S/I = 1).

Outputs (never overwritten): data/final/GenreHalluEval-v<version>/, the labels file, and
release/kaggle-genrehallueval-v2/GenreHalluEval-v2.zip.
Usage: python3 -I src/genrehallueval_v2/build_v2.py <project_root> <version> [--out DIR]   (--out: local tests only)
"""
import argparse
import collections
import csv
import hashlib
import json
import random
import shutil
import zipfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("root")
ap.add_argument("version")
ap.add_argument("--out")
args = ap.parse_args()
root = Path(args.root)
L = root / "data/labels/genrehallueval_v2"
SRC = root / "data/final/GenreHalluEval-v1.1"
OUT = Path(args.out) if args.out else root / f"data/final/GenreHalluEval-v{args.version}"
LABELS = (OUT.parent / "labels.csv") if args.out else L / f"labels_v{args.version}.csv"
ZIP = (OUT.parent / "GenreHalluEval-v2.zip") if args.out else root / "release/kaggle-genrehallueval-v2/GenreHalluEval-v2.zip"
NAME = "GenreHalluEval-v2"
for p in (OUT, LABELS):
    if p.exists():
        raise SystemExit(f"{p} already exists. A package is never overwritten; make a new version.")
SEED, PER_GENRE, MIN_CELL = 2026, 100, 50
NAMES = {"HISTORY": "History", "POLITICS": "Politics", "EDUCATION": "Education", "ARTS": "Arts", "CULTURE": "Culture",
         "SPORTS": "Sports", "SCIENCE": "Science", "TECHNOLOGY": "Technology", "GEOGRAPHY": "Geography",
         "PLACES": "Places", "RELIGION": "Religion", "GRAMMAR": "Grammar", "OTHER": "Other"}
BN = {"HISTORY": "ইতিহাস", "POLITICS": "রাজনীতি", "EDUCATION": "শিক্ষা", "ARTS": "শিল্পকলা", "CULTURE": "সংস্কৃতি",
      "SPORTS": "খেলাধুলা", "SCIENCE": "বিজ্ঞান", "TECHNOLOGY": "প্রযুক্তি", "GEOGRAPHY": "ভূগোল", "PLACES": "স্থান",
      "RELIGION": "ধর্ম", "GRAMMAR": "ব্যাকরণ", "OTHER": "অন্যান্য"}
ORDER = [g for g in NAMES if g != "OTHER"]
POOL = ["deepseek-r1-14b", "gemma4-31b", "gpt-oss-20b", "qwen3.5-27b", "tigerllm-9b"]
LANGUAGE = {m: "bn" if m == "tigerllm-9b" else "en" for m in POOL}
PROMPTS = {"en": ["genre_v2", "judge_v1", "judge_noctx_v1"], "bn": ["genre_bn_v2", "judge_bn_v1", "judge_noctx_bn_v1"]}
TYPES = ["F", "C", "S", "I"]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig")))


# ---- the 230 kept v1.1 questions (frozen v1.1 files) ----
want = dict(l.split()[::-1] for l in open(SRC / "checksums.sha256", encoding="utf-8") if l.strip())
for name in ("questions.csv", "setA_all_with_passage.csv"):
    assert sha(SRC / name) == want[name], f"{name} differs from v1.1"
v1q = {r["question_id"]: r for r in read(SRC / "questions.csv")}
draft = {r["question_id"]: r["single_genre_draft"] for r in read(L / "v1_questions_single_genre_draft_claude_2026-10-28.csv")
         if r["keep_in_v2"].startswith("yes")}
v1lab = {r["item_id"]: r["label"] for r in read(root / "data/labels/dataset2/passage_labels_agreed_v1.csv")}
Q, A = {}, collections.defaultdict(list)          # question_id -> row; question_id -> answers
for q, g in draft.items():
    x = v1q[q]
    src = x["source"] + (f" (Wikipedia: {x['wiki_title']}, revision {x['wiki_revid']})" if x.get("wiki_title") else "")
    Q[q] = dict(question_id=q, genre_code=g, origin="team (v1.1)", question=x["question"], gold=x["gold"],
                passage=x["passage"], source=src, source_url="", revid=x.get("wiki_revid", ""), rev_timestamp="",
                written_by="team (gold: Mahdi Hasan Qurishi); hallucinations: Claude",
                genre_by="Claude single-genre draft (kept after the blind check)")
for r in read(SRC / "setA_all_with_passage.csv"):
    if r["question_id"] in draft:
        assert v1lab[r["item_id"]] == r["design_label"], f"{r['item_id']}: agreed label differs from the design"
        A[r["question_id"]].append(dict(item_id=r["item_id"], answer_type=r["answer_type"],
                                        design_label=int(r["design_label"]), answer=r["answer"], label_how="agreed (v1.1)"))

# ---- the 970 Claude-written questions ----
hall = {}
for p in sorted((L / "hallucinations_claude").glob("batch_*.txt")):
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("g2-"):
            qid, *ans = line.split("|")
            assert len(ans) == 4 and qid not in hall, qid
            hall[qid] = dict(zip(TYPES, ans))
for r in read(L / "new_questions_claude.csv"):
    q = r["question_id"]
    book = not r["revid"]
    Q[q] = dict(question_id=q, genre_code=r["genre"], origin="Claude (v2)", question=r["question"], gold=r["gold"],
                passage=r["passage"],
                source=(f"NCTB book, passage {r['wiki_title']}: {r['url']}" if book
                        else f"Bangla Wikipedia: {r['wiki_title']} (revision {r['revid']}, {r['rev_timestamp']})"),
                source_url="" if book else r["url"], revid=r["revid"], rev_timestamp=r["rev_timestamp"],
                written_by=r["written_by"], genre_by="Claude (20% blind-checked)")
    rows = [dict(answer_type="gold", design_label=0, answer=r["gold"])]
    rows += [dict(answer_type=t, design_label=1, answer=hall[q][t]) for t in TYPES]
    assert len({x["answer"] for x in rows}) == 5, f"{q}: the 5 answers must differ"
    pos = list(range(1, 6))
    random.Random(f"2026:{q}").shuffle(pos)
    for p, x in sorted(zip(pos, rows), key=lambda z: z[0]):
        A[q].append(dict(x, item_id=f"{q}__p{p}", label_how="design (20% blind-checked)"))
assert set(hall) == {q for q in Q if Q[q]["origin"].startswith("Claude")}, "hallucinations and questions must match"
count = collections.Counter(x["genre_code"] for x in Q.values())
assert all(count[g] == PER_GENRE for g in ORDER) and len(Q) == PER_GENRE * len(ORDER), count
assert all(len(A[q]) == 5 and sorted(a["design_label"] for a in A[q]) == [0, 1, 1, 1, 1] for q in Q)

# ---- the split: per genre 50 + 50, balanced by origin; in the test half 25 with the passage, 25 without ----
rng = random.Random(SEED)
half, test_cond = {}, {}
for g in ORDER:
    groups = []
    for origin in ("team (v1.1)", "Claude (v2)"):
        qs = sorted(q for q in Q if Q[q]["genre_code"] == g and Q[q]["origin"] == origin)
        rng.shuffle(qs)
        groups += qs
    for i, q in enumerate(groups):                     # alternate: 50 / 50, each origin split as evenly as possible
        half[q] = "learn" if i % 2 == 0 else "test"
    test = [q for q in groups if half[q] == "test"]
    for i, q in enumerate(test):
        test_cond[q] = "context" if i % 2 == 0 else "no_context"
for g in ORDER:
    assert sum(half[q] == "learn" for q in Q if Q[q]["genre_code"] == g) == PER_GENRE // 2
    assert sum(test_cond.get(q) == "context" for q in Q if Q[q]["genre_code"] == g) == PER_GENRE // 4

cols = ["item_id", "question_id", "condition", "answer_type", "design_label", "genre", "genre_status", "context",
        "question", "answer", "source", "origin"]
learn_rows, test_rows, label_rows = [], [], []
for q in sorted(Q):
    x = Q[q]
    for a in sorted(A[q], key=lambda a: a["item_id"]):
        row = dict(item_id=a["item_id"], question_id=q, answer_type=a["answer_type"], design_label=a["design_label"],
                   genre=NAMES[x["genre_code"]], genre_status=x["genre_by"], context=x["passage"], question=x["question"],
                   answer=a["answer"], source=x["source"], origin=x["origin"])
        label_rows.append(dict(item_id=a["item_id"], question_id=q, label=a["design_label"], how=a["label_how"]))
        if half[q] == "learn":
            for c in ("context", "no_context"):
                learn_rows.append(dict(row, condition=c))
        else:
            test_rows.append(dict(row, condition=test_cond[q]))


def write_csv(path, rows, fields):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


OUT.mkdir(parents=True)
(OUT / "prompts").mkdir()
for lang, pids in PROMPTS.items():
    for pid in pids:
        src = SRC / "prompts" / f"{pid}.txt" if pid in ("judge_v1", "judge_noctx_v1") else root / "prompts" / f"{pid}.txt"
        shutil.copyfile(src, OUT / "prompts" / f"{pid}.txt")
write_csv(OUT / "learn_items.csv", learn_rows, cols)
write_csv(OUT / "test_items.csv", test_rows, cols)
qcols = ["question_id", "genre", "genre_code", "origin", "half", "test_condition", "question", "gold", "passage",
         "source", "source_url", "revid", "rev_timestamp", "written_by", "genre_by"]
write_csv(OUT / "questions.csv", [dict(Q[q], genre=NAMES[Q[q]["genre_code"]], half=half[q],
                                       test_condition=test_cond.get(q, "")) for q in sorted(Q)], qcols)
write_csv(OUT / "split.csv", [dict(question_id=q, genre=NAMES[Q[q]["genre_code"]], origin=Q[q]["origin"], half=half[q],
                                   test_condition=test_cond.get(q, "")) for q in sorted(Q)],
          ["question_id", "genre", "origin", "half", "test_condition"])
LABELS.parent.mkdir(parents=True, exist_ok=True)
write_csv(LABELS, label_rows, ["item_id", "question_id", "label", "how"])
(OUT / "pool.json").write_text(json.dumps(dict(
    dataset=f"GenreHalluEval v{args.version}", experiment="routes learned on the learn half and tested on the test half",
    decided="Mahdi Hasan Qurishi, 2026-10-28/29, before any v2 run",
    source=dict(v1_1_questions_csv_sha256=want["questions.csv"], v1_1_answers_csv_sha256=want["setA_all_with_passage.csv"],
                new_questions_csv_sha256=sha(L / "new_questions_claude.csv"),
                hallucination_files_sha256={p.name: sha(p) for p in sorted((L / "hallucinations_claude").glob("batch_*.txt"))}),
    seed=SEED, pool=POOL, prompt_language=LANGUAGE, prompt_ids=PROMPTS, genres=NAMES, genres_bn=BN,
    min_cell_questions=MIN_CELL,
    labels="labels_v2.0.csv (not in this package): v1.1 answers = agreed passage labels; new answers = design labels",
    rules="as lock v1/v2 and the last split: A = lowest overall BHS; best genre guesser = highest agreement with our "
          "genre; judge x genre table; own-genre cells; R = best path; ties -> lower overall BHS; a judge with no_answer "
          "on half or more of the learn answers in both conditions is dropped; cells need 50+ questions",
    main_tests="on the test half: R vs A and F vs A, with the passage and without it (4 tests, Holm over 4), paired "
               "bootstrap over test questions, 10,000 re-samples, seed 2026, two-sided. D and E vs A are extra."),
    ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

n = lambda rows, c: sum(r["condition"] == c for r in rows)
by_origin = collections.Counter((Q[q]["origin"], half[q]) for q in Q)
(OUT / "README.md").write_text(f"""# GenreHalluEval v{args.version}

Bangla hallucination-judge test set with 12 single genres x 100 questions (1,200 questions, 6,000 answers). Made by
`src/genrehallueval_v2/build_v2.py` (seed {SEED}).

- **Questions:** 230 team-written questions kept from GenreHalluEval v1.1 (golds by Mahdi Hasan Qurishi) and 970
  questions written by Claude (claude-opus-5-5) from current sources: Bangla Wikipedia (title, revision id and time
  in `questions.csv`) and, for 88 GRAMMAR questions, the NCTB class 9-10 Bangla grammar book (book page in `source`).
- **Answers:** every question has its gold answer and 4 hallucinated answers written by Claude (F = a wrong fact of
  the same kind, C = a misread question, S = the gold plus a false detail, I = a wrong inference). The passage defines
  the truth.
- **Checks:** two annotators (Umme Zoayria Abedin, Md Saminul Amin) labelled a blind, stratified 20% sample alone: 194
  Claude-written questions (genre, question quality, all 970 answers) and 46 kept v1.1 questions (genre). Answer
  labels: kappa 0.990 between the annotators; genre: kappa 0.991, and 0.973 / 0.982 against the genre used here.
- **Genres:** {", ".join(NAMES[g] for g in ORDER)} (guide `docs/genre-guide-v2.md`; prompts `genre_v2`, `genre_bn_v2`).

## Files

- `learn_items.csv`: the learn half, {len(learn_rows) // 10} questions (50 per genre); every answer twice, once per
  condition ({len(learn_rows)} rows). Every pool judge judges every row; every pool LLM names the genre of every
  question.
- `test_items.csv`: the test half, {len({r['question_id'] for r in test_rows})} questions, {len(test_rows)} answers; each
  question in one condition: with the passage {n(test_rows, 'context') // 5} questions (25 per genre), without it
  {n(test_rows, 'no_context') // 5}.
- `questions.csv`: one row per question (genre, origin, half, test condition, question, gold, passage, source).
- `split.csv`: the half and test condition of every question. The split is stratified by genre and, inside each genre,
  by origin (learn: {by_origin[('team (v1.1)', 'learn')]} v1.1 + {by_origin[('Claude (v2)', 'learn')]} new; test:
  {by_origin[('team (v1.1)', 'test')]} + {by_origin[('Claude (v2)', 'test')]}).
- `pool.json`: the judges, the prompt language per judge (TigerLLM: Bangla), the genres, the cell minimum
  ({MIN_CELL}) and the main tests, all fixed before any run.
- `prompts/`: genre and judge prompts in English and Bangla.
- `lock_ghe2_v1.json` (added after the learn run, by `src/genrehallueval_v2/make_lock_v2.py`): the routes for the test
  half.

`design_label`: 0 = correct, 1 = hallucinated. Item ids of v1.1 questions are those of v1.1.
""", encoding="utf-8")
(OUT / "dataset-metadata.json").write_text(json.dumps(dict(
    title=NAME, id="YOUR_KAGGLE_USERNAME/genrehallueval-v2", subtitle="GenreHalluEval v2: 12 genres, learn/test split",
    isPrivate=True, licenses=[dict(name="other")]), indent=2) + "\n", encoding="utf-8")
with open(OUT / "checksums.sha256", "w", encoding="utf-8") as f:
    for p in sorted(x for x in OUT.rglob("*") if x.is_file() and x.name != "checksums.sha256"):
        f.write(f"{sha(p)}  {p.relative_to(OUT)}\n")
ZIP.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(x for x in OUT.rglob("*") if x.is_file()):
        z.write(p, Path(NAME) / p.relative_to(OUT))
print(f"wrote {OUT}: {len(Q)} questions; learn {len(learn_rows)} rows ({len(learn_rows) // 10} questions); test "
      f"{len(test_rows)} answers (context {n(test_rows, 'context')}, no_context {n(test_rows, 'no_context')}); "
      f"by origin {dict(by_origin)}\nlabels: {LABELS}\nzip: {ZIP}")
