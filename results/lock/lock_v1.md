# Locked choices for Dataset 2 (v1)

Created 2026-10-18T13:04:26+00:00 by `src/routing/make_lock.py` from BenHalluEval-QA v1.3 runs only. sha256 of `lock_v1.json`: `779cc5a7cdc20b0abc1e73986a25e03d1bd1cd1e32a798d3fb0a3d62ecd50063`.

**Every choice below was computed from BenHalluEval-QA v1.3 runs only, before any Dataset 2 data was made or seen. Nothing here may change after Dataset 2 is touched. A new lock version is allowed only before that.**

- Dataset 2 pool (9 judges): deepseek-r1-14b, gemma2-27b, gemma4-31b, gpt-oss-20b, llama3.1-8b, mistral-nemo-12b, qwen2.5-32b, qwen3.5-27b, tigerllm-9b
- Excluded (no usable verdicts): banglallama-13b, titullm-3b, titullm-3b-instruct
- Secondary pool (gpt-4.1-mini): not run, so dropped unless locked in a new version before Dataset 2.

## With the passage (`context`; Dataset 2 uses the passage label)

- **A, best single judge:** gemma4-31b (BHS 1.44)
- **B, top-3 vote:** gemma4-31b, qwen3.5-27b, gemma2-27b
- **C, vote of all 9 pool judges** (tie → A)
- **Best genre guesser (E):** qwen3.5-27b (95.0% accuracy)

| Genre | D/E routes to | BHS on BenHalluEval | questions |
|---|---|---|---|
| HISTORY | gemma4-31b | 1.03 | 290 |
| ARTS | qwen3.5-27b | 1.62 | 278 |
| SCIENCE | gemma4-31b | 2.04 | 135 |
| GEOGRAPHY | gemma4-31b | 0.23 | 110 |
| RELIGION | qwen3.5-27b | 1.97 | 95 |
| OTHER | gemma4-31b | – (falls back to A) | 12 |

**F, own-genre scores** (BHS inside the genre each judge named; only cells with ≥50 questions):

| Judge | HISTORY | ARTS | SCIENCE | GEOGRAPHY | RELIGION | OTHER |
|---|---|---|---|---|---|---|
| deepseek-r1-14b | 23.21 (356) | 21.48 (263) | 25.09 (135) | 20.26 (95) | 24.44 (67) | – |
| gemma2-27b | 5.47 (439) | 6.34 (205) | 7.63 (113) | 5.79 (82) | 7.50 (75) | – |
| gemma4-31b | 1.05 (285) | 1.64 (282) | 1.82 (144) | 0.37 (101) | 2.26 (94) | – |
| gpt-oss-20b | 6.98 (367) | 7.49 (282) | 7.09 (111) | 6.06 (97) | 7.05 (55) | – |
| llama3.1-8b | 35.23 (513) | 38.67 (214) | 37.50 (76) | 38.57 (70) | – | – |
| mistral-nemo-12b | 48.52 (500) | 53.27 (233) | 52.78 (72) | 44.33 (86) | – | – |
| qwen2.5-32b | 10.34 (301) | 10.12 (268) | 10.34 (139) | 6.93 (101) | 9.68 (93) | – |
| qwen3.5-27b | 1.83 (287) | 1.79 (287) | 2.45 (143) | 0.90 (97) | 1.53 (98) | – |
| tigerllm-9b | 37.71 (474) | 43.41 (182) | 39.32 (96) | 31.73 (91) | 43.22 (59) | – |

## Without the passage (`no_context`; Dataset 2 uses the world label)

- **A, best single judge:** gemma4-31b (BHS 31.92)
- **B, top-3 vote:** gemma4-31b, qwen3.5-27b, qwen2.5-32b
- **C, vote of all 9 pool judges** (tie → A)
- **Best genre guesser (E):** qwen3.5-27b (95.0% accuracy)

| Genre | D/E routes to | BHS on BenHalluEval | questions |
|---|---|---|---|
| HISTORY | qwen3.5-27b | 31.29 | 290 |
| ARTS | gemma4-31b | 36.74 | 278 |
| SCIENCE | gemma4-31b | 26.48 | 135 |
| GEOGRAPHY | gemma4-31b | 27.05 | 110 |
| RELIGION | qwen3.5-27b | 28.42 | 95 |
| OTHER | gemma4-31b | – (falls back to A) | 12 |

**F, own-genre scores** (BHS inside the genre each judge named; only cells with ≥50 questions):

| Judge | HISTORY | ARTS | SCIENCE | GEOGRAPHY | RELIGION | OTHER |
|---|---|---|---|---|---|---|
| deepseek-r1-14b | 38.13 (356) | 42.59 (263) | 34.72 (135) | 33.82 (95) | 34.33 (67) | – |
| gemma2-27b | 38.33 (439) | 42.62 (205) | 34.51 (113) | 33.38 (82) | 36.67 (75) | – |
| gemma4-31b | 32.19 (285) | 36.61 (282) | 26.48 (144) | 26.36 (101) | 29.79 (94) | – |
| gpt-oss-20b | 39.00 (367) | 44.81 (282) | 35.36 (111) | 35.70 (97) | 34.32 (55) | – |
| llama3.1-8b | 44.62 (513) | 49.77 (214) | 47.04 (76) | 40.18 (70) | – | – |
| mistral-nemo-12b | 51.15 (500) | 49.89 (233) | 51.74 (72) | 50.15 (86) | – | – |
| qwen2.5-32b | 36.50 (301) | 41.09 (268) | 35.25 (139) | 35.89 (101) | 33.06 (93) | – |
| qwen3.5-27b | 30.92 (287) | 38.72 (287) | 27.97 (143) | 32.86 (97) | 28.70 (98) | – |
| tigerllm-9b | 43.99 (474) | 48.21 (182) | 46.48 (96) | 39.97 (91) | 44.92 (59) | – |

## Confirmatory tests on Dataset 2

- statistic: BHS difference on Dataset 2 (strict parse; no_answer = error)
- uncertainty: paired bootstrap over Dataset 2 questions, 10,000 re-samples, seed 2026; 95% range reported
- p_value: two-sided bootstrap p = 2 x min(share of differences <= 0, share >= 0)
- multiplicity: Holm correction across the 6 comparisons at alpha 0.05
- everything_else: exploratory (B, D, G, K, H/I/J if added before Dataset 2, per-genre results, Bangla-prompt runs)
- comparisons: E vs A (context); F vs A (context); F vs C (context); E vs A (no_context); F vs A (no_context); F vs C (no_context)

## Exploratory predictions

- gemma4-31b judges Science better in its own genre than in ours (context): BenHalluEval 1.82 vs 2.04
- qwen3.5-27b judges Science better in its own genre than in ours (context): 2.45 vs 2.69
- qwen2.5-32b judges History better in its own genre than in ours (context): 10.34 vs 11.12
- Our reading: these 3 of 86 comparisons are consistent with chance; we expect them not to replicate
