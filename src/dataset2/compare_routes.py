"""Score and compare the two GenreHalluEval notebooks: the routed judges (R, D, E, F) vs the single best judge (A).

Each answer of Set B (items.csv) is scored in its own condition. Confirmatory (preregistration section 4, lock v2):
R vs A with the passage and without it = 2 comparisons, two-sided, Holm-corrected at alpha 0.05. Exploratory: D, E, F
vs A per condition; every route vs A on all answers together (each in its own condition); per genre; and a
determinism check (answers the routed notebook gave to the same judge as A must get the same verdict).

BHS = 1/2 x (share of correct answers not called "no" + share of hallucinated answers not called "yes") x 100;
no_answer counts as an error. Paired bootstrap over questions: 10,000 re-samples, seed 2026; 95% range;
p = 2 x min(share of differences <= 0, share >= 0).

Labels: --labels <csv> with item_id and either `label` (0 correct, 1 hallucinated, "exclude") or `passage_label` and
`world_label` (the label matching the answer's condition is used). Without --labels the design labels are used and
every output is marked PREVIEW.

Usage: python3 -I src/dataset2/compare_routes.py <project_root> --routed <zip|dir> --single <zip|dir>
           [--package data/final/GenreHalluEval-v1.1] [--labels <csv>] [--out results/genrehallueval] [--allow-partial]
           [--dataset genrehallueval] [--items items.csv] [--main R]
  (the split experiment: --dataset ghesplit_test --package data/final/GenreHalluEval-split-v1 --items test_items.csv)
  (GenreHalluEval v2: --dataset ghe2_test --package data/final/GenreHalluEval-v2.0 --items test_items.csv --main R,F
   --labels data/labels/genrehallueval_v2/labels_v2.0.csv; main tests R vs A and F vs A per condition, Holm over 4)
"""
import argparse
import collections
import csv
import io
import json
import random
import zipfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("root")
ap.add_argument("--routed", required=True)
ap.add_argument("--single", required=True)
ap.add_argument("--package", default="data/final/GenreHalluEval-v1.1")
ap.add_argument("--labels")
ap.add_argument("--out", default="results/genrehallueval")
ap.add_argument("--allow-partial", action="store_true")
ap.add_argument("--dataset", default="genrehallueval")
ap.add_argument("--items", default="items.csv")
ap.add_argument("--main", default="R", help="routes tested against A in the confirmatory table, e.g. R or R,F")
args = ap.parse_args()
root = Path(args.root)
SEED, B, ALPHA = 2026, 10_000, 0.05
MAIN = [m.strip() for m in args.main.split(",") if m.strip()]
assert MAIN and all(m in ("R", "D", "E", "F") for m in MAIN), args.main
CONFIRMATORY = [(m, "A", c) for m in MAIN for c in ("context", "no_context")]
ROUTES_ALL = ["A", "R", "D", "E", "F"]


class Output:
    """A notebook's outputs zip or unpacked folder."""

    def __init__(self, path, kind):
        self.path, self.kind = Path(path), kind
        self.z = zipfile.ZipFile(self.path) if self.path.suffix == ".zip" else None

    def names(self):
        names = self.z.namelist() if self.z else [str(p.relative_to(self.path)) for p in self.path.rglob("*") if p.is_file()]
        # a zip re-packed on a Mac adds __MACOSX/ and ._ copies of every file: skip them
        return [n for n in names if "__MACOSX/" not in n and not Path(n).name.startswith("._")]

    def read(self, name):
        return self.z.read(name).decode("utf-8") if self.z else (self.path / name).read_text(encoding="utf-8")

    def one(self, suffix):
        hits = [n for n in self.names() if n.endswith(suffix) and f"/{self.kind}/" in f"/{n}"]
        assert len(hits) == 1, (self.path, suffix, hits)
        return hits[0]


def read_csv_text(text):
    return list(csv.DictReader(io.StringIO(text)))


pkg = root / args.package if not Path(args.package).is_absolute() else Path(args.package)
with open(pkg / args.items, encoding="utf-8", newline="") as f:
    ITEMS = {r["item_id"]: r for r in csv.DictReader(f)}

if args.labels:
    with open(args.labels, encoding="utf-8-sig", newline="") as f:
        lab = list(csv.DictReader(f))
    LABEL = {}
    for r in lab:
        if r["item_id"] not in ITEMS:          # the labels file can cover more answers (e.g. the split's test half)
            continue
        cond = ITEMS[r["item_id"]]["condition"]
        v = r["label"] if "label" in r else r["passage_label" if cond == "context" else "world_label"]
        LABEL[r["item_id"]] = None if v.strip().lower() == "exclude" else int(v)
    missing = set(ITEMS) - set(LABEL)
    assert not missing, f"{len(missing)} answers have no agreed label"
    PREVIEW = False
