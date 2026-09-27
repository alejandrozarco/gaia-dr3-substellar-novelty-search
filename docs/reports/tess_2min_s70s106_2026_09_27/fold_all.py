"""ATLAS attribution for TESS sweep candidates: for every atlas/<gaia>.txt under the given dirs, fold at the star's TESS
frequency (candidates_gated.csv). Cuts duJy>0, chi/N<3, mag5sig>17.5; season medians removed; 5-sigma clip. Reports per band:
top masked LS peak 0.5-72 c/d (0.03 c/d around 1,2,3 c/d and around 27.3-d harmonics ignored via detrend), power/amp at f, 2f, f/2."""
import sys, os, glob, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from astropy.timeseries import LombScargle
C = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "candidates_gated.csv"), dtype={"gaia": str}).set_index("gaia")
for d in sys.argv[1:]:
    for p in sorted(glob.glob(os.path.join(d, "atlas", "*.txt"))):
        gid = os.path.basename(p)[:-4]
        if gid not in C.index: continue
        r = C.loc[gid]; F0 = float(r.f)
        x = pd.read_csv(p, sep=r"\s+"); x.columns = [c.lstrip("#") for c in x.columns]
        x = x[(x.duJy > 0) & (x["chi/N"] < 3) & (x.mag5sig > 17.5)].copy(); x["y"] = np.nan
        for b in "co":
            m = x.F == b; t = x.MJD[m].values; br = np.r_[0, np.where(np.diff(t) > 60)[0] + 1, m.sum()]; idx = x.index[m]
            for a, e in zip(br[:-1], br[1:]):
                ii = idx[a:e]; x.loc[ii, "y"] = x.loc[ii, "uJy"] - x.loc[ii, "uJy"].median()
            s = 1.4826 * np.median(np.abs(x.loc[m, "y"])); x.loc[m & (np.abs(x.y) > 5 * s), "y"] = np.nan
        x = x[np.isfinite(x.y)]; FR = np.linspace(0.5, 72, 500000)
        print(f"===== {gid} {r.WDJname} G {r.G} TESS P {r.P_min:.2f} min (f {F0:.5f}), amp {r.amp} crowd {r.crowdsap} tier {r.tier}")
        for b in "co":
            v = x[x.F == b]; t, y, e = v.MJD.values, v.y.values, v.duJy.values
            if len(t) < 100: print(f"  {b}: only {len(t)} points"); continue
            ls = LombScargle(t, y, e); pw = ls.power(FR); mask = np.ones_like(FR, bool)
            for n in (1, 2, 3): mask &= np.abs(FR - n) > 0.03
            k = np.argmax(np.where(mask, pw, 0))
            out = [f"top {FR[k]:.5f} (P {1440/FR[k]:.2f} min) FAP {ls.false_alarm_probability(pw[k], minimum_frequency=0.5, maximum_frequency=72):.2g}"]
            for lab, fq in (("f", F0), ("2f", 2 * F0), ("f/2", F0 / 2)):
                w = np.abs(FR - fq) < 0.01
                if not w.any(): continue
                kk = np.argmax(pw * w); X = np.vstack([np.sin(2 * np.pi * FR[kk] * t), np.cos(2 * np.pi * FR[kk] * t), np.ones_like(t)]).T
                c2 = np.linalg.lstsq(X / e[:, None], y / e, rcond=None)[0]; cov = np.linalg.inv((X / e[:, None]).T @ (X / e[:, None]))
                out.append(f"{lab}: FAP {ls.false_alarm_probability(pw[kk], minimum_frequency=0.5, maximum_frequency=72):.2g} amp {np.hypot(c2[0], c2[1]):.1f}+-{np.sqrt((cov[0,0]+cov[1,1])/2):.1f} uJy")
            print(f"  {b}: n {len(t)}; " + "; ".join(out))
