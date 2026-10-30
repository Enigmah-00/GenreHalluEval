# GenreHalluEval v2 test half: routes E, F, R vs the single best judge A

Lock `lock_ghe2_v1.json` (sha256 `88da7af7…`); test plan `test_plan_v2.json` (sha256 `beab2a43…`, decided 2026-10-30). Labels: `data/labels/genrehallueval_v2/labels_v2.0.csv`.
BHS: lower is better; 50 = chance. Difference = route minus A (below 0 = the route is better).

## Main tests (6, Holm-corrected)

| Test | Condition | Questions | Route BHS | A BHS | Difference | 95% range | p | p (Holm) | Result |
|---|---|---|---|---|---|---|---|---|---|
| E vs A | context | 300 | 0.21 | 0.29 | -0.08 | -0.21 to +0.00 | 0.2618 | 1.0000 | no clear difference; not significant |
| E vs A | no_context | 300 | 20.96 | 21.17 | -0.21 | -1.88 to +1.46 | 0.8468 | 1.0000 | no clear difference; not significant |
| F vs A | context | 300 | 4.38 | 0.29 | +4.08 | +2.71 to +5.67 | 0.0000 | 0.0000 | route clearly worse; significant |
| F vs A | no_context | 300 | 24.54 | 21.17 | +3.38 | +1.33 to +5.46 | 0.0012 | 0.0060 | route clearly worse; significant |
| R vs A | context | 300 | 0.21 | 0.29 | -0.08 | -0.21 to +0.00 | 0.2618 | 1.0000 | no clear difference; not significant |
| R vs A | no_context | 300 | 21.67 | 21.17 | +0.50 | -1.33 to +2.29 | 0.5970 | 1.0000 | no clear difference; not significant |

## BHS of each route

| Condition | Route | BHS | Answers | Questions | no_answer | Judges used |
|---|---|---|---|---|---|---|
| context | A | 0.29 | 1500 | 300 | 0 | gemma4-31b 1500 |
| context | E | 0.21 | 1500 | 300 | 0 | gemma4-31b 1375, qwen3.5-27b 125 |
| context | F | 4.38 | 1500 | 300 | 1 | gemma4-31b 930, gpt-oss-20b 210, tigerllm-9b 170, qwen3.5-27b 155, deepseek-r1-14b 35 |
| context | R | 0.21 | 1500 | 300 | 0 | gemma4-31b 1360, qwen3.5-27b 140 |
| no_context | A | 21.17 | 1500 | 300 | 0 | gemma4-31b 1500 |
| no_context | E | 20.96 | 1500 | 300 | 0 | gemma4-31b 760, qwen3.5-27b 740 |
| no_context | F | 24.54 | 1500 | 300 | 3 | gemma4-31b 625, qwen3.5-27b 435, gpt-oss-20b 245, tigerllm-9b 145, deepseek-r1-14b 50 |
| no_context | R | 21.67 | 1500 | 300 | 0 | gemma4-31b 735, qwen3.5-27b 695, gpt-oss-20b 60, deepseek-r1-14b 10 |

## Each route vs A on all answers (each in its own condition; not corrected)

| Comparison | Answers | Questions | Difference | 95% range |
|---|---|---|---|---|
| E vs A | 3000 | 600 | -0.15 | -1.00 to +0.71 |
| F vs A | 3000 | 600 | +3.73 | +2.52 to +5.00 |
| R vs A | 3000 | 600 | +0.21 | -0.69 to +1.12 |

## BHS per genre (exploratory)

| Condition | Genre | Questions | A | E | F | R |
|---|---|---|---|---|---|---|
| context | Arts | 25 | 0.00 | 0.00 | 0.50 | 0.00 |
| context | Culture | 25 | 0.00 | 0.00 | 2.00 | 0.00 |
| context | Education | 25 | 0.00 | 0.00 | 0.00 | 0.00 |
| context | Geography | 25 | 0.00 | 0.00 | 24.00 | 0.00 |
| context | Grammar | 25 | 0.00 | 0.00 | 0.00 | 0.00 |
| context | History | 25 | 1.00 | 1.00 | 1.00 | 1.00 |
| context | Places | 25 | 0.00 | 0.00 | 0.00 | 0.00 |
| context | Politics | 25 | 1.00 | 0.00 | 7.00 | 0.00 |
| context | Religion | 25 | 1.00 | 1.00 | 14.50 | 1.00 |
| context | Science | 25 | 0.50 | 0.50 | 0.50 | 0.50 |
| context | Sports | 25 | 0.00 | 0.00 | 3.00 | 0.00 |
| context | Technology | 25 | 0.00 | 0.00 | 0.00 | 0.00 |
| no_context | Arts | 25 | 28.50 | 28.00 | 29.00 | 30.50 |
| no_context | Culture | 25 | 15.00 | 14.50 | 25.50 | 15.00 |
| no_context | Education | 25 | 23.50 | 31.00 | 33.50 | 35.00 |
| no_context | Geography | 25 | 21.50 | 21.00 | 38.00 | 21.00 |
| no_context | Grammar | 25 | 27.50 | 28.00 | 27.50 | 28.50 |
| no_context | History | 25 | 14.00 | 14.00 | 13.00 | 14.00 |
| no_context | Places | 25 | 29.00 | 29.00 | 29.00 | 29.00 |
| no_context | Politics | 25 | 29.00 | 25.50 | 26.00 | 25.50 |
| no_context | Religion | 25 | 19.00 | 17.50 | 23.50 | 18.50 |
| no_context | Science | 25 | 15.50 | 14.00 | 13.00 | 14.00 |
| no_context | Sports | 25 | 22.50 | 20.00 | 27.50 | 20.00 |
| no_context | Technology | 25 | 9.00 | 9.00 | 9.00 | 9.00 |

