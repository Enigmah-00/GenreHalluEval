# English vs Bangla prompts (side experiment, exploratory)

Models with both runs: banglallama-13b, llama3.1-8b, tigerllm-9b, titullm-3b, titullm-3b-instruct. Same 4,600 answers;
only the prompt language differs. BHS: lower is better. bn_minus_en < 0 means Bangla prompts help. The range is
a paired bootstrap over questions (1,000 re-samples). Built by `src/bench/compare_prompt_language.py`.

## Judging

| model | condition | BHS_en | BHS_bn | bn_minus_en | range95 | no_answer_en | no_answer_bn | BHS_answered_en | BHS_answered_bn | says_yes_en | says_yes_bn | same_verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| banglallama-13b | context | 100.00 | 100.00 | +0.00 | +0.00 to +0.00 | 4600 | 4600 | – | – | 0% | 0% | 100% |
| banglallama-13b | no_context | 100.00 | 100.00 | +0.00 | +0.00 to +0.00 | 4600 | 4600 | – | – | 0% | 0% | 100% |
| llama3.1-8b | context | 36.71 | 66.48 | +29.77 | +27.72 to +31.66 | 0 | 19 | 36.71 | 66.39 | 34% | 36% | 51% |
| llama3.1-8b | no_context | 45.98 | 50.67 | +4.69 | +3.15 to +6.15 | 0 | 0 | 45.98 | 50.67 | 40% | 6% | 59% |
| tigerllm-9b | context | 38.82 | 37.35 | -1.47 | -2.98 to +0.15 | 0 | 0 | 38.82 | 37.35 | 32% | 45% | 78% |
| tigerllm-9b | no_context | 44.80 | 39.97 | -4.82 | -6.35 to -3.34 | 0 | 0 | 44.80 | 39.97 | 20% | 53% | 64% |
| titullm-3b | context | 100.00 | 100.00 | +0.00 | +0.00 to +0.00 | 4600 | 4600 | – | – | 0% | 0% | 100% |
| titullm-3b | no_context | 100.00 | 100.00 | +0.00 | +0.00 to +0.00 | 4600 | 4600 | – | – | 0% | 0% | 100% |
| titullm-3b-instruct | context | 100.00 | 62.55 | -37.45 | -38.65 to -36.28 | 4600 | 1141 | – | 50.11 | 0% | 74% | 25% |
| titullm-3b-instruct | no_context | 100.00 | 52.45 | -47.55 | -48.60 to -46.51 | 4600 | 267 | – | 49.52 | 0% | 75% | 6% |

## Genre guessing

| model | accuracy_en | accuracy_bn | kappa_en | kappa_bn | kappa_blind_en | kappa_blind_bn | no_answer_en | no_answer_bn | named_HISTORY_en | named_HISTORY_bn |
|---|---|---|---|---|---|---|---|---|---|---|
| banglallama-13b | 0.0 | 0.0 | 0.000 | 0.000 | 0.000 | 0.000 | 920 | 920 | 0 | 0 |
| llama3.1-8b | 73.4 | 81.1 | 0.634 | 0.749 | 0.603 | 0.698 | 0 | 0 | 513 | 386 |
| tigerllm-9b | 76.8 | 75.8 | 0.689 | 0.678 | 0.656 | 0.646 | 1 | 1 | 474 | 441 |
| titullm-3b | 0.0 | 0.0 | 0.000 | 0.000 | 0.000 | 0.000 | 920 | 920 | 0 | 0 |
| titullm-3b-instruct | 0.0 | 26.0 | 0.000 | 0.091 | 0.000 | 0.084 | 920 | 330 | 0 | 522 |

## Judging per genre (our genres)

