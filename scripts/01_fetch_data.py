#!/usr/bin/env python
"""Fetch FLORES-200 parallel sentences (eng/tel/hin) + a Python code reference set.

Public data only. Resumable: skips work whose output already exists.
"""
import json, os, sys, tarfile, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
FLORES_URL = "https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz"
TARBALL = os.path.join(DATA, "flores200.tar.gz")
LANGS = ["eng_Latn", "tel_Telu", "hin_Deva"]
N_SENT = 200


def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f"[skip] {os.path.basename(path)} exists")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print(f"[get ] {url}")
    urllib.request.urlretrieve(url, path)


def fetch_flores():
    get(FLORES_URL, TARBALL)
    want = [f"./flores200_dataset/devtest/{lg}.devtest" for lg in LANGS]
    with tarfile.open(TARBALL) as tf:
        names = set(tf.getnames())
        members = [n for n in want if n in names]
        if len(members) != len(want):
            missing = set(want) - names
            raise SystemExit(f"missing members in tarball: {missing}")
        tf.extractall(DATA, members=members)
    out = {}
    for lg in LANGS:
        p = os.path.join(DATA, "flores200_dataset", "devtest", f"{lg}.devtest")
        with open(p, encoding="utf-8") as f:
            sent = [l.rstrip("\n") for l in f if l.strip()]
        out[lg] = sent[:N_SENT]
        print(f"[ok  ] {lg}: {len(out[lg])} sentences (of {len(sent)} available)")
    return out


def fetch_code():
    """HumanEval + MBPP -> first 200 Python snippets (non-parallel reference row)."""
    try:
        from datasets import load_dataset
    except Exception as e:  # pragma: no cover
        print("datasets unavailable, skipping code row:", e)
        return []
    snips = []
    try:
        he = load_dataset("openai/openai_humaneval", split="test")
        for r in he:
            snips.append(r["prompt"] + r.get("canonical_solution", ""))
    except Exception as e:
        print("HumanEval failed:", e)
    if len(snips) < N_SENT:
        try:
            mb = load_dataset("google-research-datasets/mbpp", "full", split="test")
            for r in mb:
                if len(snips) >= N_SENT:
                    break
                snips.append(r["text"] + "\n" + r["code"])
        except Exception as e:
            print("MBPP failed:", e)
    snips = snips[:N_SENT]
    print(f"[ok  ] code: {len(snips)} Python snippets")
    return snips


def main():
    os.makedirs(DATA, exist_ok=True)
    flores = fetch_flores()
    code = fetch_code()
    out = {"flores": flores, "code": code, "n_sentences": N_SENT}
    p = os.path.join(DATA, "sentences.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"[done] wrote {p}")


if __name__ == "__main__":
    main()
