"""Merge Claude's draft genre labels into the BenHalluEval QA seed file.

Labels = Claude's draft v0.2 (genre_draft_claude.txt) + the guide v1.0 rule changes (genre_rule_changes_v1.txt).
Reads only id / question / context for checks; copies correct_answer through untouched.
Outputs (UTF-8 with BOM so Excel shows Bangla correctly):
  data/processed/banglahallueval_qa_1000_with_genre.csv  - original rows + draft genre + empty review columns
  data/labels/genre_blind200_for_human.csv               - 200 random questions, NO draft labels (blind set)

Usage: python3 -I src/genre/build_genre_csv.py <project_root>
"""
import collections
import csv
import random
import re
import sys
from pathlib import Path

# Frozen genre list, guide v1.0 (docs/genre-guide.md). Sports is kept as a fine label inside Arts, Culture & Sports.
GENRES = {
    "HP": "History, Politics & Education",
    "AC": "Arts, Culture & Sports",
    "SP": "Arts, Culture & Sports",
    "ST": "Science & Technology",
    "GP": "Geography & Places",
    "RE": "Religion",
    "OT": "Other",
}
FINE = {**GENRES, "AC": "Arts & Culture", "SP": "Sports"}
CONF = {"H": "high", "L": "low"}
BLIND_N, BLIND_SEED = 200, 2026
# Devanagari block minus the danda/double danda (U+0964/0965), which Bangla text uses as full stops.
DEVANAGARI = re.compile(r"[ऀ-ॣ०-ॿ]")

root = Path(sys.argv[1])
raw = root / "data/raw/benhallueval/banglahallueval_qa_1000.csv"
labels_path = root / "data/labels/genre_draft_claude.txt"
changes_path = root / "data/labels/genre_rule_changes_v1.txt"
flags_path = root / "data/labels/data_flags_claude.txt"
out_main = root / "data/processed/banglahallueval_qa_1000_with_genre.csv"
out_blind = root / "data/labels/genre_blind200_for_human.csv"

with open(raw, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    src_cols = reader.fieldnames
    rows = list(reader)
assert len(rows) == 1000, len(rows)

# Unique questions in order of first appearance (same order Claude labeled them in).
first_row_of_id, uniq_ids = {}, []
for i, r in enumerate(rows):
    if r["id"] not in first_row_of_id:
        first_row_of_id[r["id"]] = i
        uniq_ids.append(r["id"])

labels = {}
for line in labels_path.read_text(encoding="utf-8").splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    idx, code, conf, note = line.split("|", 3)
    idx = int(idx)
    assert idx not in labels, f"index {idx} labeled twice"
    assert code in GENRES and conf in CONF, line
    labels[idx] = (code, conf, note.strip())
assert sorted(labels) == list(range(len(uniq_ids))), "every unique question must be labeled exactly once"

n_changed = 0
for line in changes_path.read_text(encoding="utf-8").splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    idx, old, new, conf, reason = line.split("|", 4)
    idx = int(idx)
    assert labels[idx][0] == old, f"index {idx}: draft is {labels[idx][0]}, change file expects {old}"
    assert new in GENRES and conf in CONF, line
    labels[idx] = (new, conf, f"v1.0 rule: {reason.strip()}")
    n_changed += 1
label_of_id = {qid: labels[k] for k, qid in enumerate(uniq_ids)}

flag_of_id = {}
for line in flags_path.read_text(encoding="utf-8").splitlines():
    if line.strip() and not line.startswith("#"):
        idx, flag = line.split("|", 1)
        flag_of_id[uniq_ids[int(idx)]] = flag.strip()

# Checks: identical question text should get the same genre; flag Devanagari script.
by_text = collections.defaultdict(set)
for qid in uniq_ids:
    by_text[rows[first_row_of_id[qid]]["question"].strip()].add(label_of_id[qid][0])
conflicts = {t: g for t, g in by_text.items() if len(g) > 1}
devanagari_q = [i + 1 for i, r in enumerate(rows) if DEVANAGARI.search(r["question"])]
devanagari_ctx = [i + 1 for i, r in enumerate(rows) if DEVANAGARI.search(r["context"])]

new_cols = ["row", *src_cols, "genre_draft", "genre_confidence", "genre_note",
            "duplicate_of_row", "data_flag", "verified_genre", "changed", "genre_fine"]
out_main.parent.mkdir(parents=True, exist_ok=True)
with open(out_main, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=new_cols)
    w.writeheader()
    for i, r in enumerate(rows):
        code, conf, note = label_of_id[r["id"]]
        first = first_row_of_id[r["id"]]
        w.writerow({
            "row": i + 1, **r,
            "genre_draft": GENRES[code],
            "genre_confidence": CONF[conf],
            "genre_note": note,
            "duplicate_of_row": first + 1 if first != i else "",
            "data_flag": flag_of_id.get(r["id"], ""),
            "verified_genre": "",
            "changed": "",
            "genre_fine": FINE[code],
        })

blind_ids = random.Random(BLIND_SEED).sample(uniq_ids, BLIND_N)
with open(out_blind, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["blind_no", "row", "id", "question", "context", "your_genre"])
    w.writeheader()
    for n, qid in enumerate(blind_ids, 1):
        r = rows[first_row_of_id[qid]]
        w.writerow({"blind_no": n, "row": first_row_of_id[qid] + 1, "id": qid,
                    "question": r["question"], "context": r["context"], "your_genre": ""})

# Summary (counts are per unique question).
counts = collections.Counter(GENRES[c] for c, _, _ in labels.values())
low = collections.Counter(GENRES[c] for c, conf, _ in labels.values() if conf == "L")
print(f"rows: {len(rows)}  unique questions: {len(uniq_ids)}  duplicate rows: {len(rows) - len(uniq_ids)}")
print(f"guide v1.0 rule changes applied: {n_changed}")
print(f"{'genre':<32}{'questions':>10}{'share':>8}{'low conf':>10}")
for g, n in counts.most_common():
    print(f"{g:<32}{n:>10}{n / len(uniq_ids):>8.1%}{low[g]:>10}")
print(f"{'total':<32}{len(uniq_ids):>10}{'':>8}{sum(low.values()):>10}")
print("of which fine label Sports:", sum(c == "SP" for c, _, _ in labels.values()))
print("same question text, different genre:", conflicts or "none")
print("rows whose QUESTION has Devanagari script:", devanagari_q or "none")
print("rows whose PASSAGE has Devanagari script (often a Hindi name in brackets):", len(devanagari_ctx))
print("wrote", out_main.relative_to(root), "and", out_blind.relative_to(root))
