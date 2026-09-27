"""WDJ1949+6730 (Gaia DR3 2249098833310553728): TESS SPOC 120-s PDCSAP (all sectors), joint frequency, fold (100 bins), harmonic content,
eclipse search (residual bins), per-sector amplitude; Gaia DR3 G/BP/RP folded on the same ephemeris."""
import glob, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits; from astropy.timeseries import LombScargle
T, Y, E, SEC = [], [], [], []
for p in sorted(glob.glob("spoc/mastDownload/TESS/*/*_lc.fits")):
    h = fits.open(p); d = h[1].data; q = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"]); t = d["TIME"][q] + 2457000; y = d["PDCSAP_FLUX"][q]; e = d["PDCSAP_FLUX_ERR"][q]
    m = np.median(y); y, e = y / m - 1, e / m; s = 1.4826 * np.median(np.abs(y - np.median(y))); k = np.abs(y - np.median(y)) < 6 * s
    T.append(t[k]); Y.append(y[k]); E.append(e[k]); SEC.append(np.full(k.sum(), h[0].header["SECTOR"]))
t, y, e, sec = map(np.concatenate, (T, Y, E, SEC)); fr = np.linspace(22.60, 22.63, 300001); f = fr[np.argmax(LombScargle(t, y, e).power(fr))]
t0 = 2460000.0; X = np.vstack([np.ones_like(t)] + [fn(2 * np.pi * k * f * (t - t0)) for k in (1, 2, 3) for fn in (np.cos, np.sin)]).T
c = np.linalg.lstsq(X / e[:, None], y / e, rcond=None)[0]; A = [np.hypot(c[2 * k - 1], c[2 * k]) for k in (1, 2, 3)]
ph1 = np.arctan2(c[2], c[1]); tmax = t0 + ph1 / (2 * np.pi * f)
print(f"f = {f:.6f} c/d, P = {1440/f:.4f} min; harmonic amplitudes {100*A[0]:.2f}, {100*A[1]:.2f}, {100*A[2]:.2f}% (crowding-corrected PDCSAP); n = {len(t)}, sectors {sorted(set(sec.astype(int)))}")
ph = ((t - tmax) * f) % 1; nb = 100; b = np.floor(ph * nb).astype(int); mb = np.array([np.mean(y[b == i]) for i in range(nb)]); sb = np.array([np.std(y[b == i]) / np.sqrt((b == i).sum()) for i in range(nb)])
r = y - X @ c; rb = np.array([np.mean(r[b == i]) for i in range(nb)]); z = rb / sb; print(f"residual bins: min {100*rb.min():+.2f}% ({z.min():.1f} sigma) at phase {(np.argmin(rb)+.5)/nb:.2f}; max {100*rb.max():+.2f}% ({z.max():.1f} sigma); bin error {100*np.median(sb):.2f}%")
for s in sorted(set(sec.astype(int))):
    m = sec == s; Xs = np.vstack([np.ones(m.sum()), np.cos(2 * np.pi * f * (t[m] - t0)), np.sin(2 * np.pi * f * (t[m] - t0))]).T; cs = np.linalg.lstsq(Xs, y[m], rcond=None)[0]
    print(f"  S{s}: A {100*np.hypot(cs[1], cs[2]):.1f}%, phase of max {((np.arctan2(cs[2], cs[1]) - ph1) / (2*np.pi)) % 1:.3f}")
fig, ax = plt.subplots(1, 2, figsize=(12, 3.5)); ax[0].errorbar((np.arange(nb) + .5) / nb, mb, sb, fmt="k.", ms=3); ax[0].errorbar((np.arange(nb) + .5) / nb + 1, mb, sb, fmt="k.", ms=3)
ax[0].set_title(f"TESS 120 s, {len(set(sec))} sectors, P = {1440/f:.3f} min", fontsize=8); ax[0].set_xlabel("phase")
ax[1].plot((np.arange(nb) + .5) / nb, 100 * rb, "k.", ms=3); ax[1].set_title("residual after 3-harmonic fit (%)", fontsize=8)
plt.tight_layout(); plt.savefig("tess_fold.png", dpi=80); np.save("ephem.npy", np.array([f, tmax]))
