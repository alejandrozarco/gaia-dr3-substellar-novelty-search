"""Comparison-star test of the 2015-2016 negative ATLAS difference flux of the fader (2026-09-30). Three field stars of similar
G (15.8-16.0) and colour (BP-RP 1.33-1.40) within 1.7 arcmin (atlas_comparison/<gaia>.txt), cleaned as atlas_fader.py.
Per star and filter: yearly median difference flux, and the 2015 and 2016 medians expressed in units of the star's own
2017-2023 nightly scatter. Output: atlas_comparison.txt."""
import os, glob, numpy as np, pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); out = []
files = sorted(glob.glob(os.path.join(H, "atlas_comparison", "*.txt"))) + [os.path.join(H, "atlas", "4104182344862107904.txt")]
for fn in files:
    g = os.path.basename(fn)[:-4]; L = [l for l in open(fn).read().splitlines() if l.strip()]; h = L[0].lstrip("#").split(); R = pd.DataFrame([dict(zip(h, l.split())) for l in L[1:]])
    for c in ("MJD", "uJy", "duJy", "err", "chi/N"): R[c] = pd.to_numeric(R[c], errors="coerce")
    R = R[(R.err == 0) & (R["chi/N"] < 10) & (R.duJy > 0)]; R = R[R.duJy < 3 * R.duJy.median()]; R["night"] = np.floor(R.MJD)
    for f in "oc":
        x = R[R.F == f]; n = x.groupby("night").uJy.median(); yr = np.floor((n.index - 57023) / 365.25) + 2015
        ref = n[(yr >= 2017) & (yr <= 2023)]; sc = 1.4826 * np.median(np.abs(ref - ref.median()))
        ym = n.groupby(yr).median()
        out.append(f"{g}{' (fader)' if g.startswith('41041823448621079') else ''} {f}: 2015 {ym.get(2015.0, np.nan):.0f}, 2016 {ym.get(2016.0, np.nan):.0f} uJy; 2017-2023 nightly scatter {sc:.0f}; 2015/2016 in scatter units {ym.get(2015.0, np.nan) / sc:.1f} / {ym.get(2016.0, np.nan) / sc:.1f}")
open(os.path.join(H, "atlas_comparison.txt"), "w").write("\n".join(out) + "\n"); print("\n".join(out))
