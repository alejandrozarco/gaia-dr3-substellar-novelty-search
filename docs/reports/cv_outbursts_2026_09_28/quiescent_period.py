"""Quiescent orbital-period / eclipse search for the seven ZTF dwarf-nova candidates (2026-09-29).
ZTF DR light curves (ztfdr/<oid>.csv), catflags == 0, one oid per filter (the one with most points); nights with more than 6 points (high-cadence runs) are dropped because
minute-scale flickering on those nights produced a spurious 7.38-h 'eclipse' in ZTF21abuysmk. Box search runs on flux. Outburst points removed:
anything brighter than the quiescent median by > 0.5 mag, plus 3 d either side of each outburst point (decline tails).
Per filter the median is subtracted; g and r combined. Barycentric times (hjd).
(1) Lomb-Scargle, 1-60 c/d (0.4-24 h), FAP by 200 bootstrap shuffles of magnitudes within filter (max-power distribution).
(2) Box search for eclipses (faint excursions): BLS on the same data, periods 1.2-24 h, durations 7, 14, 29 min, significance from the same
    shuffles. Also counts points > 0.75 mag fainter than the quiescent median (eclipse candidates).
Output: quiescent_period.csv; folded plots for any FAP < 0.01 signal."""
import numpy as np, pandas as pd, os, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.timeseries import LombScargle, BoxLeastSquares
H = os.path.dirname(os.path.abspath(__file__))
C = [("6291945806661266560", "ZTF20aaxughc"), ("3082396190372984832", "ZTF18acrmcvc"), ("5614298790271682688", "ZTF20actkemr"),
     ("5701425912708783488", "ZTF22aaahiva"), ("3109248424693126400", "ZTF18actbmig"), ("4308831935765230720", "ZTF21abuysmk"),
     ("5182404743053707904", "ZTF24abfojgu")]
fr = np.linspace(1, 60, 120000); rng = np.random.default_rng(5); rows = []
for gaia, oid in C:
    d = pd.read_csv(os.path.join(H, "ztfdr", oid + ".csv")); d = d[d.catflags == 0]
    parts = []
    for fc in ("zg", "zr"):
        x = d[d.filtercode == fc]
        if len(x) < 20: continue
        x = x[x.oid == x.oid.value_counts().index[0]]
        n = np.floor(x.mjd); x = x[n.map(n.value_counts()).values <= 6]  # drop high-cadence nights: minute-scale flickering there fakes eclipses/periods
        med = np.median(x.mag); ob = x.hjd[x.mag < med - 0.5].values
        q = x[~np.any(np.abs(x.hjd.values[:, None] - ob[None, :]) < 3, axis=1)] if len(ob) else x
        med = np.median(q.mag); parts.append(pd.DataFrame(dict(t=q.hjd.values, m=q.mag.values - med, e=q.magerr.values, f=fc)))
    Q = pd.concat(parts); t, m, e = Q.t.values, Q.m.values, Q.e.values
    ls = LombScargle(t, m, e); p = ls.power(fr); k = int(np.argmax(p))
    mx = []
    for s in range(200):
        mm = m.copy()
        for fc in Q.f.unique():
            i = np.where(Q.f.values == fc)[0]; mm[i] = rng.permutation(mm[i])
        mx.append(LombScargle(t, mm, e).power(fr[::4]).max())
    fap = (np.sum(np.array(mx) >= p[k]) + 1) / 201
    fl = 10**(-0.4 * m); fe = 0.921 * e * fl; bls = BoxLeastSquares(t, fl, fe); per = 1 / fr[(fr <= 20)][::4]; r = bls.power(per, [0.005, 0.01, 0.02], objective="snr"); kb = int(np.argmax(r.power))
    bmx = []
    for s in range(50):
        mm = m.copy()
        for fc in Q.f.unique():
            i = np.where(Q.f.values == fc)[0]; mm[i] = rng.permutation(mm[i])
        bmx.append(BoxLeastSquares(t, 10**(-0.4 * mm), fe).power(per[::3], [0.005, 0.01, 0.02], objective="snr").power.max())
    bfap = (np.sum(np.array(bmx) >= r.power[kb]) + 1) / 51
    faint = int((m > 0.75).sum())
    rows.append(dict(gaia=gaia, oid=oid, n_quiet=len(t), rms=float(np.std(m)), ls_f=fr[k], ls_P_h=24 / fr[k], ls_power=float(p[k]), ls_fap=fap, ls_amp=float(np.ptp(ls.model(np.linspace(0, 1 / fr[k], 50) + t[0], fr[k])) / 2),
                     bls_P_h=float(r.period[kb] * 24), bls_depth=float(r.depth[kb]), bls_snr=float(r.power[kb]), bls_fap=bfap, n_faint_0p75=faint))
    fig, ax = plt.subplots(1, 3, figsize=(15, 3.5))
    ax[0].plot(fr, p, lw=0.4); ax[0].set_title(f"{oid} LS; best {24/fr[k]:.4f} h FAP {fap:.3f}", fontsize=9)
    for a, P_, lab in ((ax[1], 1 / fr[k], "LS"), (ax[2], r.period[kb], "BLS")):
        ph = ((t - t[0]) / P_) % 1
        for fc, c in (("zg", "g"), ("zr", "r")):
            i = Q.f.values == fc; a.errorbar(np.r_[ph[i], ph[i] + 1], np.r_[m[i], m[i]], np.r_[e[i], e[i]], fmt=".", ms=2, color=c, alpha=0.4, lw=0.3)
        a.invert_yaxis(); a.set_title(f"{lab} fold P = {P_*24:.4f} h", fontsize=9)
    plt.tight_layout(); plt.savefig(os.path.join(H, f"quiet_{oid}.png"), dpi=60); plt.close()
    print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv(os.path.join(H, "quiescent_period.csv"), index=False)
