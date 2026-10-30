# GenreHalluEval split (exploratory)

Made by `src/split/build_split.py` from GenreHalluEval v1.1 (seed 2026; stratified by our genre).

- `learn_items.csv`: the learn half, 125 questions; every answer appears twice, once per condition
  (1250 rows). Every pool judge judges every row; every pool LLM names the genre of every question.
- `test_items.csv`: the test half, 125 questions, 625 answers;
  each question in one condition: with the passage 63 questions (315
  answers), without it 62 (310 answers).
- `split.csv`: the half and test condition of every question. `pool.json`: the pool, the prompt language per model
  (TigerLLM: Bangla) and the rules, fixed before any run.
- `prompts/`: the English prompts of every run, and the Bangla prompts of TigerLLM's Bangla-prompt run.
- `lock_split_v1.json` (added after the learn run, by `src/split/make_split_lock.py`): the routes for the test half.

Item and question ids are those of GenreHalluEval v1.1. Labels are not in this package.
