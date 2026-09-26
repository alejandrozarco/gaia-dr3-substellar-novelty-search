"""CoRoT faint-star white-light curves of CoRoT 102743730 (mask includes the hot WD Gaia DR3 3107374277060584064, 4.1" away):
STATUS == 0 points, per run: 5-sigma clip of a 1-day running median residual, Lomb-Scargle 0.05-20 c/d, sine fit at the peak.
Dates: DATEBARTT = BJD(TT) - 2451545.0. Output printed + corot_fold.png."""
import numpy as np, glob, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.timeseries import LombScargle
from scipy.ndimage import median_filter
res = []
fig, ax = plt.subplots(3, 2, figsize=(12, 9))
for i, f in enumerate(sorted(glob.glob("corot/*.fits"))):
    d = fits.open(f)["BAR"].data; ok = (d["STATUS"] == 0) & np.isfinite(d["WHITEFLUX"]) & (d["WHITEFLUX"] > 0)
    t = d["DATEBARTT"][ok].astype(float); y = d["WHITEFLUX"][ok].astype(float)
    y = y / np.median(y) - 1
    # slow trend: 3-day running median over time-sorted points (removes CoRoT long-term drifts, keeps 14 h)
    o = np.argsort(t); t, y = t[o], y[o]; dt = np.median(np.diff(t)); w = int(3 / dt) | 1
    trend = median_filter(y, size=w, mode="nearest"); r = y - trend
    s = 1.4826 * np.median(np.abs(r)); k = np.abs(r) < 5 * s; t, r = t[k], r[k]
    fr = np.arange(0.05, 20, 0.02 / (t.max() - t.min())); ls = LombScargle(t, r); p = ls.power(fr)
    f0 = fr[np.argmax(p)]
    # refine
    ff = np.linspace(f0 - 0.002, f0 + 0.002, 4001); f0 = ff[np.argmax(ls.power(ff))]
    X = np.vstack([np.ones_like(t), np.sin(2*np.pi*f0*t), np.cos(2*np.pi*f0*t), np.sin(4*np.pi*f0*t), np.cos(4*np.pi*f0*t)]).T
    c, *_ = np.linalg.lstsq(X, r, rcond=None); resid = r - X @ c; sig = resid.std()
    amp = np.hypot(c[1], c[2]); T = t.max() - t.min()
    ef = np.sqrt(6 / len(t)) * sig / (np.pi * T * amp)   # Montgomery & O'Donoghue 1999
    run = f.split("_")[3][:8]
    print(f"{run}: n={len(t)} span {T:.1f} d, cadence {dt*1440:.1f} min, peak {f0:.6f} +- {ef:.6f} c/d (P {24/f0:.5f} h), "
          f"semi-amplitude {100*amp:.2f}% (2nd harmonic {100*np.hypot(c[3],c[4]):.2f}%), rms resid {100*sig:.2f}%")
    res.append((run, f0, ef, t, r))
    ax[i, 0].plot(fr, p, lw=.6); ax[i, 0].set_xlim(0, 8); ax[i, 0].set_title(f"CoRoT {run} Lomb-Scargle")
    ph = (t * f0) % 1; b = np.linspace(0, 1, 51); m = [np.median(r[(ph >= b[j]) & (ph < b[j+1])]) for j in range(50)]
    ax[i, 1].plot(ph, r, ",", alpha=.3); ax[i, 1].plot(b[:-1] + .01, m, "r-"); ax[i, 1].set_ylim(-0.12, 0.12); ax[i, 1].set_title(f"folded at {24/f0:.4f} h")
plt.tight_layout(); plt.savefig("corot_fold.png", dpi=80)
np.save("corot_res.npy", np.array([(a, b, c) for a, b, c, *_ in res], dtype=object), allow_pickle=True)
