# Prompts (frozen; never edit a version in place)

Placeholders are `{context}`, `{question}` and `{answer}`. They are filled in one pass (a regular
expression), so braces inside a passage cannot break a prompt. Each prompt is sent as a single user
message with the model's own chat template, with no system message, to every model (golden rule 6).
Temperature 0, seed 2026.

| File | Used for | Input | Output |
|---|---|---|---|
| `judge_v1.txt` | Turn 2: hallucination verdict | passage + question + answer | `yes` (hallucinated) or `no` |
| `judge_noctx_v1.txt` | Turn 2, no-context condition: hallucination verdict without the passage | question + answer | `yes` (hallucinated) or `no` |
| `genre_v1.txt` | Turn 1: genre guess | question + passage, **never the answer** (golden rule 1) | one of `HISTORY`, `ARTS`, `SCIENCE`, `GEOGRAPHY`, `RELIGION`, `OTHER` |
| `genre_bn_v1.txt`, `judge_bn_v1.txt`, `judge_noctx_bn_v1.txt` | **Side experiment only:** the same three prompts in Bangla (`notebooks/benchmark_bangla_prompts.ipynb`) | as above | হ্যাঁ / না; ইতিহাস, শিল্পকলা, বিজ্ঞান, ভূগোল, ধর্ম, অন্যান্য |
| `hallucination_writing_guide_v1.md` | Not a model prompt: the guide Claude used to write the hallucinated answers | | |

## judge_v1 (2026-10-14)

- The text is BenHalluEval's zero-shot judge prompt as printed in Table 14 of the paper (arXiv 2605.31483).
  It is in English. The paper says its QA prompts are in Bengali, but the Bengali text is not in the paper
  or the download.
- **Decide before the first judge result** whether to look for the Bengali text in the authors' repository.
  After the first judge result, the prompt never changes (a change would break comparisons across judges).
- The answer comes last, so the 5 answers of one question share the same prompt start. Ollama reuses the
  cached start, which makes runs faster without changing the result.

## judge_noctx_v1 (2026-10-17)

- The second main condition (decided by Mahdi on 2026-10-17): the judge sees **only the question and the
  answer** and must rely on its own knowledge. It is the same as `judge_v1` with the passage line removed,
  and the definition of "yes" changed from "not supported by the context" to "false, or does not answer the
  question correctly". Everything else (format, reply, settings) is the same, so the two conditions differ
  only in the passage.
- Labels do not change: the gold is correct and the 4 hallucinated answers are wrong. This holds without the
  passage too, because every hallucinated answer was written to be wrong in the real world, and v1.3 checked
  every gold against today's world. Caveat: facts updated to 2026 (34 time-sensitive seeds and the `UPD`
  seeds) may be newer than a judge's training data. The notebook also reports BHS without them.

## Bangla prompts: genre_bn_v1, judge_bn_v1, judge_noctx_bn_v1 (2026-10-18)

- **What they are:** translations of the three English prompts, made by Claude and **to be checked by Mahdi (a
  native speaker) before any run**. The meaning, the placeholders and the order are unchanged. The judge prompts
  ask for "হ্যাঁ অথবা না" and "উত্তর শুধু বাংলায় দিন" (answer only in Bangla).
- **Genre codes:** ইতিহাস, শিল্পকলা, বিজ্ঞান, ভূগোল, ধর্ম, অন্যান্য. শিল্পকলা is used, not শিল্প, because শিল্প also
  means "industry".
- **Why:** with English prompts, the three Bangla fine-tunes gave no usable verdicts (R4, R9, R10). This side
  experiment asks whether the prompt language is the cause. It was decided after the English results, so it is
  exploratory and never feeds the main analysis.
- **Parsing (fixed before any Bangla-prompt result):**
  - Strict: the whole reply, after edge punctuation (including "।") and an optional "উত্তর:" / "ধরন:" label, must be
    হ্যাঁ/হ্যা/না or yes/no for the judge, or one Bangla genre word or English code for the genre.
  - Lenient (diagnostic only): the first such word anywhere in the reply.
  - Up to 16 new tokens per reply, against 8 in the English notebook, because Bangla words take more tokens.

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
