"""ZTF24abfojgu = Gaia DR3 5182404743053707904: the 2024 low-to-high state change in ATLAS forced photometry (2026-09-30).
Cleaning as atlas_outbursts.py. Per filter: median difference flux before MJD 60578 and after MJD 60580 (the ZTF switch date
2024-09-27 = MJD 60580), yearly medians, and the step date as the first night after which the 5-night running median of nightly
medians (o) stays above 50 uJy. Output: atlas_step_abfojgu.txt and atlas_step_abfojgu.png."""
import os, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.time import Time
H = os.path.dirname(os.path.abspath(__file__)); g = "5182404743053707904"; out = []
L = [l for l in open(os.path.join(H, "atlas", g + ".txt")).read().splitlines() if l.strip()]; h = L[0].lstrip("#").split(); R = pd.DataFrame([dict(zip(h, l.split())) for l in L[1:]])
for c in ("MJD", "uJy", "duJy", "err", "chi/N"): R[c] = pd.to_numeric(R[c], errors="coerce")
R = R[(R.err == 0) & (R["chi/N"] < 10) & (R.duJy > 0)]; R = R[R.duJy < 3 * R.duJy.median()]
for f in "oc":
    x = R[R.F == f]
    for lab, s in (("before MJD 60578", x.MJD < 60578), ("after MJD 60580", x.MJD >= 60580)):
        y = x[s]; out.append(f"{f} {lab}: n {len(y)}, median {y.uJy.median():.1f} uJy, error of median {1.25 * y.uJy.std() / np.sqrt(len(y)):.1f}")
    yr = np.floor((x.MJD - 57023) / 365.25) + 2015; out.append(f"{f} yearly medians (uJy): " + str(x.groupby(yr).uJy.median().round(1).to_dict()))
x = R[R.F == "o"]; nm = x.groupby(np.floor(x.MJD)).uJy.median(); rm = nm.rolling(5, center=True).median()
above = rm > 50; idx = [t for i, t in enumerate(rm.index) if above.iloc[i:].mean() > 0.95 and above.iloc[i]]
step = idx[0] if idx else np.nan; out.append(f"o step night (5-night running median stays above 50 uJy): MJD {step:.0f} = {Time(step, format='mjd').iso[:10]}")
last_low = nm[(nm.index < step)].index.max(); out.append(f"last o night before the step: MJD {last_low:.0f} = {Time(last_low, format='mjd').iso[:10]} (nightly median {nm[last_low]:.1f} uJy)")
open(os.path.join(H, "atlas_step_abfojgu.txt"), "w").write("\n".join(out) + "\n"); print("\n".join(out))
fig, ax = plt.subplots(1, 2, figsize=(14, 3.5), gridspec_kw=dict(width_ratios=[2, 1]))
for a in ax:
    for f, c in (("o", "tab:orange"), ("c", "tab:cyan")):
        y = R[R.F == f]; a.errorbar(y.MJD, y.uJy, y.duJy, fmt=".", ms=2, color=c, alpha=0.4, lw=0.3, label=f)
    a.axvline(60580, color="k", ls="--", lw=0.8); a.set_xlabel("MJD"); a.set_ylabel("difference flux (uJy)")
ax[1].set_xlim(60400, 60800); ax[0].legend(); ax[0].set_title("ZTF24abfojgu: ATLAS forced photometry; dashed = ZTF switch 2024-09-27")
plt.tight_layout(); plt.savefig(os.path.join(H, "atlas_step_abfojgu.png"), dpi=80)
