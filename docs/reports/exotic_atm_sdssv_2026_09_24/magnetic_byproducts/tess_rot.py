# TESS SPOC light curves (PDCSAP, QUALITY == 0, 5-sigma clip): per-sector and combined Lomb-Scargle, 0.1-359 c/d (120 s) or 0.1-2159 c/d
# (20 s); top peak, Baluev FAP, CROWDSAP. Usage: python tess_rot.py <label> <TIC>
import sys, os, subprocess, numpy as np
from astropy.io import fits
from astropy.timeseries import LombScargle
from astroquery.mast import Observations
label, tic = sys.argv[1], sys.argv[2]
obs = Observations.query_criteria(obs_collection="TESS", target_name=tic, dataproduct_type="timeseries", provenance_name="SPOC")
fns = sorted({n for n in Observations.get_product_list(obs)["productFilename"] if n.endswith(("s_lc.fits", "fast-lc.fits"))})
os.makedirs("lc", exist_ok=True); comb = {"120": [], "20": []}
for fn in fns:
    p = f"lc/{fn}"
    if not os.path.exists(p): subprocess.run(["curl", "-sL", "-m", "600", "-o", p, f"https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:TESS/product/{fn}"])
    h = fits.open(p); d = h[1].data; cad = "20" if "fast" in fn else "120"
    m = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"]); t = d["TIME"][m]; y = d["PDCSAP_FLUX"][m] / np.nanmedian(d["PDCSAP_FLUX"][m]) - 1
    mad = 1.4826 * np.median(np.abs(y - np.median(y))); ok = np.abs(y - np.median(y)) < 5 * mad; t, y = t[ok], y[ok]
    fmax = 2159 if cad == "20" else 359; fr = np.arange(0.1, fmax, 0.2 / (t.max() - t.min()))
    ls = LombScargle(t, y); P = ls.power(fr, method="fast"); amp = np.sqrt(4 * LombScargle(t, y, normalization="psd").power(fr, method="fast") / len(t)); k = np.argmax(P)
    fap = ls.false_alarm_probability(P[k], minimum_frequency=0.1, maximum_frequency=fmax, method="baluev")
    print(f"{label} S{h[0].header['SECTOR']} {cad}-s CROWDSAP {h[1].header.get('CROWDSAP')}: top {fr[k]:.4f} c/d ({24/fr[k]:.3f} h) amp {amp[k]*100:.2f}% S/N {amp[k]/amp.mean():.1f} FAP {fap:.2g}")
    comb[cad].append((t, y))
for cad, L in comb.items():
    if len(L) < 2: continue
    t = np.concatenate([a for a, b in L]); y = np.concatenate([b for a, b in L]); fmax = 2159 if cad == "20" else 359
    fr = np.arange(0.1, fmax, 0.5 / (t.max() - t.min())) if (t.max() - t.min()) > 400 else np.arange(0.1, fmax, 0.2 / (t.max() - t.min()))
    ls = LombScargle(t, y); P = ls.power(fr, method="fast"); amp = np.sqrt(4 * LombScargle(t, y, normalization="psd").power(fr, method="fast") / len(t)); k = np.argmax(P)
    print(f"{label} combined {cad}-s ({len(L)} sectors): top {fr[k]:.5f} c/d ({24/fr[k]:.4f} h) amp {amp[k]*100:.3f}% S/N {amp[k]/amp.mean():.1f} FAP {ls.false_alarm_probability(P[k], minimum_frequency=0.1, maximum_frequency=fmax, method='baluev'):.2g}")
