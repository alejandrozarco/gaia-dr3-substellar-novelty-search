# TIC 685214650 follow-up tests at the S87 frequency 787.4655 c/d: amplitude (e/s) in SAP_FLUX, PDCSAP_FLUX and SAP_BKG per
# sector and per orbit (split at the largest gap); S94 amplitude at the exact S87 frequency.
import numpy as np, glob
from astropy.io import fits
f0 = 787.4655
def fit(t, y, f):
    X = np.vstack([np.ones_like(t), np.sin(2*np.pi*f*t), np.cos(2*np.pi*f*t)]).T; b, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ b; s = np.sqrt(np.sum(r**2)/(len(y)-3)); C = np.linalg.inv(X.T @ X)*s**2
    return np.hypot(b[1], b[2]), np.sqrt((C[1,1]+C[2,2])/2), np.degrees(np.arctan2(b[2], b[1]))
for sec in ("0087", "0094"):
    d = fits.open(glob.glob(f"mastDownload/TESS/*s{sec}*/*fast-lc.fits")[0])[1].data
    m = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"]) & np.isfinite(d["SAP_BKG"])
    t = d["TIME"][m]; cols = {k: d[k][m] for k in ("PDCSAP_FLUX", "SAP_FLUX", "SAP_BKG")}
    gap = np.argmax(np.diff(t)); halves = (("orbit 1", t <= t[gap]), ("orbit 2", t > t[gap]), ("all", np.ones(len(t), bool)))
    for lab, sel in halves:
        line = []
        for k, y in cols.items():
            yy = y[sel] - np.median(y[sel]); A, eA, ph = fit(t[sel], yy, f0)
            line.append(f"{k} {A:.3f}+-{eA:.3f} e/s ({A/eA:.1f} sig, phase {ph:.0f})")
        print(f"S{sec[2:]} {lab} (n {sel.sum()}, {t[sel].min():.1f}-{t[sel].max():.1f}): " + " | ".join(line))
