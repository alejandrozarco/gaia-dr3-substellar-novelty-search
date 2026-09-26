import requests, io, pandas as pd, numpy as np
from astropy.timeseries import LombScargle
ra,dec=287.097272,9.226177
r=requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves",params=dict(POS=f"CIRCLE {ra} {dec} 0.0005",BANDNAME="g,r,i",FORMAT="csv"),timeout=300)
df=pd.read_csv(io.StringIO(r.text)); df.to_csv("ztf_4307667617377160704.csv",index=False)
print("rows",len(df), df.groupby(["oid","filtercode"]).size().to_dict())
df=df[(df.catflags==0)&(df.magerr<0.2)]
parts=[]
for (o,f),g in df.groupby(["oid","filtercode"]):
    if len(g)<30: continue
    fl=10**(-0.4*(g.mag-np.median(g.mag))); e=0.921*g.magerr*fl
    print(f,o,len(g),"median mag",round(np.median(g.mag),2),"rms%",round(100*np.std(fl),2),"err%",round(100*np.median(e),2))
    parts.append(pd.DataFrame(dict(t=g.hjd.values,f=fl.values-1,e=e.values)))
d=pd.concat(parts); fr=np.arange(0.02,300,0.1/(d.t.max()-d.t.min())); ls=LombScargle(d.t,d.f,d.e); p=ls.power(fr,method="fast")
seen=[]
for i in np.argsort(p)[::-1]:
    if all(abs(fr[i]-s)>0.01 for s in seen): seen.append(fr[i])
    if len(seen)==6: break
for f in seen:
    pw=ls.power(f); print(f"f {f:.5f} c/d P {24/f:.4f} h amp~{100*np.sqrt(4*pw*np.var(d.f)):.2f}% FAP {ls.false_alarm_probability(pw,minimum_frequency=0.02,maximum_frequency=300,method='baluev'):.2e}")
