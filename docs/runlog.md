# Run log

This file records what has run, with which setup, and what is still to run. Each Kaggle run gets one entry; new
entries go at the bottom. Raw outputs are in `runs/` (never edit them) and the tables are in `results/`.

## How to add a run

1. Download `<model>__<mode>__outputs.zip` from the notebook version's **Output** tab.
2. Run `python3 -I src/bench/import_run.py "$PWD" <path to the zip>`. It does four things:
   - copies the files into `runs/` and `results/`;
   - keeps the original zip in `runs/kaggle_outputs/`;
   - checks the run (dataset checksums, partial, statuses, setups, truncation);
   - rebuilds `results/overview.md` (all models side by side) and `release/kaggle-runs/`.
3. Add an entry below and update the progress table.
4. Upload `release/kaggle-runs/benhallueval-qa-judge-runs.zip` as a **New Version** of the private Kaggle dataset
   "BenHalluEval-QA judge runs".

## The fixed setup (the same for every model)

| | Value |
|---|---|
| Dataset | Kaggle `mahdihasanqurishi/benhallueval-qa-bangla` = package v1.3 (920 questions, 4,600 answers). `items.csv` sha256 starts `a6e4e413fd95`; `genre_blind200.csv` `8b326fc8b452` |
| Prompts (sha256, first 12) | `genre_v1` 3bb6f869c352; `judge_v1` (context) 0e4241e4d57f; `judge_noctx_v1` (no context) 2fe589f38e9e |
| Software | Ollama **0.40.6**, pinned in the notebook from 2026-10-18 (`OLLAMA_VERSION`). R1 ran on 0.40.5; R2 and R3 ran on 0.40.6 without the pin (the Kaggle copy still had `""`, which installs the latest). The pin moved to 0.40.6 so only R1 needs a check |
| Hardware and settings | Kaggle GPU T4 × 2; temperature 0; seed 2026; strict parsing |
| Analysis plan | The 6 pre-specified comparisons (`refined-plan.md` 2.2) were saved 2026-10-17 11:20 UTC, **before** the first judge result (run started 14:11 UTC) |

## Progress (BenHalluEval)

| # | Model key | Pool | Genre (920) | Judge, context (4,600) | Judge, no context (4,600) | Entry |
|---|---|---|---|---|---|---|
| 1 | `llama3.1-8b` | open, paper | done | done | done | R1 (Ollama 0.40.5; check pending) |
| 2 | `mistral-nemo-12b` | open, paper | done | done | done | R2 |
| 3 | `gemma2-27b` | open, paper | done | done | done | R3 |
| 4 | `qwen2.5-32b` | open, paper | done | done | done | R6 |
| 5 | `deepseek-r1-14b` | open, paper | done | done | done | R11 (2 sessions) |
| 6 | `tigerllm-9b` | open, paper | done | done | done | R5 (after the arch-check fix) |
| 7 | `titullm-3b` | open, paper | done (no usable reply) | done (no usable reply) | done (no usable reply) | R4 |
| 8 | `banglallama-13b` | open, paper | done (no usable reply) | done (no usable reply) | done (no usable reply) | R9 (third try, after both fixes) |
| 9 | `gpt-4.1-mini` | closed, paper (secondary pool; paid) | – | – | – | |
| 10 | `gemma4-31b` | open, new | done | done | done | R12 |
| 11 | `qwen3.5-27b` | open, new | done | done | done | R8 |
| 12 | `gpt-oss-20b` | open, new (optional) | done | done | done | R7 |
| 13 | `titullm-3b-instruct` | open, new (added 2026-10-18, before any result) | done (no usable reply) | done (no usable reply) | done (no usable reply) | R10 |

Dataset 2: nothing yet (it is built in Step 3 and touched only after the lock).
Cross-model tables: `results/overview.md` (and `results/overview_*.csv`).

**Kaggle datasets (checked 2026-10-17, and again 2026-10-18, logged out: both still public):**
- `mahdihasanqurishi/benhallueval-qa-judge-runs` (version 1) has the llama3.1-8b run. It is the same files we
  imported: `judge_v1.jsonl` is 4.05 MB in both. It also holds the outputs folder a second time and the 373 MB
  Ollama log (763 MB in all).
- **It is PUBLIC, with an MIT licence. So is `benhallueval-qa-bangla`,** and its Code tab shows 1 notebook.
- The plan was to keep both private until BenHalluEval's licence is confirmed. Set both to Private, or confirm
  the licence first.

---

## R1: `llama3.1-8b`, full run, 2026-10-17

**Run facts**

| | |
|---|---|
| Notebook | https://www.kaggle.com/code/mahdihasanqurishi/the-one-run-decides-all (the version that made this zip) |
| Model | `llama3.1:8b`, Q4_K_M, Ollama digest `46e0c10c039e…`; context window 11,264 tokens; 4 requests at once |
| Setup hashes | genre `1ca315634b97ecb6`; judge context `f10c16459b359b01`; judge no context `3ab6de3cf00b75c8` |
| Session | 14:11–15:41 UTC (1 h 30 min) on T4 × 2. Genre 17 min, judge with context 58 min, judge without context 10 min |
| Calls | 920 + 4,600 + 4,600 = 10,120. All `ok`, 0 `no_answer`, 0 truncated (10,126 server requests checked). Longest prompt 9,621 tokens |
| Tokens | in: genre 1.53 M, context 4.26 M, no context 0.78 M; out: 21,333 |
| Cost | $0 (Kaggle GPU) |
| Files | `runs/benhallueval__llama3.1-8b__*.jsonl`; `results/llama3.1-8b/full/`; `runs/kaggle_outputs/llama3.1-8b__full__outputs.zip` (includes the 373 MB Ollama log) |

**Results** (BHS: lower is better, 50 = chance; 95% ranges come from re-sampling questions)

| | With passage | Without passage |
|---|---|---|
| BHS (main) | **36.7** (35.4–38.0) | **46.0** (44.7–47.3) |
| Correct answers flagged (Track A error) | 13.0% | 33.6% |
| Hallucinations missed (Track B error) | 60.4% | 58.4% |
| BHS on the span subset (answers copied from the passage) | 48.0 | 47.9 |
| BHS without the 38 questions dated 2026 | 36.7 | 46.1 |
| Miss rate F / C / S / I | 55 / 81 / 41 / 64% | 68 / 62 / 41 / 63% |

- The passage helps by 9.3 BHS points (7.5–11.1).
- The two conditions give the same verdict on 58% of answers.
- **Paper (same model, its own hallucinations):** Track A 13.8%, Track B 81.6%, BHS 47.7.
  - Our Track A matches the paper closely.
  - Our hallucinations are missed less often, so the BHS numbers are not directly comparable.
- **Span rule:** BHS 13.8. The judge is far worse than this rule. On answers copied from the passage it is at
  chance level: it misses 83% of hallucinated spans.

**Genre guessing:**
- Against our final labels: accuracy 73.4%, macro-F1 0.633, kappa 0.634 (0.592–0.668).
- Against the blind 200 (189 in the set): accuracy 71.4%, kappa 0.603.
- It names HISTORY for 513 questions; our labels have 290. Many Arts (73), Science (53), Religion (50) and
  Geography (41) questions become HISTORY.
- When it names another genre, it is almost always right:
  - ARTS 204 of 214;
  - SCIENCE 74 of 76;
  - GEOGRAPHY 69 of 70;
  - RELIGION 39 of 40.
- One possible reason: HISTORY is the first option in the prompt. This is a hypothesis; the prompt stays frozen.

**Judge score in each of our genres** (Run 1):

| Genre | With passage | Without passage |
|---|---|---|
| History | 35.6 (33.3–38.0) | 45.1 (43.0–47.4) |
| Arts | 37.7 (35.7–39.8) | 48.8 (46.6–51.1) |
| Science | 39.1 (34.9–42.9) | 44.9 (41.3–48.5) |
| Geography | 34.4 (31.3–37.6) | **40.3** (37.3–43.6) |
| Religion | 36.8 (32.4–40.8) | 47.4 (43.3–51.3) |

- With the passage, the ranges overlap, so there is no clear genre effect.
- Without the passage, Geography is clearly better than Arts.
- This is exploratory and comes from one model.

**Own genres** (Run 2):
- Usable cells (50 questions or more): HISTORY 513, ARTS 214, SCIENCE 76, GEOGRAPHY 70.
- RELIGION (40) and OTHER (7) are too small to route on.

**Mechanism check:** the judge is not worse when its genre is wrong.
- With passage: 37.5 when the genre matches ours, 34.4 when it does not.
- Without passage: 46.6 vs 44.3.

This is the opposite of the expected direction, but small and exploratory.

**Deviations (report them):**
1. There was no pilot before the full run. The rules ask for a 200-item pilot. No harm is visible: 0
   `no_answer`, 0 truncation.
2. `docs/expectations.md` and `docs/preregistration.md` were not written before this first judge result. The
   pre-specified comparisons were saved earlier (see the fixed setup). Write both before the next model, and say
   that one model's results were already seen.

---

## R2: `mistral-nemo-12b`, full run, 2026-10-17

**Run facts**

| | |
|---|---|
| Notebook | https://www.kaggle.com/code/mahdihasanqurishi/the-one-run-decides-all?scriptVersionId=359427729 |
| Model | `mistral-nemo:12b`, Q4_0, Ollama digest `e7e06d107c6c…`; context window 7,168 tokens; 4 requests at once |
| Setup hashes | genre `34fa0c0f21b189a0`; judge context `4210f75b17395ce9`; judge no context `6e943cabb75ae1d4` |
| Session | 16:43–17:40 UTC (57 min) on T4 × 2. Genre 11 min, judge with context 34 min, judge without context 7 min |
| Calls | 10,120. All `ok`, 0 `no_answer`, 0 truncated (10,126 server requests checked). Longest prompt 5,517 tokens |
| Tokens | in: genre 1.18 M, context 2.33 M, no context 0.57 M; out: 22,122 |
| Cost | $0 (Kaggle GPU) |
| Files | `runs/benhallueval__mistral-nemo-12b__*.jsonl`; `results/mistral-nemo-12b/full/`; `runs/kaggle_outputs/mistral-nemo-12b__full__outputs.zip` |

**Results**

| | With passage | Without passage |
|---|---|---|
| BHS (main) | **49.7** (48.0–51.3) | **50.8** (49.8–51.7) |
| Correct answers flagged (Track A error) | 42.9% | 84.5% |
| Hallucinations missed (Track B error) | 56.4% | 17.0% |
| Says "yes" (hallucinated) | 43% of answers | 83% of answers |
| BHS on the span subset | 59.0 | 53.0 |
| BHS without the 38 questions dated 2026 | 50.3 | 50.8 |
| Miss rate F / C / S / I | 61 / 71 / 33 / 60% | 17 / 22 / 11 / 18% |

- **Chance level in both conditions.**
  - The passage does not help: the gain is 1.1 points, range −0.8 to 3.0.
  - Without the passage it calls almost everything hallucinated.
  - The paper found the same bias for this model: it flags 87.7% of correct answers there, and its paper BHS is 53.8.
- **Compared with llama3.1-8b** (paired, the same questions):
  - worse by 12.9 points with the passage (10.9–14.9);
  - worse by 4.8 points without it (3.0–6.4);
  - same verdict on 58% of answers with the passage and 46% without.
- **Genre guessing:**
  - Against our labels: accuracy 69.8%, macro-F1 0.614, kappa 0.584 (0.544–0.619).
  - Against the blind 200: kappa 0.596.
  - Against llama: 3.6 points less accurate (paired range −6.2 to −1.1), so clearly worse. On the blind 200 the
    two are about equal (0.596 vs 0.603).
  - It also over-uses HISTORY (500 questions). It names RELIGION for only 25 questions; 51 of our Religion
    questions go to History and 19 to Arts.
