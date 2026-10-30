# BenHalluEval-QA v1.2 (audited and human-reviewed seeds + new hallucinated answers), Bangla

A Bangla hallucination-detection set. Each item is **passage + question + one answer**, and the label says
whether the answer is hallucinated **relative to the passage**. Every question has 5 answers: 1 correct
(the audited gold) and 4 hallucinated, one of each type (factualness, comprehension, specificity, inference).

> **This is not the original BenHalluEval.** The questions and passages are BenHalluEval's QA seeds
> (from TyDiQA-GoldP, Bengali), audited by Claude and reviewed by a person. The original 4,000
> hallucinated answers (written by GPT-5.4) are not in the public BenHalluEval download, so **all 3,896
> hallucinated answers here are new**. Claude (`claude-opus-5-5`) wrote them in batches of 25 questions
> under a frozen guide (`docs/hallucination_writing_guide_v1.md`). Judge scores on this set are **not
> comparable** to the numbers printed in the BenHalluEval paper.

Version 1.2, built 2026-10-17. Facts in time-sensitive answers are as of 2026-10-13 (web check) or
2026-10-17 (human review).

## Numbers

| | Count |
|---|---|
| Questions (seeds) used | 974 (997 unique questions; 23 excluded, see `seeds.csv`) |
| Items | 4,870 = 974 correct + 3,896 hallucinated |
| Hallucinated per type | 974 each: factualness, comprehension, specificity, inference |
| Recommended main set (`include_main = yes`) | all 974 questions |
| Seeds flagged `weak_gold = yes` (kept, flagged) | 9 |
| Time-sensitive seeds (`time_sensitive = yes`) | 39 |
| Human blind check | 198 questions (990 answers): agreement 99.8% with our labels, Cohen's kappa 0.994 |

Questions per genre (frozen genre guide v1.0; labels LLM-drafted, human-verified):

| Genre | Questions |
|---|---|
| History, Politics & Education | 300 |
| Arts, Culture & Sports | 296 |
| Science & Technology | 147 |
| Geography & Places | 121 |
| Religion | 97 |
| Other | 13 |

## Files

| File | What it is |
|---|---|
| `items.csv` | The dataset: 4,870 rows, one per (question, answer). Use this. |
| `seeds.csv` | 997 seeds (passage, question, gold) with the full record of what changed and why, including the human review (`human_review`, `human_note`, `followup_note`). |
| `human_validation_blind198.csv` | The blind human check: one person's yes/no and naturalness (1–3) for 990 answers, next to our label. |
| `gold_issues.csv` | 131 notes on gold answers that may be wrong or incomplete in the real world (124 on seeds still in use). Found while writing the hallucinations. Not fixed; for human review. |
| `shortcut_report.md`, `stats.json` | Length and form of each answer type, simple rule baselines, and the human-check numbers. |
| `updates_2026.json` | Web check of the 50 time-sensitive seeds: decision, new gold, patched passage text, source. |
| `prompts/judge_v1.txt`, `prompts/genre_v1.txt` | The two benchmark prompts (judge verdict; genre guess). See `prompts/README.md`. |
| `genre_blind200.csv` | 200 genre labels made blind by one person before seeing any LLM label (v1.0 names). For scoring genre guessers. |
| `docs/hallucination_writing_guide_v1.md` | The frozen rules used to write the hallucinated answers. |
| `docs/genre_guide_v1.md` | The frozen genre guide. |
| `dataset-metadata.json` | Kaggle metadata (set your username in `id` before upload). |
| `checksums.sha256` | SHA-256 of every file. |

All CSV files are UTF-8, comma-separated, with a header row.

## Columns of `items.csv`

