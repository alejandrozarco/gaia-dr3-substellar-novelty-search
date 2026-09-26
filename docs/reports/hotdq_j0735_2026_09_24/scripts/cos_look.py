# HST/COS G130M (SNAP 17420, PI Gaensicke; 2024-07-13, 1800 s; public) spectrum of Gaia DR3 5208047381438507520.
# Plot with line markers: Ly-alpha, C II 1334.5/1335.7, C III 1174.9-1176.4 and 1247.4, C II 1323.9, C I 1277/1329, Si II 1260/1265,
# Si III 1206.5, Si IV 1393.8/1402.8, N V 1238.8/1242.8, geocoronal Ly-alpha and O I 1302-1306 airglow. Equivalent widths of the
# strongest carbon features against a local continuum.
import numpy as np
from astropy.io import fits
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
h = fits.open("mastDownload/HST/lfac0z010/lfac0z010_x1dsum.fits"); d = h[1].data
print("targname", h[0].header.get("TARGNAME"), "opt_elem", h[0].header.get("OPT_ELEM"), "cenwave", h[0].header.get("CENWAVE"), "exptime", h[1].header.get("EXPTIME"), "date", h[1].header.get("DATE-OBS"))
W = np.concatenate([r["WAVELENGTH"] for r in d]); F = np.concatenate([r["FLUX"] for r in d]); E = np.concatenate([r["ERROR"] for r in d]); DQ = np.concatenate([r["DQ_WGT"] for r in d])
o = np.argsort(W); W, F, E, DQ = W[o], F[o], E[o], DQ[o]; ok = (DQ > 0) & (E > 0)
W, F, E = W[ok], F[ok], E[ok]
def smooth(y, n=7): return np.convolve(y, np.ones(n) / n, mode="same")
print(f"range {W.min():.1f}-{W.max():.1f} A; median flux 1400 A {np.median(F[(W>1380)&(W<1420)]):.2e}, S/N per pixel ~{np.median(F/E):.1f}")
LINES = {"Ly-a": [1215.67], "C III": [1174.93, 1175.26, 1175.59, 1175.71, 1175.99, 1176.37], "C III 1247": [1247.38], "C II": [1334.53, 1335.71], "C II 1324": [1323.95],
         "C I": [1277.25, 1328.83, 1280.33], "Si II": [1260.42, 1264.74, 1193.29, 1194.50], "Si III": [1206.50], "Si IV": [1393.76, 1402.77], "N V": [1238.82, 1242.80], "O I air": [1302.17, 1304.86, 1306.03]}
col = {"Ly-a": "b", "C III": "m", "C III 1247": "m", "C II": "r", "C II 1324": "r", "C I": "orange", "Si II": "g", "Si III": "g", "Si IV": "g", "N V": "c", "O I air": "0.5"}
fig, ax = plt.subplots(2, 1, figsize=(16, 8))
for a, (lo, hi) in zip(ax, [(1130, 1285), (1285, 1440)]):
    s = (W > lo) & (W < hi); a.plot(W[s], smooth(F[s]), "k", lw=0.6)
    for nm, ls in LINES.items():
        for l in ls:
            if lo < l < hi: a.axvline(l, color=col[nm], lw=0.7, alpha=0.7)
    a.set_xlim(lo, hi); a.set_ylim(0, np.percentile(smooth(F[s]), 99.5) * 1.15)
    a.set_ylabel("flux (erg/s/cm2/A)")
ax[0].set_title("HST/COS G130M, Gaia DR3 5208047381438507520 (SNAP 17420). blue Ly-a, magenta C III, red C II, orange C I, green Si, cyan N V, grey O I airglow", fontsize=9)
plt.tight_layout(); plt.savefig("fig_cos.png", dpi=85)
def ew(center, half=1.5, cont=((-6, -3), (3, 6))):
    cs = np.concatenate([F[(W > center + a) & (W < center + b)] for a, b in cont]); c = np.median(cs)
    s = np.abs(W - center) < half; dw = np.median(np.diff(W))
    ewv = np.sum(1 - F[s] / c) * dw; eew = np.sqrt(np.sum((E[s] / c) ** 2)) * dw
    return ewv, eew, c
for nm, cen, hw, ct in [("C II 1335 (blend)", 1335.1, 2.0, ((-9, -4), (4, 9))), ("C III 1175 (multiplet)", 1175.6, 2.0, ((-8, -4), (4, 8))), ("C III 1247", 1247.38, 0.8, ((-4, -2), (2, 4))),
                        ("C II 1324", 1323.95, 0.8, ((-4, -2), (2, 4))), ("Si II 1260", 1260.42, 0.8, ((-4, -2), (2, 4))), ("Si IV 1394", 1393.76, 0.8, ((-4, -2), (2, 4))), ("N V 1239", 1238.82, 0.8, ((-4, -2), (2, 4)))]:
    v, e, c = ew(cen, hw, ct); print(f"  {nm:22s}: EW {v:+.3f} +- {e:.3f} A ({v/e:+.1f} sigma)")
# Ly-alpha profile: flux ratio at +-20, +-40 A from line centre to the continuum at 1170 and 1270 A
for dl in (10, 20, 30, 50):
    f1 = np.median(F[np.abs(W - (1215.67 - dl)) < 1.5]); f2 = np.median(F[np.abs(W - (1215.67 + dl)) < 1.5])
    print(f"  Ly-a wings: F(1215.7-{dl}) = {f1:.2e}, F(1215.7+{dl}) = {f2:.2e}")
print(f"  continuum 1150 {np.median(F[np.abs(W-1150)<3]):.2e}, 1300 {np.median(F[np.abs(W-1290)<3]):.2e}, 1420 {np.median(F[np.abs(W-1420)<3]):.2e}")