- **Judge score in each of our genres, with the passage:** Geography 42.8 (38.1–47.4) is its best; the others
  are 48.7–52.1. Without the passage, every genre is 47–52.
- **Own genres:**
  - Usable cells: HISTORY 500, ARTS 233, SCIENCE 72, GEOGRAPHY 86.
  - Too small: RELIGION 25 and OTHER 4.
- **Mechanism check:** no difference (50.1 vs 48.6 with the passage, 50.9 vs 50.5 without).

**Deviations (report them):**
1. **Ollama 0.40.6, while the pin was 0.40.5.** The Kaggle copy of the notebook still had `OLLAMA_VERSION = ""`.
   R3 also used 0.40.6, so on 2026-10-18 the pin moved to 0.40.6. This run now matches the pin; R1 is the one
   to check.
2. No pilot before the full run, the same as R1.

---

## R3: `gemma2-27b`, full run, 2026-10-17

**Run facts**

| | |
|---|---|
| Notebook | `the-one-run-decides-all` (version not given; it ran at the same time as R2, so probably another session or account) |
| Model | `gemma2:27b`, Q4_0, Ollama digest `53261bc9c192…`; context window 7,168 tokens; 2 requests at once |
| Setup hashes | genre `8d5dfed51bb7c5ad`; judge context `31b109adc5478894`; judge no context `0475135a00738fcf` |
| Session | 16:44–20:30 UTC (3 h 46 min) on T4 × 2. Genre 40 min, judge with context 2 h 11 min, judge without context 47 min |
| Calls | 10,120. All `ok`, 0 `no_answer`, 0 truncated (10,126 server requests checked). Longest prompt 5,397 tokens |
| Tokens | in: genre 1.11 M, context 2.24 M, no context 0.59 M; out: 23,754 |
| Software | Ollama 0.40.6, without the pin (it matches the pin set on 2026-10-18) |
| Cost | $0 (Kaggle GPU) |
| Files | `runs/benhallueval__gemma2-27b__*.jsonl`; `results/gemma2-27b/full/`; `runs/kaggle_outputs/gemma2-27b__full__outputs.zip` |

**Results**

| | With passage | Without passage |
|---|---|---|
| BHS (main) | **6.1** (5.5–6.8) | **38.2** (37.0–39.5) |
| Correct answers flagged (Track A error) | 1.6% | 16.5% |
| Hallucinations missed (Track B error) | 10.6% | 59.8% |
| Says "yes" (hallucinated); the true rate is 80% | 72% of answers | 35% of answers |
| BHS on the span subset | 7.5 | 30.1 |
| BHS without the 38 questions dated 2026 | 6.1 | 38.1 |
| Miss rate F / C / S / I | 4 / 12 / 16 / 11% | 75 / 40 / 61 / 64% |

- **With the passage it is excellent.**
  - It beats the span rule (13.8) and the paper's best judge (GPT-4.1 mini, 15.6).
  - It also works on the span subset (7.5), so it really checks whether a passage span answers the question.
  - The passage helps by 32.1 points (30.6–33.4).
