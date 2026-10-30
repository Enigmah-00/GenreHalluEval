# Overview of all judge runs (BenHalluEval-QA v1.3)

Built 2026-10-19 by `src/bench/overview.py` from `results/<model>/full/`. Models so far: 12 of 12 (banglallama-13b, deepseek-r1-14b, gemma2-27b, gemma4-31b, gpt-oss-20b, llama3.1-8b, mistral-nemo-12b, qwen2.5-32b, qwen3.5-27b, tigerllm-9b, titullm-3b, titullm-3b-instruct). Details of each run: `docs/runlog.md`.

BHS: lower is better; 50 = chance. Ranges are 95% from re-sampling questions. This page describes; it chooses
nothing. All choices are made and locked in the routing notebook after every model is in.

## 0. Routing at a glance (all judges, both conditions)

For each of our genres: the judge with the lowest BHS in **our** genre (routing E/D), the runner-up and
whether its gap is clear; the judge with the lowest BHS in the genre it **named itself** (routing F; only
cells with 50+ questions) and how that judge does in its own genre vs ours; every judge that is clearly
better in its own genre (paired 95% range below 0); and the best overall judge (A) for comparison.
Judges with no usable verdicts are left out. Exploratory: the locked choices are in `results/lock/`.
A label depends on the 95% range, not on the size of the difference: a small difference with a narrow
range can be 'below 0' while a larger one with a wide range is not. About 86 own-vs-ours comparisons are
made, so about 2 'below 0' results are expected by chance alone; none stays below 0 after a Holm
correction. Treat single 'below 0' cells as hints to re-test on Dataset 2, not as findings.

| condition | genre | questions | route_by_our_genre | runner_up | route_by_own_genre | own_minus_ours_for_that_judge | same_judge | judges_clearly_better_in_own_genre | best_overall_judge_here |
|---|---|---|---|---|---|---|---|---|---|
| with passage | HISTORY | 290 | gemma4-31b 1.03 | qwen3.5-27b 1.85 (+0.82, clear) | gemma4-31b 1.05 (285) | +0.02 (range includes 0: -0.02 to +0.07) | yes | qwen2.5-32b (-0.78; -1.44 to -0.25) | gemma4-31b 1.03 |
| with passage | ARTS | 278 | qwen3.5-27b 1.62 | gemma4-31b 1.66 (+0.04, not clear) | gemma4-31b 1.64 (282) | -0.02 (range includes 0: -0.08 to +0.02) | no | none | gemma4-31b 1.66 |
| with passage | SCIENCE | 135 | gemma4-31b 2.04 | qwen3.5-27b 2.69 (+0.65, not clear) | gemma4-31b 1.82 (144) | -0.21 (own better, range below 0: -0.46 to -0.04) | yes | gemma4-31b (-0.21; -0.46 to -0.04), qwen3.5-27b (-0.24; -0.47 to -0.06) | gemma4-31b 2.04 |
| with passage | GEOGRAPHY | 110 | gemma4-31b 0.23 | qwen3.5-27b 0.80 (+0.57, not clear) | gemma4-31b 0.37 (101) | +0.14 (range includes 0: +0.00 to +0.43) | yes | none | gemma4-31b 0.23 |
| with passage | RELIGION | 95 | qwen3.5-27b 1.97 | gemma4-31b 2.76 (+0.79, not clear) | qwen3.5-27b 1.53 (98) | -0.44 (range includes 0: -1.72 to +0.45) | yes | none | gemma4-31b 2.76 |
| with passage | OTHER | 12 | gemma4-31b 0.00 (under 50 questions: A) | qwen3.5-27b 1.04 (+1.04, not clear) | – (no judge named it 50+ times; falls back to gemma4-31b) | – | yes | none | gemma4-31b 0.00 |
| without passage | HISTORY | 290 | qwen3.5-27b 31.29 | gemma4-31b 32.20 (+0.91, not clear) | qwen3.5-27b 30.92 (287) | -0.37 (range includes 0: -1.20 to +0.50) | yes | none | gemma4-31b 32.20 |
| without passage | ARTS | 278 | gemma4-31b 36.74 | qwen3.5-27b 38.53 (+1.80, not clear) | gemma4-31b 36.61 (282) | -0.12 (range includes 0: -0.86 to +0.63) | yes | none | gemma4-31b 36.74 |
| without passage | SCIENCE | 135 | gemma4-31b 26.48 | qwen3.5-27b 27.78 (+1.30, not clear) | gemma4-31b 26.48 (144) | -0.01 (range includes 0: -1.08 to +1.10) | yes | none | gemma4-31b 26.48 |
| without passage | GEOGRAPHY | 110 | gemma4-31b 27.05 | deepseek-r1-14b 31.93 (+4.89, clear) | gemma4-31b 26.36 (101) | -0.68 (range includes 0: -2.18 to +0.89) | yes | none | gemma4-31b 27.05 |
| without passage | RELIGION | 95 | qwen3.5-27b 28.42 | gemma4-31b 30.26 (+1.84, not clear) | qwen3.5-27b 28.70 (98) | +0.28 (range includes 0: -1.24 to +1.98) | yes | none | gemma4-31b 30.26 |
| without passage | OTHER | 12 | gemma4-31b 32.29 (under 50 questions: A) | qwen3.5-27b 34.38 (+2.08, not clear) | – (no judge named it 50+ times; falls back to gemma4-31b) | – | yes | none | gemma4-31b 32.29 |

Whole-set view: sending each genre to its best judge (same data, optimistic) gives with passage 1.44 → 1.35; without passage 31.92 → 31.44. The honest 5-fold check is in `results/routing_preview.csv`.

## 1. Judges

