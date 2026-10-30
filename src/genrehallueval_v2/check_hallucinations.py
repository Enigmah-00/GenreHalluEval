"""Check one batch of Claude-written hallucinated answers for the new v2 questions (rules of
prompts/hallucination_writing_guide_v1.md that a script can check).

Batch file (data/labels/genrehallueval_v2/hallucinations_claude/batch_NN.txt): `question_id|F|C|S|I` per line.
Errors (the batch is refused): unknown or repeated id, not 4 answers, an empty answer, an answer equal to the gold or
to another answer, a hedge word. Warnings (read by hand): an answer inside the gold or the gold inside an answer
(could still be correct), a different digit script from the gold, a C answer that is not in the passage.
Usage: python3 -I src/genrehallueval_v2/check_hallucinations.py <project_root> <batch file>
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

root, batch = Path(sys.argv[1]), Path(sys.argv[2])
N = lambda s: unicodedata.normalize("NFC", " ".join((s or "").split()))
qs = {r["question_id"]: r for r in csv.DictReader(open(root / "data/labels/genrehallueval_v2/new_questions_claude.csv",
                                                         encoding="utf-8"))}
HEDGE = ("সম্ভবত", "হয়তো", "সম্ভবতঃ", "মনে হয়", "বোধহয়")
bn_digit, en_digit = re.compile(r"[০-৯]"), re.compile(r"[0-9]")
errors, warnings, ids = [], [], set()
for n, line in enumerate(batch.read_text(encoding="utf-8").splitlines(), 1):
    if not line.strip() or line.startswith("#"):
        continue
    parts = [N(x) for x in line.split("|")]
    qid, ans = parts[0], parts[1:]
    if qid not in qs or qid in ids:
        errors.append(f"line {n}: id {qid} unknown or repeated")
        continue
    ids.add(qid)
    if len(ans) != 4 or not all(ans):
        errors.append(f"{qid}: needs 4 non-empty answers")
        continue
    gold, passage = N(qs[qid]["gold"]), N(qs[qid]["passage"])
    if gold in ans or len(set(ans)) < 4:
        errors.append(f"{qid}: an answer equals the gold or another answer")
    for t, a in zip("FCSI", ans):
        if any(h in a for h in HEDGE):
            errors.append(f"{qid} {t}: hedge word")
        if t != "S" and (a in gold or gold in a):
            warnings.append(f"{qid} {t}: '{a}' and the gold '{gold}' contain each other")
        if bool(bn_digit.search(gold)) != bool(bn_digit.search(a)) and (bn_digit.search(gold) or bn_digit.search(a)) \
                and not en_digit.search(a + gold):
            warnings.append(f"{qid} {t}: digits differ from the gold's form")
    if ans[1] not in passage:
        warnings.append(f"{qid} C: not a span of the passage (allowed only if the passage has no suitable span)")
print(f"{batch.name}: {len(ids)} questions checked; {len(errors)} errors, {len(warnings)} warnings")
print("\n".join(["ERROR " + e for e in errors] + ["warn  " + w for w in warnings]))
if errors:
    raise SystemExit(1)