- **Big gap from the paper.** On the paper's own hallucinations this model scored Track A 16.4%, Track B 78.5%,
  BHS 47.5. So either our hallucinations are much easier to check against the passage than the paper's, or the
  prompt language matters (the paper's QA prompts were in Bengali). This is a threat to validity, so report it.
  Dataset 2 (real model answers) is the test.
- **Best judge so far in both conditions** (paired):
  - llama3.1-8b is worse by 30.6 with the passage (29.3–31.9) and 7.8 without (6.2–9.5);
  - mistral-nemo-12b is worse by 43.6 and 12.6.
  - It is the best in every one of our genres, in both conditions.
- **Genre guessing, best so far:**
  - Against our labels: accuracy 81.5%, macro-F1 0.771, kappa 0.752 (0.719–0.783).
  - Against the blind 200: kappa 0.707.
  - 8.2 points more accurate than llama (5.8–11.0).
  - It over-uses HISTORY less (439 questions).
  - It names Religion for 75 questions (74 correct), so every main genre cell is usable.
- **Our genres:**
  - With the passage, all genres are 5.5–7.5, so there is no genre effect.
  - Without the passage: Science 34.0 and Geography 34.4 are best, Arts 42.0 is worst. That is the same pattern
    as llama (Arts worst without the passage).
- **Own genres:** HISTORY 439, ARTS 205, SCIENCE 113, GEOGRAPHY 82, RELIGION 75 are all usable; OTHER 6 is too
  small.
- **Mechanism check:** no support. With the passage it scores 6.4 when its genre matches ours and 5.0 when it
  does not; without the passage, 38.4 vs 37.4.
- **Our genres vs its own genres** (overview section 6): almost the same in every usable genre. The differences
  are −0.3 to +0.8 with the passage and −1.1 to +0.6 without. Only Science with the passage is clearly different:
  it is slightly worse in its own Science (7.6 vs 6.9).

**Deviations:** no pilot before the full run.

---

## R4: `titullm-3b`, full run, 2026-10-17

**Run facts**

| | |
|---|---|
| Notebook | https://kaggle.com/code/zoayriaabedin/one-run-decides-it-all (second Kaggle account). Outputs also in a separate dataset, `mahdihasanqurishi/benhallueval-qa-judge-runs-titullm` |
| Model | `hf.co/mradermacher/titulm-llama-3.2-3b-v1.1-GGUF:Q4_K_M` (`hishab/titulm-llama-3.2-3b-v1.1`), digest `78a9cab00c64…`, arch llama; context window 11,264 tokens; 4 requests at once |
| Software | Ollama 0.40.6, **pinned** (the first run with the pin) |
| Setup hashes | genre `1f0746b338e98740`; judge context `98699ea572bf0790`; judge no context `0d85867f06d6b007` |
| Session | 21:02–21:55 UTC (53 min). Genre 9 min, judge with context 31 min, judge without context 8 min |
| Calls | 10,120, all `ok`, 0 truncated. **100% `no_answer` in every turn** (strict and lenient parse) |
| Tokens | in: genre 1.54 M, context 4.32 M, no context 0.84 M; out: 80,960 (every reply hit the 8-token limit) |
| Files | `runs/benhallueval__titullm-3b__*.jsonl`; `results/titullm-3b/full/`; `runs/kaggle_outputs/titullm-3b__full__outputs.zip` |

**Result: no usable verdicts.**
- Every reply restates the start of the prompt and stops at the 8-token limit. For example, "You are an
  assistant. Decide whether the" (3,827 of 4,600 with the passage) and "You are sorting Bangla quiz questions
  by" (all 920 genre calls).
- Why: v1.1 is a **base model**, continually pre-trained on Bangla text. It was never instruction-tuned, so it
  continues text instead of answering.
- Under our rules every `no_answer` is an error, so its BHS is 100 in both conditions and its genre accuracy is
  0. It is never routed to.
- **The paper** reports BHS 50.0 for this model (Track A 99.75%, Track B 0.25%, so almost always "yes").
  Their parser probably turned such replies into a label; ours counts them as `no_answer`. Both describe the
  same thing: no real verdict.
- **Instruction-tuned versions exist:** `hishab/titulm-llama-3.2-3b-v2.0-Instruct-v1.0` (and `-v0.1`). They are
  not the paper's checkpoint. Adding one would be a new judge; decide that before seeing its result.

**Deviations:** no pilot (a 40-question pilot would have shown this in 5 minutes).

## R12: `gemma4-31b`, full run, 2026-10-18

**Run facts**

| | |
|---|---|
| Model | `gemma4:31b`, Q4_K_M, digest `17ba34c06c80…`, arch gemma4; thinking off; context window 4,096 tokens; 2 requests at once |
| Software | Ollama 0.40.6 (pinned) |
| Session | 06:11–11:42 UTC (5 h 31 min). Genre 1 h 32 min, judge with context 2 h 30 min, judge without context 1 h 17 min |
| Calls | 10,120, all `ok`, 0 `no_answer`, 0 truncated. Longest prompt 3,427 tokens |
| Tokens | in: genre 0.93 M, context 1.28 M, no context 0.50 M; out: 20,529 |
| Files | `runs/benhallueval__gemma4-31b__*.jsonl`; `results/gemma4-31b/full/`; `runs/kaggle_outputs/gemma4-31b__full__outputs.zip`. Also in `…/benhallueval-qa-judge-runs-b` |

**Results**

| | With passage | Without passage |
|---|---|---|
| BHS (main) | **1.44** (0.95–1.94) | **31.9** (30.5–33.4) |
| Correct answers flagged / hallucinations missed | 2.3% / 0.6% | 29.7% / 34.2% |
| Span subset | 1.7 | 25.6 |
| Miss rate F / C / S / I | 0.0 / 1.0 / 0.8 / 0.7% | 45 / 19 / 38 / 35% |

- **Best overall in both conditions, but tied with qwen3.5-27b.** It is 0.34 better with the passage (range −0.16
  to +0.87) and 0.94 better without (−0.49 to +2.50); neither gap is clear. It clearly beats every other judge.
- **Genre guessing:**
  - Against our labels: accuracy 93.8%, kappa 0.919 (0.898–0.937), 1.2 points below qwen3.5-27b (clear but small).
  - **Against the blind 200: kappa 0.805, the best of all models** (qwen3.5-27b 0.798).
- **Our genres:**
  - With the passage: Geography 0.2 (best), Religion 2.8 (worst).
  - Without it: Science 26.5 (best), Arts 36.7 (worst), the usual pattern.
- **Our genres vs its own genres:** the genres overlap 82–94%. It is slightly better in its own Science with the
  passage (1.82 vs 2.04, range −0.46 to −0.04), a tiny gain. Nothing else differs.
- **Mechanism check:** only 57 questions where its genre differs from ours, too few to tell.
- **Genre split between the two top judges (exploratory; none clear):**
  - With the passage, qwen3.5 leads in Arts and Religion, gemma4 in History, Science and Geography.
  - Without it, qwen3.5 leads in History and Religion, gemma4 in Arts, Science and Geography.
  - In-sample routing gain: 1.44 → 1.35 and 31.92 → 31.44.
- **Voting (exploratory):** gemma4 + qwen3.5 + a third judge scores 1.40 (vs 1.44) and 31.20 (vs 31.92), within
  noise.

**Deviations:** no pilot.

## R11: `deepseek-r1-14b`, full run in two sessions, 2026-10-17/18

**Run facts**

| | |
|---|---|
| Model | `deepseek-r1:14b`, Q4_K_M, digest `c333b7232bdb…`; a reasoning model, thinking capped at 1,024 tokens; context window 11,264 tokens; 4 requests at once |
| Software | Ollama 0.40.6 in both sessions. Session 1 was not pinned but got 0.40.6; session 2 was pinned. The setup fingerprints match, so the notebook would have stopped otherwise |
| Session 1 | 11 h (time budget): genre 1 h 34 min, judge with context 6 h 23 min, judge without context 2,272 of 4,600 |
| Session 2 | 3 h 14 min. It resumed from a dataset made of session 1's logs (`deepseek-partial-runs`) and did only the 2,328 calls left |
| Calls | 10,120. Capped: 3 with context, 5 without (counted as `no_answer`). 0 truncated (7,798 + 2,334 server requests checked) |
| Tokens | in: genre 1.43 M, context 3.80 M, no context 0.71 M; **out: 2.39 M** (mostly thinking). Slowest model: about 14 h of GPU time |
| Files | `runs/benhallueval__deepseek-r1-14b__*.jsonl`; `results/deepseek-r1-14b/full/`; `runs/kaggle_outputs/deepseek-r1-14b__full__outputs.zip` (session 2) and `…__session1_partial__outputs.zip` |

**Results**

| | With passage | Without passage |
|---|---|---|
| BHS (official; `no_answer` = error) | **22.8** (21.2–24.6) | **38.3** (36.7–39.9) |
| `no_answer` | **745 (16.2%)** | 7 (0.2%) |
| BHS, answered items only | 7.7 | 38.2 |
| BHS, lenient parse (diagnostic) | 7.6 | 38.3 |
| Track A / Track B | 22.7% / 22.8% | 48.2% / 28.4% |

- **With the passage it judges well but often breaks the format.** In 16% of replies it wrote an explanation
  after thinking instead of a bare yes/no, for example "…Therefore, the answer is hallucinated.\n\nyes".
  Strict parsing counts these as errors. On the replies it formats correctly, it is at the level of gemma2-27b
  and gpt-oss-20b (7.7). Report the strict, answered-only and lenient numbers.
- **Without the passage it follows the format** (0.2% `no_answer`) and leans to "yes" (it flags 48% of correct
  answers).
- **Compared with qwen3.5-27b:** worse by 21.0 with the passage (19.4–22.8) and 5.4 without (3.7–7.4).
- **Genre guessing:**
  - Against our labels: accuracy 83.7%, macro-F1 0.729, kappa 0.783 (0.751–0.813).
  - Against the blind 200: kappa 0.739.
  - Third best, after the two Qwens. It over-uses HISTORY (356).
- **Our genres:**
  - With the passage, every genre is 20.3–24.1. The format errors are spread evenly.
  - Without the passage, Geography (31.9) is best and Arts (43.3) is worst, the usual pattern.
- **Our genres vs its own genres:** no clear difference in any usable genre.
- **Mechanism check:** no difference (22.9 vs 22.3; 38.4 vs 37.8).
- **Genre split:** without the passage, DeepSeek is best in Geography (31.9 vs qwen3.5's 32.5). The gap is not
  clear (range −4.1 to +5.1). In-sample routing gain: 32.85 → 32.79.

## R10: `titullm-3b-instruct`, full run, 2026-10-18

**Run facts**

| | |
|---|---|
| Model | `hishab/titulm-llama-3.2-3b-v2.0-Instruct-v1.0` @ `6a9600483daf`; transformers 4-bit NF4; its own chat template; context 4,096 tokens; 8 prompts at once |
| Session | about 2 h 50 min. Load under 1 min (GPUs then had 14.4 and 13.9 GB free). Genre 55 min, judge with context 78 min, judge without context 36 min |
| Calls | 10,120, all `ok`, none too long (longest 3,395 tokens). **100% `no_answer`** |
| Files | `runs/benhallueval__titullm-3b-instruct__*.jsonl`; `results/titullm-3b-instruct/full/`; `runs/kaggle_outputs/titullm-3b-instruct__full__outputs.zip` |

**Result: no usable verdicts.** It ignores the English task and **answers the Bangla question itself**, or
starts to chat:
- "ভালুকা মোট ১১০টি গ্রাম নিয়ে গঠিত" (*Bhaluka has 110 villages*);
- "আচ্ছা, আমি ভাব[ছি]…" (*Okay, I think…*);
- "ধাপ 1: প্রদত্ত তথ্য বুঝুন" (*Step 1: understand the given information*).

No reply contains an English yes or no. Only 46 (with the passage) and 35 (without) start with a Bangla হ্যাঁ/না,
about 1%, so a Bangla-aware reading would not rescue it either. For genre it names an entity from the question
(for example "ক্রিকেট", *cricket*) or says nothing.

**Pattern across the Bangla-centric judges:**
- None of the three Bangla fine-tunes (TituLLM base, TituLLM instruct, BanglaLLaMA) gives usable verdicts to an
  English judging prompt.
- TigerLLM, a Gemma-3 fine-tune, works but is weak (38.8 / 44.8).
- Report this as a finding, together with the English-prompt limitation.

## R9: `banglallama-13b`, full run, 2026-10-18 (third try)

**Run facts**

| | |
|---|---|
| Model | `BanglaLLM/bangla-llama-13b-instruct-v0.1` @ `a5986f8599cd`. LoRA merged (r=64, alpha=128; 280 layers in 6 min). Transformers 4-bit NF4, Alpaca format, context 4,096; batches limited to 6,144 tokens |
| Memory | 31 GB RAM free throughout; after loading, the GPUs had 12.2 and 10.4 GB free. No memory errors |
| Session | about 2 h 44 min. Merge and load 9 min, genre 39 min, judge with context 74 min, judge without context 42 min |
| Calls | 10,120, all `ok`, none too long (longest 3,971 tokens). **100% `no_answer` under the strict parse** |
| Files | `runs/benhallueval__banglallama-13b__*.jsonl`; `results/banglallama-13b/full/`; `runs/kaggle_outputs/banglallama-13b__full__outputs.zip` |

**Result: no usable verdicts (official).** The merged model writes fluent Bangla, so the merge worked. But it
answers **in Bangla** despite "Provide the answer in English only":
- with the passage: "উত্তর: না" 2,853, "উত্তর: হ্যাঁ" 453, plus "না, …" with an explanation;
- without the passage: "উত্তর: না" 1,842 and "উত্তর নেই …" ("no answer") 2,033;
- genre: "এই কাজটিতে, আপনাকে…" ("In this task, you…") 524, and "উত্তরঃ ইতিহা[স]" ("Answer: History") 301.

The strict parser (English yes/no only, fixed before any result) counts all of these as `no_answer`.

**Diagnostic only: reading হ্যাঁ/না as yes/no** (decided after seeing the replies; never official):

| | With passage | Without passage |
|---|---|---|
| Readable verdicts | 4,266 of 4,600 | 1,856 of 4,600 |
| BHS on those | 57.9 (Track A 24.2%, Track B 91.5%) | 50.1 (almost always "no") |

- With the passage it flags correct answers **more** often (24%) than hallucinated ones (8.5%), which is worse
  than chance.
- Genre, read in Bangla: it answers HISTORY or explains; 10.4% correct.
- **Conclusion:** even loaded correctly, BanglaLLaMA cannot judge in this setup. Its BHS of about 50 in the paper
  does not depend on the loading bug (see the reference doc, known issue 7, now corrected).
- **Limit to report:** our prompt is in English, as in the paper's Table 14. A Bangla prompt might suit
  Bangla-centric models better; that would be an optional extra.

## R8: `qwen3.5-27b`, full run, 2026-10-18

**Run facts**

| | |
|---|---|
| Model | `qwen3.5:27b`, Q4_K_M, digest `64ae5b1d651f…`, arch qwen35; thinking off; context window 6,144 tokens; 2 requests at once |
| Software | Ollama 0.40.6 (pinned) |
| Setup hashes | genre `7d28037168826fa1`; judge context `67657d792d69b4ef`; judge no context `04f6eafa83c5f384` |
| Session | 22:01–02:14 UTC (4 h 13 min). Genre 33 min, judge with context 2 h 34 min, judge without context 57 min |
| Calls | 10,120, all `ok`, 0 `no_answer`, 0 truncated. Longest prompt 5,013 tokens |
| Tokens | in: genre 1.11 M, context 2.07 M, no context 0.59 M; out: 21,444 |
| Files | `runs/benhallueval__qwen3.5-27b__*.jsonl`; `results/qwen3.5-27b/full/`; `runs/kaggle_outputs/qwen3.5-27b__full__outputs.zip`. Also in the separate dataset `…/benhallueval-qa-judge-runs-b` |

**Results**

| | With passage | Without passage |
|---|---|---|
| BHS (main) | **1.8** (1.3–2.2) | **32.9** (31.6–34.1) |
| Correct answers flagged (Track A error) | 1.4% | 19.9% |
| Hallucinations missed (Track B error) | 2.2% | 45.8% |
| BHS on the span subset | 3.0 | 27.6 |
| Miss rate F / C / S / I | 0.7 / 4.6 / 1.9 / 1.5% | 60 / 32 / 40 / 51% |

- **Best judge in both conditions, clearly.**
  - With the passage it beats gemma2-27b by 4.3 (3.7–5.0), gpt-oss-20b by 5.3 and qwen2.5-32b by 8.1.
  - Without the passage it beats qwen2.5-32b by 4.6 (3.1–6.1) and gemma2-27b by 5.3.
- **Near the ceiling with the passage (1.8).** With the passage, our set is close to solved for the best open
  judge, so that condition has little room to show a routing gain. Report this as a finding: Dataset 2 (real
  answers) and the without-passage condition carry the routing test.
- **Best in every genre in both conditions.** The earlier genre splits (gpt-oss in Science with the passage;
  gemma2 in Science and Geography without) are gone. In-sample routing headroom is 0 again.
- **Genre guessing, best:**
  - Against our labels: accuracy 95.0%, macro-F1 0.906, kappa 0.934 (0.915–0.952). That is 3.2 points above
    qwen2.5-32b (1.7–4.8).
  - **Against the blind 200: kappa 0.798**, the same as qwen2.5-32b (0.799) and as the human-vs-draft agreement
    (0.81).
  - So the two Qwen models agree more with our LLM-drafted labels than with blind human labels. Report both
    numbers.
- **Our genres:** with the passage, Geography (0.8) is best and Science (2.7) worst. Without it, Science (27.8)
  is best and Arts (38.5) worst.
- **Our genres vs its own genres:** its genres overlap ours on 86–94%. It is slightly better in its own Science
  with the passage (2.45 vs 2.69, range −0.47 to −0.06); the gain is tiny. Nothing else differs.
- **Mechanism check:** only 46 questions where its genre differs from ours (too few to judge): 1.7 vs 2.5 with
  the passage, 32.8 vs 33.7 without.

**Cross-judge pattern (7 working judges):**
- With the passage, **Geography is the easiest genre for all 7 judges**.
- Without the passage, **Arts is the hardest for 5 of 7**.

So genre changes how hard the questions are, consistently across judges. It does not change which judge is
best.

**Deviations:** no pilot.

## R7: `gpt-oss-20b`, full run, 2026-10-17/18

**Run facts**

| | |
|---|---|
| Model | `gpt-oss:20b`, MXFP4, digest `f38aa0c53da5…`; a reasoning model, run with thinking "low" and output capped at 512 tokens; context window 7,168 tokens; 4 requests at once |
| Software | Ollama 0.40.6 (pinned) |
| Setup hashes | genre `38e9804692115dfd`; judge context `861808a65828b6ab`; judge no context `851492af7866ce02` |
| Session | 22:03–03:13 UTC (5 h 10 min). Genre 16 min, judge with context 2 h 30 min, judge without context 2 h 16 min |
| Calls | 10,120, 0 truncated. **Capped** (thinking reached 512 tokens, so counted as `no_answer`): genre 1, with context 13 (0.3%), without context 79 (1.7%) |
| Tokens | in: genre 1.18 M, context 2.52 M, no context 0.83 M; **out: 1.26 M** (mostly thinking) |
| Files | `runs/benhallueval__gpt-oss-20b__*.jsonl`; `results/gpt-oss-20b/full/`; `runs/kaggle_outputs/gpt-oss-20b__full__outputs.zip`. Also in a separate dataset, `…/benhallueval-qa-judge-runs-b` |

**Results**

| | With passage | Without passage |
|---|---|---|
| BHS (main) | **7.1** (6.2–8.0) | **39.8** (38.3–41.2) |
| BHS, answered items only | 6.8 | 38.8 |
| Correct answers flagged (Track A error) | 6.6% | 57.4% |
| Hallucinations missed (Track B error) | 7.5% | 22.1% |
| BHS on the span subset | 7.2 | 36.5 |
| Miss rate F / C / S / I | 1 / 8 / 18 / 3% | 29 / 14 / 26 / 20% |

- **With the passage: second best, close to gemma2-27b.** It is 1.0 point behind (range 0.0 to 2.1, so not
  clearly different).
- **Its errors differ from gemma's.** It catches more hallucinations (F 1% vs 4%, C 8% vs 12%, I 3% vs 11%)
  but flags more correct answers (6.6% vs 1.6%), and it misses more S answers (18% vs 16%). The two agree on 88%
  of verdicts. This kind of complementarity is what voting (method B) needs.
- **Without the passage it leans to "yes":** it flags 57% of correct answers. It is 2.3 points worse than
  qwen2.5-32b (0.5–4.1).
- **Genre guessing:**
  - Against our labels: accuracy 80.0%, macro-F1 0.687, kappa 0.732 (0.698–0.762).
  - Against the blind 200: kappa 0.715.
  - About gemma2-27b's level; 11.8 points below qwen2.5-32b.
- **Our genres:**
  - With the passage: Geography 5.9 is best; Arts 8.1 and Religion 8.2 are worst. In Science it beats gemma2
    (6.2 vs 6.9), the first split with the passage, but not clearly (range −2.2 to +3.4).
  - Without the passage: Geography 35.5 and Science 35.7 are best; Arts 44.1 is worst.
- **Our genres vs its own genres:** no clear difference in any usable genre.
- **Mechanism check:** with the passage, 6.9 when its genre matches ours and 8.0 when it does not; without it,
  39.6 vs 40.4. Both are in the expected direction but not clear.
- In-sample routing headroom with the passage: 6.10 → 6.01 (gemma2 everywhere, gpt-oss for Science).

**Deviations:** no pilot. Optional model, so it belongs to the "new open models" set.

## R6: `qwen2.5-32b`, full run, 2026-10-17

**Run facts**

| | |
|---|---|
| Model | `qwen2.5:32b`, Q4_K_M, digest `9f13ba1299af…`; context window 10,240 tokens; 2 requests at once |
| Software | Ollama 0.40.6. **Not pinned** in this notebook copy: the log shows `install.sh \| sh` without `OLLAMA_VERSION`. It installed the latest, which was still 0.40.6 |
| Setup hashes | genre `a38053a85a99f96c`; judge context `72ff00cd6779621e`; judge no context `c8468a0208880e29` |
| Session | 18:11–21:43 UTC (3 h 32 min). Genre 53 min, judge with context 1 h 56 min, judge without context 29 min |
| Calls | 10,120, all `ok`, 0 `no_answer`, 0 truncated. Longest prompt 8,682 tokens |
| Tokens | in: genre 1.46 M, context 3.92 M, no context 0.82 M; out: 21,437 |
| Files | `runs/benhallueval__qwen2.5-32b__*.jsonl`; `results/qwen2.5-32b/full/`; `runs/kaggle_outputs/qwen2.5-32b__full__outputs.zip`. Also uploaded to a separate dataset, `…/benhallueval-qa-judge-runs-qwen2-5-32b` |

**Results**

| | With passage | Without passage |
|---|---|---|
| BHS (main) | **9.9** (9.0–10.8) | **37.4** (36.2–38.8) |
| Correct answers flagged (Track A error) | 3.2% | 22.1% |
| Hallucinations missed (Track B error) | 16.6% | 52.8% |
| Says "yes" (the true rate is 80%) | 67% of answers | 42% of answers |
| BHS on the span subset | 21.0 | 32.3 |
| Miss rate F / C / S / I | 3 / 38 / 12 / 13% | 67 / 40 / 45 / 59% |

- **With the passage: second best.** It is 3.8 points behind gemma2-27b (2.9–4.7). Its weak spot is
  comprehension: it misses 38% of passage spans that answer a different question (gemma misses 12%).
- **Without the passage: best so far,** but tied with gemma2-27b (+0.75, range −0.56 to +2.16).
- **The paper** had it at BHS 46.9 (Track A 27.9%, Track B 65.8%). As with gemma2-27b, it misses far fewer of our
  hallucinations than of the paper's.
- **Genre guessing, by far the best:**
  - Against our labels: accuracy 91.8%, macro-F1 0.848, kappa 0.893 (0.869–0.917).
  - **Against the blind 200: kappa 0.799 (0.732–0.865), about the human-vs-draft level (0.81).**
  - 10.3 points more accurate than gemma2-27b (8.0–12.7).
  - No History over-use (301 named; ours 290). Science recall is 134 of 135.
  - Its agreement with our labels may be inflated, because those labels were LLM-drafted. The blind 200 is the
    cleaner number.
- **Our genres:** with the passage Geography is best (6.5) and History worst (11.1). Without it, Religion is best
  (33.3) and Arts worst (41.2).
- **Our genres vs its own genres:** its genres overlap ours on 80–96% of questions, so the differences are tiny.
  It is slightly **better** in its own History with the passage (10.3 vs 11.1, range −1.4 to −0.3). This is the
  first "better in own genre" case, and it is small.
- **Mechanism check:** with the passage, 10.1 when its genre matches ours and 7.7 when it does not. Without the
  passage, 37.3 vs 39.5, in the expected direction but not clear.
- **First genre split** (overview section 7). Without the passage, gemma2-27b beats qwen in Science (34.0 vs 35.3)
  and Geography (34.4 vs 36.4). Neither gap is clear (ranges include 0). In-sample routing would go from 37.43
  to 37.01.

**Deviations:** no pilot; Ollama version not pinned (it happened to match).

## R5: `tigerllm-9b`, full run, 2026-10-17

**Run facts**

| | |
|---|---|
| Model | `hf.co/mradermacher/TigerLLM-9B-it-GGUF:Q4_K_M`: the Sept 2025 upload of TigerLLM-9B-it, a Gemma-3 model of about 12B (see the TigerLLM note). Digest `d2b91a15fc7e…`, arch `gemma3`; context window 4,096 tokens; 4 requests at once |
| Software | Ollama 0.40.6 (pinned) |
| Setup hashes | genre `383624e809db2d36`; judge context `829505b5fa8ca4eb`; judge no context `bb6bc4c99ba0c942` |
| Session | 20:50–22:40 UTC (1 h 50 min). Genre 36 min, judge with context 49 min, judge without context 19 min |
| Calls | 10,120, all `ok`, 0 truncated. `no_answer`: 1 genre reply ("AGRICULTURE"), 0 judge replies. Longest prompt 3,423 tokens |
| Tokens | in: genre 0.93 M, context 1.26 M, no context 0.48 M; out: 20,450 |
| Files | `runs/benhallueval__tigerllm-9b__*.jsonl`; `results/tigerllm-9b/full/`; `runs/kaggle_outputs/tigerllm-9b__full__outputs.zip` |

**Results**

| | With passage | Without passage |
|---|---|---|
| BHS (main) | **38.8** (37.2–40.4) | **44.8** (43.7–45.9) |
| Correct answers flagged (Track A error) | 14.6% | 11.6% |
| Hallucinations missed (Track B error) | 63.1% | 78.0% |
| Says "yes" (the true rate is 80%) | 32% of answers | 20% of answers |
| BHS on the span subset | 47.9 | 47.3 |
| Miss rate F / C / S / I | 62 / 76 / 49 / 66% | 89 / 81 / 55 / 87% |

- **A lenient judge.** It says "no" too often and misses most hallucinations. On answers copied from the passage
  it is at chance. The passage helps by 6.0 points (4.2–7.8).
- **The paper** had it as the best open QA judge (BHS 28.3; Track A 18.4%, Track B 38.2%). On our set it misses
  more. The two sets are not directly comparable.
- **Compared with gemma2-27b** (paired): worse by 32.7 with the passage (31.2–34.3) and by 6.6 without
  (5.1–8.2). It is second without the passage (44.8, vs llama 46.0).
- **Genre guessing, second best:**
  - Against our labels: accuracy 76.8%, macro-F1 0.727, kappa 0.689 (0.652–0.723).
  - Against the blind 200: kappa 0.656.
  - 4.7 points less accurate than gemma2-27b (2.4–7.1).
  - It over-uses HISTORY (474; 93 of our Arts questions become History). It names Religion 59 times, all correct.
- **Our genres:** Geography is its best genre in both conditions (33.0 with the passage, 39.2 without). With the
  passage Religion is worst (44.1); without it, Science is worst (47.5).
- **Our genres vs its own genres:** it is clearly worse in its **own Arts** in both conditions (with the passage
  43.4 vs 39.7, range +1.7 to +5.8; without it 48.2 vs 46.1, range +0.7 to +3.6). The other genres show no clear
  difference.
- **Mechanism check:** no support. With the passage it scores 39.4 when its genre matches ours and 36.9 when it
  does not; without the passage, 45.0 vs 44.2.

**Deviations:** no pilot.

## Note, 2026-10-18: TituLLM instruct added as a 13th judge

**Decision (Mahdi, 2026-10-18, before any result for this model).** Add
`hishab/titulm-llama-3.2-3b-v2.0-Instruct-v1.0` (revision `6a9600483daf…`) as key `titullm-3b-instruct`.

- **Why:** the paper's TituLLM (`titulm-llama-3.2-3b-v1.1`) is a base model and gave no usable verdict (R4).
  The study needs a working small Bangla-centric judge.
- **How it is reported:** a new judge, not the paper's checkpoint. R4 stays as the paper's model.
- **Setup:**
  - Hugging Face backend, 4-bit NF4 (no GGUF exists);
  - the model's own chat template (an Alpaca-style system line plus "### Instruction / ### Response");
  - context 4,096 tokens;
  - 8 prompts at once.
- **Checked with its tokenizer:** the longest prompt is 3,395 tokens, so none is too long.

## Note, 2026-10-18: TigerLLM-9B

The first Kaggle try stopped at the architecture check: the GGUF is `gemma3`, and the notebook expected
`gemma2`. The check worked, but the expectation was wrong.

Hugging Face history of `md-nishat-008/TigerLLM-9B-it`:
- Created 2025-09-14.
- Held a Gemma-3 model of about 12B from 2025-09-15 to 2026-09-17.
- Then got new weights and was renamed TigerLLM-12B-it (2026-10-15).

So the only public "TigerLLM-9B-it" during BenHalluEval's study was this Gemma-3 upload. The GGUF we use is
`mradermacher/TigerLLM-9B-it-GGUF:Q4_K_M` (7.4 GB, made 2025-09-15 from exactly that upload). The notebook now
expects `gemma3`. Report it as "TigerLLM-9B-it (Sept 2025 upload; Gemma-3, ~12B)". The paper names no revision,
so this match is very likely but unverified.

## Note, 2026-10-18: BanglaLLaMA-13B

The first Kaggle try ran out of GPU memory while loading.

**Cause.** The checkpoint stores **un-merged LoRA layers**: 280 modules saved as `base_layer` / `lora_A` /
`lora_B`. Transformers therefore saw every main weight as missing. It created them empty at full fp16 size
(hence the out-of-memory error), and it would otherwise have run them with random values.

**Fix in the notebook.**
- For `banglallama-13b`, the backend first merges the LoRA layers: W = base + (128/64) × B·A. The r and alpha
  values come from the repo's own training script.
- Each shard is downloaded and merged on the CPU, then saved to `/tmp`. The merge needs about 40 GB of free
  disk and stops with a message if there is less.
- The merged model is then loaded in 4-bit as before.
- A new guard stops **any** Hugging Face model whose checkpoint has missing weights, so no judge ever runs
  with random layers.

Tested on a tiny fake model with `src/bench/test_lora_merge.py` (all 4 checks pass). The setup record says
"LoRA merged r=64 alpha=128".

**Second try (2026-10-18, Kaggle version 4).** The merge worked: 280 layers merged in about 6 min, the model
loaded in 2 min, and all prompts fit 4,096 tokens. It then ran out of **GPU** memory during the genre turn.

- **Why:** LLaMA-2-13B has no grouped-query attention, so its key-value cache costs about 0.8 MB per token.
  Four genre prompts of about 4,000 tokens each need about 13 GB.
- **Fix:**
  - Hugging Face batches now have a token budget: prompts × (tokens + new tokens) ≤ `batch_tokens`, which is
    6,144 for BanglaLLaMA. The longest prompts go one at a time.
  - A GPU memory error splits the batch in two and retries. A single prompt that still does not fit is
    recorded as `error` and retried on resume.
  - The repeated "max_length" notice is silenced.
- **Tested** on CPU with a tiny model (`src/bench/test_hf_batching.py`, 3 checks). The answers are identical
  however the prompts are grouped.
- The row in the progress table stays empty until a run finishes.

## Note, 2026-10-18: DeepSeek-R1-14B, first session (partial, not imported)

- **Session:** 11 h, ending at the time budget. Genre (920) and judge with passage (4,600) are done; judge
  without passage has 2,272 of 4,600. Ollama 0.40.6, but **not pinned** in that notebook copy.
- **Preview of the finished parts:**
  - Genre: accuracy 83.7%, kappa 0.78; blind 200 kappa 0.74.
  - With passage: strict BHS 22.8, because 745 replies (16.2%) gave an explanation instead of a bare yes/no
    after thinking, e.g. "…Therefore, the answer is hallucinated.\n\nyes".
  - On answered items only: BHS 7.7. Lenient parse (diagnostic only): 7.6.
  - Report all three; the strict number is the official one (golden rule 6: no prompt change for one model).
- **To finish:** resume with this version's output as input and `OLLAMA_VERSION = "0.40.6"` (about 3 h).

## Lock v1, 2026-10-18 13:04 UTC

`results/lock/lock_v1.json` (sha256 `779cc5a7cdc2…`), made by `src/routing/make_lock.py` from BenHalluEval runs only.
The script refuses non-BenHalluEval records and never overwrites a lock.

- **Dataset 2 pool:** 9 judges. Excluded for no usable verdicts: banglallama-13b, titullm-3b, titullm-3b-instruct.
  gpt-4.1-mini was not run, so it is dropped unless a new lock version comes before Dataset 2.
- **A** = gemma4-31b in both conditions. **Best genre guesser** = qwen3.5-27b.
- **E table:**
  - with passage: gemma4-31b for History, Science, Geography; qwen3.5-27b for Arts, Religion;
  - without passage: qwen3.5-27b for History, Religion; gemma4-31b for Arts, Science, Geography;
  - Other falls back to A.
- **Tests:** 6 confirmatory comparisons, Holm-corrected, with 10,000 paired bootstrap re-samples.
- **Drafts to freeze:** `docs/preregistration.md` and `docs/expectations.md`.

## Lock v2 and GenreHalluEval v1.0 (Dataset 2), 2026-10-27

- **Lock v2** (`results/lock/lock_v2.json`, sha256 `6d3c1d29cb81…`, by `src/routing/make_lock_v2.py`, BenHalluEval
  runs only): every lock v1 choice unchanged, plus route **R (best path)**: the our-genre path (qwen3.5-27b names the
  genre → judge × genre table) competes with the own-genre cells; the lower BenHalluEval BHS wins. Only LLMs with a cell
  below the highest our-genre score are asked for genre: gemma4-31b and qwen3.5-27b with the passage; plus deepseek,
  gemma2, gpt-oss and qwen2.5 without it (pruning checked to give the same routes on all 920 questions).
  BenHalluEval check, R minus A: −0.10 / −0.33 (same data), 0.00 / +0.45 (5-fold); no range excludes 0.
  Confirmatory tests on Dataset 2: R vs A per condition, Holm over 2.
- **GenreHalluEval v1.0** (`data/final/GenreHalluEval-v1.0/`, zip in `release/kaggle-genrehallueval/`): 250 questions
  from the team's sheet (17 rows replaced for BenHalluEval overlap), gold + 4 hallucinations each, written by Claude
  under guide v1.0 (`data/labels/dataset2/hallucinations_claude/batch_01..10.txt`). Set B (`items.csv`, the test):
  875 answers with the passage, 375 without. Set A: all with the passage, for publishing.
- **Notebooks** (not run yet): `genrehallueval_single_best.ipynb` (A; about 1 GPU hour, estimate) and
  `genrehallueval_routed.ipynb` (R, D, E, F; about 3 GPU hours, estimate). Tested end to end with the fake model
  (`src/dataset2/test_notebooks.sh`): pilot, clean stop at the time limit, resume from a nested input, compare.
- **Next:** freeze the prereg on OSF → run both notebooks → both annotators label → score with
  `src/dataset2/compare_routes.py --labels …`.
- **Update, same day: labels and v1.1.** Both annotators' passage-label sheets arrived (all 1,250 answers; world label
  dropped). Correction, same day: the first two files were both annotator 2's (Md Saminul Amin filled both sheets);
  annotator 1 (Umme Zoayria Abedin) sent their own sheet afterwards. Annotator 1's labels were not in the copy annotator
  2 filled, so the labels stayed blind; gold answers were written by Mahdi, who has not seen the labels. Kappa 0.990 (1,246 of 1,250 agree); the 4
  disagreements are annotator 2's swaps in d2-068 and d2-201 (to resolve by discussion). 18 text fixes (`data/labels/dataset2/text_fixes_v1.1.csv`): 16 passages that did not
  state the gold (15 Islamic Religion passages, flagged by the team and by annotator 1 in the sheet), d2-142's question year, d2-110's C answer.
  GenreHalluEval v1.1 built (`data/final/GenreHalluEval-v1.1/`; v1.0 moved to `data/final/superseded/`); item ids
  unchanged; notebook test suite passes again. Re-upload the zip to Kaggle (New Version) before running.
- **Frozen on OSF, 2026-10-27:** registration https://osf.io/fmbs8 (Open-Ended, embargoed; the API answers 401 for the
  registration, so it exists and is private). Frozen files: `release/osf_freeze/` (prereg sha256 `9e747de4…`, lock v2,
  GenreHalluEval v1.1 checksums, expectations, `files_sha256.txt` with the label-sheet hashes). Next: Kaggle runs.

