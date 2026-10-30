# GenreHalluEval

Data, prompts, raw model outputs and analysis code for the paper *Routing Bangla Hallucination Judges by Genre
Does Not Beat the Best Single Judge* (Mahdi Hasan Qurishi, Umme Zoayria Abedin, Md Saminul Amin; Shahjalal
University of Science and Technology).

LLM judges read a Bangla question and an answer, with or without a supporting passage, and say whether the answer is
hallucinated. We test whether sending each answer to the judge that is best for its genre beats the single best
judge. In five tests (one preregistered at https://osf.io/fmbs8, four exploratory), it does not.

## What is here

| Folder | Contents |
|---|---|
| `data/final/benhallueval-qa-v1.3/` | Audited BenHalluEval-QA set: 920 questions, 4,600 answers (gold + 4 hallucinations each), human-verified genre labels. Learning set of the preregistered test. |
| `data/final/GenreHalluEval-v1.1/` | 250 team-written questions, 1,250 answers, 5 genres x 50. Test set of the preregistered test. |
| `data/final/GenreHalluEval-split-v1/` | Learn/test split of v1.1 (Study 2b). |
| `data/final/GenreHalluEval-v2.0/` | 1,200 questions, 6,000 answers, 12 genres x 100, with its learn/test split, lock and test plan (Study 3). |
| `data/labels/` | Every annotator's raw sheet, agreed labels, agreement reports and the blind 20% check of v2.0. |
| `prompts/` | Judge prompts (with and without the passage), genre prompts (English and Bangla) and the hallucination writing guide. |
| `runs/` | Every raw model output (one JSONL line per call: prompt hash, raw reply, parsed verdict, tokens, latency) and the Kaggle output zips with manifests and server logs. |
| `notebooks/` | The Kaggle notebooks that produced the runs. |
| `src/` | Dataset builders, route locks, scoring and agreement code (Python 3, standard library only). |
| `results/` | All result tables (`results/genrehallueval/`, `results/split_experiment/`, `results/split_ghe/`, `results/ghe2/`). |
| `docs/` | Genre guides, preregistration with deviation log, run log, audit notes and study plans. |
| `paper/` | LaTeX source of the paper. |

Each dataset folder has its own `README.md` and `checksums.sha256`.

## Main result

| Study | Route vs single best judge | Outcome |
|---|---|---|
| 1, preregistered (learn on BenHalluEval, test on GenreHalluEval v1.1) | R vs A | no difference (Holm p 0.37 and 0.55) |
| 2a, split inside BenHalluEval | R, E, F vs A | no gain; F worse with the passage |
| 2b, split inside GenreHalluEval v1.1 | R, E, F vs A | no gain; all clearly worse without the passage |
| 3, GenreHalluEval v2.0 (12 balanced genres) | E, F, R vs A | E and R no difference; F clearly worse (Holm p < 0.001, 0.006) |

Scores are BenHalluScore (lower is better; 50 = chance). See `results/ghe2/test_v1.md` and the paper.

## Reproduce the scores

```bash
python3 -I src/dataset2/compare_routes.py . --routed runs/genrehallueval/genrehallueval__routed__full__outputs.zip \
  --single runs/genrehallueval/genrehallueval__single_best__full__outputs.zip \
  --labels data/labels/dataset2/passage_labels_agreed_v1.csv
python3 -I src/genrehallueval_v2/compare_v2.py . --A runs/ghe2/ghe2_test__single_best__full__all__outputs.zip \
  --E runs/ghe2/ghe2_test__route_E__full__all__outputs.zip --F runs/ghe2/ghe2_test__route_F__full__all__outputs.zip \
  --R runs/ghe2/ghe2_test__route_R__full__all__outputs.zip --labels data/labels/genrehallueval_v2/labels_v2.0.csv
```

## How the data were made

Hallucinated answers, the 970 new v2.0 questions, genre drafts and the grammar-book passage transcriptions were
written with an AI assistant (Claude, Anthropic) and then checked by people as described in the paper: genre labels
were human-verified, GenreHalluEval v1.1 answers were labelled by two annotators (Cohen's kappa 0.990), and a blind
20% sample of v2.0 was double-checked (kappa 0.990 for answers, 0.991 for genres). The remaining 80% of v2.0 is not
human-checked.

## Licences

See `LICENSE.md`. In short: BenHalluEval-derived data CC BY-NC-SA 4.0; Wikipedia passages CC BY-SA; grammar-book
and news passages for research purposes under Bangladesh's Copyright Act 2023; code MIT.

## Citation

Please cite the paper (details to be added on publication) and BenHalluEval (arXiv:2605.31483).
