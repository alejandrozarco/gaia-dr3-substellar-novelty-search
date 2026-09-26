# Shared loaders / measurement helpers for the adversarial spectroscopy review of Gaia DR3 5208047381438507520.
import numpy as np
from astropy.io import fits
C = 299792.458
SPEC = "/tmp/hotdq/review2/spec_agent/spec"
TARGET = "/tmp/hotdq/review2/raw/mwmVisit-0.8.1-95077848.fits"

def load_visits(path, undo=True):
    """Return list of dicts (one per BOSS visit with data): w (barycentric vacuum), f, iv, flags, wresl, meta."""
    out = []
    with fits.open(path) as h:
        for k in (1, 2):
            hd = h[k].header; d = h[k].data
            if d is None or len(d) == 0:
                continue
            wg = 10 ** (hd["CRVAL"] + hd["CDELT"] * np.arange(hd["NPIXELS"]))
            for r in d:
                f = np.array(r["flux"], float); iv = np.array(r["ivar"], float)
                if not np.any(iv > 0):
                    continue
                v = float(r["xcsao_v_rad"]); ins = bool(r["in_stack"])
                w = wg * (1 + v / C) if (undo and ins and np.isfinite(v)) else wg.copy()
                out.append(dict(w=w, wg=wg, f=f, iv=iv, flags=np.array(r["pixel_flags"]), wresl=np.array(r["wresl"], float),
                                snr=float(r["snr"]), mjd=int(r["mjd"]), in_stack=ins, xv=v, obs=hd.get("OBSRVTRY"), nexp=int(r["n_exp"])))
    return out

def best_visit(path, undo=True):
    vs = load_visits(path, undo)
    return max(vs, key=lambda x: x["snr"]) if vs else None

def coadd(path, undo=True, rest_v=None):
    """ivar-weighted coadd of all visits on the first visit grid after shifting each to barycentric frame (and optionally to rest via rest_v)."""
    vs = load_visits(path, undo)
    if not vs:
        return None
    wref = vs[0]["wg"]
    F = np.zeros_like(wref); W = np.zeros_like(wref)
    for v in vs:
        w = v["w"] if rest_v is None else v["w"] / (1 + rest_v / C)
        ok = v["iv"] > 0
        fi = np.interp(wref, w[ok], v["f"][ok], left=np.nan, right=np.nan)
        ii = np.interp(wref, w[ok], v["iv"][ok], left=0, right=0)
        g = np.isfinite(fi) & (ii > 0)
        F[g] += fi[g] * ii[g]; W[g] += ii[g]
    f = np.where(W > 0, F / np.where(W > 0, W, 1), np.nan)
    return dict(w=wref, f=f, iv=W, snr=np.sqrt(np.nansum([x["snr"] ** 2 for x in vs])), n=len(vs))

def linear_cont(w, f, iv, windows):
    sel = np.zeros_like(w, bool)
    for a, b in windows:
        sel |= (w > a) & (w < b)
    sel &= (iv > 0) & np.isfinite(f)
    # robust: median in each window, straight line through window medians
    xs, ys = [], []
    for a, b in windows:
        s = (w > a) & (w < b) & (iv > 0) & np.isfinite(f)
        if s.sum() >= 3:
            xs.append(np.median(w[s])); ys.append(np.median(f[s]))
    p = np.polyfit(xs, ys, 1) if len(xs) >= 2 else [0, ys[0]]
    return np.polyval(p, w)

def ew(w, f, iv, lam0, halfw, side, mask_centres=(), mask_hw=4.0, vel=0.0):
    """Equivalent width (A, positive = absorption) of a line at lam0*(1+vel/c) integrated over +-halfw,
    continuum = straight line through the medians of the two sideband windows 'side' (offsets from centre, A).
    mask_centres (observed wavelengths) are replaced by linear interpolation before integrating. Returns ew, err, core_depth."""
    lc = lam0 * (1 + vel / C)
    wins = [(lc + a, lc + b) for a, b in side]
    cont = linear_cont(w, f, iv, wins)
    n = f / cont; en = np.where(iv > 0, 1 / np.sqrt(np.where(iv > 0, iv, 1)) / cont, np.inf)
    good = (iv > 0) & np.isfinite(n)
    n2 = n.copy()
    m = np.zeros_like(w, bool)
    for mc in mask_centres:
        m |= np.abs(w - mc) < mask_hw
    ok = good & ~m
    n2[~ok] = np.interp(w[~ok], w[ok], n[ok])
    s = np.abs(w - lc) < halfw
    dw = np.gradient(w)
    E = np.sum((1 - n2[s]) * dw[s]); eE = np.sqrt(np.sum((en[s & ok] * dw[s & ok]) ** 2))
    core = np.abs(w - lc) < 3.0
    cd = 1 - np.average(n2[core], weights=1 / en[core] ** 2) if np.any(core & ok) else np.nan
    return E, eE, cd, n2, cont
