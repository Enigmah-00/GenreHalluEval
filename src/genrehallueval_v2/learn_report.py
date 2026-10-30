"""Learn-half report for GenreHalluEval v2: routing at a glance, from the learn runs and lock_ghe2_v1.json.

Per condition and genre (our genre label): the best judge, the runner-up and whether the gap is clear (95% range of
the runner-up minus best difference from a bootstrap over questions, 2,000 draws, seed 2026, excludes 0); the best
own-genre cell for that genre (an LLM's score inside the genre it named itself, 50+ questions); and that LLM's own vs
our-genre score. Also genre agreement with our labels, no_answer counts and cost. Descriptive only: every routing
choice is in the lock; this report changes nothing.

Usage: python3 -I src/genrehallueval_v2/learn_report.py <project_root> <learn zip> [...] [--out results/ghe2/learn_report_v1.md]
"""
import argparse
import collections
import csv
import json
import random
import zipfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("root")
ap.add_argument("inputs", nargs="+")
ap.add_argument("--out", default="results/ghe2/learn_report_v1.md")
args = ap.parse_args()
root = Path(args.root)
PKG = root / "data/final/GenreHalluEval-v2.0"
lock = json.loads((PKG / "lock_ghe2_v1.json").read_text(encoding="utf-8"))
cfg = json.loads((PKG / "pool.json").read_text(encoding="utf-8"))
CODE = {n: c for c, n in cfg["genres"].items()}
GEN = [g for g in cfg["genres"] if g != "OTHER"]
POOL, MIN = lock["pools"]["usable"], cfg["min_cell_questions"]
rows = list(csv.DictReader(open(PKG / "learn_items.csv", encoding="utf-8")))
human = {r["question_id"]: CODE[r["genre"]] for r in rows}
QIDS = sorted(human)
label = {r["item_id"]: r["label"] for r in csv.DictReader(open(root / lock["source"]["labels_file"], encoding="utf-8-sig"))}
qitems = collections.defaultdict(list)
for r in rows:
    if r["condition"] == "context":
        qitems[r["question_id"]].append(r["item_id"])

recs, cost = {}, []
for p in args.inputs:
    z = zipfile.ZipFile(p)
    for n in z.namelist():
        if n.endswith(".jsonl") and "/ghe2_learn__" in f"/{n}":
            _, m, stage, pid = Path(n).stem.split("__")
            key = stage if stage == "genre" else ("judge:context" if pid in ("judge_v1", "judge_bn_v1") else "judge:no_context")
            recs[(m, key)] = {r["key"]: r for r in map(json.loads, z.read(n).decode().splitlines()) if r}
        elif n.endswith("manifest.json"):
            cost += json.loads(z.read(n))["cost"]
named = {m: {q: r["parsed"] for q, r in recs[(m, "genre")].items()} for m in POOL}


def cnt(m, c):
    v = {k: r["parsed"] for k, r in recs[(m, f"judge:{c}")].items()}
    out = {}
    for q in QIDS:
        a = [0, 0, 0, 0]
        for i in qitems[q]:
            if label[i] == "0":
                a[0] += 1; a[1] += v[i] != "no"
            else:
                a[2] += 1; a[3] += v[i] != "yes"
        out[q] = a
    return out


def bhs(ct, qs):
    s = [sum(ct[q][k] for q in qs) for k in range(4)]
    return 50 * (s[1] / s[0] + s[3] / s[2]) if s[0] and s[2] else None


rng = random.Random(2026)


def clear_gap(c1, c2, qs, draws=2000):
    """95% range of BHS(c2) - BHS(c1) over question re-samples; clear if it excludes 0."""
    d = []
    for _ in range(draws):
        s = [rng.choice(qs) for _ in qs]
        a, b = bhs(c1, s), bhs(c2, s)
        if a is not None and b is not None:
            d.append(b - a)
    d.sort()
    lo, hi = d[int(0.025 * len(d))], d[int(0.975 * len(d)) - 1]
    return lo, hi, lo > 0


out = [f"# GenreHalluEval v2: learn half report (descriptive; the routes are in lock_ghe2_v1.json)", "",
       f"Lock sha256 `{(root / 'results/lock/lock_ghe2_v1.sha256').read_text().split()[0]}`. {len(QIDS)} learn questions "
       f"(50 per genre), {len(qitems) * 5} answers, each judged with and without the passage. Labels: "
       f"`{lock['source']['labels_file']}`. BHS: lower is better; 50 = chance.", "",
       "## 0. Routing at a glance", "",
       "Gap = runner-up minus best, 95% range over question re-samples; 'clear' when the range excludes 0. "
       "Own-genre best = the lowest score of any LLM inside the genre it named itself (cells of 50+ questions).", ""]
