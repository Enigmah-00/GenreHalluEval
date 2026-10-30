# Lock for GenreHalluEval v2 (lock_ghe2_v1)

Created 2026-10-30T00:50:05+00:00 by `src/genrehallueval_v2/make_lock_v2.py` from the learn half only (600 questions, 3000 answers, each judged with and without the passage). sha256 `88da7af7d073e60600afb1ea6f3bc27f022dd89c1d109c377a63b4396bd77ae4`.

- Pool: deepseek-r1-14b (en), gemma4-31b (en), gpt-oss-20b (en), qwen3.5-27b (en), tigerllm-9b (bn); usable: deepseek-r1-14b, gemma4-31b, gpt-oss-20b, qwen3.5-27b, tigerllm-9b; excluded: none
- Cells need 50+ questions.

## With the passage

- A = gemma4-31b; best genre guesser = gemma4-31b; askers = gemma4-31b, qwen3.5-27b
- Overall BHS: gemma4-31b 0.33, qwen3.5-27b 0.88, gpt-oss-20b 4.15, deepseek-r1-14b 20.98, tigerllm-9b 36.12

| Genre | Table judge | BHS | Questions |
|---|---|---|---|
| HISTORY | gemma4-31b | 0.0 | 50 |
| POLITICS | qwen3.5-27b | 0.5 | 50 |
| EDUCATION | gemma4-31b | 0.25 | 50 |
| ARTS | gemma4-31b | 0.5 | 50 |
| CULTURE | gemma4-31b | 0.5 | 50 |
| SPORTS | gemma4-31b | 0.0 | 50 |
| SCIENCE | gemma4-31b | 0.25 | 50 |
| TECHNOLOGY | gemma4-31b | 0.0 | 50 |
| GEOGRAPHY | gemma4-31b | 0.25 | 50 |
| PLACES | gemma4-31b | 0.5 | 50 |
| RELIGION | gemma4-31b | 0.0 | 50 |
| GRAMMAR | gemma4-31b | 0.5 | 50 |
| OTHER | gemma4-31b | – (A) | 0 |

Own-genre cells: deepseek-r1-14b HISTORY 23.9286 (105); deepseek-r1-14b CULTURE 13.7255 (51); deepseek-r1-14b SCIENCE 18.2692 (52); deepseek-r1-14b GRAMMAR 18.75 (52); gemma4-31b HISTORY 0.0 (63); gemma4-31b EDUCATION 0.25 (50); gemma4-31b SCIENCE 0.25 (50); gemma4-31b TECHNOLOGY 0.0 (50); gemma4-31b PLACES 0.5 (50); gemma4-31b GRAMMAR 0.4808 (52); gpt-oss-20b HISTORY 3.8732 (142); gpt-oss-20b CULTURE 2.9545 (55); gpt-oss-20b SCIENCE 3.9216 (51); qwen3.5-27b HISTORY 0.3731 (67); qwen3.5-27b EDUCATION 0.75 (50); qwen3.5-27b ARTS 0.75 (50); qwen3.5-27b SCIENCE 0.75 (50); qwen3.5-27b TECHNOLOGY 0.9804 (51); qwen3.5-27b GRAMMAR 3.3482 (56); tigerllm-9b HISTORY 29.3367 (147); tigerllm-9b CULTURE 46.8137 (51); tigerllm-9b SCIENCE 37.2807 (57); tigerllm-9b GEOGRAPHY 29.1016 (64)

## Without the passage

- A = gemma4-31b; best genre guesser = gemma4-31b; askers = deepseek-r1-14b, gemma4-31b, gpt-oss-20b, qwen3.5-27b
- Overall BHS: gemma4-31b 21.96, qwen3.5-27b 23.1, deepseek-r1-14b 29.79, gpt-oss-20b 32.44, tigerllm-9b 40.92

| Genre | Table judge | BHS | Questions |
|---|---|---|---|
| HISTORY | gemma4-31b | 16.0 | 50 |
| POLITICS | qwen3.5-27b | 21.25 | 50 |
| EDUCATION | qwen3.5-27b | 33.75 | 50 |
| ARTS | gemma4-31b | 28.5 | 50 |
| CULTURE | gemma4-31b | 20.0 | 50 |
| SPORTS | qwen3.5-27b | 25.75 | 50 |
| SCIENCE | qwen3.5-27b | 10.5 | 50 |
| TECHNOLOGY | qwen3.5-27b | 15.5 | 50 |
| GEOGRAPHY | qwen3.5-27b | 18.75 | 50 |
| PLACES | gemma4-31b | 19.25 | 50 |
| RELIGION | gemma4-31b | 11.75 | 50 |
| GRAMMAR | gemma4-31b | 23.0 | 50 |
| OTHER | gemma4-31b | – (A) | 0 |

Own-genre cells: deepseek-r1-14b HISTORY 27.7381 (105); deepseek-r1-14b CULTURE 41.9118 (51); deepseek-r1-14b SCIENCE 21.3942 (52); deepseek-r1-14b GRAMMAR 33.4135 (52); gemma4-31b HISTORY 15.6746 (63); gemma4-31b EDUCATION 36.75 (50); gemma4-31b SCIENCE 15.25 (50); gemma4-31b TECHNOLOGY 16.75 (50); gemma4-31b PLACES 19.5 (50); gemma4-31b GRAMMAR 22.3558 (52); gpt-oss-20b HISTORY 27.2887 (142); gpt-oss-20b CULTURE 35.6818 (55); gpt-oss-20b SCIENCE 21.0784 (51); qwen3.5-27b HISTORY 15.8582 (67); qwen3.5-27b EDUCATION 33.5 (50); qwen3.5-27b ARTS 32.5 (50); qwen3.5-27b SCIENCE 10.25 (50); qwen3.5-27b TECHNOLOGY 15.1961 (51); qwen3.5-27b GRAMMAR 28.3482 (56); tigerllm-9b HISTORY 36.8197 (147); tigerllm-9b CULTURE 44.8529 (51); tigerllm-9b SCIENCE 38.8158 (57); tigerllm-9b GEOGRAPHY 39.2578 (64)

