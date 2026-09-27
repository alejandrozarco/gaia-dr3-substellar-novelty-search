import os, sys, subprocess, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.ndimage import gaussian_filter1d
D = os.path.dirname(os.path.abspath(__file__)); C = 299792.458
BASE = "https://data.sdss.org/sas/dr20/spectro/boss/redux/v6_2_1/spectra/daily/full"
V = pd.read_csv(f"{D}/visits.csv", dtype={"sdss_id": str}); E = pd.read_csv(f"{D}/exposures.csv", dtype={"sdss_id": str})
ids = sys.argv[1:]; L = {"Ha": 6564.61, "Hb": 4862.68, "Hg": 4341.69}
for sid in ids:
    exps = []
    for _, r in V[V.sdss_id == sid].iterrows():
        f = f"{int(r.field):06d}"; name = f"spec-{f}-{int(r.mjd)}-{int(r.catalogid)}.fits"; p = f"{D}/vet/{name}"
        if not os.path.exists(p): subprocess.run(["curl", "-s", "-m", "300", "-o", p, f"{BASE}/{f[:3]}XXX/{f}/{int(r.mjd)}/{name}"])
        if not os.path.exists(p) or os.path.getsize(p) < 10000: continue
        for x in fits.open(p):
            if x.name.startswith("MJD_EXP"):
                d = x.data; t = (x.header["TAI-BEG"] + x.header["EXPTIME"] / 2) / 86400; exps.append((t, 10 ** d["LOGLAM"], d["FLUX"], d["IVAR"] * (d["AND_MASK"] == 0)))
    exps.sort(key=lambda z: z[0]); e = E[E.sdss_id == sid]
    fig, ax = plt.subplots(1, 3, figsize=(13, 1.0 + 0.55 * len(exps)))
    for j, (n, l) in enumerate(L.items()):
        for k, (t, w, f, iv) in enumerate(exps):
            v = (w / l - 1) * C; m = (np.abs(v) < 2500) & (iv > 0)
            if m.sum() < 20: continue
            y = gaussian_filter1d(f[m], 2); y = y / np.median(y[np.abs(v[m]) > 1800]); ax[j].plot(v[m], y + 0.35 * k, lw=.7)
            row = e.iloc[(e.mjd_mid - t).abs().argsort()[:1]]; vv = row.v.iloc[0] if len(row) else np.nan
            if np.isfinite(vv): ax[j].plot([vv, vv], [0.4 + 0.35 * k, 0.9 + 0.35 * k], "k-", lw=1)
            if j == 0: ax[j].text(-2450, 1.05 + 0.35 * k, f"MJD {t:.3f}  v={vv:.0f}", fontsize=6)
        ax[j].axvline(0, color="0.6", lw=.5); ax[j].set_title(f"{sid} {n}", fontsize=8); ax[j].set_xlabel("km/s", fontsize=7); ax[j].set_yticks([])
    plt.tight_layout(); plt.savefig(f"{D}/vet/{sid}.png", dpi=70); plt.close()
    print(sid, len(exps), "exposures plotted")
