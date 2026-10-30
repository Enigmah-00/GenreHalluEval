"""Build notebooks/benchmark_bangla_prompts.ipynb: the same benchmark notebook, but with the three prompts in Bangla
(prompts/genre_bn_v1.txt, judge_bn_v1.txt, judge_noctx_bn_v1.txt) and replies in Bangla (হ্যাঁ / না; ইতিহাস,
শিল্পকলা, বিজ্ঞান, ভূগোল, ধর্ম, অন্যান্য).

An exploratory side experiment (decided 2026-10-18, after the English runs): do the Bangla-centric judges
(tigerllm-9b, banglallama-13b, titullm-3b-instruct) work better when the prompt is in Bangla? It never feeds the
main analysis. Its files cannot mix with the English runs: run files are named by prompt id (`…__judge_bn_v1.jsonl`),
tables go to results/bangla_prompts/<model>/<mode>/, and the zip is <model>__bnprompt__<mode>__outputs.zip.

Usage: python3 -I src/bench/make_notebook_bangla.py <project_root>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_notebook as base                                  # noqa: E402  (builds the English cells on import)

cells = [list(c) for c in base.CELLS]


def patch(old, new, count=1):
    hits = [i for i, (_, text) in enumerate(cells) if old in text]
    assert len(hits) == 1 and cells[hits[0]][1].count(old) == count, (old[:70], hits)
    cells[hits[0]][1] = cells[hits[0]][1].replace(old, new)


# ---- title ----
patch("# Benchmark one LLM on BenHalluEval-QA v1.3: genre guessing and hallucination judging",
      """# Benchmark one LLM with BANGLA prompts (side experiment)

> **This is the Bangla-prompt version of the benchmark notebook.** Everything works the same way, except:
> - the genre prompt and both judge prompts are in Bangla (`genre_bn_v1`, `judge_bn_v1`, `judge_noctx_bn_v1`);
> - the LLM must reply হ্যাঁ / না (judge) or ইতিহাস / শিল্পকলা / বিজ্ঞান / ভূগোল / ধর্ম / অন্যান্য (genre);
>   English yes/no and English genre codes are also accepted, and a leading "উত্তর:" or "ধরন:" label is ignored;
> - up to 16 new tokens per reply (Bangla words need more tokens than English ones);
> - outputs go to `results/bangla_prompts/…` and `<model>__bnprompt__<mode>__outputs.zip`, never mixed with the
>   English runs.
>
> **Why:** with English prompts, the Bangla-centric judges gave no usable verdicts (they answered in Bangla, answered
> the question itself, or repeated the prompt). This experiment tests whether the prompt language is the cause.
> It is exploratory (decided 2026-10-18, after the English results) and never feeds the main analysis.
> **Intended models:** `tigerllm-9b`, `banglallama-13b`, `titullm-3b-instruct`; optional reference: `qwen3.5-27b`.

# Benchmark one LLM on BenHalluEval-QA v1.3: genre guessing and hallucination judging""")

# ---- settings ----
patch('''MODEL_KEY = "llama3.1-8b"   # which LLM to test: a key from the table in section 4''',
      '''MODEL_KEY = "tigerllm-9b"   # Bangla-prompt run: tigerllm-9b, banglallama-13b or titullm-3b-instruct (reference: qwen3.5-27b)''')

# ---- prompts and checksums ----
patch('''PROMPT_IDS = {"genre": "genre_v1", "judge:context": "judge_v1", "judge:no_context": "judge_noctx_v1"}''',
      '''PROMPT_IDS = {"genre": "genre_bn_v1", "judge:context": "judge_bn_v1", "judge:no_context": "judge_noctx_bn_v1"}''')
patch('''for name in ["items.csv", "genre_blind200.csv", "prompts/judge_v1.txt", "prompts/judge_noctx_v1.txt",
             "prompts/genre_v1.txt"]:''',
      '''for name in ["items.csv", "genre_blind200.csv", "prompts/judge_bn_v1.txt", "prompts/judge_noctx_bn_v1.txt",
             "prompts/genre_bn_v1.txt"]:''')

# ---- longer replies for Bangla words ----
patch('''DEFAULTS = dict(think=None, max_new={"genre": 8, "judge": 8},''',
      '''DEFAULTS = dict(think=None, max_new={"genre": 16, "judge": 16},''')

