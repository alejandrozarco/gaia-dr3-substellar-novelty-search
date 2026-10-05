import io, requests, pandas as pd, numpy as np, time
from concurrent.futures import ThreadPoolExecutor
t=pd.read_csv('targets.csv')
rows=[dict(name=r.Name,ra=r.RAdeg,dec=r.DEdeg) for r in t.itertuples()]+[dict(name='CTRL_AMHer',ra=274.05458,dec=49.86778)]
def q(cat,cols,r,rad):
    for k in range(4):
        try:
            x=requests.get('https://vizier.cds.unistra.fr/viz-bin/asu-tsv',params={'-source':cat,'-c':f"{r['ra']:.6f} {r['dec']:+.6f}",'-c.rs':rad,'-out':cols,'-out.max':200,'-oc.form':'d','-out.add':'_r'},timeout=120)
            if x.ok:
                L=[l for l in x.text.splitlines() if l and not l.startswith('#')]
                if len(L)<3: return pd.DataFrame()
                hdr=L[0].split('\t'); data=[l.split('\t') for l in L[3:]]
                d=pd.DataFrame(data,columns=hdr); d.insert(0,'name',r['name']); return d
        except Exception as e: pass
        time.sleep(5)
    return None
def run(cat,cols,rad,out):
    with ThreadPoolExecutor(6) as ex: res=list(ex.map(lambda r: q(cat,cols,r,rad),rows))
    fails=[r['name'] for r,d in zip(rows,res) if d is None]
    D=pd.concat([d for d in res if d is not None and len(d)]); D.to_csv(out,index=False)
    print(out,'fails',fails,'ctrl rows',(D.name=='CTRL_AMHer').sum(),'objects with rows',D.name.nunique(),flush=True)
run('I/355/gaiadr3','Source,RA_ICRS,DE_ICRS,Gmag,BP-RP,Plx,e_Plx,pmRA,e_pmRA,pmDE,e_pmDE,RUWE,PQSO,PGal,QSO,Gal',3,'gaia_nb3.csv')
run('II/328/allwise','AllWISE,W1mag,W2mag,W3mag,W4mag,Jmag,Hmag,Kmag,ccf,qph',3,'allwise3.csv')
