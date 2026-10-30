"""Lock v2 for Dataset 2 (GenreHalluEval): lock v1 plus one best-path route R, computed from BenHalluEval runs only.

R (decided by Mahdi on 2026-10-27, before any Dataset 2 answer existed): for each answer, the candidates are
  - the our-genre path: the best genre guesser names the genre; the judge × genre table gives the judge, with that
    cell's BenHalluEval BHS as its score (a genre without a cell gives A, scored by A's overall BHS);
  - the own-genre paths: each asked LLM names the genre; its (LLM, named genre) cell gives that LLM, with the cell's
    BHS as its score (cells under 50 questions are not used);
  and the answer goes to the candidate with the lowest score (tie: the lower overall BHS).
Only LLMs with at least one own-genre cell below the highest our-genre score can ever win, so only they are asked for
the genre ("askers"). This gives exactly the same routes as asking every pool judge.

Every number comes from lock_v1.json (itself computed from BenHalluEval only). The script also scores R, E, F against
A on BenHalluEval (same data and 5-fold by question) for the record. It refuses to overwrite a lock, and refuses run
records that are not BenHalluEval.

Writes results/lock/lock_v2.json, lock_v2.md, lock_v2.sha256.
Usage: python3 -I src/routing/make_lock_v2.py <project_root>
"""
import collections
import csv
import datetime
import hashlib
import json
import random
import sys
from pathlib import Path

root = Path(sys.argv[1])
OUT = root / "results/lock"
if (OUT / "lock_v2.json").exists():
    sys.exit("lock_v2 already exists. A lock is never overwritten.")
V1_SHA = "779cc5a7cdc20b0abc1e73986a25e03d1bd1cd1e32a798d3fb0a3d62ecd50063"
v1_bytes = (OUT / "lock_v1.json").read_bytes()
assert hashlib.sha256(v1_bytes).hexdigest() == V1_SHA, "lock_v1.json changed"
v1 = json.loads(v1_bytes)
POOL = v1["pools"]["dataset2_pool"]
NAME = {"History, Politics & Education": "HISTORY", "Arts, Culture & Sports": "ARTS", "Science & Technology": "SCIENCE",
        "Geography & Places": "GEOGRAPHY", "Religion": "RELIGION", "Other": "OTHER"}
PROMPT = {"context": "judge_v1", "no_context": "judge_noctx_v1"}

# ---- R from lock v1's numbers ----
R = {}
for c, L in v1["conditions"].items():
    A = L["A_best_single_judge"]
    table = {g: v for g, v in L["D_E_judge_per_genre"].items() if v.get("BHS") is not None}
    overall = {j: v["BHS"] for j, v in L["overall_BHS"].items()}
    e_max = max([v["BHS"] for v in table.values()] + [overall[A]])
    own = {(j, g): v["BHS"] for j, cells in L["F_own_genre_scores"].items() for g, v in cells.items()}
    askers = sorted({j for (j, g), s in own.items() if s < e_max} | {L["best_genre_guesser"]["judge"]})
    assert not any(s == e_max for s in own.values()), "a tie at the threshold: pruning would not be exact"
    R[c] = dict(guesser=L["best_genre_guesser"]["judge"], A=A, our_genre_scores={g: v["BHS"] for g, v in table.items()},
                our_genre_judges={g: v["judge"] for g, v in table.items()}, A_score=overall[A],
                highest_our_genre_score=e_max, askers=askers,
                own_genre_cells_that_can_win={f"{j} {g}": s for (j, g), s in sorted(own.items()) if j in askers and s < e_max})

# ---- check on BenHalluEval (exploratory; never changes R) ----
items = [r for r in csv.DictReader(open(root / "data/final/benhallueval-qa-v1.3/items.csv", encoding="utf-8"))
         if r["include_main"] == "yes"]
qids = sorted({r["question_id"] for r in items})
by_q = collections.defaultdict(list)
for r in items:
    by_q[r["question_id"]].append(r)
