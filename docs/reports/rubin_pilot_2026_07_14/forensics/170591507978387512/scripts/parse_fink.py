#!/usr/bin/env python
"""Parse Fink LSST /sources JSON into an MJD-keyed light-curve table."""
import json
import numpy as np
import pandas as pd

D = "/tmp/rubin_pilot/forensics/170591507978387512"
rows = json.load(open(f"{D}/fink_sources.json"))
print("n sources:", len(rows))
print("all keys sample:", sorted(rows[0].keys())[:80])

recs = []
for r in rows:
    flux = r.get("r:psfFlux")   # nJy
    ferr = r.get("r:psfFluxErr")
    mjd = r.get("r:midpointMjdTai")
    band = r.get("r:band")
    ra = r.get("r:ra"); dec = r.get("r:dec")
    mag = magerr = None
    if flux is not None and flux > 0:
        mag = -2.5 * np.log10(flux) + 31.4
        if ferr:
            magerr = 1.0857 * ferr / flux
    recs.append(dict(mjd=mjd, band=band, psfFlux_nJy=flux, psfFluxErr_nJy=ferr,
                     mag_AB=mag, magerr=magerr, ra=ra, dec=dec,
                     reliability=r.get("r:reliability"),
                     snr=r.get("r:snr")))

df = pd.DataFrame(recs).sort_values("mjd")
assert df["mjd"].notna().all(), "MJD missing on some rows"
pd.set_option("display.width", 200)
print(df.to_string(index=False))
df.to_csv(f"{D}/fink_lsst_alert_photometry.csv", index=False)
print("\nMJD span:", df.mjd.min(), "-", df.mjd.max(), "=", df.mjd.max() - df.mjd.min(), "days")
print("bands:", df.band.value_counts().to_dict())
print("mean pos:", df.ra.mean(), df.dec.mean())
