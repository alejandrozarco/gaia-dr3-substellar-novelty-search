# Gaia DR3 epoch photometry (VizieR I/355/epphot) of 6021870154194477312: GLS 0.5-50 c/d and a sinusoid at the ATLAS frequency
# 13.929771 c/d with the same basis as atlas_neigh.py (sin/cos of 2 pi f t, t = full BJD), so the phase is directly comparable.
# TimeG is BJD(TCB) - 2455197.5; TCB-TDB (~19 s) is ignored. Rejected-flag (GrVFlag/BPrVFlag/RPrVFlag = 1) points dropped.
import numpy as np, pandas as pd
from astropy.timeseries import LombScargle
d = pd.read_csv("gaia_epphot_6021.csv"); f1 = 13.929771
rng = np.random.default_rng(3)
for b, tc, fc, ec, flag in [("G", "TimeG", "FG", "e_FG", "GrVFlag"), ("BP", "TimeBP", "FBP", "e_FBP", "BPrVFlag"), ("RP", "TimeRP", "FRP", "e_FRP", "RPrVFlag")]:
    s = d[(d[flag] == 0) & np.isfinite(d[fc]) & np.isfinite(d[tc])]
    t = s[tc].values + 2455197.5; y = s[fc].values / np.median(s[fc]) - 1; e = s[ec].values / np.median(s[fc])
    fr = np.arange(0.5, 50, 0.0005); ls = LombScargle(t, y, e); p = ls.power(fr); k = np.argmax(p)
    X = np.vstack([np.ones_like(t), np.sin(2*np.pi*f1*t), np.cos(2*np.pi*f1*t)]).T; W = 1/e**2
    bb = np.linalg.solve(X.T @ (X*W[:, None]), X.T @ (W*y)); C = np.linalg.inv(X.T @ (X*W[:, None]))
    p1 = ls.power(np.array([f1]))[0]
    null = [LombScargle(t, rng.permutation(y), e).power(np.array([f1]))[0] for _ in range(2000)]
    top5 = fr[np.argsort(p)[::-1]]; peaks = []
    for f in top5:
        if all(abs(f - q) > 0.05 for q in peaks): peaks.append(f)
        if len(peaks) == 5: break
    print(f"{b}: n {len(t)}, span {t.min()-2457000:.1f}-{t.max()-2457000:.1f}; GLS top {fr[k]:.5f} c/d (power {p[k]:.3f}); top-5 peaks {np.round(peaks, 4).tolist()}")
    print(f"    at f1: power {p1:.3f} (permutation p {np.mean(np.array(null) >= p1):.4f}); amp {100*np.hypot(bb[1], bb[2]):.1f} +- {100*np.sqrt((C[1,1]+C[2,2])/2):.1f} %, phase {np.degrees(np.arctan2(bb[2], bb[1])) % 360:.0f} deg; rms {100*np.std(y):.1f} %, median err {100*np.median(e):.1f} %")