human = {r["question_id"]: NAME[r["genre"]] for r in items}


def log(m, turn, pid):
    p = root / "runs" / f"benhallueval__{m}__{turn}__{pid}.jsonl"
    recs = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    if {r.get("dataset") for r in recs} - {"benhallueval"}:
        raise SystemExit(f"{p.name}: the lock reads BenHalluEval only (golden rule 3)")
    return {r["key"]: r["parsed"] for r in recs}


def qc(f):
    out = {}
    for q in qids:
        a = [0, 0, 0, 0]
        for r in by_q[q]:
            v = f(r)
            if r["label"] == "0":
                a[0] += 1; a[1] += v != "no"
            else:
                a[2] += 1; a[3] += v != "yes"
        out[q] = a
    return out


def bhs(c, qs):
    s = [sum(c[q][k] for q in qs) for k in range(4)]
    return 50 * (s[1] / s[0] + s[3] / s[2])


genre = {m: log(m, "genre", "genre_v1") for m in POOL}
check = {}
for c in ("context", "no_context"):
    V = {m: log(m, "judge", PROMPT[c]) for m in POOL}
    pj = {m: qc(lambda r, m=m: V[m][r["item_id"]]) for m in POOL}

    def choose(train):
        overall = {m: bhs(pj[m], train) for m in POOL}
        A = min(overall, key=overall.get)
        guesser = max(POOL, key=lambda m: sum(genre[m][q] == human[q] for q in train))
        table, tscore, own = {}, {}, {}
        for g in NAME.values():
            qs = [q for q in train if human[q] == g]
            if len(qs) >= 50:
                table[g] = min(POOL, key=lambda m: bhs(pj[m], qs))
                tscore[g] = bhs(pj[table[g]], qs)
            for m in POOL:
                qs2 = [q for q in train if genre[m][q] == g]
                if len(qs2) >= 50:
                    own[(m, g)] = bhs(pj[m], qs2)
        return A, overall, guesser, table, tscore, own

    def route(meth, q, A, overall, guesser, table, tscore, own):
        gd = genre[guesser][q]
        e = (tscore[gd], overall[table[gd]], table[gd]) if gd in table else (overall[A], overall[A], A)
        f = [(own[(m, genre[m][q])], overall[m], m) for m in POOL if (m, genre[m][q]) in own]
        return {"A": A, "E": e[2], "F": min(f)[2] if f else A, "R": min(f + [e])[2]}[meth]

    def predict(train, test):
        ch = choose(train)
        return {(m, r["item_id"]): V[route(m, q, *ch)][r["item_id"]] for q in test for m in "AEFR" for r in by_q[q]}

    rng = random.Random(2026)
    order = qids[:]
    rng.shuffle(order)
    folds = [order[i::5] for i in range(5)]
    cv = {}
    for k in range(5):
        cv.update(predict([q for i, f in enumerate(folds) if i != k for q in f], folds[k]))
    ins = predict(qids, qids)
    S = [[qids[rng.randrange(len(qids))] for _ in qids] for _ in range(1000)]
    check[c] = {}
    for label, P in (("same_data", ins), ("5_fold", cv)):
        cnt = {m: qc(lambda r, m=m: P[(m, r["item_id"])]) for m in "AEFR"}
        check[c][label] = {"A_BHS": round(bhs(cnt["A"], qids), 2)}
        for m in "EFR":
            d = sorted(bhs(cnt[m], s) - bhs(cnt["A"], s) for s in S)
            check[c][label][f"{m}_minus_A"] = [round(bhs(cnt[m], qids) - bhs(cnt["A"], qids), 2), round(d[25], 2), round(d[974], 2)]
    # the routes R gives with only the askers equal those with every pool judge
    ch = choose(qids)
    for q in qids:
        full = route("R", q, *ch)
        e = ch[4][genre[ch[2]][q]] if genre[ch[2]][q] in ch[3] else ch[1][ch[0]]
        e_c = (e, ch[1][ch[3].get(genre[ch[2]][q], ch[0])], ch[3].get(genre[ch[2]][q], ch[0]))
        f = [(ch[5][(m, genre[m][q])], ch[1][m], m) for m in R[c]["askers"] if (m, genre[m][q]) in ch[5]]
        assert min(f + [e_c])[2] == full, (c, q)

