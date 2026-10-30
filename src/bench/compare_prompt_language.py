"""Side experiment: the same judge with English prompts (genre_v1, judge_v1, judge_noctx_v1) vs Bangla prompts
(genre_bn_v1, judge_bn_v1, judge_noctx_bn_v1), on the same 4,600 answers. Exploratory (decided after the English
results); never feeds the main analysis.

Usage: python3 -I src/bench/compare_prompt_language.py <project_root>
Writes results/bangla_prompts/comparison.md and comparison_*.csv for every model that has both runs.
"""
import csv
import json
import random
import sys
from pathlib import Path

root = Path(sys.argv[1])
OUT = root / "results/bangla_prompts"
NAME = {"History, Politics & Education": "HISTORY", "Arts, Culture & Sports": "ARTS", "Science & Technology": "SCIENCE",
        "Geography & Places": "GEOGRAPHY", "Religion": "RELIGION", "Other": "OTHER"}
GENRES = ["HISTORY", "ARTS", "SCIENCE", "GEOGRAPHY", "RELIGION"]
PROMPTS = {"en": {"genre": "genre_v1", "context": "judge_v1", "no_context": "judge_noctx_v1"},
           "bn": {"genre": "genre_bn_v1", "context": "judge_bn_v1", "no_context": "judge_noctx_bn_v1"}}
items = [r for r in csv.DictReader(open(root / "data/final/benhallueval-qa-v1.3/items.csv", encoding="utf-8"))
         if r["include_main"] == "yes"]
qids = sorted({r["question_id"] for r in items})
qi = {q: i for i, q in enumerate(qids)}
human = {r["question_id"]: NAME[r["genre"]] for r in items}
blind = {r["question_id"]: NAME[r["genre_blind_human"]] for r in csv.DictReader(
    open(root / "data/final/benhallueval-qa-v1.3/genre_blind200.csv", encoding="utf-8"))}
rng = random.Random(2026)
SAMPLES = [[rng.randrange(len(qids)) for _ in qids] for _ in range(1000)]


def log(model, turn, pid):
    p = root / "runs" / f"benhallueval__{model}__{turn}__{pid}.jsonl"
    return {r["key"]: r["parsed"] for r in map(json.loads, p.read_text(encoding="utf-8").splitlines()) if r} \
        if p.exists() else {}


def counts(v, keep=lambda r: True):
    agg = [[0, 0, 0, 0] for _ in qids]
    for r in items:
        if not keep(r):
            continue
        a, x = agg[qi[r["question_id"]]], v[r["item_id"]]
        if r["label"] == "0":
            a[0] += 1; a[1] += x != "no"
        else:
            a[2] += 1; a[3] += x != "yes"
    return agg