| Column | Meaning |
|---|---|
| `item_id` | `<question_id>__a<position>`. Unique per row and **stable across versions**: an item keeps its id even if its text was revised. |
| `question_id` | TyDiQA id. The 5 answers of one question share it. **Bootstrap and split by this column**, never by item. |
| `position` | 0–4. The 5 answers were shuffled once per question (seed 2026), so the gold's position carries no signal. |
| `context` | The passage (Wikipedia text). Some passages were patched (2026 facts, human review); see `seeds.csv` → `context_changed`. |
| `question` | The question (after audit and review). |
| `answer` | The candidate answer the judge must check. |
| `label` | 1 = hallucinated, 0 = correct. |
| `hallucinated` | Same as `label`, as `yes` / `no` (the judge's expected verdict). |
| `answer_type` | `gold`, `F`, `C`, `S` or `I`. |
| `hallucination_type` | `none`, `factualness`, `comprehension`, `specificity` or `inference`. |
| `answer_source` | Where the answer came from (audited gold, or writer + guide version, and whether it was revised in v1.2). |
| `genre`, `genre_fine` | Frozen genre of the question. `genre_fine` keeps "Sports" separate. |
| `audit_status` | `OK`, `TA`, `TU`, `WEAK`, `FIXQ`, `FIXA`, `FIXS` or `UPD` (meanings below). |
| `include_main` | `yes` for all 974. |
| `weak_gold` | `yes` if the gold is defensible for the passage but shaky (see `seeds.csv` → `audit_note`). |
| `time_sensitive` | `yes` if the true answer can change over time. |
| `current_check`, `answer_as_of` | Result and date of the check for time-sensitive seeds (`updated` = web check; `updated_human` = human review). |

`audit_status`:
- **OK**: the gold fits.
- **TA**: true for the passage but outdated in the real world. Kept, because the passage defines truth.
- **TU**: the same as TA, but not verified.
- **WEAK**: see `weak_gold` above.
- **FIXQ**: the question was rewritten so the gold fits the passage.
- **FIXA**: the gold was changed to fit the passage, or changed in the review.
- **FIXS**: the gold span was trimmed or completed.
- **UPD**: the gold and one passage sentence were updated to a current fact.
- **EXCL**: dropped. These seeds appear in `seeds.csv` only, not in `items.csv`.

## How the data was checked

1. **Audit (Claude, 2026-10-13).** Every seed was checked. 139 of 997 original golds did not fit their question.
   Most were fixed by rewriting the question, not the gold. 50 time-sensitive seeds were checked on the web,
   and 22 golds were updated to 2026 facts.
2. **Human review (Mahdi, 2026-10-17).** One person reviewed all 238 changed or flagged seeds.
   - 172 approved as they were.
   - 45 edited (new question, gold or passage).
   - 21 dropped.
   - 2 excluded seeds revived with a new question.
   
   Claude then made 26 follow-ups, each with a written reason, in `seeds.csv` → `followup_note`:
   - wrote each new gold exactly as the passage writes it;
   - fixed typos;
   - patched a passage to agree with an edited gold;
   - made small fixes for problems he flagged.
   
   One edit was **not** applied. Seed `bengali-9099268636899707207-4` would go back to a question that its
   passage contradicts; it is waiting for the reviewer's decision.
3. **Blind human check of the answers (same person, 2026-10-17).** 198 random questions (all 5 answers, 990 rows,
   shuffled, labels hidden) were labelled hallucinated yes/no and rated for naturalness (1–3).
   - 989 labelled. Agreement with our labels 99.8%; Cohen's kappa 0.994.
   - The 2 disagreements are the gold and one hallucination of the same question, marked the other way round
     (it looks like a swapped pair; the passage supports our labels).
   - Naturalness: 982 of 990 rated 3 (natural).
   - All 5 answers of one question were rated 2, because the gold copied an odd case ending from the passage
     (শমীন্দ্রনাথে). That gold was trimmed and its 4 hallucinated answers fixed.
   - 117 of the 990 checked items were revised or dropped after the check (`changed_since_check`).
4. **Answer fixes after the check.** Claude rewrote 30 seeds' hallucinated answers
   (`data/labels/hallucinations_claude/revisions_v1.2.txt` in the project). Reasons:
   - the review changed the gold or the question;
   - an answer had become correct;
   - "more than X" bug: four answers like "more than 120" were technically true when the gold is "more than 269". The validator now checks for this.

## How the hallucinated answers were made

One answer per type, as in BenHalluEval and HaluEval. Each type copies a common human error:

| Type | What goes wrong | Human habit it copies |
|---|---|---|
| F, factualness | A wrong fact of the same kind, from general knowledge | memory swap: the more famous person, a nearby year, a neighbouring place; for updated seeds, the old fact |
| C, comprehension | The question is misread; usually a span from the passage that fills a different slot | skimming and keyword matching |
| S, specificity | The gold plus a precise but false detail, or the wrong level of detail | overconfidence: adding a "precise" detail to sound sure |
| I, inference | The right kind of answer from a wrong reasoning step | arithmetic slip, before/after swap, father → grandfather, লক্ষ ↔ কোটি, CE ↔ Hijri |

Rules (the full text is in the guide):
- Every hallucinated answer is wrong for the passage **and** in the real world, as far as we know.
- It has the same form as the gold: script, Bangla digits, case ending, register.
- It has no hedging and no other tells, and it is plausible.
- The 4 answers of a question are all different.
- No synonyms, spelling variants, or broader or narrower answers that would still be correct.

For each seed, other answers that would also be correct in the real world were listed and avoided.

## Known shortcuts (read before reporting any judge score)

Golds are TyDiQA-GoldP spans, so **every gold is an exact span of the passage**. Most hallucinated answers
are not. A rule that never reads the question gets:

| Rule: say "hallucinated" when … | BHS (lower is better) |
|---|---|
| the answer is not an exact span of the passage | **13.9** |
| the answer contains a comma (catches most S answers) | 39.3 |
| the answer is longer than 24 characters | 43.1 |
| always "hallucinated" | 50.0 |

The span rule beats every judge in the original paper (best: GPT-4.1 mini, 15.56). The original BenHalluEval
QA design has the same property (gold spans, generated hallucinations), but we cannot measure it there.

What to do:
- Report the span baseline next to every judge score.
- Also report scores on the **span subset**: the 2,048 items whose answer is a passage span (972 golds,
  810 C, 220 I, 46 F). The span rule is useless there, so it shows whether a judge checks that the span
  actually answers the question.
- S answers are longer (mean 37 vs 15 characters), and 94% contain a comma. This comes from the type itself
  ("gold + a false detail"), but it is a surface cue.

## Limitations

- **One writer.** All hallucinations come from one LLM (Claude) under one guide. A judge from the same
  family may find them easier or harder. The original BenHalluEval has the same issue with GPT-5.4.
- **One human checker, who knows the design.** The blind check was done by the project owner. He knew that
  each question has one correct answer among five. A check by a second person would be more independent.
  The very high agreement also reflects the span shortcut: a careful reader can see which answer is copied
  from the passage.
- **Gold answers.** `gold_issues.csv` lists golds that are right for the passage but doubtful or incomplete
  in the real world. The passage defines truth in this task.
- **Time-sensitive facts** are as of October 2026 and will go out of date. Some updated figures (student
  counts, unions, universities) come from the human reviewer and were not re-checked by Claude.
- **Hard subset.** BenHalluEval kept only questions that three small models failed closed-book, so this
  is not a random sample of TyDiQA.
- Genre labels were drafted by an LLM and verified by one person (blind agreement kappa 0.81 on 200).

## Licence and sources

- The passages are Wikipedia text, taken from TyDi QA. TyDi QA is released under Apache 2.0; Wikipedia text
  is CC BY-SA.
- The choice of seeds comes from BenHalluEval (arXiv 2605.31483). We have not confirmed its data licence.
- **Before any public release**, confirm BenHalluEval's licence. Until then keep the Kaggle dataset private.
  The metadata suggests CC BY-SA 4.0 because the passages are Wikipedia text.

## Cite

If you use this set, cite:
- BenHalluEval (arXiv 2605.31483);
- TyDi QA (Clark et al., TACL 2020);
- HaluEval (Li et al., EMNLP 2023).

Describe the hallucinated answers as "written by claude-opus-5-5 under a frozen guide; not the original GPT-5.4 answers".

## Version history

- **v1.2 (2026-10-17):** human review of the 238 changed seeds applied (21 dropped, 2 revived), 30 seeds'
  hallucinated answers revised, the blind human check added. Item ids are unchanged.
- **v1.1 (2026-10-14):** audited seeds + 3,960 new hallucinated answers + shortcut report.
