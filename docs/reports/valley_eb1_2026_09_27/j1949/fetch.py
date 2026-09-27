"""TESS SPOC 120-s light curves of WDJ194901.41+673005.59 (TIC 1884345742) into spoc/ (run before fold.py)."""
import astropy.units as u
from astropy.coordinates import SkyCoord; from astroquery.mast import Observations
obs = Observations.query_criteria(coordinates=SkyCoord(297.25575939550504, 67.50155413383202, unit="deg"), radius=0.001 * u.deg, obs_collection="TESS", dataproduct_type="timeseries")
p = Observations.get_product_list(obs); Observations.download_products(p[[x.endswith("_lc.fits") for x in p["productFilename"]]], download_dir="spoc")
