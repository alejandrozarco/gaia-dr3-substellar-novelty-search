#!/usr/bin/env python
"""Adversarial referee: independent re-derivation of ZFPS + ATLAS nightly stacks.
All groupings keyed by explicit MJD; asserts on epoch ranges. No positional alignment."""
import numpy as np, pandas as pd, io, sys

base = "/tmp/rubin_pilot/forensics/170635519425249637/"

# ---------------- ZFPS ----------------
rows = []
cols = None
with open(base + "zfps_req479165_lc.txt") as f:
    for line in f:
        if line.startswith("# Order of columns below:"):
            cols = next(f).strip().lstrip("#").split(",")
            cols = [c.strip() for c in cols]
            continue
        if line.startswith("#") or not line.strip():
            continue
        rows.append(line.split())
# last header line handling: columns line read via next(); data lines are space-separated
df = pd.DataFrame(rows)
# re-read properly: the file has the column list line then data
with open(base + "zfps_req479165_lc.txt") as f:
    txt = f.read()
lines = txt.splitlines()
colline = None
data_start = None
for i, l in enumerate(lines):
    if l.strip().startswith("index, field"):
        colline = l
        data_start = i + 2  # skip the '#' line after
        break
cols = [c.strip() for c in colline.split(",")]
data = "\n".join(lines[data_start:])
z = pd.read_csv(io.StringIO(data), sep=r"\s+", names=cols, na_values=["null"])
print("ZFPS raw epochs:", len(z))
z["mjd"] = z["jd"] - 2400000.5
assert z["mjd"].min() > 58000 and z["mjd"].max() < 61236, (z["mjd"].min(), z["mjd"].max())
print("ZFPS mjd range: %.2f - %.2f" % (z["mjd"].min(), z["mjd"].max()))
# quality cuts (as claimed): infobitssci=0, scisigpix<25, seeing<4
zq = z[(z["infobitssci"] == 0) & (z["scisigpix"] < 25) & (z["sciinpseeing"] < 4.0)
       & (z["diffimgstatus"] == 1) & z["forcediffimflux"].notna()].copy()
print("ZFPS after quality cuts:", len(zq))
# flux to uJy via zpdiff: m_AB = zpdiff - 2.5 log10(DN); uJy: f = 10^(-0.4*(m-23.9))
zq["fluxuJy"] = zq["forcediffimflux"] * 10 ** (-0.4 * (zq["zpdiff"] - 23.9))
zq["dfluxuJy"] = zq["forcediffimfluxunc"] * 10 ** (-0.4 * (zq["zpdiff"] - 23.9))
# nightly IVW stacks per band, keyed by int(mjd)
zq["night"] = np.floor(zq["mjd"]).astype(int)
recs = []
for (night, band), g in zq.groupby(["night", "filter"]):
    w = 1.0 / g["dfluxuJy"] ** 2
    f = np.sum(w * g["fluxuJy"]) / np.sum(w)
    ef = 1.0 / np.sqrt(np.sum(w))
    mjd_mean = np.sum(w * g["mjd"]) / np.sum(w)
    assert abs(mjd_mean - night) < 1.0
    recs.append(dict(mjd=mjd_mean, night=night, band=band, n=len(g), flux=f, err=ef, snr=f / ef))
zs = pd.DataFrame(recs).sort_values("mjd")
print("ZFPS nightly stacks:", len(zs))
snr = zs["snr"].values
print("ZFPS stack SNR mean=%.3f sigma=%.3f" % (snr.mean(), snr.std()))
hits = zs[zs["snr"] > 4].sort_values("mjd")
print("\nZFPS stacks with SNR>4: %d" % len(hits))
for _, r in hits.iterrows():
    mag = 23.9 - 2.5 * np.log10(r["flux"])
    print("  MJD %.3f %s n=%d flux=%.1f+-%.1f uJy SNR=%.1f mag=%.2f" %
          (r["mjd"], r["band"], r["n"], r["flux"], r["err"], r["snr"], mag))
