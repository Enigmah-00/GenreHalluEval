"""Build the three GenreHalluEval v2 notebooks: the same design and engine as the GenreHalluEval split experiment
(src/split/make_split_notebooks.py, itself built from src/bench/make_notebook.py), with 12 genres + Other.

notebooks/ghe2_learn.ipynb        learn half: every pool judge judges every answer with and without the passage, and
                                  names the genre of every question (genre_v2 / genre_bn_v2). Its outputs make
                                  lock_ghe2_v1.json (src/genrehallueval_v2/make_lock_v2.py).
notebooks/ghe2_route_E.ipynb      test half, route E: the best guesser names the genre; the best judge for it judges.
notebooks/ghe2_route_F.ipynb      test half, route F: every LLM with an own-genre cell names the genre; the LLM with the
                                  best learn-half score inside the genre it named judges.
notebooks/ghe2_route_R.ipynb      test half, route R: the better of the our-genre path and the own-genre paths.
notebooks/ghe2_single_best.ipynb  test half: the single best judge of the learn half (A) judges every answer.
One route per notebook (Mahdi, 2026-10-30), so each route's cost is measured on its own. Main tests: E, F, R vs A per
condition (Holm over 6). The learn notebook is only rewritten with --learn.

Changes from the split notebooks (nothing else): the 12-genre table and the genre_v2 prompts (English and Bangla,
with the Bangla genre names in TigerLLM's parser); the dataset names ghe2_learn / ghe2_test; the lock file name; the
package check (pool.json must be GenreHalluEval v2); a pilot of 2 questions per genre.
Copies for Kaggle go to release/kaggle-genrehallueval-v2/.

Usage: python3 -I src/genrehallueval_v2/make_v2_notebooks.py <project_root> [--learn]
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "split"))
import make_split_notebooks as sp                             # noqa: E402  (builds the engine cells on import)

d2, base, patched = sp.d2, sp.base, sp.patched
LOCK = "lock_ghe2_v1.json"


def replace_all(text, old, new, n):
    assert text.count(old) == n, (old, text.count(old))
    return text.replace(old, new)


GENRES_OLD = '''GENRES = {"HISTORY": "History, Politics & Education", "ARTS": "Arts, Culture & Sports",
          "SCIENCE": "Science & Technology", "GEOGRAPHY": "Geography & Places",
          "RELIGION": "Religion", "OTHER": "Other"}'''
GENRES_NEW = '''GENRES = {"HISTORY": "History", "POLITICS": "Politics", "EDUCATION": "Education", "ARTS": "Arts",
          "CULTURE": "Culture", "SPORTS": "Sports", "SCIENCE": "Science", "TECHNOLOGY": "Technology",
          "GEOGRAPHY": "Geography", "PLACES": "Places", "RELIGION": "Religion", "GRAMMAR": "Grammar",
          "OTHER": "Other"}                # GenreHalluEval v2: 12 genres + Other (genre guide v2.0)'''
IMPORTS = patched(
    sp.IMPORTS,
    (GENRES_OLD, GENRES_NEW),
    ('DATASET = SPLIT_DATASET             # the split experiment (exploratory): "ghesplit_learn" or "ghesplit_test"',
     'DATASET = SPLIT_DATASET             # GenreHalluEval v2: "ghe2_learn" or "ghe2_test"'),
    ('''raise Stop(f"Expected exactly one GenreHalluEval-split dataset (a folder with split.csv and pool.json) under "''',
     '''raise Stop(f"Expected exactly one GenreHalluEval-v2 dataset (a folder with split.csv and pool.json) under "'''),
)
PROMPTS_CELL = patched(d2.PROMPTS_CELL, ('"genre": "genre_v1"', '"genre": "genre_v2"'))
BACKEND_CELL = patched(
    sp.BACKEND_CELL,
    # local tests only: the fake model names all 12 genres (English and Bangla)
    ('raw = ["ইতিহাস", "শিল্পকলা", "বিজ্ঞান", "ভূগোল", "ধর্ম", "অন্যান্য", "ধরন: ইতিহাস।", "আমার মনে হয় শিল্পকলা"][h % 8]',
     'raw = ["ইতিহাস", "রাজনীতি", "শিক্ষা", "শিল্পকলা", "সংস্কৃতি", "খেলাধুলা", "বিজ্ঞান", "প্রযুক্তি", "ভূগোল", "স্থান",\n'
     '                   "ধর্ম", "ব্যাকরণ", "অন্যান্য", "ধরন: ইতিহাস।", "আমার মনে হয় শিল্পকলা"][h % 15]'),
    ('raw = ["HISTORY", "ARTS", "SCIENCE", "GEOGRAPHY", "RELIGION", "OTHER", "History.", "I think ARTS"][h % 8]',
     'raw = ["HISTORY", "POLITICS", "EDUCATION", "ARTS", "CULTURE", "SPORTS", "SCIENCE", "TECHNOLOGY", "GEOGRAPHY",\n'
     '                   "PLACES", "RELIGION", "GRAMMAR", "OTHER", "History.", "I think ARTS"][h % 15]'),
)
DATA_CELL = patched(
    replace_all(sp.DATA_CELL, "lock_split_v1.json", LOCK, 6),
    ("PILOT_PER_GENRE = 4", "PILOT_PER_GENRE = 2"),
    ('POOL, LANG_OF = POOLCFG["pool"], POOLCFG["prompt_language"]',
     '''if not POOLCFG.get("dataset", "").startswith("GenreHalluEval v2"):
    raise Stop("This notebook is for GenreHalluEval v2. Add the GenreHalluEval-v2 dataset as input.")
POOL, LANG_OF = POOLCFG["pool"], POOLCFG["prompt_language"]'''),
)
PARSE_BN_CELL = patched(
    sp.PARSE_BN_CELL,
    ('''BN_GENRE = {"ইতিহাস": "HISTORY", "শিল্পকলা": "ARTS", "বিজ্ঞান": "SCIENCE", "ভূগোল": "GEOGRAPHY",
            "ধর্ম": "RELIGION", "অন্যান্য": "OTHER"}''',
     '''import unicodedata
BN_GENRE = {unicodedata.normalize("NFC", w): code for code, w in POOLCFG["genres_bn"].items()}   # 12 genres + Other
assert sorted(BN_GENRE.values()) == sorted(GENRES), "the Bangla genre names must cover every genre"'''),
    ('assert parse_bn("judge", "উত্তর: হ্যাঁ।") == "yes" and parse_bn("judge", "না") == "no" and parse_bn("genre", "ধর্ম") == "RELIGION"',
     'assert parse_bn("judge", "উত্তর: হ্যাঁ।") == "yes" and parse_bn("judge", "না") == "no" and parse_bn("genre", "ধর্ম") == "RELIGION"\n'
     'assert parse_bn("genre", "ব্যাকরণ") == "GRAMMAR" and parse_bn("genre", "ধরন: খেলাধুলা।") == "SPORTS"\n'
     'assert parse_bn("genre", "স্থান", strict=False) == "PLACES" and parse_en("genre", "TECHNOLOGY") == "TECHNOLOGY"'),
)
TEST_DATA_CELL = patched(                  # the test notebooks also check the test plan (added 2026-10-30)
    DATA_CELL,
    ('    need.append("lock_ghe2_v1.json")',
     '''    need += ["lock_ghe2_v1.json", "test_plan_v2.json"]
    if not (DATA_DIR / "test_plan_v2.json").exists():
        raise Stop("test_plan_v2.json is missing. Upload the newest dataset version and add it as input.")'''),
)
TEST_LOCK_CELL = patched(
    replace_all(sp.TEST_LOCK_CELL, "lock_split_v1.json", LOCK, 1),
    # F (own genre) asks every LLM that has an own-genre cell; R asks the lock's askers; E asks only the guesser
    ('ASKERS = {c: RB[c]["askers"] for c in L}',
     '''ASKERS = {c: RB[c]["askers"] for c in L}                                 # route R (best path)
ASKERS_F = {c: sorted(j for j, cells in L[c]["F_own_genre_scores"].items() if cells) for c in L}   # route F
NEED_ASK = {c: sorted(set().union(*[{"E": {GUESSER[c]}, "F": set(ASKERS_F[c]), "R": set(ASKERS[c])}.get(m, set())
                                    for m in METHODS])) for c in L}'''),
    ('''    own = [(OWN[condition][(j, named.get(j))], OVERALL[condition][j], j) for j in ASKERS[condition]
           if (j, named.get(j)) in OWN[condition]]''',
     '''    own = [(OWN[condition][(j, named.get(j))], OVERALL[condition][j], j)
           for j in (ASKERS_F if method == "F" else ASKERS)[condition] if (j, named.get(j)) in OWN[condition]]'''),
    ('''            for k in ASKERS[c]:
                if q not in ASK_Q[k]:''',
     '''            for k in NEED_ASK[c]:
                if q not in ASK_Q[k]:'''),
)
TURN2_CELL = patched(
    sp.TURN2_CELL,
    ('row.update({f"named_{k}": named[k] for k in sorted(NAMED) if k in ASKERS[r["condition"]]})',
     'row.update({f"named_{k}": named[k] for k in sorted(NAMED) if k in NEED_ASK[r["condition"]]})'),
)

CELLS = []


def md(text):
    CELLS.append(("markdown", text.strip("\n")))


def code(text):
    CELLS.append(("code", text.strip("\n")))


INTRO = {
    "learn": ("GenreHalluEval v2, step 1: the learn half (every judge, both conditions)", """
