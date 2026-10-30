"""Agreement report for the GenreHalluEval v2 blind check (check_v1): two annotators vs each other and vs the design.

Reads the two annotators' returned sheets (kept unchanged as raw files), checks them against the blank sheets (same
rows, same ids, question / passage / answer text not edited), then reports:
- answers: Cohen's kappa between the annotators and of each annotator vs the design label (gold = correct, F/C/S/I =
  hallucinated), with a 95% range from a bootstrap that re-samples questions (2,000 draws, seed 2026); agreement with
  the design per answer type and per genre;
- genre: Cohen's kappa between the annotators and of each annotator vs Claude's draft genre, for the Claude-written
  questions and the kept v1.1 questions separately; low-confidence and question_ok counts.
A blank label is "not labelled" and is left out (and counted). An answer whose text the annotator edited is left out
for that annotator (its label belongs to a different text) and listed.

Writes <check_dir>/agreement_<tag>.md and <check_dir>/disagreements_<tag>.csv (every row where the two annotators, or an
annotator and the design, differ; for the discussion after both sheets are in).
Usage: python3 -I src/genrehallueval_v2/check_agreement.py <project_root> <returned_dir> <tag>
"""
import collections
import csv
import random
import sys
import unicodedata
from pathlib import Path

root, ret, tag = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
C = root / "data/labels/genrehallueval_v2/check_v1"
L = root / "data/labels/genrehallueval_v2"
WHO = {"annotator1_umme_zoayria_abedin": "Umme Zoayria Abedin (annotator 1)",
       "annotator2_md_saminul_amin": "Md Saminul Amin (annotator 2)"}
A1, A2 = list(WHO)
SEED, DRAWS = 2026, 2000


