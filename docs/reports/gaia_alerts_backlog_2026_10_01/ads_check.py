import os, glob, requests, pandas as pd
f=[p for p in glob.glob(os.path.expanduser('~/.config/ads/*')) if os.path.isfile(p)][0]
tok=open(f).read().strip().split()[-1]
H={'Authorization':'Bearer '+tok}
A=pd.read_csv('alerts.csv',skipinitialspace=True); A.columns=[c.strip().lstrip('#') for c in A.columns]
s=pd.read_csv('short.csv').merge(A[['Name','TNSid']],on='Name')
def q(x):
    r=requests.get('https://api.adsabs.harvard.edu/v1/search/query',headers=H,params=dict(q=x,fl='bibcode,title',rows=10),timeout=60)
    r.raise_for_status(); return [(d['bibcode'],d.get('title',[''])[0][:70]) for d in r.json()['response']['docs']]
print('control Gaia19bey:',len(q('full:"Gaia19bey"')))
rows=[]
for r in s.itertuples():
    tn=str(r.TNSid).replace('AT','')
    qs=f'full:"{r.Name}" OR full:"{r.Source}"'+(f' OR full:"AT {tn}" OR full:"AT{tn}"' if tn!='nan' else '')
    h=q(qs); rows.append(dict(Name=r.Name,ads_n=len(h),ads=h)); print(r.Name,len(h),h[:4],flush=True)
pd.DataFrame(rows).to_csv('ads_short.csv',index=False)