def bhs(agg, idx):
    s = [0, 0, 0, 0]
    for i in idx:
        for k in range(4):
            s[k] += agg[i][k]
    return 50 * (s[1] / s[0] + s[3] / s[2]) if s[0] and s[2] else None


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = {}, {}
    for a, b in pairs:
        ca[a] = ca.get(a, 0) + 1; cb[b] = cb.get(b, 0) + 1
    pe = sum(ca[g] * cb.get(g, 0) for g in ca) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def write(name, rows):
    if rows:
        with open(OUT / name, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def md(rows, cols):
    return "\n".join(["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
                     + ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows])


models = sorted(p.parent.parent.name for p in OUT.glob("*/full/manifest.json"))
judge_rows, genre_rows, per_genre = [], [], []
full = range(len(qids))
for m in models:
    for c in ("context", "no_context"):
        en, bn = log(m, "judge", PROMPTS["en"][c]), log(m, "judge", PROMPTS["bn"][c])
        if len(en) != len(items) or len(bn) != len(items):
            continue
        ae, ab = counts(en), counts(bn)
        d = sorted(bhs(ab, s) - bhs(ae, s) for s in SAMPLES)
        row = {"model": m, "condition": c}
        for tag, v, agg in (("en", en, ae), ("bn", bn, ab)):
            na = sum(x == "no_answer" for x in v.values())
            answered = counts(v, keep=lambda r, v=v: v[r["item_id"]] != "no_answer")
            row.update({f"BHS_{tag}": f"{bhs(agg, full):.2f}", f"no_answer_{tag}": na,
                        f"BHS_answered_{tag}": f"{bhs(answered, full):.2f}" if bhs(answered, full) is not None else "–",
                        f"says_yes_{tag}": f"{100 * sum(x == 'yes' for x in v.values()) / len(v):.0f}%"})
        row.update(bn_minus_en=f"{bhs(ab, full) - bhs(ae, full):+.2f}", range95=f"{d[25]:+.2f} to {d[974]:+.2f}",
                   same_verdict=f"{100 * sum(en[k] == bn[k] for k in en) / len(en):.0f}%")
        judge_rows.append(row)
        for g in GENRES:
            members = {i for i, q in enumerate(qids) if human[q] == g}
            per_genre.append({"model": m, "condition": c, "genre": g, "questions": len(members),
                              "BHS_en": f"{bhs(ae, members):.2f}", "BHS_bn": f"{bhs(ab, members):.2f}",
                              "bn_minus_en": f"{bhs(ab, members) - bhs(ae, members):+.2f}"})
    ge, gb = log(m, "genre", PROMPTS["en"]["genre"]), log(m, "genre", PROMPTS["bn"]["genre"])
    if len(ge) == len(qids) and len(gb) == len(qids):
        row = {"model": m}
        for tag, g in (("en", ge), ("bn", gb)):
            row[f"accuracy_{tag}"] = f"{100 * sum(g[q] == human[q] for q in qids) / len(qids):.1f}"
            row[f"kappa_{tag}"] = f"{kappa([(human[q], g[q]) for q in qids]):.3f}"
            row[f"kappa_blind_{tag}"] = f"{kappa([(blind[q], g[q]) for q in qids if q in blind]):.3f}"
            row[f"no_answer_{tag}"] = sum(x == "no_answer" for x in g.values())
            row[f"named_HISTORY_{tag}"] = sum(x == "HISTORY" for x in g.values())
        genre_rows.append(row)

write("comparison_judge.csv", judge_rows)
write("comparison_genre.csv", genre_rows)
write("comparison_by_genre.csv", per_genre)
text = ["# English vs Bangla prompts (side experiment, exploratory)", "",
        f"Models with both runs: {', '.join(sorted({r['model'] for r in judge_rows})) or 'none yet'}. Same 4,600 answers;",
        "only the prompt language differs. BHS: lower is better. bn_minus_en < 0 means Bangla prompts help. The range is",
        "a paired bootstrap over questions (1,000 re-samples). Built by `src/bench/compare_prompt_language.py`.", "",
        "## Judging", "",
        md(judge_rows, ["model", "condition", "BHS_en", "BHS_bn", "bn_minus_en", "range95", "no_answer_en", "no_answer_bn",
                        "BHS_answered_en", "BHS_answered_bn", "says_yes_en", "says_yes_bn", "same_verdict"]), "",
        "## Genre guessing", "",
        md(genre_rows, ["model", "accuracy_en", "accuracy_bn", "kappa_en", "kappa_bn", "kappa_blind_en", "kappa_blind_bn",
                        "no_answer_en", "no_answer_bn", "named_HISTORY_en", "named_HISTORY_bn"]), "",
        "## Judging per genre (our genres)", "",
        md(per_genre, ["model", "condition", "genre", "questions", "BHS_en", "BHS_bn", "bn_minus_en"]), ""]
(OUT / "comparison.md").write_text("\n".join(text) + "\n", encoding="utf-8")
print(f"wrote {OUT / 'comparison.md'} for {len(genre_rows)} model(s)")
