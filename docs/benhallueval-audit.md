# BenHalluEval QA audit and genre labels (v1.3, 2026-10-17)

This file explains what we changed in the BenHalluEval QA seeds, why, and what is still pending. The data
file is `data/final/benhallueval_qa_seeds_v1.3.csv`. Scripts: `src/audit/` and `src/genre/`. The original
download in `data/raw/` is never edited. Older versions are in `data/final/superseded/`.

**v1.3 (2026-10-17):** every seed was checked against today's world, using Mahdi's review method (changes
proposed by Claude; Mahdi reviewed all 125 and approved them without edits on 2026-10-18). 5 facts updated, 19 questions dated, 33 world-wrong golds fixed, 14 stale passage
sentences fixed, 54 seeds dropped (44 duplicates). Main set: 920 questions, 4,600 items (section 4c). Package:
`data/final/benhallueval-qa-v1.3/`.

**v1.2 (2026-10-17):** Mahdi reviewed all 238 changed or flagged seeds and did the blind check of the
hallucinated answers (section 4b). 21 seeds dropped, 2 revived, 45 edited; 30 seeds' hallucinated answers
revised. Main set then: 974 questions, 4,870 items (now in `data/final/superseded/v1.2/`).

**v1.1 (2026-10-13):** time-sensitive gold answers were checked on the web and 22 were updated to the 2026
fact (section 3a). Item 145 was rewritten (`FIXQ`), and item 732's rewrite was put in the past tense.

**Hallucinated answers (2026-10-14):** the original 4,000 GPT-5.4 answers are not public, so Claude wrote
3,960 new ones (section 4a). The 26 `check` seeds (UPD, FIXA) are now `include_main = yes`, because their
hallucinations were written against the final gold.

## 1. What a "seed" is

BenHalluEval QA has 1,000 seeds. Each seed is one passage, one question and one gold (correct) answer, all
from TyDiQA-GoldP. GPT-5.4 then wrote 4 hallucinated answers per seed, which gives 5,000 items. A judge sees
the passage, the question and one answer, and says whether the answer is hallucinated **relative to the
passage**.

## 2. Problems found

| Problem | Count | What we did |
|---|---|---|
| Duplicate rows (identical in every column) | 3 rows | Merged: **997 unique questions**. Rows 462 and 738 copy row 240; row 870 copies row 130. |
| Question or gold written in Devanagari (Hindi) script | 4 | Rewritten in Bangla from the passage (status `FIXS`) |
| **Gold answer does not answer the question** | **139 (13.9%)** | 124 questions rewritten (`FIXQ`), 4 golds fixed (`FIXA`), 7 excluded (`EXCL`) |
| Gold partly right, incomplete or debatable | 51 | Kept and flagged (`WEAK`) |
| "Current" or "latest" questions (`time_sensitive = yes`) | 50 | Checked on the web (section 3a): 22 golds updated (`UPD`), 28 kept and flagged |
| Question names a year, e.g. "(২০১৯)" | 17 | Kept (`TA`); the gold is right for that year |
| No problem | 744 | `OK` |

Examples of a gold answer that does not answer its question:

- "When was Kolkata airport built?" → gold "১৯৩৭", which is the year of Amelia Earhart's flights. The
  passage says the airport was built in 1924.
- "How many countries took part in the first Olympics?" → gold "৪৩", which is the number of events. The
  passage says there were 14 countries.
- "Who was the last emperor of China?" → gold "Yuan Shikai". This one is kept as `WEAK`, because the passage
  says he declared himself emperor in 1915.

**Why this matters.** A good judge correctly says that a wrong gold answer is not supported by the passage.
BenHalluEval then counts that as the judge's mistake (a Track A error). So the paper's Track A errors are
partly label errors.

**A hypothesis to test (not yet verified).** BenHalluEval kept only questions that three models all got
"wrong" closed-book. A model that gives the true answer to a question whose gold is wrong is marked wrong.
So this filter may have *selected for* label errors. To test it, audit about 100 TyDiQA questions that were
**not** selected and compare error rates. The file `banglahallueval_qa_dataset.csv` lists those questions,
but the passages must be fetched from TyDiQA.

## 3. Rules we followed

- **The passage defines truth.** BenHalluEval asks "is the answer supported by the passage?", not "is it
  true in 2026?". So a 2026 fact may replace an old gold **only if the passage sentence that states the old
  fact is changed too**. Otherwise the gold would disagree with its own passage, and judges would be right
  to flag it.
