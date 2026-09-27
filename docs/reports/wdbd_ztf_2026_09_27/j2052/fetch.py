"""Inputs for the WDJ2052-0324 scripts (run from this folder): TESS SPOC light curves (S55 120 s; S81 120 s and 20 s) from MAST and the
Montreal pure-H synthetic photometry table (Holberg & Bergeron 2006; https://www.astro.umontreal.ca/~bergeron/CoolingModels/Tables/Table_DA).
The DESI DR1 spectrum (desi_dr1.npz) was retrieved with sparcl_get.py (sparclclient); the ZTF light curve is ztf_6914922055508553984.csv."""
import requests, astropy.units as u
from astropy.coordinates import SkyCoord; from astroquery.mast import Observations
obs = Observations.query_criteria(coordinates=SkyCoord(313.2053162263806, -3.4054752822694088, unit="deg"), radius=0.001 * u.deg, obs_collection="TESS", dataproduct_type="timeseries")
p = Observations.get_product_list(obs); Observations.download_products(p[[("lc.fits" in x) for x in p["productFilename"]]], download_dir="tess")
open("Table_DA.txt", "w").write(requests.get("https://www.astro.umontreal.ca/~bergeron/CoolingModels/Tables/Table_DA", timeout=120).text)
