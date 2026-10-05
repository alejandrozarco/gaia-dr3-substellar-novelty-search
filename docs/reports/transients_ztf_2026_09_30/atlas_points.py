"""ATLAS confirmation points for the TNS reports (2026-09-30): per object, nightly inverse-variance mean difference flux of the
2026-09 outburst nights with S/N > 5 (cleaned as atlas_dn.py), mean exposure time (UT), AB magnitude and error, filter, telescope
(obs code prefix). Output: atlas_points.txt."""
import numpy as np, pandas as pd
from astropy.time import Time
out = []
for o in ("ZTF26absimmf", "ZTF26abwacec", "ZTF26abtpoev", "ZTF26abwqsgt", "ZTF26abtoqyd"):
    L = [l for l in open(f"atlas/{o}.txt").read().splitlines() if l.strip()]; h = L[0].lstrip("#").split(); R = pd.DataFrame([dict(zip(h, l.split())) for l in L[1:]])
    for c in ("MJD", "uJy", "duJy", "err", "chi/N"): R[c] = pd.to_numeric(R[c], errors="coerce")
    R = R[(R.err == 0) & (R["chi/N"] < 10) & (R.duJy > 0)]; R = R[(R.duJy < 3 * R.duJy.median()) & (R.MJD > 61280)]; R["night"] = np.floor(R.MJD)
    for (n, f), x in R.groupby(["night", "F"]):
        w = 1 / x.duJy**2; fl = (w * x.uJy).sum() / w.sum(); e = 1 / np.sqrt(w.sum())
        if fl / e > 5:
            m = 23.9 - 2.5 * np.log10(fl); em = 1.0857 * e / fl; tel = x.Obs.iloc[0][:3]
            out.append(f"{o} {Time(x.MJD.mean(), format='mjd').iso[:19]} ATLAS-{f} {m:.2f} {em:.2f} n={len(x)} unit={tel}")
open("atlas_points.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
