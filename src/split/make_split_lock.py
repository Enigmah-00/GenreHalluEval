"""Make lock_split_v1.json from the learn-half runs of the GenreHalluEval split experiment (exploratory).

The rules are those of lock v1 and v2 (src/routing/make_lock.py, make_lock_v2.py), applied to the learn half only:
  - pool: the judges in pool.json; a judge with no_answer on half or more of the answers in both conditions is dropped;
  - A = the lowest overall BHS; best genre guesser = the highest agreement with our genre (tie: lower overall BHS);
  - judge x genre table (D/E): per our genre, the judge with the lowest BHS (tie: lower overall BHS);
  - own-genre cells (F): each judge's BHS inside the genre it named itself;
  - R = best path: the lowest of the our-genre path's cell score and the own-genre cells (tie: lower overall BHS);
    askers = the LLMs with an own-genre cell at or below the highest our-genre score, plus the guesser;
  - a cell needs at least `min_cell_questions` questions (20, pool.json; lock v1/v2 used 50 on 920 questions).
Labels: the agreed passage labels, in both conditions. Every learn record is checked (dataset, model, prompt text,
completeness) before it is used. The lock is never overwritten.

Writes <lock-dir>/lock_split_v1.json (+ .md, .sha256), copies it into the package, updates the package checksums and
the Kaggle zip (upload it as a new version of the Kaggle dataset before the test notebooks run).
Usage: python3 -I src/split/make_split_lock.py <project_root> <learn outputs zip or dir> [...]
           [--package DIR] [--lock-dir DIR] [--zip PATH] [--labels CSV]
"""
import argparse
import collections
import csv
import datetime
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("root")
ap.add_argument("inputs", nargs="+")
ap.add_argument("--package", default="data/final/GenreHalluEval-split-v1")
ap.add_argument("--lock-dir", default="results/lock")
ap.add_argument("--zip", default="release/kaggle-split/GenreHalluEval-split.zip")
ap.add_argument("--labels", default="data/labels/dataset2/passage_labels_agreed_v1.csv")
args = ap.parse_args()
root = Path(args.root)
rel = lambda p: Path(p) if Path(p).is_absolute() else root / p
PKG, LOCK_DIR, ZIP, LABELS = rel(args.package), rel(args.lock_dir), rel(args.zip), rel(args.labels)
NAME = "lock_split_v1"
for p in (LOCK_DIR / f"{NAME}.json", PKG / f"{NAME}.json"):
    if p.exists():
        raise SystemExit(f"{p} already exists. A lock is never overwritten.")
DATASET = "ghesplit_learn"
CONDS = ("context", "no_context")
STAGE_KEYS = ("genre", "judge:context", "judge:no_context")
CODE = {"History, Politics & Education": "HISTORY", "Arts, Culture & Sports": "ARTS", "Science & Technology": "SCIENCE",
        "Geography & Places": "GEOGRAPHY", "Religion": "RELIGION", "Other": "OTHER"}
GENRES = list(CODE.values())
sha = lambda b: hashlib.sha256(b).hexdigest()

# ---- the package ----
sums = dict(l.split("  ", 1)[::-1] for l in (PKG / "checksums.sha256").read_text(encoding="utf-8").splitlines() if l.strip())
sums = {k.strip(): v for k, v in sums.items()}
for name in ("learn_items.csv", "pool.json"):
    assert sha((PKG / name).read_bytes()) == sums[name], f"{name} differs from the package checksums"
cfg = json.loads((PKG / "pool.json").read_text(encoding="utf-8"))
POOL, LANG, MIN_CELL = cfg["pool"], cfg["prompt_language"], cfg["min_cell_questions"]
PIDS = {lang: dict(zip(STAGE_KEYS, p)) for lang, p in cfg["prompt_ids"].items()}
TPL = {lang: {k: (PKG / "prompts" / f"{pid}.txt").read_text(encoding="utf-8").rstrip() for k, pid in ids.items()}
       for lang, ids in PIDS.items()}
