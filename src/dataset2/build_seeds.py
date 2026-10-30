"""Build the Dataset 2 seeds (passage, question, gold, genre) from the team's sheet, with the overlap fixes applied.

Inputs (never edited):
  data/raw/dataset2/dataset2_sheet1_2026-10-27.csv        the team's sheet (250 rows, 3 genre annotators)
  data/labels/dataset2/overlap_replacements_v1.csv        16 rows changed to remove BenHalluEval overlap
  data/raw/dataset2/wikipedia_replacements/*.json         Bangla Wikipedia API downloads for the new passages
Outputs:
  data/processed/dataset2/seeds_v1.0.csv                  one row per question
  data/labels/dataset2/genre_agreement.md                 agreement of the 3 genre annotators (original sheet)

Rules:
  - question_id = d2-<sheet row - 1, 3 digits>, in sheet order; never renumbered.
  - Rows changed for overlap keep their genre slot, but their genre must be labelled again by the annotators
    (genre_status = relabel_pending), because the question (and often the passage) is new.
  - mix_condition: how the Set B (`mix`) answers of a question are judged: `context` (passage + question + answer)
    for 70% of the questions, `no_context` (question + answer) for 30%, assigned per genre (35 / 15 of 50) with seed
    "2026:<genre>". Set A (`ctx`) answers are always judged with the passage. Fixed here, before any answer exists.

Usage: python3 -I src/dataset2/build_seeds.py <project_root>
"""
import collections
import csv
import json
import random
import re
import sys
import unicodedata
from pathlib import Path

root = Path(sys.argv[1])
SHEET = root / "data/raw/dataset2/dataset2_sheet1_2026-10-27.csv"
REPL = root / "data/labels/dataset2/overlap_replacements_v1.csv"
WIKI = root / "data/raw/dataset2/wikipedia_replacements"
OUT = root / "data/processed/dataset2/seeds_v1.0.csv"
AGREE = root / "data/labels/dataset2/genre_agreement.md"
SEED, MIX_CONTEXT_SHARE = 2026, 0.70
GENRES = ["History, Politics & Education", "Arts, Culture & Sports", "Geography & Places", "Science & Technology", "Religion", "Other"]
TIME_WORDS = r"বর্তমান|সর্বশেষ|এখন|সম্প্রতি|২০২৫|২০২৬"


def N(t):
    return unicodedata.normalize("NFC", " ".join((t or "").split()))


def load(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[g] * cb[g] for g in set(ca) | set(cb)) / n ** 2
    return (po - pe) / (1 - pe)


def fleiss(rows):
    n, cats = 3, sorted({g for r in rows for g in r})
    P = [(sum(r.count(c) ** 2 for c in cats) - n) / (n * (n - 1)) for r in rows]
    p = [sum(r.count(c) for r in rows) / (n * len(rows)) for c in cats]
    pbar, pe = sum(P) / len(P), sum(x * x for x in p)
    return (pbar - pe) / (1 - pe)


sheet = load(SHEET)
assert len(sheet) == 250, len(sheet)
repl = {int(r["sheet_row"]): r for r in load(REPL)}

# Wikipedia passages must be verbatim from the saved downloads.
extracts = {}
for p in WIKI.glob("*.json"):
    page = next(iter(json.loads(p.read_text(encoding="utf-8"))["query"]["pages"].values()))
    extracts[page["title"]] = (N(page["extract"]), str(page["revisions"][0]["revid"]))

ann = [[N(r[f"Genre(Annotator {k})"]) for k in (1, 2, 3)] for r in sheet]
for a in ann:
    assert all(g in GENRES for g in a), a

