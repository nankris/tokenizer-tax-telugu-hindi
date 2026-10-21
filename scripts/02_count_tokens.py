#!/usr/bin/env python
"""Count tokens per sentence for every tokenizer x language.

Resumable: results/token_counts.csv is appended per (tokenizer, lang) group and
existing groups are skipped on re-run. Only tokenizer files are downloaded --
no model weights. CPU only.
"""
import csv, json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RES = os.path.join(ROOT, "results")
CSV_PATH = os.path.join(RES, "token_counts.csv")
FIELDS = ["tokenizer", "family", "lang", "sent_idx", "n_tokens"]

LANGS = ["eng", "tel", "hin", "code"]

# name -> (kind, spec)
TOKENIZERS = [
    ("o200k_base",  "tiktoken", "o200k_base"),
    ("cl100k_base", "tiktoken", "cl100k_base"),
    ("Qwen3-1.7B",  "hf", "Qwen/Qwen3-1.7B"),
    ("Gemma-3-1B",  "hf", "unsloth/gemma-3-1b-it"),
    ("Gemma-2-2B",  "hf", "unsloth/gemma-2-2b"),
    ("Llama-3.2-1B","hf", "unsloth/Llama-3.2-1B"),
]


def load_sentences():
    with open(os.path.join(DATA, "sentences.json"), encoding="utf-8") as f:
        d = json.load(f)
    fl = d["flores"]
    out = {"eng": fl["eng_Latn"], "tel": fl["tel_Telu"], "hin": fl["hin_Deva"]}
    if d.get("code"):
        out["code"] = d["code"]
    return out


def done_groups():
    if not os.path.exists(CSV_PATH):
        return set()
    with open(CSV_PATH, encoding="utf-8") as f:
        return {(r["tokenizer"], r["lang"]) for r in csv.DictReader(f)}


def append_rows(rows):
    new = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)
        f.flush()
        os.fsync(f.fileno())


def count_tiktoken(enc_name, text):
    import tiktoken
    enc = tiktoken.get_encoding(enc_name)
    return len(enc.encode(text))


def main():
    os.makedirs(RES, exist_ok=True)
    sents = load_sentences()
    done = done_groups()
    print("already done:", sorted(done))
    hf_cache = {}
    for name, kind, spec in TOKENIZERS:
        todo = [lg for lg in LANGS if lg in sents and (name, lg) not in done]
        if not todo:
            print(f"[skip] {name}: all groups present")
            continue
        t0 = time.time()
        if kind == "tiktoken":
            counter = lambda t, s=spec: count_tiktoken(s, t)
        else:
            from transformers import AutoTokenizer
            if spec not in hf_cache:
                print(f"[load] tokenizer {spec}")
                hf_cache[spec] = AutoTokenizer.from_pretrained(spec)
            tok = hf_cache[spec]
            counter = lambda t, k=tok: len(k.encode(t, add_special_tokens=False))
        for lg in todo:
            rows = []
            for i, s in enumerate(sents[lg]):
                n = counter(s)
                rows.append({"tokenizer": name, "family": kind, "lang": lg,
                             "sent_idx": i, "n_tokens": n})
            append_rows(rows)
            print(f"[ok  ] {name}/{lg}: n={len(rows)} mean={sum(r['n_tokens'] for r in rows)/len(rows):.1f}")
        print(f"[time] {name}: {time.time()-t0:.1f}s")

    # byte-level baseline (worst case: 1 byte == 1 token)
    todo = [lg for lg in LANGS if lg in sents and ("bytes_utf8", lg) not in done]
    if todo:
        for lg in todo:
            rows = [{"tokenizer": "bytes_utf8", "family": "bytes", "lang": lg,
                     "sent_idx": i, "n_tokens": len(s.encode("utf-8"))}
                    for i, s in enumerate(sents[lg])]
            append_rows(rows)
            print(f"[ok  ] bytes_utf8/{lg}: mean={sum(r['n_tokens'] for r in rows)/len(rows):.1f}")
    print("[done] ->", CSV_PATH)


if __name__ == "__main__":
    main()
