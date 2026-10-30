# Plan: the GenreHalluEval split experiment (exploratory)

Written 2026-10-27, before any split run. The design was decided by Mahdi Hasan Qurishi; the code was written by
Claude.

## Why

The registered test on Dataset 2 found no benefit from genre routing (H1 and H2 not supported). One possible reason
is that the two datasets differ: BenHalluEval questions come from TyDi QA, while GenreHalluEval questions were written
by the team. This experiment learns and tests the routes inside GenreHalluEval itself, so the two datasets cannot
differ. (A split inside BenHalluEval, made from saved runs, is in `results/split_experiment/`.)

**Status:** exploratory. It was added after the confirmatory result, so it can never replace H1 or H2. It uses
Dataset 2 to make choices, but only within this experiment and only on the learn half.

## Design (fixed before any run)

- **Data:** GenreHalluEval v1.1, 250 questions, split by `src/split/build_split.py` (seed 2026, stratified by our
  genre):
  - **Learn half:** 25 questions per genre (125 questions, 625 answers). Every answer is judged both with and
    without the passage.
  - **Test half:** the other 125 questions. Each question is judged in one condition: with the passage 13 or 12 per
    genre (63 questions, 315 answers), without it 62 questions (310 answers).
  - The package is `data/final/GenreHalluEval-split-v1/`.
- **Pool:** deepseek-r1-14b, gemma4-31b, gpt-oss-20b and qwen3.5-27b (English prompts), and tigerllm-9b (Bangla
  prompts `genre_bn_v1`, `judge_bn_v1` and `judge_noctx_bn_v1`, with the Bangla-aware parse and 16 new tokens per
  reply, as in its Bangla-prompt BenHalluEval run). llama3.1-8b, mistral-nemo-12b, qwen2.5-32b and gemma2-27b are not
  run (Mahdi's choice).
  - This breaks golden rule 6 (the same prompt for every judge) on purpose, for TigerLLM only. Report it.
- **Settings:** the same as every earlier run: Ollama 0.40.6, temperature 0, seed 2026, strict parsing; no_answer
  counts as an error.
- **Labels:** the agreed passage labels (`data/labels/dataset2/passage_labels_agreed_v1.csv`), in both conditions.
- **Genres:** the v1.1 majority vote. The 17 questions waiting for their genre relabel are included with their current
  genre: 9 are in the learn half and 8 in the test half.
- **Choices made on the learn half** (`src/split/make_split_lock.py`, output `lock_split_v1.json`). These are the
  rules of lock v1 and v2, with one change:
  - A = the lowest overall BHS.
  - The best genre guesser is the LLM that agrees most often with our genre.
  - The judge × genre table and the own-genre cells as before.
  - R = best path, as before.
  - Ties go to the judge with the lower overall BHS.
  - A judge with no_answer on half or more of the answers in both conditions is dropped.
  - **The change: a cell needs 20 or more questions, instead of 50.** A half has only 25 questions per genre, so the
    old minimum would leave no cell.
- **Tests on the test half:**
  - Main: R vs A with the passage and R vs A without it. Paired bootstrap over test questions (10,000 re-samples,
    seed 2026), two-sided p, Holm over the 2 tests.
  - Also reported: D, E and F vs A; both conditions together; and how often A's judge gives the same verdict in the two
    test notebooks.
  - Scoring: `src/dataset2/compare_routes.py --dataset ghesplit_test --package data/final/GenreHalluEval-split-v1
    --items test_items.csv --labels data/labels/dataset2/passage_labels_agreed_v1.csv --out results/split_ghe`.

## Limits, stated before the run

- **Low power.** The test half has 63 questions with the passage and 62 without it. With the passage, the best judge
  made 5 errors in 875 answers on Dataset 2, so there is almost no room to improve. Expect 95% ranges of about ±3–4
  BHS points with the passage and about ±6–8 without it. Only very large effects can show up.
- **One split.** A single split of 125 questions can be lucky or unlucky. The BenHalluEval split experiment shows how
  much one split can vary.

## Cost (estimate)

| Run | Calls | GPU hours |
|---|---|---|
| Learn half | 5 judges × (1,250 judge + 125 genre) = 6,875 | about 5 (deepseek-r1-14b about 2) |
| Test half, routed | about 300–500 genre calls and 700–900 judge calls | about 1.5 |
| Test half, single best | 625 judge calls | about 0.5 |

These are estimates from each model's measured BenHalluEval speed.