| model | pool | BHS_context | range95_context | BHS_no_context | range95_no_context | passage_gain | trackA_context | trackB_context | trackA_no_context | trackB_no_context |
|---|---|---|---|---|---|---|---|---|---|---|
| banglallama-13b | open | 100.00 | 100.00 to 100.00 | 100.00 | 100.00 to 100.00 | 0.00 (0.00 to 0.00) | 100.00 | 100.00 | 100.00 | 100.00 |
| deepseek-r1-14b | open | 22.76 | 21.18 to 24.59 | 38.29 | 36.67 to 39.92 | 15.53 (13.25 to 17.84) | 22.72 | 22.80 | 48.15 | 28.42 |
| gemma2-27b | open | 6.10 | 5.45 to 6.79 | 38.18 | 36.96 to 39.48 | 32.08 (30.62 to 33.44) | 1.63 | 10.57 | 16.52 | 59.84 |
| gemma4-31b | open | 1.44 | 0.95 to 1.94 | 31.92 | 30.54 to 33.44 | 30.48 (28.98 to 32.11) | 2.28 | 0.60 | 29.67 | 34.16 |
| gpt-oss-20b | open | 7.08 | 6.15 to 8.03 | 39.76 | 38.33 to 41.21 | 32.68 (30.94 to 34.43) | 6.63 | 7.53 | 57.39 | 22.12 |
| llama3.1-8b | open | 36.71 | 35.41 to 38.03 | 45.98 | 44.71 to 47.28 | 9.27 (7.49 to 11.06) | 13.04 | 60.38 | 33.59 | 58.37 |
| mistral-nemo-12b | open | 49.65 | 47.98 to 51.26 | 50.75 | 49.81 to 51.71 | 1.10 (-0.77 to 3.00) | 42.93 | 56.36 | 84.46 | 17.04 |
| qwen2.5-32b | open | 9.86 | 9.04 to 10.75 | 37.43 | 36.17 to 38.75 | 27.57 (26.13 to 29.14) | 3.15 | 16.58 | 22.07 | 52.80 |
| qwen3.5-27b | open | 1.78 | 1.33 to 2.23 | 32.85 | 31.56 to 34.10 | 31.07 (29.77 to 32.40) | 1.41 | 2.15 | 19.89 | 45.82 |
| tigerllm-9b | open | 38.82 | 37.23 to 40.39 | 44.80 | 43.74 to 45.90 | 5.98 (4.20 to 7.76) | 14.57 | 63.07 | 11.63 | 77.96 |
| titullm-3b | open | 100.00 | 100.00 to 100.00 | 100.00 | 100.00 to 100.00 | 0.00 (0.00 to 0.00) | 100.00 | 100.00 | 100.00 | 100.00 |
| titullm-3b-instruct | open | 100.00 | 100.00 to 100.00 | 100.00 | 100.00 to 100.00 | 0.00 (0.00 to 0.00) | 100.00 | 100.00 | 100.00 | 100.00 |

- trackA = correct answers flagged as hallucinated (%); trackB = hallucinations missed (%).
- passage_gain = BHS without the passage − BHS with it (paired; positive = the passage helps).
- Reference: the rule "hallucinated if the answer is not a passage span" scores **13.8** with the passage.
- **No usable verdicts:** banglallama-13b, titullm-3b, titullm-3b-instruct. Over half of the replies were not yes/no, so BHS is 100 by construction (every no_answer counts as an error on both tracks). Never routed to; report separately.

| model | span_BHS_context | span_BHS_no_context | paper_BHS | no_answer_context | no_answer_no_context | calls | tokens_in_M | session_h | version | date |
|---|---|---|---|---|---|---|---|---|---|---|
| banglallama-13b | 100.00 | 100.00 | 48.62 | 4600 | 4600 | 10120 | 3.34 | 2.73 | hf revision a5986f8599cd749ab4e8a2afb068b881493dac28 | 2026-10-18 |
| deepseek-r1-14b | 25.03 | 33.66 | 38.6 | 745 | 7 | 10120 | 5.94 | 3.23 | ollama 0.40.6 | 2026-10-18 |
| gemma2-27b | 7.50 | 30.14 | 47.45 | 0 | 0 | 10120 | 3.94 | 3.77 | ollama 0.40.6 | 2026-10-17 |
| gemma4-31b | 1.73 | 25.60 | – | 0 | 0 | 10120 | 2.7 | 5.53 | ollama 0.40.6 | 2026-10-18 |
| gpt-oss-20b | 7.15 | 36.51 | – | 13 | 79 | 10120 | 4.53 | 5.16 | ollama 0.40.6 | 2026-10-17 |
| llama3.1-8b | 48.02 | 47.87 | 47.71 | 0 | 0 | 10120 | 6.57 | 1.5 | ollama 0.40.5 | 2026-10-17 |
| mistral-nemo-12b | 59.03 | 53.00 | 53.84 | 0 | 0 | 10120 | 4.08 | 0.94 | ollama 0.40.6 | 2026-10-17 |
| qwen2.5-32b | 20.95 | 32.32 | 46.85 | 0 | 0 | 10120 | 6.2 | 3.53 | ollama 0.40.6 | 2026-10-17 |
| qwen3.5-27b | 2.97 | 27.64 | – | 0 | 0 | 10120 | 3.77 | 4.22 | ollama 0.40.6 | 2026-10-17 |
| tigerllm-9b | 47.94 | 47.31 | 28.28 | 0 | 0 | 10120 | 2.66 | 1.83 | ollama 0.40.6 | 2026-10-17 |
| titullm-3b | 100.00 | 100.00 | 50.0 | 4600 | 4600 | 10120 | 6.69 | 0.89 | ollama 0.40.6 | 2026-10-17 |
| titullm-3b-instruct | 100.00 | 100.00 | – | 4600 | 4600 | 10120 | 2.93 | 2.83 | hf revision 6a9600483daf9a3af7494e7fa91f2e72e2799b96 | 2026-10-18 |

- span_BHS = BHS on the answers copied from the passage (920 golds + 1,017 hallucinations); the span rule is
  useless there. paper_BHS = the paper's QA score for the same model, on its own (GPT-5.4) hallucinations.

## 2. Genre guessing (against our human-verified genres)

| model | accuracy | macro_F1 | kappa | kappa_range95 | kappa_blind200 | no_answer |
|---|---|---|---|---|---|---|
| banglallama-13b | 0.0 | 0.000 | 0.000 | 0.000 to 0.000 | 0.000 | 920 |
| deepseek-r1-14b | 83.7 | 0.729 | 0.783 | 0.751 to 0.813 | 0.739 | 0 |
| gemma2-27b | 81.5 | 0.771 | 0.752 | 0.719 to 0.783 | 0.707 | 0 |
| gemma4-31b | 93.8 | 0.870 | 0.919 | 0.898 to 0.937 | 0.805 | 0 |
| gpt-oss-20b | 80.0 | 0.687 | 0.732 | 0.698 to 0.762 | 0.715 | 1 |
| llama3.1-8b | 73.4 | 0.633 | 0.634 | 0.592 to 0.668 | 0.603 | 0 |
| mistral-nemo-12b | 69.8 | 0.614 | 0.584 | 0.544 to 0.619 | 0.596 | 0 |
| qwen2.5-32b | 91.8 | 0.848 | 0.893 | 0.869 to 0.917 | 0.799 | 0 |
| qwen3.5-27b | 95.0 | 0.906 | 0.934 | 0.915 to 0.952 | 0.798 | 0 |
| tigerllm-9b | 76.8 | 0.727 | 0.689 | 0.652 to 0.723 | 0.656 | 1 |
| titullm-3b | 0.0 | 0.000 | 0.000 | 0.000 to 0.000 | 0.000 | 920 |
| titullm-3b-instruct | 0.0 | 0.000 | 0.000 | 0.000 to 0.000 | 0.000 | 920 |

How many questions each model put in each genre (ours: HISTORY 290, ARTS 278, SCIENCE 135, GEOGRAPHY 110, RELIGION 95, OTHER 12):

