# VizieR all-table 5" cone per candidate: list catalogue names whose descriptions are not generic surveys; flag variability/sdB/binary catalogues.
import warnings; warnings.filterwarnings("ignore")
import pandas as pd, re
from astroquery.vizier import Vizier
import astropy.units as u
from astropy.coordinates import SkyCoord
ids = ["6456720612064924928", "2883364038621038208", "5055036663256963072", "2888030331609338240", "3496637913394359680", "5657176543986789248", "3537042874067950336", "4749559145849819008", "6828182472250027776", "6644157726508197504", "437628614520520320", "178685757799822080"]
u_ = pd.read_csv("unconfirmed.csv", dtype={"source_id": str}).set_index("source_id")
generic = re.compile(r"^(I/|II/|IV/|V/|VI/|B/(denis|vsx|gcvs|wd|sb)|J/ApJS/249/18)")
V = Vizier(columns=["_r"], row_limit=3)
for i in ids:
    r = u_.loc[i]; c = SkyCoord(r.ra, r.dec, unit="deg")
    try: T = V.query_region(c, radius=5 * u.arcsec)
    except Exception as e: print(i, "ERR", e); continue
    names = [t.meta.get("name") for t in T]; spec = [n for n in names if not generic.match(n)]
    print(f"== {i} ({r.main_id}, otype {r.otype}, vsx {r.vsx_type}): {len(names)} tables; non-generic: {spec}", flush=True)
