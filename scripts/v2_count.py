#!/usr/bin/env python
"""119b: fresh FLORES sentences (dev + devtest[200:]), more tokenizers, dedupe. Resumable per tokenizer."""
import json, os, sys, time, traceback
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD=os.path.join(ROOT,"data","flores200_dataset"); OUT=os.path.join(ROOT,"results","v2")
LANGS=["eng_Latn","tel_Telu","hin_Deva","tam_Taml","kan_Knda","mal_Mlym","ben_Beng","mar_Deva"]
TOK=[("o200k_base","tiktoken","o200k_base"),("cl100k_base","tiktoken","cl100k_base"),
 ("Qwen3-1.7B","hf","Qwen/Qwen3-1.7B"),("Gemma-3-1B","hf","unsloth/gemma-3-1b-it"),
 ("Gemma-2-2B","hf","unsloth/gemma-2-2b"),("Llama-3.2-1B","hf","unsloth/Llama-3.2-1B"),
 # new in 119b
 ("Mistral-Nemo (Tekken)","hf","unsloth/Mistral-Nemo-Instruct-2407"),
 ("DeepSeek-V3","hf","deepseek-ai/DeepSeek-V3"),
 ("gpt-oss (o200k_harmony)","hf","openai/gpt-oss-20b"),
 ("Phi-4-mini","hf","microsoft/Phi-4-mini-instruct"),
 ("Sarvam-1","hf","sarvamai/sarvam-1"),
 ("SmolLM3-3B","hf","HuggingFaceTB/SmolLM3-3B"),
 ("Granite-3.3-2B","hf","ibm-granite/granite-3.3-2b-instruct"),
]
def sents():
    d={}
    for lg in LANGS:
        dev=[l.rstrip("\n") for l in open(f"{FD}/dev/{lg}.dev",encoding="utf-8")]
        dt=[l.rstrip("\n") for l in open(f"{FD}/devtest/{lg}.devtest",encoding="utf-8")]
        d[lg]=dev+dt[200:]
    n={len(v) for v in d.values()}; assert len(n)==1, n
    return d
def main():
    S=sents(); print("sentences per lang", len(S["eng_Latn"]))
    status={}
    for name,kind,spec in TOK:
        fn=os.path.join(OUT,"counts_"+name.split()[0].replace("/","_")+".json")
        if os.path.exists(fn): status[name]="ok(cached)"; continue
        try:
            t0=time.time()
            if kind=="tiktoken":
                import tiktoken; enc=tiktoken.get_encoding(spec); f=lambda t: len(enc.encode(t))
            else:
                from transformers import AutoTokenizer
                tk=AutoTokenizer.from_pretrained(spec, trust_remote_code=False)
                f=lambda t: len(tk.encode(t, add_special_tokens=False))
                vs=len(tk)
            res={lg:[f(s) for s in S[lg]] for lg in LANGS}
            meta={"name":name,"spec":spec,"kind":kind,"vocab": (enc.n_vocab if kind=="tiktoken" else vs)}
            json.dump({"meta":meta,"counts":res},open(fn,"w"))
            status[name]=f"ok {time.time()-t0:.1f}s vocab={meta['vocab']}"
        except Exception as e:
            status[name]="FAILED: "+repr(e)[:300]
        print(name, status[name], flush=True)
    json.dump(status,open(os.path.join(OUT,"load_status.json"),"w"),indent=1)
main()
