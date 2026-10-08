"""Survey time stamps -> mid-exposure BJD_TDB (ATLAS, ZTF, Gaia DR3 epoch photometry).

ATLAS forced photometry: column MJD is the UTC MJD of the START of the exposure; all exposures are 30 s and the value is not
barycentred (https://fallingstar-data.com/forcedphot/resultdesc/). Mid-exposure = MJD + 15 s.

ZTF (IRSA light-curve service, ZTF DR): column `mjd` is the UTC MJD of the START of the exposure; `hjd` is the HJD (UTC) at
MID-exposure (hjd - heliocentric(mjd) = exptime/2 to < 0.1 ms, verified on 2026-10-07 for exptime 20-450 s). Most exposures
are 30 s, but 20-450 s occur, so use the `exptime` column, not a fixed 15 s. `hjd` is on the UTC scale: using it as BJD_TDB
is ~69 s early (TDB - UTC = 69.18 s) plus the heliocentric-barycentric difference (up to ~4 s).
ZTF forced photometry (ZFPS, column `jd`) and ZTF alerts (`jd`; ALeRCE `mjd` = jd - 2400000.5) are also exposure START (UTC).

Gaia DR3 epoch photometry: TimeG/TimeBP/TimeRP + 2455197.5 is a barycentric JD in TCB, not TDB. TCB - TDB grows linearly
(L_B = 1.550519768e-8); at Gaia DR3 epochs (2014-2017) it is 18.5-19.3 s, so TimeG + 2455197.5 used as BJD_TDB is ~19 s late.

Usage:
    from atlas_time import atlas_bjd_tdb, ztf_bjd_tdb, ztf_hjd_utc, gaia_bjd_tdb
    bjd = atlas_bjd_tdb(mjd_column, ra_deg, dec_deg)
    bjd = ztf_bjd_tdb(df.mjd, ra_deg, dec_deg, exptime_s=df.exptime)    # IRSA DR light curve
    bjd = ztf_bjd_tdb(zfps.jd - 2400000.5, ra, dec, exptime_s=zfps.exptime)   # ZFPS / alerts (default 30 s)
    bjd = gaia_bjd_tdb(epphot.TimeG)                                       # Gaia DR3 epoch photometry

The ATLAS barycentric correction uses the geocentre (ATLAS sites differ from it by < 21 ms); ZTF uses Palomar.
"""
import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u

ATLAS_EXPTIME_S = 30.0
HALF_EXPOSURE_D = ATLAS_EXPTIME_S / 2 / 86400.0      # 0.000173611 d
ZTF_DEFAULT_EXPTIME_S = 30.0
GAIA_DR3_TIME_ZERO_JD = 2455197.5                    # TimeG = BJD(TCB) - 2455197.5
_GEO = EarthLocation.from_geocentric(0, 0, 0, unit="m")
PALOMAR = EarthLocation.from_geodetic(lon=-116.8597 * u.deg, lat=33.3563 * u.deg, height=1712 * u.m)


def _bary(t, ra_deg, dec_deg, kind="barycentric"):
    c0 = SkyCoord(np.asarray(ra_deg, dtype=float) * u.deg, np.asarray(dec_deg, dtype=float) * u.deg)
    return t.light_travel_time(c0, kind=kind)


# --- ATLAS -------------------------------------------------------------------------------------------------------------------
def atlas_mid_time(mjd_start):
    """astropy Time (UTC, geocentre) at mid-exposure from the ATLAS MJD column (exposure start)."""
    return Time(np.asarray(mjd_start, dtype=float) + HALF_EXPOSURE_D, format="mjd", scale="utc", location=_GEO)


def atlas_bjd_tdb(mjd_start, ra_deg, dec_deg):
    """BJD_TDB (JD, float array) at mid-exposure for a target at (ra_deg, dec_deg) ICRS."""
    t = atlas_mid_time(mjd_start)
    return (t.tdb + _bary(t, ra_deg, dec_deg)).jd


def atlas_hjd_utc(mjd_start, ra_deg, dec_deg):
    """HJD (UTC) at mid-exposure, as VSX expects in its Epoch field."""
    t = atlas_mid_time(mjd_start)
    return (t.utc + _bary(t, ra_deg, dec_deg, "heliocentric")).jd


