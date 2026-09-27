import os, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
X = os.path.dirname(os.path.abspath(__file__)); G = np.arange(5150, 5800, 1.0)
A = np.load(f"{X}/stack_flux.npy"); ids = pd.read_csv(f"{X}/stack_ids.csv").iloc[:, 0].astype(str).values
R = pd.read_csv(f"{X}/lamost_ranked.csv", dtype={"ObsID": str, "GaiaDR3": str}).set_index("ObsID").loc[ids]
kn = R.known.notna().values; da = (R.wdClass.values == "DA") & ~kn
top = ["1455413341140758016", "882283932975431040", "1912267874249376768", "124105523855366272", "978604724981696768", "2503322616188632064"]
fig, ax = plt.subplots(2 + len(top), 1, figsize=(10, 1.6 * (2 + len(top))), sharex=True)
ax[0].plot(G, np.nanmedian(A[da], 0), "k", lw=.8); ax[0].set_ylabel(f"median\n{da.sum()} DA", fontsize=7)
m = np.nanmedian(A[da], 0); print("median DA 5268-5292 mean depth:", 1 - np.nanmean(m[(G > 5268) & (G < 5292)]), "vs 5088-5112 n/a; 5468-5492:", 1 - np.nanmean(m[(G > 5468) & (G < 5492)]))
ax[1].plot(G, np.nanmedian(A[kn], 0), "b", lw=.8); ax[1].set_ylabel(f"median\n{kn.sum()} known UHE", fontsize=7)
for i, g in enumerate(top):
    o = R.index[R.GaiaDR3 == g][0]; j = list(ids).index(o)
    ax[2 + i].plot(G, gaussian_filter1d(A[j], 1.5), "k", lw=.6); ax[2 + i].set_ylabel(f"{g}\nS/N {R.loc[o].snrg:.0f}", fontsize=6)
for a in ax:
    a.set_ylim(0.9, 1.06); [a.axvline(l, color="r", lw=.5) for l in (5243, 5280, 5665)]; [a.axvspan(l - 12, l + 12, color="0.9") for l in (5480, 5740)]
plt.tight_layout(); plt.savefig(f"{X}/stack.png", dpi=70)
