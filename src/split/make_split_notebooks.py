"""Build the three notebooks of the GenreHalluEval split experiment (exploratory), from the same engine as every
earlier run (src/bench/make_notebook.py, via src/dataset2/make_notebooks.py), so prompts, parsing, Ollama setup,
logging, resume and the time budget are unchanged.

notebooks/split_learn.ipynb        learn half: every pool judge judges every answer with and without the passage, and
                                   names the genre of every question. Its outputs make lock_split_v1.json
                                   (src/split/make_split_lock.py).
notebooks/split_routed.ipynb       test half: routes R (main), D, E, F with the tables in lock_split_v1.json.
notebooks/split_single_best.ipynb  test half: the single best judge of the learn half (A) judges every answer.

New compared with the Dataset 2 notebooks: the prompt language is set per model (pool.json; TigerLLM uses the Bangla
prompts and the Bangla-aware parse of its BenHalluEval Bangla-prompt run, with 16 new tokens per reply).

Usage: python3 -I src/split/make_split_notebooks.py <project_root>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dataset2"))
import make_notebooks as d2                                   # noqa: E402  (builds the engine cells on import)

base = d2.base


def patched(text, *patches):
    for old, new in patches:
        assert text.count(old) == 1, old[:80]
        text = text.replace(old, new)
    return text


IMPORTS = patched(
    d2.IMPORTS,
    ('DATASET = "genrehallueval"          # Dataset 2, test-only: this notebook never makes or changes a choice',
     'DATASET = SPLIT_DATASET             # the split experiment (exploratory): "ghesplit_learn" or "ghesplit_test"'),
    ('hits += glob.glob(f"/kaggle/input/{depth}/items.csv")', 'hits += glob.glob(f"/kaggle/input/{depth}/split.csv")'),
    ('hits = sorted({str(Path(h).parent) for h in hits if (Path(h).parent / "lock_v2.json").exists()})',
     'hits = sorted({str(Path(h).parent) for h in hits if (Path(h).parent / "pool.json").exists()})'),
    ('''raise Stop(f"Expected exactly one GenreHalluEval dataset (a folder with items.csv and lock_v2.json) under "
                   f"/kaggle/input, found {hits}. Add it with 'Add Input' (step 2 at the top).")''',
     '''raise Stop(f"Expected exactly one GenreHalluEval-split dataset (a folder with split.csv and pool.json) under "
                   f"/kaggle/input, found {hits}. Add it with 'Add Input' (step 2 at the top).")'''),
)
BACKEND_CELL = patched(
    d2.BACKEND_CELL,
    # local tests only: the fake model also answers the Bangla prompts (TigerLLM)
    ('''        if prompt.rstrip().endswith("Genre:"):''',
     '''        if prompt.rstrip().endswith("ধরন:"):
            raw = ["ইতিহাস", "শিল্পকলা", "বিজ্ঞান", "ভূগোল", "ধর্ম", "অন্যান্য", "ধরন: ইতিহাস।", "আমার মনে হয় শিল্পকলা"][h % 8]
        elif "মডেলের উত্তর: " in prompt:
            raw = ["হ্যাঁ", "না", "উত্তর: হ্যাঁ", "না।", "আমি নিশ্চিত নই"][h % 5]
        elif prompt.rstrip().endswith("Genre:"):'''),
)

CELLS = []


def md(text):
    CELLS.append(("markdown", text.strip("\n")))


def code(text):
    CELLS.append(("code", text.strip("\n")))


DATA_CELL = r'''
PILOT_PER_GENRE = 4


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


sums = {}
for line in (DATA_DIR / "checksums.sha256").read_text(encoding="utf-8").splitlines():
    if line.strip():
        digest, name = line.split("  ", 1)
        sums[name.strip()] = digest
POOLCFG = json.loads((DATA_DIR / "pool.json").read_text(encoding="utf-8"))
POOL, LANG_OF = POOLCFG["pool"], POOLCFG["prompt_language"]
ITEMS_FILE = "learn_items.csv" if NOTEBOOK == "learn" else "test_items.csv"
need = [ITEMS_FILE, "pool.json", "split.csv"] + [f"prompts/{p}.txt" for ps in POOLCFG["prompt_ids"].values() for p in ps]
if NOTEBOOK != "learn":
    need.append("lock_split_v1.json")
    if not (DATA_DIR / "lock_split_v1.json").exists():
        raise Stop("lock_split_v1.json is missing. Upload the dataset version made after the learn run "
                   "(HOW_TO_USE.md, step 3) and add that version as input.")
for name in need:
    if sha256_file(DATA_DIR / name) != sums.get(name):
        raise Stop(f"{name} does not match checksums.sha256. Re-upload the dataset folder unchanged.")
LOCK, LOCK_SHA256 = None, None
if NOTEBOOK != "learn":
    LOCK_SHA256 = sha256_file(DATA_DIR / "lock_split_v1.json")
    LOCK = json.loads((DATA_DIR / "lock_split_v1.json").read_text(encoding="utf-8"))
    if LOCK["source"]["learn_items_sha256"] != sums["learn_items.csv"] or LOCK["pools"]["pool"] != POOL:
        raise Stop("lock_split_v1.json was not made from this package's learn half and pool.")
    POOL = LOCK["pools"]["usable"]          # judges with usable verdicts on the learn half
missing = [k for k in POOL if k not in MODELS]
if missing:
    raise Stop(f"pool judges missing from the model table: {missing}")

ITEMS = read_csv(DATA_DIR / ITEMS_FILE)
if (len({(r["item_id"], r["condition"]) for r in ITEMS}) != len(ITEMS)
        or any(r["condition"] not in JUDGE_CONDITIONS for r in ITEMS)):
    raise Stop(f"{ITEMS_FILE}: (item id, condition) must be unique and every condition context or no_context")
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
print(f"{NOTEBOOK}: {len(QUESTIONS)} questions, {len(ITEMS)} rows; this {RUN_MODE} run: {len(RUN_QIDS)} questions, "
      f"{len(RUN_ITEMS)} rows")
print("rows by condition:", dict(collections.Counter(r["condition"] for r in RUN_ITEMS)))
print("pool:", ", ".join(f"{k} ({LANG_OF[k]} prompts)" for k in POOL), "| lock sha256:", LOCK_SHA256 or "none (learn half)")
'''

LANG_CELL = r'''
STAGE_KEYS = ("genre", "judge:context", "judge:no_context")
PROMPT_IDS_BY = {lang: dict(zip(STAGE_KEYS, pids)) for lang, pids in POOLCFG["prompt_ids"].items()}
TEMPLATES_BY = {lang: {k: (DATA_DIR / "prompts" / f"{pid}.txt").read_text(encoding="utf-8").rstrip() for k, pid in ids.items()}
                for lang, ids in PROMPT_IDS_BY.items()}
SHA_BY = {lang: {k: hashlib.sha256(t.encode("utf-8")).hexdigest()[:12] for k, t in ts.items()} for lang, ts in TEMPLATES_BY.items()}
assert PROMPT_IDS_BY["en"] == PROMPT_IDS and TEMPLATES_BY["en"] == TEMPLATES, "the English prompts must be the engine's"


def g_prompt(lang, question, context):                     # takes no answer, by design (rule 1)
    return fill(TEMPLATES_BY[lang]["genre"], question=question, context=context)


def j_prompt(lang, condition, context, question, answer):
    if condition == "context":
        return fill(TEMPLATES_BY[lang]["judge:context"], context=context, question=question, answer=answer)
    return fill(TEMPLATES_BY[lang]["judge:no_context"], question=question, answer=answer)


for lang, ts in TEMPLATES_BY.items():
    assert "{answer}" not in ts["genre"] and "{context}" in ts["judge:context"] and "{context}" not in ts["judge:no_context"]
    leaks = []
    for r in ITEMS:
        q = QUESTIONS[r["question_id"]]
        a = r["answer"].strip()
        explained = ts["genre"].count(a) + q["question"].count(a) + q["context"].count(a)
        if a and g_prompt(lang, q["question"], q["context"]).count(a) > explained:
            leaks.append(r["item_id"])
    if leaks:
        raise Stop(f"Golden rule 1 broken ({lang} prompts): answer text in {len(leaks)} genre prompts, e.g. {leaks[:3]}")
print("Golden rule 1 check passed for the English and the Bangla prompts.")
print("prompt fingerprints:", SHA_BY)
'''

PARSE_BN_CELL = r'''
# The Bangla-aware strict parse of the Bangla-prompt BenHalluEval runs (src/bench/make_notebook_bangla.py), used only
# for models whose prompt language is "bn" (TigerLLM). Every other model keeps the English strict parse above.
BN_YES, BN_NO = ("হ্যাঁ", "হ্যা"), ("না",)
BN_GENRE = {"ইতিহাস": "HISTORY", "শিল্পকলা": "ARTS", "বিজ্ঞান": "SCIENCE", "ভূগোল": "GEOGRAPHY",
            "ধর্ম": "RELIGION", "অন্যান্য": "OTHER"}
BN_LABEL = re.compile(r"^(উত্তর|ধরন|answer|genre)\s*[:ঃ]\s*", re.I)
EDGE_BN = EDGE + "।"
parse_en = parse


def parse_bn(stage, raw, strict=True):
    import unicodedata
    text = unicodedata.normalize("NFC", strip_think(raw))
    if strict:
        t = BN_LABEL.sub("", text.strip(EDGE_BN)).strip(EDGE_BN)
        if stage == "judge":
            return "yes" if t in BN_YES or t.lower() == "yes" else "no" if t in BN_NO or t.lower() == "no" else "no_answer"
        return BN_GENRE.get(t) or (t.upper() if t.upper() in GENRES else "no_answer")
    for w in re.findall(r"[ঀ-৿]+|[A-Za-z]+", text):
        if stage == "judge":
            if w in BN_YES or w.lower() == "yes":
                return "yes"
            if w in BN_NO or w.lower() == "no":
                return "no"
        elif w in BN_GENRE or w.upper() in GENRES:
            return BN_GENRE.get(w) or w.upper()
    return "no_answer"


def set_language(lang):
    """Prompts, fingerprints, run-file names and parser of the model being loaded."""
    global PROMPT_IDS, TEMPLATES, PROMPT_SHA, parse
    PROMPT_IDS, TEMPLATES, PROMPT_SHA = PROMPT_IDS_BY[lang], TEMPLATES_BY[lang], SHA_BY[lang]
    parse = parse_bn if lang == "bn" else parse_en


assert parse_bn("judge", "উত্তর: হ্যাঁ।") == "yes" and parse_bn("judge", "না") == "no" and parse_bn("genre", "ধর্ম") == "RELIGION"
assert parse_en("judge", "হ্যাঁ") == "no_answer"
'''

SWITCH_CELL = r'''
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


def prompts_for(key):
    lang = LANG_OF[key]
    return ([g_prompt(lang, QUESTIONS[q]["question"], QUESTIONS[q]["context"]) for q in sorted(RUN_QIDS)]
            + [j_prompt(lang, r["condition"], r["context"], r["question"], r["answer"]) for r in RUN_ITEMS])


def use_model(key, keep=()):
    global MODEL_KEY, CFG, PAR, backend, LOADED
    if LOADED == key:
        return
    make_room(keep)
    if getattr(backend, "proc", None):
        backend.proc.terminate()
        backend.proc.wait(timeout=120)
    MODEL_KEY = key
    set_language(LANG_OF[key])
    CFG = {**DEFAULTS, **MODELS[key]}
    if LANG_OF[key] == "bn":
        CFG["max_new"] = {"genre": 16, "judge": 16}       # as in the Bangla-prompt BenHalluEval runs
    if "claude" in CFG["model"].lower():
        raise Stop("Claude wrote the hallucinated answers: never use it as a judge or guesser.")
    if os.environ.get("BENCH_BACKEND_OVERRIDE"):          # local tests only
        CFG["backend"] = os.environ["BENCH_BACKEND_OVERRIDE"]
    PAR = PARALLEL or CFG["parallel"]
    print(f"\n==================== {key} ({CFG['model']}; {LANG_OF[key]} prompts) ====================")
    backend = BACKENDS[CFG["backend"]](CFG, PAR)
    backend.preflight(prompts_for(key))
    VERSIONS[key] = dict(model_id=backend.model_id, version=backend.version_id, num_ctx=backend.num_ctx, parallel=PAR,
                         prompt_language=LANG_OF[key], prompt_ids=PROMPT_IDS, max_new=CFG["max_new"],
                         think=CFG.get("think"))
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
    p = RUN_DIR / f"{DATASET}__{key}__{base(stage)}__{PROMPT_IDS_BY[LANG_OF[key]][stage]}.jsonl"
    out = {}
    if p.exists():
        for line in open(p, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                if want.get(r["key"]) == r.get("prompt_hash") and r["status"] != "error":
                    out[r["key"]] = r
    return out


def genre_jobs(key, qids):
    return [(q, q, None, g_prompt(LANG_OF[key], QUESTIONS[q]["question"], QUESTIONS[q]["context"])) for q in qids]


def judge_jobs(key, rows, condition):
    return [(r["item_id"], r["question_id"], r["item_id"],
             j_prompt(LANG_OF[key], condition, r["context"], r["question"], r["answer"]))
            for r in rows if r["condition"] == condition]


def md_table(rows, cols):
    return "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n" + "\n".join(
        "| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows)


ITEM_LABEL = {r["item_id"]: int(r["design_label"]) for r in RUN_ITEMS}


def preview_bhs(pairs):
    """pairs: (item_id, verdict). BHS against the design labels (a preview; the final scores use the agreed labels)."""
    s = [0, 0, 0, 0]
    for item_id, v in pairs:
        if ITEM_LABEL[item_id] == 0:
            s[0] += 1; s[1] += v != "no"
        else:
            s[2] += 1; s[3] += v != "yes"
    return round(50 * (s[1] / s[0] + s[3] / s[2]), 2) if s[0] and s[2] else None
'''

LEARN_CELL = r'''
ORDER = [k for k in ("gemma4-31b", "qwen3.5-27b", "gpt-oss-20b", "tigerllm-9b", "deepseek-r1-14b") if k in POOL]
ORDER += [k for k in POOL if k not in ORDER]
if MODELS_THIS_RUN:
    bad = [k for k in MODELS_THIS_RUN if k not in POOL]
    if bad:
        raise Stop(f"MODELS_THIS_RUN has models outside the pool: {bad}")
    ORDER = [k for k in ORDER if k in MODELS_THIS_RUN]
print("models in this session, in order:", ORDER)
QS = sorted(RUN_QIDS)
for i, k in enumerate(ORDER):
    if time.time() - T0 > TIME_BUDGET_HOURS * 3600:
        print("TIME BUDGET reached. Resume in a new version.")
        DONE[(k, "start")] = False
        break
    use_model(k, keep=ORDER[i:])
    run("genre", genre_jobs(k, QS))
    for c in JUDGE_CONDITIONS:
        run(f"judge:{c}", judge_jobs(k, RUN_ITEMS, c))

GEN = {k: records(k, "genre", genre_jobs(k, QS)) for k in ORDER}
JUD = {(k, c): records(k, f"judge:{c}", judge_jobs(k, RUN_ITEMS, c)) for k in ORDER for c in JUDGE_CONDITIONS}
N_COND = {c: sum(r["condition"] == c for r in RUN_ITEMS) for c in JUDGE_CONDITIONS}
PARTIAL = (any(v is False for v in DONE.values()) or any(len(GEN[k]) < len(QS) for k in ORDER)
           or any(len(JUD[(k, c)]) < N_COND[c] for k in ORDER for c in JUDGE_CONDITIONS))
prev = []
for k in ORDER:
    row = dict(model=k, prompts=LANG_OF[k], genre=f"{len(GEN[k])}/{len(QS)}",
               genre_agrees=f"{100 * sum(r['parsed'] == QUESTIONS[q]['genre_human'] for q, r in GEN[k].items()) / max(1, len(GEN[k])):.1f}%",
               genre_no_answer=sum(r["parsed"] == "no_answer" for r in GEN[k].values()))
    for c in JUDGE_CONDITIONS:
        recs = JUD[(k, c)]
        row[f"{c}_done"] = f"{len(recs)}/{N_COND[c]}"
        row[f"{c}_no_answer"] = sum(r["parsed"] == "no_answer" for r in recs.values())
        row[f"{c}_BHS_preview"] = preview_bhs((i, r["parsed"]) for i, r in recs.items()) if len(recs) == N_COND[c] else ""
    prev.append(row)
show_md("**Preview (design labels; the lock uses the agreed labels)**\n\n" + md_table(prev, list(prev[0]) if prev else ["model"]))
ALL_RECS = list(GEN.values()) + list(JUD.values())
'''

TEST_LOCK_CELL = r'''
for lang in SHA_BY:
    if SHA_BY[lang] != LOCK["setup"]["prompt_sha12"][lang]:
        raise Stop(f"the {lang} prompts differ from the ones in lock_split_v1.json")
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


ASK_Q = collections.defaultdict(list)
if any(m in METHODS for m in "REF"):
    for q in sorted(RUN_QIDS):
        for c in sorted(QUESTIONS[q]["conditions"]):
            for k in ASKERS[c]:
                if q not in ASK_Q[k]:
                    ASK_Q[k].append(q)
GENRE_JOBS = {k: genre_jobs(k, qs) for k, qs in ASK_Q.items()}
print("A:", A_OF, "| best genre guesser:", GUESSER)
print("LLMs asked for the genre:", {k: len(v) for k, v in ASK_Q.items()} or "none (route A needs no genre)")
'''

TURN1_CELL = r'''
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
'''

TURN2_CELL = r'''
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
            run(f"judge:{c}", judge_jobs(k, NEED[k], c))

VERDICT = {}
for k, rows in NEED.items():
    for c in JUDGE_CONDITIONS:
        for item_id, rec in records(k, f"judge:{c}", judge_jobs(k, rows, c)).items():
            VERDICT[(k, item_id)] = rec
PARTIAL = (not GENRE_COMPLETE or any(v is False for v in DONE.values())
           or any((row[m], row["item_id"]) not in VERDICT for row in ROUTES for m in METHODS))
if ROUTES:
    prev = []
    for c in JUDGE_CONDITIONS + ["both"]:
        rows = [row for row in ROUTES if c == "both" or row["condition"] == c]
        for m in METHODS:
            vs = [(row["item_id"], VERDICT.get((row[m], row["item_id"]), {}).get("parsed", "no_answer")) for row in rows]
            prev.append(dict(condition=c, route=m, answers=len(rows), questions=len({row["question_id"] for row in rows}),
                             no_answer=sum(v == "no_answer" for _, v in vs), BHS_preview_design_labels=preview_bhs(vs)))
    show_md("**Preview (design labels, not the final result)**\n\n" + md_table(
        prev, ["condition", "route", "answers", "questions", "no_answer", "BHS_preview_design_labels"]))
ALL_RECS = [VERDICT]
'''

SAVE_CELL = r'''
cut = sum(rec["status"] in ("truncated", "too_long") for recs in ALL_RECS for rec in recs.values())
logs_cut = [p.name for p in OUT_DIR.glob("ollama_server__*.log") if "truncating input" in p.read_text(errors="ignore").lower()]
if cut or logs_cut:
    show_md(f"**WARNING: {cut} prompts were cut; server logs with truncation: {logs_cut}.** They count as no_answer.")
show_md("**Cost (this session)**\n\n" + md_table(COST, ["model", "turn", "jobs", "calls", "seconds"]))

out = RES_DIR / NOTEBOOK / RUN_MODE
out.mkdir(parents=True, exist_ok=True)
if NOTEBOOK != "learn" and ROUTES:
    cols = list(dict.fromkeys(k for row in ROUTES for k in row))
    with open(out / "routes.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(ROUTES)
TAG = "all" if NOTEBOOK != "learn" or not MODELS_THIS_RUN else "+".join(ORDER)
manifest = dict(notebook=NOTEBOOK, dataset=DATASET, methods=METHODS, run_mode=RUN_MODE, models=VERSIONS, pool=POOL,
                models_this_run=ORDER if NOTEBOOK == "learn" else sorted(VERSIONS),
                askers={k: len(v) for k, v in ASK_Q.items()} if NOTEBOOK != "learn" else None,
                prompt_ids=PROMPT_IDS_BY, prompt_sha=SHA_BY, lock_sha256=LOCK_SHA256, seed=SEED, temperature=0,
                dataset_dir=str(DATA_DIR), dataset_checksums=sums, questions=len(RUN_QIDS), rows=len(RUN_ITEMS),
                started=datetime.datetime.fromtimestamp(T0, datetime.timezone.utc).isoformat(),
                finished=datetime.datetime.now(datetime.timezone.utc).isoformat(), partial=PARTIAL,
                truncated=cut, cost=COST)
(out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
zpath = OUT_DIR / f"{DATASET}__{NOTEBOOK}__{RUN_MODE}__{TAG}__outputs.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(RUN_DIR.glob(f"{DATASET}__*.jsonl")) + sorted(out.glob("*")) + sorted(OUT_DIR.glob("ollama_server__*.log")):
        z.write(p, p.relative_to(OUT_DIR))
print("download:", zpath)
show_md(("## PARTIAL: resume before using these numbers (see the top of the notebook)." if PARTIAL else "## Done.")
        + f"\n\nNotebook `{NOTEBOOK}`, mode `{RUN_MODE}`, models: {', '.join(VERSIONS)}.")
'''

INTRO = {
    "learn": ("GenreHalluEval split, step 1: the learn half (every judge, both conditions)", """