pre = zs[zs["mjd"] < 61200]
print("Historical (<61200) stacks: %d ; >4sig: %d ; max SNR %.2f" %
      (len(pre), (pre["snr"] > 4).sum(), pre["snr"].max()))
# the 61201.41 r non-detection
nd = zs[(zs["night"] == 61201) & (zs["band"] == "ZTF_r")]
if len(nd):
    r = nd.iloc[0]
    lim = 23.9 - 2.5 * np.log10(3 * r["err"])
    print("MJD 61201 r stack: flux=%.1f+-%.1f SNR=%.2f  3sig limit mag=%.2f" %
          (r["flux"], r["err"], r["snr"], lim))
# per-band recent fluxes vs Rubin r for cross-survey consistency
rec = zs[(zs["mjd"] > 61225) & (zs["band"] == "ZTF_r")]
print("\nZTF r stacks MJD>61225 (compare Rubin r=10.7 uJy at 61232.3):")
print(rec[["mjd", "n", "flux", "err", "snr"]].to_string(index=False))
# also per-exposure detail for night 61231
n1 = zq[(zq["night"] == 61231)][["mjd", "filter", "fluxuJy", "dfluxuJy", "forcediffimchisq"]]
print("\nZFPS single exposures night 61231:")
print(n1.to_string(index=False))

zs.to_csv(base + "referee3/zfps_stacks_referee.csv", index=False)

# ---------------- ATLAS ----------------
a = pd.read_csv(base + "atlas_fp.txt", sep=r"\s+", escapechar=None, comment=None, skiprows=0)
a.columns = [c.replace("###", "") for c in a.columns]
print("\nATLAS raw epochs:", len(a))
assert a["MJD"].min() > 57000 and a["MJD"].max() < 61236
aq = a[(a["chi/N"] < 10) & (a["err"] == 0) & (a["duJy"] > 0) & (a["duJy"] < 100)].copy()
print("ATLAS after cuts:", len(aq))
aq["night"] = np.floor(aq["MJD"]).astype(int)
recs = []
for (night, band), g in aq.groupby(["night", "F"]):
    if len(g) < 2:
        continue
    w = 1.0 / g["duJy"] ** 2
    f = np.sum(w * g["uJy"]) / np.sum(w)
    ef = 1.0 / np.sqrt(np.sum(w))
    mjd_mean = np.sum(w * g["MJD"]) / np.sum(w)
    assert abs(mjd_mean - night) < 1.0
    recs.append(dict(mjd=mjd_mean, night=night, band=band, n=len(g), flux=f, err=ef, snr=f / ef))
ast = pd.DataFrame(recs).sort_values("mjd")
print("ATLAS nightly stacks (n>=2):", len(ast))
snr = ast["snr"].values
print("ATLAS stack SNR mean=%.3f sigma=%.3f" % (snr.mean(), snr.std()))
hits = ast[ast["snr"] > 4]
print("ATLAS stacks SNR>4: %d" % len(hits))
for _, r in hits.iterrows():
    mag = 23.9 - 2.5 * np.log10(r["flux"] / 1e0) + 0  # uJy->AB
    mag = 23.9 - 2.5 * np.log10(r["flux"])
    print("  MJD %.3f %s n=%d flux=%.1f+-%.1f uJy SNR=%.2f mag=%.2f" %
          (r["mjd"], r["band"], r["n"], r["flux"], r["err"], r["snr"], mag))
# event window stacks 61210-61218
ev = ast[(ast["mjd"] > 61209) & (ast["mjd"] < 61219)]
print("\nATLAS stacks 61209-61219:")
print(ev[["mjd", "band", "n", "flux", "err", "snr"]].to_string(index=False))
ast.to_csv(base + "referee3/atlas_stacks_referee.csv", index=False)