| model | named_HISTORY | named_ARTS | named_SCIENCE | named_GEOGRAPHY | named_RELIGION | named_OTHER |
|---|---|---|---|---|---|---|
| banglallama-13b | 0 | 0 | 0 | 0 | 0 | 0 |
| deepseek-r1-14b | 356 | 263 | 135 | 95 | 67 | 4 |
| gemma2-27b | 439 | 205 | 113 | 82 | 75 | 6 |
| gemma4-31b | 285 | 282 | 144 | 101 | 94 | 14 |
| gpt-oss-20b | 367 | 282 | 111 | 97 | 55 | 7 |
| llama3.1-8b | 513 | 214 | 76 | 70 | 40 | 7 |
| mistral-nemo-12b | 500 | 233 | 72 | 86 | 25 | 4 |
| qwen2.5-32b | 301 | 268 | 139 | 101 | 93 | 18 |
| qwen3.5-27b | 287 | 287 | 143 | 97 | 98 | 8 |
| tigerllm-9b | 474 | 182 | 96 | 91 | 59 | 17 |
| titullm-3b | 0 | 0 | 0 | 0 | 0 | 0 |
| titullm-3b-instruct | 0 | 0 | 0 | 0 | 0 | 0 |

## 3a. Judge × genre, WITH the passage

Run 1, by **our** genre (the routing table for methods D and E). Cells: BHS (questions); † = under 50
questions, never used for routing.

| model | HISTORY | ARTS | SCIENCE | GEOGRAPHY | RELIGION | OTHER |
|---|---|---|---|---|---|---|
| banglallama-13b | 100.00 (290) | 100.00 (278) | 100.00 (135) | 100.00 (110) | 100.00 (95) | 100.00 (12) † |
| deepseek-r1-14b | 23.15 (290) | 20.32 (278) | 23.80 (135) | 23.41 (110) | 24.08 (95) | 41.67 (12) † |
| gemma2-27b | 5.78 (290) | 5.71 (278) | 6.85 (135) | 5.45 (110) | 7.50 (95) | 9.38 (12) † |
| gemma4-31b | 1.03 (290) | 1.66 (278) | 2.04 (135) | 0.23 (110) | 2.76 (95) | 0.00 (12) † |
| gpt-oss-20b | 6.47 (290) | 8.14 (278) | 6.20 (135) | 5.91 (110) | 8.16 (95) | 9.38 (12) † |
| llama3.1-8b | 35.56 (290) | 37.72 (278) | 39.07 (135) | 34.43 (110) | 36.84 (95) | 34.38 (12) † |
| mistral-nemo-12b | 48.66 (290) | 51.53 (278) | 52.13 (135) | 42.84 (110) | 49.74 (95) | 63.54 (12) † |
| qwen2.5-32b | 11.12 (290) | 9.98 (278) | 10.28 (135) | 6.48 (110) | 8.82 (95) | 11.46 (12) † |
| qwen3.5-27b | 1.85 (290) | 1.62 (278) | 2.69 (135) | 0.80 (110) | 1.97 (95) | 1.04 (12) † |
| tigerllm-9b | 38.32 (290) | 39.66 (278) | 38.80 (135) | 32.95 (110) | 44.08 (95) | 43.75 (12) † |
| titullm-3b | 100.00 (290) | 100.00 (278) | 100.00 (135) | 100.00 (110) | 100.00 (95) | 100.00 (12) † |
| titullm-3b-instruct | 100.00 (290) | 100.00 (278) | 100.00 (135) | 100.00 (110) | 100.00 (95) | 100.00 (12) † |

Run 2, by the genre **each model named itself** (the {LLM, genre} pairs for method F).

| model | HISTORY | ARTS | SCIENCE | GEOGRAPHY | RELIGION | OTHER |
|---|---|---|---|---|---|---|
| banglallama-13b | – (0) † | – (0) † | – (0) † | – (0) † | – (0) † | – (0) † |
| deepseek-r1-14b | 23.21 (356) | 21.48 (263) | 25.09 (135) | 20.26 (95) | 24.44 (67) | 18.75 (4) † |
| gemma2-27b | 5.47 (439) | 6.34 (205) | 7.63 (113) | 5.79 (82) | 7.50 (75) | 2.08 (6) † |
| gemma4-31b | 1.05 (285) | 1.64 (282) | 1.82 (144) | 0.37 (101) | 2.26 (94) | 3.57 (14) † |
| gpt-oss-20b | 6.98 (367) | 7.49 (282) | 7.09 (111) | 6.06 (97) | 7.05 (55) | 10.71 (7) † |
| llama3.1-8b | 35.23 (513) | 38.67 (214) | 37.50 (76) | 38.57 (70) | 41.56 (40) † | 30.36 (7) † |
| mistral-nemo-12b | 48.52 (500) | 53.27 (233) | 52.78 (72) | 44.33 (86) | 46.50 (25) † | 56.25 (4) † |
| qwen2.5-32b | 10.34 (301) | 10.12 (268) | 10.34 (139) | 6.93 (101) | 9.68 (93) | 11.81 (18) † |
| qwen3.5-27b | 1.83 (287) | 1.79 (287) | 2.45 (143) | 0.90 (97) | 1.53 (98) | 1.56 (8) † |
| tigerllm-9b | 37.71 (474) | 43.41 (182) | 39.32 (96) | 31.73 (91) | 43.22 (59) | 39.71 (17) † |
| titullm-3b | – (0) † | – (0) † | – (0) † | – (0) † | – (0) † | – (0) † |
| titullm-3b-instruct | – (0) † | – (0) † | – (0) † | – (0) † | – (0) † | – (0) † |

## 3b. Judge × genre, WITHOUT the passage

Run 1, by **our** genre (the routing table for methods D and E). Cells: BHS (questions); † = under 50
questions, never used for routing.

| model | HISTORY | ARTS | SCIENCE | GEOGRAPHY | RELIGION | OTHER |
|---|---|---|---|---|---|---|
| banglallama-13b | 100.00 (290) | 100.00 (278) | 100.00 (135) | 100.00 (110) | 100.00 (95) | 100.00 (12) † |
| deepseek-r1-14b | 37.93 (290) | 43.30 (278) | 34.81 (135) | 31.93 (110) | 36.32 (95) | 43.75 (12) † |
| gemma2-27b | 38.19 (290) | 42.04 (278) | 33.98 (135) | 34.43 (110) | 36.97 (95) | 39.58 (12) † |
| gemma4-31b | 32.20 (290) | 36.74 (278) | 26.48 (135) | 27.05 (110) | 30.26 (95) | 32.29 (12) † |
| gpt-oss-20b | 39.66 (290) | 44.11 (278) | 35.74 (135) | 35.45 (110) | 37.50 (95) | 43.75 (12) † |
| llama3.1-8b | 45.13 (290) | 48.83 (278) | 44.91 (135) | 40.34 (110) | 47.37 (95) | 53.12 (12) † |
| mistral-nemo-12b | 51.90 (290) | 50.45 (278) | 51.76 (135) | 49.66 (110) | 47.24 (95) | 56.25 (12) † |
| qwen2.5-32b | 36.16 (290) | 41.23 (278) | 35.28 (135) | 36.36 (110) | 33.29 (95) | 46.88 (12) † |
| qwen3.5-27b | 31.29 (290) | 38.53 (278) | 27.78 (135) | 32.50 (110) | 28.42 (95) | 34.38 (12) † |
| tigerllm-9b | 43.97 (290) | 46.09 (278) | 47.50 (135) | 39.20 (110) | 46.05 (95) | 45.83 (12) † |
| titullm-3b | 100.00 (290) | 100.00 (278) | 100.00 (135) | 100.00 (110) | 100.00 (95) | 100.00 (12) † |
| titullm-3b-instruct | 100.00 (290) | 100.00 (278) | 100.00 (135) | 100.00 (110) | 100.00 (95) | 100.00 (12) † |

