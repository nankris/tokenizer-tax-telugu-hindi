# Tokenizer Tax: Telugu & Hindi vs English

**Concept (one sentence).** Tokenization is the step where a language model chops raw text into
sub-word pieces before it ever sees it, so the *vocabulary* a model was trained with decides how
many pieces — and therefore how much of its context window and compute — a sentence consumes.

**Question.** For the *same meaning*, how many more tokens do Telugu and Hindi cost than English?

**Hypothesis.** Telugu costs >= 2x the English token count on most tokenizers (Hindi somewhere
between English and Telugu, since Devanagari is usually better represented than Telugu script).

## Setup

| Item | Choice |
|---|---|
| Data | FLORES-200 `devtest` (`facebookresearch/flores`, CC-BY-SA-4.0), first **200** sentences, English / Telugu / Hindi. Sentence-aligned, so "same meaning" is guaranteed by construction. |
| Extra row | First 200 Python snippets from HumanEval (164) + MBPP (36) — **non-parallel reference row**, ASCII-heavy, reported separately. |
| Tokenizers | `tiktoken` `o200k_base` (GPT-4o), `tiktoken` `cl100k_base` (GPT-4), Qwen3 (`Qwen/Qwen3-1.7B`), Gemma 3 (`unsloth/gemma-3-1b-it`), Gemma 2 (`unsloth/gemma-2-2b`), Llama 3.2 (`unsloth/Llama-3.2-1B`) |
| Byte baseline | Raw UTF-8 byte count (upper bound: 1 byte = 1 token, the practical ceiling for any byte-level BPE) |
| Hardware | CPU only, 2 vCPU, ~7 GB RAM, aarch64. **No GPU, 0 CU used.** Model *weights* are never loaded — only tokenizer files (a few MB each). |
| Statistic | Tokens per sentence; ratio vs English. **95% bootstrap CI**, 10 000 resamples of the 200 sentence indices (paired: same index used for all languages). |

Why pairing matters: because the three texts are translations of the *same* sentence, the
per-sentence ratio is a paired quantity. Bootstrapping over sentence indices (not pooling tokens)
keeps the CI honest about sentence-to-sentence variance.

## Fixed decision rule (set before seeing results)

Let **R_tel** = mean Telugu tokens / mean English tokens, per tokenizer, with its 95% CI.

- **PROVEN** — at least **4 of the 6** sub-word tokenizers have `CI_lower(R_tel) > 2.0`.
- **DISPROVEN** — at least **4 of the 6** have `CI_upper(R_tel) < 2.0`.
- **INCONCLUSIVE** — anything else.

**Headline number** = the median of R_tel across the 6 sub-word tokenizers (rounded to 1 dp).
Token counts for Hindi are reported the same way but are *not* part of the decision rule.

## Reproduce

```bash
source /workspace/tools/setup.sh
PY=/workspace/tools/mlenv/bin/python
$PY scripts/01_fetch_data.py      # downloads FLORES-200 + code set -> data/
$PY scripts/02_count_tokens.py    # resumable; -> results/token_counts.csv
$PY scripts/03_analyze.py         # bootstrap CIs -> results/*.json + chart.png
```

## Outputs

- `results/token_counts.csv` — per-sentence token counts, every tokenizer x language
- `results/summary.json` — means, ratios, 95% CIs, verdict
- `writeup.md` — results table + the one headline number
- `chart.png` — tokens per sentence by language, per tokenizer

## Environment actually used

- CPU only (aarch64, 2 vCPU). **No Colab session was created → 0 CU consumed.**
- Model *weights* were never downloaded — only tokenizer files (few MB each), so every
  tokenizer is exactly the vocabulary its real model uses.
- Versions: `torch 2.14.1+cpu`, `transformers 5.19.0`, `datasets 5.1.0`, `tiktoken 0.14.0`.

## 119b strengthening: pre-registered 21 Oct 2026 21:55 IST, before any 119b count
**Why.** The 21 Oct review found three weaknesses in v1. (1) "PROVEN 4/6" counts one tokenizer twice: Llama-3.2 and cl100k give identical Telugu counts. (2) The 4.9× headline is the median of a bimodal set ({1.75, 1.90, 2.83} vs {6.9, 8.2, 8.2}), so it describes no real tokenizer. (3) There are only 200 sentences, from one source, and no newer or Indic-focused tokenizers.
**Design.**
- Fresh text: FLORES-200 **dev** (997 sentences) plus **devtest rows 200-1011** (812). That is 1,809 parallel sentences, none of them used in v1. Languages: eng, tel, hin (primary). tam, kan, mal, ben, mar are descriptive extras.
- Tokenizers: the v1 six plus every newer one I can load without a token. Candidates: Mistral Tekken (Mistral-Nemo), DeepSeek-V3, gpt-oss (o200k_harmony), Phi-4-mini, Sarvam-1 (Indic-focused), SmolLM3, and IBM Granite-3.3. **Deduplication rule:** two tokenizers whose Telugu token counts are identical on all 1,809 sentences count as one "distinct tokenizer" for the vote (the first-listed name is kept). The one that loaded is recorded, and the ones that failed are listed.
- Statistic: R_tel = mean Telugu tokens / mean English tokens per tokenizer, with a paired bootstrap over sentences (10,000 draws, seed 1192).
- **H1 (replication of the split):** each v1 tokenizer stays on the same side of 2.0, with its 95% CI excluding 2.0. o200k and Gemma-3 stay below 2.0. cl100k, Qwen3, Gemma-2 and Llama-3.2 stay above. PROVEN if 6/6 hold; DISPROVEN if 2 or more flip side; INCONCLUSIVE otherwise.
- **H2 (the original claim, fixed):** "Telugu costs ≥ 2× English on most *distinct* tokenizers." PROVEN if more than half of the distinct tokenizers have CI_low > 2.0. DISPROVEN if more than half have CI_high < 2.0. INCONCLUSIVE otherwise.
- Prediction, written now: H1 PROVEN. H2 INCONCLUSIVE or narrowly PROVEN. Indic-focused (Sarvam) and ≥200k-vocab tokenizers (o200k, Gemma-3) come in under 2×, and legacy 100-150k vocabularies come in over 5×.
- Headline will be the **range and the two clusters**, not the median.
- Outputs go in `results/v2/`. The v1 files are untouched.
