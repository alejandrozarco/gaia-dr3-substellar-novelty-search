"""TESScut 11x11 px FFI cutouts of CRTS J205436.5-541810 (Gaia DR3 6470209729951480576) for all sectors; run before tess_lc.py."""
from astroquery.mast import Tesscut; from astropy.coordinates import SkyCoord
Tesscut.download_cutouts(coordinates=SkyCoord(313.6523466764687, -54.30286141537966, unit="deg"), size=11, path=".")
