#!/usr/bin/env python
import json, glob, os, numpy as np
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT=os.path.join(ROOT,"results","v2")
ORDER=["o200k_base","cl100k_base","Qwen3-1.7B","Gemma-3-1B","Gemma-2-2B","Llama-3.2-1B","Mistral-Nemo (Tekken)","DeepSeek-V3","gpt-oss (o200k_harmony)","Phi-4-mini","Sarvam-1","SmolLM3-3B","Granite-3.3-2B"]
V1={"o200k_base":"below","cl100k_base":"above","Qwen3-1.7B":"above","Gemma-3-1B":"below","Gemma-2-2B":"above","Llama-3.2-1B":"above"}
LANGS=["tel_Telu","hin_Deva","tam_Taml","kan_Knda","mal_Mlym","ben_Beng","mar_Deva"]
data={}
for f in glob.glob(OUT+"/counts_*.json"):
    d=json.load(open(f)); data[d["meta"]["name"]]=d
names=[n for n in ORDER if n in data]
rng=np.random.default_rng(1192); N=len(data[names[0]]["counts"]["eng_Latn"]); B=10000
idx=rng.integers(0,N,(B,N))
rows=[]
for n in names:
    c={k:np.array(v) for k,v in data[n]["counts"].items()}; e=c["eng_Latn"]
    r={"tokenizer":n,"spec":data[n]["meta"]["spec"],"vocab":data[n]["meta"]["vocab"],"eng_mean":float(e.mean())}
    for lg in LANGS:
        x=c[lg]; pt=x.mean()/e.mean(); bs=x[idx].mean(1)/e[idx].mean(1)
        r[lg]=[float(pt),float(np.percentile(bs,2.5)),float(np.percentile(bs,97.5))]
    rows.append(r)
# dedupe on Telugu counts
distinct=[]; dup={}
for r in rows:
    key=tuple(data[r["tokenizer"]]["counts"]["tel_Telu"])
    m=[d for d in distinct if tuple(data[d["tokenizer"]]["counts"]["tel_Telu"])==key]
    if m: dup[r["tokenizer"]]=m[0]["tokenizer"]
    else: distinct.append(r)
# H1
h1=[]
for n,side in V1.items():
    r=next((x for x in rows if x["tokenizer"]==n),None)
    if r is None: h1.append((n,side,"MISSING")); continue
    p,lo,hi=r["tel_Telu"]
    obs="above" if lo>2 else ("below" if hi<2 else "straddles")
    h1.append((n,side,obs))
held=sum(1 for _,s,o in h1 if s==o); flips=sum(1 for _,s,o in h1 if o not in (s,"straddles","MISSING"))
H1="PROVEN" if held==6 else ("DISPROVEN" if flips>=2 else "INCONCLUSIVE")
above=sum(1 for r in distinct if r["tel_Telu"][1]>2); below=sum(1 for r in distinct if r["tel_Telu"][2]<2); D=len(distinct)
H2="PROVEN" if above>D/2 else ("DISPROVEN" if below>D/2 else "INCONCLUSIVE")
summ={"n_sentences":N,"tokenizers_loaded":names,"duplicates":dup,"n_distinct":D,"H1":{"detail":h1,"held":held,"verdict":H1},
 "H2":{"above_2":above,"below_2":below,"distinct":D,"verdict":H2},"rows":rows,
 "status":json.load(open(OUT+"/load_status.json")) if os.path.exists(OUT+"/load_status.json") else None}
json.dump(summ,open(OUT+"/summary.json","w"),indent=1)
with open(OUT+"/summary.md","w") as f:
    f.write("| Tokenizer | Vocab | Telugu ÷ English [95% CI] | Hindi ÷ English | Tamil | Kannada | Malayalam | Bengali | Marathi |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
    for r in sorted(rows,key=lambda r:r["tel_Telu"][0]):
        t=r["tel_Telu"]; nm=r["tokenizer"]+(f" (= {dup[r['tokenizer']]} on Telugu)" if r["tokenizer"] in dup else "")
        f.write(f"| {nm} | {r['vocab']:,} | {t[0]:.2f}× [{t[1]:.2f}, {t[2]:.2f}] | "+" | ".join(f"{r[l][0]:.2f}×" for l in LANGS[1:])+" |\n")
print(json.dumps({k:summ[k] for k in ["n_sentences","duplicates","n_distinct","H1","H2"]},indent=1))
# figure
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
rs=sorted(rows,key=lambda r:r["tel_Telu"][0])
fig,ax=plt.subplots(figsize=(9,0.45*len(rs)+1.5))
y=np.arange(len(rs)); p=[r["tel_Telu"][0] for r in rs]
ax.barh(y,p,color=["#2b8a3e" if v<2 else "#c92a2a" for v in p])
ax.barh(y,[r["hin_Deva"][0] for r in rs],height=0.3,color="#1c7ed6",label="Hindi")
ax.axvline(2,ls="--",c="k",lw=1); ax.set_yticks(y); ax.set_yticklabels([r["tokenizer"] for r in rs])
for i,v in enumerate(p): ax.text(v+0.08,i,f"{v:.2f}×",va="center",fontsize=9)
ax.set_xlabel("tokens per sentence ÷ English tokens (same meaning, FLORES-200, 1,809 fresh sentences)")
ax.set_title("Telugu (bars) and Hindi (thin blue) token tax by tokenizer"); ax.legend(loc="lower right")
plt.tight_layout(); os.makedirs(os.path.join(ROOT,"figures"),exist_ok=True); plt.savefig(os.path.join(ROOT,"figures","v2_tax_by_tokenizer.png"),dpi=150)