| model | condition | genre | questions | BHS_en | BHS_bn | bn_minus_en |
|---|---|---|---|---|---|---|
| banglallama-13b | context | HISTORY | 290 | 100.00 | 100.00 | +0.00 |
| banglallama-13b | context | ARTS | 278 | 100.00 | 100.00 | +0.00 |
| banglallama-13b | context | SCIENCE | 135 | 100.00 | 100.00 | +0.00 |
| banglallama-13b | context | GEOGRAPHY | 110 | 100.00 | 100.00 | +0.00 |
| banglallama-13b | context | RELIGION | 95 | 100.00 | 100.00 | +0.00 |
| banglallama-13b | no_context | HISTORY | 290 | 100.00 | 100.00 | +0.00 |
| banglallama-13b | no_context | ARTS | 278 | 100.00 | 100.00 | +0.00 |
| banglallama-13b | no_context | SCIENCE | 135 | 100.00 | 100.00 | +0.00 |
| banglallama-13b | no_context | GEOGRAPHY | 110 | 100.00 | 100.00 | +0.00 |
| banglallama-13b | no_context | RELIGION | 95 | 100.00 | 100.00 | +0.00 |
| llama3.1-8b | context | HISTORY | 290 | 35.56 | 67.93 | +32.37 |
| llama3.1-8b | context | ARTS | 278 | 37.72 | 66.82 | +29.09 |
| llama3.1-8b | context | SCIENCE | 135 | 39.07 | 64.44 | +25.37 |
| llama3.1-8b | context | GEOGRAPHY | 110 | 34.43 | 68.64 | +34.20 |
| llama3.1-8b | context | RELIGION | 95 | 36.84 | 61.84 | +25.00 |
| llama3.1-8b | no_context | HISTORY | 290 | 45.13 | 51.25 | +6.12 |
| llama3.1-8b | no_context | ARTS | 278 | 48.83 | 50.00 | +1.17 |
| llama3.1-8b | no_context | SCIENCE | 135 | 44.91 | 51.20 | +6.30 |
| llama3.1-8b | no_context | GEOGRAPHY | 110 | 40.34 | 50.80 | +10.45 |
| llama3.1-8b | no_context | RELIGION | 95 | 47.37 | 50.13 | +2.76 |
| tigerllm-9b | context | HISTORY | 290 | 38.32 | 33.66 | -4.66 |
| tigerllm-9b | context | ARTS | 278 | 39.66 | 40.38 | +0.72 |
| tigerllm-9b | context | SCIENCE | 135 | 38.80 | 36.94 | -1.85 |
| tigerllm-9b | context | GEOGRAPHY | 110 | 32.95 | 33.18 | +0.23 |
| tigerllm-9b | context | RELIGION | 95 | 44.08 | 44.74 | +0.66 |
| tigerllm-9b | no_context | HISTORY | 290 | 43.97 | 39.27 | -4.70 |
| tigerllm-9b | no_context | ARTS | 278 | 46.09 | 42.00 | -4.09 |
| tigerllm-9b | no_context | SCIENCE | 135 | 47.50 | 38.43 | -9.07 |
| tigerllm-9b | no_context | GEOGRAPHY | 110 | 39.20 | 38.18 | -1.02 |
| tigerllm-9b | no_context | RELIGION | 95 | 46.05 | 41.32 | -4.74 |
| titullm-3b | context | HISTORY | 290 | 100.00 | 100.00 | +0.00 |
| titullm-3b | context | ARTS | 278 | 100.00 | 100.00 | +0.00 |
| titullm-3b | context | SCIENCE | 135 | 100.00 | 100.00 | +0.00 |
| titullm-3b | context | GEOGRAPHY | 110 | 100.00 | 100.00 | +0.00 |
| titullm-3b | context | RELIGION | 95 | 100.00 | 100.00 | +0.00 |
| titullm-3b | no_context | HISTORY | 290 | 100.00 | 100.00 | +0.00 |
| titullm-3b | no_context | ARTS | 278 | 100.00 | 100.00 | +0.00 |
| titullm-3b | no_context | SCIENCE | 135 | 100.00 | 100.00 | +0.00 |
| titullm-3b | no_context | GEOGRAPHY | 110 | 100.00 | 100.00 | +0.00 |
| titullm-3b | no_context | RELIGION | 95 | 100.00 | 100.00 | +0.00 |
| titullm-3b-instruct | context | HISTORY | 290 | 100.00 | 61.59 | -38.41 |
| titullm-3b-instruct | context | ARTS | 278 | 100.00 | 66.50 | -33.50 |
| titullm-3b-instruct | context | SCIENCE | 135 | 100.00 | 61.11 | -38.89 |
| titullm-3b-instruct | context | GEOGRAPHY | 110 | 100.00 | 59.55 | -40.45 |
| titullm-3b-instruct | context | RELIGION | 95 | 100.00 | 60.13 | -39.87 |
| titullm-3b-instruct | no_context | HISTORY | 290 | 100.00 | 52.54 | -47.46 |
| titullm-3b-instruct | no_context | ARTS | 278 | 100.00 | 53.78 | -46.22 |
| titullm-3b-instruct | no_context | SCIENCE | 135 | 100.00 | 53.33 | -46.67 |
| titullm-3b-instruct | no_context | GEOGRAPHY | 110 | 100.00 | 50.57 | -49.43 |
| titullm-3b-instruct | no_context | RELIGION | 95 | 100.00 | 50.00 | -50.00 |

