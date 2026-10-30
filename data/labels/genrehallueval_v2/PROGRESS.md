# GenreHalluEval v2: progress of the 970 new questions (Claude)

**Status (2026-10-28):** 970 of 970 written, with hallucinations; all checks pass (0 errors). The 12th genre GRAMMAR
(Bangla grammar) was added on Mahdi's request: 88 questions from the NCTB class 9-10 grammar book (`grammar_book/`)
plus 12 grammar questions moved from CULTURE (g2-003, 013, 030, 031, 032, 034, 037, 149-153; genre field changed
in place), and CULTURE was refilled with 12 new questions (batch 15). The blind check sheets are in `check_v1/`.
**Check result (2026-10-29, `check_v1/agreement_v1.md`):** answer labels annotator 1 vs 2 kappa 0.990 (969 answers),
annotator 1 vs design 1.000, annotator 2 vs design 0.990 (2 golds and 1 C differ; an upper bound, as both marked exactly
one answer correct per question); genre annotator 1 vs 2 kappa 0.991 (240 questions), vs Claude's draft 0.973 and
0.982; 4 questions where both annotators chose another genre than the draft (g2-487, g2-677, g2-420, d2-194); every
question_ok = yes. **Decision (Mahdi, 2026-10-29): keep Claude's draft genre for all questions**, including the 4
above and the 2 split cases (g2-052, g2-648); report the draft-vs-annotator kappas. Answer labels: the design label
stands (annotator 1 agrees on all three rows where annotator 2 differs).

**Target:** 1,200 questions = 230 kept from v1.1 + 970 new, written by Claude, so that each of the 12 genres has 100.
**Check:** two annotators blind-check a random 20% of the new questions (194, stratified by genre, seed 2026), plus
46 of the 230 for the single-genre label only. Drawn once, after all 970 existed (`make_check_sheets.py`).

## How a batch is made

1. Write a title list `titles/<genre>_<n>.txt` (`GENRE|Bangla Wikipedia title`).
2. `python3 -I src/genrehallueval_v2/fetch_passages.py . titles/<file> <batch>`: saves the raw API answers and
   `data/raw/genrehallueval_v2/new/<batch>__candidates.csv`.
3. Read the leads compactly: `python3 -I /private/tmp/claude-503/show.py <candidates.csv>` prints the first 2
   paragraphs of each lead, 380 characters each. Recreate the script if the folder was cleared.
4. Write `new_questions/batch_NN.txt` (`GENRE|title|paragraph|question|gold`).
   - The gold must appear word for word in the paragraph.
   - The question must fit one genre of `docs/genre-guide-v2.md`.
   - It must not repeat a BenHalluEval fact.
   - It must not use the article of a kept v1.1 question (`add_questions.py` now checks this against the source
     check file).
5. `python3 -I src/genrehallueval_v2/add_questions.py .` rebuilds `new_questions_claude.csv` from all batch files.
   Fix a question by editing its line in place, never by reordering lines.
6. `python3 -I src/dataset2/check_overlap.py . data/labels/genrehallueval_v2/new_questions_claude.csv`: replace every
   same-fact or same-article flag that is real.
7. Write `hallucinations_claude/batch_NN.txt` (`id|F|C|S|I`, frozen writing guide v1.0), then check it with
   `python3 -I src/genrehallueval_v2/check_hallucinations.py . <file>`.

## Needed per genre (new)

| Genre | Needed | Done |
|---|---|---|
| HISTORY | 87 | 87 (done) |
| POLITICS | 72 | 72 (done) |
| EDUCATION | 96 | 96 (done) |
| ARTS | 67 | 67 (done) |
| CULTURE | 100 | 100 (done; 12 moved to GRAMMAR, refilled by batch 15) |
| SPORTS | 87 | 87 (done) |
| SCIENCE | 77 | 77 (done) |
| TECHNOLOGY | 74 | 74 (done) |
| GEOGRAPHY | 67 | 67 (done) |
| PLACES | 89 | 89 (done) |
| RELIGION | 54 | 54 (done) |
| GRAMMAR | 100 | 100 (done; 88 from the NCTB book, 12 moved from CULTURE) |

## Batches

