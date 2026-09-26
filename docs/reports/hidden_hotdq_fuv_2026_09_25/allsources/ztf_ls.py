import numpy as np, pandas as pd
from astropy.timeseries import LombScargle
df = pd.read_csv("ztf_J2051.csv")
print("programids", df.groupby(["filtercode","programid"]).size().to_dict())
df = df[(df.catflags==0) & (df.magerr<0.15)]
parts=[]
for (oid,f),g in df.groupby(["oid","filtercode"]):
    if len(g)<30: continue
    fl = 10**(-0.4*(g.mag-np.median(g.mag))); ef = 0.921*g.magerr*fl
    m = np.abs(fl-np.median(fl)) < 5*1.4826*np.median(np.abs(fl-np.median(fl)))
    print(f, oid, len(g), "kept", m.sum(), "median mag", round(np.median(g.mag),3), "rms %", round(100*np.std(fl[m]),2), "median err %", round(100*np.median(ef[m]),2))
    parts.append(pd.DataFrame(dict(t=g.hjd[m].values, f=fl[m].values-1, e=ef[m].values, band=f)))
d = pd.concat(parts); print("combined", len(d), "baseline d", round(d.t.max()-d.t.min(),1))
freq = np.arange(0.02, 300, 0.1/(d.t.max()-d.t.min()))
ls = LombScargle(d.t, d.f, d.e); p = ls.power(freq, method="fast")
top = np.argsort(p)[::-1]
seen=[]
for i in top:
    if all(abs(freq[i]-s)>0.01 for s in seen): seen.append(freq[i])
    if len(seen)==8: break
N=len(d)
for fq in seen:
    pw = ls.power(fq); amp = np.sqrt(4*pw*np.var(d.f))  # rough semi-amplitude
    fap = ls.false_alarm_probability(pw, minimum_frequency=0.02, maximum_frequency=300, method="baluev")
    print(f"f={fq:.5f} c/d P={24/fq:.4f} h power={pw:.4f} amp~{100*amp:.2f}% FAP={fap:.2e}")
# per-band check of the top frequency
f0=seen[0]
for b,g in d.groupby("band"):
    l=LombScargle(g.t,g.f,g.e); fr=np.linspace(f0-0.01,f0+0.01,2001); pp=l.power(fr)
    print(b, "peak near top", round(fr[np.argmax(pp)],5), "power", round(pp.max(),4), "FAP", l.false_alarm_probability(pp.max(),minimum_frequency=0.02,maximum_frequency=300,method="baluev"))
# upper limit: injection of a sinusoid at a range of periods
rng=np.random.default_rng(1)
for P_min in (5,10,20,60,240,1440):
    fq=1440/P_min; det=0
    for k in range(20):
        A=0.01; ph=rng.uniform(0,2*np.pi)
        ff=d.f+A*np.sin(2*np.pi*fq*d.t+ph)
        l=LombScargle(d.t,ff,d.e); fr=np.linspace(fq*0.999,fq*1.001,201); pp=l.power(fr).max()
        det += l.false_alarm_probability(pp,minimum_frequency=0.02,maximum_frequency=300,method="baluev")<1e-3
    print(f"injected 1.0% at P={P_min} min: recovered {det}/20")
