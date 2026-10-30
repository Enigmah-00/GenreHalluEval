# Dataset 2 labels

- `genre_3annotators_raw_2026-10-27.csv`: the team's sheet exactly as received on 2026-10-27 (250 questions; genre
  columns "Genre(Annotator 1/2/3)" and "Majority vote"). Raw sheet: never edit, never delete. The same file is in
  `data/raw/dataset2/` as the source of the passages and questions.
- `genre_agreement.md`: agreement of the three genre annotators on that sheet (made by `src/dataset2/build_seeds.py`).
- `overlap_replacements_v1.csv`: the 17 rows Claude changed to remove BenHalluEval overlap (2026-10-27), with the
  reason, the BenHalluEval evidence, the new question and gold, and (for 12 rows) the new Bangla Wikipedia passage
  with its title and revision id. The annotators should check these 17 questions and label their genre again.
- `overlap_check_seeds_v1.0.md`: the overlap check on the final seeds. The 6 rows left are false alarms (read by
  hand): different facts that share a generic word such as "কততম", "দেশের" or "অনুষ্ঠিত".

Hallucination labels: see "Added 2026-10-27 (labels)" below. The world label was dropped (decided 2026-10-27).

## Added 2026-10-27

- `hallucinations_claude/batch_01..10.txt`: the 1,000 hallucinated answers (question_id|F|C|S|I), written by Claude
  (claude-opus-5-5) under `prompts/hallucination_writing_guide_v1.md`.
- `blank_sheets/`: the labelling sheets, one copy per annotator, shuffled, with no answer type or design label:
  `passage_labels_annotator{1,2}_BLANK.csv` (all 1,250 answers, with the passage) and
  `world_labels_annotator{1,2}_BLANK.csv` (the 375 answers judged without the passage; no passage shown), plus
  `genre_relabel_17_BLANK.csv` for the three genre annotators. Fill a copy alone, save it as `..._filled_raw.csv`
  next to it, and never edit it after discussion.

## Added 2026-10-27 (labels)

Raw passage-label sheets, exactly as received (read-only; never edit). Labels are `c` (correct) and `h`
(hallucinated). Annotator 1 = Umme Zoayria Abedin, annotator 2 = Md Saminul Amin, each alone. Mahdi Hasan Qurishi has
not seen the labels.
- `passage_labels_annotator1_filled_raw_2026-10-27.csv` (annotator 1). The file was sorted after filling, so its header
  row sits in the middle; `src/dataset2/label_agreement.py` handles that. It has 10 text edits and 5 notes ("update the
  passage in main dataset"); they went into `text_fixes_v1.1.csv`.
- `passage_labels_annotator2_filled_raw_2026-10-27.csv` (annotator 2, own sheet).
- `passage_labels_annotator2_copy_on_annotator1_sheet_2026-10-27.csv`: annotator 2 also filled a copy of annotator 1's
  sheet by mistake (it carries annotator 1's text edits and notes, with annotator 2's labels). Same labels as annotator
  2's own sheet in all 1,250 rows. Kept for the record; not used for kappa. Annotator 1's labels were not in this copy
  when annotator 2 filled it (Mahdi Hasan Qurishi, 2026-10-27), so annotator 2 stayed blind to them.
- `passage_label_agreement.md` (by `src/dataset2/label_agreement.py`): kappa 0.990 (1,246 of 1,250 agree; 0.993 with
  the passage, 0.983 without). Annotator 1 matches the design label everywhere; annotator 2 differs on 4 answers.
- `passage_label_resolutions_v1.csv`: the 4 disagreements (d2-068 p2/p4, d2-201 p3/p5; annotator 2 marked the gold
  hallucinated and one hallucination correct, although the passage states the gold). Fill `final_label` (0 / 1 /
  exclude) and `decided_by` after the discussion, then rerun the script; it then writes
  `passage_labels_agreed_v1.csv`, the input of `compare_routes.py --labels`.
  Resolved 2026-10-27: annotator 2 withdrew all 4 labels (the answers looked close to the correct one and the
  difference was missed); the final label is annotator 1's, which the passage supports.
- `passage_labels_agreed_v1.csv`: the final labels (1,246 agreed + 4 resolved; 250 correct, 1,000 hallucinated; none
  unclear). The final label differs from the design label for 0 answers.
- `text_fixes_v1.1.csv`: the 18 text fixes of GenreHalluEval v1.1 (question_id, field, old, new, made_by, reason):
  16 passages that did not state the gold answer clearly (15 Islamic Religion passages and d2-012), the year in
  d2-142's question, and d2-110's C answer. Applied by `src/dataset2/build_package.py`.
