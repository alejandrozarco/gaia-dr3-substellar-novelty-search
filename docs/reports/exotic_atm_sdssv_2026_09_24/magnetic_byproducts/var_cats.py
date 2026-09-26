# Variability-catalogue check around Gaia DR3 6021870154194477312 (GALEX J161854.1-355427) and its three neighbours within 14".
import warnings; warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier
from astroquery.gaia import Gaia
import astropy.units as u
from astropy.coordinates import SkyCoord
ids = ["6021870154194477312", "6021870158500230656", "6021870154194477696", "6021870158500371840"]
r = Gaia.launch_job(f"select source_id, ra, dec, phot_g_mean_mag, bp_rp, parallax, phot_variable_flag, ruwe from gaiadr3.gaia_source where source_id in ({','.join(ids)})").get_results()
print(r)
c = SkyCoord(r["ra"][r["source_id"] == int(ids[0])][0], r["dec"][r["source_id"] == int(ids[0])][0], unit="deg")
V = Vizier(columns=["**"], row_limit=50)
for cat, nm in [("B/vsx/vsx", "VSX"), ("J/AJ/156/241", "ATLAS-VAR (Heinze+2018)"), ("I/358/vclassre", "Gaia DR3 vari_classifier"), ("I/358/varisum", "Gaia DR3 vari_summary"),
                ("J/ApJS/249/18", "ZTF periodic (Chen+2020)"), ("II/366/catv2021", "ASAS-SN variables"), ("J/MNRAS/503/200", "ASAS-SN var")]:
    try:
        t = V.query_region(c, radius=30 * u.arcsec, catalog=cat)
        print(f"{nm}: {sum(len(x) for x in t)} rows")
        for x in t: print(x)
    except Exception as e: print(nm, "ERROR", str(e)[:100])
t = V.query_region(c, radius=30 * u.arcsec, catalog=None)
print("all-table 30\" cone:", [x.meta.get("name") for x in t])
