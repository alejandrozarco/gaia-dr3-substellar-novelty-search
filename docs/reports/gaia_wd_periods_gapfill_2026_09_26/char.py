"""Characterise ZTF-confirmed Gaia-period white dwarfs: per band (g, r) sine + first harmonic at the best ZTF frequency near
f_gaia (+-0.001 c/d), amplitude ratio r/g (reflection: r > g), harmonic ratio; plot fold + H-alpha of every SPARCL/SDSS-V
spectrum. python char.py <source_id> ...  (todo.csv for ra/dec/f_gaia). Outputs char_<id>.png, char.csv (appended)."""
import sys, io, os, requests, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.timeseries import LombScargle
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import gas_disc_epochs as GE
from scipy.ndimage import gaussian_filter1d
U = pd.read_csv("todo.csv", dtype={"source_id": str}).set_index("source_id")
sw = pd.read_csv("/tmp/hotdq/lane_gasdisc/sw_all.csv", dtype=str)
def ztf(i, ra, dec):
    p = f"ztf/{i}.csv"
    if not os.path.exists(p):
        r = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves", params=dict(POS=f"CIRCLE {ra} {dec} 0.000556", BANDNAME="g,r", FORMAT="csv"), timeout=600)
        if not r.text.startswith("oid"): raise IOError("IRSA")
        open(p, "w").write(r.text)
    d = pd.read_csv(p); return d[(d.catflags == 0) & (d.magerr < 0.25)]
rows = []
for i in sys.argv[1:]:
    u = U.loc[i]; d = ztf(i, u.ra, u.dec); fg = u.gls_freq_g_fov
    T = d.hjd.values; fr = np.arange(fg - 0.002, fg + 0.002, 2e-7)
    fl = np.zeros(len(d)); e = np.zeros(len(d))
    for (o, b), s in d.groupby(["oid", "filtercode"]):
        m = (d.oid == o) & (d.filtercode == b); fl[m] = 10 ** (-0.4 * (d.mag[m] - d.mag[m].median())) - 1; e[m] = 0.921 * d.magerr[m]
    f0 = fr[np.argmax(LombScargle(T, fl, e).power(fr))]
    out = dict(source_id=i, f_gaia=fg, f_ztf=round(f0, 6), P_h=round(24 / f0, 4))
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    for b, c in (("zg", "g"), ("zr", "r")):
        m = d.filtercode.values == b
        if m.sum() < 15: continue
        t, y, ee = T[m], fl[m], e[m]; ph = 2 * np.pi * f0 * (t - 2459000)
        X = np.vstack([np.ones_like(t), np.cos(ph), np.sin(ph), np.cos(2 * ph), np.sin(2 * ph)]).T; W = 1 / ee ** 2
        p = np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (W * y)); C = np.linalg.inv(X.T @ (X * W[:, None])); c2 = max(np.sum(W * (y - X @ p) ** 2) / (len(t) - 5), 1)
        out[f"A1_{c}"] = round(100 * np.hypot(p[1], p[2]), 2); out[f"eA1_{c}"] = round(100 * np.sqrt(c2 * (C[1, 1] + C[2, 2]) / 2), 2); out[f"A2_{c}"] = round(100 * np.hypot(p[3], p[4]), 2)
        out[f"phi1_{c}"] = round(np.degrees(np.arctan2(p[2], p[1])), 0); out[f"n_{c}"] = int(m.sum())
        pf = (ph / (2 * np.pi)) % 1; ax[0].errorbar(np.r_[pf, pf + 1], np.r_[y, y], np.r_[ee, ee], fmt=".", ms=3, alpha=.5, label=b, color="g" if c == "g" else "r")
    if "A1_g" in out and "A1_r" in out: out["r_over_g"] = round(out["A1_r"] / max(out["A1_g"], 1e-3), 2)
    ax[0].set_title(f"{i} ZTF P = {24/f0:.4f} h"); ax[0].legend()
    # spectra: SDSS-V + SPARCL, H-alpha region
    spec = []
    s_id = sw[sw.gaia_dr3_source_id == i].sdss_id
    try:
        if len(s_id): co, per = GE.sdssv_spectra(s_id.iloc[0]); spec += [co] + per
    except Exception as ex: out["sdssv"] = f"HOLE {type(ex).__name__}"
    for k in range(4):
        try: spec += GE.sparcl_spectra(u.ra, u.dec); break
        except Exception: import time; time.sleep(20)
    out["n_spec"] = len(spec); out["spec_sets"] = ";".join(sorted({s["dataset"] for s in spec}))
    for k, s in enumerate(spec):
        w, f, iv = s["w"], s["f"], s["iv"]; m = (w > 6400) & (w < 6730) & (iv > 0) & np.isfinite(f)
        if m.sum() < 30: continue
        ax[1].plot(w[m], gaussian_filter1d(f[m] / np.median(f[m]), 2) + 0.3 * k, lw=.7); ax[1].text(6732, 1 + 0.3 * k, f"{s['dataset'][:12]} {s['date']}", fontsize=6)
    ax[1].axvline(6564.6, color="grey", lw=.4); ax[1].set_title("H-alpha")
    plt.tight_layout(); plt.savefig(f"char_{i}.png", dpi=80); plt.close()
    print(out, flush=True); rows.append(out)
pd.DataFrame(rows).to_csv("char.csv", mode="a", header=not os.path.exists("char.csv"), index=False)