| Batch | Downloads | Questions | Hallucinations | Notes |
|---|---|---|---|---|
| 01 | culture_1 | g2-001..g2-052 (48 Culture, 3 Arts, 1 Sports) | done, checked | 2 BenHalluEval same-fact questions replaced (Nabanna month, Muslin cotton) |
| 02 | education_1 | g2-053..g2-128 (76 Education) | done, checked | 5 BenHalluEval overlaps replaced in place (DU year, RU/Bhasani/KUET/Rajshahi College same article) |
| 03 | education_2 | g2-129..g2-148 (20 Education) | done, checked (in hallucinations batch_02) | |
| 04 | culture_2 | g2-149..g2-205 (52 Culture, 2 Arts, 2 Sports, 1 Religion) | done, checked (hallucinations batch_03) | 1 same-article overlap replaced (consonant count) |
| 05 | sports_1 | g2-206..g2-289 (84 Sports) | done, checked (hallucinations batch_04) | overlap flags were false alarms (generic answers) |
| 06 | science_1 | g2-290..g2-366 (77 Science) | done, checked (hallucinations batch_05) | 105 written, 8 BenHalluEval overlaps (relativity year, gene, ilish, blue whale, bee, Newton, Galileo, S. N. Bose) and 20 weak ones dropped before ids were fixed |
| 07 | technology_1 | g2-367..g2-440 (74 Technology) | done, checked (hallucinations batch_06) | 108 written; 18 used the article of a v1.1 question, 5 BenHalluEval overlaps (Google, Apple founders, Facebook, GPS, Steve Jobs) and 11 weak ones dropped. In batch 06, g2-329 (Sun) and g2-346 (DNA) used v1.1 articles and were replaced in place (rainbow, tuberculosis) with new hallucinations |
| 08 | geography_1 | g2-441..g2-507 (67 Geography) | done, checked (hallucinations batch_07) | 102 written (17 v1.1 articles skipped before writing); 7 BenHalluEval overlaps (Andes, Sundarbans, Canada, Sylhet division, Hakaluki, Kenya, Morocco capital) and 28 weaker ones (mostly capitals and famous country facts) dropped |
| 09 | places_1, places_2 | g2-508..g2-596 (89 Places) | done, checked (hallucinations batch_08) | 123 written; 1 BenHalluEval overlap (Kolkata metro year) and 33 weaker ones (mostly 'which city' questions and very famous facts) dropped |
| 10 | history_1 | g2-597..g2-683 (87 History) | done, checked (hallucinations batch_09) | 104 written; 12 BenHalluEval overlaps (Mesopotamia, Egypt, Gupta, Buxar, East India Company, 1770 famine, Operation Jackpot, World War II alliances, Temujin, Osman, Jallianwala Bagh, Vasco da Gama) and 5 very famous facts dropped |
| 11 | politics_1 | g2-684..g2-755 (72 Politics) | done, checked (hallucinations batch_10) | 84 written; current-officeholder facts avoided; 8 BenHalluEval overlaps (Awami League founding, flag map, Indian constitution, BJP, Modi, Putin, Union Parishad, Hitler) and 2 weak ones dropped |

| 12 | arts_1 | g2-756..g2-817 (62 Arts) | done, checked (hallucinations batch_11) | 100 written; 11 BenHalluEval overlaps and 27 famous ones dropped |
| 13 | religion_1 | g2-818..g2-870 (53 Religion) | done, checked (hallucinations batch_12) | 95 written; 9 BenHalluEval overlaps and 33 famous or trivial ones dropped |
| 14 | NCTB grammar book (`grammar_book/book__candidates.csv`) | g2-871..g2-958 (88 Grammar) | done, checked (hallucinations batch_13) | 37 passages transcribed by Claude from the book's page images (no text layer); several questions per passage allowed for GRAMMAR only; 4 overlap flags, all false alarms (generic answers: তিন প্রকার, আরবি, ইংরেজি, চার প্রকার). Wrong sandhi splits avoid vowel-length or spelling variants of the gold split |
| 15 | culture_3 | g2-959..g2-970 (12 Culture) | done, checked (hallucinations batch_14) | refill after the move to GRAMMAR; 18 written, 0 overlap flags, 1 article already used (বাকরখানি) and 5 weaker ones dropped |

## Done steps (formerly 'Resume here')

Arts and Religion were finished (batches 12-13), GRAMMAR was added (batch 14) and CULTURE refilled (batch 15). The blind
check sample was drawn once with `src/genrehallueval_v2/make_check_sheets.py` (seed 2026). Still open:

- Fold the source-check result (`source_check_2026-10-28.csv`: 167 current, 30 changed, 15 not found, 11 not
  Wikipedia, 7 to check by hand) into the package; extend `build_v2.py` to the 970 new questions (book passages need
  their own source fields: book title, page, PDF page).
- Mahdi freezes genre guide v2.0 (now 12 genres + Other) before any judge run.
- Licences before any public release: BenHalluEval, Wikipedia (CC BY-SA), the NCTB book.

## Package built (2026-10-29)

`data/final/GenreHalluEval-v2.0/` (1,200 questions; learn 600 / test 600, 50 + 50 per genre) by
`src/genrehallueval_v2/build_v2.py`; labels `labels_v2.0.csv`; notebooks and Kaggle kit in
`release/kaggle-genrehallueval-v2/`. See the runlog entry "GenreHalluEval v2 (12 single genres)".