## GenreHalluEval run 1: single best (A), 2026-10-27

- **Notebook:** `genrehallueval_single_best.ipynb`, `RUN_MODE = "full"`, on Kaggle (2× T4). Outputs zip stored
  unchanged (read-only): `runs/genrehallueval/genrehallueval__single_best__full__outputs.zip` (sha256 `759c850d…`).
- **Setup:** gemma4-31b = `gemma4:31b`, Ollama 0.40.6, digest `17ba34c0…`, Q4_K_M (the same digest as on BenHalluEval);
  temperature 0, seed 2026, `max_new_tokens` 8, think off, 2 parallel. `num_ctx` 2048 (BenHalluEval: 4096): the same
  rule (next multiple of 1,024 above the longest prompt), and these prompts are shorter (longest 514 tokens).
- **Checks, all passed:** the dataset files on Kaggle match the frozen v1.1 checksums; the lock and the 3 prompt hashes
  match lock v2; 875 `context` + 375 `no_context` calls = exactly Set B; status ok 1,250; `no_answer` 0; truncated 0;
  every call stopped normally; every answer routed to gemma4-31b.
- **Cost:** 1,250 calls; 259,104 prompt tokens and 2,500 output tokens; judge time 1,994 s (875 calls 1,616 s, 375 calls
  378 s); wall time 41 min (13:58–14:39 UTC).
