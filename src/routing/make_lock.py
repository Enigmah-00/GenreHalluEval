"""Lock every choice for Dataset 2, computed from BenHalluEval runs only (golden rule 3).

Writes results/lock/lock_v1.json (machine-readable), results/lock/lock_v1.md (for people) and lock_v1.sha256.
Refuses to overwrite an existing lock version; refuses any run record that is not BenHalluEval.

Usage: python3 -I src/routing/make_lock.py <project_root> [version]
"""
import csv
import datetime
import hashlib
import json
import random
import sys
from pathlib import Path

root = Path(sys.argv[1])
VERSION = sys.argv[2] if len(sys.argv) > 2 else "v1"
OUT = root / "results/lock"
if (OUT / f"lock_{VERSION}.json").exists():
    sys.exit(f"lock_{VERSION} already exists. A lock is never overwritten; make a new version if Dataset 2 is untouched.")
NAME = {"History, Politics & Education": "HISTORY", "Arts, Culture & Sports": "ARTS", "Science & Technology": "SCIENCE",
        "Geography & Places": "GEOGRAPHY", "Religion": "RELIGION", "Other": "OTHER"}
GENRES = list(NAME.values())
PROMPT = {"genre": "genre_v1", "context": "judge_v1", "no_context": "judge_noctx_v1"}
MIN_CELL, SEED, BOOT = 50, 2026, 1000
PKG = root / "data/final/benhallueval-qa-v1.3"
items = [r for r in csv.DictReader(open(PKG / "items.csv", encoding="utf-8")) if r["include_main"] == "yes"]
qids = sorted({r["question_id"] for r in items})
by_q = {q: [] for q in qids}
for r in items:
    by_q[r["question_id"]].append(r)
human = {r["question_id"]: NAME[r["genre"]] for r in items}
blind = {r["question_id"]: NAME[r["genre_blind_human"]] for r in csv.DictReader(open(PKG / "genre_blind200.csv", encoding="utf-8"))}
manifests = {p.parent.parent.name: json.loads(p.read_text()) for p in (root / "results").glob("*/full/manifest.json")}
run_files = {}


