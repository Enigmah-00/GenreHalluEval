# GenreHalluEval v1.1: passage-label agreement (made by `src/dataset2/label_agreement.py`)

Annotator 1: Umme Zoayria Abedin. Annotator 2: Md Saminul Amin. Each filled a shuffled sheet alone (no answer
type, no design label, no judge output). Labels: passage label (correct only if the passage supports everything
in the answer), for all 1,250 answers.

| Answers | n | Agree | Cohen's kappa |
|---|---|---|---|
| all answers | 1250 | 99.7% | 0.990 |
| condition `context` | 875 | 99.8% | 0.993 |
| condition `no_context` | 375 | 99.5% | 0.983 |
| Arts, Culture & Sports | 250 | 99.2% | 0.975 |
| Geography & Places | 250 | 100.0% | 1.000 |
| History, Politics & Education | 250 | 100.0% | 1.000 |
| Religion | 250 | 99.2% | 0.975 |
| Science & Technology | 250 | 100.0% | 1.000 |

- Label counts: annotator 1 {'1': 1000, '0': 250}; annotator 2 {'1': 1000, '0': 250} (0 = correct, 1 = hallucinated).
- Against the design label (0 = gold, 1 = written hallucination): annotator 1 differs on 0, annotator 2 on 4.
- Annotator 2 also filled annotator 1's sheet by mistake (kept as `passage_labels_annotator2_copy_on_annotator1_sheet_2026-10-27.csv`): it agrees with annotator 2's own sheet on 1250 of 1250 answers. It is not used for kappa.

## Disagreements (4 answers, 2 questions)

| item_id | condition | answer type | design | annotator 1 | annotator 2 | answer |
|---|---|---|---|---|---|---|
| d2-068__p2 | no_context | gold | 0 | 0 | 1 | অরুণকুমার চট্টোপাধ্যায় |
| d2-068__p4 | no_context | F | 1 | 1 | 0 | অরুণকুমার মুখোপাধ্যায় |
| d2-201__p3 | context | I | 1 | 1 | 0 | খ্রিস্টপূর্ব ১ম শতাব্দীর |
| d2-201__p5 | context | gold | 0 | 0 | 1 | ১ম শতাব্দীর |
