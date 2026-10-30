# BenHalluEval-QA v1.1 (audited seeds + new hallucinated answers), Bangla

A Bangla hallucination-detection set. Each item is **passage + question + one answer**, and the label says
whether the answer is hallucinated **relative to the passage**. Every question has 5 answers: 1 correct
(the audited gold) and 4 hallucinated, one of each type (factualness, comprehension, specificity, inference).

> **This is not the original BenHalluEval.** The questions and passages are BenHalluEval's QA seeds
> (from TyDiQA-GoldP, Bengali), audited and corrected by us. The original 4,000 hallucinated answers
> (written by GPT-5.4) are not in the public BenHalluEval download, so **all 3,960 hallucinated answers here
> are new**. Claude (`claude-opus-5-5`) wrote them in batches of 25 questions under a frozen guide
> (`docs/hallucination_writing_guide_v1.md`). Judge scores on this set are **not comparable** to the
> numbers printed in the BenHalluEval paper.

Version 1.1, built 2026-10-14. Facts in time-sensitive answers are as of 2026-10-13.

## Numbers

| | Count |
|---|---|
| Questions (seeds) used | 990 (997 unique questions; 7 excluded, see `seeds.csv`) |
| Items | 4,950 = 990 correct + 3,960 hallucinated |
| Hallucinated per type | 990 factualness, 990 comprehension, 990 specificity, 990 inference |
| Recommended main set (`include_main = yes`) | all 990 questions |
| Seeds flagged `weak_gold = yes` (kept, flagged) | 51 |
| Time-sensitive seeds (`time_sensitive = yes`) | 50 (22 updated to 2026 facts) |

Questions per genre (frozen genre guide v1.0; labels LLM-drafted, human-verified):

| Genre | Questions |
|---|---|
| History, Politics & Education | 311 |
| Arts, Culture & Sports | 296 |
| Science & Technology | 147 |
| Geography & Places | 125 |
| Religion | 97 |
| Other | 14 |

## Files

