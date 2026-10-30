"""Automatic checks on the BenHalluEval QA seed file (one row per unique question).

  - gold answer found verbatim in the passage? (TyDiQA-GoldP gold answers are spans of the passage)
  - question contains a time word (বর্তমান, সর্বশেষ, a year 2010-2029, ...): the answer may have changed since
  - question or passage contains Devanagari letters (not the danda, which Bangla shares)

Usage: python3 -I src/audit/auto_checks.py <project_root>   -> writes data/processed/audit_auto_checks.csv
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

root = Path(sys.argv[1])
raw = root / "data/raw/benhallueval/banglahallueval_qa_1000.csv"
out = root / "data/processed/audit_auto_checks.csv"
TIME = re.compile(r"বর্তমান|সর্বশেষ|এখন|সাম্প্রতিক|২০১[০-৯]|২০২[০-৯]")
DEVANAGARI = re.compile(r"[ऀ-ॣ०-ॿ]")


def norm(s):
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"[\s‌‍]+", " ", s)
    return re.sub(r"[\"'“”‘’।,.;:()\[\]{}!?\-]", "", s).strip().lower()


with open(raw, encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))
seen, out_rows = set(), []
for i, r in enumerate(rows):
    if r["id"] in seen:
        continue
    seen.add(r["id"])
    g, c = norm(r["correct_answer"]), norm(r["context"])
    out_rows.append({
        "uidx": len(out_rows), "row": i + 1, "id": r["id"],
        "gold_in_passage": "yes" if g and g in c else "no",
        "time_word": "yes" if TIME.search(r["question"]) else "no",
        "devanagari_question": "yes" if DEVANAGARI.search(r["question"]) else "no",
    })
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out_rows[0]))
    w.writeheader()
    w.writerows(out_rows)
n = len(out_rows)
print(f"unique questions: {n}")
for k in ["gold_in_passage", "time_word", "devanagari_question"]:
    print(f"{k}=yes: {sum(r[k] == 'yes' for r in out_rows)}")
print("wrote", out.relative_to(root))