Run 2, by the genre **each model named itself** (the {LLM, genre} pairs for method F).

| model | HISTORY | ARTS | SCIENCE | GEOGRAPHY | RELIGION | OTHER |
|---|---|---|---|---|---|---|
| banglallama-13b | – (0) † | – (0) † | – (0) † | – (0) † | – (0) † | – (0) † |
| deepseek-r1-14b | 38.13 (356) | 42.59 (263) | 34.72 (135) | 33.82 (95) | 34.33 (67) | 62.50 (4) † |
| gemma2-27b | 38.33 (439) | 42.62 (205) | 34.51 (113) | 33.38 (82) | 36.67 (75) | 29.17 (6) † |
| gemma4-31b | 32.19 (285) | 36.61 (282) | 26.48 (144) | 26.36 (101) | 29.79 (94) | 41.96 (14) † |
| gpt-oss-20b | 39.00 (367) | 44.81 (282) | 35.36 (111) | 35.70 (97) | 34.32 (55) | 42.86 (7) † |
| llama3.1-8b | 44.62 (513) | 49.77 (214) | 47.04 (76) | 40.18 (70) | 51.88 (40) † | 42.86 (7) † |
| mistral-nemo-12b | 51.15 (500) | 49.89 (233) | 51.74 (72) | 50.15 (86) | 50.00 (25) † | 50.00 (4) † |
| qwen2.5-32b | 36.50 (301) | 41.09 (268) | 35.25 (139) | 35.89 (101) | 33.06 (93) | 46.53 (18) † |
| qwen3.5-27b | 30.92 (287) | 38.72 (287) | 27.97 (143) | 32.86 (97) | 28.70 (98) | 29.69 (8) † |
| tigerllm-9b | 43.99 (474) | 48.21 (182) | 46.48 (96) | 39.97 (91) | 44.92 (59) | 46.32 (17) † |
| titullm-3b | – (0) † | – (0) † | – (0) † | – (0) † | – (0) † | – (0) † |
| titullm-3b-instruct | – (0) † | – (0) † | – (0) † | – (0) † | – (0) † | – (0) † |

## 4. Each judge against the best so far (paired, same questions)

difference = this model's BHS − the best model's BHS (positive = worse); 95% range from 1,000 re-samples of
questions (the same re-samples for every model). "clearly_worse" = the whole range is above 0. Exploratory:
the best judge is chosen and locked only in the routing notebook.

| condition | model | BHS | vs | difference | range95 | clearly_worse |
|---|---|---|---|---|---|---|
| context | gemma4-31b | 1.44 | gemma4-31b | +0.00 | +0.00 to +0.00 | – |
| context | qwen3.5-27b | 1.78 | gemma4-31b | +0.34 | -0.16 to +0.87 | no |
| context | gemma2-27b | 6.10 | gemma4-31b | +4.66 | +3.91 to +5.41 | yes |
| context | gpt-oss-20b | 7.08 | gemma4-31b | +5.64 | +4.69 to +6.63 | yes |
| context | qwen2.5-32b | 9.86 | gemma4-31b | +8.42 | +7.43 to +9.46 | yes |
| context | deepseek-r1-14b | 22.76 | gemma4-31b | +21.32 | +19.70 to +23.11 | yes |
| context | llama3.1-8b | 36.71 | gemma4-31b | +35.27 | +33.83 to +36.66 | yes |
| context | tigerllm-9b | 38.82 | gemma4-31b | +37.38 | +35.84 to +38.99 | yes |
| context | mistral-nemo-12b | 49.65 | gemma4-31b | +48.21 | +46.43 to +49.92 | yes |
| context | banglallama-13b | 100.00 | gemma4-31b | +98.56 | +98.06 to +99.05 | yes |
| context | titullm-3b | 100.00 | gemma4-31b | +98.56 | +98.06 to +99.05 | yes |
| context | titullm-3b-instruct | 100.00 | gemma4-31b | +98.56 | +98.06 to +99.05 | yes |
| no_context | gemma4-31b | 31.92 | gemma4-31b | +0.00 | +0.00 to +0.00 | – |
| no_context | qwen3.5-27b | 32.85 | gemma4-31b | +0.94 | -0.49 to +2.50 | no |
| no_context | qwen2.5-32b | 37.43 | gemma4-31b | +5.52 | +3.99 to +7.08 | yes |
| no_context | gemma2-27b | 38.18 | gemma4-31b | +6.26 | +4.71 to +7.84 | yes |
| no_context | deepseek-r1-14b | 38.29 | gemma4-31b | +6.37 | +4.40 to +8.34 | yes |
| no_context | gpt-oss-20b | 39.76 | gemma4-31b | +7.84 | +6.06 to +9.55 | yes |
| no_context | tigerllm-9b | 44.80 | gemma4-31b | +12.88 | +11.14 to +14.66 | yes |
| no_context | llama3.1-8b | 45.98 | gemma4-31b | +14.06 | +12.17 to +15.91 | yes |
| no_context | mistral-nemo-12b | 50.75 | gemma4-31b | +18.83 | +17.08 to +20.57 | yes |
| no_context | banglallama-13b | 100.00 | gemma4-31b | +68.08 | +66.56 to +69.46 | yes |
| no_context | titullm-3b | 100.00 | gemma4-31b | +68.08 | +66.56 to +69.46 | yes |
| no_context | titullm-3b-instruct | 100.00 | gemma4-31b | +68.08 | +66.56 to +69.46 | yes |

Genre guessing, accuracy against our genres (difference in percentage points; negative = worse):