PSHA = {lang: {k: sha(t.encode("utf-8"))[:12] for k, t in ts.items()} for lang, ts in TPL.items()}
SLOT = re.compile(r"\{(context|question|answer)\}")
fill = lambda t, **v: SLOT.sub(lambda m: v[m.group(1)], t)
rows = list(csv.DictReader(open(PKG / "learn_items.csv", encoding="utf-8")))
qinfo = {r["question_id"]: r for r in rows}
QIDS = sorted(qinfo)
human = {q: CODE[r["genre"]] for q, r in qinfo.items()}
by_cond = {c: {r["item_id"]: r for r in rows if r["condition"] == c} for c in CONDS}
lab_rows = list(csv.DictReader(open(LABELS, encoding="utf-8-sig")))
label = {r["item_id"]: r["label"].strip() for r in lab_rows}
assert all(label.get(i) in ("0", "1") for i in by_cond["context"]), "every learn answer needs an agreed 0/1 label"


def prompt_of(m, stage, key):
    lang = LANG[m]
    if stage == "genre":
        q = qinfo[key]
        return fill(TPL[lang]["genre"], question=q["question"], context=q["context"])
    r = by_cond[stage.split(":")[1]][key]
    if stage == "judge:context":
        return fill(TPL[lang]["judge:context"], context=r["context"], question=r["question"], answer=r["answer"])
    return fill(TPL[lang]["judge:no_context"], question=r["question"], answer=r["answer"])


# ---- the learn runs (one or more outputs zips / folders) ----
files, manifests = {}, []
for src in args.inputs:
    p = Path(src)
    z = zipfile.ZipFile(p) if p.suffix == ".zip" else None
    names = z.namelist() if z else [str(x.relative_to(p)) for x in p.rglob("*") if x.is_file()]
    read = (lambda n: z.read(n)) if z else (lambda n: (p / n).read_bytes())
    for n in names:
        if re.fullmatch(rf"runs/{DATASET}__.+\.jsonl", n):
            assert Path(n).name not in files, f"{Path(n).name} is in two inputs: give each model's runs once"
            files[Path(n).name] = read(n)
        elif n.endswith("manifest.json") and "/learn/" in f"/{n}":
            manifests.append(json.loads(read(n)))
assert manifests, "no learn manifest found"
for m in manifests:
    assert m["notebook"] == "learn" and m["run_mode"] == "full" and not m["partial"] and m["truncated"] == 0, \
        "every learn session must be a finished full run (resume a partial one first)"
    for name in ("learn_items.csv", "pool.json", *[f"prompts/{pid}.txt" for ids in PIDS.values() for pid in ids.values()]):
        assert m["dataset_checksums"].get(name) == sums[name], f"a learn session used a different {name}"
versions = {k: v for m in manifests for k, v in m["models"].items()}

