"""J2052 H-alpha: fit with the tile-20836/petal-8 flux-calibration residual template (median fractional residual of 28 bright galaxy/QSO
continua) as a free-amplitude multiplicative term, plus an optional Gaussian emission line. Compares chi2 with and without the Gaussian."""
import numpy as np
from scipy.optimize import least_squares
D = np.load("tilemates_ha.npy", allow_pickle=True).item(); LINES = [3727.4, 4102.9, 4341.7, 4862.7, 4960.3, 5008.2, 6549.9, 6564.6, 6585.3, 6718.3, 6732.7]
d = np.load("desi_dr1.npz"); w0, f0, iv0 = d["w"], d["f"], d["iv"]; m = (w0 > 6520) & (w0 < 6610) & (iv0 > 0); w, f, iv = w0[m], f0[m], iv0[m]
R = []
for k, s in D.items():
    if k == "39627705435554416" or s["t"] not in ("GALAXY", "QSO") or any(6530 < l * (1 + s["z"]) < 6610 for l in LINES): continue
    ww, ff, ii = s["w"], s["f"], s["iv"]; ok = ii > 0; side = ok & (((ww > 6500) & (ww < 6550)) | ((ww > 6585) & (ww < 6640)))
    if side.sum() < 40: continue
    p = np.polyfit(ww[side], ff[side], 1); c = np.polyval(p, ww); snr = np.median(c[side]) / np.std(ff[side] - c[side])
    if snr >= 8: R.append(np.interp(w, ww, ff / c - 1))
T = np.median(np.array(R), 0); print("template peak at", w[np.argmax(T)].round(2), "A, height", (100 * T.max()).round(1), "%")
def model(p, em):
    c0, c1, a, mu, sg, amp = p[:6]; wd = c0 + c1 * (w - 6565) - a * np.exp(-0.5 * ((w - mu) / sg) ** 2)
    out = wd * (1 + p[6] * T)
    if em: out = out + p[7] * np.exp(-0.5 * ((w - p[8]) / p[9]) ** 2)
    return out
res = lambda p, em: (f - model(p, em)) * np.sqrt(iv)
p0 = [21, 0, 4, 6563, 12, 0, 1.0]
a = least_squares(res, p0, args=(False,)); b = least_squares(res, p0 + [8, 6568.7, 1.7], args=(True,))
c2a, c2b = np.sum(a.fun ** 2), np.sum(b.fun ** 2); print(f"artefact only: chi2 {c2a:.1f} (template amplitude {a.x[6]:.2f}); + emission: chi2 {c2b:.1f}, delta chi2 {c2a - c2b:.1f} for 3 extra params")
print(f"with emission: template amplitude {b.x[6]:.2f}; emission centre {b.x[8]:.2f} A ({(b.x[8]-6564.61)/6564.61*299792.458:.0f} km/s), sigma {abs(b.x[9]):.2f} A, peak {b.x[7]:.1f} (continuum ~{b.x[0]:.1f}), n = {len(w)}")
