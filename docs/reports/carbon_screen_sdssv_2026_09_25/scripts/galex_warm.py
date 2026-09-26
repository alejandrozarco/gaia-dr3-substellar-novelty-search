"""FUV-NUV of SDSS-V SnowWhite DA white dwarfs at the colour of a target (GUVcat AIS via CDS XMatch, Gaia positions
propagated to 2007.0, 4 arcsec), compared with the target's FUV-NUV. Usage: python galex_warm.py <bp_rp> <M_G> <FUV-NUV> <err>"""
import sys, numpy as np, pandas as pd
from astropy.table import Table
from astroquery.xmatch import XMatch
import astropy.units as u
bprp, mg, fn, efn = map(float, sys.argv[1:5])
d = pd.read_csv("sw_classified.csv", dtype={"gaia_dr3_source_id": str})
d["bp_rp"] = d.bp_mag - d.rp_mag
with np.errstate(invalid="ignore"): d["MG"] = d.g_mag + 5 * np.log10(d.plx / 100)
da = d[(d.classification == "DA") & (np.abs(d.bp_rp - bprp) < 0.06) & (d.plx / d.e_plx > 5) & (d.snr > 10)].copy()
da["ra07"] = da.ra - (da.pmra * 9 / 3.6e6) / np.cos(np.radians(da.dec)); da["de07"] = da.dec - da.pmde * 9 / 3.6e6
t = Table.from_pandas(da[["gaia_dr3_source_id", "ra07", "de07", "MG", "bp_rp", "teff"]])
x = XMatch.query(cat1=t, cat2="vizier:II/335/galex_ais", max_distance=4 * u.arcsec, colRA1="ra07", colDec1="de07").to_pandas()
x = x.sort_values("angDist").drop_duplicates("gaia_dr3_source_id")
x = x[np.isfinite(x.FUVmag) & np.isfinite(x.NUVmag)]
x["fn"] = x.FUVmag - x.NUVmag
for lab, s in (("all", x), (f"M_G within 0.5 of {mg}", x[np.abs(x.MG - mg) < 0.5])):
    if len(s): print(f"DA |dBP-RP|<0.06 {lab}: n={len(s)} FUV-NUV median {np.median(s.fn):+.2f} p95 {np.percentile(s.fn,95):+.2f} max {s.fn.max():+.2f}; n >= target {int((s.fn >= fn).sum())}; median SnowWhite Teff {np.nanmedian(s.teff):.0f}")
print(f"target FUV-NUV {fn:+.2f} +- {efn:.2f}")
