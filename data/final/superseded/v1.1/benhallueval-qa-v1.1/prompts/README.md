# Prompts (frozen; never edit a version in place)

Placeholders are `{context}`, `{question}` and `{answer}`. They are filled in one pass (a regular
expression), so braces inside a passage cannot break a prompt. Each prompt is sent as a single user
message with the model's own chat template, with no system message, to every model (golden rule 6).
Temperature 0, seed 2026.

| File | Used for | Input | Output |
|---|---|---|---|
| `judge_v1.txt` | Turn 2: hallucination verdict | passage + question + answer | `yes` (hallucinated) or `no` |
| `genre_v1.txt` | Turn 1: genre guess | question + passage, **never the answer** (golden rule 1) | one of `HISTORY`, `ARTS`, `SCIENCE`, `GEOGRAPHY`, `RELIGION`, `OTHER` |
| `hallucination_writing_guide_v1.md` | Not a model prompt: the guide Claude used to write the hallucinated answers | | |

## judge_v1 (2026-10-14)

- The text is BenHalluEval's zero-shot judge prompt as printed in Table 14 of the paper (arXiv 2605.31483).
  It is in English. The paper says its QA prompts are in Bengali, but the Bengali text is not in the paper
  or the download.
- **Decide before the first judge result** whether to look for the Bengali text in the authors' repository.
  After the first judge result, the prompt never changes (a change would break comparisons across judges).
- The answer comes last, so the 5 answers of one question share the same prompt start. Ollama reuses the
  cached start, which makes runs faster without changing the result.

## genre_v1 (2026-10-14)

- A short version of the frozen genre guide v1.0 (`docs/genre-guide.md`): the 6 genres and the 8 rules for
  unsure cases. Every rule is kept. The Bangla example questions are left out because they come from
  the dataset itself, and showing them would give those questions away.
- One-word codes (not the long genre names) make the reply easy to parse for small models.
- The answer is never in this prompt. The notebook checks this before every run.

## Parsing (the same for every model)

- **Strict parse (official):** remove spaces, quotes, `*`, and `.,!:;` at both ends and ignore case. The
  result must then be exactly `yes`/`no` (judge) or one of the 6 codes (genre). The full genre name is also
  accepted. Anything else is `no_answer`. `no_answer` is counted and reported, and in BHS it counts as an
  error (the judge gave no usable verdict).
- **Lenient parse (diagnostic only):** the first `yes`/`no` word or genre code anywhere in the reply. It is
  used only to see whether a model fails on format rather than on judgment. It never feeds a result.
- **Reasoning models:** the thinking block is removed before parsing. A reply cut off by the output limit
  counts as `no_answer`.
