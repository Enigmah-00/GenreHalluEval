# GenreHalluEval v2: learn half report (descriptive; the routes are in lock_ghe2_v1.json)

Lock sha256 `88da7af7d073e60600afb1ea6f3bc27f022dd89c1d109c377a63b4396bd77ae4`. 600 learn questions (50 per genre), 3000 answers, each judged with and without the passage. Labels: `data/labels/genrehallueval_v2/labels_v2.0.csv`. BHS: lower is better; 50 = chance.

## 0. Routing at a glance

Gap = runner-up minus best, 95% range over question re-samples; 'clear' when the range excludes 0. Own-genre best = the lowest score of any LLM inside the genre it named itself (cells of 50+ questions).

### With the passage (A = gemma4-31b)

| Genre | Best (ours) | Runner-up | Gap | Own-genre best | Its own vs ours | Clearly better in own genre |
|---|---|---|---|---|---|---|
| HISTORY | gemma4-31b 0.00 | qwen3.5-27b 0.50 | +0.00 to +1.25 | gemma4-31b 0.00 (63 q) | 0.00 vs 0.00 | none |
| POLITICS | qwen3.5-27b 0.50 | gemma4-31b 1.25 | -0.75 to +3.00 | none (no cell of 50+) | – | none |
| EDUCATION | gemma4-31b 0.25 | qwen3.5-27b 0.75 | +0.00 to +1.25 | gemma4-31b 0.25 (50 q) | 0.25 vs 0.25 | none |
| ARTS | gemma4-31b 0.50 | qwen3.5-27b 0.75 | -0.75 to +1.50 | qwen3.5-27b 0.75 (50 q) | 0.75 vs 0.75 | none |
| CULTURE | gemma4-31b 0.50 | qwen3.5-27b 1.25 | +0.00 to +2.00 | gpt-oss-20b 2.95 (55 q) | 2.95 vs 1.75 | none |
| SPORTS | gemma4-31b 0.00 | qwen3.5-27b 0.25 | +0.00 to +0.75 | none (no cell of 50+) | – | none |
| SCIENCE | gemma4-31b 0.25 | qwen3.5-27b 0.75 | +0.00 to +1.25 | gemma4-31b 0.25 (50 q) | 0.25 vs 0.25 | none |
| TECHNOLOGY | gemma4-31b 0.00 | qwen3.5-27b 1.00 | +0.25 to +2.00 clear | gemma4-31b 0.00 (50 q) | 0.00 vs 0.00 | none |
| GEOGRAPHY | gemma4-31b 0.25 | qwen3.5-27b 0.25 | -0.75 to +0.75 | tigerllm-9b 29.10 (64 q) | 29.10 vs 34.50 | none |
| PLACES | gemma4-31b 0.50 | qwen3.5-27b 0.75 | -0.50 to +1.25 | gemma4-31b 0.50 (50 q) | 0.50 vs 0.50 | none |
| RELIGION | gemma4-31b 0.00 | qwen3.5-27b 0.00 | +0.00 to +0.00 | none (no cell of 50+) | – | none |
| GRAMMAR | gemma4-31b 0.50 | qwen3.5-27b 3.75 | +1.50 to +5.00 clear | gemma4-31b 0.48 (52 q) | 0.48 vs 0.50 | none |

### Without the passage (A = gemma4-31b)