## Genre answers on the test half (agreement with our genre)

- route E: gemma4-31b 94.0% of 600
- route F: deepseek-r1-14b 70.5% of 600; gemma4-31b 94.0% of 600; gpt-oss-20b 71.7% of 600; qwen3.5-27b 94.7% of 600; tigerllm-9b 66.0% of 600
- route R: deepseek-r1-14b 35.7% of 600; gemma4-31b 94.0% of 600; gpt-oss-20b 34.7% of 600; qwen3.5-27b 94.7% of 600

## Checks

- Routes recomputed from the lock and the named genres: 0 differences (all equal).
- Answers with no verdict from their routed judge: {'A': 0, 'E': 0, 'F': 0, 'R': 0}. Empty genre answers in routes.csv: {'E': 0, 'F': 0, 'R': 0}.
- Determinism: 3270 (judge, answer) pairs were judged in more than one notebook; 3258 gave the same verdict everywhere (99.63%). It should be 100%.

## Cost of each route (every call in the saved logs)

| Route | Notebook | Turn | Calls | Prompt tokens | Output tokens | Sum of latencies (h) |
|---|---|---|---|---|---|---|
| A | single_best | judge | 3,000 | 548,460 | 6,000 | 2.47 |
| E | route_E | genre | 600 | 871,515 | 1,643 | 1.61 |
| E | route_E | judge | 3,000 | 586,347 | 6,000 | 2.26 |
| F | route_F | genre | 3,000 | 5,065,484 | 186,927 | 8.87 |
| F | route_F | judge | 3,000 | 670,084 | 83,219 | 3.38 |
| R | route_R | genre | 1,800 | 3,001,368 | 91,744 | 4.68 |
| R | route_R | judge | 3,000 | 592,957 | 15,990 | 2.53 |

- single_best: models gemma4-31b (ollama 0.40.6; digest 17ba34c06c801ba22f6047bab21ced9429c6d43e0e42ecf339b0f3e5a61e8d97; Q4_K_M); asked for the genre: {}; started 2026-10-30T06:56:17.161788+00:00, finished 2026-10-30T08:18:30.830025+00:00.
- route_E: models gemma4-31b (ollama 0.40.6; digest 17ba34c06c801ba22f6047bab21ced9429c6d43e0e42ecf339b0f3e5a61e8d97; Q4_K_M); qwen3.5-27b (ollama 0.40.6; digest 64ae5b1d651fb2709d5928ccb8dcfb4bb2cc9c2c8001ac34497e36a6cf905b59; Q4_K_M); asked for the genre: {'gemma4-31b': 600}; started 2026-10-30T06:27:35.550487+00:00, finished 2026-10-30T08:37:12.148752+00:00.
- route_F: models deepseek-r1-14b (ollama 0.40.6; digest c333b7232bdb521236694ffbb5f5a6b11cc45d98e9142c73123b670fca400b09; Q4_K_M); gpt-oss-20b (ollama 0.40.6; digest f38aa0c53da5f8c49d08c43a99df24ff53167fe68e24664a7777288e7656fdfe; MXFP4); qwen3.5-27b (ollama 0.40.6; digest 64ae5b1d651fb2709d5928ccb8dcfb4bb2cc9c2c8001ac34497e36a6cf905b59; Q4_K_M); tigerllm-9b (ollama 0.40.6; digest d2b91a15fc7e34289604835971cae670c5e31033b47c6e6dc1deaa5e6d2fea06; Q4_K_M); gemma4-31b (ollama 0.40.6; digest 17ba34c06c801ba22f6047bab21ced9429c6d43e0e42ecf339b0f3e5a61e8d97; Q4_K_M); asked for the genre: {'deepseek-r1-14b': 600, 'gemma4-31b': 600, 'gpt-oss-20b': 600, 'qwen3.5-27b': 600, 'tigerllm-9b': 600}; started 2026-10-30T06:31:40.634126+00:00, finished 2026-10-30T11:11:03.970032+00:00.
- route_R: models deepseek-r1-14b (ollama 0.40.6; digest c333b7232bdb521236694ffbb5f5a6b11cc45d98e9142c73123b670fca400b09; Q4_K_M); gpt-oss-20b (ollama 0.40.6; digest f38aa0c53da5f8c49d08c43a99df24ff53167fe68e24664a7777288e7656fdfe; MXFP4); qwen3.5-27b (ollama 0.40.6; digest 64ae5b1d651fb2709d5928ccb8dcfb4bb2cc9c2c8001ac34497e36a6cf905b59; Q4_K_M); gemma4-31b (ollama 0.40.6; digest 17ba34c06c801ba22f6047bab21ced9429c6d43e0e42ecf339b0f3e5a61e8d97; Q4_K_M); asked for the genre: {'deepseek-r1-14b': 300, 'gemma4-31b': 600, 'gpt-oss-20b': 300, 'qwen3.5-27b': 600}; started 2026-10-30T06:32:04.077103+00:00, finished 2026-10-30T09:54:28.672313+00:00.
