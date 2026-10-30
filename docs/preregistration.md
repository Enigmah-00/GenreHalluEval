# Preregistration: Dataset 2 (GenreHalluEval) test (ready to freeze)

Status: **final, 2026-10-27** (first draft 2026-10-18). Freeze it by uploading this file, `results/lock/lock_v2.json`
and `data/final/GenreHalluEval-v1.1/checksums.sha256` (with the sha256 of the two label sheets) to OSF (osf.io, free;
an embargo is fine) **before either notebook runs**. After that, nothing here changes; any deviation goes in the
deviation log at the end.

**Frozen (added after freezing):** OSF registration https://osf.io/fmbs8 (submitted 2026-10-27, private while
embargoed). The frozen copy is `release/osf_freeze/preregistration.md` (sha256 `9e747de4…`); this file differs from it
only by this line and the deviation log.

## 1. What we have already seen (honest disclosure)

- All BenHalluEval-QA v1.3 results for 12 open judges (genre guessing and judging, with and without the passage)
  were seen before this preregistration. Every choice for Dataset 2 was computed from them and frozen in
  `results/lock/lock_v1.json` (sha256 `779cc5a7cdc2…`) and `results/lock/lock_v2.json` (sha256
  `6d3c1d29cb8159d5f74300c799ce040c9a7c737dfb68b5c292a2a2aa948c9137`). Lock v2 keeps every v1 choice and adds the
  best-path route R (section 2).
- BenHalluEval is the training set, not a test: the routing tables were built on it, so a route scored there is
  scored on the data that chose it. For the record: on BenHalluEval, R scored 0.10 (with the passage) and 0.33
  (without it) BHS points better than A; an exploratory 5-fold check inside BenHalluEval gave 0.00 and +0.45. Whether
  genre-aware routing beats the single best judge can only be tested on questions no choice has seen: Dataset 2.
- **What exists of Dataset 2 at freezing:** GenreHalluEval v1.1 (`data/final/GenreHalluEval-v1.1/`): 250 questions
  with passage, source, gold answer and three genre labels (collected by the team; gold answers written by Mahdi Hasan Qurishi, genre annotator 3), and 4
  hallucinated answers per question written by Claude. The answers were written before freezing (Mahdi's decision,
  2026-10-27). Both annotators' passage labels for all 1,250 answers were also made before freezing (2026-10-27;
  Cohen's kappa 0.990, 4 disagreements in 2 questions, to be resolved by discussion; section 3.3). **No judge or
  genre-guessing LLM has seen any Dataset 2 item.** Dataset 2 is never used to make or change any choice.
- The two notebooks and the scoring script were written and tested (with a fake model) before freezing:
  `src/dataset2/make_notebooks.py`, `src/dataset2/compare_routes.py`, `src/dataset2/test_notebooks.sh`.

## 2. Research question and confirmatory hypotheses

**Hypothesis: genre-aware routing of LLM hallucination judges, learned on BenHalluEval, is better than the single best
judge on new, held-out Bangla questions.** No judge is best in every genre, so sending each answer to the judge that
fits its genre should make fewer errors than sending every answer to one judge.

- **H1 (with the passage, `context`):** R has a lower BHS than A on Dataset 2.
- **H2 (without the passage, `no_context`):** R has a lower BHS than A on Dataset 2.

A hypothesis is supported when R minus A is below 0 and its Holm-corrected p-value is below 0.05 (section 4). The test
is two-sided, as locked, so a route that is clearly worse is also detected and reported.

Two notebook runs judge the same answers:

- **Single best (A):** gemma4-31b judges every answer (A in both conditions).
- **Routed (R, best path):** for each answer, two kinds of path compete and the one with the lower BenHalluEval BHS
  wins:
  - *our-genre path:* the best genre guesser (qwen3.5-27b) names the genre; the judge × genre table built on our
    genres gives the judge, scored by that cell's BHS (no usable cell: A, scored by A's overall BHS);
  - *own-genre paths:* an LLM names the genre; that LLM, scored by its BHS inside the genre it named (cells under 50
    questions not used).
  Ties go to the better overall judge. Only the LLMs whose genre answer can change R are asked ("askers" in lock v2):
  gemma4-31b and qwen3.5-27b with the passage; also deepseek-r1-14b, gemma2-27b, gpt-oss-20b and qwen2.5-32b
  without it. This gives exactly the same routes as asking all 9 pool judges (checked on BenHalluEval).