| Genre | Best (ours) | Runner-up | Gap | Own-genre best | Its own vs ours | Clearly better in own genre |
|---|---|---|---|---|---|---|
| HISTORY | gemma4-31b 16.00 | qwen3.5-27b 19.50 | -1.75 to +8.75 | gemma4-31b 15.67 (63 q) | 15.67 vs 16.00 | none |
| POLITICS | qwen3.5-27b 21.25 | deepseek-r1-14b 23.50 | -5.25 to +9.50 | none (no cell of 50+) | – | none |
| EDUCATION | qwen3.5-27b 33.75 | deepseek-r1-14b 35.75 | -4.75 to +9.00 | qwen3.5-27b 33.50 (50 q) | 33.50 vs 33.75 | none |
| ARTS | gemma4-31b 28.50 | qwen3.5-27b 32.50 | -3.25 to +11.25 | qwen3.5-27b 32.50 (50 q) | 32.50 vs 32.50 | none |
| CULTURE | gemma4-31b 20.00 | qwen3.5-27b 26.00 | +0.75 to +11.25 clear | gpt-oss-20b 35.68 (55 q) | 35.68 vs 30.75 | none |
| SPORTS | qwen3.5-27b 25.75 | gemma4-31b 28.25 | -3.50 to +9.00 | none (no cell of 50+) | – | none |
| SCIENCE | qwen3.5-27b 10.50 | gemma4-31b 15.50 | -0.75 to +10.25 | qwen3.5-27b 10.25 (50 q) | 10.25 vs 10.50 | none |
| TECHNOLOGY | qwen3.5-27b 15.50 | deepseek-r1-14b 16.25 | -5.00 to +6.25 | qwen3.5-27b 15.20 (51 q) | 15.20 vs 15.50 | none |
| GEOGRAPHY | qwen3.5-27b 18.75 | gemma4-31b 23.75 | -0.25 to +10.50 | tigerllm-9b 39.26 (64 q) | 39.26 vs 43.25 | none |
| PLACES | gemma4-31b 19.25 | qwen3.5-27b 27.25 | +0.50 to +15.25 clear | gemma4-31b 19.50 (50 q) | 19.50 vs 19.25 | none |
| RELIGION | gemma4-31b 11.75 | qwen3.5-27b 16.50 | -1.50 to +10.75 | none (no cell of 50+) | – | none |
| GRAMMAR | gemma4-31b 23.00 | qwen3.5-27b 30.00 | -0.75 to +14.25 | gemma4-31b 22.36 (52 q) | 22.36 vs 23.00 | none |

## 1. Overall scores, genre agreement and no_answer

| LLM | Prompts | BHS with passage | BHS without | Genre agrees with ours | Genre no_answer | no_answer with / without |
|---|---|---|---|---|---|---|
| deepseek-r1-14b | en | 20.98 | 29.79 | 74.0% | 47 | 578 / 11 |
| gemma4-31b | en | 0.33 | 21.96 | 94.7% | 0 | 0 / 0 |
| gpt-oss-20b | en | 4.15 | 32.44 | 72.8% | 0 | 1 / 31 |
| qwen3.5-27b | en | 0.88 | 23.1 | 94.3% | 0 | 0 / 0 |
| tigerllm-9b | bn | 36.12 | 40.92 | 69.7% | 3 | 0 / 0 |

## 2. The routes in the lock

- context: A = gemma4-31b; best genre guesser = gemma4-31b; askers = gemma4-31b, qwen3.5-27b; highest our-genre cell = 0.5; own-genre cells that can win: gemma4-31b HISTORY 0.00, gemma4-31b EDUCATION 0.25, gemma4-31b SCIENCE 0.25, gemma4-31b TECHNOLOGY 0.00, gemma4-31b PLACES 0.50, gemma4-31b GRAMMAR 0.48, qwen3.5-27b HISTORY 0.37
- no_context: A = gemma4-31b; best genre guesser = gemma4-31b; askers = deepseek-r1-14b, gemma4-31b, gpt-oss-20b, qwen3.5-27b; highest our-genre cell = 33.75; own-genre cells that can win: deepseek-r1-14b HISTORY 27.74, deepseek-r1-14b SCIENCE 21.39, deepseek-r1-14b GRAMMAR 33.41, gemma4-31b HISTORY 15.67, gemma4-31b SCIENCE 15.25, gemma4-31b TECHNOLOGY 16.75, gemma4-31b PLACES 19.50, gemma4-31b GRAMMAR 22.36, gpt-oss-20b HISTORY 27.29, gpt-oss-20b SCIENCE 21.08, qwen3.5-27b HISTORY 15.86, qwen3.5-27b EDUCATION 33.50, qwen3.5-27b ARTS 32.50, qwen3.5-27b SCIENCE 10.25, qwen3.5-27b TECHNOLOGY 15.20, qwen3.5-27b GRAMMAR 28.35

## 3. Cost (learn half)

| LLM | Calls | Prompt tokens | Output tokens | Model busy time |
|---|---|---|---|---|
| deepseek-r1-14b | 6,600 | 3,904,848 | 1,567,606 | 9.78 h |
| gemma4-31b | 6,600 | 1,968,500 | 13,633 | 3.16 h |
| gpt-oss-20b | 6,600 | 3,107,861 | 755,699 | 3.11 h |
| qwen3.5-27b | 6,600 | 2,600,100 | 14,178 | 2.46 h |
| tigerllm-9b | 6,600 | 2,156,900 | 16,965 | 1.33 h |
| total | 33,000 | 13,738,209 | 2,368,081 | 19.84 h |