- **Rewrite the question, not the gold.** The 4 hallucinated answers were generated around the original
  gold. If we change the gold, a hallucinated answer could become correct by accident (for example, a
  hallucination "১৪" for the Olympics question). So for most errors we rewrote the question so the
  original gold becomes correct for the passage (`FIXQ`). The gold and its 4 hallucinations stay together.
- **Fix the gold only for broken spans** (`FIXA`), such as "৯৮১" instead of "১৯৮১". These must be checked
  against the 4 hallucinated answers before use (was `include_main = check`; resolved 2026-10-14, see 4a).
- **Exclude** when the passage cannot answer any sensible version of the question (`EXCL`,
  `include_main = no`).
- **Update a time-sensitive gold only together with its passage** (`UPD`, section 3a).
- **Flag rather than delete** debatable (`WEAK`) and time-sensitive (`TU`) items. The main analysis keeps
  them; a sensitivity analysis drops them. Time-sensitive items are also a ready-made test of whether judges
  trust their own knowledge over the passage.

## 3a. 2026 update of time-sensitive answers (v1.1)

Mahdi asked for "current" answers to be brought up to date, with the question left unchanged. Claude
checked all 50 time-sensitive seeds with web search on 2026-10-13. Every decision, its source links and
the exact passage edits are in `data/labels/updates_2026.json`.