Every pool judge judges **every answer of the learn half twice**, with the passage (`context`) and without it
(`no_context`), and names the genre of every learn question (question + passage only, never the answer), with the
12-genre prompt `genre_v2` (TigerLLM: `genre_bn_v2`). The learn half has 600 questions (50 per genre), 3,000 answers
and 6,000 judge rows per judge. From these outputs Claude makes `lock_ghe2_v1.json` (the routes for the test half):
the best single judge (A), the best judge per genre (D/E), each LLM's score inside the genre it named itself (F), and
the best path (R). Cells need 50+ questions.

Pool (`pool.json`): gemma4-31b, qwen3.5-27b, gpt-oss-20b, deepseek-r1-14b with the English prompts; tigerllm-9b with
the Bangla prompts. **About 20 GPU hours in total**, too long for one session. Run it as three sessions (two can run at
the same time), each with its own `MODELS_THIS_RUN`:
- session 1: `["deepseek-r1-14b"]` (about 9 h);
- session 2: `["gemma4-31b", "tigerllm-9b"]` (about 5–6 h);
- session 3: `["qwen3.5-27b", "gpt-oss-20b"]` (about 6 h)."""),
    "route_E": ("GenreHalluEval v2, step 2a: the test half, route E (best guesser's genre)", """
**Route E:** the best genre guesser of the learn half (`lock_ghe2_v1.json`) names the genre of every test question
(question + passage only, never the answer). The answer then goes to the best judge for that genre on the learn half
(the judge x genre table). Only the guesser is asked for the genre; only the table judges judge.
Separately with the passage and without it. The test half has 600 questions: 300 with the passage and 300 without
(25 + 25 per genre). About 2–3 GPU hours."""),
    "route_F": ("GenreHalluEval v2, step 2b: the test half, route F (each LLM's own genre)", """