lock = dict(lock_version="v2", created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            rule=v1["rule"] + " Lock v2 adds route R (decided 2026-10-27, before any Dataset 2 answer existed); every "
                 "lock v1 choice is unchanged.",
            based_on=dict(lock_v1_sha256=V1_SHA), source=v1["source"], setup=v1["setup"], pools=v1["pools"],
            min_cell_questions=v1["min_cell_questions"], conditions=v1["conditions"],
            R_best_path=dict(rule="candidates: the our-genre path (best genre guesser names the genre -> judge x genre "
                                  "table judge, scored by that cell's BHS; no cell -> A, scored by A's overall BHS) and "
                                  "the own-genre paths of the askers (asker names the genre -> that asker, scored by its "
                                  "own-genre cell's BHS; cells under 50 questions not used); pick the lowest score; tie -> "
                                  "lower overall BHS. The genre prompt always gets question + passage, never the answer.",
                             per_condition=R),
            dataset2_answers="GenreHalluEval Set B: each answer is judged in its own condition (column `condition`)",
            confirmatory_tests=dict(comparisons=["R vs A (context)", "R vs A (no_context)"],
                                    statistic=v1["confirmatory_tests"]["statistic"],
                                    uncertainty=v1["confirmatory_tests"]["uncertainty"],
                                    p_value=v1["confirmatory_tests"]["p_value"],
                                    multiplicity="Holm correction across the 2 comparisons at alpha 0.05",
                                    everything_else="exploratory: D, E, F (F over the askers only), Set A, per genre, "
                                                    "determinism check"),
            benhallueval_check_of_R=check)
OUT.mkdir(parents=True, exist_ok=True)
text = json.dumps(lock, ensure_ascii=False, indent=1) + "\n"
(OUT / "lock_v2.json").write_text(text, encoding="utf-8")
sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
(OUT / "lock_v2.sha256").write_text(f"{sha}  lock_v2.json\n", encoding="utf-8")
md = [f"# Locked choices for Dataset 2, v2 (GenreHalluEval)", "",
      f"Created {lock['created_utc']} by `src/routing/make_lock_v2.py`. sha256 of `lock_v2.json`: `{sha}`. Based on "
      f"lock v1 (`{V1_SHA[:12]}…`), whose choices are all unchanged.", "",
      "**New: route R (best path).** " + lock["R_best_path"]["rule"], ""]
for c, x in R.items():
    md += [f"## {c}", "", f"- A = {x['A']} (BHS {x['A_score']}); best genre guesser = {x['guesser']}",
           "- our-genre path: " + ", ".join(f"{g} → {x['our_genre_judges'][g]} ({s})" for g, s in x["our_genre_scores"].items()),
           f"- LLMs asked for the genre: {', '.join(x['askers'])} (own-genre cells below {x['highest_our_genre_score']})",
           "- own-genre cells that can win: " + ", ".join(f"{k} ({v:.2f})" for k, v in x["own_genre_cells_that_can_win"].items()),
           f"- BenHalluEval check (R minus A, 95% range): same data {check[c]['same_data']['R_minus_A']}, "
           f"5-fold {check[c]['5_fold']['R_minus_A']}", ""]
md += ["## Confirmatory tests on Dataset 2", "", "- R vs A with the passage; R vs A without it; Holm over 2 at α = 0.05.",
       "- Everything else is exploratory."]
(OUT / "lock_v2.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