| model | accuracy | vs | difference | range95 | clearly_worse |
|---|---|---|---|---|---|
| qwen3.5-27b | 95.0 | qwen3.5-27b | +0.0 | +0.0 to +0.0 | – |
| gemma4-31b | 93.8 | qwen3.5-27b | -1.2 | -2.3 to -0.1 | yes |
| qwen2.5-32b | 91.8 | qwen3.5-27b | -3.2 | -4.8 to -1.7 | yes |
| deepseek-r1-14b | 83.7 | qwen3.5-27b | -11.3 | -13.6 to -9.0 | yes |
| gemma2-27b | 81.5 | qwen3.5-27b | -13.5 | -16.0 to -11.0 | yes |
| gpt-oss-20b | 80.0 | qwen3.5-27b | -15.0 | -17.6 to -12.6 | yes |
| tigerllm-9b | 76.8 | qwen3.5-27b | -18.2 | -20.9 to -15.4 | yes |
| llama3.1-8b | 73.4 | qwen3.5-27b | -21.6 | -24.9 to -19.0 | yes |
| mistral-nemo-12b | 69.8 | qwen3.5-27b | -25.2 | -28.2 to -22.2 | yes |
| banglallama-13b | 0.0 | qwen3.5-27b | -95.0 | -96.3 to -93.5 | yes |
| titullm-3b | 0.0 | qwen3.5-27b | -95.0 | -96.3 to -93.5 | yes |
| titullm-3b-instruct | 0.0 | qwen3.5-27b | -95.0 | -96.3 to -93.5 | yes |

## 5. How often two judges give the same verdict (all 4,600 answers)

Low agreement between good judges is what makes voting and routing worth trying.

With the passage:

| model | banglallama-13b | deepseek-r1-14b | gemma2-27b | gemma4-31b | gpt-oss-20b | llama3.1-8b | mistral-nemo-12b | qwen2.5-32b | qwen3.5-27b | tigerllm-9b | titullm-3b | titullm-3b-instruct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| banglallama-13b | 100% | 16% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 100% |
| deepseek-r1-14b | 16% | 100% | 74% | 77% | 75% | 42% | 39% | 71% | 77% | 41% | 16% | 16% |
| gemma2-27b | 0% | 74% | 100% | 91% | 88% | 52% | 47% | 86% | 92% | 49% | 0% | 0% |
| gemma4-31b | 0% | 77% | 91% | 100% | 93% | 49% | 46% | 86% | 98% | 46% | 0% | 0% |
| gpt-oss-20b | 0% | 75% | 88% | 93% | 100% | 49% | 45% | 84% | 92% | 47% | 0% | 0% |
| llama3.1-8b | 0% | 42% | 52% | 49% | 49% | 100% | 58% | 56% | 50% | 65% | 0% | 0% |
| mistral-nemo-12b | 0% | 39% | 47% | 46% | 45% | 58% | 100% | 50% | 46% | 61% | 0% | 0% |
| qwen2.5-32b | 0% | 71% | 86% | 86% | 84% | 56% | 50% | 100% | 87% | 54% | 0% | 0% |
| qwen3.5-27b | 0% | 77% | 92% | 98% | 92% | 50% | 46% | 87% | 100% | 47% | 0% | 0% |
| tigerllm-9b | 0% | 41% | 49% | 46% | 47% | 65% | 61% | 54% | 47% | 100% | 0% | 0% |
| titullm-3b | 100% | 16% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 100% |
| titullm-3b-instruct | 100% | 16% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 100% |

Without the passage:

| model | banglallama-13b | deepseek-r1-14b | gemma2-27b | gemma4-31b | gpt-oss-20b | llama3.1-8b | mistral-nemo-12b | qwen2.5-32b | qwen3.5-27b | tigerllm-9b | titullm-3b | titullm-3b-instruct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| banglallama-13b | 100% | 0% | 0% | 0% | 2% | 0% | 0% | 0% | 0% | 0% | 100% | 100% |
| deepseek-r1-14b | 0% | 100% | 55% | 64% | 66% | 52% | 61% | 59% | 62% | 42% | 0% | 0% |
| gemma2-27b | 0% | 55% | 100% | 65% | 53% | 61% | 38% | 75% | 72% | 66% | 0% | 0% |
| gemma4-31b | 0% | 64% | 65% | 100% | 64% | 53% | 54% | 66% | 72% | 48% | 0% | 0% |
| gpt-oss-20b | 2% | 66% | 53% | 64% | 100% | 49% | 66% | 55% | 59% | 37% | 2% | 2% |
| llama3.1-8b | 0% | 52% | 61% | 53% | 49% | 100% | 46% | 63% | 57% | 64% | 0% | 0% |
| mistral-nemo-12b | 0% | 61% | 38% | 54% | 66% | 46% | 100% | 45% | 48% | 31% | 0% | 0% |
| qwen2.5-32b | 0% | 59% | 75% | 66% | 55% | 63% | 45% | 100% | 71% | 63% | 0% | 0% |
| qwen3.5-27b | 0% | 62% | 72% | 72% | 59% | 57% | 48% | 71% | 100% | 58% | 0% | 0% |
| tigerllm-9b | 0% | 42% | 66% | 48% | 37% | 64% | 31% | 63% | 58% | 100% | 0% | 0% |
| titullm-3b | 100% | 0% | 0% | 0% | 2% | 0% | 0% | 0% | 0% | 0% | 100% | 100% |
| titullm-3b-instruct | 100% | 0% | 0% | 0% | 2% | 0% | 0% | 0% | 0% | 0% | 100% | 100% |

## 6. Judging in OUR genres (Run 1) vs in the genres the model NAMED ITSELF (Run 2)

The verdicts are the same; only the grouping of questions differs. BHS_ours = the judge's score on the
questions we put in that genre; BHS_own = its score on the questions it put there itself (its {LLM, genre}
pair). own_minus_ours < 0 means the judge looks better in its own genre. The range is paired (same
re-sampled questions). same_questions = overlap of the two groups. Overall BHS is identical in both runs.

With the passage:

