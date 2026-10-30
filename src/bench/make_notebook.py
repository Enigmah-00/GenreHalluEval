"""Write notebooks/benchmark_one_llm.ipynb (the Kaggle notebook that benchmarks one LLM per run).

The notebook is plain Python (no shell magics), so src/bench/run_notebook_locally.py can test it with a fake
("mock") model before it goes to Kaggle.

Usage: python3 -I src/bench/make_notebook.py <project_root>
"""
import json
import sys
from pathlib import Path

CELLS = []


def md(text):
    CELLS.append(("markdown", text.strip("\n")))


def code(text):
    CELLS.append(("code", text.strip("\n")))


# --------------------------------------------------------------------------------------------------------
md(r"""
# Benchmark one LLM on BenHalluEval-QA v1.3: genre guessing and hallucination judging

**One run of this notebook = one LLM.** To test another LLM, change one line (`MODEL_KEY`) and run it again.

The LLM does two jobs (two "turns"). Each turn has its own prompt:

| Turn | The LLM sees | The LLM answers | Calls (full run) |
|---|---|---|---|
| **Turn 1: genre** | question + passage (**never the answer**) | one of 6 genres | 920 (one per question) |
| **Turn 2: judge, with passage** (`context`) | passage + question + one answer | `yes` (hallucinated) or `no` | 4,600 |
| **Turn 2: judge, without passage** (`no_context`) | question + one answer only | `yes` or `no` | 4,600 |

**Two judging conditions (both are main conditions of the study):** with the passage, the judge checks the
answer against the passage. Without it, the judge must use its own knowledge. The labels are the same in both,
because every gold was checked against today's world (v1.3) and every hallucinated answer is wrong in the real
world. The genre is always guessed from question + passage, so one genre guess serves both conditions.

From these saved outputs the notebook makes **two runs (two ways of scoring)**:

- **Run 1, our human genres.**
  - How well does the LLM guess the genre? This compares its genres with our human-verified labels
    (accuracy, macro-F1, Cohen's kappa, confusion table) and with 200 labels a person made blind.
  - How well does it judge inside each **human** genre? BHS per genre.
- **Run 2, its own genres.** We take the LLM's genre guess as true and ask how well it judges inside each
  genre **it named itself**. Every question counts, even when its genre disagrees with ours. This is the
  {LLM, genre} table: each row is one (this LLM, a genre it named) pair, the pairs that method F routes on.

Both runs are reported for each judging condition, side by side.

**Why one set of calls serves both runs.** The verdict does not depend on the genre. Run 1 and Run 2 only
group the same verdicts differently. So we ask each question once and each answer once. That halves the
cost and makes the two runs directly comparable, because the verdicts are identical. The genre is asked in
its own call, without the answer, because seeing the answer would leak the label into the genre
(golden rule 1).

**BHS (BenHalluScore)** = ½ × (Track A error + Track B error) × 100. Lower is better; 50 is chance.
- Track A error: correct answers that the judge calls hallucinated.
- Track B error: hallucinated answers that the judge misses.
""")

md(r"""
## Where to change what (control map)

| You want to … | Go to | Change |
|---|---|---|
| test another LLM | section 3 | `MODEL_KEY` (the list is in section 4) |
| judge with the passage, without it, or both | section 3 | `JUDGE_CONDITIONS = ["context"]`, `["no_context"]` or `["context", "no_context"]` |
| run a small test or the whole set | section 3 | `RUN_MODE = "pilot"` (40 questions) or `"full"` (920) |
| see the prompts the LLM gets | section 6 | nothing to change: the prompts are files in the dataset (`prompts/`) |
| ask the LLM for the genre (turn 1) | section 9 | runs automatically |
| let the LLM judge (turn 2) | section 10 | runs automatically, once per condition |
| see how well it **guesses the genre** vs our hand-checked genres | section 13 (Run 1) | read the "Genre guessing" and "Confusion" tables |
| see how well it **judges in each of our genres** | section 13 (Run 1) | read "Judge score in each HUMAN genre" |
| see how well it **judges in the genres it named itself** ({LLM, genre} pairs) | section 14 (Run 2) | read "Judge score in each genre the LLM named itself" |
| compare with vs without the passage | sections 12–14 | read the "side by side" tables |
| download the results | Output tab | `<model>__<mode>__outputs.zip` |

Everything else runs by itself. Edit only the settings cell (section 3).

## Rules this notebook enforces (from the project's golden rules)

| Rule | How the code enforces it |
|---|---|
| 1. Never show the answer when asking for the genre | The genre prompt takes only question + passage, and a check fails the run if an answer leaks in. |
| 3. Choose everything on BenHalluEval only | The notebook stops if it is pointed at Dataset 2. Routing choices are made later, offline. |
| 5. Ignore small cells | Every (judge, genre) cell with fewer than 50 questions is marked `usable = no`. |
| 6. Same prompt and settings for every judge | One prompt file per turn, temperature 0, seed 2026, the model's own chat template, no system message. |
| 8. 95% ranges from a bootstrap over **questions** | All ranges re-sample questions (1,000 times), never single answers. |
| 9. Report cost | Calls, tokens and time are saved next to every score. |
| No silent truncation | The context size is measured before the run. Any prompt that was cut, or is too long, is counted as `no_answer` and reported. |
| Strict parsing | Only `yes`/`no` (or one genre code) counts. Everything else is `no_answer`, counted separately. |
| Never overwrite | Every call is appended to a log file. Re-running resumes; it never deletes. |
| One setup per study | Each record carries a setup fingerprint. The notebook refuses to mix records made with a different model version, prompt or settings. |
""")

# --------------------------------------------------------------------------------------------------------
md(r"""
## 1. One-time setup (do this once, before the first model)

**1a. Upload the dataset (private).**
1. On your computer, zip the folder `data/final/benhallueval-qa-v1.3/`. A ready zip is
   `data/final/benhallueval-qa-v1.3.zip`.
   - If you uploaded an older version before, open that Kaggle dataset and click **New Version** with this zip,
     or remove the old input from the notebook. The notebook stops if it sees two datasets.
2. On kaggle.com, go to **Create → New Dataset**. Drag the zip in. Kaggle unpacks it.
3. Title: **`BenHalluEval-QA Bangla`**. Kaggle makes the URL name `benhallueval-qa-bangla` from it. Keep
   **Private** (the licence check is still pending) and click **Create**. For a later version of the data,
   open the same dataset and click **New Version**; do not make a new dataset. Then every notebook keeps the
   same input, and Kaggle keeps the old versions.
4. Check that the dataset shows `items.csv`, `prompts/` and `checksums.sha256` at its top level. The notebook
   finds the dataset by these files, so the folder name does not matter.

(Command-line alternative: put your username in `dataset-metadata.json`, then run
`kaggle datasets create -p data/final/benhallueval-qa-v1.3`.)

**1b. Create the notebook.**
1. **Create → New Notebook**, then **File → Import Notebook** and upload `notebooks/benchmark_one_llm.ipynb`.
2. In the right panel (**Settings**):
   - **Accelerator: GPU T4 x2.** The 27–32B models need both GPUs (about 20 GB). Smaller models also run
     faster there.
   - **Internet: On.** It downloads Ollama and the model. Turning it on needs a phone-verified Kaggle account.
   - Language Python, environment "latest".
3. **Add Input → Datasets → Your Datasets →** `BenHalluEval-QA Bangla`.

**1c. Secrets (only if needed).** Use **Add-ons → Secrets**, and never paste a key into a cell.
- `OPENAI_API_KEY`: only for `gpt-4.1-mini`. A full run of both conditions costs about $2–5 (estimate; check
  current prices; the no-context prompts are short).
- `HF_TOKEN`: only if a Hugging Face model is gated (none on the default list is).

**1d. Before the first pilot: write your predictions.** The plan (section 2.8) asks for
`docs/expectations.md` and `docs/preregistration.md` to be committed **before any judge result**. A pilot
already shows judge results, so write both first.
""")

md(r"""
## 2. The routine for every model

1. In section 3, set `MODEL_KEY` and leave `RUN_MODE = "pilot"`.
2. Click **Save Version → Save & Run All (Commit)**. A commit runs in the background (up to 12 hours), you can
   close the browser, and the outputs are kept with the version. An interactive session loses its outputs
   when it ends.
3. Open the finished version's **Logs/Output** and read the **pilot report** at the end. The run should have:
   - a parse rate near 100% (few `no_answer`);
   - no truncated or too-long prompts;
   - speed, with an **estimated full-run time** (both conditions double the judge calls). Decide whether you
     can afford it before you go on. If the time is too long, run one condition per version: the resume
     reuses everything that is already done.

   Compare the pilot BHS only roughly with the paper. Our hallucinated answers are new, so the numbers are not
   directly comparable.
4. Set `RUN_MODE = "full"`. Click **Add Input → Your Work** and add the **pilot version's output**, so the
   pilot's calls (40 genre + 200 per judging condition) are reused, not paid for twice. Commit again.
5. **If the run stops at the time budget** ("PARTIAL" in the report), add that version's output as input and
   commit again with the same settings. It continues where it stopped.
6. From the version's **Output** tab, download `<model>__full__outputs.zip`. Unzip it into the project:
   `runs/` goes to `runs/` and `results/` goes to `results/`. Never overwrite an existing file.
7. Go to the next model.

**Pin the setup after the first pilot.** The first pilot prints the Ollama version. Write it into
`OLLAMA_VERSION` in section 3 and keep it for **every** model and for Dataset 2 later. Then all judges run
with the same software (golden rule 6; "one setup for both datasets").
""")

# --------------------------------------------------------------------------------------------------------
md(r"""
## 3. Settings (edit only this cell)
""")

code(r'''
# ======================= EDIT ONLY THIS CELL =======================
MODEL_KEY = "llama3.1-8b"   # which LLM to test: a key from the table in section 4
RUN_MODE = "pilot"          # "pilot" = 40 questions (200 answers); "full" = all 920 questions (4,600 answers)
JUDGE_CONDITIONS = ["context", "no_context"]  # judge WITH the passage, WITHOUT it, or both (the study uses both)
STAGES = ["genre", "judge"] # turn 1 = genre, turn 2 = judge. Keep both.
PARALLEL = None             # requests at once; None = the model's default from section 4
TIME_BUDGET_HOURS = 11.0    # stop cleanly before Kaggle's 12-hour limit, then resume (section 2, step 5)
OLLAMA_VERSION = "0.40.6"   # pinned 2026-10-18 (runs 2-3 used it). Keep it for every model and for Dataset 2
# ===================================================================
''')

