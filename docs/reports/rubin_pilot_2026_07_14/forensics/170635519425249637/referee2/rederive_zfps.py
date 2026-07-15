#!/usr/bin/env python
"""Referee stage-3: independent re-derivation of ZFPS nightly stacks from raw lightcurve file."""
import pandas as pd, numpy as np, io, re

RAW = "/tmp/rubin_pilot/forensics/170635519425249637/zfps_req479165_lc.txt"
hdr = None
lines = []
for l in open(RAW):
    if l.lstrip().startswith("index,") and "forcediffimflux" in l:
        hdr = [c.strip() for c in l.strip().split(",")]
        continue
    if l.startswith("#") or not l.strip():
        continue
    lines.append(l)
assert hdr, "no header found"
df = pd.read_csv(io.StringIO("".join(lines)), sep=r"\s+", names=hdr, na_values=["null"])
print("raw epochs:", len(df))
df["mjd"] = df["jd"] - 2400000.5
print("MJD range:", df.mjd.min(), df.mjd.max())

# claimed cuts: infobitssci=0, scisigpix<25, seeing<4"
q = df[(df.infobitssci == 0) & (df.scisigpix < 25) & (df.sciinpseeing < 4.0)
       & df.forcediffimflux.notna() & (df.diffimgstatus == 1)].copy()
print("after cuts:", len(q))
# flux DN -> uJy via zpdiff: f_uJy = flux * 10^(-0.4*(zpdiff-23.9))
q["f_uJy"] = q.forcediffimflux * 10 ** (-0.4 * (q.zpdiff - 23.9))
q["ef_uJy"] = q.forcediffimfluxunc * 10 ** (-0.4 * (q.zpdiff - 23.9))
q["night"] = np.floor(q.mjd).astype(int)

rows = []
for (night, band), g in q.groupby(["night", "filter"]):
    w = 1.0 / g.ef_uJy ** 2
    flux = np.sum(w * g.f_uJy) / np.sum(w)
    err = np.sqrt(1.0 / np.sum(w))
    mjd = np.sum(w * g.mjd) / np.sum(w)
    rows.append(dict(mjd=mjd, band=band, n=len(g), flux=flux, err=err, snr=flux / err))
st = pd.DataFrame(rows).sort_values("mjd").reset_index(drop=True)
print("nightly stacks:", len(st))
hi = st[st.snr > 4]
print(f"\nstacks SNR>4: {len(hi)}")
for _, r in hi.iterrows():
    mag = 23.9 - 2.5 * np.log10(r.flux)
    print(f"  MJD {r.mjd:.3f} {r.band} n={r.n} flux={r.flux:.1f}+-{r.err:.1f} SNR={r.snr:.2f} mAB={mag:.2f}")

# CLAIMS (MJD-keyed asserts):
assert (hi.mjd >= 61206).all() and (hi.mjd <= 61232).all(), "SNR>4 stack outside claimed window!"
pre = st[st.mjd < 61200]
print(f"\nhistorical stacks (<61200): {len(pre)}, max SNR = {pre.snr.max():.2f} at MJD {pre.loc[pre.snr.idxmax(),'mjd']:.3f}")
assert (pre.snr < 4).all(), "historical >4sig stack exists!"

def get(mjd, band, tol=0.02):
    m = st[(np.abs(st.mjd - mjd) < tol) & (st.band == band)]
    assert len(m) == 1, f"anchor missing {mjd} {band}: {len(m)}"
    return m.iloc[0]

for mjd, band, f_c, snr_c in [(61206.455,"ZTF_g",16.2,4.5),(61206.461,"ZTF_r",16.9,4.9),
        (61210.462,"ZTF_r",19.3,6.3),(61214.455,"ZTF_r",18.7,6.4),(61231.415,"ZTF_r",19.9,5.8),
        (61231.458,"ZTF_g",13.2,4.4),(61209.456,"ZTF_i",30.8,4.2)]:
    r = get(mjd, band)
    assert abs(r.flux - f_c) < 1.5 and abs(r.snr - snr_c) < 0.3, (mjd, band, r.flux, r.snr, "claimed", f_c, snr_c)
    print(f"anchor OK: {mjd} {band} flux {r.flux:.1f} snr {r.snr:.2f} (claimed {f_c},{snr_c})")

# last non-detection claim: MJD 61201.413 r, 3-sig limit 21.1
nd = st[(np.abs(st.mjd - 61201.413) < 0.05) & (st.band == "ZTF_r")]
print("\nnon-detection night 61201:", nd.to_string(index=False))
if len(nd) == 1:
    lim = 23.9 - 2.5 * np.log10(3 * nd.iloc[0].err)
    print(f"  3-sigma limit = {lim:.2f} AB (claimed 21.1); flux SNR = {nd.iloc[0].snr:.2f}")
# marginal 61203-61205 claim
mar = st[(st.mjd > 61202) & (st.mjd < 61206)]
print("\n61203-61205 stacks:\n", mar.to_string(index=False))
# plateau claim: r-band 61206-61231 range 20.65-20.99
rp = st[(st.band == "ZTF_r") & (st.mjd > 61205) & (st.mjd < 61232) & (st.snr > 4)]
mags = 23.9 - 2.5 * np.log10(rp.flux)
print(f"\nr plateau mags: {mags.min():.2f} - {mags.max():.2f} over MJD {rp.mjd.min():.1f}-{rp.mjd.max():.1f}")
# check all r stacks in window incl <4sig ones for consistency (any deep dips?)
rall = st[(st.band == "ZTF_r") & (st.mjd > 61205) & (st.mjd < 61232)]
print("all r stacks in window:\n", rall.assign(mag=23.9-2.5*np.log10(rall.flux.clip(0.01)))[["mjd","n","flux","err","snr","mag"]].to_string(index=False))
print("\nALL ZFPS ASSERTS PASSED")