- **Not scored yet, on purpose:** no BHS is computed until the 4 label disagreements are settled
  (`data/labels/dataset2/passage_label_resolutions_v1.csv`) and the routed run is in.
- **Timing:** Mahdi confirmed the run started after the OSF registration was submitted (same day).
- **Labels settled, 2026-10-27 (before any score was computed):** annotator 2 withdrew the 4 disputed labels (d2-068,
  d2-201; the answers looked close to the correct one). Final labels: `data/labels/dataset2/passage_labels_agreed_v1.csv`
  (1,246 agreed + 4 resolved; 0 differ from the design label; 0 unclear). The routed notebook is running.

## GenreHalluEval run 2: routed (R, D, E, F), 2026-10-27

- **Notebook:** `genrehallueval_routed.ipynb`, `RUN_MODE = "full"`, on Kaggle (2× T4), 14:00–16:07 UTC (started after
  the OSF registration, like run 1). Outputs zip stored unchanged (read-only):
  `runs/genrehallueval/genrehallueval__routed__full__outputs.zip` (sha256 `a23acc08…`).
- **Setup:** Ollama 0.40.6; every model digest equals lock v2 (the same as on BenHalluEval): deepseek-r1-14b
  `c333b723…`, gemma2-27b `53261bc9…`, gemma4-31b `17ba34c0…`, gpt-oss-20b `f38aa0c5…`, qwen2.5-32b `9f13ba12…`,
  qwen3.5-27b `64ae5b1d…`. Temperature 0, seed 2026; think mode and output cap per model as in the lock; `num_ctx` by
  the usual rule (next multiple of 1,024 above the longest prompt).
- **Checks (Claude, with an independent script that uses no labels), all passed:**
  - the dataset files match the frozen v1.1 checksums; the lock and the 3 prompt hashes match lock v2;
  - every call's prompt hash equals the prompt rebuilt from the package and the templates, so the genre prompts held
    only question + passage (golden rule 1);
  - genre askers as locked: gemma4-31b and qwen3.5-27b on all 250 questions; deepseek-r1-14b, gemma2-27b, gpt-oss-20b
    and qwen2.5-32b on the 75 `no_context` questions;
  - the R, D, E and F routes of all 1,250 answers equal an independent recomputation from lock v2 and the named
    genres, and every routed answer has a verdict from its judge in its own condition;
  - judge calls: 1,480, all status ok, `no_answer` 0, all stopped normally; no prompt was cut (manifest: truncated 0,
    partial false; the longest prompt is below `num_ctx` for every model).
  - Genre `no_answer` 2: deepseek-r1-14b on d2-205 (reached the 1,024-token cap while thinking) and gemma2-27b on
    d2-073 (answered "SPORTS", not one of the 6 codes). Each only removes that LLM's own-genre path for that question.
- **Answers per judge:**

  | Route | With passage (875) | Without passage (375) |
  |---|---|---|
  | R | gemma4-31b 520, qwen3.5-27b 355 | gemma4-31b 220, qwen3.5-27b 155 |
  | D | gemma4-31b 525, qwen3.5-27b 350 | gemma4-31b 225, qwen3.5-27b 150 |
  | E | gemma4-31b 505, qwen3.5-27b 370 | gemma4-31b 210, qwen3.5-27b 165 |
  | F | gemma4-31b 665, qwen3.5-27b 210 | gemma4-31b 210, qwen3.5-27b 155, gemma2-27b 5, deepseek-r1-14b 5 |

  Prediction #11 (at least 95% of answers to gemma4-31b or qwen3.5-27b) holds for every route (lowest: F without the
  passage, 365 of 375).