def log(m, turn, pid):
    p = root / "runs" / f"benhallueval__{m}__{turn}__{pid}.jsonl"
    recs = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    bad = {r.get("dataset") for r in recs} - {"benhallueval"}
    if bad:
        raise SystemExit(f"{p.name} contains records from {bad}: the lock reads BenHalluEval only (golden rule 3)")
    run_files[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return {r["key"]: r["parsed"] for r in recs}


def qcounts(v):
    out = {}
    for q in qids:
        a = [0, 0, 0, 0]
        for r in by_q[q]:
            x = v[r["item_id"]]
            if r["label"] == "0":
                a[0] += 1; a[1] += x != "no"
            else:
                a[2] += 1; a[3] += x != "yes"
        out[q] = a
    return out


def bhs(cnt, qs):
    s = [0, 0, 0, 0]
    for q in qs:
        for k in range(4):
            s[k] += cnt[q][k]
    return 50 * (s[1] / s[0] + s[3] / s[2]) if s[0] and s[2] else None


def boot_range(cnt, qs):
    rng = random.Random(SEED)
    vals = sorted(bhs(cnt, [qs[rng.randrange(len(qs))] for _ in qs]) for _ in range(BOOT))
    return [round(vals[int(0.025 * BOOT)], 2), round(vals[int(0.975 * BOOT) - 1], 2)]


models = sorted(manifests)
genre = {m: log(m, "genre", PROMPT["genre"]) for m in models}
verdict = {c: {m: log(m, "judge", PROMPT[c]) for m in models} for c in ("context", "no_context")}
# judges that ever give usable verdicts (no_answer under 50% in both conditions) form the Dataset 2 pool
usable = [m for m in models if all(sum(x == "no_answer" for x in verdict[c][m].values()) < len(items) / 2
                                   for c in verdict)]
excluded = {m: "over 50% no_answer on BenHalluEval in both conditions (no usable verdicts)" for m in models if m not in usable}

lock = {
    "lock_version": VERSION,
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "rule": "Every choice below was computed from BenHalluEval-QA v1.3 runs only, before any Dataset 2 data was made "
            "or seen. Nothing here may change after Dataset 2 is touched. A new lock version is allowed only before that.",
    "source": {"dataset": "BenHalluEval-QA v1.3", "items_csv_sha256": hashlib.sha256((PKG / "items.csv").read_bytes()).hexdigest(),
               "questions": len(qids), "answers": len(items), "run_files_sha256": run_files},
    "setup": {
        "prompts": {k: v for k, v in PROMPT.items()},
        "prompt_sha12": {k: hashlib.sha256((root / "prompts" / f"{v}.txt").read_text(encoding="utf-8").rstrip().encode()).hexdigest()[:12]
                         for k, v in PROMPT.items()},
        "temperature": 0, "seed": SEED, "parse": "strict: yes/no (judge), one of 6 codes or names (genre); else no_answer, "
                                                  "counted as an error in BHS",
        "ollama_version": "0.40.6 for every Dataset 2 run (llama3.1-8b's BenHalluEval run used 0.40.5)",
        "models": {m: {"version": manifests[m]["model_version"], "think": manifests[m]["config"].get("think"),
                       "max_new": manifests[m]["config"].get("max_new")} for m in models},
    },
    "pools": {"primary_open_weight": models, "dataset2_pool": usable, "excluded_from_dataset2": excluded,
              "secondary_with_gpt-4.1-mini": "not run; dropped unless run on BenHalluEval and locked (new version) "
                                              "before Dataset 2 is touched"},
    "min_cell_questions": MIN_CELL,
    "conditions": {},
}

for c in ("context", "no_context"):
    cnt = {m: qcounts(verdict[c][m]) for m in usable}
    overall = {m: bhs(cnt[m], qids) for m in usable}
    rank = sorted(usable, key=overall.get)
    A = rank[0]
    acc = {m: sum(genre[m][q] == human[q] for q in qids) / len(qids) for m in usable}
    guesser = max(usable, key=lambda m: (acc[m], -overall[m]))
    table = {}
    for g in GENRES:
        qs = [q for q in qids if human[q] == g]
        if len(qs) >= MIN_CELL:
            best = min(usable, key=lambda m: (bhs(cnt[m], qs), overall[m]))
            table[g] = {"judge": best, "BHS": round(bhs(cnt[best], qs), 2), "questions": len(qs)}
        else:
            table[g] = {"judge": A, "BHS": None, "questions": len(qs), "note": f"under {MIN_CELL} questions: falls back to A"}
    own = {}
    for m in usable:
        cells = {}
        for g in GENRES:
            qs = [q for q in qids if genre[m][q] == g]
            if len(qs) >= MIN_CELL:
                cells[g] = {"BHS": round(bhs(cnt[m], qs), 4), "questions": len(qs)}
        own[m] = cells
    lock["conditions"][c] = {
        "labels_on_dataset2": "passage label" if c == "context" else "world label",
        "overall_BHS": {m: {"BHS": round(overall[m], 2), "range95": boot_range(cnt[m], qids)} for m in rank},
        "A_best_single_judge": A,
        "B_top3_vote": rank[:3],
        "C_vote_of_all": {"judges": usable, "rule": "majority of yes vs no among usable verdicts; tie -> A's verdict"},
        "best_genre_guesser": {"judge": guesser, "metric": "accuracy against our human-verified genres",
                               "accuracy": {m: round(100 * acc[m], 1) for m in sorted(usable, key=acc.get, reverse=True)}},
        "D_E_judge_per_genre": table,
        "D_rule": "our (human) genre on Dataset 2 -> D_E_judge_per_genre",
        "E_rule": "best_genre_guesser names the genre (genre prompt, question + passage) -> D_E_judge_per_genre",
        "F_own_genre_scores": own,
        "F_rule": "every judge in dataset2_pool names a genre; candidates = judges whose (judge, named genre) cell is in "
                  "F_own_genre_scores; pick the lowest BHS; tie -> lower overall_BHS; no candidate -> A",
        "G_rule": "as F, but ignore judges whose named genre differs from the most common genre named by the pool "
                  "(a tie for most common keeps all judges); exploratory",
        "K_oracle": "for each answer, correct if any pool judge is correct; a ceiling, not a method",
    }

lock["confirmatory_tests"] = {
    "comparisons": ["E vs A (context)", "F vs A (context)", "F vs C (context)",
                    "E vs A (no_context)", "F vs A (no_context)", "F vs C (no_context)"],
    "statistic": "BHS difference on Dataset 2 (strict parse; no_answer = error)",
    "uncertainty": "paired bootstrap over Dataset 2 questions, 10,000 re-samples, seed 2026; 95% range reported",
    "p_value": "two-sided bootstrap p = 2 x min(share of differences <= 0, share >= 0)",
    "multiplicity": "Holm correction across the 6 comparisons at alpha 0.05",
    "everything_else": "exploratory (B, D, G, K, H/I/J if added before Dataset 2, per-genre results, Bangla-prompt runs)",
}
lock["exploratory_predictions_from_benhallueval"] = [
    "gemma4-31b judges Science better in its own genre than in ours (context): BenHalluEval 1.82 vs 2.04",
    "qwen3.5-27b judges Science better in its own genre than in ours (context): 2.45 vs 2.69",
    "qwen2.5-32b judges History better in its own genre than in ours (context): 10.34 vs 11.12",
    "Our reading: these 3 of 86 comparisons are consistent with chance; we expect them not to replicate",
]
lock["optional_baselines_H_I_J"] = "not locked yet. If used, their tables must be computed from BenHalluEval and added in a " \
                                   "new lock version before Dataset 2 is touched; otherwise they are dropped."

OUT.mkdir(parents=True, exist_ok=True)
text = json.dumps(lock, ensure_ascii=False, indent=1)
(OUT / f"lock_{VERSION}.json").write_text(text + "\n", encoding="utf-8")
digest = hashlib.sha256((text + "\n").encode()).hexdigest()
(OUT / f"lock_{VERSION}.sha256").write_text(f"{digest}  lock_{VERSION}.json\n", encoding="utf-8")

md = [f"# Locked choices for Dataset 2 ({VERSION})", "",
      f"Created {lock['created_utc']} by `src/routing/make_lock.py` from BenHalluEval-QA v1.3 runs only. "
      f"sha256 of `lock_{VERSION}.json`: `{digest}`.", "", "**" + lock["rule"] + "**", "",
      f"- Dataset 2 pool ({len(usable)} judges): {', '.join(usable)}",
      f"- Excluded (no usable verdicts): {', '.join(excluded) or 'none'}",
      "- Secondary pool (gpt-4.1-mini): not run, so dropped unless locked in a new version before Dataset 2.", ""]
for c, L in lock["conditions"].items():
    md += [f"## {'With the passage' if c == 'context' else 'Without the passage'} (`{c}`; Dataset 2 uses the {L['labels_on_dataset2']})", "",
           f"- **A, best single judge:** {L['A_best_single_judge']} (BHS {L['overall_BHS'][L['A_best_single_judge']]['BHS']})",
           f"- **B, top-3 vote:** {', '.join(L['B_top3_vote'])}",
           f"- **C, vote of all {len(usable)} pool judges** (tie → A)",
           f"- **Best genre guesser (E):** {L['best_genre_guesser']['judge']} "
           f"({L['best_genre_guesser']['accuracy'][L['best_genre_guesser']['judge']]}% accuracy)", "",
           "| Genre | D/E routes to | BHS on BenHalluEval | questions |", "|---|---|---|---|"]
    md += [f"| {g} | {t['judge']} | {t['BHS'] if t['BHS'] is not None else '– (falls back to A)'} | {t['questions']} |"
           for g, t in L["D_E_judge_per_genre"].items()]
    md += ["", "**F, own-genre scores** (BHS inside the genre each judge named; only cells with ≥50 questions):", "",
           "| Judge | " + " | ".join(GENRES) + " |", "|" + "---|" * (len(GENRES) + 1)]
    for m in usable:
        cells = L["F_own_genre_scores"][m]
        md.append(f"| {m} | " + " | ".join(f"{cells[g]['BHS']:.2f} ({cells[g]['questions']})" if g in cells else "–"
                                           for g in GENRES) + " |")
    md.append("")
md += ["## Confirmatory tests on Dataset 2", "",
       *[f"- {k}: {v}" for k, v in lock["confirmatory_tests"].items() if k != "comparisons"],
       "- comparisons: " + "; ".join(lock["confirmatory_tests"]["comparisons"]), "",
       "## Exploratory predictions", "", *[f"- {p}" for p in lock["exploratory_predictions_from_benhallueval"]], ""]
(OUT / f"lock_{VERSION}.md").write_text("\n".join(md), encoding="utf-8")
print(f"wrote {OUT}/lock_{VERSION}.json, .md, .sha256 ({digest[:16]}…)")