Every pool judge judges **every answer of the learn half twice**, with the passage (`context`) and without it
(`no_context`), and names the genre of every learn question (question + passage only, never the answer). From these
outputs Claude makes `lock_split_v1.json` (the routes for the test half) with the same rules as on BenHalluEval, but
with cells of 20+ questions.

Pool (`pool.json`): gemma4-31b, qwen3.5-27b, gpt-oss-20b, deepseek-r1-14b with the English prompts; tigerllm-9b with
the Bangla prompts. About 5 GPU hours in one session (deepseek-r1-14b alone about 2 h). To finish sooner, run two
copies of this notebook at the same time: one with `MODELS_THIS_RUN = ["deepseek-r1-14b"]`, one with the other four."""),
    "routed": ("GenreHalluEval split, step 2a: the test half, routed judges (R, D, E, F)", """
Every test answer goes to the judge a route picks, with the tables in `lock_split_v1.json` (learned on the learn
half), separately with and without the passage. R (best path) is the main route; D, E, F are extra. Only the LLMs whose
genre answer can change a route are asked for the genre; only the judges a route picks judge."""),
    "single_best": ("GenreHalluEval split, step 2b: the test half, single best judge (A)", """
The single best judge of the learn half (A in `lock_split_v1.json`, per condition) judges every test answer."""),
}


def build(kind):
    CELLS.clear()
    title, what = INTRO[kind]
    learn = kind == "learn"
    md(f"""
