"""Build GenreHalluEval v1.1 (Dataset 2): the Kaggle package, its zip, and blank labelling sheets.

Per question (250): the team's gold answer + 4 hallucinated answers written by Claude (F, C, S, I; guide v1.0).
  - Set B, `items.csv` (the TEST set; the notebooks read it): each answer is judged in its question's
    `mix_condition`: `context` (passage + question + answer) for 175 questions, `no_context` (question + answer)
    for 75. 1,250 answers.
  - Set A, `setA_all_with_passage.csv` (for publishing): the same 1,250 answers, all with the passage.
The passage stays in every row of Set B because the genre guess always uses question + passage (as on
BenHalluEval); `condition` decides whether the judge sees it. item_id = <question_id>__p<position>, positions
shuffled once per question (seed "2026:<question_id>"); the same answer has the same id in both sets.

Inputs:  data/processed/dataset2/seeds_v1.0.csv
         data/labels/dataset2/hallucinations_claude/batch_*.txt   (question_id|F|C|S|I)
         data/labels/dataset2/text_fixes_v1.1.csv                 (v1.1: passage, question and answer fixes)
         data/final/benhallueval-qa-v1.3/prompts/{genre_v1,judge_v1,judge_noctx_v1}.txt (the same prompts)
         results/lock/lock_v2.json
Outputs: data/final/GenreHalluEval-v1.1/, release/kaggle-genrehallueval/GenreHalluEval.zip,
         data/labels/dataset2/blank_sheets/ (never overwritten once an annotator has filled a copy)

Usage: python3 -I src/dataset2/build_package.py <project_root> [--fake-answers <out_dir>]   (fake = local tests only)
"""
import collections
import csv
import hashlib
import json
import random
import shutil
import sys
import zipfile
from pathlib import Path

root = Path(sys.argv[1])
FAKE = "--fake-answers" in sys.argv
NAME, VERSION = "GenreHalluEval", "1.1"
OUT = Path(sys.argv[sys.argv.index("--fake-answers") + 1]) if FAKE else root / f"data/final/{NAME}-v{VERSION}"
SEEDS = root / "data/processed/dataset2/seeds_v1.0.csv"
HDIR = root / "data/labels/dataset2/hallucinations_claude"
FIXES = root / "data/labels/dataset2/text_fixes_v1.1.csv"
PROMPTS = root / "data/final/benhallueval-qa-v1.3/prompts"
LOCK = root / "results/lock/lock_v2.json"
LOCK_SHA256 = "6d3c1d29cb8159d5f74300c799ce040c9a7c737dfb68b5c292a2a2aa948c9137"
TYPES = "FCSI"
COLS = ["item_id", "question_id", "condition", "answer_type", "design_label", "genre", "genre_status", "context",
        "question", "answer", "source"]

with open(SEEDS, encoding="utf-8", newline="") as f:
    seeds = list(csv.DictReader(f))
assert len(seeds) == 250
assert hashlib.sha256(LOCK.read_bytes()).hexdigest() == LOCK_SHA256, "lock_v2.json changed"

if FAKE:
    halluc = {r["question_id"]: {t: f"TEST-{t}-{r['question_id']}" for t in TYPES} for r in seeds}
