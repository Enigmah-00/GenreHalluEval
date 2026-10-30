# GenreHalluEval v2: checking guide for the two annotators (v1, 2026-10-28)

**Annotator 1:** Umme Zoayria Abedin. **Annotator 2:** Md Saminul Amin.
Each of you gets your own two sheets. Work alone. Do not talk about any row with the other annotator, with Mahdi or
with anyone else until you have both handed in your sheets. Do not use an AI tool to fill the sheets.

## What this check is for

Claude wrote most of the v2 questions from current Bangla Wikipedia passages and from the NCTB class 9-10 Bangla
grammar book, together with one correct answer and four wrong answers for each question. You check a random 20% of them. Your labels tell us how often Claude's
questions, genres and answer labels are right. We report your agreement (Cohen's kappa) in the paper.

The sheets are blind: they do not show Claude's genre, which answer is the correct one, or where a question came from.

## Files

| File | Rows | What you fill |
|---|---|---|
| `<you>__genre.csv` | one row per question | `genre`, `confidence`, `question_ok`, `note` |
| `<you>__answers.csv` | one row per answer | `label`, `note` |

Open the files in Excel or Google Sheets. Save them as CSV (UTF-8) with the same name. Do not change, sort, delete or
add rows, and do not edit the question, passage or answer columns.

## Sheet 1: genre

Read the question and the passage. Do not look for any answer.

- `genre`: write exactly one of these codes:
  `HISTORY`, `POLITICS`, `EDUCATION`, `ARTS`, `CULTURE`, `SPORTS`, `SCIENCE`, `TECHNOLOGY`, `GEOGRAPHY`, `PLACES`,
  `RELIGION`, `GRAMMAR`, `OTHER`.
  Use the definitions and the 10 rules in `docs/genre-guide-v2.md` (GRAMMAR = Bangla grammar: সন্ধি, সমাস, কারক,
  প্রত্যয়, উপসর্গ, পদ, শব্দের শ্রেণি ও উৎস-ভাষা, বানান, বাগধারা and so on).
- `confidence`: `high` if one genre clearly fits, `low` if two genres fit about equally.
- `question_ok`: `yes` if the question is clear and the passage answers it; `no` if the question is unclear, has
  more than one right answer, or the passage does not answer it. Write the reason in `note`.

## Sheet 2: answers

Every row is one answer to one question. The passage is the only source of truth: judge the answer against the
passage, not against what you know or what is true today.

- `label`: write exactly one of:
  - `correct`: the answer is right according to the passage (small differences in wording, spelling or digits are
    fine, for example "১৯৭১ সালে" and "১৯৭১").
  - `hallucinated`: the answer is wrong according to the passage, or it adds a detail that the passage contradicts
    or does not support.
  - `unsure`: you cannot decide. Write why in `note`.
- An answer that is only part of the right answer (for example, one of two names that the question asks for) is
  `hallucinated`.
- Do not guess how many answers per question are correct. Judge every row on its own.

## When you finish

Check that every `genre`, `confidence`, `question_ok` and `label` cell is filled. Send both files to Mahdi.
Your sheets are kept unchanged as raw files; disagreements are discussed only after both of you have handed in.