code(r'''
import collections, csv, datetime, glob, hashlib, json, math, os, platform, random, re, shutil
import statistics, subprocess, sys, threading, time, urllib.error, urllib.request, zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

T0 = time.time()
SEED = 2026
DATASET = "benhallueval"            # this notebook only ever reads BenHalluEval (golden rule 3)
GENRES = {"HISTORY": "History, Politics & Education", "ARTS": "Arts, Culture & Sports",
          "SCIENCE": "Science & Technology", "GEOGRAPHY": "Geography & Places",
          "RELIGION": "Religion", "OTHER": "Other"}
CODE_OF = {name: code for code, name in GENRES.items()}
MIN_CELL = 50                       # golden rule 5
PILOT_QUESTIONS = 40
BOOT = 1000


class Stop(Exception):
    """A clear, deliberate stop with an instruction for the user."""


try:
    from IPython.display import Markdown, display

    def show_md(text):
        display(Markdown(text))
except Exception:
    def show_md(text):
        print(text)


def find_data_dir():
    if os.environ.get("BENCH_DATA_DIR"):
        return Path(os.environ["BENCH_DATA_DIR"])
    hits = []
    for depth in ("*", "*/*", "*/*/*", "*/*/*/*"):
        hits += glob.glob(f"/kaggle/input/{depth}/items.csv")
    hits = sorted({str(Path(h).parent) for h in hits if (Path(h).parent / "prompts" / "judge_v1.txt").exists()})
    if len(hits) != 1:
        raise Stop(f"Expected exactly one BenHalluEval-QA dataset under /kaggle/input, found {hits}. "
                   "Add it with 'Add Input' (section 1a).")
    return Path(hits[0])


DATA_DIR = find_data_dir()
if any(bad in str(DATA_DIR).lower() for bad in ("dataset2", "dataset-2", "banglarqa")):
    raise Stop("This notebook reads BenHalluEval only. Dataset 2 is test-only and is never used to make "
               "choices (golden rule 3).")
OUT_DIR = Path(os.environ.get("BENCH_OUT_DIR", "/kaggle/working"))
RUN_DIR, RES_DIR = OUT_DIR / "runs", OUT_DIR / "results"
RUN_DIR.mkdir(parents=True, exist_ok=True)
RES_DIR.mkdir(parents=True, exist_ok=True)
assert RUN_MODE in ("pilot", "full"), RUN_MODE
assert STAGES and set(STAGES) <= {"genre", "judge"}, STAGES
assert JUDGE_CONDITIONS and set(JUDGE_CONDITIONS) <= {"context", "no_context"}, JUDGE_CONDITIONS
COND_NAME = {"context": "WITH the passage", "no_context": "WITHOUT the passage"}
print("dataset:", DATA_DIR)
print("outputs:", OUT_DIR)
''')

# --------------------------------------------------------------------------------------------------------
md(r"""
## 4. The model list (and why these models)

**Primary pool: open-weight judges** (free, run here, decided before any result):

| Key | Model | Why it is on the list | Notes |
|---|---|---|---|
| `llama3.1-8b` | Llama-3.1-8B-Instruct | paper judge (multilingual) | fast; **good first pilot** |
| `mistral-nemo-12b` | Mistral-Nemo-12B | paper judge (multilingual) | |
| `gemma2-27b` | Gemma-2-27B-it | paper judge (multilingual) | context 8,192 |
| `qwen2.5-32b` | Qwen2.5-32B-Instruct | paper judge (multilingual) | needs both GPUs |
| `deepseek-r1-14b` | DeepSeek-R1-Distill-Qwen-14B | paper judge (reasoning) | **slowest by far**: thinks before answering; thinking capped at 1,024 tokens |
| `tigerllm-9b` | TigerLLM-9B-it | paper judge (Bangla); best open QA judge in the paper | GGUF of the Sept 2025 upload of `md-nishat-008/TigerLLM-9B-it`, the only public version during the paper's study. Despite the name it is a Gemma-3 model of about 12B (the code checks `gemma3`). In Sept–Oct 2026 the repo got new weights and was renamed TigerLLM-12B-it; do not use those |
| `titullm-3b` | TituLLM-3B (Llama-3.2) | paper judge (Bangla) | a base model (not instruction-tuned): it gave no usable reply in our run either |
| `titullm-3b-instruct` | TituLLM-3B v2.0 Instruct v1.0 | **added 2026-10-18, before any result**: the instruction-tuned TituLLM, so the study has a working small Bangla-centric judge | not the paper's checkpoint; transformers 4-bit (no GGUF exists); its own chat template; revision pinned |
| `banglallama-13b` | BanglaLLaMA-13B-instruct | paper judge (Bangla) | LLaMA-2, context 4,096; runs in 4-bit with transformers (no GGUF found) |
| `gemma4-31b` | Gemma 4 31B | **new (2026)**, strong multilingual family | needs both GPUs |
| `qwen3.5-27b` | Qwen3.5 27B | **new (2026)**, "201 languages" | thinking turned off, so it judges zero-shot like the others |
| `gpt-oss-20b` | gpt-oss 20B | **new, optional**: a second reasoning family | thinking set to "low"; slower |

**Secondary pool:** `gpt-4.1-mini` (paper judge; the best QA judge in the paper). Paid API; dated snapshot.

**Never** use a Claude model as a judge or genre guesser. Claude drafted the genre labels and wrote the
hallucinated answers.

**Suggested order:**
1. `llama3.1-8b` (fast; tests the whole pipeline).
2. The other small and medium models.
3. The 27–32B models.
4. `deepseek-r1-14b` last. Plan several sessions for it; the resume works.

Two teammates' Kaggle accounts can run different models in parallel, if both use the same `OLLAMA_VERSION`.

**Quantization.** Ollama models use 4-bit GGUF (`Q4_K_M`), as the paper's Ollama setup most likely did.
BanglaLLaMA and the TituLLM instruct model use 4-bit NF4 with transformers. The exact quantization and digest
(or revision) are saved in every record.
""")

code(r'''
DEFAULTS = dict(think=None, max_new={"genre": 8, "judge": 8}, parallel=4, max_ctx=32768, expect_arch=None,
                revision="main", note="")
MODELS = {
    # ---- the paper's 9 judges ----
    "llama3.1-8b": dict(backend="ollama", model="llama3.1:8b", pool="open", source="paper"),
    "mistral-nemo-12b": dict(backend="ollama", model="mistral-nemo:12b", pool="open", source="paper"),
    "gemma2-27b": dict(backend="ollama", model="gemma2:27b", pool="open", source="paper", parallel=2,
                       max_ctx=8192),
    "qwen2.5-32b": dict(backend="ollama", model="qwen2.5:32b", pool="open", source="paper", parallel=2),
    "deepseek-r1-14b": dict(backend="ollama", model="deepseek-r1:14b", pool="open", source="paper", think=True,
                            max_new={"genre": 1024, "judge": 1024},
                            note="thinking capped at 1,024 tokens; capped replies count as no_answer"),
    "tigerllm-9b": dict(backend="ollama", model="hf.co/mradermacher/TigerLLM-9B-it-GGUF:Q4_K_M", pool="open",
                        source="paper", expect_arch="gemma3", max_ctx=8192,
                        note="GGUF (2025-09-15) of the Sept 2025 TigerLLM-9B-it upload: Gemma-3, ~12B despite the name"),
    "titullm-3b": dict(backend="ollama", model="hf.co/mradermacher/titulm-llama-3.2-3b-v1.1-GGUF:Q4_K_M",
                       pool="open", source="paper", expect_arch="llama",
                       note="hishab/titulm-llama-3.2-3b-v1.1; check it is the checkpoint the paper used"),
    "banglallama-13b": dict(backend="hf", model="BanglaLLM/bangla-llama-13b-instruct-v0.1", pool="open",
                            source="paper", max_ctx=4096, lora_merge=dict(r=64, alpha=128), batch_tokens=6144,
                            note="LLaMA-2 based; the checkpoint stores un-merged LoRA layers, merged here with "
                                 "r=64, alpha=128 (its training script); prompts over 4,096 tokens are skipped"),
    "titullm-3b-instruct": dict(backend="hf", model="hishab/titulm-llama-3.2-3b-v2.0-Instruct-v1.0",
                                revision="6a9600483daf9a3af7494e7fa91f2e72e2799b96", pool="open",
                                source="new (instruct TituLLM, added 2026-10-18)", max_ctx=4096, parallel=8,
                                batch_tokens=16384,
                                note="instruction-tuned TituLLM (not the paper's base checkpoint); own chat template"),
    "gpt-4.1-mini": dict(backend="openai", model="gpt-4.1-mini-2025-04-14", pool="closed", source="paper",
                         parallel=8, max_ctx=1_000_000, note="secondary pool only; paid API"),
    # ---- new open models (2025-26) ----
    "gemma4-31b": dict(backend="ollama", model="gemma4:31b", pool="open", source="new", parallel=2),
    "qwen3.5-27b": dict(backend="ollama", model="qwen3.5:27b", pool="open", source="new", think=False,
                        parallel=2),
    "gpt-oss-20b": dict(backend="ollama", model="gpt-oss:20b", pool="open", source="new (optional)",
                        think="low", max_new={"genre": 512, "judge": 512}),
}
PAPER_QA_BHS = {"deepseek-r1-14b": 38.60, "gpt-4.1-mini": 15.56, "qwen2.5-32b": 46.85, "gemma2-27b": 47.45,
                "mistral-nemo-12b": 53.84, "llama3.1-8b": 47.71, "tigerllm-9b": 28.28, "titullm-3b": 50.00,
                "banglallama-13b": 48.62}   # zero-shot QA, paper Table 4 (other answers, so only a rough guide)
PRICE_PER_M = {"gpt-4.1-mini-2025-04-14": (0.40, 1.60)}  # USD per 1M input/output tokens; check current prices

if MODEL_KEY not in MODELS:
    raise Stop(f"MODEL_KEY must be one of: {', '.join(MODELS)}")
CFG = {**DEFAULTS, **MODELS[MODEL_KEY]}
if "claude" in CFG["model"].lower():
    raise Stop("Claude wrote the genre drafts and the hallucinated answers: never use it as a judge or guesser.")
if os.environ.get("BENCH_BACKEND_OVERRIDE"):          # local tests only
    CFG["backend"] = os.environ["BENCH_BACKEND_OVERRIDE"]
PAR = PARALLEL or CFG["parallel"]
show_md("| key | backend | model | pool | source | parallel | note |\n|---|---|---|---|---|---|---|\n" + "\n".join(
    f"| {'**' + k + '**' if k == MODEL_KEY else k} | {m['backend']} | `{m['model']}` | {m['pool']} | {m['source']} "
    f"| {m.get('parallel', DEFAULTS['parallel'])} | {m.get('note', '')} |" for k, m in MODELS.items()))
print(f"\nThis run: {MODEL_KEY} | mode {RUN_MODE} | stages {STAGES} | conditions {JUDGE_CONDITIONS} | parallel {PAR}")
''')

