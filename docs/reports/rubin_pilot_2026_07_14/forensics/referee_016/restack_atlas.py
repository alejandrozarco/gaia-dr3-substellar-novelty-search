#!/usr/bin/env python
"""Referee: independent nightly inverse-variance re-stack of ATLAS FP raw file.
MJD-keyed; verifies claimed pre-discovery detections and historical spike adjudication."""
import numpy as np
import pandas as pd

RAW = "/tmp/rubin_pilot/forensics/170591519677875016/atlas_fp_raw.txt"
rows = []
with open(RAW) as f:
    hdr = f.readline()
    for line in f:
        p = line.split()
        if len(p) < 19:
            continue
        rows.append(dict(mjd=float(p[0]), m=float(p[1]), dm=float(p[2]),
                         uJy=float(p[3]), duJy=float(p[4]), F=p[5], err=p[6],
                         chiN=float(p[7]), ra=float(p[8]), dec=float(p[9]),
                         mag5sig=float(p[16]), obs=p[18]))
df = pd.DataFrame(rows)
print("n exposures:", len(df), "MJD range:", df.mjd.min(), df.mjd.max())
print("bands:", df.F.value_counts().to_dict())
# quality cut: finite errs, duJy>0, chi/N sane, err flag 0
g = df[(df.duJy > 0) & (df.duJy < 3000) & (df.err == "0") & (df.chiN < 100)].copy()
print("after cuts:", len(g))
g["night"] = np.floor(g.mjd)  # Hawaii/Chile night stays within one integer MJD at this RA

def stack(sub):
    w = 1.0 / sub.duJy**2
    f = np.sum(w * sub.uJy) / np.sum(w)
    e = 1.0 / np.sqrt(np.sum(w))
    return f, e, len(sub), sub.mjd.mean()

res = []
for (night, band), sub in g.groupby(["night", "F"]):
    f, e, n, mjdm = stack(sub)
    res.append(dict(night=night, band=band, mjd=mjdm, flux=f, err=e, n=n, snr=f / e))
st = pd.DataFrame(res).sort_values("mjd")
st.to_csv("/tmp/rubin_pilot/forensics/referee_016/ref_atlas_stacks.csv", index=False)

def ab(f):
    return -2.5 * np.log10(f * 1e-6 / 3631)

# CLAIMS keyed by approx stack MJD (band, flux uJy, snr)
claims = [
    (61202.53, "o", 36.6, 5.1),
    (61207.51, "c", 38.1, 6.8),
    (61208.57, "c", 33.1, 6.8),
    (61214.48, "c", 28.2, 5.3),
]
print("\n-- claimed pre-discovery stacks --")
for mjd_c, band_c, f_c, snr_c in claims:
    m = st[(np.abs(st.mjd - mjd_c) < 0.3) & (st.band == band_c)]
    assert len(m) == 1, f"claim {mjd_c} {band_c}: {len(m)} stacks"
    r = m.iloc[0]
    print(f"claim MJD~{mjd_c} {band_c}: my stack mjd={r.mjd:.3f} flux={r.flux:.1f}+/-{r.err:.1f} "
          f"snr={r.snr:.1f} n={r.n} mag={ab(r.flux):.2f} | claimed {f_c} uJy snr {snr_c}")

# event window overview 61190-61235
print("\n-- all stacks 61190-61235 --")
ev = st[(st.mjd > 61190) & (st.mjd < 61235)]
for _, r in ev.iterrows():
    mag = ab(r.flux) if r.flux > 0 else np.nan
    print(f"{r.mjd:10.3f} {r.band} n={int(r.n):2d} {r.flux:7.1f}+/-{r.err:5.1f} snr={r.snr:5.1f} mag={mag:5.2f}")

# historical significance scan (before 61150): any stationary stack snr>=5?
hist = st[st.mjd < 61150]
hi = hist[hist.snr >= 5]
print(f"\n-- historical stacks snr>=5 (n={len(hi)}) --")
print(hi.to_string() if len(hi) else "(none)")
# also snr>=4
h4 = hist[hist.snr >= 4]
print(f"historical snr>=4 count: {len(h4)}")
print(h4.to_string() if len(h4) else "")

# check the two claimed historical single-exposure spikes in raw data
print("\n-- raw exposures around claimed spikes --")
for lo, hi_ in [(59024.45, 59024.52), (57955.45, 57955.52)]:
    sub = df[(df.mjd > lo) & (df.mjd < hi_)]
    print(sub[["mjd", "uJy", "duJy", "F", "chiN", "obs"]].to_string())

# per-exposure consistency on the claimed event nights: flux positive in each exposure?
print("\n-- per-exposure fluxes on claimed nights --")
for mjd_c, band_c, _, _ in claims:
    sub = g[(np.abs(g.mjd - mjd_c) < 0.3) & (g.F == band_c)]
    frac_pos = (sub.uJy > 0).mean()
    units = set(o[:3] for o in sub.obs)
    print(f"{mjd_c} {band_c}: n={len(sub)} frac_flux_positive={frac_pos:.2f} units={units} "
          f"fluxes={list(np.round(sub.uJy.values,1))}")

# median nightly 3-sigma limits per band (all nights)
for band in ["o", "c"]:
    b = st[st.band == band]
    lim = ab(3 * b.err.median())
    print(f"median nightly-stack 3sig limit {band}: {lim:.2f} (claimed o~20.2/c~20.7)")
print("DONE")
