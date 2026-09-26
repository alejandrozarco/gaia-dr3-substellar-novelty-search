# Balmer-emission screen (DAHe search) on SDSS-V mwmStar coadds.
# For each spectrum: robust polynomial pseudo-continuum over 5750-7400 A (H-alpha) and 4500-5300 A (H-beta), masking +-130 A
# around the Balmer line and the strongest sky lines, with asymmetric iterative clipping; residual r = f/cont - 1 smoothed with a
# Gaussian (sigma = 3 px ~ 4.5 A at H-alpha); noise per smoothed pixel from the empirical MAD of the smoothed residual in the
# continuum windows (so that correlated noise / sky residue is included). Metrics:
#   sigHa  = max significance of a positive (emission) excursion of the smoothed residual inside 6440-6690 A
#   ewHa   = integral of r over 6500-6630 A (A; positive = net emission here, i.e. the opposite sign of LineForest)
#   npk_Ha = number of separate >3 sigma positive peaks in 6300-6850 A (Zeeman pi + sigma components give >=2)
#   same for H-beta (4800-4930 A window; 4700-5050 A peak count).
import numpy as np
from scipy.ndimage import gaussian_filter1d
SKY = [5577.3, 5889.9, 5895.9, 6300.3, 6363.8, 6498.7, 6533.0, 6553.6, 6577.2, 6604.1, 6827.5, 6834.0, 6863.9, 6923.2, 6949.0, 6978.0, 7276.4, 7316.3, 7340.9, 7369.2, 4358.3, 5460.7]
def _cont(w, f, iv, lo, hi, core, deg=3):
    m = (w > lo) & (w < hi) & np.isfinite(f) & (iv > 0)
    for c in core: m &= ~((w > c[0]) & (w < c[1]))
    for s in SKY: m &= ~(np.abs(w - s) < 6)
    x = (w - (lo + hi) / 2) / ((hi - lo) / 2)
    keep = m.copy()
    for it in range(6):
        if keep.sum() < 50: return None
        p = np.polyfit(x[keep], f[keep], deg, w=np.sqrt(iv[keep]))
        c = np.polyval(p, x); res = (f - c) * np.sqrt(iv)
        new = m & (res > -2.5) & (res < 3.0)
        if (new == keep).all(): break
        keep = new
    return np.polyval(p, x), keep
def metrics(w, f, iv, line=6564.61, lo=5750, hi=7400, core_half=130, win=(6440, 6690), ewwin=(6500, 6630), pkwin=(6300, 6850), sm=3):
    out = dict(sig=np.nan, ew=np.nan, npk=0, lam_pk=np.nan, noise=np.nan, peaks=[])
    r = _cont(w, f, iv, lo, hi, [(line - core_half, line + core_half)])
    if r is None: return out
    c, keep = r
    sel = (w > lo) & (w < hi)
    with np.errstate(invalid="ignore", divide="ignore"): res = np.where(sel & (c > 0), f / c - 1, 0.0)
    bad = ~np.isfinite(res) | (iv <= 0)
    res[bad] = 0.0
    rs = gaussian_filter1d(res, sm)
    # empirical noise of the smoothed residual in the continuum windows (robust)
    cw = keep & sel
    if cw.sum() < 50: return out
    noise = 1.4826 * np.median(np.abs(rs[cw] - np.median(rs[cw])))
    out["noise"] = noise
    # mask sky-line pixels for peak finding
    skym = np.zeros_like(w, bool)
    for s in SKY: skym |= np.abs(w - s) < 5
    z = np.where(skym | bad, 0.0, rs / noise)
    m1 = (w > win[0]) & (w < win[1])
    if m1.any():
        i = np.argmax(np.where(m1, z, -99)); out["sig"] = float(z[i]); out["lam_pk"] = float(w[i])
    m2 = (w > ewwin[0]) & (w < ewwin[1])
    dw = np.gradient(w)
    out["ew"] = float(np.sum(res[m2] * dw[m2]))
    # separate peaks > 3 sigma in the wide window
    m3 = (w > pkwin[0]) & (w < pkwin[1])
    zz = np.where(m3, z, 0); above = zz > 3.0
    pk = []
    i = 0; n = len(zz)
    while i < n:
        if above[i]:
            j = i
            while j < n and above[j]: j += 1
            k = i + np.argmax(zz[i:j]); pk.append((round(float(w[k]), 1), round(float(zz[k]), 1), round(float(w[j - 1] - w[i]), 1)))
            i = j
        else: i += 1
    out["peaks"] = pk; out["npk"] = len(pk)
    return out
def screen(w, f, iv):
    a = metrics(w, f, iv)
    b = metrics(w, f, iv, line=4862.68, lo=4450, hi=5350, core_half=110, win=(4800, 4930), ewwin=(4830, 4900), pkwin=(4700, 5050))
    return a, b
