# Zeeman-triplet vs core+wing null fit (method of /tmp/mwd/zeeman_scan2.py, v2), generalised to SDSS lite, DESI and SDSS-V spectra.
# Adds a coarse line-centre search (+-120 A) before the +-8 A fine shift grid, so pipeline RV offsets cannot masquerade as splitting.
import numpy as np
from astropy.io import fits
LINES = {"Ha": 6564.61, "Hb": 4862.68}
WIN = {"Ha": (220, 190), "Hb": (180, 150)}      # half-window, continuum-exclusion half-width (A) around the (re-centred) line
SIG = np.array([2, 3, 4.5, 6.5, 9, 13, 18, 25, 35, 50, 70, 100.0]); SH = np.linspace(-8, 8, 17)
BGRID = np.concatenate([[0.0], np.geomspace(0.2, 30, 70)])
def load_sdss(fn):
    d = fits.open(fn)[1].data
    lam = 10 ** np.array(d['loglam'], float); f = np.array(d['flux'], float); iv = np.array(d['ivar'], float)
    # SDSS lite spectra are in vacuum wavelengths, heliocentric -> fine for Balmer vacuum wavelengths used here
    return lam, f, iv
def centre(lam, f, iv, l0):
    m = (lam > l0 - 150) & (lam < l0 + 150) & (iv > 0) & np.isfinite(f)
    x, y = lam[m], f[m]
    if len(x) < 30: return 0.0
    k = np.exp(-0.5 * (np.arange(-40, 41) / 12.0) ** 2); k /= k.sum()
    ys = np.convolve(y, k, mode='same')
    core = (x > l0 - 120) & (x < l0 + 120)
    return float(x[core][np.argmin(ys[core])] - l0)
def segment(lam, f, iv, l0, hw, edge):
    m = (lam > l0 - hw) & (lam < l0 + hw) & (iv > 0) & np.isfinite(f); x, y, w2 = lam[m], f[m], iv[m]
    cont = np.abs(x - l0) > edge
    p = np.polyfit(x[cont], y[cont], 1, w=np.sqrt(w2[cont])); c = np.polyval(p, x)
    return x, y / c, w2 * c ** 2
def best_chi2(x, y, w2, l0, B):
    dl = 4.67e-13 * l0 ** 2 * B * 1e6; r = 1 - y; rr = np.sum(w2 * r * r); best = (rr, None)
    comps = ((0.0, 1.0),) if B == 0 else ((0.0, 0.5), (-dl, 0.25), (dl, 0.25))
    for sh in SH:
        T = np.zeros((len(SIG), len(x)))
        for off, wt in comps: T += wt * np.exp(-0.5 * ((x[None, :] - (l0 + sh + off)) / SIG[:, None]) ** 2)
        G = (T * w2) @ T.T; bvec = (T * w2) @ r
        for i in range(len(SIG)):
            d = bvec[i] / G[i, i]
            if d > 0:
                c = rr - d * bvec[i]
                if c < best[0]: best = (c, (sh, SIG[i], d, None, 0.0))
            for j in range(i + 1, len(SIG)):
                det = G[i, i] * G[j, j] - G[i, j] ** 2
                if det <= 0: continue
                d1 = (G[j, j] * bvec[i] - G[i, j] * bvec[j]) / det; d2 = (G[i, i] * bvec[j] - G[i, j] * bvec[i]) / det
                if d1 <= 0 or d2 <= 0: continue
                c = rr - d1 * bvec[i] - d2 * bvec[j]
                if c < best[0]: best = (c, (sh, SIG[i], d1, SIG[j], d2))
    return best
def profile(x, l0, B, par):
    sh, s1, d1, s2, d2 = par; dl = 4.67e-13 * l0 ** 2 * B * 1e6
    comps = ((0.0, 1.0),) if B == 0 else ((0.0, 0.5), (-dl, 0.25), (dl, 0.25)); m = np.zeros_like(x)
    for off, wt in comps:
        m += wt * d1 * np.exp(-0.5 * ((x - (l0 + sh + off)) / s1) ** 2)
        if s2 is not None: m += wt * d2 * np.exp(-0.5 * ((x - (l0 + sh + off)) / s2) ** 2)
    return 1 - m
def fit(lam, f, iv):
    segs = {}; cen = {}
    for k, l0 in LINES.items():
        dc = centre(lam, f, iv, l0); cen[k] = dc
        # shift the wavelength scale so the line minimum sits at l0 (removes pipeline RV offsets); record the offset
        segs[k] = segment(lam - dc, f, iv, l0, *WIN[k])
    chis = np.array([sum(best_chi2(*segs[k], LINES[k], B)[0] for k in LINES) for B in BGRID])
    j = int(np.argmin(chis[1:])) + 1; npix = sum(len(segs[k][0]) for k in LINES)
    chir = chis[j] / (npix - 12); dchi = chis[0] - chis[j]
    return dict(B_MG=float(BGRID[j]), dchi2=float(dchi), chi2r_best=float(chir), chi2r_null=float(chis[0] / (npix - 11)), metric=float(dchi / max(chir, 1)),
                centre_offsets=cen, chis=chis, segs=segs, par0={k: best_chi2(*segs[k], LINES[k], 0.0)[1] for k in LINES},
                parB={k: best_chi2(*segs[k], LINES[k], BGRID[j])[1] for k in LINES})