- **Genre guessing (exploratory), agreement with our genre on the settled questions** (233 of 250; the 17 awaiting the
  relabel are left out): qwen3.5-27b 92.3%, gemma4-31b 87.6%; on the 69 settled `no_context` questions: qwen2.5-32b
  84.1%, deepseek-r1-14b 75.4%, gpt-oss-20b 75.4%, gemma2-27b 73.9%. (BenHalluEval accuracy: 95.0, 93.8, 91.8, 83.7,
  80.0, 81.5.)
- **Determinism (exploratory):** gemma4-31b gave the same verdict in both notebooks on 917 of the 920 answers it judged
  here (99.7%; the prompts are identical). Different: d2-160__p2 (with passage), d2-057__p5 and d2-145__p2 (without).
  Likely GPU non-determinism with 2 parallel slots (not verified). Prediction #12 (at least 99%) holds.
- **Cost:** 2,280 calls (800 genre, 1,480 judge); 1,323,842 prompt tokens and 30,823 output tokens; model busy time
  5,567 s; wall time 2 h 07 min. Preregistered estimate: about 1,300–1,800 judge calls and about 3 GPU hours.
- **Scored, 2026-10-27 (confirmatory; agreed labels; `results/genrehallueval/confirmatory_v1.md`):** H1 (with the
  passage) R 0.86 vs A 0.57, +0.29 (95% −0.07 to +0.71), Holm p 0.369; H2 (without) R 22.83 vs A 21.83, +1.00 (−2.00 to
  +4.17), Holm p 0.548. **Neither hypothesis is supported.** E = R on every answer; F vs A +0.14 and +0.50, not clear.
  With the passage A made only 5 errors in 875 answers (1 false alarm, 4 misses), so H1 had almost no room.
- **Held:** route D and the per-genre tables wait for the genre relabel of the 17 replaced questions (deviation log,
  2026-10-27). When it is in: update the genres in the package, recompute D from the relabelled genres (the D column in
  `routes.csv` used the old ones), then run `compare_routes.py` into `results/genrehallueval/comparison.md`.

## Exploratory, 2026-10-27: split experiments (after the confirmatory result)

- **Inside BenHalluEval (from saved runs, no new calls):** `src/routing/split_experiment.py` →
  `results/split_experiment/split_experiment.md`. The 920 questions are split into halves stratified by genre (seed
  2026). All choices are learned on one half with the lock rules and tested on the other half. R vs A: with the
  passage +0.00 (R sent every question to gemma4-31b); without it +0.03 (−1.38 to +1.41). Over 400 more runs (200
  random splits, each used in both directions), R − A averages +0.06 with the passage and −0.09 without it. So routing
  does not beat A even when there is no change of dataset.
- **Inside GenreHalluEval (new runs; built, not run yet):** plan in `docs/split-experiment-plan.md`.
  - Package `data/final/GenreHalluEval-split-v1/` (`learn_items.csv` sha256 `34aa4bad…`, `test_items.csv`
    `c68137f9…`), built by `src/split/build_split.py`.
  - Notebooks `split_learn`, `split_routed` and `split_single_best`, built by `src/split/make_split_notebooks.py`.
  - Lock made by `src/split/make_split_lock.py`; local test `src/split/test_split.sh`, which passes.
  - Kaggle kit in `release/kaggle-split/` (`HOW_TO_USE.md`).
  - Pool: deepseek-r1-14b, gemma4-31b, gpt-oss-20b and qwen3.5-27b, plus tigerllm-9b with Bangla prompts. Cells need
    20+ questions.
  - Estimate: about 7 GPU hours in total.
- `src/dataset2/compare_routes.py` gained `--dataset` and `--items` (the defaults keep the Dataset 2 scoring
  unchanged; checked: the same output).

## GenreHalluEval routed notebook, second run (rerun by Mahdi, 2026-10-27; replication check, exploratory)

- Zip stored read-only: `runs/genrehallueval/genrehallueval__routed__full__outputs__rerun2.zip` (sha256 `64683549…`),
  run 17:35–19:41 UTC. The confirmatory result stays with the first run.
- **Checks, all passed:** the same as for run 2 (checksums, lock, prompt hashes rebuilt, digests, routes recomputed from
  lock v2, every routed answer has a verdict, no_answer 0 in judge calls, nothing truncated).
- **Compared with the first routed run:**
  - Genre answers: qwen3.5-27b and qwen2.5-32b were identical. The others differed on a few questions: deepseek 3 of
    75, gpt-oss 2 of 75, gemma2 1 of 75, gemma4 1 of 250.
  - **R chose the same judge for all 1,250 answers.** One verdict differs (d2-145__p2: gemma4-31b gave a different
    verdict on the same prompt).
  - F changed judges on 10 answers (d2-072, d2-074), because the genre answers changed.
  - Verdicts on the same (judge, answer): qwen3.5-27b 550 of 550 identical; gemma4-31b 919 of 920; deepseek-r1-14b
    3 of 5.
- **Scores with the rerun:**
  - R vs A with the passage: +0.29 (−0.07 to +0.71), Holm p 0.369, the same as the first run.
  - R vs A without the passage: +1.17 (−1.83 to +4.33), Holm p 0.473; the first run gave +1.00.
  - Neither difference is clear, as in the first run.
- **Cost:** 2,285 calls; 1,325,254 prompt tokens and 30,908 output tokens; wall time 2 h 06 min.

## GenreHalluEval split: learn run and lock (2026-10-27/28; exploratory)

- **Learn run:** `split_learn.ipynb`, full, one session, 17:30–21:49 UTC. Zip stored read-only:
  `runs/ghesplit/ghesplit_learn__learn__full__all__outputs.zip` (sha256 `ee3e7bc9…`).
- **Checks, all passed:**
  - the dataset checksums match the split package;
  - every model digest equals lock v2, including tigerllm-9b `d2b91a15…`;
  - TigerLLM ran with Bangla prompts and 16 new tokens per reply;
  - every model has 125 genre calls and 625 + 625 judge calls;
  - every prompt hash equals the rebuilt prompt (checked by `make_split_lock.py`);
  - nothing truncated (manifest, and 0 "truncating input" lines in the server logs).
- **no_answer:** deepseek-r1-14b 129 of 625 with the passage (21%; on BenHalluEval 16%) and 1 without it; gpt-oss-20b
  15 without the passage (capped while thinking). The other models had none.
- **Cost:** 6,875 calls; 2,614,676 prompt tokens and 488,088 output tokens; model busy time 14,257 s (deepseek 6,508
  s); wall time 4 h 19 min.
- **Lock:** `results/lock/lock_split_v1.json` (sha256 `2616eb9a…`), made by `src/split/make_split_lock.py` and copied
  into the package (the checksums and the Kaggle zip were rebuilt).
  - **With the passage:**
    - A = qwen3.5-27b (0.6 vs gemma4-31b 0.7 on the learn half); best genre guesser qwen3.5-27b.
    - Table: History qwen3.5, Arts gemma4, Science gemma4, Geography qwen3.5, Religion qwen3.5.
    - Most cells are 0.0 or 0.5–1.0, decided by 0–2 errors.
  - **Without the passage:**
    - A = gemma4-31b (23.0); best genre guesser qwen3.5-27b.
    - Table: History qwen3.5 39.5, Arts gemma4 31.0, Science gemma4 11.0, Geography gemma4 17.5, Religion qwen3.5
      13.0.
    - All 5 LLMs are askers, because History's 39.5 is high enough for many own-genre cells to beat it.
- **Next:** upload the new `release/kaggle-split/GenreHalluEval-split.zip` as a new version on Kaggle, then run
  `split_routed.ipynb` and `split_single_best.ipynb`.

## GenreHalluEval split: test-half runs and result (2026-10-28; exploratory)

- **Runs:**
  - routed 23:20–00:40 UTC; single best 23:22–23:49 UTC. Both ran on the package version with the lock (lock sha256
    `2616eb9a…` in both manifests).
  - The zips were re-packed on a Mac before they were sent (a top folder and `__MACOSX` files were added). They are
    stored as received, read-only: `runs/ghesplit/ghesplit_test__routed__full__all__outputs__mac_rezipped.zip`
    (`315acaef…`) and `…single_best…__mac_rezipped.zip` (`e69e4827…`).
- **Checks, all passed:**
  - dataset checksums and model digests match;
  - every prompt hash (English and Bangla) equals the rebuilt prompt;
  - every route equals an independent recomputation from lock_split_v1;
  - every routed answer has a verdict;
  - `no_answer` 0 in every judge call, and nothing truncated.
- **Genre answers on the test half** (agreement with our genre): qwen3.5-27b 94.4%, gemma4-31b 91.2%, deepseek-r1-14b
  72.6%, tigerllm-9b 72.6%, gpt-oss-20b 71.0%.
- **Result (`results/split_ghe/split_test_v1.md`):**
  - **With the passage:** A = qwen3.5-27b 0.79 vs R 0.40, −0.40 (−0.99 to +0.00), Holm p 0.25. That is 4 vs 2 misses.
  - **Without the passage:** A = gemma4-31b 19.76 vs R 24.19, **+4.44 (+1.21 to +8.27), Holm p 0.014: routing clearly
    worse.**
    - qwen3.5-27b, the learn-half winner for History and Religion, lost on the test half: 21 vs 18 errors in History
      and 13 vs 5 in Religion.
    - E, F and D were also worse without the passage.
- **Determinism:** 424 of 425 shared (judge, answer) pairs gave the same verdict.
- **Cost:**
  - routed: 1,176 calls; 657,077 prompt and 33,944 output tokens; 1 h 20 min;
  - single best: 625 calls; 156,506 prompt and 1,250 output tokens; 27 min.
- `compare_routes.py` now skips `__MACOSX` entries and ignores label rows for answers that are not in the scored items.
  The Dataset 2 scoring output is unchanged (checked).
- Per-genre tables are held until the 17-question genre relabel is in.

## GenreHalluEval v2 (12 single genres): package and notebooks built 2026-10-29 (no run yet)

- Decided by Mahdi (2026-10-28/29): 12 single genres (GRAMMAR added) with 100 questions each; routes learned and
  tested inside v2. Plan: `docs/genrehallueval-v2-plan.md`; progress log: `data/labels/genrehallueval_v2/PROGRESS.md`.
- **Questions:** 230 kept v1.1 questions (Claude's single-genre draft) + 970 written by Claude (current Bangla
  Wikipedia revisions; 88 GRAMMAR questions from the NCTB class 9-10 grammar book), each with 4 hallucinations.
- **Blind check (20%, `data/labels/genrehallueval_v2/check_v1/agreement_v1.md`):** Umme Zoayria Abedin and Md Saminul
  Amin; answers kappa 0.990 between them (969 answers; vs design 1.000 and 0.990, an upper bound); genre kappa 0.991
  (240 questions), vs the draft 0.973 / 0.982. Mahdi kept every drafted genre (2026-10-29).
- **Package:** `data/final/GenreHalluEval-v2.0/`, built by `src/genrehallueval_v2/build_v2.py` (seed 2026; a second
  build gives the same files). Split stratified by genre and origin: learn 600 questions (50 per genre; 6,000 judge
  rows per judge), test 600 (25 + 25 per genre with / without the passage). `learn_items.csv` sha256 `68236850…`,
  `test_items.csv` `f4361b6b…`, `pool.json` `63e98251…`. Labels (outside the package):
  `data/labels/genrehallueval_v2/labels_v2.0.csv` (v1.1 answers: agreed labels; new: design labels).