for c in ("context", "no_context"):
    C = {m: cnt(m, c) for m in POOL}
    out += [f"### {'With the passage' if c == 'context' else 'Without the passage'} (A = {lock['conditions'][c]['A_best_single_judge']})", "",
            "| Genre | Best (ours) | Runner-up | Gap | Own-genre best | Its own vs ours | Clearly better in own genre |",
            "|---|---|---|---|---|---|---|"]
    for g in GEN:
        qs = [q for q in QIDS if human[q] == g]
        rank = sorted(POOL, key=lambda m: (bhs(C[m], qs), m))
        b1, b2 = rank[0], rank[1]
        lo, hi, clear = clear_gap(C[b1], C[b2], qs)
        own = []
        better = []
        for m in POOL:
            oq = [q for q in QIDS if named[m][q] == g]
            if len(oq) >= MIN:
                own.append((bhs(C[m], oq), m, len(oq)))
                if bhs(C[m], oq) < bhs(C[m], qs):
                    # clearly better inside its own genre than inside ours: bootstrap own-set vs our-set (independent)
                    d = []
                    for _ in range(1000):
                        a = bhs(C[m], [rng.choice(oq) for _ in oq])
                        b = bhs(C[m], [rng.choice(qs) for _ in qs])
                        if a is not None and b is not None:
                            d.append(b - a)
                    d.sort()
                    if d[int(0.025 * len(d))] > 0:
                        better.append(m)
        ob = min(own) if own else None
        out.append(f"| {g} | {b1} {bhs(C[b1], qs):.2f} | {b2} {bhs(C[b2], qs):.2f} | {lo:+.2f} to {hi:+.2f}"
                   f"{' clear' if clear else ''} | "
                   + (f"{ob[1]} {ob[0]:.2f} ({ob[2]} q)" if ob else "none (no cell of 50+)") + " | "
                   + (f"{ob[0]:.2f} vs {bhs(C[ob[1]], qs):.2f}" if ob else "–") + " | "
                   + (", ".join(better) or "none") + " |")
    out.append("")

out += ["## 1. Overall scores, genre agreement and no_answer", "",
        "| LLM | Prompts | BHS with passage | BHS without | Genre agrees with ours | Genre no_answer | no_answer with / without |",
        "|---|---|---|---|---|---|---|"]
for m in POOL:
    ag = sum(named[m][q] == human[q] for q in QIDS) / len(QIDS)
    na = [sum(r["parsed"] == "no_answer" for r in recs[(m, f"judge:{c}")].values()) for c in ("context", "no_context")]
    out.append(f"| {m} | {cfg['prompt_language'][m]} | {lock['conditions']['context']['overall_BHS'][m]['BHS']} | "
               f"{lock['conditions']['no_context']['overall_BHS'][m]['BHS']} | {100 * ag:.1f}% | "
               f"{sum(v == 'no_answer' for v in named[m].values())} | {na[0]} / {na[1]} |")
out += ["", "## 2. The routes in the lock", ""]
for c in ("context", "no_context"):
    R = lock["R_best_path"]["per_condition"][c]
    out.append(f"- {c}: A = {R['A']}; best genre guesser = {R['guesser']}; askers = {', '.join(R['askers'])}; "
               f"highest our-genre cell = {R['highest_our_genre_score']}; own-genre cells that can win: "
               + (", ".join(f"{k} {v:.2f}" for k, v in R["own_genre_cells_that_can_win"].items()) or "none"))
tok = collections.defaultdict(lambda: [0, 0.0])
for x in cost:
    tok[x["model"]][0] += x["calls"]; tok[x["model"]][1] += x["seconds"]
pt = {m: sum(r.get("prompt_tokens") or 0 for k in recs if k[0] == m for r in recs[k].values()) for m in POOL}
ot = {m: sum(r.get("output_tokens") or 0 for k in recs if k[0] == m for r in recs[k].values()) for m in POOL}
out += ["", "## 3. Cost (learn half)", "", "| LLM | Calls | Prompt tokens | Output tokens | Model busy time |", "|---|---|---|---|---|"]
out += [f"| {m} | {tok[m][0]:,} | {pt[m]:,} | {ot[m]:,} | {tok[m][1] / 3600:.2f} h |" for m in POOL]
out.append(f"| total | {sum(v[0] for v in tok.values()):,} | {sum(pt.values()):,} | {sum(ot.values()):,} | "
           f"{sum(v[1] for v in tok.values()) / 3600:.2f} h |")
p = root / args.out
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
