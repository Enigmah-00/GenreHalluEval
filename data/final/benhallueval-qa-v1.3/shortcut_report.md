# Shortcut report (main set: include_main = yes)

920 questions, 4600 items. BHS = ½ × (Track A error + Track B error) × 100; lower is better; 50 = chance. These rules never read the question, so a real judge must beat them to show it uses the passage and question rather than surface form.

## Answer length and form by type

| Type | Mean chars | Median chars | Exact span of passage | Contains a comma |
|---|---|---|---|---|
| gold | 15.2 | 12.0 | 100.0% | 4.8% |
| F | 13.2 | 12.0 | 4.9% | 4.0% |
| C | 12.1 | 11.0 | 83.0% | 3.2% |
| S | 37.2 | 35.0 | 0.0% | 94.2% |
| I | 12.9 | 11.0 | 22.6% | 3.4% |

## Rule baselines

| Rule ('hallucinated' when …) | BHS | Track A error | Track B error |
|---|---|---|---|
| not an exact span of the passage | 13.82 | 0.0% | 27.64% |
| not a span after normalising spaces and punctuation | 13.86 | 0.0% | 27.72% |
| contains a comma | 39.29 | 4.78% | 73.8% |
| longer than 24 characters (2 x the median gold length) | 43.19 | 12.61% | 73.78% |
| longest of the 5 answers (uses all 5, so not a real single-answer judge) | 37.46 | 0.11% | 74.81% |
| always yes | 50.0 | 100.0% | 0.0% |

## Span subset (robustness check)

1937 items in 920 questions have an answer that is an exact span of the passage (by type: {'C': 764, 'gold': 920, 'I': 208, 'F': 45}). On these items the span rule is useless, so judge scores here show whether a judge really checks that the span answers the question.

Golds are TyDiQA-GoldP spans, so every gold is a span. The original BenHalluEval QA design has the same property (gold spans, generated hallucinations), so this shortcut is a property of the task design, not only of these answers. Report the span baseline next to every judge score.
