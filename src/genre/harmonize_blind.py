"""Apply two guide v1.0 rules, decided by Mahdi on 2026-10-13, to his blind 200 labels mechanically.

This writes a NEW file and never touches the original blind sheet. The result is "rule-harmonized", not blind:
report its agreement only next to the clean blind number (kappa 0.806 against Claude draft v0.2).

Rules applied:
  - Schools, colleges, universities, libraries -> History, Politics & Education
    (questions listed as education changes in data/labels/genre_rule_changes_v1.txt)
  - When a place/building was built, opened or renamed, or who designed it -> Geography & Places
    (the blind questions below; found by listing blind History labels where Claude said Geography)

Optional third rule (--word-rule), also decided by Mahdi: the meaning/origin of a word -> the field of the word.

Usage: python3 -I src/genre/harmonize_blind.py <project_root> [--word-rule]
"""
import csv
import sys
from pathlib import Path

root = Path(sys.argv[1])
raw = root / "data/raw/benhallueval/banglahallueval_qa_1000.csv"
changes = root / "data/labels/genre_rule_changes_v1.txt"
blind_in = root / "data/labels/genre_blind200_human_mahdi_raw.csv"
blind_out = root / "data/labels/genre_blind200_human_mahdi_v1rules.csv"
HPE, GP = "History, Politics & Education", "Geography & Places"
BUILT_OPENED_ROWS = {"302", "552", "617", "827"}  # Nabanna opening, Rabindra Setu designer, Guwahati old name, Kolkata metro opening
# Word meaning/origin questions in the blind 200 whose blind label differs from the field of the word.
WORD_ORIGIN_ROWS = {"909": "Religion",                        # পাপ শব্দটির উৎপত্তি
                    "452": "Religion",                        # জৈন শব্দটি কোন শব্দ থেকে এসেছে
                    "474": "Science & Technology",            # আত্মহত্যা শব্দটির উৎপত্তি
                    "736": HPE,                               # জমিদার শব্দের অর্থ
                    "495": "Arts, Culture & Sports"}          # সমাস শব্দটির অর্থ (grammar)
word_rule = "--word-rule" in sys.argv[2:]
if word_rule:
    blind_out = blind_out.with_name(blind_out.stem + "_wordrule.csv")


def load(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


seen, uniq_ids = set(), []
for r in load(raw):
    if r["id"] not in seen:
        seen.add(r["id"])
        uniq_ids.append(r["id"])
edu_ids = set()
for line in changes.read_text(encoding="utf-8").splitlines():
    if line.strip() and not line.startswith("#"):
        idx, _, new, _, reason = line.split("|")
        if new == "HP" and ("education" in reason or "library" in reason or "university" in reason):
            edu_ids.add(uniq_ids[int(idx)])

blind = load(blind_in)
out = []
for r in blind:
    orig = r["your_genre"].strip()
    new, why = orig, ""
    if r["id"] in edu_ids and orig != "History & Politics":
        new, why = HPE, "schools/colleges/universities/libraries rule"
    elif r["row"] in BUILT_OPENED_ROWS and orig != GP:
        new, why = GP, "built/opened/renamed/designed rule"
    elif word_rule and r["row"] in WORD_ORIGIN_ROWS:
        new, why = WORD_ORIGIN_ROWS[r["row"]], "word meaning/origin rule"
    out.append({**r, "your_genre": new, "original_genre": orig, "rule_applied": why})

with open(blind_out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=[*blind[0].keys(), "original_genre", "rule_applied"])
    w.writeheader()
    w.writerows(out)
for r in out:
    if r["rule_applied"]:
        print(f"row {r['row']:>4}: {r['original_genre']} -> {r['your_genre']} ({r['rule_applied']})")
print(f"changed {sum(bool(r['rule_applied']) for r in out)} of {len(out)}; wrote {blind_out.relative_to(root)}")
