"""Exploratory: the Dataset 2 experiment repeated inside BenHalluEval-QA v1.3, with no change of dataset.

The 920 questions are split in two halves, stratified by our genre (seed 2026): "split 1" plays Dataset 1 (every choice
is learned on it with the lock rules: pool, A, best genre guesser, judge x genre table, own-genre cells, route R) and
"split 2" plays Dataset 2 (test only). Then R vs A per condition, paired bootstrap over questions (10,000, seed 2026),
Holm over the 2 tests; D, E, F vs A exploratory. Everything comes from the saved BenHalluEval runs (every pool judge
judged every answer in both conditions; every LLM named the genre of every question), so no model is called.
Also: the same direction with cells of 25+ questions (a half has half the questions), and 200 more random splits
(point estimates only) to show how much one split can vary.

Usage: python3 -I src/routing/split_experiment.py <project_root>
Writes results/split_experiment/split_experiment.md
"""
import collections
import csv
import json
import random
import sys
from pathlib import Path

root = Path(sys.argv[1])
NAME = {"History, Politics & Education": "HISTORY", "Arts, Culture & Sports": "ARTS", "Science & Technology": "SCIENCE",
        "Geography & Places": "GEOGRAPHY", "Religion": "RELIGION", "Other": "OTHER"}
GENRES = list(NAME.values())
PROMPT = {"genre": "genre_v1", "context": "judge_v1", "no_context": "judge_noctx_v1"}
CONDS = ("context", "no_context")
SEED, B, ALPHA, REPEATS = 2026, 10_000, 0.05, 200
PKG = root / "data/final/benhallueval-qa-v1.3"
items = [r for r in csv.DictReader(open(PKG / "items.csv", encoding="utf-8")) if r["include_main"] == "yes"]
by_q = collections.defaultdict(list)
for r in items:
    by_q[r["question_id"]].append(r)
QIDS = sorted(by_q)
human = {r["question_id"]: NAME[r["genre"]] for r in items}
pool = json.load(open(root / "results/lock/lock_v2.json", encoding="utf-8"))["pools"]["dataset2_pool"]


def log(m, turn, pid):
    recs = [json.loads(l) for l in open(root / "runs" / f"benhallueval__{m}__{turn}__{pid}.jsonl", encoding="utf-8") if l.strip()]
    assert {r["dataset"] for r in recs} == {"benhallueval"}
    return {r["key"]: r["parsed"] for r in recs}


genre = {m: log(m, "genre", PROMPT["genre"]) for m in pool}
verdict = {c: {m: log(m, "judge", PROMPT[c]) for m in pool} for c in CONDS}
# per question and judge: [correct answers, false alarms, hallucinated answers, misses]
CNT = {c: {m: {q: [sum(r["label"] == "0" for r in by_q[q]),
                   sum(r["label"] == "0" and verdict[c][m][r["item_id"]] != "no" for r in by_q[q]),
                   sum(r["label"] == "1" for r in by_q[q]),
                   sum(r["label"] == "1" and verdict[c][m][r["item_id"]] != "yes" for r in by_q[q])] for q in QIDS}
           for m in pool} for c in CONDS}


def bhs(counts):
    s = [sum(x[k] for x in counts) for k in range(4)]
    return 50 * (s[1] / s[0] + s[3] / s[2]) if s[0] and s[2] else None


def learn(train, min_cell):
    """The lock rules (make_lock.py, make_lock_v2.py), on the training questions only."""
    out = {}
    for c in CONDS:
        ov = {m: round(bhs([CNT[c][m][q] for q in train]), 2) for m in pool}
        A = min(pool, key=lambda m: (ov[m], m))
        acc = {m: sum(genre[m][q] == human[q] for q in train) for m in pool}
        guesser = max(pool, key=lambda m: (acc[m], -ov[m]))
        table = {}
        for g in GENRES:
            qs = [q for q in train if human[q] == g]
            if len(qs) >= min_cell:
                best = min(pool, key=lambda m: (bhs([CNT[c][m][q] for q in qs]), ov[m]))
                table[g] = (best, round(bhs([CNT[c][best][q] for q in qs]), 2))
        own = {}
        for m in pool:
            for g in GENRES:
                qs = [q for q in train if genre[m][q] == g]
                if len(qs) >= min_cell:
                    own[(m, g)] = round(bhs([CNT[c][m][q] for q in qs]), 4)
        out[c] = dict(A=A, ov=ov, guesser=guesser, table=table, own=own, acc=acc)
    return out


def route(L, c, q):
    """Judge per method for one test question (all its answers go to the same judge)."""
    x = L[c]
    A, tab = x["A"], x["table"]
    g = genre[x["guesser"]][q]
    own = [(x["own"][(m, genre[m][q])], x["ov"][m], m) for m in pool if (m, genre[m][q]) in x["own"]]
    ours = (tab[g][1], x["ov"][tab[g][0]], tab[g][0]) if g in tab else (x["ov"][A], x["ov"][A], A)
    return {"A": A, "D": tab[human[q]][0] if human[q] in tab else A, "E": tab[g][0] if g in tab else A,
            "F": min(own)[2] if own else A, "R": min(own + [ours])[2]}


def compare(c, routes, test, m1, m2):
    a = {q: CNT[c][routes[q][m1]][q] for q in test}
    b = {q: CNT[c][routes[q][m2]][q] for q in test}
    base = bhs([a[q] for q in test]) - bhs([b[q] for q in test])
    rng, diffs = random.Random(SEED), []
    for _ in range(B):
        s = [test[rng.randrange(len(test))] for _ in test]
        diffs.append(bhs([a[q] for q in s]) - bhs([b[q] for q in s]))
    diffs.sort()
    p = min(1.0, 2 * min(sum(d <= 0 for d in diffs), sum(d >= 0 for d in diffs)) / B)
    return dict(diff=base, lo=diffs[int(0.025 * B)], hi=diffs[int(0.975 * B) - 1], p=p)


