# Shortcut report (main set: include_main = yes)

990 questions, 4950 items. BHS = ½ × (Track A error + Track B error) × 100; lower is better; 50 = chance. These rules never read the question, so a real judge must beat them to show it uses the passage and question rather than surface form.

## Answer length and form by type

| Type | Mean chars | Median chars | Exact span of passage | Contains a comma |
|---|---|---|---|---|
| gold | 15.1 | 12.0 | 100.0% | 4.6% |
| F | 13.1 | 12.0 | 4.4% | 3.8% |
| C | 11.9 | 11.0 | 82.9% | 3.2% |
| S | 37.1 | 35.0 | 0.0% | 94.1% |
| I | 12.9 | 11.0 | 22.2% | 3.3% |

## Rule baselines

| Rule ('hallucinated' when …) | BHS | Track A error | Track B error |
|---|---|---|---|
| not an exact span of the passage | 13.7 | 0.0% | 27.4% |
| not a span after normalising spaces and punctuation | 13.76 | 0.0% | 27.53% |
| contains a comma | 39.26 | 4.65% | 73.86% |
| longer than 24 characters (2 x the median gold length) | 43.12 | 12.53% | 73.71% |
| longest of the 5 answers (uses all 5, so not a real single-answer judge) | 37.47 | 0.1% | 74.85% |
| always yes | 50.0 | 100.0% | 0.0% |

## Span subset (robustness check)

2075 items in 990 questions have an answer that is an exact span of the passage (by type: {'C': 821, 'gold': 990, 'I': 220, 'F': 44}). On these items the span rule is useless, so judge scores here show whether a judge really checks that the span answers the question.

Golds are TyDiQA-GoldP spans, so every gold is a span. The original BenHalluEval QA design has the same property (gold spans, generated hallucinations), so this shortcut is a property of the task design, not only of these answers. Report the span baseline next to every judge score.
