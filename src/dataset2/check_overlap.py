"""Check Dataset 2 questions for overlap with BenHalluEval (run it on every new batch and on the final seeds).

Three checks per row, against all BenHalluEval files we have (qa_1000 passages, the 2,509-question QA file and the
v1.3 package):
  1. same text:     share of the row's passage 30-character pieces that also occur in one BenHalluEval passage;
  2. same article:  share of the passage's rare words (in <= 30 BenHalluEval passages) found in one BenHalluEval
                    passage; this catches a Wikipedia lead that was lightly reworded since TyDiQA copied it;
  3. same fact:     the gold answers match (loosely) and the two questions share a rare word.
Flags: same text >= 0.10, same article >= 0.45, or any same-fact match. A flag is a reason to look, not a verdict:
same-fact matches on generic words (e.g. "কততম" -> "তৃতীয়") are false alarms.

Input: a CSV (or a TSV with no header, columns passage | source | question | gold) with the columns
Context/Question/Correct Answer (sheet) or passage/question/gold (seeds).
Usage: python3 -I src/dataset2/check_overlap.py <project_root> <file> [report.md]
"""
import collections
import csv
import re
import sys
import unicodedata
from pathlib import Path

root, path = Path(sys.argv[1]), Path(sys.argv[2])
report = Path(sys.argv[3]) if len(sys.argv) > 3 else None
SAME_TEXT, SAME_ARTICLE = 0.10, 0.45


def N(t):
    return unicodedata.normalize("NFC", " ".join((t or "").split()))


def load_rows(p):
    if p.suffix == ".tsv":
        with open(p, encoding="utf-8", newline="") as f:
            return [dict(passage=r[0], question=r[2], gold=r[3]) for r in csv.reader(f, delimiter="\t") if any(c.strip() for c in r)]
    with open(p, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    key = {"passage": ("passage", "Context"), "question": ("question", "Question"), "gold": ("gold", "Correct Answer")}
    return [{k: next(r[c] for c in cols if c in r) for k, cols in key.items()} | {"id": r.get("question_id", "")} for r in rows]


def grams(t, n=30, step=3):
    return {t[i:i + n] for i in range(0, max(1, len(t) - n + 1), step)}


def words(t, n=3):
    return {w for w in re.findall(r"[ঀ-৿A-Za-z0-9]+", N(t)) if len(w) >= n}


def norm_ans(a):
    a = re.sub(r"[\"'“”‘’(),।?.:;–-]", " ", N(a))
    a = re.sub(r"(সালে|সালের|সাল|খ্রিস্টাব্দে|খ্রিস্টাব্দ|তিথিতে|ভাষায়|মহাদেশে|শহরে|জেলায়|দেশে)(?=\s|$)", " ", a)
    return " ".join(w.rstrip("েরও") if len(w) > 3 else w for w in a.split())


bh_ctx, bh_q = {}, []
with open(root / "data/raw/benhallueval/banglahallueval_qa_1000.csv", encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        bh_ctx.setdefault(N(r["context"]), r["id"])
        bh_q.append(("qa1000", r["id"], N(r["question"]), N(r["correct_answer"])))
with open(root / "data/raw/benhallueval/banglahallueval_qa_dataset.csv", encoding="utf-8-sig", newline="") as f:
    bh_q += [("qa2509", r["id"], N(r["question"]), N(r["correct_answer"])) for r in csv.DictReader(f)]
with open(root / "data/final/benhallueval-qa-v1.3/items.csv", encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        bh_ctx.setdefault(N(r["context"]), r["question_id"])
        if r["answer_type"] == "gold":
            bh_q.append(("v1.3", r["question_id"], N(r["question"]), N(r["answer"])))
ctx = list(bh_ctx)
ctx_grams = [grams(c) for c in ctx]
ctx_words = [words(c) for c in ctx]
df_ctx = collections.Counter(w for ws in ctx_words for w in ws)
df_q = collections.Counter(w for *_, q, _ in bh_q for w in words(q, 4))

rows = load_rows(path)
flags = []
for n, r in enumerate(rows, 1):
    p, q, a = N(r["passage"]), N(r["question"]), N(r["gold"])
    g = grams(p)
    j = max(range(len(ctx)), key=lambda k: len(g & ctx_grams[k]))
    same_text = len(g & ctx_grams[j]) / max(1, len(g))
    rare = {w for w in words(p) if df_ctx[w] <= 30}
    k = max(range(len(ctx)), key=lambda k: len(rare & ctx_words[k])) if rare else 0
    same_article = len(rare & ctx_words[k]) / len(rare) if len(rare) >= 5 else 0.0
    na, qw, facts = norm_ans(a), words(q, 4), []
    for src, bid, bq, ba in bh_q:
        nb = norm_ans(ba)
        same = na and nb and (na == nb or (min(len(na), len(nb)) >= 3 and (na in nb or nb in na)))
        if same and [w for w in qw & words(bq, 4) if df_q[w] <= 40]:
            facts.append(f"{src} {bid}: {bq} -> {ba}")
    why = []
    if same_text >= SAME_TEXT:
        why.append(f"same text {same_text:.0%} ({bh_ctx[ctx[j]]})")
    if same_article >= SAME_ARTICLE:
        why.append(f"same article {same_article:.0%} ({bh_ctx[ctx[k]]})")
    why += [f"same fact? {x}" for x in dict.fromkeys(facts)]
    if why:
        flags.append((n, r.get("id", ""), q, a, why))

lines = [f"# Overlap check: {path.name}", "", f"{len(rows)} rows checked against {len(ctx)} BenHalluEval passages and "
         f"{len(bh_q)} BenHalluEval questions. {len(flags)} rows flagged (same text >= {SAME_TEXT:.0%}, same article >= "
         f"{SAME_ARTICLE:.0%}, or a possible same fact).", ""]
for n, qid, q, a, why in flags:
    lines.append(f"- row {n} {qid}: {q} -> {a}")
    lines += [f"  - {w}" for w in why]
text = "\n".join(lines) + "\n"
print(text)
if report:
    report.write_text(text, encoding="utf-8")
