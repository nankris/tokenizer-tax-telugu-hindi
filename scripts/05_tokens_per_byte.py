#!/usr/bin/env python
"""Normalise token counts by UTF-8 bytes -> removes the 'Telugu text is just longer' confound."""
import os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
df = pd.read_csv(os.path.join(RES, "token_counts.csv"))
piv = df.pivot_table(index="sent_idx", columns=["tokenizer", "lang"], values="n_tokens")
rows = []
for t in [x for x in dict.fromkeys(df["tokenizer"]) if x != "bytes_utf8"]:
    r = {"tokenizer": t}
    for lg in ["eng", "tel", "hin"]:
        r[f"{lg}_tok_per_byte"] = round(piv[(t, lg)].mean() / piv[("bytes_utf8", lg)].mean(), 3)
    rows.append(r)
out = pd.DataFrame(rows)
out.to_csv(os.path.join(RES, "tokens_per_byte.csv"), index=False)
print(out.to_string(index=False))
