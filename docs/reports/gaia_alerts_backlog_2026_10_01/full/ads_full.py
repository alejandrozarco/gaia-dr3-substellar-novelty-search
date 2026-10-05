import os, glob, requests, pandas as pd, time, datetime
f=[p for p in glob.glob(os.path.expanduser('~/.config/ads/*')) if os.path.isfile(p)][0]
H={'Authorization':'Bearer '+open(f).read().strip().split()[-1]}
t=pd.read_csv('gates.csv'); t=t[t.survive]
def q(x):
    for k in range(3):
        try:
            r=requests.get('https://api.adsabs.harvard.edu/v1/search/query',headers=H,params=dict(q=x,fl='bibcode,title',rows=20),timeout=60)
            r.raise_for_status(); return [(d['bibcode'],d.get('title',[''])[0][:70]) for d in r.json()['response']['docs']]
        except Exception as e: time.sleep(5)
    return None
c=q('full:"Gaia19bey"'); print('control Gaia19bey hits:',None if c is None else len(c),flush=True)
rows=[]
for r in t.itertuples():
    tn=str(r.TNSid).strip().replace('AT','').strip()
    qs=f'full:"{r.Name}" OR full:"{r.Source}"'+(f' OR full:"AT {tn}" OR full:"AT{tn}"' if tn not in ('nan','') else '')
    h=q(qs); ts=datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%MZ')
    nontns=None if h is None else [x for x in h if 'TNS' not in x[0]]
    rows.append(dict(Name=r.Name,ads_ts=ts,ads_n=None if h is None else len(h),ads_nonTNS=None if h is None else len(nontns),ads=h))
    if nontns: print(r.Name,nontns,flush=True)
    time.sleep(1)
d=pd.DataFrame(rows); d.to_csv('ads_full.csv',index=False); print('fails',d.ads_n.isna().sum(),'with non-TNS hits',(d.ads_nonTNS>0).sum())