# --------------------------------------------------------------------------------------------------------
md(r"""
## 5. Load the data and check it

- `items.csv`: 4,600 rows = 920 questions × (1 correct + 4 hallucinated answers). We use `include_main = yes`
  (all 920).
- The file checksums are compared with `checksums.sha256`. A broken or changed upload stops the run.
- **Pilot sample:** 40 questions, stratified by human genre with at least 3 per genre (seed 2026), with all
  5 answers each: 40 correct + 160 hallucinated = 200 judge calls, plus 40 genre calls. Whole questions are
  sampled, never single answers, because answers to one question are not independent.
""")

code(r'''
def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


sums = {}
for line in (DATA_DIR / "checksums.sha256").read_text(encoding="utf-8").splitlines():
    if line.strip():
        digest, name = line.split("  ", 1)
        sums[name.strip()] = digest
for name in ["items.csv", "genre_blind200.csv", "prompts/judge_v1.txt", "prompts/judge_noctx_v1.txt",
             "prompts/genre_v1.txt"]:
    if hashlib.sha256((DATA_DIR / name).read_bytes()).hexdigest() != sums.get(name):
        raise Stop(f"{name} does not match checksums.sha256. Re-upload the dataset folder unchanged.")

ITEMS = [r for r in read_csv(DATA_DIR / "items.csv") if r["include_main"] == "yes"]
QUESTIONS = {}
for r in ITEMS:
    QUESTIONS.setdefault(r["question_id"], dict(question=r["question"], context=r["context"],
                                               genre_human=CODE_OF[r["genre"]]))
BLIND = {r["question_id"]: CODE_OF[r["genre_blind_human"]] for r in read_csv(DATA_DIR / "genre_blind200.csv")}

by_genre = collections.defaultdict(list)
for qid in sorted(QUESTIONS):
    by_genre[QUESTIONS[qid]["genre_human"]].append(qid)
alloc = {g: max(3, round(PILOT_QUESTIONS * len(q) / len(QUESTIONS))) for g, q in by_genre.items()}
while sum(alloc.values()) > PILOT_QUESTIONS:
    alloc[max(alloc, key=alloc.get)] -= 1
while sum(alloc.values()) < PILOT_QUESTIONS:
    alloc[max(alloc, key=alloc.get)] += 1
rng = random.Random(SEED)
PILOT_QIDS = {q for g in sorted(by_genre) for q in rng.sample(by_genre[g], alloc[g])}

RUN_QIDS = PILOT_QIDS if RUN_MODE == "pilot" else set(QUESTIONS)
RUN_ITEMS = [r for r in ITEMS if r["question_id"] in RUN_QIDS]       # file order: 5 answers per question together
print(f"{len(QUESTIONS)} questions, {len(ITEMS)} items in the main set; "
      f"this {RUN_MODE} run uses {len(RUN_QIDS)} questions and {len(RUN_ITEMS)} items")
print("human genres in this run:", dict(collections.Counter(QUESTIONS[q]["genre_human"] for q in RUN_QIDS)))
print("blind human labels available for", len(set(BLIND) & RUN_QIDS), "of these questions")
''')

# --------------------------------------------------------------------------------------------------------
md(r"""
## 6. The prompts

The prompts are files in the dataset (`prompts/`), not strings in this notebook. Their fingerprints are
saved with every call. Details and reasons are in `prompts/README.md`.

- **Turn 1, genre (`genre_v1`):** the 6 genres and the 8 rules of the frozen genre guide v1.0. Input:
  **question + passage only**. Reply: one code word (`HISTORY`, `ARTS`, `SCIENCE`, `GEOGRAPHY`, `RELIGION`,
  `OTHER`). Code words are easy for small models and easy to parse.
- **Turn 2, judge with the passage (`judge_v1`):** BenHalluEval's own zero-shot judge prompt (paper
  Table 14), unchanged, so our judges see what the paper's judges saw. Reply: `yes` or `no`. The answer
  comes last, so the 5 answers of a question share the same prompt start, and Ollama reuses that part
  (faster, same result).
- **Turn 2, judge without the passage (`judge_noctx_v1`):** the same prompt with the passage line removed;
  "yes" means the answer is false or does not answer the question correctly. Only the passage differs
  between the two conditions.

The cell below prints one filled example of each prompt and runs the **golden rule 1 check**: no answer text
may appear in any genre prompt.
""")

code(r'''
PROMPT_IDS = {"genre": "genre_v1", "judge:context": "judge_v1", "judge:no_context": "judge_noctx_v1"}
TEMPLATES = {k: (DATA_DIR / "prompts" / f"{pid}.txt").read_text(encoding="utf-8").rstrip()
             for k, pid in PROMPT_IDS.items()}
PROMPT_SHA = {k: hashlib.sha256(t.encode("utf-8")).hexdigest()[:12] for k, t in TEMPLATES.items()}
SLOT = re.compile(r"\{(context|question|answer)\}")


def fill(template, **values):
    return SLOT.sub(lambda m: values[m.group(1)], template)        # one pass: braces in a passage are safe


def genre_prompt(question, context):                               # takes no answer, by design (rule 1)
    return fill(TEMPLATES["genre"], question=question, context=context)


def judge_prompt(condition, context, question, answer):
    if condition == "context":
        return fill(TEMPLATES["judge:context"], context=context, question=question, answer=answer)
    return fill(TEMPLATES["judge:no_context"], question=question, answer=answer)


assert "{answer}" not in TEMPLATES["genre"], "the genre prompt must not have an answer slot"
assert "{context}" in TEMPLATES["judge:context"], "the with-passage judge prompt needs the passage"
assert "{context}" not in TEMPLATES["judge:no_context"], "the no-context judge prompt must not show the passage"
leaks = []
for r in ITEMS:
    q = QUESTIONS[r["question_id"]]
    a = r["answer"].strip()
    # a leak = the answer appears in the genre prompt more often than the guide text, question and passage explain
    explained = TEMPLATES["genre"].count(a) + q["question"].count(a) + q["context"].count(a)
    if a and genre_prompt(q["question"], q["context"]).count(a) > explained:
        leaks.append(r["item_id"])
if leaks:
    raise Stop(f"Golden rule 1 broken: answer text found in {len(leaks)} genre prompts, e.g. {leaks[:3]}")
print("Golden rule 1 check passed: no answer text in any genre prompt.")
print("prompt fingerprints:", PROMPT_SHA)

ex = RUN_ITEMS[0]
q0 = QUESTIONS[ex["question_id"]]
print("\n========== example: turn 1 (genre) ==========\n" + genre_prompt(q0["question"], q0["context"])[-700:])
for c in JUDGE_CONDITIONS:
    print(f"\n========== example: turn 2 (judge, {c}) ==========\n"
          + judge_prompt(c, q0["context"], q0["question"], ex["answer"]))
''')

# --------------------------------------------------------------------------------------------------------
md(r"""
## 7. Start the model

What happens here depends on the backend:

- **Ollama** (most models). It installs Ollama (the version in `OLLAMA_VERSION`, else the latest), starts
  the server, downloads the model and saves its **digest**, its architecture and its quantization. Then it
  runs a **context check**: it measures the longest prompts with the real tokenizer and sets the context
  size (`num_ctx`) so no prompt is cut. The check always uses the full question set, so the pilot and the
  full run get the same `num_ctx`. Two guards catch any cut prompt during the run: the token count, and
  Ollama's own warning in the server log.
- **transformers** (`banglallama-13b`). It loads the model in 4-bit and saves the exact Hugging Face
  revision. Every prompt is tokenized exactly. A prompt that does not fit is marked `too_long` and never cut.
- **OpenAI** (`gpt-4.1-mini`). It uses the dated snapshot and reads the key from Kaggle Secrets.

The first download takes a few minutes (a 32B model is about 20 GB).
""")

