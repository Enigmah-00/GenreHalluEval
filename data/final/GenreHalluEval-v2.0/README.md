# GenreHalluEval v2.0

Bangla hallucination-judge test set with 12 single genres x 100 questions (1,200 questions, 6,000 answers). Made by
`src/genrehallueval_v2/build_v2.py` (seed 2026).

- **Questions:** 230 team-written questions kept from GenreHalluEval v1.1 (golds by Mahdi Hasan Qurishi) and 970
  questions written by Claude (claude-opus-5-5) from current sources: Bangla Wikipedia (title, revision id and time
  in `questions.csv`) and, for 88 GRAMMAR questions, the NCTB class 9-10 Bangla grammar book (book page in `source`).
- **Answers:** every question has its gold answer and 4 hallucinated answers written by Claude (F = a wrong fact of
  the same kind, C = a misread question, S = the gold plus a false detail, I = a wrong inference). The passage defines
  the truth.
- **Checks:** two annotators (Umme Zoayria Abedin, Md Saminul Amin) labelled a blind, stratified 20% sample alone: 194
  Claude-written questions (genre, question quality, all 970 answers) and 46 kept v1.1 questions (genre). Answer
  labels: kappa 0.990 between the annotators; genre: kappa 0.991, and 0.973 / 0.982 against the genre used here.
- **Genres:** History, Politics, Education, Arts, Culture, Sports, Science, Technology, Geography, Places, Religion, Grammar (guide `docs/genre-guide-v2.md`; prompts `genre_v2`, `genre_bn_v2`).

## Files

- `learn_items.csv`: the learn half, 600 questions (50 per genre); every answer twice, once per
  condition (6000 rows). Every pool judge judges every row; every pool LLM names the genre of every
  question.
- `test_items.csv`: the test half, 600 questions, 3000 answers; each
  question in one condition: with the passage 300 questions (25 per genre), without it
  300.
- `questions.csv`: one row per question (genre, origin, half, test condition, question, gold, passage, source).
- `split.csv`: the half and test condition of every question. The split is stratified by genre and, inside each genre,
  by origin (learn: 118 v1.1 + 482 new; test:
  112 + 488).
- `pool.json`: the judges, the prompt language per judge (TigerLLM: Bangla), the genres, the cell minimum
  (50) and the main tests, all fixed before any run.
- `prompts/`: genre and judge prompts in English and Bangla.
- `lock_ghe2_v1.json` (added after the learn run, by `src/genrehallueval_v2/make_lock_v2.py`): the routes for the test
  half.

`design_label`: 0 = correct, 1 = hallucinated. Item ids of v1.1 questions are those of v1.1.
