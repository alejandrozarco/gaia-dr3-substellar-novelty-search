import os, io, gzip, requests, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits; from scipy.ndimage import gaussian_filter1d, median_filter
X = os.path.dirname(os.path.abspath(__file__)); R = pd.read_csv(f"{X}/lamost_ranked.csv", dtype={"ObsID": str, "GaiaDR3": str}).set_index("GaiaDR3")
S = [("124105523855366272", "cand"), ("978604724981696768", "cand"), ("2498367529597482496", "known DO UHE J0254"), ("777283596179360128", "known UHE J1059"), ("1746496503290277888", "known DAO UHE HS2115")]
reg = [(4440, 4560, "4495"), (5180, 5380, "5243/5280"), (5580, 5750, "5665"), (4620, 4740, "He II 4686")]
fig, ax = plt.subplots(len(S), len(reg), figsize=(14, 1.8 * len(S)))
for i, (g, lab) in enumerate(S):
    ob = R.loc[g].ObsID
    for rel in ("v1.1", "v2.0"):
        q = requests.get(f"https://www.lamost.org/dr11/{rel}/spectrum/fits/{ob}", timeout=90)
        if q.status_code == 200 and len(q.content) > 5000: break
    raw = q.content; d = fits.open(io.BytesIO(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw))[1].data[0]
    w = np.array(d["WAVELENGTH"], float); f = np.array(d["FLUX"], float); ok = (np.array(d["IVAR"]) > 0) & (d["ANDMASK"] == 0); w, f = w[ok], f[ok]; c = median_filter(f, 201, mode="nearest")
    for j, (a, b, n) in enumerate(reg):
        k = (w > a) & (w < b); ax[i, j].plot(w[k], gaussian_filter1d(f[k] / c[k], 1.2), "k", lw=.6); ax[i, j].set_ylim(0.85, 1.08); ax[i, j].set_yticks([]); ax[i, j].tick_params(labelsize=6)
        for l in (4495, 5243, 5280, 5665, 4687.0):
            if a < l < b: ax[i, j].axvline(l, color="r", lw=.5, alpha=.6)
        if i == 0: ax[i, j].set_title(n, fontsize=8)
    ax[i, 0].set_ylabel(f"{lab}\n{g}\nS/N {R.loc[g].snrg:.0f} {R.loc[g].wdClass}", fontsize=6, rotation=0, ha="right")
plt.tight_layout(); plt.savefig(f"{X}/candidates.png", dpi=70)
