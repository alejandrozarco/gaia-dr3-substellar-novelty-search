"""KK76 Gaia re-anchoring - independent re-measurement (main thread, 2026-09-22).
Written from scratch; does NOT import the referee's scripts. Referee numbers are used only
afterwards, as a comparison."""
import warnings, json, subprocess, urllib.parse, os, math
warnings.filterwarnings("ignore")
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from scipy import ndimage, optimize

DATA = "/tmp/kk76_referee/data"   # public MAST files (read-only use)

def load(root):
    for suf in ("flc", "flt"):
        fn = f"{DATA}/{root}_{suf}.fits"
        if os.path.exists(fn): break
    hd = fits.open(fn)
    sci = hd["SCI", 1].data.astype(float)
    dq = hd["DQ", 1].data.astype(int)
    w = WCS(hd["SCI", 1].header, hd)
    h0 = hd[0].header
    tmid = Time(h0["EXPSTART"] + h0["EXPTIME"] / 2 / 86400.0, format="mjd", scale="utc")
    return dict(root=root, fn=fn, sci=sci, dq=dq, wcs=w, h0=h0, h1=hd["SCI", 1].header, tmid=tmid)

def gaia_cone(ra, dec, rad_arcsec, cap=20000):
    q = (f"SELECT TOP {cap} source_id, ra, dec, ra_error, dec_error, pmra, pmdec, pmra_error, pmdec_error, "
         f"parallax, astrometric_params_solved, phot_g_mean_mag FROM gaiadr3.gaia_source "
         f"WHERE 1=CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{ra},{dec},{rad_arcsec/3600.0}))")
    url = ("https://gea.esac.esa.int/tap-server/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT=json&QUERY="
           + urllib.parse.quote(q))
    for k in range(4):
        out = subprocess.run(["curl", "-sL", "--max-time", "240", url], capture_output=True, text=True).stdout
        try:
            js = json.loads(out); break
        except Exception:
            if k == 3: raise RuntimeError("Gaia TAP failed: " + out[:300])
    cols = [c["name"] for c in js["metadata"]]
    rows = [dict(zip(cols, r)) for r in js["data"]]
    assert len(rows) < cap, "Gaia row cap hit"
    return rows

def gaia_at_epoch(rows, jyear):
    """PM-propagate Gaia DR3 (epoch 2016.0) to jyear. Returns arrays; 2-parameter sources flagged."""
    dt = jyear - 2016.0
    ra = np.array([r["ra"] for r in rows]); de = np.array([r["dec"] for r in rows])
    pmra = np.array([r["pmra"] if r["pmra"] is not None else np.nan for r in rows])
    pmde = np.array([r["pmdec"] if r["pmdec"] is not None else np.nan for r in rows])
    epmra = np.array([r["pmra_error"] if r["pmra_error"] is not None else np.nan for r in rows])
    epmde = np.array([r["pmdec_error"] if r["pmdec_error"] is not None else np.nan for r in rows])
    era = np.array([r["ra_error"] for r in rows]); ede = np.array([r["dec_error"] for r in rows])
    g = np.array([r["phot_g_mean_mag"] if r["phot_g_mean_mag"] is not None else np.nan for r in rows])
    has_pm = np.isfinite(pmra) & np.isfinite(pmde)
    ra_t = ra + np.where(has_pm, pmra, 0) * dt / 3.6e6 / np.cos(np.radians(de))
    de_t = de + np.where(has_pm, pmde, 0) * dt / 3.6e6
    # 1-sigma position error at epoch (mas); 2-par sources get an assumed 6 mas/yr unknown PM
    sig = np.where(has_pm, np.hypot(np.hypot(era, epmra * dt), np.hypot(ede, epmde * dt)) / np.sqrt(2),
                   np.hypot(np.hypot(era, ede) / np.sqrt(2), 6.0 * abs(dt)))
    return dict(ra=ra_t, dec=de_t, g=g, has_pm=has_pm, sig_mas=sig, sid=[str(r["source_id"]) for r in rows])

def tangent(ra, dec, ra0, dec0):
    """gnomonic projection -> xi, eta in arcsec"""
    ra, dec, ra0, dec0 = map(np.radians, (ra, dec, ra0, dec0))
    cosc = np.sin(dec0) * np.sin(dec) + np.cos(dec0) * np.cos(dec) * np.cos(ra - ra0)
    xi = np.cos(dec) * np.sin(ra - ra0) / cosc
    eta = (np.cos(dec0) * np.sin(dec) - np.sin(dec0) * np.cos(dec) * np.cos(ra - ra0)) / cosc
    return np.degrees(xi) * 3600, np.degrees(eta) * 3600

