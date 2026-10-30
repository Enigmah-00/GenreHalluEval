# GenreHalluEval v1.0

A Bangla question-answering hallucination test set with genre labels (Dataset 2 of the study "Genre-aware
hallucination judges for Bangla"). Test-only: nothing here is used to make or change a routing choice.

## Files

| File | What it is |
|---|---|
| `items.csv` | **Set B, the test set** (1,250 answers). Column `condition` says how each answer is judged: `context` = passage + question + answer (875 answers, 175 questions); `no_context` = question + answer only (375 answers, 75 questions). The passage stays in every row only because the genre guess uses question + passage. |
| `setA_all_with_passage.csv` | **Set A, for publishing**: the same 1,250 answers, all with the passage. Same `item_id`s. |
| `questions.csv` | The 250 questions: passage, source, gold answer, the three genre labels and the majority genre. |
| `prompts/` | The exact judge and genre prompts used on BenHalluEval-QA v1.3. |
| `lock_v2.json` | The routing choices locked on BenHalluEval before any answer here existed (sha256 `6d3c1d29cb81…`). |
| `checksums.sha256` | sha256 of every file; the notebooks check them. |

## How it was made

- **Questions, passages and gold answers:** written by the team (mostly Umme Zoayria Abedin), 50 per genre
  (History, Politics & Education; Arts, Culture & Sports; Geography & Places; Science & Technology; Religion). Every
  question can be answered without its passage (checked by Mahdi Hasan Qurishi while annotating).
  Sources: Bangla Wikipedia (most), a few news sites, Banglapedia.
- **Overlap with BenHalluEval removed:** 17 rows were replaced (12 new Wikipedia passages, 5 new questions); see
  `questions.csv` column `change`.
- **Genre:** three annotators per question, frozen guide v1.0 (Fleiss' kappa 0.987 on the original sheet); the 17
  changed questions (`genre_status = relabel_pending`) are labelled again.
- **Hallucinated answers:** 4 per question, written by Claude (claude-opus-5-5) with the guide used for
  BenHalluEval-QA v1.3: F factualness, C comprehension, S specificity, I inference. All are meant to be wrong both by
  the passage and in the real world.
- **Labels:** `design_label` (0 = correct gold, 1 = written hallucination) is the label by construction. The final
  labels are the two annotators' agreed labels (passage label for every answer; world label for the 375 answers
  judged without the passage), added in v1.1.

## Licence and limits

Passages from Wikipedia are CC BY-SA 4.0; a few passages are short excerpts from news sites and Banglapedia, so check
their terms before any public release. Keep the Kaggle dataset private until then. Both this set and BenHalluEval-QA
v1.3 use Claude-written hallucinations, so this set tests new questions, passages and topics, not new answer writers.
