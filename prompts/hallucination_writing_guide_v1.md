# Hallucinated-answer writing guide v1.0 (2026-10-13, frozen)

Used by Claude (claude-opus-5-5) to write the 4 hallucinated answers per BenHalluEval QA seed, because the
original 4,000 GPT-5.4 answers are not in the public download. One answer per type, so labels stay
single-label, as in BenHalluEval. The four types are BenHalluEval's QA types (taken from HaluEval).

The writer sees: the final question, the final gold answer, the passage (whole, or a window around the
gold when the passage is long) and, for updated seeds (`UPD`), the old gold.

## The four types

| Code | Type | What goes wrong | How people make this mistake |
|---|---|---|---|
| F | Factualness | A wrong fact of the same kind as the gold, usually from general knowledge, not from the passage. | Memory swap: the more famous or closely linked person, a nearby year, a round number, a neighbouring place. For `UPD` seeds, the old (outdated) fact is preferred. |
| C | Comprehension | The question is misread, so the answer fills a different slot. Usually copied from the passage; if the passage has no suitable span, the answer to a misread version of the question (e.g. "first" read as "current"). | Skim reading and keyword matching: the question says "built", the reader grabs the first year near the name. |
| S | Specificity | Wrong level of detail. Usually the gold plus a precise but false detail (exact date, place, title, number). Sometimes a broader or narrower thing that does not answer the question. | Overconfidence: adding a "precise" detail to sound sure, or naming the container instead of the thing. |
| I | Inference | The right kind of answer reached by a wrong reasoning step from passage facts. | Arithmetic or counting slip, first/last or before/after swap, part/whole or cause/effect swap, a fact given to the wrong entity, relation slip (father → grandfather), scale slip (লক্ষ ↔ কোটি). |

## Rules for every answer

1. **Wrong, both by the passage and in the real world**, as far as known. Never a synonym, spelling variant,
   transliteration or partial form of the gold that is still correct.
2. **Same form as the gold**: same script (Bangla digits if the gold uses them), similar length (S may be
   longer), same grammatical ending (gold "জিয়াউর রহমানের" → "শেখ মুজিবুর রহমানের"), same register.
   If the gold is a bare span, the answer is a bare span; no full sentence unless the gold is one.
3. **No tells**: no hedging ("সম্ভবত", "হয়তো"), no explanation, no reference to the passage, no English or
   Devanagari unless the gold has it.
4. **Plausible**: someone who knows a little about the topic could believe it. Nothing absurd.
5. **Distinct**: the 4 answers differ from each other and from the gold.
6. **C answers must not answer the question.** Check that the copied span is not also a valid answer.
7. **S answers** must not be correct at any level of detail. An added detail must be false, not just
   missing from the passage.
8. For number golds, do not make all four answers gold ± 1; vary the kind of error.

## Output format

One line per seed: `uidx|F|C|S|I` in `data/labels/hallucinations_claude/batch_NN.txt`. Lines starting
with `#` are comments. `|` never appears inside an answer.