def untangent(xi, eta, ra0, dec0):
    xi, eta = np.radians(np.asarray(xi) / 3600), np.radians(np.asarray(eta) / 3600)
    ra0, dec0 = np.radians(ra0), np.radians(dec0)
    rho = np.hypot(xi, eta); c = np.arctan(rho)
    with np.errstate(invalid="ignore", divide="ignore"):
        dec = np.arcsin(np.cos(c) * np.sin(dec0) + np.where(rho > 0, eta * np.sin(c) * np.cos(dec0) / rho, 0))
        ra = ra0 + np.arctan2(xi * np.sin(c), rho * np.cos(dec0) * np.cos(c) - eta * np.sin(dec0) * np.sin(c))
    return np.degrees(ra) % 360, np.degrees(dec)

def background(img, box=41):
    b = ndimage.median_filter(np.nan_to_num(img, nan=np.nanmedian(img)), size=box)
    r = img - b
    mad = np.nanmedian(np.abs(r - np.nanmedian(r))) * 1.4826
    return b, mad

def detect_components(img, noise, nsig=5.0, sm=1.2, minpix=5, pad=3):
    """connected-component detection with flux-weighted (first-moment) centroids -> good for trails"""
    s = ndimage.gaussian_filter(np.nan_to_num(img), sm)
    ns = np.nanmedian(np.abs(s - np.nanmedian(s))) * 1.4826
    lab, n = ndimage.label(s > nsig * ns)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None: continue
        npix = (lab[sl] == i).sum()
        if npix < minpix: continue
        y0, y1 = max(sl[0].start - pad, 0), min(sl[0].stop + pad, img.shape[0])
        x0, x1 = max(sl[1].start - pad, 0), min(sl[1].stop + pad, img.shape[1])
        st = np.clip(np.nan_to_num(img[y0:y1, x0:x1]), 0, None)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        f = st.sum()
        if f <= 0: continue
        xc, yc = (st * xx).sum() / f, (st * yy).sum() / f
        out.append((xc, yc, f, npix))
    return np.array(out) if out else np.zeros((0, 4))

def detect_peaks(img, noise, nsig=6.0, sm=1.0, win=2):
    """local-maximum detection + windowed first-moment centroid -> good for crowded, round PSFs"""
    s = ndimage.gaussian_filter(np.nan_to_num(img), sm)
    ns = np.nanmedian(np.abs(s - np.nanmedian(s))) * 1.4826
    pk = (s == ndimage.maximum_filter(s, size=2 * win + 1)) & (s > nsig * ns)
    ys, xs = np.nonzero(pk)
    out = []
    for x, y in zip(xs, ys):
        if x < win or y < win or x >= img.shape[1] - win or y >= img.shape[0] - win: continue
        st = np.clip(np.nan_to_num(img[y - win:y + win + 1, x - win:x + win + 1]), 0, None)
        yy, xx = np.mgrid[y - win:y + win + 1, x - win:x + win + 1]
        f = st.sum()
        if f <= 0: continue
        out.append(((st * xx).sum() / f, (st * yy).sum() / f, f, 0))
    return np.array(out) if out else np.zeros((0, 4))

def find_offset(det_xy, gxy, search, binsz=1.0):
    dx = (gxy[:, None, 0] - det_xy[None, :, 0]).ravel(); dy = (gxy[:, None, 1] - det_xy[None, :, 1]).ravel()
    m = (np.abs(dx) < search) & (np.abs(dy) < search)
    nb = int(2 * search / binsz)
    H, xe, ye = np.histogram2d(dx[m], dy[m], bins=nb, range=[[-search, search], [-search, search]])
    H = ndimage.gaussian_filter(H, 1.0)
    i, j = np.unravel_index(np.argmax(H), H.shape)
    return (xe[i] + xe[i + 1]) / 2, (ye[j] + ye[j + 1]) / 2

def match(det_xy, gxy, off, tol):
    pairs = []
    for k, (gx, gy) in enumerate(gxy):
        d = np.hypot(det_xy[:, 0] + off[0] - gx, det_xy[:, 1] + off[1] - gy)
        j = np.argmin(d) if len(d) else None
        if j is not None and d[j] < tol: pairs.append((k, j))
    # enforce one-to-one
    seen, uniq = set(), []
    for k, j in pairs:
        if j in seen: continue
        seen.add(j); uniq.append((k, j))
    return uniq