- **Fixed before any run (pool.json):** pool deepseek-r1-14b, gemma4-31b, gpt-oss-20b, qwen3.5-27b (English prompts)
  and tigerllm-9b (Bangla prompts, 16 new tokens); genre prompts `genre_v2` / `genre_bn_v2`; cells need 50+
  questions (golden rule 5); main tests R vs A and F vs A with and without the passage (Holm over 4).
- **Notebooks:** `ghe2_learn`, `ghe2_routed`, `ghe2_single_best` (`src/genrehallueval_v2/make_v2_notebooks.py`, the
  split notebooks with 12 genres); lock maker `src/genrehallueval_v2/make_lock_v2.py` (lock `lock_ghe2_v1.json`);
  scoring `compare_routes.py --dataset ghe2_test --main R,F` (new option `--main`; the default R keeps every earlier
  output unchanged). Local fake-model test `src/genrehallueval_v2/test_v2.sh` passes end to end.
- **Kaggle kit:** `release/kaggle-genrehallueval-v2/` (`HOW_TO_USE.md`).
- **Cost (estimate from the last split run, scaled by 4.8x and the longer genre prompt):** learn about 20 GPU hours
  in 3 sessions (deepseek-r1-14b about 9 h); routed about 6 h; single best about 2 h. About 28 GPU hours in all.
- **Before any run:** Mahdi freezes genre guide v2.0. No OSF registration for v2 (Mahdi, 2026-10-30).

## GenreHalluEval v2: learn run and lock (2026-10-29/30)

- **Learn run:** `ghe2_learn.ipynb`, full, three sessions started 2026-10-29 13:11–13:12 UTC:
  - deepseek-r1-14b alone, 13:11–23:02 (9 h 51 min);
  - gemma4-31b + tigerllm-9b, 13:12–17:51 (4 h 39 min);
  - qwen3.5-27b + gpt-oss-20b, 13:12–18:56 (5 h 44 min).
  Zips stored as received, read-only, in `runs/ghe2/` (sha256 `585c5177…`, `5498f12c…`, `a167511f…`); none was re-zipped.
- **Checks, all passed:**
  - every manifest is full, not partial, with 0 truncated prompts; 0 "truncating input" lines in the 5 server logs;
  - the dataset checksums in every manifest match the v2.0 package;
  - every model digest equals the one in lock_split_v1 (and so lock v2), including tigerllm-9b;
  - TigerLLM ran with `genre_bn_v2` / `judge_bn_v1` / `judge_noctx_bn_v1` and 16 new tokens;
  - every model has 600 genre calls and 3,000 + 3,000 judge calls, and every prompt hash equals the rebuilt prompt
    (checked by `make_lock_v2.py`);
  - the question and hallucination source files are unchanged since the package build (sha256 in `pool.json`).
- **no_answer:** deepseek-r1-14b 578 of 3,000 with the passage (19%), 11 without, 47 of 600 genre answers; gpt-oss-20b
  31 without the passage (capped while thinking) and 1 with it; tigerllm-9b 3 genre answers. The others had none.
- **Cost:** 33,000 calls; 13,738,209 prompt and 2,368,081 output tokens; model busy time 19.84 h (deepseek 9.78 h).
- **Lock:** `results/lock/lock_ghe2_v1.json` (sha256 `88da7af7…`), made by `src/genrehallueval_v2/make_lock_v2.py`
  from the learn half only, and copied into the package (checksums and Kaggle zip rebuilt). Cells 50+.
  - **With the passage:** A = gemma4-31b (0.33; qwen3.5-27b 0.88); best genre guesser gemma4-31b (94.7%). Table:
    gemma4-31b in 11 genres, qwen3.5-27b in Politics. Askers: gemma4-31b, qwen3.5-27b. Cells rest on 0–2 errors.
  - **Without the passage:** A = gemma4-31b (21.96; qwen3.5-27b 23.10); guesser gemma4-31b. Table: qwen3.5-27b in
    Politics, Education, Sports, Science, Technology and Geography; gemma4-31b in the other 6. Askers:
    deepseek-r1-14b, gemma4-31b, gpt-oss-20b, qwen3.5-27b.
  - Report (descriptive): `results/ghe2/learn_report_v1.md` (`src/genrehallueval_v2/learn_report.py`). Clear gaps
    between the best and the runner-up: Technology and Grammar with the passage, Culture and Places without it. No LLM is
    clearly better inside the genre it named itself than inside our genre.
- **Next:** upload the rebuilt `release/kaggle-genrehallueval-v2/GenreHalluEval-v2.zip` as a new version, then run
  `ghe2_routed.ipynb` and `ghe2_single_best.ipynb`.

## GenreHalluEval v2: test-half design (2026-10-30, after the lock, before any test run)

- Mahdi: no OSF for v2; one route per notebook, so each route's cost is measured on its own.
- Notebooks `ghe2_route_E`, `ghe2_route_F`, `ghe2_route_R`, `ghe2_single_best` (`make_v2_notebooks.py`); the combined
  `ghe2_routed` was never run and is in `release/kaggle-genrehallueval-v2/superseded/`.
- Route F asks every LLM with an own-genre cell (all 5 in both conditions); route R asks the lock's askers (with the
  passage gemma4-31b and qwen3.5-27b; without it also deepseek-r1-14b and gpt-oss-20b); route E asks only the guesser
  (gemma4-31b).
- `test_plan_v2.json` added to the package (sha256 `beab2a43…`; `src/genrehallueval_v2/add_test_plan.py`): main tests
  E vs A, F vs A, R vs A per condition, Holm over 6. It replaces the 4 tests in `pool.json`. The package checksums and
  the Kaggle zip were rebuilt; the lock is unchanged (`88da7af7…`).
- Scoring `src/genrehallueval_v2/compare_v2.py` (also recomputes every route from the lock and checks determinism).
  The local fake-model test (`test_v2.sh`) passes: 0 route differences, determinism 100%.
- Estimates: route E 2–3 h, F 4–5 h, R 3–4 h, A 1–2 h; about 12 GPU hours in all.

## GenreHalluEval v2: test half, routes F and R, and the final result (2026-10-30)

- **Runs:** `ghe2_route_F` 06:31–11:11 UTC; `ghe2_route_R` 06:32–09:54 UTC. Zips stored as received, read-only:
  `runs/ghe2/ghe2_test__route_F__full__all__outputs.zip` (sha256 `2085c0f1…`) and `…route_R…` (`c1aba473…`).
- **Checks, all passed:** full runs, not partial, nothing truncated (manifests and 9 server logs); lock and package
  checksums match; model digests equal to the learn run; every route of all four notebooks equals an independent
  recomputation from the lock (0 differences); every routed answer has a verdict.
- **no_answer:** route F 1 with the passage and 3 without (deepseek-r1-14b and gpt-oss-20b); genre answers: deepseek
  52 of 600 (F) and 28 of 300 (R), tigerllm 9 of 600. Routes E, R and A: 0 in the verdicts.
- **Result (`results/ghe2/test_v1.md`; 6 main tests, Holm over 6):**

  | Test | With the passage | Without the passage |
  |---|---|---|
  | E vs A | 0.21 vs 0.29, −0.08 (−0.21 to +0.00), Holm p 1.00 | 20.96 vs 21.17, −0.21 (−1.88 to +1.46), Holm p 1.00 |
  | F vs A | 4.38 vs 0.29, **+4.08 (+2.71 to +5.67), Holm p < 0.001: clearly worse** | 24.54 vs 21.17, **+3.38 (+1.33 to +5.46), Holm p 0.006: clearly worse** |
  | R vs A | 0.21 vs 0.29, −0.08 (−0.21 to +0.00), Holm p 1.00 | 21.67 vs 21.17, +0.50 (−1.33 to +2.29), Holm p 1.00 |

  No route beats A. F is clearly worse in both conditions. E and R are no different from A.
- **Why F fails:** a judge needs an own-genre cell of 50+ learn questions. gemma4-31b and qwen3.5-27b have no cell for
  Geography, Culture or Religion (they named those genres for fewer than 50 learn questions), so F sends those
  answers to the only LLM that has a cell: Geography mostly to tigerllm-9b (with the passage BHS 24.0 vs A's 0.0),
  Culture to gpt-oss-20b, Religion partly to gpt-oss-20b and tigerllm-9b. F never compares a cell with A; R does,
  which is why R stays close to A.
- **Determinism:** 3,258 of 3,270 shared (judge, answer) pairs gave the same verdict (99.63%); the flips have
  identical prompts (GPU batching).
- **Cost of each route (calls; prompt tokens; wall time):** A 3,000; 0.55 M; 1 h 22 min. E 3,600; 1.46 M; 2 h 10 min.
  R 4,800; 3.59 M; 3 h 22 min. F 6,000; 5.74 M; 4 h 39 min. Routing costs 1.2–2× the calls and 2.7–10× the prompt
  tokens of A, for no gain.
- **Conclusion:** the same answer as the registered v1.1 test and both split experiments. Fine, balanced genres (12 x
  100) do not make genre routing beat the single best judge.

## GenreHalluEval v2: test half, route E and single best A (2026-10-30; F and R pending)

- **Runs:** `ghe2_route_E` 06:27–08:37 UTC; `ghe2_single_best` 06:56–08:18 UTC. Zips stored as received, read-only:
  `runs/ghe2/ghe2_test__route_E__full__all__outputs.zip` (sha256 `91dda6f8…`) and
  `…single_best…` (`4afbc257…`); not re-zipped.
- **Checks, all passed:** full runs, not partial, 0 truncated prompts and 0 truncation lines in the server logs; lock
  `88da7af7…` and the package checksums (including `test_plan_v2.json`) in both manifests; model digests equal to the
  learn run; every route equals an independent recomputation from the lock; every routed answer has a verdict;
  no_answer 0 everywhere.
- **Route E:** gemma4-31b named every genre (94.0% agreement with ours); judges with the passage gemma4-31b 1,375 and
  qwen3.5-27b 125 (Politics); without it gemma4-31b 760 and qwen3.5-27b 740.
- **Interim result (`results/ghe2/test_v1_interim_E.md`; final Holm over 6 needs F and R):**
  - with the passage: E 0.21 vs A 0.29, −0.08 (−0.21 to +0.00), p 0.26;
  - without it: E 20.96 vs A 21.17, −0.21 (−1.88 to +1.46), p 0.85;
  - so far no clear difference. The p × 6 bound is 1.0 for both.
- **Determinism:** 2,129 of 2,135 shared (gemma4-31b, answer) pairs gave the same verdict (99.72%). The 6 flips are
  all without the passage, with identical prompts (GPU batching); 4 of them favour E and 2 favour A, so part of E's
  −0.21 is this noise.
- **Cost:** A 3,000 judge calls (548,460 prompt tokens; 1 h 22 min wall); E 600 genre + 3,000 judge calls (1,457,862
  prompt tokens; 2 h 10 min wall).

## Preview, 2026-10-18: routing methods A, C, E, F on BenHalluEval (exploratory, not locked)

- **Script:** `src/routing/preview_methods.py`, with the plan's rules: cells under 50 questions are not used,
  ties go to the better overall judge, and empty cells fall back to A.
- **Scoring:** on the same data (in-sample, optimistic) and with 5-fold cross-validation by question.
- **Output:** `results/routing_preview.csv`, and `routing_preview_without_top2.csv` for the pool without gemma4
  and qwen3.5.

**Change in BHS against A, the single best judge** (negative = better):

| Pool | Condition | E in-sample | E 5-fold | F in-sample | F 5-fold | C (vote of all) |
|---|---|---|---|---|---|---|
| All judges (A = gemma4) | with passage | −0.08 | +0.01 | +0.08 | +0.15 | **+1.54, clearly worse** |
| All judges (A = gemma4) | without passage | −0.46 | +0.71 | −0.45 | +0.41 | −0.19 |
| Without the top 2 (A = gemma2 / qwen2.5) | with passage | −0.05 | +0.42 | +0.05 | +0.33 | **+2.40, clearly worse** |
| Without the top 2 (A = gemma2 / qwen2.5) | without passage | −0.62 | +0.43 | −0.27 | +0.58 | **−1.29, clearly better** |

**Readings:**
- **No routing method clearly beats A anywhere.** The small in-sample gains for E and F become small losses under
  5-fold, which points to overfitting.
- F mostly picks the overall best judge. With all judges it routes 706–805 of 920 questions to gemma4 with the
  passage, and 486–498 without.
- The only clear gain: **voting** among comparable judges without the passage (−1.3). With the passage, voting
  clearly hurts.

## B5: `llama3.1-8b` with Bangla prompts (the matched reference), 2026-10-19

**Run facts:**
- Ollama **0.40.5**, digest `46e0c10c039e…`, both identical to R1 as planned, so only the prompt language differs.
- 1 h 33 min. 10,120 calls, all `ok`, 0 truncated (longest prompt 13,021 tokens; context window 15,360).
- `no_answer`: 19 replies with the passage, where it replied with a name or title instead of a verdict.
- Files: `results/bangla_prompts/llama3.1-8b/full/`; dataset `…/llamainbangla`.

**Result: the Bangla prompt makes llama much WORSE as a judge.**

| | English | Bangla | Change (paired range) |
|---|---|---|---|
| BHS with passage | 36.7 | **66.5** | **+29.8 (+27.7 to +31.7)** |
| Says "yes" to correct / hallucinated answers, with passage | 13% / 40% | **62% / 29%** | the signal flips |
| BHS without passage | 46.0 | 50.7 | +4.7 (+3.2 to +6.2) |
| Says "yes", without passage | 40% | 6% | almost always "না" |
| Genre accuracy (kappa; blind 200) | 73.4% (0.63; 0.60) | **81.1% (0.75; 0.70)** | **better** |

- With the passage, llama answers হ্যাঁ more often to **correct** answers than to hallucinated ones: BHS above 50
  means a reversed signal. It seems to read the Bangla question as "is the answer right?".
- Without the passage it says না to nearly everything.
- Its **genre guessing improves** with the Bangla genre prompt; History over-use drops from 513 to 386.

**Reading, as fixed before the result:** the gain is **specific to the Bangla-centric model.** It is not just
"specific": the Bangla prompt **hurts** a multilingual judge of the same strength. So prompt language interacts with
the model, as a crossover:
- TigerLLM: −4.8 without the passage;
- llama: +29.8 with the passage and +4.7 without.

**The Bangla-prompt side experiment is complete (B1–B5).** Summary: `results/bangla_prompts/summary.md`.

## B4: `titullm-3b-instruct` with Bangla prompts (side experiment), 2026-10-18

**Run facts:**
- Same model and revision as R10 (`6a9600483daf`); transformers 4-bit; 4 h 20 min.
- 10,120 calls, all `ok`, none too long (longest 3,484 tokens).
- Files: `results/bangla_prompts/titullm-3b-instruct/full/`; dataset `…/bangla-judgea`.
- Mahdi first attached the base model's zip by mistake. The instruct zip was imported instead (the manifests were
  checked).