| File | What it is |
|---|---|
| `items.csv` | The dataset: 4,950 rows, one per (question, answer). Use this. |
| `seeds.csv` | 997 seeds (passage, question, gold) with the full audit trail: original text, what changed and why. |
| `gold_issues.csv` | 124 notes on gold answers that may be wrong or incomplete in the real world. Found while writing the hallucinations. Not fixed; for human review. |
| `shortcut_report.md`, `stats.json` | Length and form of each answer type, and simple rule baselines (see "Known shortcuts"). |
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
| `item_id` | `<question_id>__a<position>`. Unique per row. |
| `question_id` | TyDiQA id. The 5 answers of one question share it. **Bootstrap and split by this column**, never by item. |
| `position` | 0–4. The 5 answers were shuffled per question (seed 2026), so the gold's position carries no signal. |
| `context` | The passage (Wikipedia text). For 22 updated seeds one sentence was patched to the 2026 fact. |
| `question` | The question (after audit fixes). |
| `answer` | The candidate answer the judge must check. |
| `label` | 1 = hallucinated, 0 = correct. |
| `hallucinated` | Same as `label`, as `yes` / `no` (the judge's expected verdict). |
| `answer_type` | `gold`, `F`, `C`, `S` or `I`. |
| `hallucination_type` | `none`, `factualness`, `comprehension`, `specificity` or `inference`. |
| `answer_source` | Where the answer came from (audited TyDiQA gold, or writer + guide version). |
| `genre`, `genre_fine` | Frozen genre of the question. `genre_fine` keeps "Sports" separate. |
| `audit_status` | `OK`, `TA`, `TU`, `WEAK`, `FIXQ`, `FIXA`, `FIXS` or `UPD` (meanings below). |
| `include_main` | `yes` for all 990. (UPD and FIXA seeds were `check` only until hallucinations existed; they now pass.) |
| `weak_gold` | `yes` if the gold is defensible for the passage but shaky (see `seeds.csv` → `audit_note`). |
| `time_sensitive` | `yes` if the true answer can change over time. |
| `current_check`, `answer_as_of` | Result and date of the web check for time-sensitive seeds. |

`audit_status`: **OK** gold fits; **TA** true for the passage but outdated in the real world (kept, the
passage defines truth); **TU** the same, unverified; **WEAK** see above; **FIXQ** the question was rewritten
so the gold fits the passage; **FIXA** the gold was changed to fit the passage; **FIXS** the gold span was
trimmed or completed; **UPD** gold and one passage sentence updated to the 2026 fact.

## How the hallucinated answers were made

One answer per type, as in BenHalluEval and HaluEval. Each type copies a common human error:

| Type | What goes wrong | Human habit it copies |
|---|---|---|
| F, factualness | A wrong fact of the same kind, from general knowledge | memory swap: the more famous person, a nearby year, a neighbouring place; for updated seeds, the old fact |
| C, comprehension | The question is misread; usually a span from the passage that fills a different slot | skimming and keyword matching |
| S, specificity | The gold plus a precise but false detail, or the wrong level of detail | overconfidence: adding a "precise" detail to sound sure |
| I, inference | The right kind of answer from a wrong reasoning step | arithmetic slip, before/after swap, father → grandfather, লক্ষ ↔ কোটি, CE ↔ Hijri |

Rules (full text in the guide): every hallucinated answer is wrong for the passage **and** in the real world
as far as we know; it has the same form as the gold (script, Bangla digits, case ending, register); no
hedging or tells; plausible; the 4 answers are distinct; no synonyms, spelling variants, or broader/narrower
answers that are still correct. Real-world alternatives that would also be correct were listed per seed
and avoided (for example "৮০ হিজরী" when the gold is the same date in CE).

Automatic checks (`src/halluc/validate.py`): every seed covered once, 4 distinct answers that differ from
the gold, no Devanagari, Latin letters only where the gold or the topic has them.

## Known shortcuts (read before reporting any judge score)

Golds are TyDiQA-GoldP spans, so **every gold is an exact span of the passage**. Most hallucinated answers
are not. A rule that never reads the question gets:

| Rule: say "hallucinated" when … | BHS (lower is better) |
|---|---|
| the answer is not an exact span of the passage | **13.7** |
| the answer contains a comma (catches most S answers) | 39.3 |
| the answer is longer than 24 characters | 43.1 |
| always "hallucinated" | 50.0 |

The span rule beats every judge in the original paper (best: GPT-4.1 mini, 15.56). The original BenHalluEval
QA design has the same property (gold spans, generated hallucinations), but we cannot measure it there.
What to do:

- report the span baseline next to every judge score;
- also report scores on the **span subset**: the 2,076 items whose answer is a passage span (990 golds,
  821 C, 221 I, 44 F). The span rule is useless there, so it shows whether a judge checks that the span
  actually answers the question;
- S answers are longer (mean 37 vs 15 characters) and 94% contain a comma. This is built into the type
  ("gold + a false detail"), but it is a surface cue.

## Limitations

- **One writer.** All hallucinations come from one LLM (Claude) under one guide. A judge from the same
  family may find them easier or harder. The original BenHalluEval has the same issue with GPT-5.4.
- **Not yet human-validated.** A native speaker has not yet checked the hallucinated answers. A blind
  20% sample (198 questions, 990 items) is ready for that. In a random spot check of 30 questions, 2 of 120
  hallucinated answers were arguably correct in the real world and were replaced. So expect roughly 1–3%
  of hallucinated answers to be debatable until the human check is done. This is an estimate, not a
  measurement.
- **Naturalness is unmeasured.** The answers were written to look like human mistakes, but nobody has
  rated that yet. The validation sheet has a 1–3 naturalness column.
- **Gold answers.** 139 of 997 original golds did not fit their question; we fixed or flagged them (see
  `seeds.csv`). Another 124 notes in `gold_issues.csv` list golds that are right for the passage but
  doubtful or incomplete in the real world. The passage defines truth in this task.
- **Time-sensitive facts** are as of 2026-10-13 and will go out of date.
- **Hard subset.** BenHalluEval kept only questions that three small models failed closed-book, so this
  is not a random sample of TyDiQA.
- Genre labels were drafted by an LLM and verified by one person (blind agreement kappa 0.81 on 200).

## Licence and sources

- Passages are Wikipedia text via TyDi QA (TyDi QA is released under Apache 2.0; Wikipedia text is
  CC BY-SA). The seed selection comes from BenHalluEval (arXiv 2605.31483), whose data licence we have not
  confirmed.
- **Before any public release**, confirm BenHalluEval's licence. Until then keep the Kaggle dataset private.
  The metadata suggests CC BY-SA 4.0 because the passages are Wikipedia text.

## Cite

If you use this set, cite BenHalluEval (arXiv 2605.31483), TyDi QA (Clark et al., TACL 2020) and HaluEval
(Li et al., EMNLP 2023), and describe the hallucinated answers as "written by claude-opus-5-5 under a
frozen guide; not the original GPT-5.4 answers".

## Version history

- **v1.1 (2026-10-14):** audited seeds v1.1 + 3,960 new hallucinated answers + shortcut report.
