"""Dwarf-nova screen of the 2026 Lasair-ZTF Galactic-plane objects (plane.json; |b| < 15, >= 4 detections) (2026-09-30).
CDS XMatch with Gaia DR3 (2 arcsec, nearest); amplitude = Gaia G of the counterpart minus the brightest ZTF difference-image
PSF magnitude (min of gmin, rmin; a lower bound on the outburst amplitude when the counterpart is the source). Objects without a
Gaia counterpart within 2 arcsec get amplitude '>' (G > ~21). Flag: amplitude >= 3 mag or no counterpart. Output: plane_amp.csv."""
import json, numpy as np, pandas as pd, astropy.units as u
from astropy.table import Table
from astroquery.xmatch import XMatch
P = pd.DataFrame(json.load(open("plane.json"))); P["peak"] = P[["maggmin", "magrmin"]].min(axis=1)
t = Table.from_pandas(P[["objectId", "ramean", "decmean"]])
X = XMatch.query(cat1=t, cat2="vizier:I/355/gaiadr3", max_distance=2 * u.arcsec, colRA1="ramean", colDec1="decmean").to_pandas()
X = X.sort_values("angDist").drop_duplicates("objectId")[["objectId", "angDist", "Source", "Gmag", "BP-RP"]]
P = P.merge(X, on="objectId", how="left"); P["amp"] = P.Gmag - P.peak
P["flag"] = (P.amp >= 3) | P.Gmag.isna(); P.to_csv("plane_amp.csv", index=False)
pd.set_option("display.width", 250)
print(len(P), "objects;", int(P.Gmag.isna().sum()), "without Gaia within 2 arcsec;", int((P.amp >= 3).sum()), "with amplitude >= 3 mag")
print(P[P.flag].sort_values("peak")[["objectId", "ramean", "decmean", "glatmean", "classification", "ncandgp", "peak", "Gmag", "BP-RP", "angDist", "amp", "tns"]].to_string(index=False))
