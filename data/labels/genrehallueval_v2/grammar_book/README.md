# Grammar book passages (GRAMMAR genre, GenreHalluEval v2)

**Source book:** বাংলা ভাষার ব্যাকরণ ও নির্মিতি, নবম-দশম শ্রেণি (Bangla grammar and composition, classes 9-10),
National Curriculum and Textbook Board (NCTB), Bangladesh; PDF of the 2021 school year edition. Mahdi's team gave the
PDF on 2026-10-28 as a more accurate source for grammar questions than Wikipedia.

- Raw copy (read-only): `data/raw/genrehallueval_v2/grammar_book/nctb_class9-10_bangla_bhashar_byakaran.pdf`
  (224 pages; sha256 `dec1ffad2ee43c21063c83449be26369572a42b2f0d274119bef3ebd4bbae610`).
- Page numbers: **book page N = PDF page N + 6.**

## How the passages were made

The PDF pages are scanned images with no text layer, and no OCR tool was available. On 2026-10-28 Claude
(claude-opus-5-5) rendered the needed pages with `pdftoppm` and transcribed the passages by reading the page images.
The transcription keeps the book's wording; some long lists of examples were shortened, and the passage keeps only the
sentences around the examples used by the questions. A passage is a source for its questions, not a full copy of a
page. A transcription error is possible; the annotators' blind check (`../check_v1/`) and `question_ok` column are the
check for that.

`book__candidates.csv` (sha256 `e203e2be735f719399d644b998cce69872b247c2921da8eda2acc3563dadf354`) holds the 37
passages, in the same columns as the Wikipedia candidate files, so `src/genrehallueval_v2/add_questions.py` reads them
like any download:

- `title` = passage id `NCTB-<book page>-<letter>`; the batch file refers to it as `book::NCTB-<page>-<letter>`;
- `url` = the citation (book, edition, book page, PDF page); `pageid`, `revid`, `timestamp` are empty;
- `mode` = `book`; `paragraphs` = a JSON list with the one passage text.

| Book page | Topic | Passages | Questions |
|---|---|---|---|
| 29 | উপসর্গ (prefixes) | 3 | 6 |
| 37-39 | সমাস (compounds) | 14 | 22 |
| 41-42 | সন্ধি (sandhi) | 10 | 34 |
| 51-52 | শব্দের শ্রেণিবিভাগ (word classes by source and structure; parts of speech) | 5 | 18 |
| 112 | বাগধারা (idioms) | 5 | 8 |

All 37 passages are used by the 88 GRAMMAR questions g2-871..g2-958 (`../new_questions/batch_14.txt`). Unlike the
other genres, one passage may serve several questions. The 12 grammar questions moved from CULTURE (g2-003, 013, 030,
031, 032, 034, 037, 149-153) keep their Wikipedia passages.

## Licence

NCTB textbooks are published free for students by the Government of Bangladesh. Before any public release, check
whether quoting these passages in a released dataset is allowed (add this to the BenHalluEval and Wikipedia licence
check that Mahdi asked to be reminded about).
