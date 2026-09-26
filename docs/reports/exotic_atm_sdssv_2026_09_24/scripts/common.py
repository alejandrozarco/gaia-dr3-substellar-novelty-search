# Shared helpers for the exotic-atmosphere lane (SDSS-V DR20 / Astra 0.8.1 BOSS spectra of SnowWhite white dwarfs).
# Downloads are cached in /tmp/fanout/exotic_atm/{spec,visit}; files already fetched by the earlier Zeeman screen in /tmp/mwd/spec
# are read from there (read-only). Every failed download is returned as None and must be logged as a HOLE by the caller.
import os, time, requests, numpy as np, shutil
from astropy.io import fits
BASE = "/tmp/fanout/exotic_atm"
SAS = "https://data.sdss.org/sas/dr20/spectro/astra/0.8.1/spectra"
def _path(sid, kind):
    sid = str(sid); return f"{SAS}/{kind}/{sid[-4:-2]}/{sid[-2:]}/{'mwmStar' if kind=='star' else 'mwmVisit'}-0.8.1-{sid}.fits"
def fetch(sid, kind="star", retries=3):
    sid = str(sid); fn = f"{BASE}/{'spec' if kind=='star' else 'visit'}/{'mwmStar' if kind=='star' else 'mwmVisit'}-0.8.1-{sid}.fits"
    if os.path.exists(fn) and os.path.getsize(fn) > 1000: return fn
    old = f"/tmp/mwd/spec/{os.path.basename(fn)}"
    if os.path.exists(old) and os.path.getsize(old) > 1000: return old
    err = None
    for k in range(retries):
        try:
            r = requests.get(_path(sid, kind), timeout=120)
            if r.status_code == 200 and len(r.content) > 1000:
                open(fn, "wb").write(r.content); return fn
            err = f"HTTP {r.status_code}"
        except Exception as e: err = str(e)[:100]
        time.sleep(2 + 3 * k)
    return None
def load_star(fn):
    """Return list of (telescope_hdu, wave, flux, ivar, snr) for non-empty HDUs of an mwmStar file."""
    out = []
    with fits.open(fn) as h:
        for i in (1, 2):
            if i >= len(h) or h[i].data is None or len(h[i].data) == 0: continue
            d = h[i].data[0]
            w = np.array(d["wavelength"], float); f = np.array(d["flux"], float); iv = np.array(d["ivar"], float)
            out.append((i, w, f, iv, float(d["snr"])))
    return out
def best_star(fn):
    s = load_star(fn)
    if not s: return None
    return max(s, key=lambda t: t[4])
def load_visits(fn):
    """Per-visit spectra with the XCSAO rest-frame shift undone: lambda_obs(bary) = lambda_grid*(1+v/c)."""
    out = []
    with fits.open(fn) as h:
        for i in (1, 2):
            if i >= len(h) or h[i].data is None or len(h[i].data) == 0: continue
            hd = h[i].header; d = h[i].data
            n = hd.get("NPIXELS"); c0 = hd.get("CRVAL"); cd = hd.get("CDELT")
            wg = 10 ** (c0 + cd * np.arange(n))
            for row in d:
                v = float(row["xcsao_v_rad"]) if "xcsao_v_rad" in d.names else np.nan
                out.append(dict(hdu=i, mjd=int(row["mjd"]), v=v, wave_grid=wg, wave_bary=wg * (1 + (0 if not np.isfinite(v) else v) / 299792.458),
                                flux=np.array(row["flux"], float), ivar=np.array(row["ivar"], float), snr=float(row["snr"]),
                                in_stack=bool(row["in_stack"]) if "in_stack" in d.names else None))
    return out
def coadd_visits(fn, wmin=3600, wmax=10300, dlog=1e-4, min_snr=1.0, only=None):
    """Own coadd of all visits (either HDU) on a common log-lambda barycentric grid after undoing each visit's XCSAO shift.
    Returns wave, flux, ivar, list of used (hdu, mjd, v, snr)."""
    vs = load_visits(fn)
    if only is not None: vs = [v for v in vs if (v["hdu"], v["mjd"]) in only]
    grid = 10 ** np.arange(np.log10(wmin), np.log10(wmax), dlog)
    num = np.zeros_like(grid); den = np.zeros_like(grid); used = []
    for v in vs:
        if not (v["snr"] >= min_snr): continue
        f, iv = v["flux"], v["ivar"]; ok = np.isfinite(f) & np.isfinite(iv) & (iv > 0)
        if ok.sum() < 100: continue
        fi = np.interp(grid, v["wave_bary"][ok], f[ok], left=np.nan, right=np.nan)
        ii = np.interp(grid, v["wave_bary"][ok], iv[ok], left=0, right=0)
        g = np.isfinite(fi) & (ii > 0)
        num[g] += fi[g] * ii[g]; den[g] += ii[g]; used.append((v["hdu"], v["mjd"], v["v"], v["snr"]))
    with np.errstate(invalid="ignore", divide="ignore"):
        flux = np.where(den > 0, num / den, np.nan)
    return grid, flux, den, used
