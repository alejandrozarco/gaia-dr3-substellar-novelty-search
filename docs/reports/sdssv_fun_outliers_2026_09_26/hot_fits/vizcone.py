import pandas as pd, warnings; warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier; from astropy.coordinates import SkyCoord; import astropy.units as u
h = pd.read_csv("/tmp/hotdq/hot_lum.csv", dtype=str)
ids = "100568930 74510696 102043792 102152010 80998734 73346836 99327334 109787602".split()
V = Vizier(columns=["*"], row_limit=5); V.TIMEOUT = 120
for _, r in h[h.sdss_id.isin(ids)].iterrows():
    try:
        res = V.query_region(SkyCoord(float(r.ra), float(r.dec), unit="deg"), radius=3 * u.arcsec)
        cats = sorted(res.keys())
        print(r.sdss_id, r.gaia_dr3_source_id, r.main_id, len(cats), "tables", flush=True)
        for c in cats:
            t = res[c]; cols = [x for x in t.colnames if any(k in x.lower() for k in ["sp", "type", "teff", "class", "cl"])]
            print("   ", c, {x: str(t[x][0]) for x in cols[:6]})
    except Exception as e:
        print(r.sdss_id, "HOLE", repr(e)[:120], flush=True)
