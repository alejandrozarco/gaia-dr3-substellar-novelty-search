import warnings; warnings.filterwarnings("ignore")
import numpy as np, lightkurve as lk, pickle
from astropy.coordinates import SkyCoord
from astropy.timeseries import LombScargle
c=SkyCoord(223.46949,49.94663,unit="deg")
sr=lk.search_lightcurve(c,radius=5,author="TESS-SPOC")
out={}
print("per-sector Lomb-Scargle on PDCSAP flux (TESS-SPOC); Green+2023 says Porb=0.67759 d -> ellipsoidal at 0.33880 d\n")
for i in range(len(sr)):
    lc=sr[i].download(flux_column="pdcsap_flux")
    if lc is None: continue
    sec=lc.meta.get("SECTOR"); lc=lc.remove_nans().normalize()
    q=lc.quality.value if hasattr(lc.quality,"value") else np.asarray(lc.quality)
    lc=lc[q==0] if len(lc[q==0])>100 else lc
    t=lc.time.value; f=lc.flux.value; e=lc.flux_err.value
    f=f/np.nanmedian(f); m=np.isfinite(f)
    t,f,e=t[m],f[m],e[m]
    fr=np.linspace(1/10.0,1/0.08,60000)
    ls=LombScargle(t,f,e); pw=ls.power(fr)
    top=np.argsort(pw)[::-1]; peaks=[]
    for j in top:
        p=1/fr[j]
        if all(abs(p-q2)/q2>0.03 for q2,_ in peaks): peaks.append((p,pw[j]))
        if len(peaks)>=4: break
    def amp_at(P):
        mdl=ls.model(t,1/P); return (mdl.max()-mdl.min())/2*1e6
    fap=ls.false_alarm_probability(pw.max(),method="baluev")
    print(f"sector {sec}: {len(t)} pts, cadence {np.median(np.diff(t))*1440:.1f} min, rms {np.std(f)*1e6:.0f} ppm")
    print("   top peaks: "+"  ".join(f"{p:.5f}d (pw {w:.4f})" for p,w in peaks)+f"   FAP(top) {fap:.1e}")
    for P,lab in ((0.33880,"Green P/2 (ellipsoidal)"),(0.67759,"Green Porb")):
        k=np.argmin(abs(fr-1/P)); w=slice(max(0,k-40),k+40)
        print(f"   power near {lab:24s} {P:.5f}d: max {pw[w].max():.4f}   semi-amplitude of model there {amp_at(P):.0f} ppm")
    out[sec]=(t,f,e)
pickle.dump(out,open("tess_spoc.pkl","wb"))
