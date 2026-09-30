"""Outbursts of the dwarf-nova candidates in ATLAS forced photometry (2026-09-30).
Input: atlas/<gaia>.txt (fallingstar-data.com forced photometry on difference images, MJD >= 57000). Cleaning: err 0, chi/N < 10,
duJy > 0, duJy < 3x median. Flux in uJy (difference flux: quiescence sits near 0). An outburst point has flux above the median by
more than 10 sigma and more than 300 uJy (AB 17.7 mag); points are grouped into episodes separated by more than 10 d without an
outburst point. Peak AB magnitude = 23.9 - 2.5 log10(peak uJy) (difference flux, so a lower limit on the brightness change).
Output: atlas_outbursts.csv (episodes), atlas_<gaia>.png (light curve). Usage: python atlas_outbursts.py [gaia ...] (default: all files)."""
import os, sys, glob, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.time import Time
H = os.path.dirname(os.path.abspath(__file__))
ids = sys.argv[1:] or [os.path.basename(f)[:-4] for f in sorted(glob.glob(os.path.join(H, "atlas", "*.txt")))]
rows = []
for g in ids:
    L = [l for l in open(os.path.join(H, "atlas", g + ".txt")).read().splitlines() if l.strip()]; h = L[0].lstrip("#").split()
    R = pd.DataFrame([dict(zip(h, l.split())) for l in L[1:]])
    for c in ("MJD", "uJy", "duJy", "err", "chi/N"): R[c] = pd.to_numeric(R[c], errors="coerce")
    R = R[(R.err == 0) & (R["chi/N"] < 10) & (R.duJy > 0)]; R = R[R.duJy < 3 * R.duJy.median()].sort_values("MJD")
    q = R.uJy.median(); ob = R[(R.uJy - q > 10 * R.duJy) & (R.uJy - q > 300)]; ep = []
    for t in ob.MJD:
        if ep and t - ep[-1][1] <= 10: ep[-1][1] = t
        else: ep.append([t, t])
    for a, b in ep:
        x = ob[(ob.MJD >= a) & (ob.MJD <= b)]; pk = x.loc[x.uJy.idxmax()]
        rows.append(dict(gaia=g, start=Time(a, format="mjd").iso[:10], mjd_start=round(a, 2), mjd_end=round(b, 2), n_points=len(x), n_nights=int(np.floor(x.MJD).nunique()),
                         peak_uJy=round(pk.uJy), peak_mag=round(23.9 - 2.5 * np.log10(pk.uJy), 2), peak_filter=pk.F, filters="".join(sorted(set(x.F)))))
    print(g, "points", len(R), "MJD %.0f-%.0f" % (R.MJD.min(), R.MJD.max()), "median %.0f uJy, err %.0f; episodes %d" % (q, R.duJy.median(), len(ep)), flush=True)
    fig, ax = plt.subplots(figsize=(12, 3.5))
    for f, c in (("o", "tab:orange"), ("c", "tab:cyan")):
        x = R[R.F == f]; ax.errorbar(x.MJD, x.uJy, x.duJy, fmt=".", ms=2, color=c, alpha=0.5, lw=0.3, label=f)
    for a, b in ep: ax.axvspan(a - 1, b + 1, color="r", alpha=0.15)
    ax.set_xlabel("MJD"); ax.set_ylabel("difference flux (uJy)"); ax.set_title(f"Gaia DR3 {g}: ATLAS forced photometry, {len(ep)} outburst episodes"); ax.legend()
    plt.tight_layout(); plt.savefig(os.path.join(H, f"atlas_{g}.png"), dpi=80); plt.close()
E = pd.DataFrame(rows); fn = os.path.join(H, "atlas_outbursts.csv")
if os.path.exists(fn): old = pd.read_csv(fn, dtype={"gaia": str}); E = pd.concat([old[~old.gaia.isin(ids)], E])
E.to_csv(fn, index=False); print(E[E.gaia.isin(ids)].to_string(index=False))
