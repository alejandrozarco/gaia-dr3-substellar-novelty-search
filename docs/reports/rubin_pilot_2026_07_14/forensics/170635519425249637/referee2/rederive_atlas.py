#!/usr/bin/env python
"""Referee stage-3: independent re-derivation of ATLAS nightly stacks from raw parsed file.
Own code, not reusing stage-1/2 scripts. All comparisons keyed by MJD with asserts."""
import pandas as pd, numpy as np, sys

RAW = "/tmp/rubin_pilot/forensics/170635519425249637/atlas_fp_parsed.csv"
df = pd.read_csv(RAW)
print("raw epochs:", len(df), "MJD range:", df.MJD.min(), df.MJD.max())

# Claimed quality cuts: chi/N < 10, err flag 0, 0 < duJy < 100
q = df[(df["chi/N"] < 10) & (df["err"] == 0) & (df["duJy"] > 0) & (df["duJy"] < 100)].copy()
print("after cuts:", len(q))

# nightly stacks per band: group by floor(MJD) x filter, n>=2, inverse-variance weighted
q["night"] = np.floor(q["MJD"]).astype(int)
rows = []
for (night, band), g in q.groupby(["night", "F"]):
    if len(g) < 2:
        continue
    w = 1.0 / g["duJy"] ** 2
    flux = np.sum(w * g["uJy"]) / np.sum(w)
    err = np.sqrt(1.0 / np.sum(w))
    mjd = np.sum(w * g["MJD"]) / np.sum(w)
    rows.append(dict(mjd=mjd, band=band, n=len(g), flux=flux, err=err, snr=flux / err))
st = pd.DataFrame(rows).sort_values("mjd").reset_index(drop=True)
print("nightly stacks (n>=2):", len(st))
snr = st["snr"]
print(f"SNR dist: mean={snr.mean():.3f} sigma={snr.std():.3f}")
hi = st[st.snr > 4]
print("stacks with SNR>4:")
for _, r in hi.iterrows():
    mag = 23.9 - 2.5 * np.log10(r["flux"])
    magerr = 2.5 / np.log(10) * r["err"] / r["flux"]
    print(f"  MJD {r['mjd']:.3f} {r['band']} n={r['n']} flux={r['flux']:.1f}+-{r['err']:.1f} uJy SNR={r['snr']:.2f} mAB={mag:.2f}+-{magerr:.2f}")

# MJD-keyed asserts against the claimed anchor rows
def get(mjd, band, tol=0.01):
    m = st[(np.abs(st.mjd - mjd) < tol) & (st.band == band)]
    assert len(m) == 1, f"anchor not found: {mjd} {band} -> {len(m)} rows"
    return m.iloc[0]

a = get(61213.279, "o"); assert abs(a.flux - 22.8) < 1.0 and abs(a.snr - 5.8) < 0.15, a
b = get(61214.285, "o"); assert abs(a.snr) > 4
b = get(61214.285, "o"); assert abs(b.flux - 29.8) < 1.0 and abs(b.snr - 5.4) < 0.15, b
# claim: ONLY these 2 nights >4 sigma, both pre-Rubin (first Rubin alert 61228.3877)
assert len(hi) == 2, f"expected 2 stacks >4sig, got {len(hi)}"
assert (hi.mjd < 61228.39).all(), "some >4sig stack is NOT pre-Rubin"
# Rubin-epoch ATLAS consistency claim: 7-11 uJy at 0.5-1.5 sigma at 61228-61235
late = st[(st.mjd > 61227) & (st.mjd < 61236) & (st.band == "o")]
print("\nATLAS o stacks during Rubin window:")
print(late[["mjd", "band", "n", "flux", "err", "snr"]].to_string(index=False))
# historical spikes claim: check single exposures >5sig before 61200
raw_hi = df[(df.MJD < 61200) & (df.uJy / df.duJy > 5) & (df.duJy > 0)]
print("\nraw single-exposure SNR>5 pre-61200 (claimed artifacts/movers):", len(raw_hi))
print(raw_hi[["MJD", "m", "uJy", "duJy", "chi/N", "F", "snr"]].head(15).to_string(index=False))
print("\nALL ATLAS ASSERTS PASSED")
