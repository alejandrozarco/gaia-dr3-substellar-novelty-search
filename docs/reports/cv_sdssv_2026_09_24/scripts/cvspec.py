# Spectral tools for the CV lane (SDSS-V DR20, Astra 0.8.1 mwmVisit/mwmStar files in spec/).
# Key point (brief): Astra resamples every visit to a "rest frame" using xcsao_v_rad, which is meaningless for WDs/CVs.
# Here every visit is put back on its barycentric wavelength scale, lambda_bary = lambda_grid * (1 + v/c), and the
# visits are re-coadded with inverse-variance weights on the native log-linear grid. Vacuum wavelengths throughout.
import numpy as np
from astropy.io import fits

C_KMS = 299792.458
# vacuum wavelengths (Angstrom)
LINES = {"Ha": 6564.61, "Hb": 4862.68, "Hg": 4341.68, "Hd": 4102.89, "HeI4472": 4472.73, "HeI4922": 4923.30, "HeI5016": 5017.08,
         "HeI5876": 5877.25, "HeI6678": 6679.99, "HeI7065": 7067.20, "HeII4686": 4687.02, "HeII5411": 5413.03,
         "Bowen4645": 4645.0, "FeII5169": 5170.47, "CaII8542": 8544.44, "CaII8662": 8664.52, "OI7774": 7776.0, "NaD": 5891.6, "OIII4960": 4960.30, "OIII5008": 5008.24, "NII6585": 6585.27, "SII6718": 6718.29, "SII6733": 6732.67, "OII3728": 3728.5}


def grid(h):
    return 10 ** (h.header["CRVAL"] + h.header["CDELT"] * np.arange(h.header["NPIXELS"]))


def load_visits(sid, specdir="spec"):
    """Return list of dicts (one per BOSS visit, APO and LCO) with barycentric wavelength, flux, ivar and metadata."""
    out = []
    with fits.open(f"{specdir}/mwmVisit-0.8.1-{sid}.fits") as h:
        for ext in (1, 2):
            hd = h[ext]
            if hd.header.get("NAXIS2", 0) == 0:
                continue
            lg = grid(hd)
            d = hd.data
            for k in range(len(d)):
                fl = np.array(d["flux"][k], float); iv = np.array(d["ivar"][k], float)
                if fl.size == 0 or not np.any(iv > 0):
                    continue
                v = float(d["xcsao_v_rad"][k]) if np.isfinite(d["xcsao_v_rad"][k]) else 0.0
                # VERIFIED 2026-09-23 by cross-correlation against the BOSS pipeline spec-full files (barycentric, no XCSAO
                # shift): Astra applied the XCSAO shift ONLY to in_stack=True visits (5/5 shifted); in_stack=False visits
                # (3/3) are already on the barycentric grid. So undo only when in_stack is True.
                ins = bool(d["in_stack"][k]); vapp = v if ins else 0.0
                out.append(dict(ext=hd.header["EXTNAME"], mjd=int(d["mjd"][k]), v_xcsao=v, v_applied=vapp, snr=float(d["snr"][k]),
                                in_stack=ins, lam_grid=lg, lam=lg * (1 + vapp / C_KMS), flux=fl, ivar=iv,
                                pixflags=np.array(d["pixel_flags"][k]) if "pixel_flags" in d.names else None,
                                tai_beg=float(d["tai_beg"][k]) if "tai_beg" in d.names else np.nan,
                                exptime=float(d["exptime"][k]) if "exptime" in d.names else np.nan, fieldid=int(d["fieldid"][k])))
    return out


def load_star(sid, specdir="spec"):
    out = []
    with fits.open(f"{specdir}/mwmStar-0.8.1-{sid}.fits") as h:
        for ext in (1, 2):
            hd = h[ext]
            if hd.header.get("NAXIS2", 0) == 0:
                continue
            d = hd.data
            out.append(dict(ext=hd.header["EXTNAME"], lam=np.array(d["wavelength"][0], float) if "wavelength" in d.names else grid(hd),
                            flux=np.array(d["flux"][0], float), ivar=np.array(d["ivar"][0], float), snr=float(d["snr"][0]),
                            v_rad=float(d["v_rad"][0]), n_visits=int(d["n_visits"][0])))
    return out


def coadd(visits, lam_out=None, min_snr=0.0, use=None):
    """Inverse-variance coadd of barycentric-frame visits onto lam_out (default: native grid 3566-10390 A)."""
    if lam_out is None:
        lam_out = 10 ** (3.5523 + 0.0001 * np.arange(4648))
    num = np.zeros_like(lam_out); den = np.zeros_like(lam_out); n = 0
    for i, v in enumerate(visits):
        if use is not None and i not in use:
            continue
        if v["snr"] < min_snr:
            continue
        good = (v["ivar"] > 0) & np.isfinite(v["flux"])
        if good.sum() < 100:
            continue
        f = np.interp(lam_out, v["lam"][good], v["flux"][good], left=np.nan, right=np.nan)
        iv = np.interp(lam_out, v["lam"][good], v["ivar"][good], left=0, right=0)
        ok = np.isfinite(f) & (iv > 0)
        num[ok] += f[ok] * iv[ok]; den[ok] += iv[ok]; n += 1
    with np.errstate(invalid="ignore", divide="ignore"):
        fl = np.where(den > 0, num / den, np.nan)
    return lam_out, fl, den, n