**Route F (own genre):** every LLM that has an own-genre cell on the learn half names the genre of every test question
(question + passage only). Each LLM's learn-half score inside the genre *it* named is looked up (cells of 50+
questions); the answer goes to the LLM with the best such score. If no LLM has a cell for the genre it named, the
answer goes to A. Separately with the passage and without it. About 4–5 GPU hours (all 5 LLMs name the genre)."""),
    "route_R": ("GenreHalluEval v2, step 2c: the test half, route R (best path: our genre or own genre)", """
**Route R (mixed, best path):** for every test question, two kinds of path compete and the one with the better
learn-half score wins:
- *our-genre path* (as in route E): the best guesser names the genre; the best judge for that genre judges;
- *own-genre paths* (as in route F): an LLM names the genre; if it scored better inside that genre than the
  our-genre path, it judges.
Only the LLMs whose own-genre score can win are asked for the genre (the lock's askers); only the judges a route picks
judge. Separately with the passage and without it. About 3–4 GPU hours."""),
    "single_best": ("GenreHalluEval v2, step 2d: the test half, single best judge (A)", """
The single best judge of the learn half (A in `lock_ghe2_v1.json`, per condition) judges every test answer: 1,500
answers with the passage and 1,500 without. About 1–2 GPU hours."""),
}


DESIGN_NOTE = {
    True: """Design fixed before any run (`pool.json`; plan `docs/genrehallueval-v2-plan.md`). Prompts, settings, Ollama version
and parsing are those of every earlier run; TigerLLM uses its Bangla prompts and parser. Main tests on the test half:
R vs A and F vs A, with and without the passage (Holm over 4).""",
    False: """Design fixed before any test-half run (`pool.json`, `test_plan_v2.json`; plan `docs/genrehallueval-v2-plan.md`).
Prompts, settings, Ollama version and parsing are those of every earlier run; TigerLLM uses its Bangla prompts and
parser. Main tests on the test half: E vs A, F vs A and R vs A, with and without the passage (6 tests, Holm over 6).
Each route has its own notebook, so the cost of each route is measured on its own.""",
}


def build(kind):
    CELLS.clear()
    title, what = INTRO[kind]
    learn = kind == "learn"
    md(f"""
# {title}

{what}

{DESIGN_NOTE[learn]}

## How to run it on Kaggle

1. **Settings:** GPU T4 x2, Internet on.
2. **Add Input:** your private Kaggle dataset **GenreHalluEval-v2** ({"version 1 or later" if learn else "the version WITH `lock_ghe2_v1.json`"}).
3. Run all. Keep `RUN_MODE = "full"` (a `"pilot"` of 24 questions, 2 per genre, is only for a quick check).
4. When it ends, download the `ghe2_…_outputs.zip` from the Output tab and give it to Claude.
5. **If the run stops** (time limit, error): "Save Version", then in a new version **Add Input → this notebook's own
   output**, and run all again. Finished calls are skipped. Add only this notebook's own earlier output.
""")
    code(f'''
# ======================= EDIT ONLY THIS CELL =======================
RUN_MODE = "full"           # "full" = the whole half (600 questions); "pilot" = 24 questions (2 per genre), a check only
TIME_BUDGET_HOURS = 11.0    # stop cleanly before Kaggle's 12-hour limit; then resume (step 5 above)
OLLAMA_VERSION = "0.40.6"   # the Ollama of every earlier run. Do not change
{'MODELS_THIS_RUN = None      # None = every pool model; or a list, e.g. ["deepseek-r1-14b"] (see the sessions above)' if learn else ''}
# ===================================================================
NOTEBOOK = "{kind}"
SPLIT_DATASET = "{'ghe2_learn' if learn else 'ghe2_test'}"
METHODS = {'[]' if learn else '["A"]' if kind == "single_best" else '["' + kind[-1] + '"]'}
MODEL_KEY = "gemma4-31b"    # the starting model; the notebook switches models by itself
PARALLEL = None             # requests at once: each model's default
STAGES = {'["genre", "judge"]' if kind != "single_best" else '["judge"]'}
JUDGE_CONDITIONS = ["context", "no_context"]
''')
    code(IMPORTS)
    md("## The judge models (the same table as every earlier run)")
    code(d2.MODELS_CELL)
    md(f"## Load the {'learn' if learn else 'test'} half{'' if learn else ' and the lock'} (files must match `checksums.sha256`)")
    code(DATA_CELL if learn else TEST_DATA_CELL)
    md("## The prompts (English for most models, Bangla for TigerLLM; golden rule 1 check)")
    code(PROMPTS_CELL)
    code(sp.LANG_CELL)
    md("## The model backends (Ollama; a fake model for local tests)")
    code(BACKEND_CELL)
    md("## Logging, parsing and resuming (one log line per call; strict parse; `no_answer` counted separately)")
    code(d2.RUN_CELL)
    code(PARSE_BN_CELL)
    md("## Model switching")
    code(sp.SWITCH_CELL)
    if learn:
        md("## Every model: genre of every question, then every answer with and without the passage")
        code(sp.LEARN_CELL)
    else:
        md("## The routes in `lock_ghe2_v1.json`")
        code(TEST_LOCK_CELL)
        if kind.startswith("route_"):
            md("## Turn 1: the asked LLMs name the genre (question + passage only)")
            code(sp.TURN1_CELL)
        else:
            code("NAMED, GENRE_COMPLETE = {}, True     # route A needs no genre")
        md("## Turn 2: route every answer, then each picked judge judges its answers")
        code(TURN2_CELL)
    md("## Cost, manifest and the outputs zip")
    code(sp.SAVE_CELL)
    return list(CELLS)


def main():
    """Writes the test notebooks; pass --learn to rewrite the learn notebook too (it already ran on 2026-10-29)."""
    root = Path(sys.argv[1])
    rel = root / "release/kaggle-genrehallueval-v2"
    rel.mkdir(parents=True, exist_ok=True)
    kinds = ("learn",) * ("--learn" in sys.argv) + ("route_E", "route_F", "route_R", "single_best")
    for kind in kinds:
        nb = root / "notebooks" / f"ghe2_{kind}.ipynb"
        base.write_notebook(build(kind), nb)
        shutil.copyfile(nb, rel / nb.name)
        print("wrote", nb, "and", rel / nb.name)


if __name__ == "__main__":
    main()
