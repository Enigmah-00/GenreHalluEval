"""Build the cross-model overview from results/<model>/full/ and runs/ (one row per finished model).

Usage: python3 -I src/bench/overview.py <project_root>
Writes results/overview.md and results/overview_*.csv. Exploratory description only: no judge is chosen here
(choices are made and locked in the routing notebook, after all models are in).
"""
import csv
import datetime
import json
import random
import sys
from pathlib import Path

root = Path(sys.argv[1])
RES = root / "results"
GENRES = ["HISTORY", "ARTS", "SCIENCE", "GEOGRAPHY", "RELIGION", "OTHER"]
CONDS = ["context", "no_context"]
# zero-shot QA BHS in the BenHalluEval paper (Table 4; their own hallucinated answers, so a rough guide only)
PAPER = {"deepseek-r1-14b": 38.60, "gpt-4.1-mini": 15.56, "qwen2.5-32b": 46.85, "gemma2-27b": 47.45,
         "mistral-nemo-12b": 53.84, "llama3.1-8b": 47.71, "tigerllm-9b": 28.28, "titullm-3b": 50.00,
         "banglallama-13b": 48.62}
SPAN_RULE = 13.8                                    # "not a passage span" rule, package shortcut_report.md
PROMPT = {"context": "judge_v1", "no_context": "judge_noctx_v1"}
NAME = {"History, Politics & Education": "HISTORY", "Arts, Culture & Sports": "ARTS", "Science & Technology": "SCIENCE",
        "Geography & Places": "GEOGRAPHY", "Religion": "RELIGION", "Other": "OTHER"}
BOOT, SEED = 1000, 2026


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write(name, rows):
    if rows:
        with open(RES / name, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)


def md(rows, cols):
    return "\n".join(["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
                     + ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows])


def cell(row):                                      # "BHS (n)", marked when the cell is too small to route on
    return f"{row['BHS']} ({row['questions']})" + ("" if row["usable"] == "yes" else " †")


models = sorted(p.parent.parent.name for p in RES.glob("*/full/manifest.json"))
board, guess, run1, run2 = [], [], {c: [] for c in CONDS}, {c: [] for c in CONDS}
for m in models:
    d = RES / m / "full"
    man = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    summ = json.loads((d / "summary.json").read_text(encoding="utf-8"))
    hours = (datetime.datetime.fromisoformat(man["finished"]) - datetime.datetime.fromisoformat(man["started"])).seconds / 3600
    row = {"model": m, "pool": man["config"].get("pool", ""), "date": man["started"][:10]}
    for c in CONDS:
        if not (d / f"overall__{c}.csv").exists():
            row[f"BHS_{c}"] = "–"
            continue
        o = read(d / f"overall__{c}.csv")
        main = o[0]
        span = next(r for r in o if r["view"].startswith("span subset"))
        row.update({f"BHS_{c}": main["BHS"], f"range95_{c}": main["range95"], f"trackA_{c}": main["trackA_err"],
                    f"trackB_{c}": main["trackB_err"], f"no_answer_{c}": main["no_answer"], f"span_BHS_{c}": span["BHS"]})
        run1[c].append({"model": m, **{r["genre"]: cell(r) for r in read(d / f"judge_by_human_genre__{c}.csv")}})
        run2[c].append({"model": m, **{r["genre"]: cell(r) for r in read(d / f"judge_by_own_genre__{c}.csv")
                                       if r["genre"] != "no_answer"}})
    diff = read(d / "context_vs_no_context__overall.csv")[0] if (d / "context_vs_no_context__overall.csv").exists() else {}
    row.update(passage_gain=f"{diff.get('difference', '–')} ({diff.get('range95', '–')})", paper_BHS=PAPER.get(m, "–"),
               calls=sum(v["calls"] for v in summ["cost"].values()),
               tokens_in_M=round(sum(v["prompt_tokens"] for v in summ["cost"].values()) / 1e6, 2),
               session_h=round(hours, 2), version=man["model_version"].split(";")[0])
    board.append(row)
    g = {r["compared_with"].split(" ")[0]: r for r in read(d / "genre_guessing.csv")}
    named = {r["genre"]: r["questions"] for r in read(d / "judge_by_own_genre__context.csv")}
    guess.append({"model": m, "accuracy": g["final"]["accuracy"], "macro_F1": g["final"]["macro_F1"],
                  "kappa": g["final"]["kappa"], "kappa_range95": g["final"]["kappa_range95"],
                  "kappa_blind200": g.get("blind", {}).get("kappa", "–"), "no_answer": g["final"]["no_answer"],
                  **{f"named_{k}": named.get(k, 0) for k in GENRES}})