seeds = []
for i, r in enumerate(sheet):
    row = i + 2
    a1, a2, a3 = ann[i]
    top, cnt = collections.Counter(ann[i]).most_common(1)[0]
    assert N(r["Majority vote"]) == top or cnt == 1, (row, r["Majority vote"], ann[i])
    s = dict(question_id=f"d2-{i + 1:03d}", sheet_row=row, genre=N(r["Majority vote"]), genre_a1=a1, genre_a2=a2, genre_a3=a3,
             genre_agree=f"{cnt}/3", genre_status="ok", passage=N(r["Context"]), source=N(r["Source"]) or "unknown",
             question=N(r["Question"]), gold=N(r["Correct Answer"]), change="none", change_reason="", original_question="",
             original_gold="", wiki_title="", wiki_revid="")
    if row in repl:
        x = repl[row]
        s.update(change=x["action"], change_reason=x["reason"], original_question=s["question"], original_gold=s["gold"],
                 question=N(x["new_question"]), gold=N(x["new_gold"]), genre_status="relabel_pending")
        if x["action"] == "new_passage":
            text, rev = extracts[x["wiki_title"]]
            assert N(x["new_passage"]) in text and rev == x["wiki_revid"], row
            s.update(passage=N(x["new_passage"]), source="Wikipedia", wiki_title=x["wiki_title"], wiki_revid=rev)
    s["gold_in_passage"] = "yes" if s["gold"] in s["passage"] else "no"
    s["time_words"] = "yes" if re.search(TIME_WORDS, s["question"]) else "no"
    seeds.append(s)

# 70 / 30 judging condition for the Set B answers, per genre slot.
by_genre = collections.defaultdict(list)
for s in seeds:
    by_genre[s["genre"]].append(s)
for g, ss in sorted(by_genre.items()):
    ids = sorted(s["question_id"] for s in ss)
    random.Random(f"{SEED}:{g}").shuffle(ids)
    k = round(MIX_CONTEXT_SHARE * len(ids))
    yes = set(ids[:k])
    for s in ss:
        s["mix_condition"] = "context" if s["question_id"] in yes else "no_context"

assert len({s["question"] for s in seeds}) == 250 and len({s["passage"] for s in seeds}) == 250
OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(seeds[0]))
    w.writeheader()
    w.writerows(seeds)

# Genre agreement of the three annotators (original sheet, before the overlap changes).
pairs = {(1, 2): "1 vs 2", (1, 3): "1 vs 3", (2, 3): "2 vs 3"}
md = ["# Dataset 2: genre agreement of the three annotators (original sheet, 250 questions)", "",
      "Annotator numbers are the sheet's column names. Computed on the sheet as received (2026-10-27), before 16 questions",
      "were changed to remove BenHalluEval overlap; those 16 must be labelled again.", "",
      "| Pair | Agreement | Cohen's kappa |", "|---|---|---|"]
for (x, y), name in pairs.items():
    a, b = [r[x - 1] for r in ann], [r[y - 1] for r in ann]
    md.append(f"| {name} | {100 * sum(p == q for p, q in zip(a, b)) / len(a):.1f}% | {kappa(a, b):.3f} |")
md += ["", f"Fleiss' kappa (all three): {fleiss(ann):.3f}. All three agree on {sum(len(set(r)) == 1 for r in ann)} of 250.", "",
       "Rows where the annotators differ:", ""]
md += [f"- {seeds[i]['question_id']} (sheet row {i + 2}): {' / '.join(r)} -> majority {seeds[i]['genre']}"
       for i, r in enumerate(ann) if len(set(r)) > 1]
AGREE.write_text("\n".join(md) + "\n", encoding="utf-8")

print("\n".join(md))
print(f"\nwrote {OUT.relative_to(root)}: {len(seeds)} questions")
print("changes:", collections.Counter(s["change"] for s in seeds))
print("genre slots:", dict(collections.Counter(s["genre"] for s in seeds)))
print("Set B condition:", dict(collections.Counter((s["genre"][:10], s["mix_condition"]) for s in seeds)))
print("gold not word-for-word in passage:", sum(s["gold_in_passage"] == "no" for s in seeds),
      "| time words in question:", sum(s["time_words"] == "yes" for s in seeds),
      "| unknown source:", [s["question_id"] for s in seeds if s["source"] == "unknown"])
