# Locked choices for Dataset 2, v2 (GenreHalluEval)

Created 2026-10-27T07:05:45+00:00 by `src/routing/make_lock_v2.py`. sha256 of `lock_v2.json`: `6d3c1d29cb8159d5f74300c799ce040c9a7c737dfb68b5c292a2a2aa948c9137`. Based on lock v1 (`779cc5a7cdc2…`), whose choices are all unchanged.

**New: route R (best path).** candidates: the our-genre path (best genre guesser names the genre -> judge x genre table judge, scored by that cell's BHS; no cell -> A, scored by A's overall BHS) and the own-genre paths of the askers (asker names the genre -> that asker, scored by its own-genre cell's BHS; cells under 50 questions not used); pick the lowest score; tie -> lower overall BHS. The genre prompt always gets question + passage, never the answer.

## context

- A = gemma4-31b (BHS 1.44); best genre guesser = qwen3.5-27b
- our-genre path: HISTORY → gemma4-31b (1.03), ARTS → qwen3.5-27b (1.62), SCIENCE → gemma4-31b (2.04), GEOGRAPHY → gemma4-31b (0.23), RELIGION → qwen3.5-27b (1.97)
- LLMs asked for the genre: gemma4-31b, qwen3.5-27b (own-genre cells below 2.04)
- own-genre cells that can win: gemma4-31b ARTS (1.64), gemma4-31b GEOGRAPHY (0.37), gemma4-31b HISTORY (1.05), gemma4-31b SCIENCE (1.82), qwen3.5-27b ARTS (1.79), qwen3.5-27b GEOGRAPHY (0.90), qwen3.5-27b HISTORY (1.83), qwen3.5-27b RELIGION (1.53)
- BenHalluEval check (R minus A, 95% range): same data [-0.1, -0.49, 0.27], 5-fold [0.0, -0.3, 0.3]

## no_context

- A = gemma4-31b (BHS 31.92); best genre guesser = qwen3.5-27b
- our-genre path: HISTORY → qwen3.5-27b (31.29), ARTS → gemma4-31b (36.74), SCIENCE → gemma4-31b (26.48), GEOGRAPHY → gemma4-31b (27.05), RELIGION → qwen3.5-27b (28.42)
- LLMs asked for the genre: deepseek-r1-14b, gemma2-27b, gemma4-31b, gpt-oss-20b, qwen2.5-32b, qwen3.5-27b (own-genre cells below 36.74)
- own-genre cells that can win: deepseek-r1-14b GEOGRAPHY (33.82), deepseek-r1-14b RELIGION (34.33), deepseek-r1-14b SCIENCE (34.72), gemma2-27b GEOGRAPHY (33.38), gemma2-27b RELIGION (36.67), gemma2-27b SCIENCE (34.51), gemma4-31b ARTS (36.61), gemma4-31b GEOGRAPHY (26.36), gemma4-31b HISTORY (32.19), gemma4-31b RELIGION (29.79), gemma4-31b SCIENCE (26.48), gpt-oss-20b GEOGRAPHY (35.70), gpt-oss-20b RELIGION (34.32), gpt-oss-20b SCIENCE (35.36), qwen2.5-32b GEOGRAPHY (35.89), qwen2.5-32b HISTORY (36.50), qwen2.5-32b RELIGION (33.06), qwen2.5-32b SCIENCE (35.25), qwen3.5-27b GEOGRAPHY (32.86), qwen3.5-27b HISTORY (30.92), qwen3.5-27b RELIGION (28.70), qwen3.5-27b SCIENCE (27.97)
- BenHalluEval check (R minus A, 95% range): same data [-0.33, -1.4, 0.72], 5-fold [0.45, -0.6, 1.56]

## Confirmatory tests on Dataset 2

- R vs A with the passage; R vs A without it; Holm over 2 at α = 0.05.
- Everything else is exploratory.