| Result | Count | What we did |
|---|---|---|
| `updated` | 22 | Gold replaced by the 2026 fact. The one or two passage sentences that stated the old fact were rewritten to state the new one. Status `UPD`. |
| `still_correct` | 4 | Gold still true (Netanyahu, Maanayata Dutt, Robert A. Daly, Oli Ahmed's LDP). Netanyahu must be re-checked after Israel's 27 Oct 2026 election. |
| `kept_vacant` | 4 | Kolkata mayor: the post has been empty since 5 June 2026, so there is no current answer. Gold kept. |
| `kept_unverified` | 20 | No reliable 2026 figure, or the sources disagree (student counts, populations, unions, universities, euro users). Gold kept. |

Examples: latest FIFA World Cup 2018 → 2026 and winner France → Spain; Andhra Pradesh capital Hyderabad →
Amaravati; Iran provinces 30 → 31; Iraq parliament seats 275 → 329; West Bengal's current CM is the 8th →
9th (Suvendu Adhikari).

Rules:

- The question is never changed. Only the gold and the passage sentence(s) that state the old fact change.
  The original gold and passage are kept in `correct_answer_original` and `context_original`.
- The build fails if a passage edit does not match exactly once, or if the new gold is not in the new
  passage.
- v1.1 also had `benhallueval_qa_seeds_v1.1_original_facts.csv`, the same table without these 22 updates
  (now in `data/final/superseded/v1.1/`). It is not built for v1.2: the hallucinated answers use the old facts
  as wrong answers, so the two cannot be mixed.

**Risk to check (resolved 2026-10-14: the hallucinations were rewritten for the new gold, see 4a).** The original 4 hallucinated answers were written for the old gold. GPT-5.4 knows many 2026-era
facts, so it may have written the *new* fact as a "hallucination" (for example "অমরাবতী" when the passage
said Hyderabad). That answer would now be correct. So every `UPD` seed has `include_main = check` until its
4 hallucinated answers are checked.

**BNP question.** The dataset has no "current BNP secretary-general" question. Item 145 asked who held the
secretary-general post before Mirza Fakhrul, but its passage is about the senior joint secretary-general
post in 2009, so the question was rewritten (`FIXQ`). (For the record: Fakhrul was elected President of
Bangladesh in August 2026, and Ruhul Kabir Rizvi is BNP's acting secretary-general.)

## 4. Genre labels

- **Method:** Claude drafted the genres (guide v0.1 → v0.2), and Mahdi labeled 200 questions blind. The guide
  was revised to v1.0 (frozen), and then Mahdi checked all 997 drafts.
- **Blind agreement**, Mahdi vs Claude's v0.2 draft: kappa **0.806** (95% range 0.737 to 0.866). This is the
  clean number.
- **After applying the rules Mahdi decided** to 12 of his 200 blind labels: kappa 0.895. Report this only
  next to the clean number.
- **Verification:** Mahdi changed 15 of 997 drafts (1.5%).
- **Anchoring:** on the 200 blind questions, Mahdi's blind label and his own verified final label differ in
  27 cases (13.5%; about 12 are explained by rules decided later). So people accept a shown draft much
  more often than they would choose it themselves. Report the labels as "LLM-drafted, human-verified", and
  get a second, independent human blind set (a teammate, guide v1.0) for the paper.
- **Final counts** (`include_main = yes`, 990 questions):

  | Genre | Questions |
  |---|---|
  | History, Politics & Education | 311 |
  | Arts, Culture & Sports | 296 |
  | Science & Technology | 147 |
  | Geography & Places | 125 |
  | Religion | 97 |
  | Other | 14 |

- **Genre changes from rewrites:** 3 genres changed because the rewritten question has a new topic (see the
  `genre_note` column).

## 4a. Hallucinated answers (written 2026-10-14)

- **Why new answers:** the BenHalluEval download has only the seeds, not the 4,000 GPT-5.4 hallucinations.
  So judge scores on our set are not comparable to the paper's numbers. Say this in the paper.
- **Who and how:** Claude (`claude-opus-5-5`) wrote 4 answers per usable seed (990 × 4 = 3,960), one per
  type (F factualness, C comprehension, S specificity, I inference), in batches of 25, under the frozen
  guide `prompts/hallucination_writing_guide_v1.md`. Raw files: `data/labels/hallucinations_claude/`.
  For each seed, real-world alternatives that would also be correct were listed and avoided. For `UPD`
  seeds the old gold is the F answer (except item 329, where the old name is the same airport).
- **Checks:** `src/halluc/validate.py` (coverage, distinct, not equal to the gold, script). A random spot
  check of 30 seeds (120 answers) found 2 answers that were arguably correct in the real world; both were
  replaced. Expect roughly 1–3% debatable answers until a person checks them (an estimate).
- **Gold problems found while writing:** 124 notes in `notes_gold_issues.txt` (package: `gold_issues.csv`).
  They are right for the passage but doubtful or incomplete in the real world. Not fixed.
- **Shortcut:** every gold is a passage span; most hallucinations are not. The rule "hallucinated if not a
  span" scores BHS 13.7 (better than every judge in the paper). Report it next to every judge score, and
  also report the span subset (2,076 items). S answers are longer and 94% contain a comma.
- **Do not pair** these hallucinations with `benhallueval_qa_seeds_v1.1_original_facts.csv`: for `UPD`
  seeds the F answer is the old gold, which is correct in that version.
- **Builder:** `python3 -I src/halluc/build_items.py <root>` writes the package (the blind sheet was made once,
  in v1.1, and is not rebuilt).

## 4b. Human review and blind check (Mahdi, 2026-10-17)

**Review of the 238 changed or flagged seeds** (`data/labels/human_audit_review/review_audit_changes_human_raw.csv`):
- 172 approved as they were.
- 45 edited: a new question, gold or passage, often from current Wikipedia.
- 21 dropped (`approve = 0`): 11 WEAK, 6 TU, 3 already excluded and 1 OK.
- 2 excluded seeds revived with a new question: 489 (Jabir ibn Hayyan) and 780 (the Kavita magazine).

Claude's 26 follow-ups are in `claude_followups_v1.2.json`, each with a reason. In short:
- wrote new golds exactly as the passage writes them (চারটি, not ৪টি; the passage's spelling of McNair;
  "আরবি س-ل-م", whose word order the spreadsheet had flipped; ড়/য় as the passage encodes them);
- fixed typos;
- patched passage 114 to agree with its new gold;
- removed citation marks from gold 485;
- fixed year ১৩৩৫ → ১৩৪৫ in passage 780;
- applied his blind-sheet edits (326, 149, 913, 18, 309);
- rewrote four questions he flagged without a fix (378, 882, 0, 667). **He should check these four.**

`src/audit/apply_human_review.py` turns all of this into `decisions_v1.2.json`, which `build_final_seeds.py`
applies. `data/final/human_review_applied_v1.2.csv` lists every change, row by row.

**Not applied:** seed 432. He asked to go back to the original question (Indira Gandhi / Palam airport, gold
1930). But the passage says Safdarjung was built in 1930 and Palam during the Second World War, so our rewrite
(Safdarjung) is kept. Mahdi approved this in his v1.3 review (2026-10-18).

**Kept by his decision, flagged:** 919. The gold is "আর্যভট্ট", but the passage credits Brahmagupta with
zero as a number. A judge that reads the passage may rightly flag the gold. Consider rewriting the question.

**Blind check of the hallucinated answers** (`data/labels/human_halluc_blind198/..._raw_v2.csv`):
- 198 questions × 5 answers, shuffled, labels hidden.
- All 990 labelled blind. One cell (seed 113, an F answer) arrived blank: Mahdi had labelled it blind, but the cell
  was deleted before he sent the sheet. He restored it (`yes`) on 2026-10-17
  (`data/labels/human_halluc_blind198/restored_labels.csv`).
- Agreement with our labels: 99.8%; Cohen's kappa **0.994**.
- The only 2 disagreements are on seed 471: gold marked hallucinated, the I answer "হোমো স্যাপিয়েন্স" marked
  correct. The passage supports our labels, so this looks like a swapped pair; please recheck.
- Naturalness: 982 of 990 rated 3. All 5 answers of seed 913 were rated 2 because the gold copied a case
  ending (শমীন্দ্রনাথে); fixed.
- His notes found a real bug: four "more than X" answers (seeds 542, 578) were technically true. They are
  fixed, and the validator now checks for this.
- **Caveats for the paper:**
  - the checker is the project owner, who knows the design (one correct answer in five);
  - a careful reader can spot the copied passage span;
  - so the high kappa is an upper bound. A second, independent checker would be stronger evidence.
  - 117 of the 990 checked items changed or were dropped after the check (`changed_since_check` in the
    package's `human_validation_blind198.csv`).

**Hallucinated answers revised:** 30 seeds, in `data/labels/hallucinations_claude/revisions_v1.2.txt`.
- Reasons: the gold, question or passage changed; or the review made an old answer correct (for example 255:
  "Wundt" is the real-world father of psychology; 722: the old F answer became the new gold).
- Item ids are stable: positions are frozen in `data/final/item_positions.csv`, so a revised item keeps its id.
- The notebook re-asks only items whose prompt text changed.

## 4c. Currency and world-fact check (Claude, 2026-10-17, v1.3)

**Why.** Judges that know today's facts should not be penalised for it. In the blind check Mahdi found many
passages and questions that were out of date, and he asked that every sample fit the current world. Claude
proposed changes with his method from the v1.2 review, and Mahdi reviewed all 125 of them (approved without edits,
2026-10-18; `data/labels/human_review_v1.3/`):
- update when a reliable current source exists, with the date in the question (as he did for 606 and 814);
- otherwise rewrite the question to the passage's date or to a lasting fact in the passage (as for 164, 168, 223);
- drop what cannot be verified or fixed cleanly, and duplicates (as for 452, 457, 256, 596, 650).

**How.**
- `src/audit/scan_time_sensitive.py` flagged 394 time-dependent questions (current words, counts, records,
  officeholders, years). A passage scan flagged every "current" sentence about a person or a count.
- All 131 gold-issue notes were reviewed.
- Each flagged seed was read by hand. Decisions and reasons are in `data/labels/currency_check_v1.3.json`.
- `data/final/currency_applied_v1.3.csv` lists every change; `seeds.csv` → `currency_note` has the reason.

**What changed** (125 seeds):

| Kind | Seeds | Examples |
|---|---|---|
| update | 5 | Qatar population 3.37 million (March 2026, National Planning Council); Turkey 86.09 million (31 Dec 2025, TÜİK); Aleppo 2,132,100 (2004 census; the passage dropped a digit); India's constitution now 25 parts, amended 106 times; sharks: more than 500 species |
| pin (dated) | 19 | "বর্তমান (২০১৯)" questions dated to when the passage was true (Maldives president → 2015, the passage's Yameen; book-fair venue → 2017); marriages instead of "wife" (Trudeau, Konkona Sen Sharma); Israel's PM pinned to October 2026 (election on 27 Oct); J&K now a union territory |
| world_fix | 33 | Al-Kahf 12 rukus (not 11); Aztec empire 1428; Asansol is West Bengal's second city; League of Nations 1920; Harington's toilet 1596; Baltoro "one of the longest outside the poles", question now asks its range; first Shaheed Minar (not the central one); Amin Khan (not Aamir Khan) |
| passage | 14 | stale "current" sentences put in the past with real dates (Sheikh Hasina PM until 2024; Manik Sarkar CM 1998-2018; Sovan Chatterjee mayor 2010-2018; Lesnar left WWE) |
| drop | 54 | 44 duplicates (same passage and answer, reworded question; first copy kept). 10 not fixable: unverified counts 387, 578, 748; wrong passages 248, 842, 899, 416; duplicates 925, 503, 952 |

**Hallucinated answers:** 23 seeds revised (`revisions_v1.3.txt`) because their gold or question changed. The
validator passes (920 seeds, 3,680 answers).

**Limits.**
- Mahdi reviewed all 125 v1.3 changes and approved them without edits (2026-10-18). No second person checked them.
- Figures that changed come with sources in the JSON.
- 34 seeds still ask about "now" (verified on 2026-10-13 or 17); re-check them if the set is reused later.
- 74 gold notes stay open. Most say "another answer would also be correct", which the hallucinated answers
  already avoid.

## 5. Still pending (in this order)

1. ~~Mahdi's decisions~~ Done. They were proposed on 2026-10-17 and approved by Mahdi in his v1.3 review on
   2026-10-18: seed 432 keeps the Safdarjung question; the four rewrites (378, 882, 0,
   667) are kept; revived seed 489 is Science & Technology; seed 471 keeps our labels. The lost blind label of seed
   113 was restored by Mahdi (`yes`).
2. **Second annotator (reported by Mahdi, 2026-10-18):**
   - A teammate labelled the 990-answer hallucination sheet alone, without discussion, matching Mahdi 100%.
     That sheet was deleted, so this cannot be reported.
   - That teammate's genre labels matched the LLM draft exactly (the draft was visible), so they count as
     verification.
   - **Done 2026-10-26:** blind re-label by **Md Saminul Amin (annotator 2)**, kept as raw files in
     `data/labels/second_annotator/` (`src/audit/second_annotator_agreement.py`, results in `agreement.md`).
     - **Genre (200 questions):** human–human kappa **0.770** (0.696–0.835), 82.5% agreement. Mahdi's blind
       labels used the older guide v0.2. With the v1.0 rules applied to his labels, kappa is **0.796**
       (0.729–0.856).
     - Annotator 2 vs the LLM draft v0.2: kappa 0.829, against 0.806 for Mahdi.
     - Disagreements: Mahdi used "Other" 13 times, annotator 2 never did; the History/Geography boundary (9);
       Arts → History (5).
     - **Hallucination (200 answers, 40 questions):** 99.0% agreement, kappa **0.969** (0.906–1.000). Both
       disagreements are one question (Bhawal zamindar), where annotator 2 swapped the gold (শ্রীকৃষ্ণ) and the inference
       answer (মুর্শিদকুলী খান); the passage supports our labels.
     - Golden rule 7: genre is double-labelled on 200 of 920 questions (22%). Hallucination is double-labelled on
       200 of 4,600 answers (4.3%); reaching 20% would need about 720 more answers from annotator 2.
3. Optional: ask the BenHalluEval authors for the original GPT-5.4 answers.
4. Optional: test the hard-subset hypothesis (section 2).

## 6. Columns in `benhallueval_qa_seeds_v1.3.csv`

| Column | Meaning |
|---|---|
| `question_id` | TyDiQA id. All answers of one question share it; bootstraps re-sample this. |
| `context`, `question`, `correct_answer` | Final text (after fixes). |
| `genre`, `genre_fine` | Frozen v1.0 genre. `genre_fine` keeps "Sports" inside Arts, Culture & Sports. |
| `audit_status` | OK, TA, TU, WEAK, FIXQ, FIXA, FIXS, UPD or EXCL (see sections 2 and 3a) |
| `include_main` | yes / no (`check` was used until 2026-10-14). Main analysis uses `yes` only. |
| `time_sensitive`, `weak_gold` | Flags for the sensitivity analysis |
| `audit_note`, `genre_note` | Why the row was flagged or changed (for `UPD`: the old status and the 2026 fact) |
| `current_check` | For time-sensitive seeds: updated, still_correct, kept_vacant or kept_unverified |
| `answer_as_of`, `update_note`, `update_source` | Date of the web check, why it was kept, source links |
| `question_changed`, `answer_changed`, `context_changed` | yes/no |
| `question_original`, `correct_answer_original`, `context_original` | Original text, for traceability |
| `source_rows` | Row numbers in the original file (two rows mean a duplicate) |
| `genre_human_corrected` | yes if Mahdi changed Claude's draft genre |
| `human_review`, `human_note`, `followup_note` | Mahdi's review (approved, edited, dropped, flagged in blind sheet, not reviewed), his note, Claude's follow-up and its reason (v1.2) |
| `currency_note` | v1.3 currency / world-fact change and its reason (update, pin, world_fix, passage, drop) |