def load(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig")))


def norm(s):
    return unicodedata.normalize("NFC", s.strip())


def kappa(pairs):
    """Cohen's kappa for a list of (label_a, label_b)."""
    n = len(pairs)
    if not n:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def boot(pairs_by_q, stat, rng):
    """95% range of stat over a bootstrap that re-samples questions."""
    qs = sorted(pairs_by_q)
    vals = []
    for _ in range(DRAWS):
        s = [p for q in (rng.choice(qs) for _ in qs) for p in pairs_by_q[q]]
        v = stat(s)
        if v == v:
            vals.append(v)
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def fmt(pairs_by_q, rng):
    pairs = [p for v in pairs_by_q.values() for p in v]
    if not pairs:
        return "n/a", "n/a", "n/a", 0
    lo, hi = boot(pairs_by_q, kappa, rng)
    agree = sum(a == b for a, b in pairs) / len(pairs)
    return f"{kappa(pairs):.3f}", f"{lo:.3f} to {hi:.3f}", f"{agree:.1%}", len(pairs)


rng = random.Random(SEED)
out, problems, disagree = [], [], []

# ---------- load and check ----------
sheets = {}
for kind, idc, txt, fill in [("genre", "check_id", ["question", "passage"], ["genre", "confidence", "question_ok"]),
                             ("answers", "answer_id", ["question", "passage", "answer"], ["label"])]:
    blank = load(C / f"{A1}__{kind}.csv")
    for who in WHO:
        got = load(ret / f"{who}__{kind}.csv")
        if len(got) != len(blank) or any(b[idc] != g[idc] for b, g in zip(blank, got)):
            raise SystemExit(f"{who} {kind}: rows or ids differ from the blank sheet")
        edited = {g[idc] for b, g in zip(blank, got) if any(norm(b[t]) != norm(g[t]) for t in txt)}
        for b, g in zip(blank, got):
            if g[idc] in edited:
                problems.append(f"{WHO[who]}, {kind} {g[idc]}: text edited ("
                                + "; ".join(f"{t}: '{b[t]}' -> '{g[t]}'" for t in txt if norm(b[t]) != norm(g[t]))
                                + f"); label '{g.get('label', g.get('genre'))}' left out")
        blanks = [g[idc] for g in got if any(not g[f].strip() for f in fill)]
        if blanks:
            problems.append(f"{WHO[who]}, {kind}: {len(blanks)} rows not filled ({blanks[0]}..{blanks[-1]})")
        sheets[who, kind] = {g[idc]: {f: g[f].strip().lower() for f in fill + ["note"]} for g in got
                             if g[idc] not in edited}

akey = {r["answer_id"]: r for r in load(C / "KEY_do_not_share__answers.csv")}
gkey = {r["check_id"]: r for r in load(C / "KEY_do_not_share__genre.csv")}
genre_of = {r["question_id"]: r["genre"] for r in load(L / "new_questions_claude.csv")}
ans_text = {r["answer_id"]: r for r in load(C / f"{A1}__answers.csv")}
LABELS = {"correct", "hallucinated", "unsure"}
for who in WHO:
    bad = [k for k, v in sheets[who, "answers"].items() if v["label"] and v["label"] not in LABELS]
    if bad:
        problems.append(f"{WHO[who]}: {len(bad)} answer labels not in {sorted(LABELS)} (left out)")
    for k in bad:
        sheets[who, "answers"][k]["label"] = ""


def lab(who, aid):
    v = sheets[who, "answers"].get(aid)
    return v["label"] if v and v["label"] in ("correct", "hallucinated") else None


out += [f"# GenreHalluEval v2 blind check: agreement report ({tag})", "",
        f"Made by `src/genrehallueval_v2/check_agreement.py` from the raw returned sheets in `{ret.relative_to(root)}/`. "
        "Kappa = Cohen's kappa; the 95% range comes from a bootstrap that re-samples questions "
        f"({DRAWS:,} draws, seed {SEED}). Design label: the gold answer is correct, the four written answers (F/C/S/I) "
        "are hallucinated.", ""]
out += ["## Problems in the returned sheets", ""] + ([f"- {p}" for p in problems] or ["- none"]) + [""]

# ---------- answers ----------
out += ["## Answer labels (194 Claude-written questions x 5 answers)", ""]
cov = {who: sum(lab(who, a) is not None for a in akey) for who in WHO}
unsure = {who: sum(1 for v in sheets[who, "answers"].values() if v["label"] == "unsure") for who in WHO}
for who in WHO:
    out.append(f"- {WHO[who]}: {cov[who]} of {len(akey)} answers labelled correct/hallucinated, {unsure[who]} unsure.")
out.append("")
out += ["| Pair | Answers | Agreement | Kappa | 95% range |", "|---|---|---|---|---|"]


def by_q(fn):
    d = collections.defaultdict(list)
    for aid, k in akey.items():
        p = fn(aid, k)
        if p:
            d[k["question_id"]].append(p)
    return d


pair_sets = {
    "annotator 1 vs annotator 2": by_q(lambda a, k: (lab(A1, a), lab(A2, a)) if lab(A1, a) and lab(A2, a) else None),
    "annotator 1 vs design": by_q(lambda a, k: (lab(A1, a), k["design_label"]) if lab(A1, a) else None),
    "annotator 2 vs design": by_q(lambda a, k: (lab(A2, a), k["design_label"]) if lab(A2, a) else None),
    "annotator 2 vs design, same answers as annotator 1": by_q(
        lambda a, k: (lab(A2, a), k["design_label"]) if lab(A1, a) and lab(A2, a) else None),
}
for name, d in pair_sets.items():
    kp, rg, ag, n = fmt(d, rng)
    out.append(f"| {name} | {n} | {ag} | {kp} | {rg} |")
out.append("")

out += ["Share of answers given the design label, per answer type:", "",
        "| Answer type | Annotator 1 | Annotator 2 |", "|---|---|---|"]
for t in ["gold", "F", "C", "S", "I"]:
    cells = []
    for who in WHO:
        xs = [lab(who, a) == k["design_label"] for a, k in akey.items() if k["answer_type"] == t and lab(who, a)]
        cells.append(f"{sum(xs)}/{len(xs)} ({sum(xs) / len(xs):.1%})" if xs else "n/a")
    out.append(f"| {t} | {cells[0]} | {cells[1]} |")
out.append("")

out += ["Per genre (agreement with the design label; kappa between the annotators):", "",
        "| Genre | Questions | Annotator 1 vs design | Annotator 2 vs design | Annotator 1 vs 2 (kappa) |",
        "|---|---|---|---|---|"]
for g in sorted(set(genre_of[k["question_id"]] for k in akey.values())):
    ids = [a for a, k in akey.items() if genre_of[k["question_id"]] == g]
    cells = []
    for who in WHO:
        xs = [lab(who, a) == akey[a]["design_label"] for a in ids if lab(who, a)]
        cells.append(f"{sum(xs)}/{len(xs)}" if xs else "n/a")
    pairs = [(lab(A1, a), lab(A2, a)) for a in ids if lab(A1, a) and lab(A2, a)]
    nq = len({akey[a]["question_id"] for a in ids})
    out.append(f"| {g} | {nq} | {cells[0]} | {cells[1]} | {kappa(pairs):.3f} ({len(pairs)} answers) |"
               if pairs else f"| {g} | {nq} | {cells[0]} | {cells[1]} | n/a |")
out.append("")

for who in WHO:
    per_q = collections.defaultdict(list)
    for a, k in akey.items():
        if lab(who, a):
            per_q[k["question_id"]].append(lab(who, a))
    full = [v for v in per_q.values() if len(v) == 5]
    out.append(f"- {WHO[who]}: number of answers marked correct per fully labelled question: "
               f"{dict(sorted(collections.Counter(v.count('correct') for v in full).items()))} "
               f"({len(full)} questions).")
out += ["", "Every question has exactly one correct answer by design. An annotator who marks exactly one per question "
        "may have guessed the design, so agreement with the design is an upper bound (as for Mahdi's BenHalluEval check).",
        ""]

for a, k in akey.items():
    l1, l2 = lab(A1, a), lab(A2, a)
    if (l1 and l2 and l1 != l2) or (l1 and l1 != k["design_label"]) or (l2 and l2 != k["design_label"]):
        r = ans_text[a]
        disagree.append(dict(sheet="answers", id=a, question_id=k["question_id"], genre=genre_of[k["question_id"]],
                             question=r["question"], answer=r["answer"], answer_type=k["answer_type"],
                             design=k["design_label"], annotator1=l1 or "", annotator2=l2 or ""))

# ---------- genre ----------
out += ["## Genre labels (240 questions)", ""]
CODES = {"HISTORY", "POLITICS", "EDUCATION", "ARTS", "CULTURE", "SPORTS", "SCIENCE", "TECHNOLOGY", "GEOGRAPHY",
         "PLACES", "RELIGION", "GRAMMAR", "OTHER"}


def gl(who, cid):
    v = sheets[who, "genre"].get(cid)
    return v["genre"].upper() if v and v["genre"].upper() in CODES else None


badg = {who: [c for c in gkey if sheets[who, "genre"].get(c) and gl(who, c) is None] for who in WHO}
for who in WHO:
    if badg[who]:
        out.append(f"- {WHO[who]}: {len(badg[who])} genre cells not a valid code (left out).")
out += ["| Questions | Pair | Questions | Agreement | Kappa | 95% range |", "|---|---|---|---|---|---|"]
for src, name in [("new", "Claude-written"), ("v1.1", "kept v1.1"), (None, "all")]:
    ids = [c for c, k in gkey.items() if src is None or k["source"] == src]
    for pname, f in [("annotator 1 vs 2", lambda c: (gl(A1, c), gl(A2, c))),
                     ("annotator 1 vs draft", lambda c: (gl(A1, c), gkey[c]["draft_genre"])),
                     ("annotator 2 vs draft", lambda c: (gl(A2, c), gkey[c]["draft_genre"]))]:
        d = {c: [f(c)] for c in ids if all(f(c))}
        kp, rg, ag, n = fmt(d, rng)
        out.append(f"| {name} | {pname} | {n} | {ag} | {kp} | {rg} |")
out.append("")
for who in WHO:
    v = sheets[who, "genre"].values()
    out.append(f"- {WHO[who]}: confidence low {sum(x['confidence'] == 'low' for x in v)}, question_ok no "
               f"{sum(x['question_ok'] == 'no' for x in v)}, notes {sum(bool(x['note']) for x in v)}.")
out.append("")
conf = collections.Counter()
for c, k in gkey.items():
    g1, g2, dg = gl(A1, c), gl(A2, c), k["draft_genre"]
    if g1 != g2 or g1 != dg or g2 != dg:
        conf[(dg, g1, g2)] += 1
        disagree.append(dict(sheet="genre", id=c, question_id=k["question_id"], genre=dg, question="", answer="",
                             answer_type=k["source"], design=dg, annotator1=g1 or "", annotator2=g2 or ""))
out += ["Genre disagreements (draft genre, annotator 1, annotator 2: count):", ""]
out += [f"- {d} / {a} / {b}: {n}" for (d, a, b), n in conf.most_common()] or ["- none"]
out.append("")

qtext = {r["check_id"]: r["question"] for r in load(C / f"{A1}__genre.csv")}
for r in disagree:
    if r["sheet"] == "genre":
        r["question"] = qtext[r["id"]]
(C / f"agreement_{tag}.md").write_text("\n".join(out) + "\n", encoding="utf-8")
with open(C / f"disagreements_{tag}.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(disagree[0]) if disagree else ["sheet"])
    w.writeheader()
    w.writerows(disagree)
print("\n".join(out))
print(f"{len(disagree)} disagreement rows written")
