# Lock for the GenreHalluEval split experiment (lock_split_v1, exploratory)

Created 2026-10-27T23:14:37+00:00 by `src/split/make_split_lock.py` from the learn half only (125 questions, 625 answers, each judged with and without the passage). sha256 `2616eb9af63ec165833098743c2542a7cb54e15b0cd33ffa67d5b9910809f125`.

- Pool: deepseek-r1-14b (en), gemma4-31b (en), gpt-oss-20b (en), qwen3.5-27b (en), tigerllm-9b (bn); usable: deepseek-r1-14b, gemma4-31b, gpt-oss-20b, qwen3.5-27b, tigerllm-9b; excluded: none
- Cells need 20+ questions.

## With the passage

- A = qwen3.5-27b; best genre guesser = qwen3.5-27b; askers = gemma4-31b, qwen3.5-27b
- Overall BHS: qwen3.5-27b 0.6, gemma4-31b 0.7, gpt-oss-20b 6.4, deepseek-r1-14b 22.0, tigerllm-9b 33.6

| Genre | Table judge | BHS | Questions |
|---|---|---|---|
| HISTORY | qwen3.5-27b | 1.0 | 25 |
| ARTS | gemma4-31b | 0.0 | 25 |
| SCIENCE | gemma4-31b | 0.0 | 25 |
| GEOGRAPHY | qwen3.5-27b | 0.5 | 25 |
| RELIGION | qwen3.5-27b | 0.0 | 25 |
| OTHER | qwen3.5-27b | – (A) | 0 |

Own-genre cells: deepseek-r1-14b HISTORY 27.2436 (39); deepseek-r1-14b ARTS 19.8864 (22); deepseek-r1-14b SCIENCE 15.2174 (23); deepseek-r1-14b GEOGRAPHY 20.625 (20); deepseek-r1-14b RELIGION 23.2143 (21); gemma4-31b HISTORY 2.1552 (29); gemma4-31b ARTS 0.0 (22); gemma4-31b SCIENCE 0.0 (23); gemma4-31b RELIGION 0.4464 (28); gpt-oss-20b HISTORY 9.2105 (38); gpt-oss-20b ARTS 2.4038 (26); gpt-oss-20b SCIENCE 5.4348 (23); qwen3.5-27b HISTORY 0.8929 (28); qwen3.5-27b ARTS 1.0417 (24); qwen3.5-27b SCIENCE 0.4808 (26); qwen3.5-27b RELIGION 0.0 (29); tigerllm-9b HISTORY 38.8889 (36); tigerllm-9b SCIENCE 29.8913 (23); tigerllm-9b GEOGRAPHY 24.4048 (21); tigerllm-9b RELIGION 36.9565 (23)

## Without the passage

- A = gemma4-31b; best genre guesser = qwen3.5-27b; askers = deepseek-r1-14b, gemma4-31b, gpt-oss-20b, qwen3.5-27b, tigerllm-9b
- Overall BHS: gemma4-31b 23.0, qwen3.5-27b 23.8, deepseek-r1-14b 30.1, gpt-oss-20b 36.3, tigerllm-9b 38.7

| Genre | Table judge | BHS | Questions |
|---|---|---|---|
| HISTORY | qwen3.5-27b | 39.5 | 25 |
| ARTS | gemma4-31b | 31.0 | 25 |
| SCIENCE | gemma4-31b | 11.0 | 25 |
| GEOGRAPHY | gemma4-31b | 17.5 | 25 |
| RELIGION | qwen3.5-27b | 13.0 | 25 |
| OTHER | gemma4-31b | – (A) | 0 |

Own-genre cells: deepseek-r1-14b HISTORY 37.1795 (39); deepseek-r1-14b ARTS 39.2045 (22); deepseek-r1-14b SCIENCE 16.3043 (23); deepseek-r1-14b GEOGRAPHY 29.375 (20); deepseek-r1-14b RELIGION 23.2143 (21); gemma4-31b HISTORY 35.7759 (29); gemma4-31b ARTS 31.25 (22); gemma4-31b SCIENCE 10.8696 (23); gemma4-31b RELIGION 15.1786 (28); gpt-oss-20b HISTORY 45.3947 (38); gpt-oss-20b ARTS 41.3462 (26); gpt-oss-20b SCIENCE 26.087 (23); qwen3.5-27b HISTORY 35.2679 (28); qwen3.5-27b ARTS 33.8542 (24); qwen3.5-27b SCIENCE 12.0192 (26); qwen3.5-27b RELIGION 15.9483 (29); tigerllm-9b HISTORY 46.1806 (36); tigerllm-9b SCIENCE 25.0 (23); tigerllm-9b GEOGRAPHY 34.5238 (21); tigerllm-9b RELIGION 38.0435 (23)