def split(seed):
    rng, s1, s2 = random.Random(seed), [], []
    for g in GENRES:
        qs = sorted(q for q in QIDS if human[q] == g)
        rng.shuffle(qs)
        s1 += qs[:len(qs) // 2]
        s2 += qs[len(qs) // 2:]
    return sorted(s1), sorted(s2)


def run(train, test, min_cell, full):
    L = learn(train, min_cell)
    res = {}
    for c in CONDS:
        routes = {q: route(L, c, q) for q in test}
        score = {m: bhs([CNT[c][routes[q][m]][q] for q in test]) for m in "ARDEF"}
        used = {m: collections.Counter(routes[q][m] for q in test) for m in "RDEF"}
        tests = {m: compare(c, routes, test, m, "A") for m in "RDEF"} if full else None
        res[c] = dict(L=L[c], score=score, used=used, tests=tests)
    return res


s1, s2 = split(SEED)
main = run(s1, s2, 50, True)
small = run(s1, s2, 25, True)
rows = [main[c]["tests"]["R"] | {"c": c} for c in CONDS]
order = sorted(range(2), key=lambda k: rows[k]["p"])
running = 0.0
for rank, k in enumerate(order):
    running = max(running, min(1.0, (2 - rank) * rows[k]["p"]))
    rows[k]["holm"] = running

rep = {c: {m: [] for m in "RDEF"} for c in CONDS}
for i in range(REPEATS):
    a, b = split(SEED + 1 + i)
    for tr, te in ((a, b), (b, a)):
        r = run(tr, te, 50, False)
        for c in CONDS:
            for m in "RDEF":
                rep[c][m].append(r[c]["score"][m] - r[c]["score"]["A"])

CN = {"context": "with passage", "no_context": "without passage"}
md = ["# Split experiment inside BenHalluEval (exploratory)", "",
      "Made by `src/routing/split_experiment.py` from the saved BenHalluEval-QA v1.3 runs (no new model calls). The 920",
      f"questions are split in two halves, stratified by our genre (seed {SEED}): split 1 ({len(s1)} questions) plays",
      f"Dataset 1, split 2 ({len(s2)} questions) plays Dataset 2. Every choice (pool of {len(pool)} judges, A, best genre",
      "guesser, judge x genre table, own-genre cells, route R) is learned on split 1 with the lock rules and tested on",
      "split 2. Same data source, same answer writer, same genre labels: no dataset shift.", "",
      "BHS: lower is better. Difference = route minus A (below 0 = the route is better). Paired bootstrap over questions,",
      f"{B:,} re-samples, seed {SEED}; two-sided p; Holm over the 2 R vs A tests.", "",
      "## The same test as on Dataset 2 (cells of 50+ questions, as locked)", "",
      "| Test | Condition | Test questions | A | R | Difference | 95% range | p | p (Holm) |", "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    c = r["c"]
    md.append(f"| R vs A | {CN[c]} | {len(s2)} | {main[c]['score']['A']:.2f} | {main[c]['score']['R']:.2f} | {r['diff']:+.2f} | "
              f"{r['lo']:+.2f} to {r['hi']:+.2f} | {r['p']:.3f} | {r['holm']:.3f} |")
for name, res in (("cells of 50+ questions (as locked)", main), ("cells of 25+ questions (half of 50, because a half has half the questions)", small)):
    md += ["", f"### All routes, {name}", "",
           "| Condition | Route | BHS on split 2 | Difference vs A | 95% range | Judges used (questions) |", "|---|---|---|---|---|---|"]
    for c in CONDS:
        md.append(f"| {CN[c]} | A | {res[c]['score']['A']:.2f} | | | {res[c]['L']['A']} {len(s2)} |")
        for m in "RDEF":
            t = res[c]["tests"][m]
            md.append(f"| {CN[c]} | {m} | {res[c]['score'][m]:.2f} | {t['diff']:+.2f} | {t['lo']:+.2f} to {t['hi']:+.2f} | "
                      + ", ".join(f"{j} {n}" for j, n in res[c]["used"][m].most_common()) + " |")
md += ["", "### What split 1 chose (cells of 50+ questions)", ""]
for c in CONDS:
    L = main[c]["L"]
    md.append(f"- **{CN[c]}:** A = {L['A']} ({L['ov'][L['A']]}); best genre guesser = {L['guesser']}; table: "
              + "; ".join(f"{g} {j} {s}" for g, (j, s) in L["table"].items())
              + f"; genres without a table cell fall back to A.")
md += ["", f"## How much one split can vary: {REPEATS} more random splits, each used in both directions ({2 * REPEATS} runs)", "",
       "Point estimates only (no bootstrap). Difference = route minus A on the test half.", "",
       "| Condition | Route | Mean difference | Middle 95% of runs | Route better (below 0) | Same | Route worse |", "|---|---|---|---|---|---|---|"]
for c in CONDS:
    for m in "RDEF":
        d = sorted(rep[c][m])
        n = len(d)
        md.append(f"| {CN[c]} | {m} | {sum(d) / n:+.2f} | {d[int(0.025 * n)]:+.2f} to {d[int(0.975 * n) - 1]:+.2f} | "
                  f"{100 * sum(x < 0 for x in d) / n:.0f}% | {100 * sum(x == 0 for x in d) / n:.0f}% | {100 * sum(x > 0 for x in d) / n:.0f}% |")
out = root / "results/split_experiment"
out.mkdir(parents=True, exist_ok=True)
(out / "split_experiment.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
