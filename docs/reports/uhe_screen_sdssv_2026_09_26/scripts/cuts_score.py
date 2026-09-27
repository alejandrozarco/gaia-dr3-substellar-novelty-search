"""Re-score the stored region cuts: EW at 5280 and 6198 A (Reindl+2021 positions; window +-12 A, side bands 3-30 A beyond),
empirical noise from control positions 5330 and 6250 A measured the same way, per S/N bin."""
import os, glob, numpy as np, pandas as pd
U = os.path.dirname(os.path.abspath(__file__))
def ew(w, f, iv, l, hw=12):
    m = (((w > l - hw - 30) & (w < l - hw - 3)) | ((w > l + hw + 3) & (w < l + hw + 30))) & (iv > 0) & np.isfinite(f); k = (np.abs(w - l) < hw) & (iv > 0) & np.isfinite(f)
    if m.sum() < 8 or k.sum() < 8: return np.nan
    p = np.polyfit(w[m], f[m], 1, w=np.sqrt(iv[m])); c = np.polyval(p, w); return float(np.sum((1 - f[k] / c[k]) * np.gradient(w)[k]))
rows = []
for p in glob.glob(f"{U}/cuts/*.npz"):
    d = np.load(p); w, f, iv = d["w"], d["f"], d["iv"]
    rows.append(dict(sdss_id=os.path.basename(p)[:-4], e5280=ew(w, f, iv, 5280), e6198=ew(w, f, iv, 6198), c5330=ew(w, f, iv, 5345), c6250=ew(w, f, iv, 6260), c5200=ew(w, f, iv, 5195)))
R = pd.DataFrame(rows); S = pd.read_csv(f"{U}/sample.csv", dtype={"sdss_id": str}); R = R.merge(S[["sdss_id", "gaia_dr3_source_id", "classification", "snr", "g_mag"]], on="sdss_id")
R["bin"] = pd.cut(R.snr.astype(float), [0, 12, 16, 20, 25, 30, 40, 60, 1000])
sc = R.groupby("bin", observed=True).apply(lambda g: 1.4826 * np.nanmedian(np.abs(np.r_[g.c5330, g.c6250, g.c5200] - np.nanmedian(np.r_[g.c5330, g.c6250, g.c5200]))))
R["sig"] = R.bin.map(sc).astype(float); R["z5280"] = R.e5280 / R.sig; R["z6198"] = R.e6198 / R.sig; R["score"] = R.z5280 + 0.5 * R.z6198
R.sort_values("score", ascending=False).to_csv(f"{U}/cuts_score.csv", index=False)
print({str(k): round(v, 2) for k, v in sc.items()})
pd.set_option("display.width", 200); print(R.sort_values("score", ascending=False).head(40)[["sdss_id", "gaia_dr3_source_id", "classification", "snr", "g_mag", "e5280", "z5280", "e6198", "z6198", "score"]].round(2).to_string(index=False))
