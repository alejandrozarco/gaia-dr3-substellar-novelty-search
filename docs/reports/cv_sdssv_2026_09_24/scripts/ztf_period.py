# Refined ZTF period search: normalized flux (per field/ccd/quad/filter), 3-sigma clipped, optional removal of a smooth
# long-term trend (per-season median), LS over 0.02-1.0 d on g, r and combined; reports top peaks with FAP and marks
# peaks within 2% of 1-day aliases (n/1 d, 1/(1-1/P) etc.). Saves periodogram PNG and phase-folded LC.
import sys, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.timeseries import LombScargle
gid = sys.argv[1]
d = pd.read_csv(f"/tmp/fanout/cv/ztf/{gid}_clean.csv")
d = d[d.filtercode.isin(["zg", "zr"])].copy()
# season detrend: subtract median per 60-day bin per band
d["bin"] = (d.bjd_tdb // 60).astype(int)
d["y"] = d.nflux - d.groupby(["filtercode", "bin"]).nflux.transform("median") + 1
out = {}
fig, axes = plt.subplots(3, 2, figsize=(14, 10))
fmin, fmax = 1 / 1.0, 1 / 0.02
for k, (lab, s) in enumerate((("g", d[d.filtercode == "zg"]), ("r", d[d.filtercode == "zr"]), ("g+r", d))):
    m = np.abs(s.y - np.median(s.y)) < 4 * 1.4826 * np.median(np.abs(s.y - np.median(s.y)))
    s = s[m]
    ls = LombScargle(s.bjd_tdb, s.y, s.neflux)
    f, p = ls.autopower(minimum_frequency=fmin, maximum_frequency=fmax, samples_per_peak=15)
    # window function (spectral window) peaks
    idx = np.argsort(p)[::-1]; peaks = []
    for i in idx:
        if all(abs(f[i] - f[j]) > 0.01 for j in peaks): peaks.append(i)
        if len(peaks) >= 6: break
    rows = []
    for i in peaks:
        P = 1 / f[i]; alias = any(abs(f[i] - n) < 0.02 * n for n in (1, 2, 3, 4)) 
        rows.append((round(P * 24, 4), round(float(p[i]), 4), float(ls.false_alarm_probability(p[i], minimum_frequency=fmin, maximum_frequency=fmax)), alias))
    out[lab] = dict(n=len(s), rms=float(np.std(s.y)), peaks=rows)
    ax = axes[k, 0]; ax.plot(f, p, "k-", lw=0.5); ax.set_xlabel("frequency (1/d)"); ax.set_title(f"{gid} ZTF {lab} (detrended) LS; N={len(s)}", fontsize=8)
    for i in peaks[:3]: ax.axvline(f[i], color="r", ls=":", lw=0.6)
    ax2 = axes[k, 1]; P0 = 1 / f[peaks[0]]
    ph = (s.bjd_tdb / P0) % 1
    ax2.plot(ph, s.y, ".", ms=2, alpha=0.4); ax2.plot(ph + 1, s.y, ".", ms=2, alpha=0.4)
    bins = np.linspace(0, 1, 21); bm = [np.median(s.y[(ph >= a) & (ph < b)]) for a, b in zip(bins[:-1], bins[1:])]
    ax2.plot(0.5 * (bins[:-1] + bins[1:]), bm, "r-o", ms=3); ax2.set_ylim(np.percentile(s.y, 1), np.percentile(s.y, 99))
    ax2.set_title(f"folded on top peak P={P0*24:.4f} h", fontsize=8)
fig.tight_layout(); fig.savefig(f"/tmp/fanout/cv/plots/ztf_period_{gid}.png", dpi=85)
import json; print(json.dumps(out, indent=0))
