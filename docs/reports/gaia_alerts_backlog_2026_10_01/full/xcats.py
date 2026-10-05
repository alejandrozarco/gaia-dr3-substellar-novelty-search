import requests, pandas as pd, time
from concurrent.futures import ThreadPoolExecutor
t=pd.read_csv('gates.csv'); t=t[t.survive]
cats=[('VII/294/catalog',3,'Milliquas'),('J/A+A/682/A34/erass1-m',20,'eRASS1'),('IX/47/2rxs',30,'2RXS'),('J/ApJS/254/33/table1',2,'SPICY'),('II/335/galex_ais',3,'GALEX'),('J/MNRAS/487/2522/table1',2,'Marton19YSO'),('J/A+A/620/A172/dr2yso',2,'Marton19b?')]
def q(r):
    out=[]
    for c,rad,lab in cats:
        for k in range(3):
            try:
                x=requests.get('https://vizier.cds.unistra.fr/viz-bin/asu-tsv',params={'-source':c,'-c':f'{r.RAdeg:.6f} {r.DEdeg:+.6f}','-c.rs':rad,'-out.max':3,'-out.add':'_r','-sort':'_r'},timeout=120)
                if x.ok:
                    L=[l for l in x.text.splitlines() if l and not l.startswith('#')]
                    if len(L)>3: out.append(lab+': '+' | '.join(' '.join(L[3].split()) for _ in [0])[:160])
                    break
            except Exception: time.sleep(5)
        else: out.append(lab+': QUERYFAIL')
    return r.Name,out
rows=list(ThreadPoolExecutor(6).map(q,t.itertuples()))
_,c=q(type('R',(),dict(Name='CTRL_AMHer',RAdeg=274.05458,DEdeg=49.86778))()); print('control AM Her', c)
d=pd.DataFrame([dict(Name=n,xcats='; '.join(o)) for n,o in rows]); d.to_csv('xcats.csv',index=False)
for r in d[d.xcats!=''].itertuples(): print(r.Name, r.xcats)