code(r'''
def sh(cmd, check=True):
    print("$", cmd)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout.strip()[-1500:])
    if r.returncode and check:
        print(r.stderr[-3000:])
        raise Stop(f"Command failed: {cmd}")
    return r.stdout


def http_json(url, payload=None, timeout=1800):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_secret(name, required):
    if os.environ.get(name):
        return os.environ[name]
    try:
        from kaggle_secrets import UserSecretsClient
        return UserSecretsClient().get_secret(name)
    except Exception:
        if required:
            raise Stop(f"Add the secret {name} under Add-ons -> Secrets (section 1c).")
        return None


def result(raw="", status="ok", prompt_tokens=None, output_tokens=None, done_reason="", latency=0.0,
           thinking_chars=0, error=None):
    return dict(raw=raw, status=status, prompt_tokens=prompt_tokens, output_tokens=output_tokens,
                done_reason=done_reason, latency_s=round(latency, 3), thinking_chars=thinking_chars, error=error)


ALL_PROMPTS = ([genre_prompt(q["question"], q["context"]) for q in QUESTIONS.values()]
               + [judge_prompt(c, QUESTIONS[r["question_id"]]["context"], QUESTIONS[r["question_id"]]["question"],
                               r["answer"]) for c in JUDGE_CONDITIONS for r in ITEMS])


class OllamaBackend:
    url = "http://127.0.0.1:11434"

    def __init__(self, cfg, parallel):
        self.cfg, self.parallel = cfg, parallel
        if not shutil.which("ollama"):
            sh("apt-get -qq update > /dev/null && apt-get -qq install -y zstd > /dev/null", check=False)
            pin = f"OLLAMA_VERSION={OLLAMA_VERSION} " if OLLAMA_VERSION else ""
            sh(f"curl -fsSL https://ollama.com/install.sh | {pin}sh")
        env = dict(os.environ, OLLAMA_NUM_PARALLEL=str(parallel), OLLAMA_MAX_LOADED_MODELS="1",
                   OLLAMA_KEEP_ALIVE="24h", OLLAMA_HOST="127.0.0.1:11434")
        self.log_path = OUT_DIR / f"ollama_server__{MODEL_KEY}.log"
        self.proc = subprocess.Popen(["ollama", "serve"], env=env, stdout=open(self.log_path, "a"),
                                     stderr=subprocess.STDOUT)
        for _ in range(90):
            try:
                self.version = http_json(self.url + "/api/version", timeout=5)["version"]
                break
            except Exception:
                time.sleep(1)
        else:
            raise Stop(f"The Ollama server did not start; read {self.log_path}")
        if OLLAMA_VERSION and self.version != OLLAMA_VERSION:
            raise Stop(f"Ollama {self.version} is running but OLLAMA_VERSION is {OLLAMA_VERSION}. Restart the session.")
        sh(f"ollama pull {cfg['model']}")
        tags = http_json(self.url + "/api/tags")["models"]
        hit = [m for m in tags if cfg["model"] in (m.get("name"), m.get("model"))]
        if not hit:
            raise Stop(f"{cfg['model']} not found after pull; installed: {[m.get('name') for m in tags]}")
        self.digest = hit[0]["digest"]
        info = http_json(self.url + "/api/show", {"model": cfg["model"]})
        self.arch = info.get("model_info", {}).get("general.architecture", "?")
        self.quant = info.get("details", {}).get("quantization_level", "?")
        if "thinking" in info.get("capabilities", []) and cfg.get("think") is None:
            cfg["think"] = False      # zero-shot like the other judges; reasoning judges set think explicitly
            print("This model can think before answering; thinking is turned OFF (think=False) for a zero-shot verdict.")
        if cfg.get("expect_arch") and self.arch != cfg["expect_arch"]:
            raise Stop(f"{cfg['model']} has architecture {self.arch}, expected {cfg['expect_arch']}. "
                       "This is not the model the paper used. Find the right GGUF before going on.")
        self.model_id = cfg["model"]
        self.version_id = f"ollama {self.version}; digest {self.digest}; {self.quant}"
        self.num_ctx = None
        print(f"Ollama {self.version} | {cfg['model']} | digest {self.digest[:16]} | arch {self.arch} | {self.quant}")

    def one(self, prompt, max_new, num_ctx):
        payload = {"model": self.cfg["model"], "messages": [{"role": "user", "content": prompt}],
                   "stream": False, "keep_alive": "24h",
                   "options": {"temperature": 0, "seed": SEED, "num_ctx": num_ctx, "num_predict": max_new}}
        if self.cfg.get("think") is not None:
            payload["think"] = self.cfg["think"]
        t, err = time.time(), None
        for attempt in range(3):
            try:
                r = http_json(self.url + "/api/chat", payload)
                break
            except Exception as e:
                err = repr(e)[:300]
                time.sleep(5 * (attempt + 1))
        else:
            return result(status="error", latency=time.time() - t, error=err)
        msg = r.get("message", {})
        pt = r.get("prompt_eval_count")
        cut = pt is not None and pt >= num_ctx - max_new - 16      # guard 1: the prompt filled the context
        return result(raw=msg.get("content", ""), status="truncated" if cut else "ok", prompt_tokens=pt,
                      output_tokens=r.get("eval_count"), done_reason=r.get("done_reason", ""),
                      latency=time.time() - t, thinking_chars=len(msg.get("thinking") or ""))

    def preflight(self, prompts):
        """Measure the longest prompts and choose num_ctx so that none is cut."""
        longest = sorted(prompts, key=len, reverse=True)[:6]
        probe_ctx = min(self.cfg["max_ctx"], 16384)
        counts = []
        for i, p in enumerate(longest):        # a unique first line stops prefix reuse from hiding tokens
            r = self.one(f"[length check {i} {time.time()}]\n" + p, 1, probe_ctx)
            if r["status"] == "error":
                raise Stop(f"The context check failed: {r['error']}")
            counts.append(r["prompt_tokens"] or 0)
        biggest, max_new = max(counts), max(self.cfg["max_new"].values())
        need = int(biggest * 1.15) + max_new + 64
        self.num_ctx = min(self.cfg["max_ctx"], int(math.ceil(need / 1024) * 1024))
        print(f"context check: longest prompt about {biggest} tokens -> num_ctx = {self.num_ctx}")
        if biggest >= probe_ctx - 8 or need > self.cfg["max_ctx"]:
            print("WARNING: the longest prompts may not fit this model. Any prompt that is cut is marked "
                  "'truncated', counted as no_answer and reported. It is never used as a verdict.")

    def generate_batch(self, prompts, max_new):
        with ThreadPoolExecutor(self.parallel) as pool:
            return list(pool.map(lambda p: self.one(p, max_new, self.num_ctx), prompts))

    def log_has_truncation(self):
        return "truncating input" in self.log_path.read_text(errors="ignore").lower()   # guard 2


def mem_report(where):
    """One line: free RAM, free disk in /tmp, free GPU memory. Shows where a memory error happens."""
    parts = [where]
    try:
        import psutil
        parts.append(f"RAM free {psutil.virtual_memory().available / 1e9:.1f} GB")
    except Exception:
        pass
    parts.append(f"disk free {shutil.disk_usage('/tmp').free / 1e9:.0f} GB")
    try:
        import torch
        for i in range(torch.cuda.device_count()):
            free, total = torch.cuda.mem_get_info(i)
            parts.append(f"GPU{i} free {free / 1e9:.1f}/{total / 1e9:.1f} GB")
    except Exception:
        pass
    print("[memory] " + " | ".join(parts))


def merge_lora_checkpoint(fetch, out_dir, r, alpha, drop=lambda path: None, part_bytes=1.5e9):
    """Some checkpoints were saved with un-merged PEFT LoRA layers (keys ...base_layer.weight,
    ...lora_A.default.weight, ...lora_B.default.weight). Plain loading then leaves every such linear layer
    uninitialized (random). This writes a normal checkpoint with W = base + (alpha / r) * B @ A.
    fetch(filename) -> local path; drop(path) frees a shard after use. Output is written in parts of about
    part_bytes, so RAM stays small (the input shard is memory-mapped). Returns out_dir."""
    import gc
    import torch
    from safetensors.torch import save_file
    out_dir = Path(out_dir)
    if (out_dir / "MERGED_OK").exists():
        return out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    index = json.loads(Path(fetch("pytorch_model.bin.index.json")).read_text(encoding="utf-8"))
    need = index.get("metadata", {}).get("total_size", 0) * 1.45
    if need and shutil.disk_usage(out_dir).free < need:
        raise Stop(f"Not enough disk to merge the LoRA layers: need about {need / 1e9:.0f} GB free in {out_dir}.")
    shards = sorted(set(index["weight_map"].values()))
    new_map, merged, parts = {}, 0, 0
    out, size = {}, 0

    def flush():
        nonlocal out, size, parts
        if out:
            parts += 1
            name = f"model-part-{parts:05d}.safetensors"
            save_file(out, str(out_dir / name), metadata={"format": "pt"})
            new_map.update({k: name for k in out})
            out, size = {}, 0
            gc.collect()

    for n, shard in enumerate(shards, 1):
        mem_report(f"merge: before shard {n}/{len(shards)}")
        path = fetch(shard)
        try:
            sd = torch.load(path, map_location="cpu", weights_only=True, mmap=True)
        except Exception as e:
            print(f"memory-mapped loading failed ({e}); loading the whole shard into RAM")
            sd = torch.load(path, map_location="cpu", weights_only=True)
        for key, t in sd.items():
            if key.endswith((".lora_A.default.weight", ".lora_B.default.weight", "rotary_emb.inv_freq")):
                continue
            if key.endswith(".base_layer.weight"):
                mod = key[: -len(".base_layer.weight")]
                a, b = sd[mod + ".lora_A.default.weight"], sd[mod + ".lora_B.default.weight"]
                if a.shape[0] != r or b.shape[1] != r:
                    raise Stop(f"{mod}: LoRA rank {a.shape[0]} is not the expected {r}, so alpha is unknown. Stop.")
                w = t.float() + (alpha / r) * (b.float() @ a.float())
                out[mod + ".weight"] = w.to(torch.float16).contiguous()
                del w
                merged += 1
            else:
                out[key] = (t.to(torch.float16) if t.is_floating_point() else t).contiguous()
            size += out[list(out)[-1]].numel() * out[list(out)[-1]].element_size()
            if size >= part_bytes:
                flush()
        flush()
        del sd
        gc.collect()
        drop(path)
    if not merged:
        raise Stop("lora_merge is set, but the checkpoint has no un-merged LoRA layers. Remove lora_merge.")
    (out_dir / "model.safetensors.index.json").write_text(json.dumps({"metadata": {}, "weight_map": new_map}))
    for f in ("config.json", "generation_config.json"):
        try:
            shutil.copyfile(fetch(f), out_dir / f)
        except Exception:
            if f == "config.json":
                raise
    (out_dir / "MERGED_OK").write_text(json.dumps(dict(r=r, alpha=alpha, merged_layers=merged)))
    print(f"merged {merged} LoRA layers (r={r}, alpha={alpha}) into {out_dir}")
    return out_dir


class HFBackend:
    def __init__(self, cfg, parallel):
        os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")   # before CUDA starts
        sh("pip install -q -U bitsandbytes accelerate", check=False)
        import torch
        from huggingface_hub import HfApi
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        token = get_secret("HF_TOKEN", required=False)
        self.cfg, self.batch, self.torch = cfg, parallel, torch
        self.sha = HfApi().model_info(cfg["model"], revision=cfg["revision"], token=token).sha
        self.tok = AutoTokenizer.from_pretrained(cfg["model"], revision=self.sha, token=token)
        self.tok.padding_side = "left"
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                   bnb_4bit_compute_dtype=torch.float16)
        source, where, merge_note = cfg["model"], dict(revision=self.sha, token=token), ""
        if cfg.get("lora_merge"):
            os.environ.setdefault("HF_XET_CHUNK_CACHE_SIZE_BYTES", "0")      # no second copy of 27 GB on disk
            from huggingface_hub import hf_hub_download
            dl = Path("/tmp/hf_download")
            mem_report("before merge")
            source = merge_lora_checkpoint(
                lambda f: hf_hub_download(cfg["model"], f, revision=self.sha, token=token, local_dir=str(dl)),
                Path("/tmp") / f"merged_{self.sha[:12]}", drop=lambda p: Path(p).unlink(missing_ok=True),
                **cfg["lora_merge"])
            where, merge_note = {}, f"; LoRA merged r={cfg['lora_merge']['r']} alpha={cfg['lora_merge']['alpha']}"
        mem_report("before loading the model in 4-bit")
        self.model, info = AutoModelForCausalLM.from_pretrained(source, **where, quantization_config=quant,
                                                                device_map="auto", torch_dtype=torch.float16,
                                                                output_loading_info=True)
        self.model.eval()
        mem_report("model loaded")
        from transformers.utils import logging as hf_logging
        hf_logging.set_verbosity_error()        # silence the per-batch "max_new_tokens and max_length" notice
        # memory for one batch grows with (prompts x tokens); LLaMA-2-13B keeps ~0.8 MB of cache per token
        self.batch_tokens = cfg.get("batch_tokens", 8192)
        missing = [k for k in info.get("missing_keys", []) if not k.endswith("rotary_emb.inv_freq")]
        if missing:                                     # never judge with uninitialized (random) weights
            raise Stop(f"{len(missing)} weights were not in the checkpoint, e.g. {missing[:3]}. They would be random. "
                       "If the names end in base_layer/lora_A/lora_B, set lora_merge for this model.")
        self.fmt = "chat_template" if self.tok.chat_template else "alpaca"
        self.model_id, self.quant, self.num_ctx = cfg["model"], "bnb-nf4", cfg["max_ctx"]
        self.version_id = f"hf revision {self.sha}; {self.quant}{merge_note}; format {self.fmt}"
        print(f"{cfg['model']} @ {self.sha[:12]} | prompt format: {self.fmt}")

    def render(self, prompt):
        if self.fmt == "chat_template":
            return self.tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False,
                                                add_generation_prompt=True)
        return f"### Instruction:\n{prompt}\n\n### Response:\n"

    def ids(self, prompt):
        return self.tok(self.render(prompt), add_special_tokens=self.fmt == "alpaca")["input_ids"]

    def preflight(self, prompts):
        lens = [len(self.ids(p)) for p in prompts]
        over = sum(n + max(self.cfg["max_new"].values()) > self.num_ctx for n in lens)
        print(f"context check: longest prompt {max(lens)} tokens; {over} of {len(lens)} prompts do not fit "
              f"{self.num_ctx} tokens and will be marked too_long (never cut)")

    def generate_batch(self, prompts, max_new):
        out, enc = [None] * len(prompts), [self.ids(p) for p in prompts]
        ok = []
        for i, e in enumerate(enc):
            if len(e) + max_new > self.num_ctx:
                out[i] = result(status="too_long", prompt_tokens=len(e))
            else:
                ok.append(i)
        ok.sort(key=lambda i: len(enc[i]))
        groups, cur = [], []
        for i in ok:                    # sorted by length: the newest prompt is the longest in its group
            if cur and (len(cur) >= self.batch or (len(cur) + 1) * (len(enc[i]) + max_new) > self.batch_tokens):
                groups.append(cur)
                cur = []
            cur.append(i)
        if cur:
            groups.append(cur)
        for idx in groups:
            self.run_group(idx, enc, out, max_new)
        return out

    def run_group(self, idx, enc, out, max_new):
        """Generate for one group; if the GPU runs out of memory, split the group in two and try again."""
        batch = self.tok.pad({"input_ids": [enc[i] for i in idx]}, return_tensors="pt").to(self.model.device)
        t = time.time()
        try:
            with self.torch.no_grad():
                gen = self.model.generate(**batch, max_new_tokens=max_new, do_sample=False,
                                          pad_token_id=self.tok.pad_token_id)
        except self.torch.cuda.OutOfMemoryError:
            del batch
            self.torch.cuda.empty_cache()
            if len(idx) == 1:
                out[idx[0]] = result(status="error", prompt_tokens=len(enc[idx[0]]),
                                     error="CUDA out of memory even for a single prompt")
                return
            print(f"GPU memory full for {len(idx)} prompts of up to {max(len(enc[i]) for i in idx)} tokens; "
                  "splitting the batch")
            half = len(idx) // 2
            self.run_group(idx[:half], enc, out, max_new)
            self.run_group(idx[half:], enc, out, max_new)
            return
        dt = (time.time() - t) / len(idx)
        for j, i in enumerate(idx):
            new = gen[j, batch["input_ids"].shape[1]:]
            n_out = int((new != self.tok.pad_token_id).sum())
            out[i] = result(raw=self.tok.decode(new, skip_special_tokens=True), prompt_tokens=len(enc[i]),
                            output_tokens=n_out, done_reason="length" if n_out >= max_new else "stop", latency=dt)


class OpenAIBackend:
    def __init__(self, cfg, parallel):
        sh("pip install -q openai", check=False)
        from openai import OpenAI
        self.client = OpenAI(api_key=get_secret("OPENAI_API_KEY", required=True))
        self.cfg, self.parallel = cfg, parallel
        self.model_id, self.quant, self.num_ctx = cfg["model"], "api", cfg["max_ctx"]
        self.version_id = f"openai {cfg['model']}"

    def preflight(self, prompts):
        print("context check: not needed (the API context is far larger than any prompt)")

    def one(self, prompt, max_new):
        t, err = time.time(), None
        for attempt in range(6):
            try:
                r = self.client.chat.completions.create(model=self.cfg["model"], temperature=0, seed=SEED,
                                                        max_tokens=max_new,
                                                        messages=[{"role": "user", "content": prompt}])
                c = r.choices[0]
                return result(raw=c.message.content or "", prompt_tokens=r.usage.prompt_tokens,
                              output_tokens=r.usage.completion_tokens, done_reason=c.finish_reason,
                              latency=time.time() - t)
            except Exception as e:
                err = repr(e)[:300]
                time.sleep(min(60, 2 ** attempt))
        return result(status="error", latency=time.time() - t, error=err)

    def generate_batch(self, prompts, max_new):
        with ThreadPoolExecutor(self.parallel) as pool:
            return list(pool.map(lambda p: self.one(p, max_new), prompts))


class MockBackend:
    """Local tests only: a fake model with a few badly formatted replies, to exercise parsing."""

    def __init__(self, cfg, parallel):
        self.model_id, self.quant, self.num_ctx, self.version_id = "mock", "none", 32768, "mock 1"

    def preflight(self, prompts):
        print("context check: mock")

    def one(self, prompt, max_new):
        h = int(hashlib.md5(prompt.encode("utf-8")).hexdigest(), 16)
        if prompt.rstrip().endswith("Genre:"):
            raw = ["HISTORY", "ARTS", "SCIENCE", "GEOGRAPHY", "RELIGION", "OTHER", "History.", "I think ARTS"][h % 8]
        elif "Context: " in prompt:
            ctx = prompt.split("Context: ", 1)[1].split("\nQuestion: ", 1)[0]
            ans = prompt.split("Model answer: ", 1)[1].rsplit("\nAnswer now:", 1)[0]
            raw = "no" if ans.strip() in ctx else "yes"
            raw = {0: "Yes.", 1: "The answer is no"}.get(h % 25, raw)
        else:                                       # no passage: the fake model guesses
            raw = {0: "Yes.", 1: "I am not sure"}.get(h % 25, ["yes", "no"][h % 2])
        return result(raw=raw, prompt_tokens=len(prompt) // 3, output_tokens=2, done_reason="stop", latency=0.001)

    def generate_batch(self, prompts, max_new):
        return [self.one(p, max_new) for p in prompts]


BACKENDS = {"ollama": OllamaBackend, "hf": HFBackend, "openai": OpenAIBackend, "mock": MockBackend}
backend = BACKENDS[CFG["backend"]](CFG, PAR)
backend.preflight(ALL_PROMPTS)
''')

