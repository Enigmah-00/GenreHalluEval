# Split experiment inside BenHalluEval (exploratory)

Made by `src/routing/split_experiment.py` from the saved BenHalluEval-QA v1.3 runs (no new model calls). The 920
questions are split in two halves, stratified by our genre (seed 2026): split 1 (459 questions) plays
Dataset 1, split 2 (461 questions) plays Dataset 2. Every choice (pool of 9 judges, A, best genre
guesser, judge x genre table, own-genre cells, route R) is learned on split 1 with the lock rules and tested on
split 2. Same data source, same answer writer, same genre labels: no dataset shift.

BHS: lower is better. Difference = route minus A (below 0 = the route is better). Paired bootstrap over questions,
10,000 re-samples, seed 2026; two-sided p; Holm over the 2 R vs A tests.

## The same test as on Dataset 2 (cells of 50+ questions, as locked)

| Test | Condition | Test questions | A | R | Difference | 95% range | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| R vs A | with passage | 461 | 2.17 | 2.17 | +0.00 | +0.00 to +0.00 | 1.000 | 1.000 |
| R vs A | without passage | 461 | 32.62 | 32.65 | +0.03 | -1.38 to +1.41 | 0.993 | 1.000 |

### All routes, cells of 50+ questions (as locked)

| Condition | Route | BHS on split 2 | Difference vs A | 95% range | Judges used (questions) |
|---|---|---|---|---|---|
| with passage | A | 2.17 | | | gemma4-31b 461 |
| with passage | R | 2.17 | +0.00 | +0.00 to +0.00 | gemma4-31b 461 |
| with passage | D | 2.17 | +0.00 | +0.00 to +0.00 | gemma4-31b 461 |
| with passage | E | 2.17 | +0.00 | +0.00 to +0.00 | gemma4-31b 461 |
| with passage | F | 3.58 | +1.41 | +0.70 to +2.20 | gemma4-31b 416, gpt-oss-20b 13, gemma2-27b 13, qwen3.5-27b 6, llama3.1-8b 5, mistral-nemo-12b 4, deepseek-r1-14b 3, tigerllm-9b 1 |
| without passage | A | 32.62 | | | gemma4-31b 461 |
| without passage | R | 32.65 | +0.03 | -1.38 to +1.41 | gemma4-31b 239, qwen3.5-27b 216, deepseek-r1-14b 4, qwen2.5-32b 2 |
| without passage | D | 32.94 | +0.33 | -1.11 to +1.76 | gemma4-31b 248, qwen3.5-27b 213 |
| without passage | E | 32.67 | +0.05 | -1.33 to +1.38 | gemma4-31b 240, qwen3.5-27b 221 |
| without passage | F | 33.57 | +0.95 | -0.73 to +2.58 | qwen3.5-27b 217, gemma4-31b 199, deepseek-r1-14b 16, gpt-oss-20b 10, llama3.1-8b 7, qwen2.5-32b 5, mistral-nemo-12b 4, gemma2-27b 2, tigerllm-9b 1 |

### All routes, cells of 25+ questions (half of 50, because a half has half the questions)

| Condition | Route | BHS on split 2 | Difference vs A | 95% range | Judges used (questions) |
|---|---|---|---|---|---|
| with passage | A | 2.17 | | | gemma4-31b 461 |
| with passage | R | 2.01 | -0.16 | -0.54 to +0.11 | gemma4-31b 414, qwen3.5-27b 47 |
| with passage | D | 2.03 | -0.14 | -0.52 to +0.14 | gemma4-31b 413, qwen3.5-27b 48 |
| with passage | E | 2.06 | -0.11 | -0.49 to +0.19 | gemma4-31b 409, qwen3.5-27b 52 |
| with passage | F | 2.28 | +0.11 | -0.35 to +0.60 | gemma4-31b 408, qwen3.5-27b 51, gpt-oss-20b 1, deepseek-r1-14b 1 |
| without passage | A | 32.62 | | | gemma4-31b 461 |
| without passage | R | 32.94 | +0.33 | -1.27 to +1.90 | qwen3.5-27b 267, gemma4-31b 187, deepseek-r1-14b 3, gpt-oss-20b 2, qwen2.5-32b 2 |
| without passage | D | 32.65 | +0.03 | -1.55 to +1.60 | qwen3.5-27b 261, gemma4-31b 200 |
| without passage | E | 32.89 | +0.27 | -1.30 to +1.82 | qwen3.5-27b 273, gemma4-31b 188 |
| without passage | F | 32.81 | +0.19 | -1.41 to +1.76 | qwen3.5-27b 268, gemma4-31b 184, deepseek-r1-14b 4, gpt-oss-20b 3, qwen2.5-32b 2 |

### What split 1 chose (cells of 50+ questions)

- **with passage:** A = gemma4-31b (0.71); best genre guesser = qwen3.5-27b; table: HISTORY gemma4-31b 0.17; ARTS gemma4-31b 0.63; SCIENCE gemma4-31b 2.24; GEOGRAPHY gemma4-31b 0.0; genres without a table cell fall back to A.
- **without passage:** A = gemma4-31b (31.21); best genre guesser = qwen3.5-27b; table: HISTORY qwen3.5-27b 30.78; ARTS gemma4-31b 35.97; SCIENCE qwen3.5-27b 25.37; GEOGRAPHY gemma4-31b 24.55; genres without a table cell fall back to A.

## How much one split can vary: 200 more random splits, each used in both directions (400 runs)

Point estimates only (no bootstrap). Difference = route minus A on the test half.

| Condition | Route | Mean difference | Middle 95% of runs | Route better (below 0) | Same | Route worse |
|---|---|---|---|---|---|---|
| with passage | R | +0.06 | -0.54 to +0.44 | 14% | 32% | 54% |
| with passage | D | +0.06 | -0.54 to +0.44 | 11% | 38% | 51% |
| with passage | E | +0.07 | -0.52 to +0.44 | 11% | 38% | 52% |
| with passage | F | +1.14 | -0.08 to +2.64 | 5% | 2% | 94% |
| without passage | R | -0.09 | -1.68 to +1.33 | 56% | 2% | 41% |
| without passage | D | -0.03 | -1.65 to +1.25 | 44% | 18% | 38% |
| without passage | E | -0.18 | -1.68 to +1.25 | 55% | 18% | 26% |
| without passage | F | +0.43 | -1.23 to +2.09 | 28% | 1% | 71% |