write("overview_leaderboard.csv", board)
write("overview_genre_guessing.csv", guess)
for c in CONDS:
    write(f"overview_judge_by_human_genre__{c}.csv", run1[c])
    write(f"overview_judge_by_own_genre__{c}.csv", run2[c])

N_ITEMS = 4600                                      # answers in the main set (v1.3)
human_n = {r["genre"]: r["questions"] for r in read(RES / models[0] / "full/judge_by_human_genre__context.csv")} if models else {}
text = [
    "# Overview of all judge runs (BenHalluEval-QA v1.3)",
    "",
    f"Built {datetime.date.today()} by `src/bench/overview.py` from `results/<model>/full/`. Models so far: "
    f"{len(models)} of 12 ({', '.join(models)}). Details of each run: `docs/runlog.md`.",
    "",
    "BHS: lower is better; 50 = chance. Ranges are 95% from re-sampling questions. This page describes; it chooses",
    "nothing. All choices are made and locked in the routing notebook after every model is in.",
    "",
    "## 1. Judges",
    "",
    md(board, ["model", "pool", "BHS_context", "range95_context", "BHS_no_context", "range95_no_context",
               "passage_gain", "trackA_context", "trackB_context", "trackA_no_context", "trackB_no_context"]),
    "",
    f"- trackA = correct answers flagged as hallucinated (%); trackB = hallucinations missed (%).",
    f"- passage_gain = BHS without the passage − BHS with it (paired; positive = the passage helps).",
    f"- Reference: the rule \"hallucinated if the answer is not a passage span\" scores **{SPAN_RULE}** with the passage.",
    *([f"- **No usable verdicts:** {', '.join(dead)}. Over half of the replies were not yes/no, so BHS is 100 by"
       " construction (every no_answer counts as an error on both tracks). Never routed to; report separately."]
      if (dead := sorted({r["model"] for r in board for c in CONDS
                          if r.get(f"no_answer_{c}") not in (None, "–") and int(r[f"no_answer_{c}"]) > N_ITEMS // 2}))
      else []),
    "",
    md(board, ["model", "span_BHS_context", "span_BHS_no_context", "paper_BHS", "no_answer_context",
               "no_answer_no_context", "calls", "tokens_in_M", "session_h", "version", "date"]),
    "",
    "- span_BHS = BHS on the answers copied from the passage (920 golds + 1,017 hallucinations); the span rule is",
    "  useless there. paper_BHS = the paper's QA score for the same model, on its own (GPT-5.4) hallucinations.",
    "",
    "## 2. Genre guessing (against our human-verified genres)",
    "",
    md(guess, ["model", "accuracy", "macro_F1", "kappa", "kappa_range95", "kappa_blind200", "no_answer"]),
    "",
    "How many questions each model put in each genre (ours: " + ", ".join(f"{g} {human_n.get(g, '?')}" for g in GENRES) + "):",
    "",
    md(guess, ["model"] + [f"named_{g}" for g in GENRES]),
    "",
]
for c, name in (("context", "WITH the passage"), ("no_context", "WITHOUT the passage")):
    text += [f"## 3{'a' if c == 'context' else 'b'}. Judge × genre, {name}", "",
             "Run 1, by **our** genre (the routing table for methods D and E). Cells: BHS (questions); † = under 50",
             "questions, never used for routing.", "", md(run1[c], ["model"] + GENRES), "",
             "Run 2, by the genre **each model named itself** (the {LLM, genre} pairs for method F).", "",
             md(run2[c], ["model"] + GENRES), ""]
# ---------- paired comparisons from the raw logs (same questions; bootstrap over questions) ----------
items = [r for r in read(root / "data/final/benhallueval-qa-v1.3/items.csv") if r["include_main"] == "yes"]
qids = sorted({r["question_id"] for r in items})
human = {r["question_id"]: NAME[r["genre"]] for r in items}


def log(m, turn, prompt):
    p = root / "runs" / f"benhallueval__{m}__{turn}__{prompt}.jsonl"
    if not p.exists():
        return {}
    return {r["key"]: r["parsed"] for r in map(json.loads, p.read_text(encoding="utf-8").splitlines()) if r}


def counts(verdicts):                              # per question: correct, false alarms, hallucinated, misses
    agg = {q: [0, 0, 0, 0] for q in qids}
    for r in items:
        v, a = verdicts[r["item_id"]], agg[r["question_id"]]
        if r["label"] == "0":
            a[0] += 1
            a[1] += v != "no"
        else:
            a[2] += 1
            a[3] += v != "yes"
    return [agg[q] for q in qids]


def bhs(rows, idx):
    s = [0, 0, 0, 0]
    for i in idx:
        r = rows[i]
        s[0] += r[0]; s[1] += r[1]; s[2] += r[2]; s[3] += r[3]
    return 50 * (s[1] / s[0] + s[3] / s[2])


rng = random.Random(SEED)
SAMPLES = [[rng.randrange(len(qids)) for _ in qids] for _ in range(BOOT)]   # the same re-samples for every pair


def paired(stat_a, stat_b):
    d = sorted(stat_b(s) - stat_a(s) for s in SAMPLES)
    return d[int(0.025 * BOOT)], d[int(0.975 * BOOT) - 1]


cmp_rows, agree_rows = [], []
for c in CONDS:
    verdicts = {m: log(m, "judge", PROMPT[c]) for m in models}
    verdicts = {m: v for m, v in verdicts.items() if len(v) == len(items)}
    rows = {m: counts(v) for m, v in verdicts.items()}
    full = list(range(len(qids)))
    score = {m: bhs(r, full) for m, r in rows.items()}
    if not score:
        continue
    best = min(score, key=score.get)
    for m in sorted(score, key=score.get):
        lo, hi = paired(lambda s: bhs(rows[best], s), lambda s: bhs(rows[m], s)) if m != best else (0, 0)
        cmp_rows.append({"condition": c, "model": m, "BHS": f"{score[m]:.2f}", "vs": best,
                         "difference": f"{score[m] - score[best]:+.2f}", "range95": f"{lo:+.2f} to {hi:+.2f}",
                         "clearly_worse": "yes" if lo > 0 else ("–" if m == best else "no")})
    names = sorted(verdicts)
    for a in names:
        row = {"condition": c, "model": a}
        for b in names:
            row[b] = f"{100 * sum(verdicts[a][k] == verdicts[b][k] for k in verdicts[a]) / len(items):.0f}%"
        agree_rows.append(row)

genre_logs = {m: log(m, "genre", "genre_v1") for m in models}
genre_logs = {m: g for m, g in genre_logs.items() if len(g) == len(qids)}
correct = {m: [g[q] == human[q] for q in qids] for m, g in genre_logs.items()}
acc = {m: sum(v) / len(qids) for m, v in correct.items()}
gcmp = []
if acc:
    top = max(acc, key=acc.get)
    for m in sorted(acc, key=acc.get, reverse=True):
        lo, hi = paired(lambda s: 100 * sum(correct[top][i] for i in s) / len(s),
                        lambda s: 100 * sum(correct[m][i] for i in s) / len(s)) if m != top else (0, 0)
        gcmp.append({"model": m, "accuracy": f"{100 * acc[m]:.1f}", "vs": top,
                     "difference": f"{100 * (acc[m] - acc[top]):+.1f}", "range95": f"{lo:+.1f} to {hi:+.1f}",
                     "clearly_worse": "yes" if hi < 0 else ("–" if m == top else "no")})
write("overview_paired_vs_best.csv", cmp_rows)
write("overview_genre_paired_vs_best.csv", gcmp)
write("overview_agreement.csv", agree_rows)
text += ["## 4. Each judge against the best so far (paired, same questions)", "",
         "difference = this model's BHS − the best model's BHS (positive = worse); 95% range from 1,000 re-samples of",
         "questions (the same re-samples for every model). \"clearly_worse\" = the whole range is above 0. Exploratory:",
         "the best judge is chosen and locked only in the routing notebook.", "",
         md(cmp_rows, ["condition", "model", "BHS", "vs", "difference", "range95", "clearly_worse"]), "",
         "Genre guessing, accuracy against our genres (difference in percentage points; negative = worse):", "",
         md(gcmp, ["model", "accuracy", "vs", "difference", "range95", "clearly_worse"]), "",
         "## 5. How often two judges give the same verdict (all 4,600 answers)", "",
         "Low agreement between good judges is what makes voting and routing worth trying.", ""]
for c in CONDS:
    rows = [r for r in agree_rows if r["condition"] == c]
    if rows:
        text += [f"{'With' if c == 'context' else 'Without'} the passage:", "",
                 md(rows, ["model"] + [r["model"] for r in rows]), ""]
# ---------- Run 1 vs Run 2: our genres against each model's own genres (same verdicts, grouped two ways) ----------
def bhs_in(rows, sample, members):
    s = [0, 0, 0, 0]
    for i in sample:
        if i in members:
            r = rows[i]
            s[0] += r[0]; s[1] += r[1]; s[2] += r[2]; s[3] += r[3]
    return 50 * (s[1] / s[0] + s[3] / s[2]) if s[0] and s[2] else None


r12 = []
for c in CONDS:
    for m in models:
        v = log(m, "judge", PROMPT[c])
        g = genre_logs.get(m)
        if len(v) != len(items) or not g:
            continue
        rows = counts(v)
        full = range(len(qids))
        for genre in GENRES:
            ours = {i for i, q in enumerate(qids) if human[q] == genre}
            own = {i for i, q in enumerate(qids) if g[q] == genre}
            a, b = bhs_in(rows, full, ours), bhs_in(rows, full, own)
            d = sorted(x - y for x, y in ((bhs_in(rows, smp, own), bhs_in(rows, smp, ours)) for smp in SAMPLES)
                       if x is not None and y is not None)
            lo, hi = (d[int(0.025 * len(d))], d[int(0.975 * len(d)) - 1]) if d else (None, None)
            r12.append({"condition": c, "model": m, "genre": genre, "questions_ours": len(ours),
                        "BHS_ours": f"{a:.2f}" if a is not None else "–", "questions_own": len(own),
                        "BHS_own": f"{b:.2f}" if b is not None else "–",
                        "own_minus_ours": f"{b - a:+.2f}" if a is not None and b is not None else "–",
                        "range95": f"{lo:+.2f} to {hi:+.2f}" if lo is not None else "–",
                        "same_questions": f"{100 * len(ours & own) / max(1, len(ours | own)):.0f}%",
                        "usable": "yes" if len(ours) >= 50 and len(own) >= 50 else "no"})
write("overview_ours_vs_own_genre.csv", r12)
text += ["## 6. Judging in OUR genres (Run 1) vs in the genres the model NAMED ITSELF (Run 2)", "",
         "The verdicts are the same; only the grouping of questions differs. BHS_ours = the judge's score on the",
         "questions we put in that genre; BHS_own = its score on the questions it put there itself (its {LLM, genre}",
         "pair). own_minus_ours < 0 means the judge looks better in its own genre. The range is paired (same",
         "re-sampled questions). same_questions = overlap of the two groups. Overall BHS is identical in both runs.", ""]
for c in CONDS:
    rows = [r for r in r12 if r["condition"] == c]
    if rows:
        text += [f"{'With' if c == 'context' else 'Without'} the passage:", "",
                 md(rows, ["model", "genre", "questions_ours", "BHS_ours", "questions_own", "BHS_own",
                           "own_minus_ours", "range95", "same_questions", "usable"]), ""]
# ---------- best judge per genre so far (exploratory; nothing is chosen or locked here) ----------
best_rows, head_rows = [], []
for c in CONDS:
    verdicts = {m: log(m, "judge", PROMPT[c]) for m in models}
    rows = {m: counts(v) for m, v in verdicts.items() if len(v) == len(items)}
    if len(rows) < 2:
        continue
    allidx = set(range(len(qids)))
    overall_best = min(rows, key=lambda m: bhs_in(rows[m], range(len(qids)), allidx))
    pick = {}
    for genre in GENRES:
        members = {i for i, q in enumerate(qids) if human[q] == genre}
        score = {m: bhs_in(r, range(len(qids)), members) for m, r in rows.items()}
        gbest = min(score, key=score.get)
        pick[genre] = gbest if len(members) >= 50 else overall_best      # small cells fall back (rule 5)
        d = sorted(x - y for x, y in ((bhs_in(rows[overall_best], smp, members), bhs_in(rows[gbest], smp, members))
                                      for smp in SAMPLES) if x is not None and y is not None)
        lo, hi = d[int(0.025 * len(d))], d[int(0.975 * len(d)) - 1]
        best_rows.append({"condition": c, "genre": genre, "questions": len(members), "best_here": gbest,
                          "BHS_best_here": f"{score[gbest]:.2f}", "overall_best": overall_best,
                          "BHS_overall_best": f"{score[overall_best]:.2f}",
                          "gain": f"{score[overall_best] - score[gbest]:+.2f}" if gbest != overall_best else "0",
                          "range95": f"{lo:+.2f} to {hi:+.2f}" if gbest != overall_best else "–",
                          "clearly_better": ("yes" if lo > 0 else "no") if gbest != overall_best else "–",
                          "usable": "yes" if len(members) >= 50 else "no"})
    routed = [rows[pick[human[q]]][i] for i, q in enumerate(qids)]
    head_rows.append({"condition": c, "single_best": overall_best,
                      "BHS_single_best": f"{bhs_in(rows[overall_best], range(len(qids)), allidx):.2f}",
                      "BHS_best_per_genre": f"{bhs_in(routed, range(len(qids)), allidx):.2f}",
                      "judges_used": ", ".join(sorted(set(pick.values())))})
write("overview_best_per_genre.csv", best_rows)
text += ["## 7. Is a different judge best in some genre? (exploratory, our genres)", "",
         "For each of our genres: the judge with the lowest BHS there, against the best judge overall. gain = how",
         "much better the genre's own best is (BHS points; paired 95% range). \"clearly_better\" = the range is above 0.",
         "This only describes the runs so far; the routing tables are built and locked in the routing notebook.", ""]
for c in CONDS:
    rows_c = [r for r in best_rows if r["condition"] == c]
    if rows_c:
        text += [f"{'With' if c == 'context' else 'Without'} the passage:", "",
                 md(rows_c, ["genre", "questions", "best_here", "BHS_best_here", "overall_best", "BHS_overall_best",
                             "gain", "range95", "clearly_better", "usable"]), ""]
if head_rows:
    text += ["Headroom: BHS if every genre went to its own best judge, chosen on the same data (in-sample, so",
             "optimistic; the honest test is the 5-fold checkpoint and Dataset 2):", "",
             md(head_rows, ["condition", "single_best", "BHS_single_best", "BHS_best_per_genre", "judges_used"]), ""]
# ---------- 0. routing at a glance: one table, both conditions (put at the top of the page) ----------
glance = []
own_r12 = {(r["condition"], r["model"], r["genre"]): r for r in r12}
for c in CONDS:
    V = {m: log(m, "judge", PROMPT[c]) for m in models}
    ok = [m for m, v in V.items() if len(v) == len(items) and m in genre_logs
          and sum(x == "no_answer" for x in v.values()) <= len(items) // 2]
    if not ok:
        continue
    rows_c = {m: counts(V[m]) for m in ok}
    full = range(len(qids))
    allq = set(full)
    A = min(ok, key=lambda m: bhs_in(rows_c[m], full, allq))
    for g in GENRES:
        ours = {i for i, q in enumerate(qids) if human[q] == g}
        sc = {m: bhs_in(rows_c[m], full, ours) for m in ok}
        rank = sorted(ok, key=sc.get)
        best, second = rank[0], rank[1] if len(rank) > 1 else None
        gap = "–"
        if second:
            d = sorted(bhs_in(rows_c[second], smp, ours) - bhs_in(rows_c[best], smp, ours) for smp in SAMPLES
                       if bhs_in(rows_c[best], smp, ours) is not None and bhs_in(rows_c[second], smp, ours) is not None)
            lo = d[int(0.025 * len(d))] if d else None
            gap = f"{second} {sc[second]:.2f} (+{sc[second] - sc[best]:.2f}, {'clear' if lo and lo > 0 else 'not clear'})"
        own_sc = {}
        for m in ok:
            mem = {i for i, q in enumerate(qids) if genre_logs[m][q] == g}
            if len(mem) >= 50:
                own_sc[m] = (bhs_in(rows_c[m], full, mem), len(mem))
        if own_sc:
            fb = min(own_sc, key=lambda m: own_sc[m][0])
            r = own_r12.get((c, fb, g), {})
            lo_hi = r.get("range95", "–")
            verdict = "–"
            if lo_hi != "–":
                lo, hi = [float(x) for x in lo_hi.split(" to ")]
                verdict = ("own better, range below 0" if hi < 0 else "own worse, range above 0" if lo > 0
                           else "range includes 0") + f": {lo_hi}"
            f_route = f"{fb} {own_sc[fb][0]:.2f} ({own_sc[fb][1]})"
            f_vs = f"{r.get('own_minus_ours', '–')} ({verdict})"
        else:
            fb, f_route, f_vs = A, f"– (no judge named it 50+ times; falls back to {A})", "–"
        better = [f"{m} ({own_r12[(c, m, g)]['own_minus_ours']}; {own_r12[(c, m, g)]['range95']})" for m in ok if (c, m, g) in own_r12
                  and own_r12[(c, m, g)]["usable"] == "yes" and own_r12[(c, m, g)]["range95"] != "–"
                  and float(own_r12[(c, m, g)]["range95"].split(" to ")[1]) < 0]
        glance.append({"condition": "with passage" if c == "context" else "without passage", "genre": g,
                       "questions": len(ours),
                       "route_by_our_genre": f"{best if len(ours) >= 50 else A} {sc[best if len(ours) >= 50 else A]:.2f}"
                                             + ("" if len(ours) >= 50 else " (under 50 questions: A)"),
                       "runner_up": gap,
                       "route_by_own_genre": f_route, "own_minus_ours_for_that_judge": f_vs,
                       "same_judge": "yes" if fb == (best if len(ours) >= 50 else A) else "no",
                       "judges_clearly_better_in_own_genre": ", ".join(better) or "none",
                       "best_overall_judge_here": f"{A} {sc[A]:.2f}"})
write("overview_routing_at_a_glance.csv", glance)
cols0 = ["condition", "genre", "questions", "route_by_our_genre", "runner_up", "route_by_own_genre",
         "own_minus_ours_for_that_judge", "same_judge", "judges_clearly_better_in_own_genre", "best_overall_judge_here"]
glance_md = ["## 0. Routing at a glance (all judges, both conditions)", "",
             "For each of our genres: the judge with the lowest BHS in **our** genre (routing E/D), the runner-up and",
             "whether its gap is clear; the judge with the lowest BHS in the genre it **named itself** (routing F; only",
             "cells with 50+ questions) and how that judge does in its own genre vs ours; every judge that is clearly",
             "better in its own genre (paired 95% range below 0); and the best overall judge (A) for comparison.",
             "Judges with no usable verdicts are left out. Exploratory: the locked choices are in `results/lock/`.",
             "A label depends on the 95% range, not on the size of the difference: a small difference with a narrow",
             "range can be 'below 0' while a larger one with a wide range is not. About 86 own-vs-ours comparisons are",
             "made, so about 2 'below 0' results are expected by chance alone; none stays below 0 after a Holm",
             "correction. Treat single 'below 0' cells as hints to re-test on Dataset 2, not as findings.", "",
             md(glance, cols0), "",
             "Whole-set view: sending each genre to its best judge (same data, optimistic) gives "
             + "; ".join(f"{'with' if r['condition'] == 'context' else 'without'} passage {r['BHS_single_best']} → "
                         f"{r['BHS_best_per_genre']}" for r in head_rows) + ". The honest 5-fold check is in "
             "`results/routing_preview.csv`.", ""]
cut = next(i for i, line in enumerate(text) if line.startswith("## 1."))
text[cut:cut] = glance_md
(RES / "overview.md").write_text("\n".join(text) + "\n", encoding="utf-8")
print(f"wrote results/overview.md and overview_*.csv for {len(models)} model(s): {', '.join(models)}")
