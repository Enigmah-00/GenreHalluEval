"""Build the list of Claude-written questions for GenreHalluEval v2 from all batch files, with strict checks.

Batch file (data/labels/genrehallueval_v2/new_questions/batch_NN.txt), one line per question:
    GENRE|wiki title|paragraph|question|gold
- GENRE: one of the 11 codes of genre guide v2.0 (HISTORY ... RELIGION).
- paragraph: the index of a lead paragraph in the saved download (0, 1, ...), "0+1" for two consecutive ones, or
  "a-b" for the lines a to b of a full download (GRAMMAR questions, whose examples sit in the article body).
- wiki title: as downloaded, `full::<title>` for a whole-article download (fetch_passages.py ... full), or
  `book::<passage id>` for a passage transcribed from the NCTB grammar book (GRAMMAR only).
  The passage is copied from the saved API download (data/raw/genrehallueval_v2/new/*__candidates.csv), never typed.
Checks: the title was downloaded; the paragraph exists; the gold occurs in the passage word for word; the gold does
not occur in the question; the question ends with "?"; no question repeats an earlier one (or a v1.1 question); no
article is used twice, and none is an article of a kept v1.1 question (source check file). GRAMMAR is the one exception
to the article rule: Bangla Wikipedia has only a few grammar articles, so several GRAMMAR questions may share one
(Mahdi's decision, 2026-10-28).

The batch files are the source: every run rebuilds data/labels/genrehallueval_v2/new_questions_claude.csv from all of
them, in file order (ids g2-001, g2-002, ...). Fix a question by editing its line in place (never reorder or delete
lines, or later ids move); a line replaced in place keeps its id. Nothing is written if any check fails.
Usage: python3 -I src/genrehallueval_v2/add_questions.py <project_root>
"""
import csv
import datetime
import json
import sys
import unicodedata
from pathlib import Path

root = Path(sys.argv[1])
L = root / "data/labels/genrehallueval_v2"
OUT = L / "new_questions_claude.csv"
CODES = ["HISTORY", "POLITICS", "EDUCATION", "ARTS", "CULTURE", "SPORTS", "SCIENCE", "TECHNOLOGY", "GEOGRAPHY",
         "PLACES", "RELIGION", "GRAMMAR"]
COLS = ["question_id", "genre", "question", "gold", "passage", "wiki_title", "url", "revid", "rev_timestamp",
        "downloaded", "batch", "written_by"]
N = lambda s: unicodedata.normalize("NFC", " ".join((s or "").split()))

cands = {}
# passages transcribed by Claude from the NCTB class 9-10 grammar book (grammar_book/README.md); key `book::<id>`
for p in sorted((L / "grammar_book").glob("*__candidates.csv")):
    for r in csv.DictReader(open(p, encoding="utf-8")):
        row = dict(r, downloaded=datetime.datetime.fromtimestamp(p.stat().st_mtime).date().isoformat())
        cands["book::" + r["title"]] = row
for p in sorted((root / "data/raw/genrehallueval_v2/new").glob("*__candidates.csv")):
    for r in csv.DictReader(open(p, encoding="utf-8")):
        if r["title"]:
            row = dict(r, downloaded=datetime.datetime.fromtimestamp(p.stat().st_mtime).date().isoformat())
            if r.get("mode") == "full":                      # whole-article downloads never replace a lead download
                cands["full::" + r["title"]] = row
                cands.setdefault("full::" + r["requested"], row)
                continue
            cands[r["title"]] = row
            cands.setdefault(r["requested"], row)            # the title as requested also works (before a redirect)
v1 = {N(r["question"]) for r in csv.DictReader(open(root / "data/final/GenreHalluEval-v1.1/questions.csv", encoding="utf-8"))}
v1_titles = {r["wiki_title"] for r in csv.DictReader(open(L / "source_check_2026-10-28.csv", encoding="utf-8")) if r["wiki_title"]}
seen_q, seen_t = set(v1), set(v1_titles)
errors, new = [], []
next_id = 1
lines = [(b, n, line) for b in sorted((L / "new_questions").glob("batch_*.txt"))
         for n, line in enumerate(b.read_text(encoding="utf-8").splitlines(), 1)]
for batch, n, line in lines:
    if not line.strip() or line.startswith("#"):
        continue
    parts = [x.strip() for x in line.split("|")]
    if len(parts) != 5:
        errors.append(f"{batch.name} line {n}: needs 5 fields, has {len(parts)}")
        continue
    g, title, para, q, gold = parts
    q, gold = N(q), N(gold)
    if g not in CODES:
        errors.append(f"{batch.name} line {n}: genre {g}")
    c = cands.get(title)
    if not c:
        errors.append(f"{batch.name} line {n}: '{title}' was not downloaded")
        continue
    paras = json.loads(c["paragraphs"])
    try:
        idx = (list(range(int(para.split("-")[0]), int(para.split("-")[1]) + 1)) if "-" in para
               else [int(x) for x in para.split("+")])
        assert idx == list(range(idx[0], idx[-1] + 1)) and idx[-1] < len(paras)
    except Exception:
        errors.append(f"{batch.name} line {n}: paragraph '{para}' (the page has {len(paras)})")
        continue
    passage = N(" ".join(paras[i] for i in idx))
    if gold not in passage:
        errors.append(f"{batch.name} line {n}: gold '{gold}' is not in the passage word for word")
    if gold in q:
        errors.append(f"{batch.name} line {n}: the gold is inside the question")
    if not q.endswith("?"):
        errors.append(f"{batch.name} line {n}: the question must end with '?'")
    if q in seen_q:
        errors.append(f"{batch.name} line {n}: repeated question")
    if c["title"] in seen_t and g != "GRAMMAR":
        errors.append(f"{batch.name} line {n}: article '{c['title']}' already used (earlier line or a v1.1 question)")
    seen_q.add(q)
    seen_t.add(c["title"])
    new.append(dict(question_id=f"g2-{next_id:03d}", genre=g, question=q, gold=gold, passage=passage, wiki_title=c["title"],
                    url=c["url"], revid=c["revid"], rev_timestamp=c["timestamp"], downloaded=c["downloaded"],
                    batch=batch.name, written_by="Claude (claude-opus-5-5)"))
    next_id += 1
if errors:
    print("\n".join(errors))
    raise SystemExit(f"{len(errors)} problems: nothing was written")
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(new)
print(f"{len(new)} questions (g2-001..{new[-1]['question_id']}) from {len({r['batch'] for r in new})} batch files")
print("per genre:", {g: sum(r["genre"] == g for r in new) for g in CODES if any(r["genre"] == g for r in new)})