**Result: the Bangla prompt fixes the format but not the judging.**

| | English prompt (R10) | Bangla prompt |
|---|---|---|
| Usable verdicts, with / without passage | 0% / 0% | **75% / 94%** |
| BHS, official (`no_answer` = error) | 100 / 100 | 62.6 / 52.5 |
| **BHS on answered items only** | – | **50.1 / 49.5 (chance)** |
| Says "হ্যাঁ" (yes) | – | **99% / 79%** |
| Genre accuracy (kappa) | 0% (0.00) | 26% (0.09): answers "ইতিহাস" 522 of 590 times |

- Under the Bangla prompt it **does** reply "হ্যাঁ" or "না" (3,409 and 37 replies with the passage). But it says yes
  to almost everything, so it judges at chance.
- For genre it picks the **first option in the list** (ইতিহাস), a strong position bias, the same direction as the
  HISTORY over-use of the weaker English-prompt models.

**The pattern across the Bangla-centric models:**

| Model | English → Bangla prompt |
|---|---|
| TigerLLM | follows the format in both; **judges better** without the passage (−4.8) |
| TituLLM-instruct | format fixed (0% → 75–94% verdicts), judging still at chance |
| BanglaLLaMA, TituLLM base | neither |

So the prompt language helps format-following first and judging only for a model that can already judge.

## Decision, 2026-10-18 (before any result): Bangla-prompt reference run

- **What:** run `llama3.1-8b` in `benchmark_bangla_prompts.ipynb` as the **matched reference** for the
  Bangla-prompt side experiment.
- **Why this model:** it is a non-Bangla-centric judge of the same strength and with the same lenient "no" bias
  as TigerLLM (English: 36.7 / 46.0 vs 38.8 / 44.8).
- **Setup:** `OLLAMA_VERSION = "0.40.5"` for this run only, to match llama's English run (R1), so that only the
  prompt language differs.
- **Reading, fixed now:**
  - If llama improves about as much as TigerLLM without the passage (about −5 BHS): Bangla prompts help judges
    in general.
  - If it changes little (within about ±2): the gain is specific to the Bangla-centric model.
  - Anything in between is reported as it is.
- Also running: `titullm-3b-instruct` with Bangla prompts.
- qwen3.5-27b as a second reference: optional, not decided.

## B3: `titullm-3b` (the paper's base model) with Bangla prompts (side experiment), 2026-10-18

**Run facts:**
- Same GGUF as R4 (digest `78a9cab00c64…`), Ollama 0.40.6 pinned. 1 h 14 min.
- 10,120 calls, all `ok`, 0 truncated.
- Bangla is token-expensive for this model's Llama-3.2 tokenizer: the longest prompt was 13,019 tokens, so the
  context window was set to 15,360.
- Files: `results/bangla_prompts/titullm-3b/full/`; dataset `…/bangla-judgea`.
- This is the **base** model, not `titullm-3b-instruct`. The instruct model's Bangla-prompt run is still pending.

**Result: no usable verdicts, the same failure as in English (R4).** Every reply restates the start of the prompt
and stops at the 16-token limit:
- judge: "আপনি একজন ম[ূল্যায়নকারী]…" (*You are an evaluator…*), 4,300 of 4,600;
- genre: "আপনি বাংলা ক[ুইজ]…" (*You are … Bangla quiz…*), 920 of 920.

Strict and lenient parses are both 100% `no_answer`. A base model continues text in any language; the prompt
language cannot help it.

## B2: `banglallama-13b` with Bangla prompts (side experiment), 2026-10-18

**Run facts:**
- Same merged model as R9 (LoRA merge again, 6 min). About 3 h 50 min in all.
- Prompt fingerprints match ours.
- 10,120 calls. One genre prompt (4,324 tokens) was longer than the 4,096-token context: skipped, never cut,
  counted as `no_answer`.
- Files: `results/bangla_prompts/banglallama-13b/full/`; dataset `…/bangla-judge-runb`.

**Result: still no usable verdicts (100% `no_answer` under the strict parse).** The replies are Bangla sentences,
not a bare হ্যাঁ/না:
- With passage: "প্রসঙ্গ এবং প্রশ্নের মধ্যে কোনো সংযোগ নে[ই]" (*there is no connection between the passage and the
  question*) 1,343 times, and "না, …" followed by an explanation.
- Without passage: "না, …" followed by an explanation, almost every time.
- Genre: it explains instead of naming a genre.

**Diagnostic (lenient reading, first হ্যাঁ/না word anywhere):**
- With passage: 77% still have no verdict; BHS 88.3.
- Without passage: always "না"; BHS 50.2.

**So the Bangla prompt does not rescue BanglaLLaMA.** With the English prompt it at least wrote "উত্তর: না/হ্যাঁ";
with the Bangla prompt it misreads the task. It cannot judge in either language.

## B1: `tigerllm-9b` with Bangla prompts (side experiment), 2026-10-18

**Run facts:**
- Notebook `benchmark_bangla_prompts.ipynb`. Prompt fingerprints `0f06339ba9b8` (genre), `f59b056def8e`
  (with passage) and `a57d643a6502` (without passage); they match our files.
- Same model and digest as R5 (`d2b91a15fc7e…`). Ollama 0.40.6, pinned. Up to 16 new tokens per reply.
- 2 h 16 min: genre 53 min, judge with passage 54 min, judge without passage 25 min.
- 10,120 calls, all `ok`, 0 truncated. `no_answer`: 1 genre reply ("ভাষা", *language*), 0 judge replies.
- Files: `runs/benhallueval__tigerllm-9b__*_bn_v1.jsonl`; `results/bangla_prompts/tigerllm-9b/full/`; the
  comparison in `results/bangla_prompts/comparison.md`. Uploaded to the separate dataset `…/bangla-judgea`.

**English vs Bangla prompts, same 4,600 answers** (paired ranges):

| | English | Bangla | Change |
|---|---|---|---|
| BHS with passage | 38.8 | 37.4 | −1.5 (−3.0 to +0.2), not clear |
| **BHS without passage** | 44.8 | **40.0** | **−4.8 (−6.4 to −3.3), clearly better** |
| Says "yes" (with / without passage) | 32% / 20% | 45% / 53% | less lenient |
| Same verdict (with / without passage) | | | 78% / 64% |
| Genre accuracy (kappa; blind 200) | 76.8% (0.69; 0.66) | 75.8% (0.68; 0.65) | no change |

- Without the passage, **every genre improves** with the Bangla prompt: Science by 9.1, History, Arts and
  Religion by about 4.5, Geography by 1.0.
- Most of the gain comes from saying "yes" more often, so it misses fewer hallucinations. Its strong "no" bias
  shrinks.
- **Open question:** does the Bangla prompt help every judge, or only Bangla-centric ones? Running
  `qwen3.5-27b` with Bangla prompts as a reference would answer it.

## Note, 2026-10-18: Bangla-prompt side experiment

**Decided 2026-10-18, after the English results, so it is exploratory.** Run the Bangla-centric judges
(`tigerllm-9b`, `banglallama-13b`, `titullm-3b-instruct`; optional reference `qwen3.5-27b`) with Bangla
prompts. The question: is the prompt language why they fail?

- **Tool:** `notebooks/benchmark_bangla_prompts.ipynb`, built by `src/bench/make_notebook_bangla.py` from the
  main notebook.
- **Prompts:** `genre_bn_v1`, `judge_bn_v1`, `judge_noctx_bn_v1`. They are Claude's translations; Mahdi checks
  them first.
- **Separate outputs:** run files `…__judge_bn_v1.jsonl`, tables in `results/bangla_prompts/`, zip
  `<model>__bnprompt__…`.
- **Tested locally:** with a fake Bangla-replying model, pilot plus full resume.
- **Golden rule 1 check:** made precise. A leak now means the answer appears in the genre prompt more often than
  the guide, question and passage explain. Before, 15 common Bangla words in the guide, such as উৎসব and
  রামায়ণ, raised false alarms. The new check is also stricter: it checks answers that appear in the passage too.

## Not run yet

- BenHalluEval: models 2–12 above (genre and both judge conditions).
- Pilots: none run so far.
- The Ollama check for R1: a llama3.1-8b pilot on 0.40.6 (440 calls, about 5 min), compared with R1. Not run yet.
- The routing notebook (methods A–K, 5-fold checkpoint, lock): after all models.
- Dataset 2: not built.
