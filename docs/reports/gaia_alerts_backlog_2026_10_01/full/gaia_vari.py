import requests, pandas as pd, time
from concurrent.futures import ThreadPoolExecutor
t=pd.read_csv('gates.csv'); t=t[t.survive]
cats=['I/358/vclassre','I/358/vlpv','I/358/vmicro','I/358/vst','I/358/veb','I/358/vagn','I/358/vrrlyr','I/358/vcep','J/A+A/674/A23/tabled1']
def q(r):
    out=[]
    for c in cats:
        for k in range(3):
            try:
                x=requests.get('https://vizier.cds.unistra.fr/viz-bin/asu-tsv',params={'-source':c,'-c':f'{r.RAdeg:.6f} {r.DEdeg:+.6f}','-c.rs':1.5,'-out.max':5,'-out.add':'_r'},timeout=120)
                if x.ok:
                    L=[l for l in x.text.splitlines() if l and not l.startswith('#')]
                    if len(L)>3: out.append(c+': '+' | '.join(L[3:])[:300])
                    break
            except Exception: time.sleep(5)
        else: out.append(c+': QUERYFAIL')
    return r.Name,out
rows=list(ThreadPoolExecutor(6).map(q,t.itertuples()))
# control: Gaia DR3 microlensing event #1 position
_,c=q(type('R',(),dict(Name='CTRL',RAdeg=184.4363263,DEdeg=-59.0294197))()); print('control', [x[:40] for x in c])
d=pd.DataFrame([dict(Name=n,gaia_vari='; '.join(o)) for n,o in rows]); d.to_csv('gaia_vari.csv',index=False)
for r in d[d.gaia_vari!=''].itertuples(): print(r.Name, r.gaia_vari[:400])
