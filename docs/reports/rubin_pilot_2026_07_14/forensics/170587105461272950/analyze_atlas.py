#!/usr/bin/env python
"""Analyze ATLAS forced photometry for 170587105461272950.
- Precursor search: any >5-sigma flux excursions before MJD 61217 (nightly-binned)?
- Current-event detection: nightly-binned flux at MJD 61217-61236.
All rows keyed by MJD; asserts on time-axis sanity.
"""
import io, math
import pandas as pd
import numpy as np

D = "/tmp/rubin_pilot/forensics/170587105461272950"
raw = open(f"{D}/atlas_fp.txt").read()
# ATLAS FP output: '###MJD m dm uJy duJy F err chi/N RA Dec x y maj min phi apfit mag5sig Sky Obs'
lines = [l for l in raw.splitlines() if l.strip()]
hdr = [l for l in lines if l.startswith("###")][0].lstrip("#").split()
rows = [l.split() for l in lines if not l.startswith("#")]
df = pd.DataFrame(rows, columns=hdr)
for c in ["MJD","uJy","duJy","mag5sig","m","dm","chi/N"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df = df.dropna(subset=["MJD","uJy","duJy"])
assert (df.MJD > 55000).all() and (df.MJD < 61300).all(), "MJD out of range"
df = df.sort_values("MJD").reset_index(drop=True)
print(f"epochs: {len(df)}  MJD {df.MJD.min():.2f} - {df.MJD.max():.2f}  filters: {sorted(df.F.unique())}")
df.to_csv(f"{D}/atlas_fp_clean.csv", index=False)

# quality cut: |uJy|<1e5, duJy<4000, chi/N<10
q = df[(df.duJy < 4000) & (df["chi/N"] < 10)].copy()
print(f"after QC: {len(q)}")

# nightly bins per filter, inverse-variance weighted
q["night"] = np.floor(q.MJD + 0.5)
out = []
for (n, f), g in q.groupby(["night", "F"]):
    w = 1.0 / g.duJy**2
    fl = float((g.uJy * w).sum() / w.sum()); er = float(np.sqrt(1.0 / w.sum()))
    out.append(dict(night_mjd=n, filt=f, n=len(g), flux_uJy=round(fl,2),
                    err_uJy=round(er,2), snr=round(fl/er,2),
                    mjd_mean=round(float(g.MJD.mean()),4)))
nb = pd.DataFrame(out).sort_values(["night_mjd","filt"]).reset_index(drop=True)
nb.to_csv(f"{D}/atlas_nightly.csv", index=False)

pre = nb[nb.night_mjd < 61217]
post = nb[nb.night_mjd >= 61217]
print(f"\nPRE-EVENT nights (<61217): {len(pre)}; span {pre.night_mjd.min():.0f}-{pre.night_mjd.max():.0f}" if len(pre) else "no pre nights")
exc = pre[pre.snr.abs() >= 5]
print(f"pre-event |SNR|>=5 nights: {len(exc)}")
if len(exc): print(exc.to_string())
exc3 = pre[pre.snr >= 3]
print(f"pre-event SNR>=+3 nights: {len(exc3)} ({100*len(exc3)/max(len(pre),1):.1f}% — expect ~0.1% Gaussian)")
if len(exc3): print(exc3.sort_values("snr", ascending=False).head(15).to_string())
# typical nightly depth
if len(pre):
    med = float(pre.err_uJy.median())
    print(f"median nightly 1-sigma {med:.1f} uJy -> 5-sig limit ~ {(-2.5*math.log10(5*med*1e-6/3631)):.2f} AB")
print("\nEVENT WINDOW nights (>=61217):")
if len(post): print(post.to_string())
