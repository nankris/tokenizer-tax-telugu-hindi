#!/usr/bin/env python
"""Bootstrap CIs + verdict + chart.

Decision rule (fixed in README before results):
  R_tel = mean(tel tokens)/mean(eng tokens) per tokenizer, 95% paired bootstrap CI.
  PROVEN      : >= 4 of 6 sub-word tokenizers have CI_lower(R_tel) > 2.0
  DISPROVEN   : >= 4 of 6 have CI_upper(R_tel) < 2.0
  INCONCLUSIVE: otherwise
  Headline    = median R_tel across the 6 sub-word tokenizers.
"""
import json, os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
CSV = os.path.join(RES, "token_counts.csv")
N_BOOT = 10000
SEED = 12345
RW = 2.0  # 2x threshold

df = pd.read_csv(CSV)
piv = df.pivot_table(index="sent_idx", columns=["tokenizer", "lang"], values="n_tokens")
tokenizers = list(dict.fromkeys(df["tokenizer"]))
sub_word = [t for t in tokenizers if t != "bytes_utf8"]

rng = np.random.default_rng(SEED)
n = piv.shape[0]
idx = rng.integers(0, n, size=(N_BOOT, n))


def ratio_ci(tok, lang):
    en = piv[(tok, "eng")].to_numpy(float)
    xx = piv[(tok, lang)].to_numpy(float)
    point = xx.mean() / en.mean()
    be = en[idx].mean(axis=1)
    bx = xx[idx].mean(axis=1)
    boots = bx / be
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return point, lo, hi, boots


summary = {"n_sentences": int(n), "n_bootstrap": N_BOOT, "seed": SEED,
           "threshold": RW, "tokenizers": {}}
for tok in tokenizers:
    entry = {}
    for lang in ["tel", "hin"]:
        p, lo, hi, _ = ratio_ci(tok, lang)
        entry[lang] = {"ratio": float(p), "ci_low": float(lo), "ci_high": float(hi),
                       "tokens_per_sentence": float(piv[(tok, lang)].mean()),
                       "eng_tokens_per_sentence": float(piv[(tok, "eng")].mean())}
    if "code" in piv.columns.get_level_values(1):
        p, lo, hi, _ = ratio_ci(tok, "code")
        entry["code"] = {"ratio": float(p), "ci_low": float(lo), "ci_high": float(hi),
                         "tokens_per_sentence": float(piv[(tok, "code")].mean())}
    summary["tokenizers"][tok] = entry

# verdict on Telugu
above = [t for t in sub_word if summary["tokenizers"][t]["tel"]["ci_low"] > RW]
below = [t for t in sub_word if summary["tokenizers"][t]["tel"]["ci_high"] < RW]
if len(above) >= 4:
    verdict = "PROVEN"
elif len(below) >= 4:
    verdict = "DISPROVEN"
else:
    verdict = "INCONCLUSIVE"

r_tel = [summary["tokenizers"][t]["tel"]["ratio"] for t in sub_word]
headline = float(np.median(r_tel))
summary["verdict"] = verdict
summary["n_tokenizers_ci_above_2x_tel"] = len(above)
summary["n_tokenizers_ci_below_2x_tel"] = len(below)
summary["headline_median_ratio_tel"] = headline
summary["headline_median_ratio_hin"] = float(np.median(
    [summary["tokenizers"][t]["hin"]["ratio"] for t in sub_word]))

with open(os.path.join(RES, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

# flat CSV summary for the writeup
rows = []
for tok in tokenizers:
    r = {"tokenizer": tok,
         "eng_tok_per_sent": summary["tokenizers"][tok]["tel"]["eng_tokens_per_sentence"],
         "tel_tok_per_sent": summary["tokenizers"][tok]["tel"]["tokens_per_sentence"],
         "tel_ratio": summary["tokenizers"][tok]["tel"]["ratio"],
         "tel_ci_low": summary["tokenizers"][tok]["tel"]["ci_low"],
         "tel_ci_high": summary["tokenizers"][tok]["tel"]["ci_high"],
         "hin_tok_per_sent": summary["tokenizers"][tok]["hin"]["tokens_per_sentence"],
         "hin_ratio": summary["tokenizers"][tok]["hin"]["ratio"],
         "hin_ci_low": summary["tokenizers"][tok]["hin"]["ci_low"],
         "hin_ci_high": summary["tokenizers"][tok]["hin"]["ci_high"]}
    if "code" in summary["tokenizers"][tok]:
        c = summary["tokenizers"][tok]["code"]
        r.update({"code_tok_per_sent": c["tokens_per_sentence"], "code_ratio": c["ratio"]})
    rows.append(r)
pd.DataFrame(rows).to_csv(os.path.join(RES, "summary.csv"), index=False)

print(json.dumps({k: v for k, v in summary.items() if k != "tokenizers"}, indent=2))
print(pd.DataFrame(rows).to_string(index=False))

# ---------------- chart ----------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

order = [t for t in tokenizers if t != "bytes_utf8"] + ["bytes_utf8"]
langs = ["eng", "tel", "hin"]
lbl = {"eng": "English", "tel": "Telugu", "hin": "Hindi"}
cols = {"eng": "#4C72B0", "tel": "#C44E52", "hin": "#DD8452"}
x = np.arange(len(order))
w = 0.26
fig, ax = plt.subplots(figsize=(11, 5.4))
for j, lg in enumerate(langs):
    vals = [piv[(t, lg)].mean() if lg in piv[t].columns.get_level_values(0) else 0 for t in order]
    ax.bar(x + (j - 1) * w, vals, w, label=lbl[lg], color=cols[lg])
ax.set_xticks(x)
ax.set_xticklabels(order, rotation=20, ha="right")
ax.set_ylabel("Tokens per sentence (mean of 200 FLORES sentences)")
rng_txt = f"Telugu costs {headline:.1f}x the English token count (median across tokenizers)"
ax.set_title("Tokenizer tax: same meaning, more tokens\n" + rng_txt)
ax.legend(title="Language")
ax.grid(axis="y", alpha=0.3)
for j, lg in enumerate(langs):
    for i, t in enumerate(order):
        v = piv[(t, lg)].mean() if lg in piv[t].columns.get_level_values(0) else 0
        ax.text(i + (j - 1) * w, v, f"{v:.0f}", ha="center", va="bottom", fontsize=7)
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "chart.png"), dpi=150)
print("chart ->", os.path.join(ROOT, "chart.png"))