def line_ew(lam, fl, iv, l0, half=30.0, side=(40.0, 80.0), vshift=0.0, windows=None):
    """Emission EW (A, positive = emission) with a linear continuum from sidebands, its 1-sigma error, S/N and a crude
    FWHM (km/s) of the continuum-subtracted profile. windows = explicit list of (lo, hi) continuum intervals (A) or None
    for symmetric sidebands at l0 +- side. vshift (km/s) moves the line centre."""
    l0 = l0 * (1 + vshift / C_KMS)
    if windows is None:
        windows = [(l0 - side[1], l0 - side[0]), (l0 + side[0], l0 + side[1])]
    sb = np.zeros_like(lam, bool)
    for lo, hi in windows:
        sb |= (lam > lo) & (lam < hi)
    sb &= np.isfinite(fl) & (iv > 0)
    win = (lam > l0 - half) & (lam < l0 + half) & np.isfinite(fl) & (iv > 0)
    nan = dict(ew=np.nan, e_ew=np.nan, sig=np.nan, fwhm=np.nan, cont=np.nan)
    if sb.sum() < 8 or win.sum() < 5:
        return nan
    x, y = lam[sb] - l0, fl[sb]; m = np.ones_like(x, bool)
    for _ in range(3):
        if m.sum() < 5:
            return nan
        p = np.polyfit(x[m], y[m], 1); r = y - np.polyval(p, x); s = 1.4826 * np.median(np.abs(r[m] - np.median(r[m])))
        m = np.abs(r) < 3 * s + 1e-30
    if m.sum() < 5:
        return nan
    c0 = np.polyval(p, 0.0)
    if not np.isfinite(c0) or c0 <= 0:
        nan["cont"] = c0; return nan
    cont = np.polyval(p, lam[win] - l0)
    dl = np.gradient(lam)[win]
    exc = fl[win] - cont
    ew = np.sum(exc * dl) / c0
    e_ph = np.sqrt(np.sum(dl ** 2 / iv[win])) / c0
    e_cont = s * np.sum(dl) / c0 / np.sqrt(max(m.sum(), 1))   # continuum-level uncertainty over the window
    e_tot = float(np.hypot(e_ph, e_cont))
    fwhm = np.nan
    if ew > 0:
        pk = np.nanmax(exc); above = lam[win][exc > pk / 2]
        if above.size >= 2:
            fwhm = (above.max() - above.min()) / l0 * C_KMS
    return dict(ew=float(ew), e_ew=e_tot, sig=float(ew / e_tot) if e_tot > 0 else np.nan, fwhm=float(fwhm), cont=float(c0))


# explicit continuum windows (vacuum A) chosen to avoid neighbouring emission lines seen in CVs
WINDOWS = {"Ha": [(6480, 6520), (6610, 6650)], "Hb": [(4780, 4815), (4950, 4990)], "Hg": [(4260, 4295), (4385, 4420)],
           "Hd": [(4030, 4060), (4140, 4170)], "HeI4472": [(4415, 4440), (4500, 4530)], "HeI4922": [(4885, 4905), (4945, 4990)],
           "HeI5016": [(4950, 4990), (5040, 5060)], "HeI5876": [(5820, 5850), (5910, 5940)], "HeI6678": [(6630, 6655), (6705, 6730)],
           "HeI7065": [(7020, 7045), (7090, 7115)], "HeII4686": [(4590, 4625), (4730, 4760)], "HeII5411": [(5360, 5390), (5440, 5470)],
           "Bowen4645": [(4590, 4625), (4730, 4760)], "FeII5169": [(5130, 5150), (5190, 5210)], "CaII8542": [(8515, 8530), (8565, 8585)],
           "CaII8662": [(8620, 8640), (8690, 8710)], "OI7774": [(7740, 7760), (7795, 7815)], "NaD": [(5850, 5870), (5910, 5930)],
           "OIII4960": [(4938, 4950), (4970, 4985)], "OIII5008": [(4985, 4998), (5028, 5040)],
           "NII6585": [(6600, 6612), (6620, 6640)], "SII6718": [(6690, 6708), (6745, 6765)], "SII6733": [(6690, 6708), (6745, 6765)],
           "OII3728": [(3700, 3715), (3745, 3760)]}
HALF = {"Ha": 35.0, "Hb": 30.0, "Hg": 28.0, "Hd": 25.0, "HeII4686": 18.0, "Bowen4645": 10.0, "HeI5876": 18.0, "HeI6678": 16.0,
        "HeI4472": 16.0, "HeI4922": 14.0, "HeI5016": 12.0, "HeI7065": 16.0, "HeII5411": 16.0, "FeII5169": 10.0, "CaII8542": 12.0,
        "CaII8662": 12.0, "OI7774": 10.0, "NaD": 8.0, "OIII4960": 5.0, "OIII5008": 5.0, "NII6585": 4.0, "SII6718": 4.0, "SII6733": 4.0, "OII3728": 5.0}


def measure_all(lam, fl, iv, vshift=0.0):
    return {k: line_ew(lam, fl, iv, l0, half=HALF[k], windows=[(a * (1 + vshift / C_KMS), b * (1 + vshift / C_KMS)) for a, b in WINDOWS[k]],
                       vshift=vshift) for k, l0 in LINES.items()}
