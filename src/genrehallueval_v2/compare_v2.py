"""Score the GenreHalluEval v2 test half: routes E, F and R (one notebook each) vs the single best judge A.

Main tests (test_plan_v2.json, Mahdi 2026-10-30): E vs A, F vs A and R vs A, with the passage and without it = 6 tests,
two-sided, Holm over the 6, alpha 0.05. Also: each route vs A on all answers together; BHS per genre; each route's own
cost; a determinism check (the same judge on the same answer must give the same verdict in every notebook); and an
independent recomputation of every route from lock_ghe2_v1.json and the genres the LLMs named.

BHS = 1/2 x (share of correct answers not called "no" + share of hallucinated answers not called "yes") x 100;
no_answer counts as an error. Paired bootstrap over questions: 10,000 re-samples, seed 2026; 95% range;
p = 2 x min(share of differences <= 0, share >= 0).

Usage: python3 -I src/genrehallueval_v2/compare_v2.py <project_root> --A <zip> [--E <zip>] [--F <zip>] [--R <zip>]
           [--package data/final/GenreHalluEval-v2.0] [--labels data/labels/genrehallueval_v2/labels_v2.0.csv]
           [--out results/ghe2] [--allow-partial]
  Without --labels the design labels are used and the output is marked PREVIEW. With fewer than all three routes
  the report is INTERIM: Holm over 6 needs all 6 p values, so each p is shown x 6 (Bonferroni), an upper bound of
  its final Holm p.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import random
import zipfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("root")
for m in "EFRA":
    ap.add_argument(f"--{m}", required=m == "A")
ap.add_argument("--package", default="data/final/GenreHalluEval-v2.0")
ap.add_argument("--labels")
ap.add_argument("--out", default="results/ghe2")
ap.add_argument("--allow-partial", action="store_true")
args = ap.parse_args()
root = Path(args.root)
rel = lambda p: Path(p) if Path(p).is_absolute() else root / p
PKG = rel(args.package)
SEED, B, ALPHA, DATASET = 2026, 10_000, 0.05, "ghe2_test"
NB = {m: k for m, k in {"E": "route_E", "F": "route_F", "R": "route_R", "A": "single_best"}.items() if getattr(args, m)}
TESTED = [m for m in "EFR" if m in NB]
assert TESTED, "give at least one routed notebook (--E, --F or --R)"
INTERIM = len(TESTED) < 3
ROUTES = ["A"] + TESTED
CONDS = ("context", "no_context")
sha = lambda b: hashlib.sha256(b).hexdigest()
sums = {l.split("  ", 1)[1].strip(): l.split("  ", 1)[0] for l in (PKG / "checksums.sha256").read_text().splitlines() if l.strip()}
lock = json.loads((PKG / "lock_ghe2_v1.json").read_text(encoding="utf-8"))
plan = json.loads((PKG / "test_plan_v2.json").read_text(encoding="utf-8"))
cfg = json.loads((PKG / "pool.json").read_text(encoding="utf-8"))
CODE = {n: c for c, n in cfg["genres"].items()}
ITEMS = {r["item_id"]: r for r in csv.DictReader(open(PKG / "test_items.csv", encoding="utf-8"))}
if args.labels:
    LABEL = {r["item_id"]: int(r["label"]) for r in csv.DictReader(open(rel(args.labels), encoding="utf-8-sig"))
             if r["item_id"] in ITEMS}
    assert set(LABEL) == set(ITEMS), "every test answer needs a label"
    PREVIEW = False
else:
    LABEL = {k: int(r["design_label"]) for k, r in ITEMS.items()}
    PREVIEW = True


class Output:
    def __init__(self, path):
        self.path = rel(path)
        self.z = zipfile.ZipFile(self.path)
        self.names = [n for n in self.z.namelist() if "__MACOSX/" not in n and not Path(n).name.startswith("._")]

    def read(self, n):
        return self.z.read(n).decode("utf-8")

    def one(self, kind, suffix):
        hits = [n for n in self.names if n.endswith(suffix) and f"/{kind}/" in f"/{n}"]
        assert len(hits) == 1, (self.path, kind, suffix, hits)
        return hits[0]


outs, manifest, routes, VERD, TOK = {}, {}, {}, {}, collections.defaultdict(lambda: [0, 0, 0, 0.0])
for m, kind in NB.items():
    o = outs[m] = Output(getattr(args, m))
    man = manifest[m] = json.loads(o.read(o.one(kind, "manifest.json")))
    assert man["notebook"] == kind and man["dataset"] == DATASET, (m, man["notebook"], man["dataset"])
    if man["partial"] and not args.allow_partial:
        raise SystemExit(f"{kind} run is PARTIAL: resume it first (or pass --allow-partial for a look only)")
    assert man["run_mode"] == "full" or args.allow_partial, f"{kind} is a {man['run_mode']} run"
    assert man["truncated"] == 0, f"{kind}: {man['truncated']} prompts were cut"
    assert man["lock_sha256"] == sums["lock_ghe2_v1.json"], f"{kind} ran on another lock"
    for name in ("test_items.csv", "pool.json", "lock_ghe2_v1.json", "test_plan_v2.json"):
        assert man["dataset_checksums"].get(name) == sums[name], f"{kind} used a different {name}"
    routes[m] = {r["item_id"]: r for r in csv.DictReader(io.StringIO(o.read(o.one(kind, "routes.csv"))))}
    for n in o.names:
        if n.endswith(".jsonl") and f"runs/{DATASET}__" in n:
            for line in o.read(n).splitlines():
                if not line.strip():
                    continue
                r = json.loads(line)
                t = TOK[(m, r["stage"])]
                t[0] += 1; t[1] += r["prompt_tokens"] or 0; t[2] += r["output_tokens"] or 0; t[3] += r["latency_s"] or 0
                if r["stage"] == "judge" and r["status"] != "error":
                    assert r["condition"] == ITEMS[r["item_id"]]["condition"], (n, r["item_id"])
                    VERD[(m, r["model_key"], r["item_id"])] = r["parsed"]


def verdict(m, i):
    j = routes[m][i][m]
    return VERD.get((m, j, i), "no_answer"), j


# ---- independent recomputation of every route from the lock and the named genres ----
L, RB = lock["conditions"], lock["R_best_path"]["per_condition"]
TABLE = {c: {g: v["judge"] for g, v in L[c]["D_E_judge_per_genre"].items() if v.get("BHS") is not None} for c in L}
TSC = {c: {g: v["BHS"] for g, v in L[c]["D_E_judge_per_genre"].items() if v.get("BHS") is not None} for c in L}
OWN = {c: {(j, g): v["BHS"] for j, cells in L[c]["F_own_genre_scores"].items() for g, v in cells.items()} for c in L}
OV = {c: {j: v["BHS"] for j, v in L[c]["overall_BHS"].items()} for c in L}
AOF = {c: L[c]["A_best_single_judge"] for c in L}
GUE = {c: L[c]["best_genre_guesser"]["judge"] for c in L}
ASK_R = {c: RB[c]["askers"] for c in L}
ASK_F = {c: sorted(j for j, cells in L[c]["F_own_genre_scores"].items() if cells) for c in L}


def expect(m, i):
    row, c = routes[m][i], ITEMS[i]["condition"]
    named = {k[6:]: v for k, v in row.items() if k.startswith("named_")}
    A = AOF[c]
    if m == "A":
        return A
    g = named.get(GUE[c])
    if m == "E":
        return TABLE[c].get(g, A)
    own = [(OWN[c][(j, named.get(j))], OV[c][j], j) for j in (ASK_F if m == "F" else ASK_R)[c]
           if (j, named.get(j)) in OWN[c]]
    if m == "F":
        return min(own)[2] if own else A
    ours = (TSC[c][g], OV[c][TABLE[c][g]], TABLE[c][g]) if g in TABLE[c] else (OV[c][A], OV[c][A], A)
    return min(own + [ours])[2]


ALL = sorted(i for i in ITEMS if all(i in routes[m] for m in ROUTES))
assert len(ALL) == len(ITEMS) or args.allow_partial, f"only {len(ALL)} of {len(ITEMS)} answers were routed in every notebook"
wrong = [(m, i) for m in ROUTES for i in ALL if routes[m][i][m] != expect(m, i)]
ASKED = {"E": {c: [GUE[c]] for c in CONDS}, "F": ASK_F, "R": ASK_R}
missing_named = {m: sum(1 for i in ALL for j in ASKED[m][ITEMS[i]["condition"]] if not routes[m][i].get(f"named_{j}"))
                 for m in TESTED}
no_verdict = {m: sum((m, routes[m][i][m], i) not in VERD for i in ALL) for m in ROUTES}


def counts(m, ids):
    q = collections.defaultdict(lambda: [0, 0, 0, 0])
    for i in ids:
        v = verdict(m, i)[0]
        c = q[ITEMS[i]["question_id"]]
        if LABEL[i] == 0:
            c[0] += 1; c[1] += v != "no"
        else:
            c[2] += 1; c[3] += v != "yes"
    return q


def bhs_of(cs):
    s = [sum(c[k] for c in cs) for k in range(4)]
    return 50 * (s[1] / s[0] + s[3] / s[2]) if s[0] and s[2] else float("nan")


def compare(m1, m2, ids):
    c1, c2 = counts(m1, ids), counts(m2, ids)
    qs = sorted(set(c1) | set(c2))
    base = bhs_of([c1[q] for q in qs]) - bhs_of([c2[q] for q in qs])
    rng = random.Random(SEED)
    diffs = []
    for _ in range(B):
        s = [rng.choice(qs) for _ in qs]
        diffs.append(bhs_of([c1[q] for q in s]) - bhs_of([c2[q] for q in s]))
    diffs = sorted(d for d in diffs if d == d)
    lo, hi = diffs[int(0.025 * len(diffs))], diffs[int(0.975 * len(diffs)) - 1]
    p = min(1.0, 2 * min(sum(d <= 0 for d in diffs), sum(d >= 0 for d in diffs)) / len(diffs))
    return dict(diff=base, lo=lo, hi=hi, p=p, questions=len(qs))


ids_c = {c: [i for i in ALL if ITEMS[i]["condition"] == c] for c in CONDS}
lines = [f"# GenreHalluEval v2 test half: routes E, F, R vs the single best judge A"
         f"{' (PREVIEW: design labels, not final)' if PREVIEW else ''}", "",
         f"Lock `lock_ghe2_v1.json` (sha256 `{sums['lock_ghe2_v1.json'][:8]}…`); test plan `test_plan_v2.json` "
         f"(sha256 `{sums['test_plan_v2.json'][:8]}…`, decided {plan['decided'][:10]}). Labels: "
         + ("design labels (PREVIEW)" if PREVIEW else f"`{args.labels}`") + ".",
         "BHS: lower is better; 50 = chance. Difference = route minus A (below 0 = the route is better).", "",
         ("## Main tests (INTERIM: " + ", ".join(f"{m} vs A" for m in TESTED) + " only; p x 6 is an upper bound of the "
          "final Holm p)" if INTERIM else "## Main tests (6, Holm-corrected)"), "",
         f"| Test | Condition | Questions | Route BHS | A BHS | Difference | 95% range | p | {'p x 6 (bound)' if INTERIM else 'p (Holm)'} | Result |",
         "|---|---|---|---|---|---|---|---|---|---|"]
rows = []
for m in TESTED:
    for c in CONDS:
        r = compare(m, "A", ids_c[c])
        rows.append(dict(test=f"{m} vs A", m=m, condition=c, **r))
order = sorted(range(len(rows)), key=lambda k: rows[k]["p"])
running = 0.0
for rank, k in enumerate(order):
    running = max(running, min(1.0, (len(rows) - rank) * rows[k]["p"]))
    rows[k]["p_holm"] = min(1.0, 6 * rows[k]["p"]) if INTERIM else running
for r in rows:
    res = "route clearly better" if r["hi"] < 0 else "route clearly worse" if r["lo"] > 0 else "no clear difference"
    sig = "significant" if r["p_holm"] < ALPHA else "not significant"
    lines.append(f"| {r['test']} | {r['condition']} | {r['questions']} | {bhs_of(list(counts(r['m'], ids_c[r['condition']]).values())):.2f} | "
                 f"{bhs_of(list(counts('A', ids_c[r['condition']]).values())):.2f} | {r['diff']:+.2f} | "
                 f"{r['lo']:+.2f} to {r['hi']:+.2f} | {r['p']:.4f} | {r['p_holm']:.4f} | {res}; {sig} |")

lines += ["", "## BHS of each route", "", "| Condition | Route | BHS | Answers | Questions | no_answer | Judges used |",
          "|---|---|---|---|---|---|---|"]
for c in CONDS:
    for m in ROUTES:
        cs = counts(m, ids_c[c])
        used = collections.Counter(verdict(m, i)[1] for i in ids_c[c])
        na = sum(verdict(m, i)[0] == "no_answer" for i in ids_c[c])
        lines.append(f"| {c} | {m} | {bhs_of(list(cs.values())):.2f} | {len(ids_c[c])} | {len(cs)} | {na} | "
                     + ", ".join(f"{j} {n}" for j, n in used.most_common()) + " |")

lines += ["", "## Each route vs A on all answers (each in its own condition; not corrected)", "",
          "| Comparison | Answers | Questions | Difference | 95% range |", "|---|---|---|---|---|"]
for m in TESTED:
    r = compare(m, "A", ALL)
    lines.append(f"| {m} vs A | {len(ALL)} | {r['questions']} | {r['diff']:+.2f} | {r['lo']:+.2f} to {r['hi']:+.2f} |")

lines += ["", "## BHS per genre (exploratory)", "", "| Condition | Genre | Questions | " + " | ".join(ROUTES) + " |",
          "|---|---|---|" + "---|" * len(ROUTES)]
for c in CONDS:
    for g in sorted({it["genre"] for it in ITEMS.values()}):
        ids = [i for i in ids_c[c] if ITEMS[i]["genre"] == g]
        sc = {m: bhs_of(list(counts(m, ids).values())) for m in ROUTES}
        lines.append(f"| {c} | {g} | {len({ITEMS[i]['question_id'] for i in ids})} | "
                     + " | ".join(f"{sc[m]:.2f}" for m in ROUTES) + " |")

# genre answers on the test half
lines += ["", "## Genre answers on the test half (agreement with our genre)", ""]
for m in TESTED:
    named = collections.defaultdict(dict)
    for i in ALL:
        for k, v in routes[m][i].items():
            if k.startswith("named_"):
                named[k[6:]][ITEMS[i]["question_id"]] = v
    human = {ITEMS[i]["question_id"]: CODE[ITEMS[i]["genre"]] for i in ALL}
    lines.append(f"- route {m}: " + "; ".join(
        f"{j} {100 * sum(v == human[q] for q, v in d.items()) / len(d):.1f}% of {len(d)}" for j, d in sorted(named.items())))

# checks and cost
pairs = collections.defaultdict(set)
for (m, j, i), v in VERD.items():
    pairs[(j, i)].add(v)
shared = [k for k in pairs if sum((m, k[0], k[1]) in VERD for m in ROUTES) > 1]
same = sum(len(pairs[k]) == 1 for k in shared)
lines += ["", "## Checks", "",
          f"- Routes recomputed from the lock and the named genres: {len(wrong)} differences "
          f"({'all equal' if not wrong else wrong[:5]}).",
          f"- Answers with no verdict from their routed judge: {no_verdict}. Empty genre answers in routes.csv: {missing_named}.",
          f"- Determinism: {len(shared)} (judge, answer) pairs were judged in more than one notebook; {same} gave the same "
          f"verdict everywhere ({100 * same / max(1, len(shared)):.2f}%). It should be 100%.", "",
          "## Cost of each route (every call in the saved logs)", "",
          "| Route | Notebook | Turn | Calls | Prompt tokens | Output tokens | Sum of latencies (h) |",
          "|---|---|---|---|---|---|---|"]
for (m, stage), t in sorted(TOK.items()):
    lines.append(f"| {m} | {NB[m]} | {stage} | {t[0]:,} | {t[1]:,} | {t[2]:,} | {t[3] / 3600:.2f} |")
lines.append("")
for m in ROUTES:
    man = manifest[m]
    lines.append(f"- {NB[m]}: models " + "; ".join(f"{j} ({v['version']})" for j, v in man["models"].items())
                 + f"; asked for the genre: {man.get('askers')}; started {man['started']}, finished {man['finished']}.")
out = rel(args.out)
out.mkdir(parents=True, exist_ok=True)
name = f"test_v1{'_interim_' + ''.join(TESTED) if INTERIM else ''}{'_PREVIEW' if PREVIEW else ''}.md"
(out / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
print("\nsaved", out / name)
