"""Build the two GenreHalluEval (Dataset 2) notebooks from the BenHalluEval benchmark notebook's engine.

notebooks/genrehallueval_routed.ipynb       every answer goes to the judge that a route picks, with the tables
                                            locked on BenHalluEval (lock_v2.json):
                                              R = best path (confirmatory): the lower BenHalluEval score of the
                                                  our-genre path and the own-genre paths;
                                              D, E, F (exploratory): our genre label; the best genre guesser's genre;
                                                  own-genre routing over the same LLMs.
                                            Only the LLMs whose genre can change a route are asked for the genre
                                            ("askers" in the lock), and only the judges a route picks judge.
notebooks/genrehallueval_single_best.ipynb  the single best judge (A = gemma4-31b in both conditions) judges every
                                            answer.

Each answer is judged once, in its own condition (items.csv column `condition`): `context` = passage + question +
answer (judge_v1), `no_context` = question + answer (judge_noctx_v1). The engine (prompt files, parsing, Ollama setup,
logging, resume, time budget) is copied verbatim from src/bench/make_notebook.py with the patches below, so the setup
is the same as on BenHalluEval. The notebooks only judge; src/dataset2/compare_routes.py scores and compares them.

Usage: python3 -I src/dataset2/make_notebooks.py <project_root>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import make_notebook as base                                  # noqa: E402  (builds the BenHalluEval cells on import)

LOCK_SHA256 = "6d3c1d29cb8159d5f74300c799ce040c9a7c737dfb68b5c292a2a2aa948c9137"


def engine(marker, *patches):
    hits = [text for kind, text in base.CELLS if kind == "code" and marker in text]
    assert len(hits) == 1, marker
    text = hits[0]
    for old, new in patches:
        assert text.count(old) == 1, old[:80]
        text = text.replace(old, new)
    return text


IMPORTS = engine(
    "T0 = time.time()",
    ('DATASET = "benhallueval"            # this notebook only ever reads BenHalluEval (golden rule 3)',
     'DATASET = "genrehallueval"          # Dataset 2, test-only: this notebook never makes or changes a choice'),
    ('hits = sorted({str(Path(h).parent) for h in hits if (Path(h).parent / "prompts" / "judge_v1.txt").exists()})',
     'hits = sorted({str(Path(h).parent) for h in hits if (Path(h).parent / "lock_v2.json").exists()})'),
    ('''raise Stop(f"Expected exactly one BenHalluEval-QA dataset under /kaggle/input, found {hits}. "
                   "Add it with 'Add Input' (section 1a).")''',
     '''raise Stop(f"Expected exactly one GenreHalluEval dataset (a folder with items.csv and lock_v2.json) under "
                   f"/kaggle/input, found {hits}. Add it with 'Add Input' (step 2 at the top).")'''),
    ('''if any(bad in str(DATA_DIR).lower() for bad in ("dataset2", "dataset-2", "banglarqa")):
    raise Stop("This notebook reads BenHalluEval only. Dataset 2 is test-only and is never used to make "
               "choices (golden rule 3).")
''', ""),
)
MODELS_CELL = engine("DEFAULTS = dict(think=None")
PROMPTS_CELL = engine("def genre_prompt")
BACKEND_CELL = engine(
    "class OllamaBackend",
    ('''ALL_PROMPTS = ([genre_prompt(q["question"], q["context"]) for q in QUESTIONS.values()]
               + [judge_prompt(c, QUESTIONS[r["question_id"]]["context"], QUESTIONS[r["question_id"]]["question"],
                               r["answer"]) for c in JUDGE_CONDITIONS for r in ITEMS])
''', ""),
    ('''backend = BACKENDS[CFG["backend"]](CFG, PAR)
backend.preflight(ALL_PROMPTS)''', '''backend = None        # started for each model by use_model() below'''),
    # local tests only: let the fake model's replies differ between models, so the routes differ too
    ('h = int(hashlib.md5(prompt.encode("utf-8")).hexdigest(), 16)',
     'h = int(hashlib.md5((MODEL_KEY + prompt).encode("utf-8")).hexdigest(), 16)'),
)
RUN_CELL = engine("def run_stage", ("    return True\n\n\nimport_previous_runs()", "    return True"))

CELLS = []


def md(text):
    CELLS.append(("markdown", text.strip("\n")))


def code(text):
    CELLS.append(("code", text.strip("\n")))


def build(kind):
    CELLS.clear()
    routed = kind == "routed"
    if routed:
        title = "GenreHalluEval, routed judges (best-path route R, plus D, E, F)"
        what = """Every answer goes to the judge that a route picks, with the tables locked on BenHalluEval