| model | genre | questions_ours | BHS_ours | questions_own | BHS_own | own_minus_ours | range95 | same_questions | usable |
|---|---|---|---|---|---|---|---|---|---|
| banglallama-13b | HISTORY | 290 | 100.00 | 0 | – | – | – | 0% | no |
| banglallama-13b | ARTS | 278 | 100.00 | 0 | – | – | – | 0% | no |
| banglallama-13b | SCIENCE | 135 | 100.00 | 0 | – | – | – | 0% | no |
| banglallama-13b | GEOGRAPHY | 110 | 100.00 | 0 | – | – | – | 0% | no |
| banglallama-13b | RELIGION | 95 | 100.00 | 0 | – | – | – | 0% | no |
| banglallama-13b | OTHER | 12 | 100.00 | 0 | – | – | – | 0% | no |
| deepseek-r1-14b | HISTORY | 290 | 23.15 | 356 | 23.21 | +0.06 | -1.52 to +1.56 | 72% | yes |
| deepseek-r1-14b | ARTS | 278 | 20.32 | 263 | 21.48 | +1.16 | -0.14 to +2.60 | 80% | yes |
| deepseek-r1-14b | SCIENCE | 135 | 23.80 | 135 | 25.09 | +1.30 | -0.94 to +3.56 | 78% | yes |
| deepseek-r1-14b | GEOGRAPHY | 110 | 23.41 | 95 | 20.26 | -3.15 | -6.74 to +0.23 | 58% | yes |
| deepseek-r1-14b | RELIGION | 95 | 24.08 | 67 | 24.44 | +0.36 | -3.63 to +4.07 | 65% | yes |
| deepseek-r1-14b | OTHER | 12 | 41.67 | 4 | 18.75 | -22.92 | -48.61 to +11.46 | 14% | no |
| gemma2-27b | HISTORY | 290 | 5.78 | 439 | 5.47 | -0.31 | -0.96 to +0.30 | 64% | yes |
| gemma2-27b | ARTS | 278 | 5.71 | 205 | 6.34 | +0.63 | -0.02 to +1.30 | 70% | yes |
| gemma2-27b | SCIENCE | 135 | 6.85 | 113 | 7.63 | +0.78 | +0.11 to +1.51 | 77% | yes |
| gemma2-27b | GEOGRAPHY | 110 | 5.45 | 82 | 5.79 | +0.34 | -0.54 to +1.27 | 71% | yes |
| gemma2-27b | RELIGION | 95 | 7.50 | 75 | 7.50 | +0.00 | -1.41 to +1.18 | 77% | yes |
| gemma2-27b | OTHER | 12 | 9.38 | 6 | 2.08 | -7.29 | -17.05 to +0.00 | 29% | no |
| gemma4-31b | HISTORY | 290 | 1.03 | 285 | 1.05 | +0.02 | -0.02 to +0.07 | 89% | yes |
| gemma4-31b | ARTS | 278 | 1.66 | 282 | 1.64 | -0.02 | -0.08 to +0.02 | 94% | yes |
| gemma4-31b | SCIENCE | 135 | 2.04 | 144 | 1.82 | -0.21 | -0.46 to -0.04 | 89% | yes |
| gemma4-31b | GEOGRAPHY | 110 | 0.23 | 101 | 0.37 | +0.14 | +0.00 to +0.43 | 82% | yes |
| gemma4-31b | RELIGION | 95 | 2.76 | 94 | 2.26 | -0.50 | -1.65 to +0.12 | 87% | yes |
| gemma4-31b | OTHER | 12 | 0.00 | 14 | 3.57 | +3.57 | +0.00 to +12.50 | 37% | no |
| gpt-oss-20b | HISTORY | 290 | 6.47 | 367 | 6.98 | +0.52 | -0.35 to +1.50 | 65% | yes |
| gpt-oss-20b | ARTS | 278 | 8.14 | 282 | 7.49 | -0.65 | -1.46 to +0.15 | 79% | yes |
| gpt-oss-20b | SCIENCE | 135 | 6.20 | 111 | 7.09 | +0.89 | -0.53 to +2.40 | 70% | yes |
| gpt-oss-20b | GEOGRAPHY | 110 | 5.91 | 97 | 6.06 | +0.15 | -2.36 to +2.42 | 53% | yes |
| gpt-oss-20b | RELIGION | 95 | 8.16 | 55 | 7.05 | -1.11 | -3.86 to +1.42 | 56% | yes |
| gpt-oss-20b | OTHER | 12 | 9.38 | 7 | 10.71 | +1.34 | -11.46 to +17.50 | 12% | no |
| llama3.1-8b | HISTORY | 290 | 35.56 | 513 | 35.23 | -0.33 | -1.81 to +1.18 | 56% | yes |
| llama3.1-8b | ARTS | 278 | 37.72 | 214 | 38.67 | +0.94 | -0.40 to +2.18 | 71% | yes |
| llama3.1-8b | SCIENCE | 135 | 39.07 | 76 | 37.50 | -1.57 | -5.20 to +2.06 | 54% | yes |
| llama3.1-8b | GEOGRAPHY | 110 | 34.43 | 70 | 38.57 | +4.14 | +1.77 to +6.59 | 62% | yes |
| llama3.1-8b | RELIGION | 95 | 36.84 | 40 | 41.56 | +4.72 | -0.24 to +9.96 | 41% | no |
| llama3.1-8b | OTHER | 12 | 34.38 | 7 | 30.36 | -4.02 | -17.86 to +10.71 | 12% | no |
| mistral-nemo-12b | HISTORY | 290 | 48.66 | 500 | 48.52 | -0.14 | -2.15 to +1.90 | 54% | yes |
| mistral-nemo-12b | ARTS | 278 | 51.53 | 233 | 53.27 | +1.74 | -0.45 to +4.08 | 60% | yes |
| mistral-nemo-12b | SCIENCE | 135 | 52.13 | 72 | 52.78 | +0.65 | -3.41 to +4.91 | 51% | yes |
| mistral-nemo-12b | GEOGRAPHY | 110 | 42.84 | 86 | 44.33 | +1.49 | -2.01 to +4.99 | 62% | yes |
| mistral-nemo-12b | RELIGION | 95 | 49.74 | 25 | 46.50 | -3.24 | -11.95 to +4.53 | 26% | no |
| mistral-nemo-12b | OTHER | 12 | 63.54 | 4 | 56.25 | -7.29 | -24.04 to +11.11 | 23% | no |
| qwen2.5-32b | HISTORY | 290 | 11.12 | 301 | 10.34 | -0.78 | -1.44 to -0.25 | 83% | yes |
| qwen2.5-32b | ARTS | 278 | 9.98 | 268 | 10.12 | +0.14 | -0.28 to +0.54 | 89% | yes |
| qwen2.5-32b | SCIENCE | 135 | 10.28 | 139 | 10.34 | +0.06 | -0.16 to +0.29 | 96% | yes |
| qwen2.5-32b | GEOGRAPHY | 110 | 6.48 | 101 | 6.93 | +0.45 | -0.22 to +1.21 | 80% | yes |
| qwen2.5-32b | RELIGION | 95 | 8.82 | 93 | 9.68 | +0.86 | -0.39 to +2.51 | 83% | yes |
| qwen2.5-32b | OTHER | 12 | 11.46 | 18 | 11.81 | +0.35 | -6.28 to +7.05 | 30% | no |
| qwen3.5-27b | HISTORY | 290 | 1.85 | 287 | 1.83 | -0.02 | -0.22 to +0.14 | 90% | yes |
| qwen3.5-27b | ARTS | 278 | 1.62 | 287 | 1.79 | +0.17 | -0.06 to +0.55 | 94% | yes |
| qwen3.5-27b | SCIENCE | 135 | 2.69 | 143 | 2.45 | -0.24 | -0.47 to -0.06 | 92% | yes |
| qwen3.5-27b | GEOGRAPHY | 110 | 0.80 | 97 | 0.90 | +0.11 | -0.21 to +0.45 | 86% | yes |
| qwen3.5-27b | RELIGION | 95 | 1.97 | 98 | 1.53 | -0.44 | -1.72 to +0.45 | 87% | yes |
| qwen3.5-27b | OTHER | 12 | 1.04 | 8 | 1.56 | +0.52 | +0.00 to +2.68 | 54% | no |
| tigerllm-9b | HISTORY | 290 | 38.32 | 474 | 37.71 | -0.61 | -2.35 to +1.22 | 59% | yes |
| tigerllm-9b | ARTS | 278 | 39.66 | 182 | 43.41 | +3.75 | +1.65 to +5.76 | 63% | yes |
| tigerllm-9b | SCIENCE | 135 | 38.80 | 96 | 39.32 | +0.53 | -1.90 to +3.18 | 67% | yes |
| tigerllm-9b | GEOGRAPHY | 110 | 32.95 | 91 | 31.73 | -1.22 | -4.51 to +2.06 | 75% | yes |
| tigerllm-9b | RELIGION | 95 | 44.08 | 59 | 43.22 | -0.86 | -5.06 to +3.25 | 62% | yes |
| tigerllm-9b | OTHER | 12 | 43.75 | 17 | 39.71 | -4.04 | -20.73 to +12.78 | 26% | no |
| titullm-3b | HISTORY | 290 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b | ARTS | 278 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b | SCIENCE | 135 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b | GEOGRAPHY | 110 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b | RELIGION | 95 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b | OTHER | 12 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b-instruct | HISTORY | 290 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b-instruct | ARTS | 278 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b-instruct | SCIENCE | 135 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b-instruct | GEOGRAPHY | 110 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b-instruct | RELIGION | 95 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b-instruct | OTHER | 12 | 100.00 | 0 | – | – | – | 0% | no |

