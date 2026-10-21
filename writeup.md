# The tokenizer tax: Telugu and Hindi cost more tokens than English

**Experiment 119 — concept: Tokenization.**
Data: FLORES-200 `devtest`, first 200 sentence-aligned English/Telugu/Hindi triples
(`facebookresearch/flores`, CC-BY-SA-4.0). CPU only, 0 CU.

## Results

Tokens per sentence (mean of 200), and ratio vs English with 95% paired bootstrap CI
(10,000 resamples, seed 12345):

| Tokenizer | English | Telugu | Telugu ratio vs EN (95% CI) | Hindi | Hindi ratio vs EN (95% CI) |
|---|---|---|---|---|---|
| `o200k_base` (GPT-4o) | 27.4 | 52.0 | **1.90x** (1.86–1.95) | 43.3 | 1.58x (1.55–1.62) |
| `cl100k_base` (GPT-4) | 27.6 | 226.7 | **8.22x** (7.99–8.45) | 130.4 | 4.72x (4.61–4.84) |
| Qwen3-1.7B | 28.3 | 195.0 | **6.90x** (6.68–7.11) | 123.0 | 4.35x (4.23–4.47) |
| Gemma-3-1B | 28.0 | 48.8 | **1.75x** (1.70–1.79) | 36.8 | 1.31x (1.29–1.34) |
| Gemma-2-2B | 27.8 | 78.8 | **2.83x** (2.76–2.91) | 52.6 | 1.89x (1.85–1.93) |
| Llama-3.2-1B | 27.6 | 226.7 | **8.22x** (7.99–8.45) | 70.0 | 2.54x (2.48–2.60) |
| byte-level (raw UTF-8) | 133.9 | 357.1 | 2.67x (2.61–2.72) | 340.3 | 2.54x (2.50–2.59) |

Reference row — 200 Python snippets (HumanEval + MBPP). These are **not** translations of the
FLORES English sentences, so this is a context anchor, not a ratio: code costs ~166 tokens per
snippet on every tokenizer, i.e. ~6x the FLORES English sentence — but snippets are also
~4.3x longer in bytes (570 vs 134), so per byte code is only ~1.4x English prose. The point of
the row is simply that English *prose* is what these vocabularies were built for, and Telugu
prose is priced above even code.

Tokens per **byte** (removes the fact that Telugu/Hindi text is simply longer in characters):

| Tokenizer | English | Telugu | Hindi |
|---|---|---|---|
| `o200k_base` | 0.204 | 0.146 | 0.127 |
| `cl100k_base` | 0.206 | 0.635 | 0.383 |
| Qwen3-1.7B | 0.211 | 0.546 | 0.361 |
| Gemma-3-1B | 0.209 | 0.137 | 0.108 |
| Gemma-2-2B | 0.208 | 0.221 | 0.154 |
| Llama-3.2-1B | 0.206 | 0.635 | 0.206 |

English is ~0.21 tokens/byte on every tokenizer (as expected, close to the ~0.25 ceiling of
byte-level BPE on Latin text). Telugu ranges from 0.14 (Gemma 3) to 0.64 (cl100k/Llama),
i.e. **3x worse than English per byte** on the older vocabularies.

## Verdict: PROVEN (exactly at the threshold)

Decision rule fixed in README before results: PROVEN if ≥4 of 6 sub-word tokenizers have
`CI_lower(Telugu ratio) > 2.0`. Result: **4 of 6** (`cl100k_base`, Qwen3, Gemma-2, Llama-3.2)
clear 2x with CIs well above it; `o200k_base` (1.90x) and Gemma-3 (1.75x) do not.

Honest caveat: this is *just* at the threshold. The two tokenizers that fail are the **newest**
ones, and that is the real finding — the tax is not a law of nature, it is a property of the
vocabulary. OpenAI's `o200k_base` and Gemma 3 clearly added Indic coverage; `cl100k_base` and
Llama-3.2 essentially did not.

## Headline number for the post

> **The same sentence costs 4.9x more tokens in Telugu.**

(Median Telugu/English ratio across the six sub-word tokenizers; the spread is the story —
1.75x on Gemma 3 to 8.2x on `cl100k_base` and Llama-3.2.)

## Takeaway (2 sentences)

The same meaning that costs an English speaker ~28 tokens can cost a Telugu speaker anywhere
from 49 to 227 tokens, depending purely on which tokenizer the model ships with — and a Hindi
speaker 37 to 130. That is not an even playing field: on the older vocabularies a Telugu user
burns an 8x larger slice of a fixed context window, pays 8x the compute, and hits truncation
8x sooner for identical content — so tokenizer coverage is not a cosmetic detail, it is a
built-in tax on half a billion speakers.
