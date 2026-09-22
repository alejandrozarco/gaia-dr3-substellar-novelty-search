import warnings,pickle,math,subprocess,urllib.parse,json; warnings.filterwarnings("ignore")
import numpy as np
from astropy.timeseries import LombScargle
d=pickle.load(open("tess_spoc.pkl","rb"))
P_=lambda x: np.asarray(getattr(x,"unmasked",x),dtype=float)
t=np.concatenate([P_(v[0]) for v in d.values()]); f=np.concatenate([P_(v[1]) for v in d.values()]); e=np.concatenate([P_(v[2]) for v in d.values()])
ok=np.isfinite(t)&np.isfinite(f)&np.isfinite(e); t,f,e=t[ok],f[ok],e[ok]
o=np.argsort(t); t,f,e=t[o],f[o],e[o]
print(f"TESS combined: {len(t)} points, {t.min():.1f}-{t.max():.1f} BTJD ({(t.max()-t.min())/365.25:.1f} yr)")
fr=np.linspace(1/0.6790,1/0.6762,40001); ls=LombScargle(t,f,e,nterms=2); pw=ls.power(fr)
P=1/fr[np.argmax(pw)]
print(f"refined orbital period (2-harmonic LS near 0.6776 d): P = {P:.6f} d")
ph=((t-t[0])/P)%1.0
nb=100; prof=np.array([np.median(f[(ph>=k/nb)&(ph<(k+1)/nb)]) for k in range(nb)])
kmin=np.argmin(prof); ph=((ph-kmin/nb)+0.02)%1.0     # put the deeper minimum near phase 0.02
prof=np.array([np.median(f[(ph>=k/nb)&(ph<(k+1)/nb)]) for k in range(nb)])
cen=(np.arange(nb)+0.5)/nb
m1=prof.min(); k1=np.argmin(prof)
mask=np.abs(((cen-cen[k1]+0.5)%1)-0.5)>0.25; k2=np.where(mask)[0][np.argmin(prof[mask])]; m2=prof[k2]
mx=np.percentile(prof,95)
print(f"primary min at phase {cen[k1]:.2f}: depth {(mx-m1)*100:.2f}%   secondary min at phase {cen[k2]:.2f}: depth {(mx-m2)*100:.2f}%   separation {abs(cen[k2]-cen[k1]):.3f}")
maxs=[prof[(np.abs(cen-c)<0.12)].max() for c in ((cen[k1]+0.25)%1,(cen[k1]+0.75)%1)]
print(f"maxima at quadratures: {maxs[0]:.5f} / {maxs[1]:.5f}  (O'Connell asymmetry {(maxs[0]-maxs[1])*1e6:+.0f} ppm)")
# shape: flat-bottom/narrow-eclipse vs continuous (ellipsoidal/contact)?
fl=np.mean(np.abs(prof-np.median(prof))>0.3*(mx-m1))
print(f"fraction of phase deviating >30% of full range: {fl:.2f}  -> {'CONTINUOUS (ellipsoidal / contact-like)' if fl>0.4 else 'NARROW ECLIPSES (detached-like)'}")
print("binned profile (ppm below max), 50 bins:")
p50=np.array([np.median(f[(ph>=k/50)&(ph<(k+1)/50)]) for k in range(50)])
print("  "+" ".join(f"{(mx-x)*1e6:5.0f}" for x in p50[:25])); print("  "+" ".join(f"{(mx-x)*1e6:5.0f}" for x in p50[25:]))
pickle.dump((P,t,f,e),open("fold.pkl","wb"))
# ---- Gaia DR3: RV statistics + NSS orbit ----
def tap(q):
    u="https://gea.esac.esa.int/tap-server/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT=json&QUERY="+urllib.parse.quote(q)
    return json.loads(subprocess.run(["curl","-sL","--max-time","120",u],capture_output=True,text=True).stdout)
g=tap("SELECT radial_velocity,radial_velocity_error,rv_nb_transits,rv_amplitude_robust,rv_chisq_pvalue,rv_renormalised_gof,rv_method_used,rv_template_teff,ruwe,non_single_star,phot_g_mean_mag,bp_rp,parallax FROM gaiadr3.gaia_source WHERE source_id=1593152388271709824")
print("\nGaia DR3 source:"); [print(f"   {c['name']:24s} {v}") for c,v in zip(g["metadata"],g["data"][0])]
n=tap("SELECT nss_solution_type,period,period_error,eccentricity,significance,a_thiele_innes,b_thiele_innes,f_thiele_innes,g_thiele_innes,goodness_of_fit,flags FROM gaiadr3.nss_two_body_orbit WHERE source_id=1593152388271709824")
print("Gaia DR3 NSS orbit:"); [print(f"   {c['name']:24s} {v}") for c,v in zip(n["metadata"],n["data"][0])] if n["data"] else print("   none")