# --------------------------------------------------------------------------------------------------------
md(r"""
## 8. Logging, parsing and resuming

- **One log line per call** (`runs/benhallueval__<model>__<turn>__<prompt>.jsonl`, appended, never
  overwritten). Each line holds: ids, model id and version (digest or revision), prompt id and fingerprint,
  temperature, seed, context size, timestamp, raw reply, parsed label, tokens in and out, latency and status.
- **Strict parse (official):** after removing spaces, quotes, `*` and `.,!:;` at both ends, the reply must
  be exactly `yes`/`no` (or one genre code or full genre name). Anything else is `no_answer`.
  - `no_answer` is counted and reported. In BHS it counts as an error, because a judge that gives no
    usable verdict cannot be routed to. We also report BHS on answered items only.
- **Lenient parse (diagnostic only):** the first `yes`/`no` or genre word anywhere in the reply. It shows
  whether a model fails on format rather than judgment. It never feeds a result.
- **Reasoning models:** the thinking block is removed. A reply cut off by the output limit is `no_answer`.
  Models that *can* think but are not reasoning judges get thinking turned off automatically, so they give a
  zero-shot verdict like the others.
- **If a pilot shows many `no_answer`:** read the example raw replies printed after turn 2. A format problem
  (for example "Yes, because…") shows up in the lenient parse. Never change the prompt for one model
  (golden rule 6); report it.
- **Resume:** finished calls are skipped. That covers calls from this session and from earlier versions you
  added as input; failed calls (`status = error`) are retried. Each record also stores a fingerprint of its
  exact prompt text. So after a new dataset version, only the items whose question, passage or answer changed
  are asked again. A **setup fingerprint** (model version,
  prompt, settings, Ollama version) is stored on every line. If old lines have a different fingerprint, the
  notebook stops instead of mixing two setups.
""")

