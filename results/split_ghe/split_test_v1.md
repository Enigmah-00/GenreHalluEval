# GenreHalluEval split experiment: test-half result (exploratory), 2026-10-28

Plan: `docs/split-experiment-plan.md`. Lock: `results/lock/lock_split_v1.json` (sha256 `2616eb9a…`), learned on the learn
half only (125 questions, each answer judged with and without the passage). Test half: 125 other questions, 63 judged
with the passage (315 answers) and 62 without it (310 answers). Labels: the agreed passage labels (0 excluded).

Scored by `src/dataset2/compare_routes.py --dataset ghesplit_test --package data/final/GenreHalluEval-split-v1 --items
test_items.csv` on `runs/ghesplit/ghesplit_test__{routed,single_best}__full__all__outputs__mac_rezipped.zip`.
Per-genre tables are held back, as for Dataset 2, until the 17-question genre relabel is in.

BHS: lower is better. Difference = route minus A (below 0 = the route is better). Paired bootstrap over test questions,
10,000 re-samples, seed 2026; two-sided p; Holm over the 2 R vs A tests.

## Main tests (exploratory, like the whole experiment)

| Test | Condition | Test questions | A | R | Difference | 95% range | p | p (Holm) | Result |
|---|---|---|---|---|---|---|---|---|---|
| R vs A | with passage | 63 | 0.79 (qwen3.5-27b) | 0.40 | −0.40 | −0.99 to +0.00 | 0.252 | 0.252 | no clear difference |
| R vs A | without passage | 62 | 19.76 (gemma4-31b) | 24.19 | **+4.44** | **+1.21 to +8.27** | 0.007 | **0.014** | **routing clearly worse** |

**Routing did not help, and without the passage it was clearly worse than the single best judge.** This holds even
though the routes were learned and tested on the same dataset (no change of dataset).

## Errors behind the scores

| Condition | Route | False alarms | Misses | BHS |
|---|---|---|---|---|
| with passage (63 correct, 252 hallucinated) | A (qwen3.5-27b) | 0 | 4 | 0.79 |
| | R, D, E, F (same verdicts) | 0 | 2 | 0.40 |
| without passage (62 correct, 248 hallucinated) | A (gemma4-31b) | 8 | 66 | 19.76 |
| | R | 11 | 76 | 24.19 |
| | D | 11 | 76 | 24.19 |
| | E | 10 | 76 | 23.39 |
| | F | 14 | 71 | 25.60 |

- **With the passage:** R sent the Arts and Science questions to gemma4-31b. gemma4 caught 2 of A's 4 misses, so the
  gain is 2 answers. Errors are too rare for this to mean much.
- **Without the passage:** where R took answers away from gemma4-31b, the new judge did worse. Errors of A vs errors of
  R's judge, on the same answers:

  | Answers | Count | A's errors | R's errors |
  |---|---|---|---|
  | qwen3.5-27b, on questions it named History | 60 | 18 | 21 |
  | qwen3.5-27b, on questions it named Religion | 55 | 5 | 13 |
  | deepseek-r1-14b, through its own Arts cell | 15 | 6 | 7 |

  On the learn half, qwen3.5-27b had beaten gemma4-31b in History (39.5) and Religion (13.0) on 25 questions each. On
  the test half, it lost in both. The same thing happened on BenHalluEval → Dataset 2.

## Other comparisons

| Comparison | Answers | Questions | Difference | 95% range |
|---|---|---|---|---|
| D vs A, with passage | 315 | 63 | −0.40 | −0.99 to +0.00 |
| D vs A, without passage | 310 | 62 | +4.44 | +1.21 to +8.06 |
| E vs A, with passage | 315 | 63 | −0.40 | −0.99 to +0.00 |
| E vs A, without passage | 310 | 62 | +3.63 | +0.81 to +6.85 |
| F vs A, with passage | 315 | 63 | −0.40 | −0.99 to +0.00 |
| F vs A, without passage | 310 | 62 | +5.85 | +1.41 to +10.89 |
| R vs A, all 625 answers (each in its own condition) | 625 | 125 | +2.00 | +0.30 to +4.00 |
| E vs A, all answers | 625 | 125 | +1.60 | +0.20 to +3.30 |
| F vs A, all answers | 625 | 125 | +2.70 | +0.40 to +5.40 |

## Checks and cost

- Both runs started after the lock existed; dataset checksums, lock sha256, model digests, prompt ids and every prompt
  hash (rebuilt here, English and Bangla) match. Every route equals an independent recomputation from the lock.
  `no_answer` 0 in every judge call used; nothing truncated.
- The two zips were re-packed on a Mac before they were sent (a top folder and `__MACOSX` files were added); the run
  files inside passed every check above.
- Determinism: the same judge on the same answer gave the same verdict in both notebooks on 424 of 425 answers
  (d2-156__p5, gemma4-31b, differs).

| Notebook | Calls | Prompt tokens | Output tokens | Wall time |
|---|---|---|---|---|
| learn half (all 5 judges, both conditions) | 6,875 | 2,614,676 | 488,088 | 4 h 19 min |
| test half, routed (436 genre + 740 judge) | 1,176 | 657,077 | 33,944 | 1 h 20 min |
| test half, single best | 625 | 156,506 | 1,250 | 27 min |
