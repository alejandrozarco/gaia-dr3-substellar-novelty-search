"""ZTF24abfojgu = Gaia DR3 5182404743053707904 (2026-09-29): is the quiescent 76.34 / 80.63-min signal present, and stronger, in the
bright state that began 2024-09-27? A polar (magnetic CV) switching from a low to a high accretion state would show a large
orbital modulation at the same period.
Data: ZTF data-release PSF photometry (catflags 0) before MJD 60578 ("low") and from MJD 60580 ("high"); in the high state, ZTF
alerts (magpsf_corr, drb >= 0.8) add points after the data release ends (deduplicated against DR epochs within 0.0005 d).
Slow changes are removed by subtracting a leave-one-out running median over +-WIN d per filter (WIN = 3 by default; environment variable WIN) (points with fewer than 3
neighbours in that window are dropped); high-cadence nights (> 6 points) are dropped.
Lomb-Scargle 1-60 c/d on g+r combined (per-filter medians removed); FAP from 300 shuffles of magnitudes within filter and
3-d block (keeps slow structure, destroys phase coherence). Output: abfojgu_highstate.json, abfojgu_highstate.png."""
import numpy as np, pandas as pd, json, os, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.timeseries import LombScargle
H = os.path.dirname(os.path.abspath(__file__)); oid = "ZTF24abfojgu"; WIN = float(os.environ.get("WIN", 3)); TAG = "" if WIN == 3 else f"_win{int(WIN)}"
d = pd.read_csv(os.path.join(H, "ztfdr", oid + ".csv")); d = d[d.catflags == 0]
a = pd.read_csv(os.path.join(H, "alerts", oid + ".csv")); a = a[(a.isdiffpos.astype(str).isin(["1", "t", "True"])) & (a.magpsf_corr < 90)]
a = a[np.where(a.drb.notna(), a.drb >= 0.8, a.rb >= 0.6)]
def dataset(state):
    rows = []
    for fc, fid in (("zg", 1), ("zr", 2)):
        x = d[d.filtercode == fc]; x = x[x.oid == x.oid.value_counts().index[0]]
        x = x[(x.mjd < 60578)] if state == "low" else x[x.mjd >= 60580]
        t, m, e = list(x.hjd), list(x.mag), list(x.magerr)
        if state == "high":
            y = a[(a.fid == fid) & (a.mjd >= 60580)]; dr_mjd = x.mjd.values
            for mj, mg, er in zip(y.mjd, y.magpsf_corr, y.sigmapsf_corr):
                if len(dr_mjd) == 0 or np.min(np.abs(dr_mjd - mj)) > 0.0005: t.append(mj + 2400000.5); m.append(mg); e.append(er)   # alert times are MJD (not barycentric; < 8 min error)
        df = pd.DataFrame(dict(t=t, m=m, e=e)); n = np.floor(df.t); df = df[n.map(n.value_counts()).values <= 6].reset_index(drop=True)
        tt_, mm_ = df.t.values, df.m.values; res = np.full(len(df), np.nan)
        for i in range(len(df)):            # leave-one-out running median; points with < 3 neighbours within 3 d are dropped
            nb = (np.abs(tt_ - tt_[i]) <= WIN); nb[i] = False
            if nb.sum() >= 3: res[i] = mm_[i] - np.median(mm_[nb])
        df["res"] = res; df = df[np.isfinite(df.res)]; df["f"] = fc; rows.append(df)
    return pd.concat(rows)
fr = np.linspace(1, 60, 200000); out = {}; rng = np.random.default_rng(9)
fig, ax = plt.subplots(2, 2, figsize=(14, 7))
for k, state in enumerate(("low", "high")):
    D = dataset(state); t, y, e = D.t.values, D.res.values, np.clip(D.e.values, 0.01, None); ls = LombScargle(t, y, e); p = ls.power(fr); j = int(np.argmax(p))
    mx = []
    for s in range(300):
        yy = y.copy()
        for f in ("zg", "zr"):
            idx = np.where(D.f.values == f)[0]; blk = np.floor(t[idx] / 3)
            for b in np.unique(blk):
                ii = idx[blk == b]; yy[ii] = rng.permutation(yy[ii])
        mx.append(LombScargle(t, yy, e).power(fr[::5]).max())
    fap = (np.sum(np.array(mx) >= p[j]) + 1) / 301
    near = {}
    for f0 in (18.8619, 17.8592, 19.8647):
        m = np.abs(fr - f0) < 0.01; i = int(np.argmax(np.where(m, p, 0))); near[f0] = (float(fr[i]), float(p[i]))
    fbest = fr[j]; ph = (t * fbest) % 1; amp = float(np.ptp(ls.model(np.linspace(0, 1 / fbest, 100) + t[0], fbest)) / 2)
    out[state] = dict(n=len(t), span_d=float(t.max() - t.min()), rms_res=float(np.std(y)), best_f=float(fbest), best_P_min=float(1440 / fbest), power=float(p[j]), fap=float(fap), semi_amp_mag=amp,
                      alias_peaks={f"{k_:.4f}": v for k_, v in near.items()})
    print(state, out[state], flush=True)
    ax[k, 0].plot(fr, p, lw=0.4); ax[k, 0].set_title(f"{state} state: n={len(t)}, best {1440/fbest:.3f} min, power {p[j]:.3f}, FAP {fap:.3f}", fontsize=9)
    for f0 in (18.8619, 17.8592): ax[k, 0].axvline(f0, color="r", lw=0.5, alpha=0.5)
    for f, c in (("zg", "g"), ("zr", "r")):
        i = D.f.values == f; pp = (t[i] * 18.8619) % 1; ax[k, 1].plot(np.r_[pp, pp + 1], np.r_[y[i], y[i]], ".", color=c, ms=3, alpha=0.6)
    ax[k, 1].invert_yaxis(); ax[k, 1].set_title(f"{state} state folded on 76.343 min (residual mag)", fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(H, f"abfojgu_highstate{TAG}.png"), dpi=70)
json.dump(out, open(os.path.join(H, f"abfojgu_highstate{TAG}.json"), "w"), indent=1)
# Targeted test (added 2026-09-29): the frequencies are known a priori from the low state, so the null distribution is the maximum
# power within +-0.01 c/d of the three alias frequencies (17.8592, 18.8619, 19.8647 c/d) under the same block shuffles.
win = np.zeros_like(fr, bool)
for f0 in (17.8592, 18.8619, 19.8647): win |= np.abs(fr - f0) < 0.01
frw = fr[win]
for state in ("low", "high"):
    D = dataset(state); t, y, e = D.t.values, D.res.values, np.clip(D.e.values, 0.01, None)
    obs = LombScargle(t, y, e).power(frw).max(); mx = []
    for s in range(1000):
        yy = y.copy()
        for f in ("zg", "zr"):
            idx = np.where(D.f.values == f)[0]; blk = np.floor(t[idx] / 3)
            for b in np.unique(blk):
                ii = idx[blk == b]; yy[ii] = rng.permutation(yy[ii])
        mx.append(LombScargle(t, yy, e).power(frw).max())
    fapt = (np.sum(np.array(mx) >= obs) + 1) / 1001; out[state]["targeted_power"] = float(obs); out[state]["targeted_fap"] = float(fapt)
    print(state, "targeted: max power in the alias windows %.3f, FAP %.4f (1000 block shuffles)" % (obs, fapt), flush=True)
json.dump(out, open(os.path.join(H, f"abfojgu_highstate{TAG}.json"), "w"), indent=1)