def gauss2d(p, xx, yy):
    a, x0, y0, sx, sy, th, b = p
    ct, st = np.cos(th), np.sin(th)
    xr = (xx - x0) * ct + (yy - y0) * st; yr = -(xx - x0) * st + (yy - y0) * ct
    return a * np.exp(-0.5 * ((xr / sx) ** 2 + (yr / sy) ** 2)) + b

def fit_source(img, x0, y0, half=6, sig0=1.2, clip=5.0, iters=3, err=None):
    """elliptical-Gaussian + constant fit with iterative outlier (cosmic-ray) masking.
    Returns x, y, sigx, sigy (pixel 1-sigma, chi2-scaled), flux, fwhm, n_masked"""
    xi, yi = int(round(x0)), int(round(y0))
    st = img[yi - half:yi + half + 1, xi - half:xi + half + 1].astype(float)
    yy, xx = np.mgrid[yi - half:yi + half + 1, xi - half:xi + half + 1]
    good = np.isfinite(st)
    b0 = np.nanmedian(np.concatenate([st[0], st[-1], st[:, 0], st[:, -1]]))
    p = [np.nanmax(st) - b0, x0, y0, sig0, sig0, 0.0, b0]
    for it in range(iters):
        res = optimize.least_squares(lambda q: (gauss2d(q, xx[good], yy[good]) - st[good]), p,
                                     bounds=([0, x0 - 3, y0 - 3, 0.4, 0.4, -np.pi, -np.inf],
                                             [np.inf, x0 + 3, y0 + 3, 4.0, 4.0, np.pi, np.inf]))
        p = res.x
        r = st - gauss2d(p, xx, yy)
        s = np.nanmedian(np.abs(r[good])) * 1.4826
        newgood = np.isfinite(st) & (np.abs(r) < clip * s)
        if (newgood == good).all(): break
        good = newgood
    J = res.jac; dof = max(good.sum() - len(p), 1)
    chi2 = (res.fun ** 2).sum() / dof
    try:
        cov = np.linalg.inv(J.T @ J) * chi2
        ex, ey = np.sqrt(cov[1, 1]), np.sqrt(cov[2, 2])
    except np.linalg.LinAlgError:
        ex = ey = np.nan
    flux = 2 * np.pi * p[0] * p[3] * p[4]
    return dict(x=p[1], y=p[2], ex=ex, ey=ey, flux=flux, sx=p[3], sy=p[4], nmask=int((~good).sum()), amp=p[0], bkg=p[6])

def horizons_hst_vectors(jd_utc_list):
    base = "https://ssd.jpl.nasa.gov/api/horizons.api"
    params = {"format": "json", "COMMAND": "-48", "OBJ_DATA": "NO", "MAKE_EPHEM": "YES", "EPHEM_TYPE": "VECTORS",
              "CENTER": "500@399", "REF_PLANE": "FRAME", "REF_SYSTEM": "ICRF", "VEC_TABLE": "1",
              "OUT_UNITS": "KM-S", "TIME_TYPE": "UT", "TLIST_TYPE": "JD", "CSV_FORMAT": "YES",
              "TLIST": " ".join(f"{j:.7f}" for j in jd_utc_list)}
    url = base + "?" + urllib.parse.urlencode(params)
    js = json.loads(subprocess.run(["curl", "-sL", "--max-time", "120", url], capture_output=True, text=True).stdout)
    txt = js["result"]; body = txt.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
    out = []
    for line in body:
        f = [x.strip() for x in line.split(",")]
        out.append((float(f[0]), float(f[2]), float(f[3]), float(f[4])))
    assert len(out) == len(jd_utc_list), txt[-800:]
    return out

def horizons_hstcentric_radec(target, jd_utc_list):
    base = "https://ssd.jpl.nasa.gov/api/horizons.api"
    params = {"format": "json", "COMMAND": f"'{target}'", "OBJ_DATA": "NO", "MAKE_EPHEM": "YES",
              "EPHEM_TYPE": "OBSERVER", "CENTER": "500@-48", "QUANTITIES": "1", "ANG_FORMAT": "DEG",
              "EXTRA_PREC": "YES", "CSV_FORMAT": "YES", "TIME_TYPE": "UT", "TLIST_TYPE": "JD",
              "TLIST": " ".join(f"{j:.7f}" for j in jd_utc_list)}
    url = base + "?" + urllib.parse.urlencode(params)
    js = json.loads(subprocess.run(["curl", "-sL", "--max-time", "120", url], capture_output=True, text=True).stdout)
    txt = js["result"]; body = txt.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
    out = []
    for line in body:
        f = [x.strip() for x in line.split(",")]
        out.append((float(f[3]), float(f[4])))
    assert len(out) == len(jd_utc_list), txt[-800:]
    return out
