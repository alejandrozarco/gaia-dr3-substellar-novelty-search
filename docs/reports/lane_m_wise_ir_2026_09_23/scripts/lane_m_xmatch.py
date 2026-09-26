# Lane M step 1: Petrosky+2021 short-period WISE periodic variables x Gaia DR3; keep sources below the main sequence
import json, numpy as np
from astropy.table import Table
from astroquery.xmatch import XMatch
import astropy.units as u
t = Table.read("petrosky_p035.fits")
up = Table(dict(wise=[str(x) for x in t["WISE"]], ra=np.array(t["RAJ2000"], float), dec=np.array(t["DEJ2000"], float), P=np.array(t["Pmhaov"], float),
                amp=np.array(t["Amp"], float), w1=np.array(t["W1mag"], float), w2=np.array(t["W2mag"], float), npts=np.array(t["Npts"], int)))
x = XMatch.query(cat1=up, cat2="vizier:I/355/gaiadr3", max_distance=4 * u.arcsec, colRA1="ra", colDec1="dec")
print("xmatch rows", len(x), "unique WISE", len(set(x["wise"])))
x.write("lane_m_xmatch.fits", overwrite=True)
print(x.colnames)
