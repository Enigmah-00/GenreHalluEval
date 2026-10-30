# Plan: GenreHalluEval v2 (12 single genres), 2026-10-28 (updated 2026-10-29)

Decided by Mahdi Hasan Qurishi on 2026-10-28, after the v1.1 result and the split experiments:
- 11 single genres;
- 100 questions per genre;
- routes learned and tested inside v2 (split);
- two blind annotators for every new answer.

Claude wrote this plan.

## Status and honesty rules

- v2 is a **new study**, made after the v1.1 results were known. The v1.1 result (registered on OSF, osf.io/fmbs8)
  stays the main result and is always reported. v2 can add to it; it can never replace it.
- **No OSF registration for v2 (Mahdi, 2026-10-30).** The design is fixed in the package files instead: `pool.json`
  (before the learn run) and `test_plan_v2.json` (before the test runs), each with its date and checksum.
- The paper must say exactly what was done:
  - Claude wrote the new questions, golds and hallucinated answers from current sources.
  - Named people checked them.
  - Two annotators labelled every answer alone, and kappa is reported.
- **Never write "verified" for a step that was not done.**

## Size

| Genre | Kept from v1.1 (draft) | New questions needed |
|---|---|---|
| History | 13 | 87 |
| Politics | 28 | 72 |
| Education | 4 | 96 |
| Arts | 33 | 67 |
| Culture | 0 | 100 |
| Sports | 13 | 87 |
| Science | 23 | 77 |
| Technology | 26 | 74 |
| Geography | 33 | 67 |
| Places | 11 | 89 |
| Religion | 46 | 54 |
| **Total** | **230** | **870** |

That makes 1,100 questions and 5,500 answers (gold + F, C, S and I hallucinations). The "kept" numbers are Claude's
draft single-genre labels (`data/labels/genrehallueval_v2/v1_questions_single_genre_draft_claude_2026-10-28.csv`).
20 v1.1 questions are left out, because two genres fit them about equally or they are Other.

## Steps

| # | Step | Who | Output |
|---|---|---|---|
| 1 | Review and **freeze** genre guide v2.0 (`docs/genre-guide-v2.md`) and the genre prompts (`prompts/genre_v2.txt`, `prompts/genre_bn_v2.txt`) | Mahdi | frozen guide |
| 2 | Check Claude's single-genre drafts for the 230 kept v1.1 questions | genre annotators | checked sheet |
| 3 | Re-check every kept v1.1 question against today's source: the current Wikipedia revision (title, revision id, date) or the live news page. Update a passage or gold only where the source changed | Claude, then the checker | source table |
| 4 | Collect 870 new passages from current sources: Bangla Wikipedia through its API (latest revision; raw downloads kept in `data/raw/genrehallueval_v2/`), and news sites with URL and date. Write one question and gold per passage, in one clear genre | Claude | batches of about 50 |
| 5 | Write 4 hallucinations per new question (F, C, S, I) under `prompts/hallucination_writing_guide_v1.md` | Claude | batches |
| 6 | Overlap check against BenHalluEval and within v2 (`src/dataset2/check_overlap.py`) | Claude | overlap report |
| 7 | Check every new question, gold, passage and source (keep / fix / drop) | one checker (named) | check sheet |
| 8 | Genre labels for all 1,100 questions, blind: the three genre annotators, as in v1.1. Keep a question only if the majority genre is the intended one | three genre annotators | genre sheets, Fleiss' kappa |
| 9 | Passage labels for every new answer, blind: Umme Zoayria Abedin and Md Saminul Amin, each alone, as in v1.1. Disagreements are settled by discussion | two annotators | raw sheets, Cohen's kappa |
| 10 | Build the package (`data/final/GenreHalluEval-v2.0/`), the split, the notebooks (12-genre support) | Claude, then Mahdi | package |
| 11 | Runs: the learn half (every judge, both conditions), then the routed and single-best notebooks on the test half | Mahdi (Kaggle) | outputs |

## Rules for new questions (Claude)

- **Source:** the passage is copied word for word from the current version of its source.
  - Wikipedia: we record the title, revision id, timestamp and access date, and keep the raw API download.
  - News: we record the site, URL, publication date and access date.
  - If a source can't be reached, its question is not used.
- **The question:**
  - The gold answer is stated in the passage (a span or a short phrase).
  - The question can be answered without the passage by someone who knows the fact.
  - It fits exactly one genre of guide v2.0.
