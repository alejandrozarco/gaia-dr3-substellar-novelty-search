# TESS SPOC light curves of TIC 764468822 = Gaia DR3 5208047381438507520 (hot DQ candidate, 96 pc): per sector and combined
# Lomb-Scargle 0.05-359 c/d (120-s) and 0.05-2159 c/d (20-s); PDCSAP, QUALITY == 0, 5-sigma clip; Baluev FAP; CROWDSAP.
import json, os, subprocess, numpy as np
from astropy.io import fits
from astropy.timeseries import LombScargle
from astroquery.mast import Observations
obs = Observations.query_criteria(obs_collection="TESS", target_name="764468822", dataproduct_type="timeseries", provenance_name="SPOC")
prods = Observations.get_product_list(obs)
files = sorted({p["productFilename"] for p in prods if p["productFilename"].endswith(("_lc.fits", "fast-lc.fits"))})
os.makedirs("lc", exist_ok=True); out = {}
T = {"120": [], "20": []}
for fn in files:
    path = f"lc/{fn}"
    if not os.path.exists(path): subprocess.run(["curl", "-sL", "-m", "600", "-o", path, f"https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:TESS/product/{fn}"])
    h = fits.open(path); d = h[1].data; hd = h[1].header; cad = "20" if "fast" in fn else "120"
    m = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"]) & np.isfinite(d["TIME"]); t = d["TIME"][m]; y = d["PDCSAP_FLUX"][m] / np.nanmedian(d["PDCSAP_FLUX"][m]) - 1
    mad = 1.4826 * np.median(np.abs(y - np.median(y))); ok = np.abs(y - np.median(y)) < 5 * mad; t, y = t[ok], y[ok]
    fmax = 2159 if cad == "20" else 359; fr = np.arange(0.05, fmax, 0.2 / (t.max() - t.min()))
    ls = LombScargle(t, y); p = ls.power(fr, method="fast"); amp = np.sqrt(4 * LombScargle(t, y, normalization="psd").power(fr, method="fast") / len(t))
    order = np.argsort(amp)[::-1]; pk = []
    for k in order:
        if all(abs(fr[k] - q[0]) > 0.05 for q in pk): pk.append((round(float(fr[k]), 4), round(float(amp[k] * 1e3), 2), round(float(amp[k] / amp.mean()), 1)))
        if len(pk) == 4: break
    fap = float(ls.false_alarm_probability(p.max(), minimum_frequency=0.05, maximum_frequency=fmax, method="baluev"))
    sec = h[0].header["SECTOR"]; out[f"S{sec}_{cad}"] = dict(n=int(len(t)), crowdsap=hd.get("CROWDSAP"), rms_ppt=float(np.std(y) * 1e3), meanamp_ppt=float(amp.mean() * 1e3), top=pk, fap_top=fap)
    print(f"S{sec} {cad}s n {len(t)} CROWDSAP {hd.get('CROWDSAP')} mean amp {amp.mean()*1e3:.2f} ppt; top {pk}; FAP {fap:.2g}", flush=True)
    T[cad].append((t, y))
for cad, L in T.items():
    if not L: continue
    t = np.concatenate([a for a, b in L]); y = np.concatenate([b for a, b in L]); fmax = 2159 if cad == "20" else 359
    fr = np.arange(0.05, fmax, 0.2 / (t.max() - t.min())) if cad == "120" else np.arange(0.05, fmax, 0.2 / (t.max() - t.min()))
    ls = LombScargle(t, y); P = ls.power(fr, method="fast"); amp = np.sqrt(4 * LombScargle(t, y, normalization="psd").power(fr, method="fast") / len(t))
    order = np.argsort(amp)[::-1]; pk = []
    for k in order:
        if all(abs(fr[k] - q[0]) > 0.01 for q in pk): pk.append((round(float(fr[k]), 5), round(float(amp[k] * 1e3), 3), round(float(amp[k] / amp.mean()), 1)))
        if len(pk) == 5: break
    fap = float(ls.false_alarm_probability(P.max(), minimum_frequency=0.05, maximum_frequency=fmax, method="baluev"))
    out[f"combined_{cad}"] = dict(n=int(len(t)), nfreq=int(len(fr)), meanamp_ppt=float(amp.mean() * 1e3), top=pk, fap_top=fap)
    print(f"combined {cad}s: n {len(t)}, {len(fr)} freqs, mean amp {amp.mean()*1e3:.3f} ppt; top {pk}; FAP {fap:.2g}", flush=True)
json.dump(out, open("tess_hotdq.json", "w"), indent=1)
