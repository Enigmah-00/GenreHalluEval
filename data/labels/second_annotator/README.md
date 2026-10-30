# Second annotator (Md Saminul Amin): blind re-labelling (2026-10-18)

Two sheets, to be filled **alone**: do not look at any other sheet, any draft genre, any label, or the first
annotator's answers, and do not discuss items before finishing. **Keep the filled files; never delete them.**
They are the only evidence for the human–human agreement (Cohen's kappa) reported in the paper.

1. `genre_blind200_for_annotator2.csv` (200 questions, about 1.5 h): write one genre in `your_genre` using the
   frozen guide `docs/genre-guide.md` (v1.0): History, Politics & Education / Arts, Culture & Sports /
   Science & Technology / Geography & Places / Religion / Other.
2. `halluc_blind200_for_annotator2.csv` (200 answers from 40 questions, about 1.5 h): for each answer write
   `yes` if it is hallucinated (not supported by the passage, contradicts it, or does not answer the question) and
   `no` if it is correct. Use `note` for anything unclear.

Name the filled files `..._filled_<initials>.csv` and put them back in this folder.

## Results (2026-10-26)

- **Filled sheets, unchanged:** `genre_blind200_filled_annotator2_raw.csv` and
  `halluc_blind200_filled_annotator2_raw.csv`. The hallucination sheet came back sorted by row number as text; the
  items and text are identical.
- **Genre:** human–human kappa 0.770, or 0.796 against Mahdi's labels with the v1.0 rules applied.
- **Hallucination:** kappa 0.969 (99.0%).
- Details: `agreement.md` and `agreement.json`.
