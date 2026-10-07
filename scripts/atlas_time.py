"""ATLAS forced-photometry times -> mid-exposure BJD_TDB.

The ATLAS forced-photometry column MJD is the UTC Modified Julian Date of the START of the exposure; all exposures are
30 s, and the value is not barycentred (https://fallingstar-data.com/forcedphot/resultdesc/). Mid-exposure is therefore
MJD + 15 s. Usage:

    from atlas_time import atlas_bjd_tdb, atlas_mid_time
    bjd = atlas_bjd_tdb(mjd_column, ra_deg, dec_deg)          # numpy array of BJD_TDB (JD days) at mid-exposure

The barycentric correction uses the geocentre (ATLAS sites differ from it by < 21 ms in light travel time).
"""
import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u

ATLAS_EXPTIME_S = 30.0
HALF_EXPOSURE_D = ATLAS_EXPTIME_S / 2 / 86400.0      # 0.000173611 d
_GEO = EarthLocation.from_geocentric(0, 0, 0, unit="m")


def atlas_mid_time(mjd_start):
    """astropy Time (UTC, geocentre) at mid-exposure from the ATLAS MJD column (exposure start)."""
    return Time(np.asarray(mjd_start, dtype=float) + HALF_EXPOSURE_D, format="mjd", scale="utc", location=_GEO)


def atlas_bjd_tdb(mjd_start, ra_deg, dec_deg):
    """BJD_TDB (JD, float array) at mid-exposure for a target at (ra_deg, dec_deg) ICRS."""
    t = atlas_mid_time(mjd_start)
    c0 = SkyCoord(ra_deg * u.deg, dec_deg * u.deg)
    return (t.tdb + t.light_travel_time(c0)).jd


def atlas_hjd_utc(mjd_start, ra_deg, dec_deg):
    """HJD (UTC) at mid-exposure, as VSX expects in its Epoch field."""
    t = atlas_mid_time(mjd_start)
    c0 = SkyCoord(ra_deg * u.deg, dec_deg * u.deg)
    return (t.utc + t.light_travel_time(c0, kind="heliocentric")).jd


if __name__ == "__main__":
    # self-test: the mid-exposure shift is exactly 15 s after barycentring (to < 1 ms)
    m = np.array([59000.0, 60000.5])
    t_start = Time(m, format="mjd", scale="utc", location=_GEO); c0 = SkyCoord(45.8 * u.deg, -42.1 * u.deg)
    b0 = (t_start.tdb + t_start.light_travel_time(c0)).jd
    d = (atlas_bjd_tdb(m, 45.8, -42.1) - b0) * 86400
    print("shift (s):", d); assert np.all(np.abs(d - 15.0) < 1e-3)