**Confirmatory comparisons: R vs A with the passage (H1) and R vs A without it (H2).**
Lock v1 listed six comparisons (E vs A, F vs A, F vs C); before any data was judged we replaced them with these two,
because R combines E and F, and C (a vote of all judges) needs every judge on every answer, which this design does not
run. E, F and D are reported as exploratory.

## 3. Dataset 2 (GenreHalluEval v1.1)

### 3.1 Questions

- **Size:** 250 questions, **50 per main genre** (History, Politics & Education; Arts, Culture & Sports; Geography &
  Places; Science & Technology; Religion). None is in Other. Every question can be answered without its passage
  (checked by Mahdi Hasan Qurishi while annotating).
- **Source:** written by the team from copied passages: Bangla Wikipedia (237), news sites (ProthomAlo 4, BBC News
  Bangla 4, Jugantor 1, The Daily Star Bangla 1, The Daily Ittefaq 1), Banglapedia 1, unknown 1 (`d2-151`).
- **Genre:** three annotators per question with the frozen guide v1.0 (Fleiss' kappa 0.987; all three agree on 246
  of 250). The majority vote is the genre. The 17 changed questions are labelled again by the same three annotators
  before scoring.
- **No overlap with BenHalluEval** (all three files we have), checked by `src/dataset2/check_overlap.py` (shared text,
  shared rare words = same Wikipedia article, same fact) and a manual read of every flag: 17 rows were replaced
  (`data/labels/dataset2/overlap_replacements_v1.csv`; 12 new Wikipedia passages, 5 new questions).
- **Text fixes (v1.1):** 16 passages that did not state the gold answer clearly (15 of them Islamic Religion passages)
  now state it in one short phrase; one question's year and one hallucinated answer were corrected
  (`data/labels/dataset2/text_fixes_v1.1.csv`). No fix makes a hallucinated answer supported.

### 3.2 Answers

- Per question: the team's gold answer + **4 hallucinated answers** written by Claude (claude-opus-5-5) with the frozen
  guide of BenHalluEval-QA v1.3 (`prompts/hallucination_writing_guide_v1.md`): F factualness, C comprehension,
  S specificity, I inference; each meant to be wrong both by the passage and in the real world. The writer saw
  passage + question + gold. 1,250 answers.
- **Set B, the test set (`items.csv`):** each question's 5 answers are judged in its `mix_condition`: with the passage
  for **70% of the questions** (35 per genre; 875 answers) and without it for **30%** (15 per genre; 375 answers),
  fixed before any answer existed (seed `2026:<genre>`).
- **Set A (`setA_all_with_passage.csv`):** the same 1,250 answers, all with the passage, for publishing. It is not
  used in any test.
- **Limitation, stated in the paper:** both datasets use the same answer writer and guide, so Dataset 2 tests transfer
  to new questions, passages, topics and recent events, not to answers written by other models.
- Claude is never a judge or a genre guesser.

### 3.3 Labels (both annotators label every answer, alone)

- **Annotator 1: Umme Zoayria Abedin; annotator 2: Md Saminul Amin.** Each worked alone, blind to the other, the
  answer type, the design label and every judge output, on shuffled sheets (`data/labels/dataset2/blank_sheets/`).
- **Passage label** for all 1,250 answers (used for every answer, also those judged without the passage, and for
  Set A): correct only if the passage supports everything in the answer.
- **No separate world label** (decided 2026-10-27): every question can be answered without its passage, and every
  passage states its gold answer. Limitation, stated in the paper: where a passage is out of date or wrong about the
  world, the label of an answer judged without the passage could be wrong.
- Disagreements are resolved by discussion; the agreed label is final, also when it differs from the design label (the
  count is reported). Cohen's kappa is reported before discussion; below 0.6 means the guide is fixed and the
  labelling repeated. Raw sheets are kept unchanged. Answers both mark as unclear after discussion are removed
  (count reported).
- **Done (2026-10-27):** 1,250 labels per annotator; kappa and disagreements in
  `data/labels/dataset2/passage_label_agreement.md`.

## 4. Analysis (fixed now)