- **Facts that can change** (officeholders, records, counts) are written "as of 2026" and checked against the
  current source.
- **No overlap:** not the same fact or the same Wikipedia passage as BenHalluEval or as another v2 question.
- **Hallucinations:** the frozen writing guide is used. Each hallucination is wrong both by the passage and in the real world.

## The experiment (first draft; see the updates below)

- **Split:** stratified by genre: 50 + 50 questions per genre.
  - Learn half (550 questions): every judge judges every answer, with and without the passage.
  - Test half (550 questions): each question in one condition, half with the passage and half without.
- **Pool:** gemma4-31b, qwen3.5-27b, gpt-oss-20b and deepseek-r1-14b with English prompts, and tigerllm-9b with Bangla
  prompts, as in the last split.
- **Cells:** a half has 50 questions per genre, so the locked minimum of 50 (golden rule 5) can be kept for the
  our-genre table. Own-genre cells need 50 named questions too; some will fall below that. Decide before the
  registration.
- **Tests:** R vs A with the passage and without it, paired bootstrap over questions (10,000 re-samples), Holm over the
  2 tests. D, E and F are exploratory.

## Cost (estimates)

| Item | Amount |
|---|---|
| Claude's writing | 870 questions + golds and 3,480 hallucinations, in about 18 batches over several sessions |
| Team checking | 870 question checks; 1,100 × 3 genre labels; 4,350 new answers × 2 annotators (v1.1 was 1,250 × 2) |
| GPU (Kaggle) | learn half about 19 h (two sessions); test half about 8 h; about 27 GPU hours in total, more than one week's free quota, so plan for two weeks |

## Update, 2026-10-29: what was built (this replaces the counts and the experiment section above where they differ)

- **12 genres:** GRAMMAR (Bangla grammar) was added on 2026-10-28. 88 GRAMMAR questions come from the NCTB class 9-10
  grammar book; 12 grammar questions moved from CULTURE, and CULTURE was refilled. Total: 1,200 questions = 230 kept
  from v1.1 + 970 new; 100 per genre; 6,000 answers.
- **Checking (changed from steps 7-9 above):** a blind, stratified 20% sample was checked by Umme Zoayria Abedin and
  Md Saminul Amin, alone: 194 new questions (genre, question quality, all 970 answers) and 46 kept v1.1 questions
  (genre). Answer kappa 0.990; genre kappa 0.991. Mahdi kept Claude's drafted genres. The other 80% are not
  human-checked; the paper must say so.
- **Split:** 50 + 50 per genre, stratified also by origin (v1.1 / new); test half 25 + 25 per genre with / without the
  passage (`data/final/GenreHalluEval-v2.0/split.csv`).
- **Cells:** 50+ questions (golden rule 5).
- **Main tests:** R vs A and F vs A, with and without the passage: 4 tests, Holm over 4. D and E are extra.
- **Labels:** v1.1 answers keep their agreed passage labels; new answers use the design labels
  (`data/labels/genrehallueval_v2/labels_v2.0.csv`).
- **Still to do before any run:** freeze genre guide v2.0 and the genre prompts. The v1.1 source
  re-check (step 3) is not folded in: the v1.1 passages are used as they are in v1.1, and the passage defines truth.

## Update, 2026-10-30: the test half (decided after the learn run, before any test run)

- No OSF registration for v2 (Mahdi).
- One route per notebook (Mahdi): `ghe2_route_E` (the best guesser names the genre; the best judge for that genre
  judges), `ghe2_route_F` (every LLM with an own-genre cell names the genre; the LLM with the best learn-half score
  inside the genre it named judges), `ghe2_route_R` (the better of the two paths) and `ghe2_single_best` (A). Each
  route's cost is measured on its own. The combined routed notebook was never run.
- F now asks every LLM with an own-genre cell (all 5), as in the original definition of F. In the combined notebook
  (and in the v1.1 and split notebooks) F used only R's askers.
- **Main tests:** E vs A, F vs A and R vs A, with and without the passage: 6 tests, Holm over 6
  (`data/final/GenreHalluEval-v2.0/test_plan_v2.json`, sha256 `beab2a43…`). This replaces the 4 tests in `pool.json`.
- Scoring: `src/genrehallueval_v2/compare_v2.py`.
