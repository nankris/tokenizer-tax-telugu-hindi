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
