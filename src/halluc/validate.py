"""Check the hallucinated answers: data/labels/hallucinations_claude/batch_*.txt, then revisions_v1.2.txt and
revisions_v1.3.txt on top (a later file replaces a seed's line).

Checks: format (uidx|F|C|S|I); every main seed covered; no empty answer; the 4 answers differ from each other and
from the gold; F/C/I answers do not contain the gold; no Devanagari; Latin letters only if the gold has them;
and no "more than X" answer that is technically true (gold "more than 269", answer "more than 120").
Lines for seeds that were dropped later (EXCL in the current seeds) are counted as retired, not as errors.
Prints problems; exit code 1 if any hard error.

Usage: python3 -I src/halluc/validate.py <project_root> [--partial]
  --partial: do not fail on seeds that have no answers yet (while writing is in progress)
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

root = Path(sys.argv[1])
partial = "--partial" in sys.argv[2:]
HDIR = root / "data/labels/hallucinations_claude"
DEVANAGARI = re.compile(r"[ऀ-ॣ०-ॿ]")
LATIN = re.compile(r"[A-Za-z]")
MORE = re.compile(r"(বেশি|বেশী|অধিক|ঊর্ধ্বে|অন্তত)")
BN = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
TYPES = ["F", "C", "S", "I"]


def norm(t):
    t = unicodedata.normalize("NFC", t)
    t = re.sub(r"[\s,।.;:'\"“”‘’()\-–—]+", " ", t)
    return " ".join(t.split()).lower()


def number(t):
    t = t.translate(BN).replace(",", "")
    m = re.search(r"\d+(\.\d+)?", t)
    if not m:
        return None
    v = float(m.group())
    for word, scale in (("হাজার", 1e3), ("লক্ষ", 1e5), ("লাখ", 1e5), ("কোটি", 1e7), ("মিলিয়ন", 1e6)):
        if word in t:
            v *= scale
    return v


def read_lines(path):
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip() and not line.startswith("#"):
            yield f"{path.name}:{n}", line


with open(root / "data/final/benhallueval_qa_seeds_v1.3.csv", encoding="utf-8", newline="") as f:
    seeds = list(csv.DictReader(f))
need = {k for k, r in enumerate(seeds) if r["include_main"] == "yes"}

errors, warns, seen, retired = [], [], {}, set()
sources = sorted(HDIR.glob("batch_*.txt")) + [HDIR / "revisions_v1.2.txt", HDIR / "revisions_v1.3.txt"]
for p in sources:
    revision = p.name.startswith("revisions")
    in_file = set()
    for where, line in read_lines(p):
        parts = line.split("|")
        if len(parts) != 5 or not parts[0].strip().isdigit():
            errors.append(f"{where}: bad format: {line[:60]}")
            continue
        k = int(parts[0])
        if k in in_file or (k in seen and not revision):
            errors.append(f"{where}: uidx {k} given twice")
        in_file.add(k)
        seen[k] = (where, [a.strip() for a in parts[1:]])
for k in list(seen):
    if k not in need:
        retired.add(k)
        del seen[k]

for k, (where, ans) in sorted(seen.items()):
    gold = seeds[k]["correct_answer"]
    g = norm(gold)
    if any(not a for a in ans):
        errors.append(f"{where}: empty answer")
    normed = [norm(a) for a in ans]
    if len(set(normed)) < 4:
        errors.append(f"{where}: duplicate answers")
    for t, a, na in zip(TYPES, ans, normed):
        if na == g:
            errors.append(f"{where}: {t} equals the gold")
        elif t != "S" and g and g in na:
            warns.append(f"{where}: {t} contains the gold: {a}")
        if DEVANAGARI.search(a):
            errors.append(f"{where}: {t} has Devanagari")
        if LATIN.search(a) and not LATIN.search(gold):
            warns.append(f"{where}: {t} has Latin letters but the gold does not: {a}")
        gv, av = number(gold), number(a)
        if t != "S" and MORE.search(gold) and MORE.search(a) and gv and av and av < gv:
            errors.append(f"{where}: {t} '{a}' is technically true when the gold is '{gold}'")

missing = sorted(need - set(seen))
if missing and not partial:
    errors.append(f"{len(missing)} seeds have no hallucinated answers, e.g. {missing[:10]}")
print(f"seeds covered: {len(seen)} / {len(need)}; answers: {4 * len(seen)}; "
      f"retired (seed dropped later): {len(retired)}")
for w in warns:
    print("WARN ", w)
for e in errors:
    print("ERROR", e)
sys.exit(1 if errors else 0)