Without the passage:

| model | genre | questions_ours | BHS_ours | questions_own | BHS_own | own_minus_ours | range95 | same_questions | usable |
|---|---|---|---|---|---|---|---|---|---|
| banglallama-13b | HISTORY | 290 | 100.00 | 0 | – | – | – | 0% | no |
| banglallama-13b | ARTS | 278 | 100.00 | 0 | – | – | – | 0% | no |
| banglallama-13b | SCIENCE | 135 | 100.00 | 0 | – | – | – | 0% | no |
| banglallama-13b | GEOGRAPHY | 110 | 100.00 | 0 | – | – | – | 0% | no |
| banglallama-13b | RELIGION | 95 | 100.00 | 0 | – | – | – | 0% | no |
| banglallama-13b | OTHER | 12 | 100.00 | 0 | – | – | – | 0% | no |
| deepseek-r1-14b | HISTORY | 290 | 37.93 | 356 | 38.13 | +0.20 | -1.45 to +1.60 | 72% | yes |
| deepseek-r1-14b | ARTS | 278 | 43.30 | 263 | 42.59 | -0.71 | -2.03 to +0.72 | 80% | yes |
| deepseek-r1-14b | SCIENCE | 135 | 34.81 | 135 | 34.72 | -0.09 | -2.42 to +2.15 | 78% | yes |
| deepseek-r1-14b | GEOGRAPHY | 110 | 31.93 | 95 | 33.82 | +1.88 | -1.51 to +5.51 | 58% | yes |
| deepseek-r1-14b | RELIGION | 95 | 36.32 | 67 | 34.33 | -1.99 | -5.41 to +1.55 | 65% | yes |
| deepseek-r1-14b | OTHER | 12 | 43.75 | 4 | 62.50 | +18.75 | +0.96 to +37.68 | 14% | no |
| gemma2-27b | HISTORY | 290 | 38.19 | 439 | 38.33 | +0.14 | -0.98 to +1.32 | 64% | yes |
| gemma2-27b | ARTS | 278 | 42.04 | 205 | 42.62 | +0.58 | -0.66 to +1.84 | 70% | yes |
| gemma2-27b | SCIENCE | 135 | 33.98 | 113 | 34.51 | +0.53 | -0.99 to +2.09 | 77% | yes |
| gemma2-27b | GEOGRAPHY | 110 | 34.43 | 82 | 33.38 | -1.05 | -3.20 to +1.03 | 71% | yes |
| gemma2-27b | RELIGION | 95 | 36.97 | 75 | 36.67 | -0.31 | -2.68 to +1.70 | 77% | yes |
| gemma2-27b | OTHER | 12 | 39.58 | 6 | 29.17 | -10.42 | -26.39 to +4.97 | 29% | no |
| gemma4-31b | HISTORY | 290 | 32.20 | 285 | 32.19 | -0.01 | -0.86 to +0.85 | 89% | yes |
| gemma4-31b | ARTS | 278 | 36.74 | 282 | 36.61 | -0.12 | -0.86 to +0.63 | 94% | yes |
| gemma4-31b | SCIENCE | 135 | 26.48 | 144 | 26.48 | -0.01 | -1.08 to +1.10 | 89% | yes |
| gemma4-31b | GEOGRAPHY | 110 | 27.05 | 101 | 26.36 | -0.68 | -2.18 to +0.89 | 82% | yes |
| gemma4-31b | RELIGION | 95 | 30.26 | 94 | 29.79 | -0.48 | -2.02 to +0.94 | 87% | yes |
| gemma4-31b | OTHER | 12 | 32.29 | 14 | 41.96 | +9.67 | -0.48 to +21.03 | 37% | no |
| gpt-oss-20b | HISTORY | 290 | 39.66 | 367 | 39.00 | -0.66 | -2.29 to +0.95 | 65% | yes |
| gpt-oss-20b | ARTS | 278 | 44.11 | 282 | 44.81 | +0.70 | -0.63 to +2.03 | 79% | yes |
| gpt-oss-20b | SCIENCE | 135 | 35.74 | 111 | 35.36 | -0.38 | -3.19 to +2.58 | 70% | yes |
| gpt-oss-20b | GEOGRAPHY | 110 | 35.45 | 97 | 35.70 | +0.24 | -3.01 to +3.70 | 53% | yes |
| gpt-oss-20b | RELIGION | 95 | 37.50 | 55 | 34.32 | -3.18 | -7.32 to +0.67 | 56% | yes |
| gpt-oss-20b | OTHER | 12 | 43.75 | 7 | 42.86 | -0.89 | -18.75 to +18.44 | 12% | no |
| llama3.1-8b | HISTORY | 290 | 45.13 | 513 | 44.62 | -0.51 | -2.03 to +1.12 | 56% | yes |
| llama3.1-8b | ARTS | 278 | 48.83 | 214 | 49.77 | +0.94 | -0.49 to +2.48 | 71% | yes |
| llama3.1-8b | SCIENCE | 135 | 44.91 | 76 | 47.04 | +2.13 | -1.49 to +5.46 | 54% | yes |
| llama3.1-8b | GEOGRAPHY | 110 | 40.34 | 70 | 40.18 | -0.16 | -2.61 to +2.40 | 62% | yes |
| llama3.1-8b | RELIGION | 95 | 47.37 | 40 | 51.88 | +4.51 | -0.57 to +9.79 | 41% | no |
| llama3.1-8b | OTHER | 12 | 53.12 | 7 | 42.86 | -10.27 | -30.21 to +9.62 | 12% | no |
| mistral-nemo-12b | HISTORY | 290 | 51.90 | 500 | 51.15 | -0.75 | -2.02 to +0.45 | 54% | yes |
| mistral-nemo-12b | ARTS | 278 | 50.45 | 233 | 49.89 | -0.56 | -2.02 to +1.06 | 60% | yes |
| mistral-nemo-12b | SCIENCE | 135 | 51.76 | 72 | 51.74 | -0.02 | -2.25 to +2.32 | 51% | yes |
| mistral-nemo-12b | GEOGRAPHY | 110 | 49.66 | 86 | 50.15 | +0.49 | -1.78 to +2.78 | 62% | yes |
| mistral-nemo-12b | RELIGION | 95 | 47.24 | 25 | 50.00 | +2.76 | -2.70 to +7.69 | 26% | no |
| mistral-nemo-12b | OTHER | 12 | 56.25 | 4 | 50.00 | -6.25 | -12.50 to -1.04 | 23% | no |
| qwen2.5-32b | HISTORY | 290 | 36.16 | 301 | 36.50 | +0.34 | -0.63 to +1.28 | 83% | yes |
| qwen2.5-32b | ARTS | 278 | 41.23 | 268 | 41.09 | -0.14 | -1.00 to +0.66 | 89% | yes |
| qwen2.5-32b | SCIENCE | 135 | 35.28 | 139 | 35.25 | -0.03 | -0.83 to +0.92 | 96% | yes |
| qwen2.5-32b | GEOGRAPHY | 110 | 36.36 | 101 | 35.89 | -0.47 | -2.12 to +1.04 | 80% | yes |
| qwen2.5-32b | RELIGION | 95 | 33.29 | 93 | 33.06 | -0.22 | -1.72 to +1.47 | 83% | yes |
| qwen2.5-32b | OTHER | 12 | 46.88 | 18 | 46.53 | -0.35 | -9.38 to +9.35 | 30% | no |
| qwen3.5-27b | HISTORY | 290 | 31.29 | 287 | 30.92 | -0.37 | -1.20 to +0.50 | 90% | yes |
| qwen3.5-27b | ARTS | 278 | 38.53 | 287 | 38.72 | +0.19 | -0.24 to +0.69 | 94% | yes |
| qwen3.5-27b | SCIENCE | 135 | 27.78 | 143 | 27.97 | +0.19 | -0.91 to +1.42 | 92% | yes |
| qwen3.5-27b | GEOGRAPHY | 110 | 32.50 | 97 | 32.86 | +0.36 | -0.69 to +1.67 | 86% | yes |
| qwen3.5-27b | RELIGION | 95 | 28.42 | 98 | 28.70 | +0.28 | -1.24 to +1.98 | 87% | yes |
| qwen3.5-27b | OTHER | 12 | 34.38 | 8 | 29.69 | -4.69 | -13.54 to +2.08 | 54% | no |
| tigerllm-9b | HISTORY | 290 | 43.97 | 474 | 43.99 | +0.02 | -1.20 to +1.24 | 59% | yes |
| tigerllm-9b | ARTS | 278 | 46.09 | 182 | 48.21 | +2.13 | +0.74 to +3.60 | 63% | yes |
| tigerllm-9b | SCIENCE | 135 | 47.50 | 96 | 46.48 | -1.02 | -3.12 to +1.21 | 67% | yes |
| tigerllm-9b | GEOGRAPHY | 110 | 39.20 | 91 | 39.97 | +0.77 | -1.11 to +2.78 | 75% | yes |
| tigerllm-9b | RELIGION | 95 | 46.05 | 59 | 44.92 | -1.14 | -3.44 to +1.16 | 62% | yes |
| tigerllm-9b | OTHER | 12 | 45.83 | 17 | 46.32 | +0.49 | -11.81 to +12.15 | 26% | no |
| titullm-3b | HISTORY | 290 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b | ARTS | 278 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b | SCIENCE | 135 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b | GEOGRAPHY | 110 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b | RELIGION | 95 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b | OTHER | 12 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b-instruct | HISTORY | 290 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b-instruct | ARTS | 278 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b-instruct | SCIENCE | 135 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b-instruct | GEOGRAPHY | 110 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b-instruct | RELIGION | 95 | 100.00 | 0 | – | – | – | 0% | no |
| titullm-3b-instruct | OTHER | 12 | 100.00 | 0 | – | – | – | 0% | no |