else:
    LABEL = {k: int(r["design_label"]) for k, r in ITEMS.items()}
    PREVIEW = True

outs = {"routed": Output(args.routed, "routed"), "single_best": Output(args.single, "single_best")}
manifest = {k: json.loads(o.read(o.one("manifest.json"))) for k, o in outs.items()}
for k, m in manifest.items():
    if m["partial"] and not args.allow_partial:
        raise SystemExit(f"{k} run is PARTIAL: resume it first (or pass --allow-partial for a look only)")
    assert m["run_mode"] == "full" or args.allow_partial, f"{k} is a {m['run_mode']} run"
routes = {k: {r["item_id"]: r for r in read_csv_text(o.read(o.one("routes.csv")))} for k, o in outs.items()}

VERD, TOKENS = {}, collections.defaultdict(lambda: [0, 0, 0, 0.0])
for k, o in outs.items():
    for n in o.names():
        if f"runs/{args.dataset}__" in n and "__judge__" in n and n.endswith(".jsonl"):
            for line in o.read(n).splitlines():
                if line.strip():
                    r = json.loads(line)
                    if r["status"] == "error":
                        continue
                    item = ITEMS[r["item_id"]]
                    assert r["condition"] == item["condition"], (n, r["item_id"])
                    VERD[(k, r["model_key"], r["item_id"])] = r["parsed"]     # a later line replaces an earlier one
        if f"runs/{args.dataset}__" in n and n.endswith(".jsonl"):
            for line in o.read(n).splitlines():
                if line.strip():
                    r = json.loads(line)
                    t = TOKENS[(k, r["stage"])]
                    t[0] += 1; t[1] += r["prompt_tokens"] or 0; t[2] += r["output_tokens"] or 0; t[3] += r["latency_s"] or 0


def verdict(method, item_id):
    k = "single_best" if method == "A" else "routed"
    judge = routes[k][item_id][method]
    return VERD.get((k, judge, item_id), "no_answer"), judge


def keep(item_id, condition=None, genre=None):
    it = ITEMS[item_id]
    return (LABEL[item_id] is not None and (condition is None or it["condition"] == condition)
            and (genre is None or it["genre"] == genre))


def counts(method, ids):
    """Per question: [correct answers, false alarms, hallucinated answers, misses]."""
    q = collections.defaultdict(lambda: [0, 0, 0, 0])
    for i in ids:
        v = verdict(method, i)[0]
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
    z = [0, 0, 0, 0]
    base = bhs_of([c1.get(q, z) for q in qs]) - bhs_of([c2.get(q, z) for q in qs])
    rng, diffs = random.Random(SEED), []
    for _ in range(B):
        s = [qs[rng.randrange(len(qs))] for _ in qs]
        diffs.append(bhs_of([c1.get(q, z) for q in s]) - bhs_of([c2.get(q, z) for q in s]))
    diffs = sorted(d for d in diffs if d == d)
    lo, hi = diffs[int(0.025 * len(diffs))], diffs[int(0.975 * len(diffs)) - 1]
    p = min(1.0, 2 * min(sum(d <= 0 for d in diffs), sum(d >= 0 for d in diffs)) / len(diffs))
    return dict(diff=base, lo=lo, hi=hi, p=p, questions=len(qs))


def score(method, ids):
    c = counts(method, ids)
    na = sum(verdict(method, i)[0] == "no_answer" for i in ids)
    return dict(BHS=bhs_of(list(c.values())), answers=len(ids), questions=len(c), no_answer=na)


ALL = sorted(i for i in ITEMS if i in routes["routed"] and i in routes["single_best"])
assert len(ALL) == len(ITEMS) or args.allow_partial, f"only {len(ALL)} of {len(ITEMS)} answers were routed in both runs"
lines = [f"# GenreHalluEval{'' if args.dataset == 'genrehallueval' else f' ({args.dataset})'}: routed judges vs the single best judge"
         f"{' (PREVIEW: design labels, not final)' if PREVIEW else ''}",
         "", f"Routed run: `{outs['routed'].path.name}`; single-best run: `{outs['single_best'].path.name}`. Labels: "
         + ("design labels (PREVIEW)" if PREVIEW else f"`{args.labels}` (agreed human labels)") + ".",
         f"Excluded answers: {sum(v is None for v in LABEL.values())}.", "",
         "BHS: lower is better; 50 = chance. Difference = route minus A (below 0 = the route is better).", ""]