# {title}

{what}

Exploratory experiment (added after the confirmatory Dataset 2 result; see `docs/split-experiment-plan.md`). Prompts,
settings, Ollama version and parsing are those of the earlier runs; TigerLLM uses its Bangla prompts and parser.

## How to run it on Kaggle

1. **Settings:** GPU T4 x2, Internet on.
2. **Add Input:** your private Kaggle dataset **GenreHalluEval-split** ({"version 1 or later" if learn else "the version WITH `lock_split_v1.json`"}).
3. Run all. Keep `RUN_MODE = "full"` (a `"pilot"` of 20 questions is only for a quick check).
4. When it ends, download the `ghesplit_…_outputs.zip` from the Output tab and give it to Claude.
5. **If the run stops** (time limit, error): "Save Version", then in a new version **Add Input → this notebook's own
   output**, and run all again. Finished calls are skipped.
""")
    code(f'''
# ======================= EDIT ONLY THIS CELL =======================
RUN_MODE = "full"           # "full" = the whole half (125 questions); "pilot" = 20 questions (4 per genre), a check only
TIME_BUDGET_HOURS = 11.0    # stop cleanly before Kaggle's 12-hour limit; then resume (step 5 above)
OLLAMA_VERSION = "0.40.6"   # the Ollama of every earlier run. Do not change
{'MODELS_THIS_RUN = None      # None = every pool model; or a list, e.g. ["deepseek-r1-14b"], to split the work' if learn else ''}
# ===================================================================
NOTEBOOK = "{kind}"
SPLIT_DATASET = "{'ghesplit_learn' if learn else 'ghesplit_test'}"
METHODS = {'[]' if learn else '["R", "D", "E", "F"]' if kind == "routed" else '["A"]'}
MODEL_KEY = "gemma4-31b"    # the starting model; the notebook switches models by itself
PARALLEL = None             # requests at once: each model's default
STAGES = {'["genre", "judge"]' if kind != "single_best" else '["judge"]'}
JUDGE_CONDITIONS = ["context", "no_context"]
''')
    code(IMPORTS)
    md("## The judge models (the same table as every earlier run)")
    code(d2.MODELS_CELL)
    md(f"## Load the {'learn' if learn else 'test'} half{'' if learn else ' and the lock'} (files must match `checksums.sha256`)")
    code(DATA_CELL)
    md("## The prompts (English for most models, Bangla for TigerLLM; golden rule 1 check)")
    code(d2.PROMPTS_CELL)
    code(LANG_CELL)
    md("## The model backends (Ollama; a fake model for local tests)")
    code(BACKEND_CELL)
    md("## Logging, parsing and resuming (one log line per call; strict parse; `no_answer` counted separately)")
    code(d2.RUN_CELL)
    code(PARSE_BN_CELL)
    md("## Model switching")
    code(SWITCH_CELL)
    if learn:
        md("## Every model: genre of every question, then every answer with and without the passage")
        code(LEARN_CELL)
    else:
        md("## The routes in `lock_split_v1.json`")
        code(TEST_LOCK_CELL)
        if kind == "routed":
            md("## Turn 1: the asked LLMs name the genre (question + passage only)")
            code(TURN1_CELL)
        else:
            code("NAMED, GENRE_COMPLETE = {}, True     # route A needs no genre")
        md("## Turn 2: route every answer, then each picked judge judges its answers")
        code(TURN2_CELL)
    md("## Cost, manifest and the outputs zip")
    code(SAVE_CELL)
    return list(CELLS)


def main():
    root = Path(sys.argv[1])
    for kind in ("learn", "routed", "single_best"):
        base.write_notebook(build(kind), root / "notebooks" / f"split_{kind}.ipynb")


if __name__ == "__main__":
    main()