code(r'''
THINK_BLOCK = re.compile(r"<think>.*?</think>", re.S)
EDGE = " \t\r\n\"'`*.,!:;"


def strip_think(text):
    text = THINK_BLOCK.sub("", text or "")
    return "" if "<think>" in text else text        # an unfinished thinking block has no final answer


def parse(stage, raw, strict=True):
    text = strip_think(raw)
    if strict:
        t = text.strip(EDGE)
        if stage == "judge":
            return t.lower() if t.lower() in ("yes", "no") else "no_answer"
        if t.upper() in GENRES:
            return t.upper()
        return CODE_OF.get(next((n for n in GENRES.values() if n.lower() == t.lower()), ""), "no_answer")
    words = re.findall(r"[A-Za-z]+", text)
    keys = ("yes", "no") if stage == "judge" else tuple(GENRES)
    for w in words:
        w2 = w.lower() if stage == "judge" else w.upper()
        if w2 in keys:
            return w2
    return "no_answer"


def base(key):
    return key.split(":")[0]                       # "judge:no_context" -> "judge"


def setup_fingerprint(key):
    parts = dict(dataset=DATASET, model_key=MODEL_KEY, model=CFG["model"], backend=CFG["backend"],
                 version=backend.version_id, prompt=PROMPT_SHA[key], temperature=0, seed=SEED,
                 think=CFG.get("think"), max_new=CFG["max_new"][base(key)])
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:16]


def prompt_hash(prompt):
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


def run_path(key):
    return RUN_DIR / f"{DATASET}__{MODEL_KEY}__{base(key)}__{PROMPT_IDS[key]}.jsonl"


def import_previous_runs():
    """Merge run files from earlier runs that were added with 'Add Input': a notebook's output, or a dataset made
    from an outputs zip. Searched at any folder depth; a file seen twice adds nothing."""
    root = os.environ.get("BENCH_INPUT_DIR", "/kaggle/input")
    found = [f for f in glob.glob(f"{root}/**/runs/{DATASET}__{MODEL_KEY}__*.jsonl", recursive=True)
             if any(f.endswith(f"__{pid}.jsonl") for pid in PROMPT_IDS.values())]   # only this notebook's prompts
    if not found:
        print(f"no earlier runs of {MODEL_KEY} among the inputs (a fresh start)")
    for src in sorted(set(found)):
        dst = RUN_DIR / Path(src).name
        have = set()
        if dst.exists():
            have = {json.loads(l)["key"] + json.loads(l)["status"] for l in open(dst, encoding="utf-8") if l.strip()}
        new = [l for l in open(src, encoding="utf-8")
               if l.strip() and json.loads(l)["key"] + json.loads(l)["status"] not in have]
        with open(dst, "a", encoding="utf-8") as f:
            f.writelines(new)
        print(f"resumed {len(new)} records from {src}")


def load_records(stage):
    recs = {}
    if run_path(stage).exists():
        for line in open(run_path(stage), encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                recs[r["key"]] = r                     # a later line (a retry) replaces an earlier one
    return recs


SESSION = {}


def run_stage(stage, jobs):
    """stage: "genre", "judge:context" or "judge:no_context". jobs: list of (key, question_id, item_id, prompt).
    Returns True if every job is done."""
    fp, max_new = setup_fingerprint(stage), CFG["max_new"][base(stage)]
    done = load_records(stage)
    other = {r["setup_hash"] for r in done.values()} - {fp}
    if other:
        raise Stop(f"{run_path(stage).name} has records from a different setup {other} (this setup: {fp}). "
                   "Never mix setups: use the same OLLAMA_VERSION/model/prompt, or start a new study folder.")
    todo = [j for j in jobs if j[0] not in done or done[j[0]]["status"] == "error"
            or done[j[0]].get("prompt_hash") != prompt_hash(j[3])]
    print(f"[{stage}] {len(jobs)} calls in this {RUN_MODE} run: {len(jobs) - len(todo)} already done, {len(todo)} to do")
    t_start, n_done, chunk = time.time(), 0, max(16, PAR * 8)
    with open(run_path(stage), "a", encoding="utf-8") as f:
        for s in range(0, len(todo), chunk):
            if time.time() - T0 > TIME_BUDGET_HOURS * 3600:
                print(f"[{stage}] TIME BUDGET reached: stopping cleanly. Resume in a new version (section 2, step 5).")
                SESSION[stage] = dict(calls=n_done, seconds=time.time() - t_start)
                return False
            batch = todo[s:s + chunk]
            outs = backend.generate_batch([j[3] for j in batch], max_new)
            for (key, qid, item_id, prompt), o in zip(batch, outs):
                capped = bool(CFG.get("think")) and o["done_reason"] == "length"
                usable = o["status"] == "ok" and not capped
                rec = dict(dataset=DATASET, stage=base(stage), condition=stage.split(":")[1] if ":" in stage else None,
                           key=key, question_id=qid, item_id=item_id,
                           model_key=MODEL_KEY, model_id=backend.model_id, model_version=backend.version_id,
                           backend=CFG["backend"], prompt_id=PROMPT_IDS[stage], prompt_sha=PROMPT_SHA[stage],
                           temperature=0, seed=SEED, think=CFG.get("think"), num_ctx=backend.num_ctx,
                           max_new_tokens=max_new, prompt_hash=prompt_hash(prompt), timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                           raw_output=o["raw"],
                           parsed=parse(base(stage), o["raw"]) if usable else "no_answer",
                           parsed_lenient=parse(base(stage), o["raw"], strict=False) if usable else "no_answer",
                           status="capped" if capped else o["status"], prompt_tokens=o["prompt_tokens"],
                           output_tokens=o["output_tokens"], thinking_chars=o["thinking_chars"],
                           done_reason=o["done_reason"], latency_s=o["latency_s"], error=o["error"],
                           setup_hash=fp, run_mode=RUN_MODE)
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            n_done += len(batch)
            errors = sum(o["status"] == "error" for o in outs)
            if errors > 0.2 * len(batch):
                raise Stop(f"[{stage}] {errors} of {len(batch)} calls failed, e.g. {outs[0]['error']}. "
                           "Check the server log or the API key.")
            if n_done % (chunk * 10) < chunk or n_done == len(todo):
                rate = n_done / max(1e-9, time.time() - t_start)
                print(f"[{stage}] {n_done}/{len(todo)} | {rate:.2f} calls/s | about "
                      f"{(len(todo) - n_done) / max(rate, 1e-9) / 60:.0f} min left")
    SESSION[stage] = dict(calls=n_done, seconds=time.time() - t_start)
    return True


import_previous_runs()
''')

# --------------------------------------------------------------------------------------------------------
md(r"""
## 9. Turn 1: genre (question + passage only)

One call per question. The genre answers both "how good is this LLM at guessing genres?" (Run 1) and "which
genre does this LLM think each question is?" (Run 2). The genre prompt always has the passage, so **one genre
guess serves both judging conditions**.
""")

code(r'''
COMPLETE = {}
GENRE_JOBS = [(qid, qid, None, genre_prompt(q["question"], q["context"]))
              for qid, q in QUESTIONS.items() if qid in RUN_QIDS]
if "genre" in STAGES:
    COMPLETE["genre"] = run_stage("genre", GENRE_JOBS)
''')

md(r"""
## 10. Turn 2: judge (once for each condition in `JUDGE_CONDITIONS`)

- `context`: passage + question + answer (`judge_v1`, the paper's prompt).
- `no_context`: question + answer only (`judge_noctx_v1`). The judge must use its own knowledge.

One call per answer and condition. The 5 answers of a question are sent together, so the shared prompt start is
reused. Each condition has its own log file, so you can add a condition later without redoing the other one.
""")

code(r'''
JUDGE_JOBS = {c: [(r["item_id"], r["question_id"], r["item_id"],
                   judge_prompt(c, QUESTIONS[r["question_id"]]["context"], QUESTIONS[r["question_id"]]["question"],
                                r["answer"])) for r in RUN_ITEMS] for c in JUDGE_CONDITIONS}
for c in JUDGE_CONDITIONS:
    if "judge" not in STAGES:
        continue
    if (time.time() - T0) < TIME_BUDGET_HOURS * 3600:
        COMPLETE[f"judge:{c}"] = run_stage(f"judge:{c}", JUDGE_JOBS[c])
    else:
        print(f"[judge:{c}] TIME BUDGET reached before this condition started. Resume in a new version.")
        COMPLETE[f"judge:{c}"] = False

# only records made for exactly these prompts count (a record for an older text of an item is stale)
GEN_HASH = {j[0]: prompt_hash(j[3]) for j in GENRE_JOBS}
GEN = {k: r for k, r in load_records("genre").items() if r.get("prompt_hash") == GEN_HASH.get(k)}
JUD = {}
for c in JUDGE_CONDITIONS:
    want = {j[0]: prompt_hash(j[3]) for j in JUDGE_JOBS[c]}
    JUD[c] = {k: r for k, r in load_records(f"judge:{c}").items() if r.get("prompt_hash") == want.get(k)}
LOGS = [("genre", GEN)] + [(f"judge:{c}", JUD[c]) for c in JUDGE_CONDITIONS]
status_counts = {s: dict(collections.Counter(r["status"] for r in recs.values())) for s, recs in LOGS}
print("record status:", status_counts)
for stage, recs in LOGS:
    if recs:
        bad = [r for r in recs.values() if r["parsed"] == "no_answer"]
        print(f"[{stage}] no_answer: {len(bad)} of {len(recs)} ({100 * len(bad) / len(recs):.1f}%)"
              + ("; examples of raw replies: " + " | ".join(repr(r["raw_output"][:60]) for r in bad[:5]) if bad else ""))
cut = sum(r["status"] in ("truncated", "too_long") for _, recs in LOGS for r in recs.values())
if isinstance(backend, OllamaBackend) and backend.log_has_truncation():
    print("WARNING: the Ollama server log says a prompt was truncated.")
    cut = max(cut, 1)
if cut:
    show_md(f"**WARNING: {cut} prompts were cut or too long.** They count as `no_answer` and are listed in the "
            "summary. For the paper, report them. If there are many, use a model with a longer context.")
PARTIAL = (not all(COMPLETE.values()) or any(qid not in GEN for qid in RUN_QIDS)
           or any(r["item_id"] not in JUD[c] for c in JUDGE_CONDITIONS for r in RUN_ITEMS))
if PARTIAL:
    show_md("## PARTIAL RESULTS: not every call is done yet. Resume in a new version (section 2, step 5).")
''')

# --------------------------------------------------------------------------------------------------------
md(r"""
## 11. Scoring tools

- **BHS per group of questions**, with a 95% range from 1,000 bootstrap re-samples of **questions**.
- **Genre quality:** accuracy, macro-F1 (the mean F1 over the genres present), and Cohen's kappa (agreement
  beyond chance; 1 = perfect, 0 = chance). Kappa gets a bootstrap range too. A genre reply of `no_answer`
  counts as wrong.
- **usable**: `yes` only if the cell has at least 50 questions (golden rule 5). Smaller cells are shown but
  never used for routing.
- **With vs without the passage:** `difference` = BHS without the passage − BHS with it, on the same questions,
  with a 95% range from a **paired** bootstrap (the same re-sampled questions for both). Lower BHS is better, so
  a positive difference means the judge does worse without the passage.
""")