# confirmatory
rows = []
for m1, m2, c in CONFIRMATORY:
    ids = [i for i in ALL if keep(i, c)]
    rows.append(dict(test=f"{m1} vs {m2}", condition=c, **compare(m1, m2, ids)))
order = sorted(range(len(rows)), key=lambda k: rows[k]["p"])
running = 0.0
for rank, k in enumerate(order):
    running = max(running, min(1.0, (len(rows) - rank) * rows[k]["p"]))
    rows[k]["p_holm"] = running
lines += [f"## Confirmatory tests ({len(rows)}, Holm-corrected)", "",
          "| Test | Condition | Questions | Difference | 95% range | p | p (Holm) | Result |", "|---|---|---|---|---|---|---|---|"]
for r in rows:
    res = ("route clearly better" if r["hi"] < 0 else "route clearly worse" if r["lo"] > 0 else "no clear difference")
    sig = "significant" if r["p_holm"] < ALPHA else "not significant"
    lines.append(f"| {r['test']} | {r['condition']} | {r['questions']} | {r['diff']:+.2f} | {r['lo']:+.2f} to {r['hi']:+.2f} "
                 f"| {r['p']:.4f} | {r['p_holm']:.4f} | {res}; {sig} |")

# scores per route and condition
lines += ["", "## BHS of each route", "", "| Condition | Route | BHS | Answers | Questions | no_answer | Judges used |",
          "|---|---|---|---|---|---|---|"]
for c in ("context", "no_context"):
    ids = [i for i in ALL if keep(i, c)]
    for m in ROUTES_ALL:
        s = score(m, ids)
        used = collections.Counter(verdict(m, i)[1] for i in ids)
        lines.append(f"| {c} | {m} | {s['BHS']:.2f} | {s['answers']} | {s['questions']} | {s['no_answer']} | "
                     + ", ".join(f"{j} {n}" for j, n in used.most_common()) + " |")

# exploratory comparisons
lines += ["", "## Exploratory comparisons (no correction)", "",
          "| Comparison | Answers | Questions | Difference | 95% range |", "|---|---|---|---|---|"]
explore = [(f"{m} vs A, {c}", m, [i for i in ALL if keep(i, c)]) for m in ("D", "E", "F") if m not in MAIN
           for c in ("context", "no_context")]
explore += [(f"{m} vs A, all answers (each in its own condition)", m, [i for i in ALL if keep(i)]) for m in ("R", "D", "E", "F")]
for name, m, ids in explore:
    r = compare(m, "A", ids)
    lines.append(f"| {name} | {len(ids)} | {r['questions']} | {r['diff']:+.2f} | {r['lo']:+.2f} to {r['hi']:+.2f} |")

# per genre
lines += ["", "## BHS per genre (exploratory)", "", "| Condition | Genre | Questions | A | R | D | E | F |", "|---|---|---|---|---|---|---|---|"]
for c in ("context", "no_context"):
    for g in sorted({it["genre"] for it in ITEMS.values()}):
        ids = [i for i in ALL if keep(i, c, g)]
        if ids:
            sc = {m: score(m, ids) for m in ROUTES_ALL}
            lines.append(f"| {c} | {g} | {sc['A']['questions']} | " + " | ".join(f"{sc[m]['BHS']:.2f}" for m in ROUTES_ALL) + " |")

# determinism and cost
same = [(i, m) for i in ALL for m in "RDEF" if routes["routed"][i][m] == routes["single_best"][i]["A"]]
agree = sum(verdict(m, i)[0] == verdict("A", i)[0] for i, m in same)
lines += ["", "## Checks", "",
          f"- Determinism: {len(same)} (answer, route) pairs went to the same judge as A; the two notebooks gave the same "
          f"verdict in {agree} ({100 * agree / max(1, len(same)):.2f}%). It should be 100% (temperature 0, same setup).",
          "- Cost (every call in the saved logs):", ""]
lines += ["| Notebook | Turn | Calls | Prompt tokens | Output tokens | Sum of latencies (h) |", "|---|---|---|---|---|---|"]
for (k, stage), t in sorted(TOKENS.items()):
    lines.append(f"| {k} | {stage} | {t[0]} | {t[1]:,} | {t[2]:,} | {t[3] / 3600:.2f} |")
for k, m in manifest.items():
    lines.append(f"\n{k}: models " + "; ".join(f"{j} ({v['version']})" for j, v in m["models"].items())
                 + f"; started {m['started']}, finished {m['finished']}.")

out = root / args.out if not Path(args.out).is_absolute() else Path(args.out)
out.mkdir(parents=True, exist_ok=True)
name = "comparison_PREVIEW.md" if PREVIEW else "comparison.md"
(out / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
print("\nsaved", out / name)