# --- ZTF ---------------------------------------------------------------------------------------------------------------------
def ztf_mid_time(mjd_start, exptime_s=ZTF_DEFAULT_EXPTIME_S):
    """astropy Time (UTC, Palomar) at mid-exposure from a ZTF exposure-start MJD (IRSA `mjd`, or ZFPS/alert jd - 2400000.5)."""
    half = np.asarray(exptime_s, dtype=float) / 2 / 86400.0
    return Time(np.asarray(mjd_start, dtype=float) + half, format="mjd", scale="utc", location=PALOMAR)


def ztf_bjd_tdb(mjd_start, ra_deg, dec_deg, exptime_s=ZTF_DEFAULT_EXPTIME_S):
    """BJD_TDB (JD) at mid-exposure from a ZTF exposure-start MJD. Pass the `exptime` column where it exists."""
    t = ztf_mid_time(mjd_start, exptime_s)
    return (t.tdb + _bary(t, ra_deg, dec_deg)).jd


def ztf_hjd_utc(mjd_start, ra_deg, dec_deg, exptime_s=ZTF_DEFAULT_EXPTIME_S):
    """HJD (UTC) at mid-exposure (equals the IRSA `hjd` column; VSX Epoch convention)."""
    t = ztf_mid_time(mjd_start, exptime_s)
    return (t.utc + _bary(t, ra_deg, dec_deg, "heliocentric")).jd


def ztf_hjd_to_bjd_tdb(hjd_utc, ra_deg, dec_deg):
    """BJD_TDB from the IRSA `hjd` column (HJD_UTC, mid-exposure); for files that kept only `hjd`. Accurate to ~1 ms."""
    hjd_utc = np.asarray(hjd_utc, dtype=float)
    t = Time(hjd_utc, format="jd", scale="utc", location=PALOMAR)
    for _ in range(3):                                         # geocentric UTC such that UTC + helio(UTC) = hjd
        t = Time(hjd_utc, format="jd", scale="utc", location=PALOMAR) - _bary(t, ra_deg, dec_deg, "heliocentric")
    return (t.tdb + _bary(t, ra_deg, dec_deg)).jd


# --- Gaia DR3 epoch photometry -----------------------------------------------------------------------------------------------
def gaia_bjd_tdb(time_gaia):
    """BJD_TDB (JD) from Gaia DR3 epoch-photometry TimeG/TimeBP/TimeRP (= BJD_TCB - 2455197.5)."""
    t = Time(np.full(np.shape(time_gaia), GAIA_DR3_TIME_ZERO_JD), np.asarray(time_gaia, dtype=float), format="jd", scale="tcb")
    return t.tdb.jd


if __name__ == "__main__":
    c = (45.8, -42.1)
    # ATLAS: +15 s exactly
    m = np.array([59000.0, 60000.5])
    t_start = Time(m, format="mjd", scale="utc", location=_GEO)
    d = (atlas_bjd_tdb(m, *c) - (t_start.tdb + _bary(t_start, *c)).jd) * 86400
    print("ATLAS mid-exposure shift (s):", d); assert np.all(np.abs(d - 15.0) < 1e-3)
    # ZTF: +exptime/2 (to the change in light travel time over half an exposure); hjd round trip
    ex = np.array([30.0, 300.0]); t_start = Time(m, format="mjd", scale="utc", location=PALOMAR)
    d = (ztf_bjd_tdb(m, *c, ex) - (t_start.tdb + _bary(t_start, *c)).jd) * 86400
    print("ZTF mid-exposure shift (s):", d); assert np.all(np.abs(d - ex / 2) < 0.05)   # light time changes by <= 1e-4 s/s over the exposure
    h = ztf_hjd_utc(m, *c, ex); d = (ztf_hjd_to_bjd_tdb(h, *c) - ztf_bjd_tdb(m, *c, ex)) * 86400
    print("ZTF hjd -> BJD_TDB round trip (s):", d); assert np.all(np.abs(d) < 1e-2)
    print("ZTF BJD_TDB - hjd (s):", (ztf_bjd_tdb(m, *c, ex) - h) * 86400)
    # Gaia: TCB - TDB ~ 19 s at DR3 epochs
    tg = np.array([1700.0, 2600.0]); d = (tg + GAIA_DR3_TIME_ZERO_JD - gaia_bjd_tdb(tg)) * 86400
    print("Gaia TCB - TDB (s):", d); assert np.all((d > 18) & (d < 20))
