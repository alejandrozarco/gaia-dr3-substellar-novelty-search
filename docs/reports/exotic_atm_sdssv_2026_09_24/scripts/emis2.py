# Local-bump (prominence) Balmer-emission metric, robust against continuum misfits at absorption wings:
# smoothed flux (Gaussian sigma=3 px) divided by a very smooth running-median continuum (401 px), then scipy find_peaks with
# prominence measured against the neighbouring bases within wlen ~ 120 A. Noise = per-pixel error of the smoothed flux
# (propagated from ivar, scaled by an empirical factor from the MAD of first differences). Peaks within +-4 A of strong sky/nebular
# lines are flagged. Reports the most significant bump in the H-alpha (6380-6760 A) and H-beta (4700-5020 A) windows.
import numpy as np
from scipy.ndimage import gaussian_filter1d, median_filter
from scipy.signal import find_peaks
NEB = [6549.9, 6564.6, 6585.3, 6718.3, 6732.7, 6302.0, 6365.5, 4960.3, 5008.2, 4862.7]  # vacuum nebular/sky-emission lines
def bumps(w, f, iv, lo, hi, sm=3):
    good = np.isfinite(f) & (iv > 0)
    if good.sum() < 500: return None
    ff = np.where(good, f, np.interp(w, w[good], f[good]))
    fs = gaussian_filter1d(ff, sm)
    err = np.where(good, 1 / np.sqrt(np.where(iv > 0, iv, np.inf)), np.nan)
    es = np.sqrt(gaussian_filter1d(np.nan_to_num(err, nan=np.nanmedian(err)) ** 2, sm) / (2 * np.sqrt(np.pi) * sm))
    m = (w > lo) & (w < hi)
    if m.sum() < 50: return None
    idx = np.where(m)[0]
    dw = np.median(np.diff(w[m]))
    pk, pr = find_peaks(fs[idx], prominence=0, wlen=int(120 / dw), width=1)
    out = []
    for j, p in enumerate(pk):
        i = idx[p]; s = pr["prominences"][j] / es[i]
        fw = pr["widths"][j] * dw
        neb = bool(any(abs(w[i] - l) < 4 for l in NEB) and (pr["widths"][j] * dw) < 8.0)  # v2: only NARROW bumps at nebular/sky wavelengths are rejected
        out.append((round(float(w[i]), 1), round(float(s), 1), round(float(fw), 1), round(float(pr["prominences"][j] / fs[i]), 3), neb))
    out.sort(key=lambda t: -t[1])
    return out
def metric(w, f, iv):
    a = bumps(w, f, iv, 6150, 7000); b = bumps(w, f, iv, 4620, 5120)  # v2: wider windows (sigma components up to ~20 MG at H-alpha, ~23 MG at H-beta)
    def best(lst, minw=6.0):
        c = [t for t in (lst or []) if t[2] >= minw and not t[4]]
        return c[0] if c else (np.nan, 0.0, np.nan, np.nan, False)
    def nsig(lst, thr=4.0, minw=6.0): return sum(1 for t in (lst or []) if t[1] > thr and t[2] >= minw and not t[4])
    ba, bb = best(a), best(b)
    narrow = [t for t in (a or []) if t[4] and t[1] > 5]
    return dict(Ha_lam=ba[0], Ha_sig=ba[1], Ha_fwhm=ba[2], Ha_rel=ba[3], Ha_n=nsig(a), Hb_lam=bb[0], Hb_sig=bb[1], Hb_fwhm=bb[2], Hb_rel=bb[3], Hb_n=nsig(b),
                neb_n=len(narrow), top_Ha=(a or [])[:4], top_Hb=(b or [])[:4])
def metric_ctrl(w, f, iv):
    """Same bump statistic in line-free control windows (5230-5560, 5600-5860 A) to self-calibrate the noise/wiggle level."""
    out = []
    for lo, hi in ((5230, 5560), (5600, 5860)):
        b = bumps(w, f, iv, lo, hi) or []
        b = [t for t in b if t[2] >= 6.0 and abs(t[0] - 5578.9) > 5]
        out.append(b[0][1] if b else 0.0)
    return max(out)