- **Runs:** the two notebooks, with the same prompts, models, versions and settings as on BenHalluEval (Ollama 0.40.6,
  temperature 0, seed 2026, strict parsing). The notebooks stop if a prompt or the lock differs.
- **Scoring:** `src/dataset2/compare_routes.py` on Set B with the agreed labels: answers judged with the passage form
  the `context` test (875 answers, 175 questions); answers judged without it form the `no_context` test (375 answers,
  75 questions). Both use the agreed passage label.
- **Metric:** BHS = ½ × (Track A error + Track B error) × 100; `no_answer` counts as an error.
- **Tests:** paired bootstrap over questions (10,000 re-samples, seed 2026); two-sided bootstrap p-values (2 × the
  smaller share of differences ≤ 0 or ≥ 0); **Holm correction across the 2 comparisons at α = 0.05**; 95% ranges for
  every comparison.
- **Expected precision (estimate):** with the passage (175 questions) about ±2 BHS points; without it (75 questions)
  about ±4–5 points, so only large differences can be seen there.
- **Cost (estimate from gemma4-31b's BenHalluEval speed):** single best 1,250 judge calls, about 1 GPU hour; routed
  250 + 250 + 4 × 75 genre calls and about 1,300–1,800 judge calls, about 3 GPU hours. Measured calls, tokens and
  time are reported.
- **Reported whatever the outcome:** both results, the BHS of every route, which judges each route used, `no_answer`
  counts and cost. A clear "no" is a result.

## 5. Exploratory (not confirmatory)

D, E and F vs A per condition (F over the askers only); every route vs A on all 1,250 answers together (each in its own
condition); per-genre results; how well the asked LLMs guess our genres on Dataset 2; the determinism check (answers
routed to gemma4-31b should get the same verdict in both notebooks); the passage-span rule (shortcut baseline);
whether Geography stays the easiest genre with the passage.

## 6. Deviation log (fill after freezing, never delete)

| Date | What changed | Why |
|---|---|---|
| 2026-10-27 | The confirmatory tests (R vs A, both conditions) and the E and F comparisons were scored before the 17 replaced questions got their genre relabel (section 3.1 says relabel before scoring). Route D and the per-genre results are held until the relabel is in. Decided by Mahdi after both runs finished, before any score was computed. | R uses only the genres the LLMs named and A uses none, so the relabel cannot change H1 or H2. D and the per-genre tables do use our genres, so they wait. |
| 2026-10-27 | Two exploratory analyses added after the confirmatory result: (1) the same routing experiment inside BenHalluEval, by splitting it into halves (from saved runs; `results/split_experiment/`); (2) a split of GenreHalluEval into a learn half and a test half, with new runs of 5 judges (TigerLLM with Bangla prompts) and cells of 20+ questions (`docs/split-experiment-plan.md`). Decided by Mahdi. | To see whether the result depends on the change of dataset. Both are exploratory: they cannot change or replace H1 and H2, and the GenreHalluEval split uses Dataset 2 to make choices only inside that experiment. |
| 2026-10-28 to 2026-10-30 | A new, separate study, GenreHalluEval v2, was built and run after the confirmatory result: 12 single genres x 100 questions (230 kept v1.1 questions + 970 written by Claude, 20% blind-checked by two annotators), routes learned on a learn half and tested on a test half inside v2, cells of 50+ questions, one route per notebook (E, F, R vs A, Holm over 6). Its design is fixed in the package files with dates (`pool.json` before the learn run, `test_plan_v2.json` before the test runs); it has no OSF registration of its own (Mahdi, 2026-10-30). Decided by Mahdi. | To test whether the H1/H2 result came from the merged, coarse genres. v2 is exploratory with respect to this registration: it cannot change or replace H1 and H2, and both are always reported together. |

Changes made before freezing (for the record), all on 2026-10-27 and decided by Mahdi: source changed from BanglaRQA
to team-written questions; answers changed from real LLM answers to Claude-written hallucinations (4 per question);
each answer is judged in one condition (Set B), with Set A kept for publishing; the analysis changed to two notebooks
(routed and single best) and one best-path route R (lock v2), so the confirmatory tests went from 6 to 2; the
hallucinated answers were written before this document was frozen (no judge had seen them). Also before freezing,
on 2026-10-27: the passage labels were made, the separate world label was dropped, and 18 text fixes made v1.1
(v1.0 is kept in `data/final/superseded/`).
