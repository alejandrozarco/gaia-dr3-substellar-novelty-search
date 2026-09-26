"""Arevalo+2026 'variable-but-called-constant' reservoir pilot.
Same EB pipeline as the 20,007-star hunt, wide-cone ZTF fetch (3in cone + 2in per-epoch filter),
template-tested end-to-end first. Reservoir vs control -> enrichment factor."""
import json,os,sys,math,csv,io,subprocess,time,threading
from concurrent.futures import ThreadPoolExecutor
EB="/private/tmp/claude-501/-Users-USER-claude-projects/5bae4473-7497-4a6b-8bf6-3ecc9abd4295/scratchpad/eb"
sys.path.insert(0,EB); os.chdir(EB); src=open("eb_hunt.py").read(); ns={"__name__":"x"}
exec(compile(src[:src.index('targets = json.load')],"eb_hunt.py","exec"),ns)
throttle=ns["throttle"]
def ztf_lc_wide(ra,dec,tries=4):
    u=("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?"
       f"POS=CIRCLE%20{ra:.6f}%20{dec:.6f}%20{3/3600:.6f}&BAD_CATFLAGS_MASK=32768&FORMAT=CSV")
    for k in range(tries):
        throttle(); p=subprocess.run(["curl","-sL","--max-time","120",u],capture_output=True,text=True)
        if p.returncode==0 and "oid" in p.stdout:
            rows=list(csv.DictReader(io.StringIO(p.stdout))); cd=math.cos(math.radians(dec))
            return [r for r in rows if math.hypot((float(r["ra"])-ra)*cd,float(r["dec"])-dec)*3600<2.0]
        time.sleep(3*(k+1))
    return None
ns["ztf_lc"]=ztf_lc_wide; analyse=ns["analyse"]
OUT="/private/tmp/claude-501/-Users-USER-claude-projects/5bae4473-7497-4a6b-8bf6-3ecc9abd4295/scratchpad/arev/results.jsonl"
for lab,t in (("ZTF18abxnwmb",dict(source_id="T1",ra=338.60558,dec=8.11656,g=12.7)),
              ("EA 2716884161263924224",dict(source_id="T2",ra=338.715361,dec=9.096215,g=16.4))):
    r=analyse(t); print(f"TEMPLATE {lab}: {r.get('status')} P={r.get('P')}",flush=True)
    if r.get("status")!="CANDIDATE": print("TEMPLATE FAILED - abort"); sys.exit(1)
T=[]
for s in ("reservoir","control"):
    T+=json.load(open(f"/private/tmp/claude-501/-Users-USER-claude-projects/5bae4473-7497-4a6b-8bf6-3ecc9abd4295/scratchpad/arev/targets_{s}.json"))
done=set()
if os.path.exists(OUT):
    for l in open(OUT):
        try: done.add(json.loads(l)["source_id"])
        except: pass
todo=[t for t in T if t["source_id"] not in done]
import random; random.Random(7).shuffle(todo)          # interleave samples: a partial run stays unbiased
print(f"pilot: {len(T)} targets ({sum(t['sample']=='reservoir' for t in T)} reservoir / {sum(t['sample']=='control' for t in T)} control), {len(todo)} to go",flush=True)
lk=threading.Lock(); n=[0]; t0=time.time()
def one(t):
    r=analyse(t); r.update(sample=t["sample"],arev_std=t["std"],arev_pvar=t["pvar"])
    with lk:
        open(OUT,"a").write(json.dumps(r)+"\n"); n[0]+=1
        if r.get("status") in ("CANDIDATE",): print(f"  *** {r['status']} [{t['sample']}] {t['source_id']} P={r.get('P')} depth={r.get('depth')} nights={r.get('n_ecl_nights')}",flush=True)
        if n[0]%100==0: print(f"  {n[0]}/{len(todo)}  {n[0]/(time.time()-t0):.2f}/s",flush=True)
with ThreadPoolExecutor(4) as ex: list(ex.map(one,todo))
from collections import Counter
R=[json.loads(l) for l in open(OUT)]
for s in ("reservoir","control"):
    c=Counter(r.get("status") for r in R if r.get("sample")==s); tot=sum(c.values())
    print(f"FINAL {s}: {tot} stars  CANDIDATE {c['CANDIDATE']} ({100*c['CANDIDATE']/max(1,tot):.2f}%)  WEAK {c['WEAK']}  {dict(c)}",flush=True)
print("PILOT_DONE",flush=True)
