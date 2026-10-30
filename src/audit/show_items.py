"""Print question, gold answer and the passage text around the gold answer, for manual audit.

Usage: python3 -I src/audit/show_items.py <project_root> <uidx_from>:<uidx_to> [window_chars] [--only-not-in-passage]
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

root = Path(sys.argv[1])
a, b = map(int, sys.argv[2].split(":"))
win = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 90
only_missing = "--only-not-in-passage" in sys.argv
with open(root / "data/raw/benhallueval/banglahallueval_qa_1000.csv", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))
seen, uniq = set(), []
for i, r in enumerate(rows):
    if r["id"] not in seen:
        seen.add(r["id"])
        uniq.append((i + 1, r))
for k in range(a, min(b, len(uniq))):
    rown, r = uniq[k]
    ctx = " ".join(unicodedata.normalize("NFC", r["context"]).split())
    gold = " ".join(unicodedata.normalize("NFC", r["correct_answer"]).split())
    pos = ctx.find(gold) if gold else -1
    if only_missing and pos >= 0:
        continue
    snippet = ctx[max(0, pos - win): pos + len(gold) + win] if pos >= 0 else "[GOLD NOT IN PASSAGE] " + ctx[:2 * win]
    print(f"[{k}] row {rown} Q: {r['question'].strip()}\n   A: {gold}\n   P: {snippet}")
