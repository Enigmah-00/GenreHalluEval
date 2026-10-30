# GenreHalluEval v2 blind check v1

Blank sheets and the key were made once by `src/genrehallueval_v2/make_check_sheets.py` (seed 2026; see
`sample_summary.md`). The key files (`KEY_do_not_share__*.csv`) were never given to the annotators.
Annotator 1 = Umme Zoayria Abedin, annotator 2 = Md Saminul Amin; both worked alone on identical sheets.

## Returned sheets (raw, read-only; never edit)

| Folder | What | sha256 (first 8) |
|---|---|---|
| `returned_raw_2026-10-29/` | first return of all four sheets. Annotator 1's answer sheet was incomplete (rows 601-970 blank). | a1 answers 3210e45d, a1 genre 3dee13f5, a2 answers f8d27a19, a2 genre 96be7e30 |
| `returned_raw_2026-10-29_v2/` | annotator 1's completed answer sheet (rows 1-600 unchanged from the first return) plus byte-identical copies of the other three files, so one folder holds the full set used for scoring. | a1 answers d3746351, others as above |

The files came back as Google Sheets CSV exports (no BOM; the passage column moved before the question column).
`check_agreement.py` reads columns by name and checks every row id and every question, passage and answer text against
the blank sheets. One cell was edited: annotator 2 changed answer A0573 (g2-791, I) from 'আল্লাহ রাখা খান' to
'আল্লাহ রাখা রহমান' and labelled it correct; that label is left out (969 of 970 answers scored for annotator 2).

## Results

`agreement_v1.md` (made by `python3 -I src/genrehallueval_v2/check_agreement.py . <folder> v1` on the `_v2` folder) and
`disagreements_v1.csv` (every row where the annotators, or an annotator and the design, differ).

## Decisions (Mahdi, 2026-10-29)

- Genre: keep Claude's draft genre for every question, including the 4 where both annotators chose another genre
  (g2-487, g2-677, g2-420, d2-194) and the 2 split cases (g2-052, g2-648). Report the draft-vs-annotator kappas.
- Answers: the design labels stand. In all three rows where annotator 2 differs (A0549, A0550, A0571), annotator 1
  agrees with the design and the passage supports it.