else:
    halluc = {}
    for p in sorted(HDIR.glob("batch_*.txt")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                parts = [x.strip() for x in line.split("|")]
                assert len(parts) == 5 and parts[0] not in halluc, (p.name, line[:60])
                halluc[parts[0]] = dict(zip(TYPES, parts[1:]))
    assert set(halluc) == {r["question_id"] for r in seeds}, "every question needs 4 hallucinations"

# v1.1: apply the text fixes (each old text must occur exactly once)
by_qid = {r["question_id"]: r for r in seeds}
for r in seeds:
    r["text_fix"] = ""
with open(FIXES, encoding="utf-8", newline="") as f:
    fixes = list(csv.DictReader(f))
for x in fixes:
    s, field = by_qid[x["question_id"]], x["field"]
    if field.startswith("answer:"):
        t = field.split(":")[1]
        if not FAKE:
            assert halluc[x["question_id"]][t] == x["old"], (x["question_id"], field)
            halluc[x["question_id"]][t] = x["new"]
    else:
        assert s[field].count(x["old"]) == 1, (x["question_id"], field)
        s[field] = s[field].replace(x["old"], x["new"])
    s["text_fix"] = "; ".join(filter(None, [s["text_fix"], field]))

set_a, set_b = [], []
for r in seeds:
    qid = r["question_id"]
    rows = [dict(answer_type="gold", design_label=0, answer=r["gold"])]
    rows += [dict(answer_type=t, design_label=1, answer=halluc[qid][t]) for t in TYPES]
    assert len({x["answer"] for x in rows}) == 5, f"{qid}: the 5 answers must differ"
    pos = list(range(1, 6))
    random.Random(f"2026:{qid}").shuffle(pos)
    for p, x in sorted(zip(pos, rows), key=lambda z: z[0]):
        base = dict(item_id=f"{qid}__p{p}", question_id=qid, **x, genre=r["genre"], genre_status=r["genre_status"],
                    context=r["passage"], question=r["question"], source=r["source"])
        set_a.append(dict(base, condition="context"))
        set_b.append(dict(base, condition=r["mix_condition"]))


def write_csv(path, rows, cols):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


if OUT.exists():
    shutil.rmtree(OUT)
(OUT / "prompts").mkdir(parents=True)
write_csv(OUT / "items.csv", set_b, COLS)
write_csv(OUT / "setA_all_with_passage.csv", set_a, COLS)
write_csv(OUT / "questions.csv", seeds, ["question_id", "genre", "genre_a1", "genre_a2", "genre_a3", "genre_agree",
                                         "genre_status", "mix_condition", "source", "passage", "question", "gold",
                                         "change", "text_fix", "wiki_title", "wiki_revid"])
lock = json.loads(LOCK.read_text(encoding="utf-8"))
for name, key in (("genre_v1.txt", "genre"), ("judge_v1.txt", "context"), ("judge_noctx_v1.txt", "no_context")):
    shutil.copy(PROMPTS / name, OUT / "prompts" / name)
    text = (OUT / "prompts" / name).read_text(encoding="utf-8").rstrip()
    assert hashlib.sha256(text.encode("utf-8")).hexdigest()[:12] == lock["setup"]["prompt_sha12"][key], name
shutil.copy(LOCK, OUT / "lock_v2.json")

cnt = collections.Counter((x["condition"], x["design_label"]) for x in set_b)
card = f"""# {NAME} v{VERSION}{' (FAKE ANSWERS, LOCAL TESTS ONLY)' if FAKE else ''}

A Bangla question-answering hallucination test set with genre labels (Dataset 2 of the study "Genre-aware
hallucination judges for Bangla"). Test-only: nothing here is used to make or change a routing choice.

## Files

| File | What it is |
|---|---|
| `items.csv` | **Set B, the test set** (1,250 answers). Column `condition` says how each answer is judged: `context` = passage + question + answer ({cnt[('context', 0)] + cnt[('context', 1)]} answers, 175 questions); `no_context` = question + answer only ({cnt[('no_context', 0)] + cnt[('no_context', 1)]} answers, 75 questions). The passage stays in every row only because the genre guess uses question + passage. |
| `setA_all_with_passage.csv` | **Set A, for publishing**: the same 1,250 answers, all with the passage. Same `item_id`s. |
| `questions.csv` | The 250 questions: passage, source, gold answer, the three genre labels and the majority genre. |
| `prompts/` | The exact judge and genre prompts used on BenHalluEval-QA v1.3. |
| `lock_v2.json` | The routing choices locked on BenHalluEval before any answer here existed (sha256 `{LOCK_SHA256[:12]}…`). |
| `checksums.sha256` | sha256 of every file; the notebooks check them. |

## How it was made

- **Questions, passages and gold answers:** collected by the team (gold answers written by Mahdi Hasan Qurishi), 50 per genre
  (History, Politics & Education; Arts, Culture & Sports; Geography & Places; Science & Technology; Religion). Every
  question can be answered without its passage (checked by Mahdi Hasan Qurishi while annotating).
  Sources: Bangla Wikipedia (most), a few news sites, Banglapedia.
- **Overlap with BenHalluEval removed:** 17 rows were replaced (12 new Wikipedia passages, 5 new questions); see
  `questions.csv` column `change`.
- **Text fixes in v1.1** ({len(fixes)} fixes, {sum(1 for r in seeds if r['text_fix'])} questions; column `text_fix`): passages that did not
  state the gold answer (mostly Islamic Religion passages) now state it in one short phrase; one question's year
  lost a digit; one hallucinated answer was edited by annotator 1. No judge had seen any item.
- **Genre:** three annotators per question, frozen guide v1.0 (Fleiss' kappa 0.987 on the original sheet); the 17
  changed questions (`genre_status = relabel_pending`) are labelled again.
- **Hallucinated answers:** 4 per question, written by Claude (claude-opus-5-5) with the guide used for
  BenHalluEval-QA v1.3: F factualness, C comprehension, S specificity, I inference. All are meant to be wrong both by
  the passage and in the real world.
- **Labels:** `design_label` (0 = correct gold, 1 = written hallucination) is the label by construction. The final
  labels are the two annotators' agreed labels (passage label for every answer; world label for the 375 answers
  judged without the passage), added in v1.1.

## Licence and limits

Passages from Wikipedia are CC BY-SA 4.0; a few passages are short excerpts from news sites and Banglapedia, so check
their terms before any public release. Keep the Kaggle dataset private until then. Both this set and BenHalluEval-QA
v1.3 use Claude-written hallucinations, so this set tests new questions, passages and topics, not new answer writers.
"""
(OUT / "README.md").write_text(card, encoding="utf-8")
(OUT / "dataset-metadata.json").write_text(json.dumps(dict(
    title=NAME, id="YOUR_KAGGLE_USERNAME/genrehallueval", subtitle="Bangla QA hallucination test set with genre labels",
    isPrivate=True, licenses=[dict(name="other")]), indent=2) + "\n", encoding="utf-8")
with open(OUT / "checksums.sha256", "w", encoding="utf-8") as f:
    for p in sorted(x for x in OUT.rglob("*") if x.is_file() and x.name != "checksums.sha256"):
        f.write(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT)}\n")
