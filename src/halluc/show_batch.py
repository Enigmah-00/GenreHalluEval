"""Print a batch of seeds for writing hallucinated answers (guide: prompts/hallucination_writing_guide_v1.md).

Shows the final question, the final gold, the passage (whole if short, else a window around the gold) and,
for UPD seeds, the old gold. EXCL seeds are skipped (they get no hallucinated answers).

Usage: python3 -I src/halluc/show_batch.py <project_root> <first_uidx> <last_uidx> [window]
"""
import csv
import sys
from pathlib import Path

root, first, last = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
window = int(sys.argv[4]) if len(sys.argv) > 4 else 450
with open(root / "data/final/benhallueval_qa_seeds_v1.1.csv", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

for k in range(first, min(last, len(rows) - 1) + 1):
    r = rows[k]
    if r["audit_status"] == "EXCL":
        continue
    c, a = " ".join(r["context"].split()), r["correct_answer"]
    if len(c) > 2 * window + 100:
        p = c.find(a)
        lo, hi = max(0, p - window), min(len(c), p + len(a) + window)
        c = ("…" if lo else "") + c[lo:hi] + ("…" if hi < len(c) else "")
    old = f" | OLD: {r['correct_answer_original']}" if r["audit_status"] == "UPD" else ""
    print(f"#{k} [{r['audit_status']}] Q: {r['question']} | A: {a}{old}\nP: {c}\n")