## 7. Is a different judge best in some genre? (exploratory, our genres)

For each of our genres: the judge with the lowest BHS there, against the best judge overall. gain = how
much better the genre's own best is (BHS points; paired 95% range). "clearly_better" = the range is above 0.
This only describes the runs so far; the routing tables are built and locked in the routing notebook.

With the passage:

| genre | questions | best_here | BHS_best_here | overall_best | BHS_overall_best | gain | range95 | clearly_better | usable |
|---|---|---|---|---|---|---|---|---|---|
| HISTORY | 290 | gemma4-31b | 1.03 | gemma4-31b | 1.03 | 0 | – | – | yes |
| ARTS | 278 | qwen3.5-27b | 1.62 | gemma4-31b | 1.66 | +0.04 | -0.98 to +1.14 | no | yes |
| SCIENCE | 135 | gemma4-31b | 2.04 | gemma4-31b | 2.04 | 0 | – | – | yes |
| GEOGRAPHY | 110 | gemma4-31b | 0.23 | gemma4-31b | 0.23 | 0 | – | – | yes |
| RELIGION | 95 | qwen3.5-27b | 1.97 | gemma4-31b | 2.76 | +0.79 | -0.91 to +2.92 | no | yes |
| OTHER | 12 | gemma4-31b | 0.00 | gemma4-31b | 0.00 | 0 | – | – | no |

Without the passage:

| genre | questions | best_here | BHS_best_here | overall_best | BHS_overall_best | gain | range95 | clearly_better | usable |
|---|---|---|---|---|---|---|---|---|---|
| HISTORY | 290 | qwen3.5-27b | 31.29 | gemma4-31b | 32.20 | +0.91 | -1.60 to +3.34 | no | yes |
| ARTS | 278 | gemma4-31b | 36.74 | gemma4-31b | 36.74 | 0 | – | – | yes |
| SCIENCE | 135 | gemma4-31b | 26.48 | gemma4-31b | 26.48 | 0 | – | – | yes |
| GEOGRAPHY | 110 | gemma4-31b | 27.05 | gemma4-31b | 27.05 | 0 | – | – | yes |
| RELIGION | 95 | qwen3.5-27b | 28.42 | gemma4-31b | 30.26 | +1.84 | -3.18 to +7.31 | no | yes |
| OTHER | 12 | gemma4-31b | 32.29 | gemma4-31b | 32.29 | 0 | – | – | no |

Headroom: BHS if every genre went to its own best judge, chosen on the same data (in-sample, so
optimistic; the honest test is the 5-fold checkpoint and Dataset 2):

| condition | single_best | BHS_single_best | BHS_best_per_genre | judges_used |
|---|---|---|---|---|
| context | gemma4-31b | 1.44 | 1.35 | gemma4-31b, qwen3.5-27b |
| no_context | gemma4-31b | 31.92 | 31.44 | gemma4-31b, qwen3.5-27b |

