# 119b results (run 21 Oct 2026 21:55-22:03 IST, pre-registered 21:55 IST in README.md)
Data: 1,809 FLORES-200 parallel sentences (dev + devtest rows 200-1011), none used in v1. 13 tokenizers loaded and none failed (`results/v2/load_status.json`).
Statistic: mean target-language tokens ÷ mean English tokens, with a paired bootstrap over sentences (10,000 draws, seed 1192).

| Tokenizer | Vocab | EN tok/sent | TE tok/sent | Telugu ÷ English [95% CI] | Hindi ÷ English |
|---|---:|---:|---:|---:|---:|
| Sarvam-1 | 68,096 | 30.3 | 35.1 | 1.16 [1.15, 1.17] | 1.15 |
| Gemma-3 | 262,145 | 26.2 | 46.7 | 1.78 [1.77, 1.80] | 1.31 |
| o200k_base (= gpt-oss, Phi-4-mini on Telugu) | 200,019 | 25.9 | 50.4 | 1.94 [1.93, 1.96] | 1.57 |
| Mistral-Nemo Tekken | 131,072 | 26.9 | 61.2 | 2.28 [2.26, 2.30] | 1.79 |
| Gemma-2 | 256,000 | 26.1 | 75.4 | 2.88 [2.86, 2.91] | 1.86 |
| DeepSeek-V3 | 128,815 | 26.1 | 98.6 | 3.78 [3.75, 3.81] | 2.81 |
| Granite-3.3 | 49,159 | 31.6 | 157.9 | 4.99 [4.94, 5.04] | 4.66 |
| Qwen3 | 151,669 | 26.7 | 187.6 | 7.04 [6.96, 7.11] | 4.44 |
| cl100k_base | 100,277 | 26.2 | 218.6 | 8.33 [8.25, 8.41] | 4.78 |
| Llama-3.2 (= SmolLM3 on Telugu) | 128,256 | 26.2 | 218.6 | 8.33 [8.25, 8.41] | 2.53 |

All seven Indic languages are in `results/v2/summary.md`. The figure is `figures/v2_tax_by_tokenizer.png`.

## Verdicts (pre-registered rules)
- **H1 (v1 split replicates): PROVEN, 6/6.** o200k and Gemma-3 stay below 2×, and cl100k, Qwen3, Gemma-2 and Llama-3.2 stay above, with every CI clear of 2.0. The v1 numbers moved by less than 0.15×.
- **H2 ("≥2× on most *distinct* tokenizers"): PROVEN, 7 of 10 distinct.** The dedupe rule (identical Telugu counts on all 1,809 sentences) merged gpt-oss and Phi-4-mini into o200k, and SmolLM3 into Llama-3.2. cl100k and Llama-3.2 differ on 9 of 1,809 Telugu sentences, so the rule kept them separate. *Sensitivity:* merging them too gives 6 of 9, which is still PROVEN. My prediction was "INCONCLUSIVE or narrowly PROVEN", so this came out stronger than I expected.
- The ratio isn't propped up by a big English denominator: Sarvam-1 also has the lowest *absolute* Telugu count (35 tokens/sentence vs 219 for cl100k/Llama).
- Vocab size alone doesn't explain it. Gemma-2 (256k) is at 2.88×, Sarvam-1 (68k, Indic-targeted) at 1.16×, and Granite (49k) at 4.99×. What matters is how much of the vocabulary was allocated to Indic scripts.

## Limitations
- FLORES is formal, Wikipedia-style text translated from English. There's no colloquial or code-mixed Telugu (Tenglish).
- Tokens are a proxy for cost and context use, not for quality.
- The CIs only cover sentence sampling, not the choice of tokenizers.