print(f"wrote {OUT}: Set B {len(set_b)} answers, Set A {len(set_a)} answers")
print("Set B condition x label:", dict(cnt))
if FAKE:
    sys.exit(0)

# ---- the Kaggle zip ----
zdir = root / "release/kaggle-genrehallueval"
zdir.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(zdir / f"{NAME}.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(x for x in OUT.rglob("*") if x.is_file()):
        z.write(p, Path(NAME) / p.relative_to(OUT))
print("zip:", zdir / f"{NAME}.zip")

# ---- blank labelling sheets (one copy per annotator; shuffled; no design label, set or type) ----
sheets = root / "data/labels/dataset2/blank_sheets"
sheets.mkdir(parents=True, exist_ok=True)
plans = {"passage_labels": [x for x in set_a], "world_labels": [x for x in set_b if x["condition"] == "no_context"]}
for who in ("annotator1", "annotator2"):
    for kind, rows in plans.items():
        path = sheets / f"{kind}_{who}_BLANK.csv"
        if path.exists():
            continue
        order = rows[:]
        random.Random(f"2026:{kind}:{who}").shuffle(order)
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            if kind == "passage_labels":
                w.writerow(["row", "item_id", "question", "passage", "answer", "label (correct / hallucinated / unclear)", "note"])
                w.writerows([[i + 1, x["item_id"], x["question"], x["context"], x["answer"], "", ""] for i, x in enumerate(order)])
            else:
                w.writerow(["row", "item_id", "question", "answer", "label (correct / hallucinated / unclear)", "source you checked", "note"])
                w.writerows([[i + 1, x["item_id"], x["question"], x["answer"], "", "", ""] for i, x in enumerate(order)])
relabel = sheets / "genre_relabel_17_BLANK.csv"
if not relabel.exists():
    with open(relabel, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["question_id", "question", "passage", "genre annotator 1", "genre annotator 2", "genre annotator 3"])
        w.writerows([[r["question_id"], r["question"], r["passage"], "", "", ""] for r in seeds if r["genre_status"] == "relabel_pending"])
print("blank sheets:", sorted(p.name for p in sheets.glob("*.csv")))
