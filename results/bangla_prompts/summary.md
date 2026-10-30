# Side experiment: English vs Bangla prompts (exploratory; complete 2026-10-19)

**Question.** With English prompts, the Bangla fine-tuned judges gave no usable verdicts or judged weakly. Is the
prompt language the cause?

**Design.**
- The same notebook, models, versions and answers (BenHalluEval-QA v1.3, 4,600 answers). Only the three prompts
  are in Bangla (`genre_bn_v1`, `judge_bn_v1`, `judge_noctx_bn_v1`): translated by Claude, checked by Mahdi.
- Replies are হ্যাঁ / না and Bangla genre words. Strict parse, the same rules as the English runs.
- Decided after the English results, so this is exploratory. The reference model and the reading rule were
  recorded before the reference run.

**Results (BHS: lower is better; 50 = chance; ranges are paired over questions).**

| Model | Type | Without passage: EN → BN | With passage: EN → BN | Usable verdicts (BN) | Genre accuracy EN → BN |
|---|---|---|---|---|---|
| TigerLLM-9B | Bangla fine-tune of Gemma-3 | **44.8 → 40.0 (−4.8, clearly better)** | 38.8 → 37.4 (−1.5, not clear) | 100% | 76.8% → 75.8% |
| TituLLM-3B instruct | Bangla instruct (Llama-3.2) | no verdicts → 52.5 (49.5 on answered: chance) | no verdicts → 62.6 (50.1 on answered: chance) | 0% → 94% / 75% | 0% → 26% (picks the first option) |
| BanglaLLaMA-13B | Bangla LoRA on LLaMA-2 | no verdicts → no verdicts | no verdicts → no verdicts | 0% | 0% → 0% |
| TituLLM-3B base | Bangla continued pre-training | no verdicts → no verdicts | no verdicts → no verdicts | 0% | 0% → 0% |
| **llama3.1-8b (reference)** | multilingual, not Bangla-centric | **46.0 → 50.7 (+4.7, clearly worse)** | **36.7 → 66.5 (+29.8, reversed signal)** | 100% | **73.4% → 81.1% (better)** |

**Findings (exploratory).**
1. **Prompt language interacts with the model.** A Bangla prompt helps the Bangla fine-tune that can already judge
   (TigerLLM, without the passage). It badly hurts a multilingual judge of the same strength (llama): with the
   passage, llama's signal reverses.
2. **Format first, skill second.** A Bangla prompt can make a Bangla instruct model follow the answer format
   (TituLLM-instruct: 0% → 75–94% verdicts). It cannot give it judging skill (still chance), and it cannot fix
   models without instruction-following (BanglaLLaMA, TituLLM base).
3. **Genre guessing and judging react differently.** llama guesses genres better with the Bangla genre prompt but
   judges worse with the Bangla judge prompt.
4. Weak models show a strong **first-option bias** (ইতিহাস / HISTORY is listed first).

**Limits.**
- One translation of each prompt.
- Only two reference-quality comparisons (TigerLLM vs llama).
- Decided after the English results.
- llama ran on Ollama 0.40.5 in both languages; the others ran on 0.40.6.

**How to report.** A short section or appendix: "prompt language matters, and in opposite directions for
Bangla-centric and multilingual judges". The main study keeps the English prompts, as in BenHalluEval.
