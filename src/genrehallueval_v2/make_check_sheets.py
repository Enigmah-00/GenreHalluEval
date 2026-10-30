"""Draw the blind 20% check sample of GenreHalluEval v2 and write the two annotators' blank sheets.

Design (Mahdi, 2026-10-28):
- 20% of the Claude-written questions (new_questions_claude.csv), stratified by genre, seed 2026. Two annotators
  check them blind: the genre of each question, whether the question is clear and answerable from its passage, and a
  correct / hallucinated label for each of its 5 answers (the gold and the 4 written hallucinations, shuffled).
- 20% of the 230 team-written v1.1 questions kept in v2, stratified by their draft single genre, seed 2026: the
  genre label only (their answers were already double-labelled for v1.1).

The sheets are blind: no genre draft, no answer type, no design label, no question source. The key that maps the
blinded ids back is written to a separate file that must not be given to the annotators.
Both annotators get identical sheets (annotator 1 = Umme Zoayria Abedin, annotator 2 = Md Saminul Amin).

Outputs (never overwritten) in data/labels/genrehallueval_v2/check_v1/:
  annotator1_umme_zoayria_abedin__genre.csv, annotator1_umme_zoayria_abedin__answers.csv,
  annotator2_md_saminul_amin__genre.csv, annotator2_md_saminul_amin__answers.csv  (utf-8-sig, opens in Excel)
  KEY_do_not_share__genre.csv, KEY_do_not_share__answers.csv, sample_summary.md
Usage: python3 -I src/genrehallueval_v2/make_check_sheets.py <project_root>
"""
import csv
import random
import sys
from pathlib import Path

root = Path(sys.argv[1])
L = root / "data/labels/genrehallueval_v2"
OUT = L / "check_v1"
SEED, SHARE = 2026, 0.2
if OUT.exists():
    raise SystemExit(f"{OUT} already exists. The check sample is drawn once and never redrawn.")


def stratified(ids_by_genre, share, rng):
    """Largest-remainder allocation of round(share * total) over the genres, then a random draw inside each genre."""
    total = sum(len(v) for v in ids_by_genre.values())
    want = round(share * total)
    quota = {g: share * len(v) for g, v in ids_by_genre.items()}
    alloc = {g: int(q) for g, q in quota.items()}
    for g in sorted(quota, key=lambda g: (-(quota[g] - alloc[g]), g))[: want - sum(alloc.values())]:
        alloc[g] += 1
    return {g: sorted(rng.sample(sorted(ids_by_genre[g]), alloc[g])) for g in sorted(ids_by_genre)}


# the Claude-written questions and their answers
new = {r["question_id"]: r for r in csv.DictReader(open(L / "new_questions_claude.csv", encoding="utf-8"))}
hall = {}
for p in sorted((L / "hallucinations_claude").glob("batch_*.txt")):
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("g2-"):
            qid, *ans = line.split("|")
            hall[qid] = dict(zip("FCSI", ans))
missing = [q for q in new if q not in hall]
assert not missing, f"no hallucinations for {missing[:5]}"

# the kept v1.1 questions (genre label only)
draft = [r for r in csv.DictReader(open(L / "v1_questions_single_genre_draft_claude_2026-10-28.csv", encoding="utf-8-sig"))
         if r["keep_in_v2"].startswith("yes")]
v1 = {r["question_id"]: r for r in csv.DictReader(open(root / "data/final/GenreHalluEval-v1.1/questions.csv",
                                                        encoding="utf-8"))}
assert len(draft) == 230, len(draft)

rng = random.Random(SEED)
by_genre = {}
for q, r in new.items():
    by_genre.setdefault(r["genre"], []).append(q)
s_new = stratified(by_genre, SHARE, rng)
by_genre_v1 = {}
for r in draft:
    by_genre_v1.setdefault(r["single_genre_draft"], []).append(r["question_id"])
s_v1 = stratified(by_genre_v1, SHARE, rng)

# genre sheet: every sampled question, in random order, blinded ids
gitems = [("new", q) for g in s_new for q in s_new[g]] + [("v1.1", q) for g in s_v1 for q in s_v1[g]]
rng.shuffle(gitems)
genre_rows, genre_key = [], []
for i, (src, q) in enumerate(gitems, 1):
    cid = f"Q{i:03d}"
    if src == "new":
        question, passage, design = new[q]["question"], new[q]["passage"], new[q]["genre"]
    else:
        question, passage = v1[q]["question"], v1[q]["passage"]
        design = next(r["single_genre_draft"] for r in draft if r["question_id"] == q)
    genre_rows.append(dict(row=i, check_id=cid, question=question, passage=passage, genre="", confidence="",
                           question_ok="", note=""))
    genre_key.append(dict(check_id=cid, question_id=q, source=src, draft_genre=design))

# answer sheet: the 5 answers of every sampled new question; questions in random order, answers shuffled inside
anew = [q for g in s_new for q in s_new[g]]
rng.shuffle(anew)
ans_rows, ans_key = [], []
n = 0
for q in anew:
    r = new[q]
    answers = [("gold", r["gold"], "correct")] + [(t, a, "hallucinated") for t, a in hall[q].items()]
    rng.shuffle(answers)
    for t, a, lab in answers:
        n += 1
        aid = f"A{n:04d}"
        ans_rows.append(dict(row=n, answer_id=aid, question=r["question"], passage=r["passage"], answer=a, label="",
                             note=""))
        ans_key.append(dict(answer_id=aid, question_id=q, answer_type=t, design_label=lab))

OUT.mkdir(parents=True)
people = {"annotator1_umme_zoayria_abedin": "Umme Zoayria Abedin", "annotator2_md_saminul_amin": "Md Saminul Amin"}


def write(path, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


for stem in people:
    write(OUT / f"{stem}__genre.csv", genre_rows)
    write(OUT / f"{stem}__answers.csv", ans_rows)
write(OUT / "KEY_do_not_share__genre.csv", genre_key)
write(OUT / "KEY_do_not_share__answers.csv", ans_key)

lines = ["# GenreHalluEval v2: blind check sample v1", "",
         f"Seed {SEED}; {SHARE:.0%} of each genre (largest-remainder rounding). Drawn by "
         "`src/genrehallueval_v2/make_check_sheets.py`.", "",
         f"- Claude-written questions: {len(anew)} of {len(new)} (genre, question_ok and the label of all "
         f"{len(ans_rows)} answers).",
         f"- Team-written v1.1 questions kept in v2: {sum(len(v) for v in s_v1.values())} of {len(draft)} (genre only).",
         f"- Genre sheet: {len(genre_rows)} rows; answer sheet: {len(ans_rows)} rows.", "",
         "| Genre | New questions | Sampled | v1.1 kept | Sampled |", "|---|---|---|---|---|"]
for g in sorted(set(by_genre) | set(by_genre_v1)):
    lines.append(f"| {g} | {len(by_genre.get(g, []))} | {len(s_new.get(g, []))} | {len(by_genre_v1.get(g, []))} | "
                 f"{len(s_v1.get(g, []))} |")
(OUT / "sample_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