# ---- Bangla-aware strict parse (fixed before any Bangla-prompt result) ----
patch('''EDGE = " \\t\\r\\n\\"'`*.,!:;"''', '''EDGE = " \\t\\r\\n\\"'`*.,!:;।"''')
patch('''def parse(stage, raw, strict=True):
    text = strip_think(raw)
    if strict:''',
      '''BN_YES, BN_NO = ("হ্যাঁ", "হ্যা"), ("না",)
BN_GENRE = {"ইতিহাস": "HISTORY", "শিল্পকলা": "ARTS", "বিজ্ঞান": "SCIENCE", "ভূগোল": "GEOGRAPHY",
            "ধর্ম": "RELIGION", "অন্যান্য": "OTHER"}
LABEL = re.compile(r"^(উত্তর|ধরন|answer|genre)\\s*[:ঃ]\\s*", re.I)


def parse(stage, raw, strict=True):
    """Bangla version. Strict: the whole reply (after edge punctuation and an optional 'উত্তর:' / 'ধরন:' label) must be
    হ্যাঁ/না or yes/no (judge), or one Bangla genre word or English code (genre). Lenient: the first such word."""
    import unicodedata
    text = unicodedata.normalize("NFC", strip_think(raw))
    if strict:
        t = LABEL.sub("", text.strip(EDGE)).strip(EDGE)
        if stage == "judge":
            return "yes" if t in BN_YES or t.lower() == "yes" else "no" if t in BN_NO or t.lower() == "no" else "no_answer"
        return BN_GENRE.get(t) or (t.upper() if t.upper() in GENRES else "no_answer")
    for w in re.findall(r"[\\u0980-\\u09FF]+|[A-Za-z]+", text):
        if stage == "judge":
            if w in BN_YES or w.lower() == "yes":
                return "yes"
            if w in BN_NO or w.lower() == "no":
                return "no"
        elif w in BN_GENRE or w.upper() in GENRES:
            return BN_GENRE.get(w) or w.upper()
    return "no_answer"


def parse_english(stage, raw, strict=True):
    text = strip_think(raw)
    if strict:''')

# ---- the fake model for local tests speaks Bangla ----
patch('''        if prompt.rstrip().endswith("Genre:"):
            raw = ["HISTORY", "ARTS", "SCIENCE", "GEOGRAPHY", "RELIGION", "OTHER", "History.", "I think ARTS"][h % 8]
        elif "Context: " in prompt:
            ctx = prompt.split("Context: ", 1)[1].split("\\nQuestion: ", 1)[0]
            ans = prompt.split("Model answer: ", 1)[1].rsplit("\\nAnswer now:", 1)[0]
            raw = "no" if ans.strip() in ctx else "yes"
            raw = {0: "Yes.", 1: "The answer is no"}.get(h % 25, raw)
        else:                                       # no passage: the fake model guesses
            raw = {0: "Yes.", 1: "I am not sure"}.get(h % 25, ["yes", "no"][h % 2])''',
      '''        if prompt.rstrip().endswith("ধরন:"):
            raw = ["ইতিহাস", "শিল্পকলা", "বিজ্ঞান", "ভূগোল", "ধর্ম", "অন্যান্য", "ধরন: ইতিহাস।", "আমার মনে হয় শিল্পকলা"][h % 8]
        elif "প্রসঙ্গ: " in prompt:
            ctx = prompt.split("প্রসঙ্গ: ", 1)[1].split("\\nপ্রশ্ন: ", 1)[0]
            ans = prompt.split("মডেলের উত্তর: ", 1)[1].rsplit("\\nএখন উত্তর দিন:", 1)[0]
            raw = "না" if ans.strip() in ctx else "হ্যাঁ"
            raw = {0: "উত্তর: হ্যাঁ", 1: "উত্তরটি সঠিক নয়"}.get(h % 25, raw)
        else:                                       # no passage: the fake model guesses
            raw = {0: "হ্যাঁ।", 1: "আমি নিশ্চিত নই"}.get(h % 25, ["হ্যাঁ", "না"][h % 2])''')

# ---- separate output folder and zip name ----
patch('''out = RES_DIR / MODEL_KEY / RUN_MODE''', '''out = RES_DIR / "bangla_prompts" / MODEL_KEY / RUN_MODE''')
patch('''zpath = OUT_DIR / f"{MODEL_KEY}__{RUN_MODE}__outputs.zip"''',
      '''zpath = OUT_DIR / f"{MODEL_KEY}__bnprompt__{RUN_MODE}__outputs.zip"''')

base.write_notebook([tuple(c) for c in cells], Path(sys.argv[1]) / "notebooks" / "benchmark_bangla_prompts.ipynb")
