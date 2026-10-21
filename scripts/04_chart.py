#!/usr/bin/env python
"""Two-panel chart: raw tokens/sentence, and the ratio vs English with 95% CIs."""
import json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
df = pd.read_csv(os.path.join(RES, "token_counts.csv"))
S = json.load(open(os.path.join(RES, "summary.json")))
piv = df.pivot_table(index="sent_idx", columns=["tokenizer", "lang"], values="n_tokens")

order = [t for t in dict.fromkeys(df["tokenizer"]) if t != "bytes_utf8"] + ["bytes_utf8"]
cols = {"eng": "#4C72B0", "tel": "#C44E52", "hin": "#DD8452"}
lbl = {"eng": "English", "tel": "Telugu", "hin": "Hindi"}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.6))

# --- panel 1: tokens per sentence ---
x = np.arange(len(order)); w = 0.26
for j, lg in enumerate(["eng", "tel", "hin"]):
    vals = [piv[(t, lg)].mean() for t in order]
    b = ax1.bar(x + (j - 1) * w, vals, w, label=lbl[lg], color=cols[lg])
    ax1.bar_label(b, fmt="%.0f", fontsize=7, padding=1)
ax1.set_xticks(x); ax1.set_xticklabels(order, rotation=22, ha="right")
ax1.set_ylabel("Tokens per sentence"); ax1.legend(title="Language")
ax1.grid(axis="y", alpha=0.3)
ax1.set_title("Same meaning, different token cost\n(200 FLORES-200 sentences, mean)")

# --- panel 2: ratio vs English with CI ---
sw = [t for t in order if t != "bytes_utf8"]
xr = np.arange(len(order))
for j, lg in enumerate(["tel", "hin"]):
    ps  = [S["tokenizers"][t][lg]["ratio"] for t in order]
    los = [S["tokenizers"][t][lg]["ci_low"] for t in order]
    his = [S["tokenizers"][t][lg]["ci_high"] for t in order]
    off = -0.19 if j == 0 else 0.19
    ax2.bar(xr + off, ps, 0.36, label=lbl[lg], color=cols[lg],
            yerr=[np.array(ps) - np.array(los), np.array(his) - np.array(ps)],
            capsize=3, error_kw=dict(lw=1, ecolor="black", alpha=0.75))
    for xi, p in zip(xr + off, ps):
        ax2.text(xi, p + 0.12, f"{p:.2f}x", ha="center", fontsize=7.5)
ax2.axhline(2.0, ls="--", lw=1.6, color="black")
ax2.text(len(order) - 0.5, 2.08, "2x hypothesis threshold", ha="right", fontsize=8.5)
ax2.set_xticks(xr); ax2.set_xticklabels(order, rotation=22, ha="right")
ax2.set_ylabel("Token ratio vs English  (95% CI)")
ax2.legend(title="Language"); ax2.grid(axis="y", alpha=0.3)
hl = S["headline_median_ratio_tel"]
ax2.set_title(f"VERDICT: {S['verdict']} — Telelu median {hl:.1f}x, "
              f"{S['n_tokenizers_ci_above_2x_tel']}/6 CIs above 2x".replace("Telelu", "Telugu"))

fig.suptitle(f'The tokenizer tax: the same sentence costs {hl:.1f}x more tokens in Telugu',
             fontsize=14, fontweight="bold", y=1.02)
fig.tight_layout()
out = os.path.join(ROOT, "chart.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
print("chart ->", out)