parsed = {}            # (model, stage) -> key -> parsed
problems = collections.Counter()
for m in POOL:
    lang = LANG[m]
    for stage in STAGE_KEYS:
        fname = f"{DATASET}__{m}__{stage.split(':')[0]}__{PIDS[lang][stage]}.jsonl"
        assert fname in files, f"missing {fname}: run {m} in the learn notebook"
        recs = {}
        for line in files[fname].decode("utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                recs[r["key"]] = r                          # a later line (a retry) replaces an earlier one
        want = QIDS if stage == "genre" else sorted(by_cond[stage.split(":")[1]])
        assert sorted(recs) == want, f"{fname}: {len(recs)} records, {len(want)} expected"
        for k, r in recs.items():
            assert r["dataset"] == DATASET and r["model_key"] == m and r["status"] != "error", (fname, k)
            assert r["prompt_sha"] == PSHA[lang][stage] and r["temperature"] == 0, (fname, k)
            assert r["prompt_hash"] == sha(prompt_of(m, stage, k).encode("utf-8"))[:16], f"{fname} {k}: prompt differs"
            problems[(m, stage, r["status"])] += 1
        parsed[(m, stage)] = {k: r["parsed"] for k, r in recs.items()}

# ---- the lock rules ----
genre = {m: parsed[(m, "genre")] for m in POOL}
verdict = {c: {m: parsed[(m, f"judge:{c}")] for m in POOL} for c in CONDS}
n_items = len(by_cond["context"])
usable = [m for m in POOL if not all(sum(v == "no_answer" for v in verdict[c][m].values()) >= n_items / 2 for c in CONDS)]
excluded = {m: "no_answer on half or more of the learn answers in both conditions" for m in POOL if m not in usable}
qrows = collections.defaultdict(list)
for i, r in by_cond["context"].items():
    qrows[r["question_id"]].append(i)


def counts(c, m):
    out = {}
    for q in QIDS:
        a = [0, 0, 0, 0]
        for i in qrows[q]:
            v = verdict[c][m][i]
            if label[i] == "0":
                a[0] += 1; a[1] += v != "no"
            else:
                a[2] += 1; a[3] += v != "yes"
        out[q] = a
    return out


def bhs(cnt, qs):
    s = [sum(cnt[q][k] for q in qs) for k in range(4)]
    return 50 * (s[1] / s[0] + s[3] / s[2]) if s[0] and s[2] else None


lock = dict(
    lock_version="split_v1",
    created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    rule="Exploratory split experiment: every choice below was computed from the learn half of GenreHalluEval only, "
         "before any test-half answer was judged. The test half never changes it.",
    source=dict(package=PKG.name, learn_items_sha256=sums["learn_items.csv"], pool_json_sha256=sums["pool.json"],
                labels_file=str(args.labels), labels_sha256=sha(LABELS.read_bytes()),
                run_files_sha256={n: sha(b) for n, b in sorted(files.items())}, questions=len(QIDS), answers=n_items),
    setup=dict(prompt_ids=PIDS, prompt_sha12=PSHA, prompt_language=LANG, temperature=0, seed=cfg["seed"],
               models={m: versions.get(m) for m in POOL},
               record_status={f"{m} {s}": {st: n for (mm, ss, st), n in problems.items() if mm == m and ss == s}
                              for m in POOL for s in STAGE_KEYS}),
    pools=dict(pool=POOL, usable=usable, excluded=excluded),
    min_cell_questions=MIN_CELL,
    conditions={}, R_best_path=dict(per_condition={}),
)
for c in CONDS:
    cnt = {m: counts(c, m) for m in usable}
    overall = {m: bhs(cnt[m], QIDS) for m in usable}
    rank = sorted(usable, key=lambda m: (overall[m], m))
    A = rank[0]
    acc = {m: sum(genre[m][q] == human[q] for q in QIDS) / len(QIDS) for m in usable}
    guesser = max(usable, key=lambda m: (acc[m], -overall[m]))
    table = {}
    for g in GENRES:
        qs = [q for q in QIDS if human[q] == g]
        if len(qs) >= MIN_CELL:
            best = min(usable, key=lambda m: (bhs(cnt[m], qs), overall[m]))
            table[g] = dict(judge=best, BHS=round(bhs(cnt[best], qs), 2), questions=len(qs))
        else:
            table[g] = dict(judge=A, BHS=None, questions=len(qs), note=f"under {MIN_CELL} questions: falls back to A")
    own = {}
    for m in usable:
        cells = {}
        for g in GENRES:
            qs = [q for q in QIDS if genre[m][q] == g]
            if len(qs) >= MIN_CELL:
                cells[g] = dict(BHS=round(bhs(cnt[m], qs), 4), questions=len(qs))
        own[m] = cells
    ov2 = {m: round(overall[m], 2) for m in usable}
    e_max = max([v["BHS"] for v in table.values() if v["BHS"] is not None] + [ov2[A]])
    askers = sorted({m for m, cells in own.items() for v in cells.values() if v["BHS"] <= e_max} | {guesser})
    lock["conditions"][c] = dict(
        overall_BHS={m: dict(BHS=ov2[m]) for m in rank}, A_best_single_judge=A,
        best_genre_guesser=dict(judge=guesser, accuracy={m: round(100 * acc[m], 1) for m in sorted(usable, key=acc.get, reverse=True)}),
        D_E_judge_per_genre=table, F_own_genre_scores=own)
    lock["R_best_path"]["per_condition"][c] = dict(
        guesser=guesser, A=A, highest_our_genre_score=e_max, askers=askers,
        own_genre_cells_that_can_win={f"{m} {g}": v["BHS"] for m, cells in sorted(own.items()) for g, v in cells.items()
                                      if v["BHS"] <= e_max})
lock["tests_on_the_test_half"] = dict(
    main="R vs A, with the passage and without it (2 tests, Holm), paired bootstrap over test questions, 10,000 "
         "re-samples, seed 2026, two-sided; exploratory like the whole experiment",
    also="D, E, F vs A; determinism of A's judge across the two test notebooks")

LOCK_DIR.mkdir(parents=True, exist_ok=True)
text = json.dumps(lock, ensure_ascii=False, indent=1) + "\n"
(LOCK_DIR / f"{NAME}.json").write_text(text, encoding="utf-8")
digest = sha(text.encode("utf-8"))
(LOCK_DIR / f"{NAME}.sha256").write_text(f"{digest}  {NAME}.json\n", encoding="utf-8")
md = [f"# Lock for the GenreHalluEval split experiment ({NAME}, exploratory)", "",
      f"Created {lock['created_utc']} by `src/split/make_split_lock.py` from the learn half only ({len(QIDS)} questions, "
      f"{n_items} answers, each judged with and without the passage). sha256 `{digest}`.", "",
      f"- Pool: {', '.join(f'{m} ({LANG[m]})' for m in POOL)}; usable: {', '.join(usable)}; excluded: {excluded or 'none'}",
      f"- Cells need {MIN_CELL}+ questions.", ""]
for c in CONDS:
    L, R = lock["conditions"][c], lock["R_best_path"]["per_condition"][c]
    md += [f"## {'With the passage' if c == 'context' else 'Without the passage'}", "",
           f"- A = {L['A_best_single_judge']}; best genre guesser = {R['guesser']}; askers = {', '.join(R['askers'])}",
           "- Overall BHS: " + ", ".join(f"{m} {v['BHS']}" for m, v in L["overall_BHS"].items()), "",
           "| Genre | Table judge | BHS | Questions |", "|---|---|---|---|"]
    md += [f"| {g} | {v['judge']} | {v['BHS'] if v['BHS'] is not None else '– (A)'} | {v['questions']} |"
           for g, v in L["D_E_judge_per_genre"].items()]
    md += ["", "Own-genre cells: " + "; ".join(f"{m} {g} {v['BHS']} ({v['questions']})" for m, cells in
                                                L["F_own_genre_scores"].items() for g, v in cells.items()), ""]
(LOCK_DIR / f"{NAME}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))

# ---- into the package (a new Kaggle version) ----
shutil.copyfile(LOCK_DIR / f"{NAME}.json", PKG / f"{NAME}.json")
with open(PKG / "checksums.sha256", "w", encoding="utf-8") as f:
    for p in sorted(x for x in PKG.rglob("*") if x.is_file() and x.name != "checksums.sha256"):
        f.write(f"{sha(p.read_bytes())}  {p.relative_to(PKG)}\n")
ZIP.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(x for x in PKG.rglob("*") if x.is_file()):
        z.write(p, Path("GenreHalluEval-split") / p.relative_to(PKG))
print(f"\nlock: {LOCK_DIR / (NAME + '.json')} (sha256 {digest})\npackage updated: {PKG}\nzip for Kaggle (new version): {ZIP}")
