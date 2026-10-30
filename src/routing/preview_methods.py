"""EXPLORATORY PREVIEW of routing methods A, C, E, F on BenHalluEval (not the locked analysis; the routing notebook
does that). Rules follow docs/refined-plan.md 2.1 and 2.5:

A  best single judge (lowest BHS on the training questions)
C  majority vote of all judges (ties -> A's verdict)
E  the best genre guesser (highest accuracy against our genres on the training questions) names the genre; the answer
   goes to the best judge for that genre (judge x human-genre table); cells under 50 questions fall back to A
F  own-genre routing: every judge names a genre; each judge's score is its BHS inside the genre it named itself; the
   answer goes to the judge with the best score for the genre it named; cells under 50 questions are not used; ties go
   to the better overall judge; if no cell is usable, A

Scored in-sample (choose and test on all questions: optimistic) and with 5-fold cross-validation by question (choose
on 4/5, test on 1/5). Paired 95% ranges re-sample questions.
Usage: python3 -I src/routing/preview_methods.py <root> [judges,to,leave,out]
"""
import csv
import json
import random
import sys
from pathlib import Path

root = Path(sys.argv[1])
NAME = {"History, Politics & Education": "HISTORY", "Arts, Culture & Sports": "ARTS", "Science & Technology": "SCIENCE",
        "Geography & Places": "GEOGRAPHY", "Religion": "RELIGION", "Other": "OTHER"}
PROMPT = {"context": "judge_v1", "no_context": "judge_noctx_v1"}
MIN_CELL = 50
items = [r for r in csv.DictReader(open(root / "data/final/benhallueval-qa-v1.3/items.csv", encoding="utf-8"))
         if r["include_main"] == "yes"]
qids = sorted({r["question_id"] for r in items})
by_q = {q: [] for q in qids}
for r in items:
    by_q[r["question_id"]].append(r)
human = {r["question_id"]: NAME[r["genre"]] for r in items}
EXCLUDE = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else set()   # optional: a smaller judge pool
models = sorted(p.parent.parent.name for p in (root / "results").glob("*/full/manifest.json")
                if p.parent.parent.name not in EXCLUDE)


def log(m, turn, pid):
    p = root / "runs" / f"benhallueval__{m}__{turn}__{pid}.jsonl"
    return {r["key"]: r["parsed"] for r in map(json.loads, p.read_text(encoding="utf-8").splitlines()) if r}


def qcounts(verdict_of):            # per question: correct, false alarms, hallucinated, misses
    out = {}
    for q in qids:
        a = [0, 0, 0, 0]
        for r in by_q[q]:
            v = verdict_of(r)
            if r["label"] == "0":
                a[0] += 1; a[1] += v != "no"
            else:
                a[2] += 1; a[3] += v != "yes"
        out[q] = a
    return out


def bhs(cnt, qs):
    s = [0, 0, 0, 0]
    for q in qs:
        for k in range(4):
            s[k] += cnt[q][k]
    return 50 * (s[1] / s[0] + s[3] / s[2]) if s[0] and s[2] else None


genre = {m: log(m, "genre", "genre_v1") for m in models}
results = []
for c in ("context", "no_context"):
    V = {m: log(m, "judge", PROMPT[c]) for m in models}
    per_judge = {m: qcounts(lambda r, m=m: V[m][r["item_id"]]) for m in models}

    def choose(train):
        """Learn A, E's table and best guesser, F's own-genre scores on the training questions."""
        overall = {m: bhs(per_judge[m], train) for m in models}
        A = min(overall, key=overall.get)
        guesser = max(models, key=lambda m: sum(genre[m][q] == human[q] for q in train))
        table = {}
        for g in NAME.values():
            qs = [q for q in train if human[q] == g]
            if len(qs) >= MIN_CELL:
                table[g] = min(models, key=lambda m: bhs(per_judge[m], qs))
        own = {}
        for m in models:
            for g in NAME.values():
                qs = [q for q in train if genre[m][q] == g]
                if len(qs) >= MIN_CELL:
                    own[(m, g)] = bhs(per_judge[m], qs)
        return A, overall, guesser, table, own

    def route(q, method, A, overall, guesser, table, own):
        if method == "A":
            return A
        if method == "E":
            return table.get(genre[guesser][q], A)
        if method == "F":
            cands = [(own[(m, genre[m][q])], overall[m], m) for m in models if (m, genre[m][q]) in own]
            return min(cands)[2] if cands else A
        raise ValueError(method)

    def predictions(train, test):
        A, overall, guesser, table, own = choose(train)
        pred, picked = {}, {"E": {}, "F": {}}
        for q in test:
            for meth in ("A", "E", "F"):
                j = route(q, meth, A, overall, guesser, table, own)
                if meth != "A":
                    picked[meth][j] = picked[meth].get(j, 0) + 1
                for r in by_q[q]:
                    pred[(meth, r["item_id"])] = V[j][r["item_id"]]
            for r in by_q[q]:                                    # C: vote of all judges, ties -> A
                ys = sum(V[m][r["item_id"]] == "yes" for m in models)
                ns = sum(V[m][r["item_id"]] == "no" for m in models)
                pred[("C", r["item_id"])] = "yes" if ys > ns else "no" if ns > ys else V[A][r["item_id"]]
        return pred, picked, A, guesser

    rng = random.Random(2026)
    order = qids[:]
    rng.shuffle(order)
    folds = [order[i::5] for i in range(5)]
    cv_pred, cv_picked = {}, {"E": {}, "F": {}}
    for k in range(5):
        test = folds[k]
        train = [q for i, f in enumerate(folds) if i != k for q in f]
        p, picked, _, _ = predictions(train, test)
        cv_pred.update(p)
        for meth in picked:
            for j, n in picked[meth].items():
                cv_picked[meth][j] = cv_picked[meth].get(j, 0) + n
    in_pred, in_picked, A_all, guesser_all = predictions(qids, qids)

    S = [[qids[rng.randrange(len(qids))] for _ in qids] for _ in range(1000)]
    for label, pred, picked in (("in-sample", in_pred, in_picked), ("5-fold", cv_pred, cv_picked)):
        cnt = {meth: qcounts(lambda r, meth=meth: pred[(meth, r["item_id"])]) for meth in "ACEF"}
        base = bhs(cnt["A"], qids)
        for meth in "ACEF":
            v = bhs(cnt[meth], qids)
            d = sorted(bhs(cnt[meth], s) - bhs(cnt["A"], s) for s in S) if meth != "A" else None
            results.append({"condition": c, "scoring": label, "method": meth, "BHS": f"{v:.2f}",
                            "vs_A": f"{v - base:+.2f}" if d else "–",
                            "range95": f"{d[25]:+.2f} to {d[974]:+.2f}" if d else "–",
                            "clearly": ("better" if d[974] < 0 else "worse" if d[25] > 0 else "no difference") if d else "–",
                            "judges_used": ", ".join(f"{j} {n}" for j, n in sorted(picked.get(meth, {}).items(), key=lambda x: -x[1]))
                            if meth in picked else ""})
    print(f"[{c}] in-sample A = {A_all}; best genre guesser = {guesser_all}")

cols = ["condition", "scoring", "method", "BHS", "vs_A", "range95", "clearly", "judges_used"]
print("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols))
for r in results:
    print("| " + " | ".join(str(r[k]) for k in cols) + " |")
out = root / ("results/routing_preview.csv" if not EXCLUDE else "results/routing_preview_without_top2.csv")
with open(out, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(results)
print("saved", out)
