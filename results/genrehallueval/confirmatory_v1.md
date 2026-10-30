# GenreHalluEval: confirmatory result (R vs A), 2026-10-27

Scored with the agreed human labels (`data/labels/dataset2/passage_labels_agreed_v1.csv`; 0 excluded) by
`src/dataset2/compare_routes.py` on the two stored runs:
`runs/genrehallueval/genrehallueval__routed__full__outputs.zip` (sha256 `a23acc08…`) and
`runs/genrehallueval/genrehallueval__single_best__full__outputs.zip` (sha256 `759c850d…`).

**Held back on purpose:** route D and the per-genre tables use our genre labels, and 17 questions still wait for their
genre relabel (preregistration section 3.1). They are scored after the relabel, into `comparison.md`. Nothing below
uses our genre labels: R, E and F use the genres the LLMs named, and A uses none (deviation log, 2026-10-27).

BHS: lower is better; 50 = chance. Difference = route minus A (below 0 = the route is better). Paired bootstrap over
questions, 10,000 re-samples, seed 2026; two-sided p; Holm over the 2 tests.

## Confirmatory tests

| Test | Condition | Questions | A | R | Difference | 95% range | p | p (Holm) | Result |
|---|---|---|---|---|---|---|---|---|---|
| H1: R vs A | with passage | 175 | 0.57 | 0.86 | +0.29 | −0.07 to +0.71 | 0.185 | 0.369 | no clear difference; not supported |
| H2: R vs A | without passage | 75 | 21.83 | 22.83 | +1.00 | −2.00 to +4.17 | 0.548 | 0.548 | no clear difference; not supported |

**Neither hypothesis is supported.** Routing learned on BenHalluEval did not beat the single best judge (gemma4-31b) on
new questions. In both conditions R was slightly worse in the point estimate, but neither difference is clear.

## Errors behind the scores

| Condition | Route | False alarms (correct answers called hallucinated) | Misses (hallucinations not caught) | BHS |
|---|---|---|---|---|
| with passage (175 correct, 700 hallucinated) | A | 1 | 4 | 0.57 |
| | R | 1 | 8 | 0.86 |
| | E | 1 | 8 | 0.86 |
| | F | 1 | 6 | 0.71 |
| without passage (75 correct, 300 hallucinated) | A | 15 | 71 | 21.83 |
| | R | 14 | 81 | 22.83 |
| | E | 14 | 81 | 22.83 |
| | F | 13 | 82 | 22.33 |

- With the passage, one false alarm costs 0.29 BHS points and one miss 0.07. A made 5 errors in 875 answers, so there
  was almost no room to improve: H1's difference is 4 extra misses.
- R and A gave different verdicts on 6 answers with the passage (R right on 1, A right on 5) and on 35 without it (R
  right on 13, A right on 22). Without the passage, qwen3.5-27b said "yes" less often than gemma4-31b: one false alarm
  fewer, 10 misses more.
- 3 of these differences come from gemma4-31b itself giving a different verdict in the two notebooks (d2-160__p2 with
  the passage, against R; d2-057__p5 and d2-145__p2 without it, both for R). Without them, R would be right on 1 vs 4
  (with passage) and 11 vs 22 (without).
- `no_answer`: 0 for every route in both conditions.

## Exploratory comparisons (no correction)

| Comparison | Answers | Questions | Difference | 95% range |
|---|---|---|---|---|
| E vs A, with passage | 875 | 175 | +0.29 | −0.07 to +0.71 |
| E vs A, without passage | 375 | 75 | +1.00 | −2.00 to +4.17 |
| F vs A, with passage | 875 | 175 | +0.14 | −0.14 to +0.43 |
| F vs A, without passage | 375 | 75 | +0.50 | −2.67 to +3.67 |
| R vs A, all answers (each in its own condition) | 1,250 | 250 | +0.50 | −0.50 to +1.50 |
| E vs A, all answers | 1,250 | 250 | +0.50 | −0.50 to +1.50 |
| F vs A, all answers | 1,250 | 250 | +0.25 | −0.75 to +1.25 |

E and R chose different judges for 25 answers, but those judges gave the same verdict on all 25, so E's verdicts equal
R's on every answer. No route is clearly different from A anywhere.

## Checks and cost

- Determinism: of 3,080 (answer, route) pairs sent to gemma4-31b in both notebooks, 3,068 got the same verdict (99.61%);
  by answer, 917 of 920 (99.7%). The prompts are identical. Likely GPU non-determinism with 2 parallel slots (not
  verified).
- Run checks (dataset checksums, lock, prompts, model digests, routes recomputed independently): see `docs/runlog.md`,
  "GenreHalluEval run 2".

| Notebook | Turn | Calls | Prompt tokens | Output tokens | Wall time |
|---|---|---|---|---|---|
| single best (A) | judge | 1,250 | 259,104 | 2,500 | 41 min |
| routed (R, D, E, F) | genre | 800 | 954,395 | 26,735 | 2 h 07 min (both turns) |
| routed (R, D, E, F) | judge | 1,480 | 369,447 | 4,088 | |

To serve R alone, each question needs 2 genre calls (6 without the passage), and each answer needs 1 judge call; A needs
only the judge call. Routing cost more and gained nothing here.

## Written predictions (`docs/expectations.md`, frozen on OSF)

| # | Prediction | Confidence | Outcome |
|---|---|---|---|
| 0 | R clearly better than A in at least one condition | 25% | did not happen |
| 1 | E not clearly different from A, in either condition | 85% | held |
| 2 | F not clearly different from A, in either condition | 85% | held |
| 4 | Dataset 2 harder than BenHalluEval for A with the passage (BHS above 1.44) | 70% | did not happen (0.57) |
| 5 | Without the passage, A's BHS around 28–40 | 65% | did not happen (21.83, easier) |
| 7 | Geography among the two easiest genres with the passage | 55% | held back (per genre) |
| 8 | The 3 "better in own genre" cases do not replicate | 85% | held back (needs our genres) |
| 11 | At least 95% of answers routed to gemma4-31b or qwen3.5-27b | 85% | held (every route; R 100%) |
| 12 | gemma4-31b gives the same verdict in both notebooks at least 99% of the time | 90% | held (99.7% of answers) |