code(r'''
OWN = {qid: GEN[qid]["parsed"] for qid in RUN_QIDS if qid in GEN}
HUMAN = {qid: QUESTIONS[qid]["genre_human"] for qid in RUN_QIDS}
ITEM = {r["item_id"]: r for r in RUN_ITEMS}


def question_counts(jud, field="parsed", no_answer_is_error=True, keep=lambda r: True):
    """jud: the judge records of one condition. Per question: [correct answers, false alarms, hallucinated
    answers, misses, no_answers]."""
    agg = {}
    for item_id, rec in jud.items():
        r = ITEM.get(item_id)
        if r is None or not keep(r):
            continue
        v = rec[field]
        a = agg.setdefault(r["question_id"], [0, 0, 0, 0, 0])
        if v == "no_answer":
            a[4] += 1
            if not no_answer_is_error:
                continue
        if r["label"] == "0":
            a[0] += 1
            a[1] += v != "no"
        else:
            a[2] += 1
            a[3] += v != "yes"
    return agg


def bhs(qids, agg):
    s = [sum(agg[q][i] for q in qids if q in agg) for i in range(5)]
    if not s[0] or not s[2]:
        return None
    return dict(BHS=50 * (s[1] / s[0] + s[3] / s[2]), trackA_err=100 * s[1] / s[0], trackB_err=100 * s[3] / s[2],
                n_items=s[0] + s[2], no_answer=s[4])


def bhs_range(qids, agg, seed=SEED):
    qids = [q for q in qids if q in agg]
    if not qids:
        return (None, None)
    rng, vals = random.Random(seed), []
    for _ in range(BOOT):
        v = bhs([qids[rng.randrange(len(qids))] for _ in qids], agg)
        if v:
            vals.append(v["BHS"])
    vals.sort()
    return (vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]) if vals else (None, None)


def diff_range(qids, agg_a, agg_b, seed=SEED):
    """Paired bootstrap of BHS(b) − BHS(a): the same re-sampled questions for both."""
    if not qids:
        return (None, None)
    rng, vals = random.Random(seed), []
    for _ in range(BOOT):
        sample = [qids[rng.randrange(len(qids))] for _ in qids]
        va, vb = bhs(sample, agg_a), bhs(sample, agg_b)
        if va and vb:
            vals.append(vb["BHS"] - va["BHS"])
    vals.sort()
    return (vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]) if vals else (None, None)


def genre_scores(pairs):
    n = len(pairs)
    acc = sum(h == p for h, p in pairs) / n
    f1s = []
    for g in GENRES:
        if not any(h == g for h, _ in pairs):
            continue
        tp = sum(h == g and p == g for h, p in pairs)
        fp = sum(h != g and p == g for h, p in pairs)
        fn = sum(h == g and p != g for h, p in pairs)
        f1s.append(2 * tp / (2 * tp + fp + fn) if tp else 0.0)
    ch, cp = collections.Counter(h for h, _ in pairs), collections.Counter(p for _, p in pairs)
    pe = sum(ch[g] * cp[g] for g in ch) / n ** 2
    kappa = (acc - pe) / (1 - pe) if pe < 1 else 1.0
    return acc, sum(f1s) / len(f1s), kappa


def kappa_range(pairs):
    rng = random.Random(SEED)
    ks = sorted(genre_scores([pairs[rng.randrange(len(pairs))] for _ in pairs])[2] for _ in range(BOOT))
    return ks[int(0.025 * BOOT)], ks[int(0.975 * BOOT) - 1]


def fmt(x, nd=2):
    return "–" if x is None else f"{x:.{nd}f}"


def md_table(rows, cols):
    return "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n" + "\n".join(
        "| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows)


def judge_table(groups, agg, extra=None, label="genre"):
    rows = []
    for name, qids in groups:
        v = bhs(qids, agg)
        lo, hi = bhs_range(qids, agg)
        row = {label: name}
        row.update(questions=len([q for q in qids if q in agg]),
                   BHS=fmt(v and v["BHS"]), range95=f"{fmt(lo)} to {fmt(hi)}",
                   trackA_err=fmt(v and v["trackA_err"]), trackB_err=fmt(v and v["trackB_err"]),
                   no_answer=v["no_answer"] if v else 0,
                   usable="yes" if len([q for q in qids if q in agg]) >= MIN_CELL else "no")
        if extra:
            row.update(extra(name, qids))
        rows.append(row)
    return rows


def compare_conditions(groups, label="genre"):
    """One row per group: BHS with and without the passage on the same questions, and the paired difference."""
    if len(JUDGE_CONDITIONS) < 2:
        return []
    a, b = AGG["context"], AGG["no_context"]
    rows = []
    for name, qids in groups:
        both = [q for q in qids if q in a and q in b]
        va, vb = bhs(both, a), bhs(both, b)
        lo, hi = diff_range(both, a, b)
        rows.append({label: name, "questions": len(both), "BHS_context": fmt(va and va["BHS"]),
                     "BHS_no_context": fmt(vb and vb["BHS"]),
                     "difference": fmt(vb["BHS"] - va["BHS"]) if va and vb else "–",
                     "range95": f"{fmt(lo)} to {fmt(hi)}", "usable": "yes" if len(both) >= MIN_CELL else "no"})
    return rows


AGG = {c: question_counts(JUD[c]) for c in JUDGE_CONDITIONS}
ALLQ = {c: sorted(q for q in RUN_QIDS if q in AGG[c]) for c in JUDGE_CONDITIONS}
# questions whose gold is a fact dated 2026 (it may be newer than a judge's training data)
DATED = {r["question_id"] for r in RUN_ITEMS
         if r["answer_as_of"] or r["time_sensitive"] == "yes" or r["audit_status"] == "UPD"}
SUMMARY = dict(model_key=MODEL_KEY, run_mode=RUN_MODE, partial=PARTIAL, judge_conditions=JUDGE_CONDITIONS,
               questions={c: len(ALLQ[c]) for c in JUDGE_CONDITIONS}, compare={})
TABLES = {}                                        # every table, saved as CSV in section 15
''')

# --------------------------------------------------------------------------------------------------------
md(r"""
## 12. Overall judge score (each condition)

The main number is **BHS with `no_answer` counted as an error**. Next to it are five checks:

- BHS on answered items only;
- the lenient parse (diagnostic only);
- the **span subset**: answers copied exactly from the passage. A simple "is it in the passage?" rule scores
  BHS 13.8 on the whole set but is useless here, so this checks whether the judge really reads the question;
- BHS without the weak golds (9 in v1.3);
- BHS **without the 2026-dated facts** (38 questions whose gold was checked or updated in October 2026). This matters
  most without the passage: a judge trained before 2026 cannot know these facts.

Then the miss rate per hallucination type (F factualness, C comprehension, S specificity, I inference), and at
the end both conditions side by side. Our hallucinated answers are new (not the paper's), so the paper's BHS
is only a rough guide.
""")

code(r'''
SUMMARY["overall"] = {}
for c in JUDGE_CONDITIONS:
    jud, agg, allq = JUD[c], AGG[c], ALLQ[c]
    overall = bhs(allq, agg)
    lo, hi = bhs_range(allq, agg)
    views = [("answered items only", bhs(allq, question_counts(jud, no_answer_is_error=False))),
             ("lenient parse (diagnostic)", bhs(allq, question_counts(jud, field="parsed_lenient"))),
             ("span subset (answer copied from the passage)",
              bhs(allq, question_counts(jud, keep=lambda r: r["answer"].strip() in r["context"]))),
             ("without weak golds", bhs(allq, question_counts(jud, keep=lambda r: r["weak_gold"] == "no"))),
             (f"without 2026-dated facts ({len(DATED)} questions out)",
              bhs([q for q in allq if q not in DATED], agg))]
    rows = [dict(view="all items (no_answer = error): MAIN", BHS=fmt(overall and overall["BHS"]),
                 range95=f"{fmt(lo)} to {fmt(hi)}", trackA_err=fmt(overall and overall["trackA_err"]),
                 trackB_err=fmt(overall and overall["trackB_err"]), no_answer=overall["no_answer"] if overall else 0)]
    for name, v in views:
        rows.append(dict(view=name, BHS=fmt(v and v["BHS"]), trackA_err=fmt(v and v["trackA_err"]),
                         trackB_err=fmt(v and v["trackB_err"]), no_answer=v["no_answer"] if v else 0))
    types = []
    for t, name in [("F", "factualness"), ("C", "comprehension"), ("S", "specificity"), ("I", "inference")]:
        recs = [jud[i] for i, r in ITEM.items() if r["answer_type"] == t and i in jud]
        if recs:
            types.append(dict(type=f"{t} ({name})", answers=len(recs),
                              miss_rate=fmt(100 * sum(x["parsed"] != "yes" for x in recs) / len(recs)),
                              no_answer=sum(x["parsed"] == "no_answer" for x in recs)))
    show_md(f"### Judge {COND_NAME[c]} (`{c}`)\n\n"
            + md_table(rows, ["view", "BHS", "range95", "trackA_err", "trackB_err", "no_answer"])
            + "\n\n**Miss rate per hallucination type**\n\n" + md_table(types, ["type", "answers", "miss_rate", "no_answer"]))
    SUMMARY["overall"][c] = dict(main=overall, range95=[lo, hi], views={n: v for n, v in views}, by_type=types)
    TABLES[f"overall__{c}"], TABLES[f"miss_rate_by_type__{c}"] = rows, types

cmp_overall = compare_conditions([("all questions", sorted(RUN_QIDS)),
                                  ("without 2026-dated facts", sorted(q for q in RUN_QIDS if q not in DATED))],
                                 label="view")
if cmp_overall:
    show_md("### With vs without the passage, side by side\n\n" + md_table(
        cmp_overall, ["view", "questions", "BHS_context", "BHS_no_context", "difference", "range95"]))
    SUMMARY["compare"]["overall"] = TABLES["context_vs_no_context__overall"] = cmp_overall
print("paper's QA BHS for this model, WITH the passage (other hallucinated answers; rough guide only):",
      PAPER_QA_BHS.get(MODEL_KEY, "not in the paper"))
print("rule baseline 'not an exact span of the passage' on the full set: see shortcut_report.md (v1.3: BHS 13.8)")
''')

# --------------------------------------------------------------------------------------------------------
md(r"""
## 13. Run 1: against our human genres

**Question 1: how well does this LLM guess the genre?** (shown once: the genre guess is the same for both
judging conditions)
- Against our final labels (LLM-drafted, human-verified; all questions in this run).
- Against the **200 blind human labels**. A person made these before seeing any LLM label, so this is the
  cleanest comparison (the plan's research question 2).

**Question 2: how well does it judge inside each human genre?** One table per judging condition. This is one
column of the judge × genre table (research question 1). The routing for methods D and E is built from these
columns across all models.
""")

