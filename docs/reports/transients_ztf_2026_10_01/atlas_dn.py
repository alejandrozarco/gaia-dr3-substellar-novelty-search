"""ATLAS forced photometry of the new Galactic outburst candidates (2026-09-30): nightly medians (cleaned as atlas_outbursts.py),
the 2026 outburst nights, and earlier outburst nights (> 5 sigma and > 150 uJy above the median) that would show recurrence.
Output: atlas_dn.txt. Usage: python atlas_dn.py <oid> [...]"""
import sys, numpy as np, pandas as pd
out = []
for o in sys.argv[1:]:
    L = [l for l in open(f"atlas/{o}.txt").read().splitlines() if l.strip()]; h = L[0].lstrip("#").split(); R = pd.DataFrame([dict(zip(h, l.split())) for l in L[1:]])
    for c in ("MJD", "uJy", "duJy", "err", "chi/N"): R[c] = pd.to_numeric(R[c], errors="coerce")
    R = R[(R.err == 0) & (R["chi/N"] < 10) & (R.duJy > 0)]; R = R[R.duJy < 3 * R.duJy.median()]; R["night"] = np.floor(R.MJD)
    N = R.groupby(["night", "F"]).agg(uJy=("uJy", "median"), e=("duJy", "median"), n=("uJy", "size")).reset_index(); q = N.uJy.median()
    rec = N[N.night >= 61280]; rec = rec.assign(mag=[f"{23.9 - 2.5 * np.log10(v):.2f}" if v > 3 * e else f">{23.9 - 2.5 * np.log10(3 * e):.2f}" for v, e in zip(rec.uJy, rec.e)])
    old = N[(N.night < 61280) & (N.uJy - q > 5 * N.e) & (N.uJy - q > 150)]
    out.append(f"== {o}: {len(R)} points, {N.night.nunique()} nights, MJD {R.MJD.min():.0f}-{R.MJD.max():.0f}; median {q:.0f} uJy")
    out.append("2026-09 nights: " + "; ".join(f"{int(r.night)} {r.F} {r.mag}" for r in rec.itertuples()))
    out.append(f"earlier outburst nights: {len(old)}" + ("" if not len(old) else " -> " + "; ".join(f"{int(r.night)} {r.F} {r.uJy:.0f}uJy" for r in old.sort_values('night').itertuples())))
open("atlas_dn.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