(`lock_v2.json`), separately for answers judged with the passage and without it:

- **R, best path (the main route):** two kinds of path compete, and the one with the better BenHalluEval score wins:
  - *our-genre path:* the best genre guesser (qwen3.5-27b) names the genre; the best judge for that genre judges;
  - *own-genre path:* an LLM names the genre; if that LLM is very good inside the genre it named, it judges.
- **D, E, F (extra, for the paper's tables):** D = our genre label picks the judge; E = only the our-genre path;
  F = only the own-genre paths.

**Turn 1:** only the LLMs whose genre answer can change a route name the genre (question + passage only, never the
answer): gemma4-31b and qwen3.5-27b for answers judged with the passage; for answers judged without it, also
deepseek-r1-14b, gemma2-27b, gpt-oss-20b and qwen2.5-32b.
**Turn 2:** only the judges a route picks judge the answers; one verdict per (judge, answer) serves every route."""
    else:
        title = "GenreHalluEval, single best judge (A)"
        what = """The single best judge on BenHalluEval (**A = gemma4-31b**, in both conditions) judges every
answer. No genre is needed."""
    md(f"""
# {title}

{what}

**Conditions:** each answer is judged once, in its own condition (`condition` column of `items.csv`, Set B):
`context` = passage + question + answer (`judge_v1`); `no_context` = question + answer (`judge_noctx_v1`).
The prompts, settings, Ollama version and parsing are exactly those of every BenHalluEval run; the notebook stops if
they differ. This notebook only collects verdicts; `src/dataset2/compare_routes.py` scores and compares the two
notebooks afterwards.

## How to run it on Kaggle

1. **Settings:** GPU T4 x2, Internet on.
2. **Add Input:** your private Kaggle dataset **GenreHalluEval** (made from `GenreHalluEval.zip`).
3. Run all. Keep `RUN_MODE = "full"` (a `"pilot"` of 20 questions is only for a quick check).
4. When it ends, download `genrehallueval__{kind}__full__outputs.zip` (Output tab) and give it to Claude.
5. **If the run stops** (time limit, error): "Save Version", then in a new version **Add Input → this notebook's
   output**, and run all again. Finished calls are skipped. Add only this notebook's own earlier output.
""")
    code(f'''
# ======================= EDIT ONLY THIS CELL =======================
RUN_MODE = "full"           # "full" = all 250 questions; "pilot" = 20 questions (4 per genre), a quick check only
TIME_BUDGET_HOURS = 11.0    # stop cleanly before Kaggle's 12-hour limit; then resume (step 5 above)
OLLAMA_VERSION = "0.40.6"   # the Ollama of every BenHalluEval run. Do not change
# ===================================================================
NOTEBOOK = "{kind}"
METHODS = {'["R", "D", "E", "F"]' if routed else '["A"]'}
MODEL_KEY = "gemma4-31b"    # the starting model; the notebook switches models by itself
PARALLEL = None             # requests at once: each model's default
STAGES = {'["genre", "judge"]' if routed else '["judge"]'}
JUDGE_CONDITIONS = ["context", "no_context"]   # each answer is judged once, in its own condition
''')
    code(IMPORTS)
    md("## The judge models (the same table as the BenHalluEval notebook)")
    code(MODELS_CELL)
    md("""
## Load GenreHalluEval and the lock

The files must match `checksums.sha256`, and the lock must be exactly `lock_v2.json` (sha256 `6d3c1d29…`).
""")
    code(r'''
LOCK_SHA256 = "%s"
PILOT_PER_GENRE = 4


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


sums = {}
for line in (DATA_DIR / "checksums.sha256").read_text(encoding="utf-8").splitlines():
    if line.strip():
        digest, name = line.split("  ", 1)
        sums[name.strip()] = digest
for name in ["items.csv", "lock_v2.json", "prompts/genre_v1.txt", "prompts/judge_v1.txt", "prompts/judge_noctx_v1.txt"]:
    if hashlib.sha256((DATA_DIR / name).read_bytes()).hexdigest() != sums.get(name):
        raise Stop(f"{name} does not match checksums.sha256. Re-upload the dataset folder unchanged.")
if hashlib.sha256((DATA_DIR / "lock_v2.json").read_bytes()).hexdigest() != LOCK_SHA256:
    raise Stop("lock_v2.json is not the locked file. Never change the lock.")
LOCK = json.loads((DATA_DIR / "lock_v2.json").read_text(encoding="utf-8"))
POOL = LOCK["pools"]["dataset2_pool"]
missing = [k for k in POOL if k not in MODELS]
if missing:
    raise Stop(f"pool judges missing from the model table: {missing}")

ITEMS = read_csv(DATA_DIR / "items.csv")
if len({r["item_id"] for r in ITEMS}) != len(ITEMS) or any(r["condition"] not in JUDGE_CONDITIONS for r in ITEMS):
    raise Stop("items.csv: item ids must be unique and every condition must be context or no_context")
QUESTIONS = {}
for r in ITEMS:
    QUESTIONS.setdefault(r["question_id"], dict(question=r["question"], context=r["context"],
                                               genre_human=CODE_OF[r["genre"]], conditions=set()))
    QUESTIONS[r["question_id"]]["conditions"].add(r["condition"])
by_genre = collections.defaultdict(list)
for qid in sorted(QUESTIONS):
    by_genre[QUESTIONS[qid]["genre_human"]].append(qid)
rng = random.Random(SEED)
PILOT_QIDS = {q for g in sorted(by_genre) for q in rng.sample(by_genre[g], min(PILOT_PER_GENRE, len(by_genre[g])))}
RUN_QIDS = PILOT_QIDS if RUN_MODE == "pilot" else set(QUESTIONS)
RUN_ITEMS = [r for r in ITEMS if r["question_id"] in RUN_QIDS]
print(f"{len(QUESTIONS)} questions, {len(ITEMS)} answers; this {RUN_MODE} run: {len(RUN_QIDS)} questions, "
      f"{len(RUN_ITEMS)} answers")
print("answers by condition:", dict(collections.Counter(r["condition"] for r in RUN_ITEMS)))
print("judge pool (locked):", ", ".join(POOL))
''' % LOCK_SHA256)
    md("## The prompts (files in the dataset; golden rule 1 check: no answer text in any genre prompt)")
    code(PROMPTS_CELL)
    md("## The model backends (Ollama; a fake model for local tests)")
    code(BACKEND_CELL)
    md("## Logging, parsing and resuming (one log line per call; strict parse; `no_answer` counted separately)")
    code(RUN_CELL)
    md("""
## Routes and model switching

- The prompts must be exactly the ones every BenHalluEval run used (the lock stores their fingerprints).
- `use_model` stops the old Ollama server, starts one with the next model's settings, downloads the model and measures
  the longest prompt it will see, so no prompt is cut. Models are deleted when the disk gets full.
- The routes follow the lock's rules exactly. A genre without a usable cell falls back to A; ties go to the better
  overall judge.
""")
    code(r'''
for key, lock_key in (("genre", "genre"), ("judge:context", "context"), ("judge:no_context", "no_context")):
    if PROMPT_SHA[key] != LOCK["setup"]["prompt_sha12"][lock_key]:
        raise Stop(f"prompt {PROMPT_IDS[key]} differs from the one in the lock: use the exact BenHalluEval prompts")

ALL_D2_PROMPTS = ([genre_prompt(QUESTIONS[q]["question"], QUESTIONS[q]["context"]) for q in sorted(RUN_QIDS)]
                  + [judge_prompt(r["condition"], r["context"], r["question"], r["answer"]) for r in RUN_ITEMS])
COST, VERSIONS, LOADED, DONE = [], {}, None, {}


def free_disk_gb():
    return shutil.disk_usage(Path.home()).free / 1e9


def installed_models():
    try:
        return [m["name"] for m in http_json(OllamaBackend.url + "/api/tags", timeout=10)["models"]]
    except Exception:
        return []


def make_room(keep, need_gb=30):
    """Delete downloaded models (those not in `keep` first) until `need_gb` GB are free."""
    if not isinstance(backend, OllamaBackend):
        return
    keep_names = {MODELS[k]["model"] for k in keep}
    for name in sorted(installed_models(), key=lambda n: n in keep_names):
        if free_disk_gb() >= need_gb:
            break
        sh(f"ollama rm {name}", check=False)
        print(f"deleted {name} to free disk ({free_disk_gb():.0f} GB free)")


def use_model(key, keep=()):
    global MODEL_KEY, CFG, PAR, backend, LOADED
    if LOADED == key:
        return
    make_room(keep)
    if getattr(backend, "proc", None):
        backend.proc.terminate()
        backend.proc.wait(timeout=120)
    MODEL_KEY = key
    CFG = {**DEFAULTS, **MODELS[key]}
    if "claude" in CFG["model"].lower():
        raise Stop("Claude wrote the hallucinated answers: never use it as a judge or guesser.")
    if os.environ.get("BENCH_BACKEND_OVERRIDE"):          # local tests only
        CFG["backend"] = os.environ["BENCH_BACKEND_OVERRIDE"]
    PAR = PARALLEL or CFG["parallel"]
    print(f"\n==================== {key} ({CFG['model']}) ====================")
    backend = BACKENDS[CFG["backend"]](CFG, PAR)
    backend.preflight(ALL_D2_PROMPTS)
    VERSIONS[key] = dict(model_id=backend.model_id, version=backend.version_id, num_ctx=backend.num_ctx, parallel=PAR)
    LOADED = key
    import_previous_runs()


def run(stage, jobs):
    if not jobs:
        return True
    if time.time() - T0 > TIME_BUDGET_HOURS * 3600:
        print(f"[{MODEL_KEY} {stage}] TIME BUDGET reached before this turn. Resume in a new version.")
        DONE[(MODEL_KEY, stage)] = False
        return False
    DONE[(MODEL_KEY, stage)] = run_stage(stage, jobs)
    s = SESSION.get(stage, {})
    COST.append(dict(model=MODEL_KEY, turn=stage, jobs=len(jobs), calls=s.get("calls", 0),
                     seconds=round(s.get("seconds", 0), 1)))
    return DONE[(MODEL_KEY, stage)]


def records(key, stage, jobs):
    """This model's finished records for exactly these prompts (a record for another prompt text is stale)."""
    want = {j[0]: prompt_hash(j[3]) for j in jobs}
    p = RUN_DIR / f"{DATASET}__{key}__{base(stage)}__{PROMPT_IDS[stage]}.jsonl"
    out = {}
    if p.exists():
        for line in open(p, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                if want.get(r["key"]) == r.get("prompt_hash") and r["status"] != "error":
                    out[r["key"]] = r
    return out


def judge_jobs(rows, condition):
    return [(r["item_id"], r["question_id"], r["item_id"], judge_prompt(condition, r["context"], r["question"], r["answer"]))
            for r in rows if r["condition"] == condition]


L, RB = LOCK["conditions"], LOCK["R_best_path"]["per_condition"]
TABLE = {c: {g: v["judge"] for g, v in L[c]["D_E_judge_per_genre"].items() if v.get("BHS") is not None} for c in L}
TSCORE = {c: {g: v["BHS"] for g, v in L[c]["D_E_judge_per_genre"].items() if v.get("BHS") is not None} for c in L}
OWN = {c: {(j, g): v["BHS"] for j, cells in L[c]["F_own_genre_scores"].items() for g, v in cells.items()} for c in L}
OVERALL = {c: {j: v["BHS"] for j, v in L[c]["overall_BHS"].items()} for c in L}
A_OF = {c: L[c]["A_best_single_judge"] for c in L}
GUESSER = {c: L[c]["best_genre_guesser"]["judge"] for c in L}
ASKERS = {c: RB[c]["askers"] for c in L}


def route(method, condition, qid, named):
    """named: {LLM: genre code it named for this question} (askers only)."""
    A = A_OF[condition]
    if method == "A":
        return A
    if method == "D":
        return TABLE[condition].get(QUESTIONS[qid]["genre_human"], A)
    g = named.get(GUESSER[condition])
    if method == "E":
        return TABLE[condition].get(g, A)
    own = [(OWN[condition][(j, named.get(j))], OVERALL[condition][j], j) for j in ASKERS[condition]
           if (j, named.get(j)) in OWN[condition]]
    if method == "F":
        return min(own)[2] if own else A
    if method == "R":
        ours = ((TSCORE[condition][g], OVERALL[condition][TABLE[condition][g]], TABLE[condition][g]) if g in TABLE[condition]
                else (OVERALL[condition][A], OVERALL[condition][A], A))
        return min(own + [ours])[2]
    raise ValueError(method)


# who names the genre of which question: the askers of each condition the question is judged in
ASK_Q = collections.defaultdict(list)
if any(m in METHODS for m in "REF"):
    for q in sorted(RUN_QIDS):
        for c in sorted(QUESTIONS[q]["conditions"]):
            for k in ASKERS[c]:
                if q not in ASK_Q[k]:
                    ASK_Q[k].append(q)
GENRE_JOBS = {k: [(q, q, None, genre_prompt(QUESTIONS[q]["question"], QUESTIONS[q]["context"])) for q in qs]
              for k, qs in ASK_Q.items()}
print("prompts match the lock:", {k: PROMPT_SHA[k] for k in PROMPT_IDS})
print("A:", A_OF, "| best genre guesser:", GUESSER)
print("LLMs asked for the genre:", {k: len(v) for k, v in ASK_Q.items()} or "none (route A needs no genre)")
''')
    if routed:
        md("""
## Turn 1: the asked LLMs name the genre (question + passage only)

The LLMs needed only for answers judged without the passage go first; gemma4-31b and qwen3.5-27b go last, so they are
still loaded for turn 2.
""")
        code(r'''
LAST = list(dict.fromkeys([A_OF["context"], A_OF["no_context"], GUESSER["context"], GUESSER["no_context"]]))
GENRE_ORDER = [k for k in POOL if k in ASK_Q and k not in LAST] + [k for k in LAST if k in ASK_Q]
for k in GENRE_ORDER:
    if time.time() - T0 > TIME_BUDGET_HOURS * 3600:
        print("TIME BUDGET reached in turn 1. Resume in a new version.")
        break
    use_model(k, keep=LAST)
    run("genre", GENRE_JOBS[k])
NAMED = {k: {q: r["parsed"] for q, r in records(k, "genre", GENRE_JOBS[k]).items()} for k in ASK_Q}
GENRE_COMPLETE = all(len(NAMED[k]) == len(GENRE_JOBS[k]) for k in ASK_Q)
for k in ASK_Q:
    qs = ASK_Q[k]
    n_bad = sum(v == "no_answer" for v in NAMED[k].values())
    acc = sum(NAMED[k].get(q) == QUESTIONS[q]["genre_human"] for q in qs) / len(qs)
    print(f"{k:18} genre guesses {len(NAMED[k])}/{len(qs)} | no_answer {n_bad} | agrees with our genre {100 * acc:.1f}%")
if not GENRE_COMPLETE:
    show_md("## PARTIAL: not every asked LLM has named every genre yet, so no answer is routed. Resume in a new version.")
''')
    else:
        code(r'''
NAMED, GENRE_COMPLETE = {}, True     # route A needs no genre
''')
    md(f"""
## Turn 2: {"route every answer, then let each picked judge judge its answers" if routed else "the single best judge judges every answer"}

Each answer is judged once per picked judge, in its own condition. The routes are saved in `routes.csv`.
""")
    code(r'''
ROUTES, NEED = [], collections.defaultdict(list)
if GENRE_COMPLETE:
    for r in RUN_ITEMS:
        named = {k: NAMED[k].get(r["question_id"]) for k in NAMED}
        row = dict(item_id=r["item_id"], question_id=r["question_id"], condition=r["condition"],
                   our_genre=QUESTIONS[r["question_id"]]["genre_human"])
        for m in METHODS:
            row[m] = route(m, r["condition"], r["question_id"], named)
            if r not in NEED[row[m]]:
                NEED[row[m]].append(r)
        row.update({f"named_{k}": named[k] for k in sorted(NAMED) if k in ASKERS[r["condition"]]})
        ROUTES.append(row)
    order = sorted(NEED, key=lambda k: (k != LOADED, -len(NEED[k])))
    for c in JUDGE_CONDITIONS:
        for m in METHODS:
            print(f"route {m}, {c}: " + ", ".join(f"{k} {n}" for k, n in collections.Counter(
                row[m] for row in ROUTES if row["condition"] == c).most_common()))
    for k in order:
        if time.time() - T0 > TIME_BUDGET_HOURS * 3600:
            print("TIME BUDGET reached in turn 2. Resume in a new version.")
            break
        use_model(k, keep=order[order.index(k):])
        for c in JUDGE_CONDITIONS:
            run(f"judge:{c}", judge_jobs(NEED[k], c))

VERDICT = {}
for k, rows in NEED.items():
    for c in JUDGE_CONDITIONS:
        for item_id, rec in records(k, f"judge:{c}", judge_jobs(rows, c)).items():
            VERDICT[(k, item_id)] = rec
PARTIAL = (not GENRE_COMPLETE or any(v is False for v in DONE.values())
           or any((row[m], row["item_id"]) not in VERDICT for row in ROUTES for m in METHODS))
''')
    md("""
## Summary, cost and the outputs zip

The preview below scores against the **design labels** (gold = correct, written hallucination = hallucinated). The
final scores use the annotators' agreed labels and are computed by `src/dataset2/compare_routes.py`.
""")
    code(r'''
def md_table(rows, cols):
    return "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n" + "\n".join(
        "| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows)


def preview_bhs(rows, method):
    s = [0, 0, 0, 0]
    for row in rows:
        v = VERDICT.get((row[method], row["item_id"]), {}).get("parsed", "no_answer")
        if ITEM_LABEL[row["item_id"]] == 0:
            s[0] += 1; s[1] += v != "no"
        else:
            s[2] += 1; s[3] += v != "yes"
    return round(50 * (s[1] / s[0] + s[3] / s[2]), 2) if s[0] and s[2] else None


ITEM_LABEL = {r["item_id"]: int(r["design_label"]) for r in RUN_ITEMS}
if ROUTES:
    prev = []
    for c in JUDGE_CONDITIONS + ["both"]:
        rows = [row for row in ROUTES if c == "both" or row["condition"] == c]
        for m in METHODS:
            na = sum(VERDICT.get((row[m], row["item_id"]), {}).get("parsed", "no_answer") == "no_answer" for row in rows)
            prev.append(dict(condition=c, route=m, answers=len(rows), questions=len({row["question_id"] for row in rows}),
                             no_answer=na, BHS_preview_design_labels=preview_bhs(rows, m)))
    show_md("**Preview (design labels, not the final result)**\n\n" + md_table(
        prev, ["condition", "route", "answers", "questions", "no_answer", "BHS_preview_design_labels"]))
cut = sum(rec["status"] in ("truncated", "too_long") for rec in VERDICT.values())
logs_cut = [p.name for p in OUT_DIR.glob("ollama_server__*.log") if "truncating input" in p.read_text(errors="ignore").lower()]
if cut or logs_cut:
    show_md(f"**WARNING: {cut} prompts were cut; server logs with truncation: {logs_cut}.** They count as no_answer.")
show_md("**Cost (this session)**\n\n" + md_table(COST, ["model", "turn", "jobs", "calls", "seconds"]))

out = RES_DIR / NOTEBOOK / RUN_MODE
out.mkdir(parents=True, exist_ok=True)
if ROUTES:
    cols = list(dict.fromkeys(k for row in ROUTES for k in row))
    with open(out / "routes.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(ROUTES)
manifest = dict(notebook=NOTEBOOK, methods=METHODS, run_mode=RUN_MODE, models=VERSIONS, pool=POOL,
                askers={k: len(v) for k, v in ASK_Q.items()}, prompt_ids=PROMPT_IDS, prompt_sha=PROMPT_SHA,
                lock_sha256=LOCK_SHA256, seed=SEED, temperature=0, dataset_dir=str(DATA_DIR), dataset_checksums=sums,
                questions=len(RUN_QIDS), answers=len(RUN_ITEMS),
                started=datetime.datetime.fromtimestamp(T0, datetime.timezone.utc).isoformat(),
                finished=datetime.datetime.now(datetime.timezone.utc).isoformat(), partial=PARTIAL,
                truncated=cut, cost=COST)
(out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
zpath = OUT_DIR / f"{DATASET}__{NOTEBOOK}__{RUN_MODE}__outputs.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(RUN_DIR.glob(f"{DATASET}__*.jsonl")) + sorted(out.glob("*")) + sorted(OUT_DIR.glob("ollama_server__*.log")):
        z.write(p, p.relative_to(OUT_DIR))
print("download:", zpath)
show_md(("## PARTIAL: resume before using these numbers (step 5 at the top)." if PARTIAL else "## Done.")
        + f"\n\nNotebook `{NOTEBOOK}`, mode `{RUN_MODE}`, judges used: {', '.join(VERSIONS)}.")
''')
    return list(CELLS)


def main():
    root = Path(sys.argv[1])
    for kind in ("routed", "single_best"):
        base.write_notebook(build(kind), root / "notebooks" / f"genrehallueval_{kind}.ipynb")


if __name__ == "__main__":
    main()