code(r'''
pairs = [(HUMAN[q], OWN[q]) for q in sorted(OWN)]
blind_pairs = [(BLIND[q], OWN[q]) for q in sorted(OWN) if q in BLIND]
grows = []
for name, pp in [("final labels (human-verified)", pairs), ("blind human labels (200)", blind_pairs)]:
    if pp:
        acc, f1, k = genre_scores(pp)
        klo, khi = kappa_range(pp)
        grows.append(dict(compared_with=name, questions=len(pp), accuracy=fmt(100 * acc, 1), macro_F1=fmt(f1, 3),
                          kappa=fmt(k, 3), kappa_range95=f"{fmt(klo, 3)} to {fmt(khi, 3)}",
                          no_answer=sum(p == "no_answer" for _, p in pp)))
show_md("**Genre guessing**\n\n" + md_table(grows, ["compared_with", "questions", "accuracy", "macro_F1", "kappa",
                                                    "kappa_range95", "no_answer"]))

cols = list(GENRES) + ["no_answer"]
conf = [dict(human=h, **{c: sum(1 for hh, p in pairs if hh == h and p == c) for c in cols}) for h in GENRES]
show_md("**Confusion table** (rows = human genre, columns = the LLM's genre)\n\n" + md_table(conf, ["human"] + cols))
SUMMARY["run1"] = dict(genre_guessing=grows, confusion=conf, judge_by_human_genre={})
TABLES["genre_guessing"], TABLES["genre_confusion"] = grows, conf

human_groups = [(g, [q for q in sorted(RUN_QIDS) if HUMAN[q] == g]) for g in GENRES]
for c in JUDGE_CONDITIONS:
    run1 = judge_table(human_groups, AGG[c])
    show_md(f"**Judge score in each HUMAN genre, {COND_NAME[c]}** (`{c}`)\n\n" + md_table(
        run1, ["genre", "questions", "BHS", "range95", "trackA_err", "trackB_err", "no_answer", "usable"]))
    SUMMARY["run1"]["judge_by_human_genre"][c] = TABLES[f"judge_by_human_genre__{c}"] = run1
cmp1 = compare_conditions(human_groups)
if cmp1:
    show_md("**HUMAN genres: with vs without the passage**\n\n" + md_table(
        cmp1, ["genre", "questions", "BHS_context", "BHS_no_context", "difference", "range95", "usable"]))
    SUMMARY["compare"]["by_human_genre"] = TABLES["context_vs_no_context__by_human_genre"] = cmp1
''')

# --------------------------------------------------------------------------------------------------------
md(r"""
## 14. Run 2: in the LLM's own genres (the {LLM, genre} pairs)

Here we take this LLM's genre guess as true. Each question goes into the genre **this LLM named**, right or
wrong, and the table scores the judge inside each of its own genres. Each row is one {this LLM, genre} pair:
the own-genre table that **method F** routes on (plan section 2.5). The column `agrees_with_human` shows how
many of those questions we also put in that genre. One table per judging condition.

**Known risk (report it):** each LLM's own "History" is a different set of questions. An LLM that calls only
easy questions "History" gets a flattering score there. Only the test on Dataset 2 can show whether that
helps or hurts routing.

**Mechanism check (research question 5):** the last table of each condition compares judging on questions
where this LLM's genre matches ours with judging on questions where it does not.
""")

code(r'''
own_groups = [(g, [q for q in sorted(RUN_QIDS) if OWN.get(q) == g]) for g in list(GENRES) + ["no_answer"]]
mech_groups = [("own genre = human genre", [q for q in sorted(RUN_QIDS) if OWN.get(q) == HUMAN[q]]),
               ("own genre ≠ human genre", [q for q in sorted(RUN_QIDS) if OWN.get(q) != HUMAN[q]])]
SUMMARY["run2"] = {}
for c in JUDGE_CONDITIONS:
    run2 = judge_table(own_groups, AGG[c], extra=lambda g, qs: dict(
        agrees_with_human=f"{sum(HUMAN[q] == g for q in qs)}/{len(qs)}" if qs else "–"))
    show_md(f"**Judge score in each genre the LLM named itself, {COND_NAME[c]}** (`{c}`)\n\n" + md_table(
        run2, ["genre", "questions", "agrees_with_human", "BHS", "range95", "trackA_err", "trackB_err", "no_answer",
               "usable"]))
    mech = judge_table(mech_groups, AGG[c], label="group")
    show_md(f"**Mechanism check, {COND_NAME[c]}** (exploratory)\n\n" + md_table(
        mech, ["group", "questions", "BHS", "range95", "trackA_err", "trackB_err", "no_answer"]))
    SUMMARY["run2"][c] = dict(judge_by_own_genre=run2, mechanism=mech)
    TABLES[f"judge_by_own_genre__{c}"], TABLES[f"mechanism__{c}"] = run2, mech
cmp2 = compare_conditions(own_groups)
if cmp2:
    show_md("**The LLM's own genres: with vs without the passage**\n\n" + md_table(
        cmp2, ["genre", "questions", "BHS_context", "BHS_no_context", "difference", "range95", "usable"]))
    SUMMARY["compare"]["by_own_genre"] = TABLES["context_vs_no_context__by_own_genre"] = cmp2
''')

# --------------------------------------------------------------------------------------------------------
md(r"""
## 15. Cost, setup record and saving

This section reports calls, tokens and time for each turn and condition (golden rule 9), the dollar cost for
the API model, and, after a pilot, the **estimated time of the full run**. It saves everything to
`/kaggle/working`:

- `runs/…jsonl`: the raw log of every call, one file per turn and condition (the most important output;
  never edit it);
- `results/<model>/<mode>/`: `summary.json`, every table as CSV (names end in `__context` or `__no_context`),
  and `manifest.json` (model version, Ollama version, GPU, prompt fingerprints, dataset checksums, settings);
- `<model>__<mode>__outputs.zip`: all of the above in one file, to download.
""")

code(r'''
cost = {}
for stage, recs in LOGS:
    rs = list(recs.values())
    pt = sum(r["prompt_tokens"] or 0 for r in rs)
    ot = sum(r["output_tokens"] or 0 for r in rs)
    cost[stage] = dict(calls=len(rs), prompt_tokens=pt, output_tokens=ot,
                       sum_latency_h=round(sum(r["latency_s"] or 0 for r in rs) / 3600, 3),
                       this_session=SESSION.get(stage, {}))
    if backend.model_id in PRICE_PER_M:
        pin, pout = PRICE_PER_M[backend.model_id]
        cost[stage]["usd_estimate"] = round(pt / 1e6 * pin + ot / 1e6 * pout, 2)
show_md("**Cost so far**\n\n" + md_table([dict(turn=s, **{k: v for k, v in c.items() if k != "this_session"})
                                          for s, c in cost.items()],
                                         ["turn", "calls", "prompt_tokens", "output_tokens", "sum_latency_h",
                                          "usd_estimate"]))

est = {}
for stage, recs in LOGS:
    sess = SESSION.get(stage, {})
    if sess.get("calls"):
        per_call = sess["seconds"] / sess["calls"]
    elif recs:
        per_call = statistics.mean(r["latency_s"] or 0 for r in recs.values()) / PAR
    else:
        continue
    est[stage] = round(per_call * (len(QUESTIONS) if stage == "genre" else len(ITEMS)) / 3600, 2)
if est:
    total = sum(est.values())
    show_md(f"**Estimated full-run time** (all {len(QUESTIONS)} questions, {len(ITEMS)} answers per condition): "
            + " + ".join(f"{s} {h} h" for s, h in est.items()) + f" = **{total:.1f} h** of GPU time. "
            + ("It fits one session." if total < TIME_BUDGET_HOURS else
               f"It needs about {math.ceil(total / TIME_BUDGET_HOURS)} sessions (the resume handles this)."))
SUMMARY["cost"], SUMMARY["full_run_estimate_h"] = cost, est


def gpu_name():
    try:
        return subprocess.run("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader", shell=True,
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        return "?"


manifest = dict(model_key=MODEL_KEY, config={k: v for k, v in CFG.items()}, model_id=backend.model_id,
                model_version=backend.version_id, num_ctx=backend.num_ctx, parallel=PAR, run_mode=RUN_MODE,
                stages=STAGES, judge_conditions=JUDGE_CONDITIONS, prompt_ids=PROMPT_IDS, prompt_sha=PROMPT_SHA,
                setup_hash={s: setup_fingerprint(s) for s, _ in LOGS}, seed=SEED, temperature=0,
                dataset_dir=str(DATA_DIR), dataset_checksums={k: v for k, v in sums.items()},
                pilot_questions=sorted(PILOT_QIDS), gpu=gpu_name(), python=platform.python_version(),
                started=datetime.datetime.fromtimestamp(T0, datetime.timezone.utc).isoformat(),
                finished=datetime.datetime.now(datetime.timezone.utc).isoformat(), partial=PARTIAL, status_counts=status_counts)

out = RES_DIR / MODEL_KEY / RUN_MODE
out.mkdir(parents=True, exist_ok=True)
(out / "summary.json").write_text(json.dumps(SUMMARY, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
(out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
for name, rows in TABLES.items():
    if rows:
        with open(out / f"{name}.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

zpath = OUT_DIR / f"{MODEL_KEY}__{RUN_MODE}__outputs.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    own = [RUN_DIR / run_path(k).name for k in ["genre"] + [f"judge:{c}" for c in JUDGE_CONDITIONS]]
    for p in [q for q in own if q.exists()] + sorted(out.glob("*")):
        z.write(p, p.relative_to(OUT_DIR))
    for p in OUT_DIR.glob(f"ollama_server__{MODEL_KEY}.log"):
        z.write(p, p.relative_to(OUT_DIR))
print("saved:", out)
print("download:", zpath)
show_md(("## PARTIAL: resume before using these numbers." if PARTIAL else "## Done.")
        + f"\n\nModel `{MODEL_KEY}` ({backend.version_id}), mode `{RUN_MODE}`, conditions {JUDGE_CONDITIONS}.")
''')

# --------------------------------------------------------------------------------------------------------
md(r"""
## 16. After every model is done (not in this notebook)

1. Put every model's `runs/` and `results/` into the project (`runs/` is never overwritten).
2. A separate **routing notebook** reads only the BenHalluEval runs. For each judging condition
   (with and without the passage) it builds:
   - the judge × genre table, the best genre guesser and the own-genre tables;
   - methods A–K offline, and the 6 pre-specified comparisons (E vs A, F vs A, F vs C in each condition,
     Holm-corrected);
   - the 5-fold checkpoint (plan section 2.4).

   It then **locks** every choice (plan Step 2).
3. Only after the lock: run this same notebook design on Dataset 2, with the same `OLLAMA_VERSION`, prompts,
   settings and both judging conditions.
4. Before any public release: confirm BenHalluEval's licence (see the dataset README).
""")


def write_notebook(cells, out):
    nb = {"cells": [], "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "kaggle": {"accelerator": "nvidiaTeslaT4", "isInternetEnabled": True, "isGpuEnabled": True,
                   "language": "python", "sourceType": "notebook"}},
        "nbformat": 4, "nbformat_minor": 5}
    for n, (kind, text) in enumerate(cells):
        lines = text.split("\n")
        source = [line + "\n" for line in lines[:-1]] + [lines[-1]]
        cell = {"cell_type": kind, "id": f"cell-{n:02d}", "metadata": {}, "source": source}
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        nb["cells"].append(cell)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(cells)} cells)")


def main():
    write_notebook(CELLS, Path(sys.argv[1]) / "notebooks" / "benchmark_one_llm.ipynb")


if __name__ == "__main__":
    main()
