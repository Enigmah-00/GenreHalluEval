# GenreHalluEval v2 blind check: agreement report (v1)

Made by `src/genrehallueval_v2/check_agreement.py` from the raw returned sheets in `data/labels/genrehallueval_v2/check_v1/returned_raw_2026-10-29_v2/`. Kappa = Cohen's kappa; the 95% range comes from a bootstrap that re-samples questions (2,000 draws, seed 2026). Design label: the gold answer is correct, the four written answers (F/C/S/I) are hallucinated.

## Problems in the returned sheets

- Md Saminul Amin (annotator 2), answers A0573: text edited (answer: 'আল্লাহ রাখা খান' -> 'আল্লাহ রাখা রহমান'); label 'correct' left out

## Answer labels (194 Claude-written questions x 5 answers)

- Umme Zoayria Abedin (annotator 1): 970 of 970 answers labelled correct/hallucinated, 0 unsure.
- Md Saminul Amin (annotator 2): 969 of 970 answers labelled correct/hallucinated, 0 unsure.

| Pair | Answers | Agreement | Kappa | 95% range |
|---|---|---|---|---|
| annotator 1 vs annotator 2 | 969 | 99.7% | 0.990 | 0.974 to 1.000 |
| annotator 1 vs design | 970 | 100.0% | 1.000 | 1.000 to 1.000 |
| annotator 2 vs design | 969 | 99.7% | 0.990 | 0.974 to 1.000 |
| annotator 2 vs design, same answers as annotator 1 | 969 | 99.7% | 0.990 | 0.974 to 1.000 |

Share of answers given the design label, per answer type:

| Answer type | Annotator 1 | Annotator 2 |
|---|---|---|
| gold | 194/194 (100.0%) | 192/194 (99.0%) |
| F | 194/194 (100.0%) | 194/194 (100.0%) |
| C | 194/194 (100.0%) | 193/194 (99.5%) |
| S | 194/194 (100.0%) | 194/194 (100.0%) |
| I | 194/194 (100.0%) | 193/193 (100.0%) |

Per genre (agreement with the design label; kappa between the annotators):

| Genre | Questions | Annotator 1 vs design | Annotator 2 vs design | Annotator 1 vs 2 (kappa) |
|---|---|---|---|---|
| ARTS | 13 | 65/65 | 63/64 | 0.950 (64 answers) |
| CULTURE | 20 | 100/100 | 98/100 | 0.937 (100 answers) |
| EDUCATION | 19 | 95/95 | 95/95 | 1.000 (95 answers) |
| GEOGRAPHY | 13 | 65/65 | 65/65 | 1.000 (65 answers) |
| GRAMMAR | 20 | 100/100 | 100/100 | 1.000 (100 answers) |
| HISTORY | 18 | 90/90 | 90/90 | 1.000 (90 answers) |
| PLACES | 18 | 90/90 | 90/90 | 1.000 (90 answers) |
| POLITICS | 14 | 70/70 | 70/70 | 1.000 (70 answers) |
| RELIGION | 11 | 55/55 | 55/55 | 1.000 (55 answers) |
| SCIENCE | 15 | 75/75 | 75/75 | 1.000 (75 answers) |
| SPORTS | 18 | 90/90 | 90/90 | 1.000 (90 answers) |
| TECHNOLOGY | 15 | 75/75 | 75/75 | 1.000 (75 answers) |

- Umme Zoayria Abedin (annotator 1): number of answers marked correct per fully labelled question: {1: 194} (194 questions).
- Md Saminul Amin (annotator 2): number of answers marked correct per fully labelled question: {1: 193} (193 questions).

Every question has exactly one correct answer by design. An annotator who marks exactly one per question may have guessed the design, so agreement with the design is an upper bound (as for Mahdi's BenHalluEval check).

## Genre labels (240 questions)

| Questions | Pair | Questions | Agreement | Kappa | 95% range |
|---|---|---|---|---|---|
| Claude-written | annotator 1 vs 2 | 194 | 99.0% | 0.989 | 0.972 to 1.000 |
| Claude-written | annotator 1 vs draft | 194 | 97.4% | 0.972 | 0.943 to 0.994 |
| Claude-written | annotator 2 vs draft | 194 | 98.5% | 0.983 | 0.960 to 1.000 |
| kept v1.1 | annotator 1 vs 2 | 46 | 100.0% | 1.000 | 1.000 to 1.000 |
| kept v1.1 | annotator 1 vs draft | 46 | 97.8% | 0.975 | 0.922 to 1.000 |
| kept v1.1 | annotator 2 vs draft | 46 | 97.8% | 0.975 | 0.922 to 1.000 |
| all | annotator 1 vs 2 | 240 | 99.2% | 0.991 | 0.977 to 1.000 |
| all | annotator 1 vs draft | 240 | 97.5% | 0.973 | 0.950 to 0.991 |
| all | annotator 2 vs draft | 240 | 98.3% | 0.982 | 0.963 to 0.995 |

- Umme Zoayria Abedin (annotator 1): confidence low 8, question_ok no 0, notes 0.
- Md Saminul Amin (annotator 2): confidence low 5, question_ok no 0, notes 0.

Genre disagreements (draft genre, annotator 1, annotator 2: count):

- TECHNOLOGY / SCIENCE / SCIENCE: 2
- GEOGRAPHY / HISTORY / HISTORY: 1
- SPORTS / CULTURE / SPORTS: 1
- HISTORY / PLACES / PLACES: 1
- HISTORY / POLITICS / HISTORY: 1

