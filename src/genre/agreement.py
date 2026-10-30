"""Agreement between the blind human genre sheet and Claude's labels, using the v1.0 genre names.

Usage: python3 -I src/genre/agreement.py <project_root> <blind_csv>

Reports (all joined on `id`, never on question text, which Excel can alter):
  1. blind vs Claude draft v0.2   - the clean number: labels made before anyone saw the blind sheet
  2. blind vs current v1.0 draft  - optimistic: the v1.0 rules were revised using this blind sheet
  3. blind vs final labels        - only once `verified_genre` is filled in (inflated if the same person
                                    did the blind sheet and the verification)
"""
import collections
import csv
import random
import sys
from pathlib import Path

root = Path(sys.argv[1])
blind_path = Path(sys.argv[2])
raw = root / "data/raw/benhallueval/banglahallueval_qa_1000.csv"
draft_v02 = root / "data/labels/genre_draft_claude.txt"
current = root / "data/processed/banglahallueval_qa_1000_with_genre.csv"
SEED, B = 2026, 2000
CODE = {"HP": "History, Politics & Education", "AC": "Arts, Culture & Sports", "SP": "Arts, Culture & Sports",
        "ST": "Science & Technology", "GP": "Geography & Places", "RE": "Religion", "OT": "Other"}
V1_NAME = {"History & Politics": "History, Politics & Education", "Arts & Culture": "Arts, Culture & Sports",
           "Sports": "Arts, Culture & Sports"}


def v1(name):
    name = name.strip()
    return V1_NAME.get(name, name)


def load(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[g] * cb[g] for g in set(ca) | set(cb)) / n ** 2
    return po, (po - pe) / (1 - pe)


def report(pairs, title):
    po, k = kappa(pairs)
    rng = random.Random(SEED)
    ks = sorted(kappa([pairs[rng.randrange(len(pairs))] for _ in pairs])[1] for _ in range(B))
    lo, hi = ks[int(0.025 * B)], ks[int(0.975 * B) - 1]
    print(f"\n== {title} (n={len(pairs)})")
    print(f"raw agreement {po:.1%} | Cohen's kappa {k:.3f} (95% range {lo:.3f} to {hi:.3f})")
    dis = collections.Counter((h, c) for h, c in pairs if h != c)
    for (h, c), n in dis.most_common(5):
        print(f"  {n} x human {h} -> {c}")


# Claude draft v0.2, keyed by id (labels are by unique-question index in first-appearance order).
seen, uniq_ids = set(), []
for r in load(raw):
    if r["id"] not in seen:
        seen.add(r["id"])
        uniq_ids.append(r["id"])
v02 = {}
for line in draft_v02.read_text(encoding="utf-8").splitlines():
    if line.strip() and not line.startswith("#"):
        idx, code, _ = line.split("|", 2)
        v02[uniq_ids[int(idx)]] = CODE[code]

blind = load(blind_path)
if "rule_applied" in blind[0]:
    n = sum(bool(r["rule_applied"]) for r in blind)
    print(f"NOTE: this blind file is rule-harmonized ({n} labels changed by rule), so none of the numbers"
          " below is a clean blind score. The clean score comes from the raw blind file.")
cur = {r["id"]: r for r in load(current)}
empty = [r["blind_no"] for r in blind if not r["your_genre"].strip()]
assert not empty, f"blind rows without a genre: {empty[:10]}"
assert all(r["id"] in cur and r["id"] in v02 for r in blind), "blind ids missing from label files"

report([(v1(r["your_genre"]), v02[r["id"]]) for r in blind], "1. blind human vs Claude draft v0.2 (clean)")
report([(v1(r["your_genre"]), cur[r["id"]]["genre_draft"]) for r in blind],
       "2. blind human vs Claude draft v1.0 (optimistic: rules revised on this sheet)")
if any(r["verified_genre"].strip() for r in cur.values()):
    final = lambda r: v1(r["verified_genre"]) if r["verified_genre"].strip() else r["genre_draft"]
    report([(v1(r["your_genre"]), final(cur[r["id"]])) for r in blind], "3. blind human vs final verified labels")
