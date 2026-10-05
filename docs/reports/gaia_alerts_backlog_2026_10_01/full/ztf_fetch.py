import io, time, requests, pandas as pd, datetime, os
from concurrent.futures import ThreadPoolExecutor
t=pd.read_csv('gates.csv'); t=t[(t.DEdeg>-31)&t.survive].reset_index(drop=True)
def now(): return datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
def ztf(a,d,r=5/3600):
    for k in range(3):
        try:
            q=requests.get('https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves',params=dict(POS=f'CIRCLE {a} {d} {r}',BANDNAME='g,r,i',FORMAT='csv'),timeout=400)
            if q.ok: return q.text
        except Exception as e: print('exc',e,flush=True)
        time.sleep(20)
    return None
def control():
    c=ztf(274.05458,49.86778); n=(c.count('\n')-1) if c else -1
    print(now(),'CONTROL AM Her rows',n,flush=True); return n>100
def one(r):
    if os.path.exists(f'ztf/{r.Name}.csv'): return dict(Name=r.Name,ztf_ts='cached',ztf='ok:cached')
    ts=now(); x=ztf(r.RAdeg,r.DEdeg)
    if x is None: st='HOLE'
    else:
        d=pd.read_csv(io.StringIO(x)) if x.count('\n')>1 else pd.DataFrame()
        if len(d)==0: st='EMPTY'
        else: d.to_csv(f'ztf/{r.Name}.csv',index=False); st=f'ok:{len(d)}'
    print(r.Name,st,flush=True); return dict(Name=r.Name,ztf_ts=ts,ztf=st)
log=[]
for c0 in range(0,len(t),24):
    ok=control()
    with ThreadPoolExecutor(4) as ex: res=list(ex.map(one,[r for r in t.iloc[c0:c0+24].itertuples()]))
    ok2=control()
    for x in res: x['ctrl_pre']=ok; x['ctrl_post']=ok2
    log+=res; pd.DataFrame(log).to_csv('ztf_log.csv',index=False)
print('END',now(),flush=True)
