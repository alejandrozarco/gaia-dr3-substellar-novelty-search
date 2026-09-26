"""Novelty gate for new ZTF/ATLAS-confirmed Gaia periods: SIMBAD id/type/refs, VSX (5 arcsec), VizieR all-table 5 arcsec
(non-generic tables listed), ADS full text by Gaia id and short names. Failed queries print HOLE."""
import sys, os, re, requests, warnings
warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier
import astropy.units as u
from astropy.coordinates import SkyCoord
Vizier.TIMEOUT = 120
tok = open(os.path.expanduser("~/.config/ads/token")).read().strip(); H = {"Authorization": "Bearer " + tok}
S = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync"
def tap(q): return requests.get(S, params=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=200).text.strip().split("\n")[1:]
for arg in sys.argv[1:]:
    g, ra, dec, *names = arg.split(":"); ra, dec = float(ra), float(dec); print("=====", g, names)
    try: print(" SIMBAD:", tap(f"SELECT b.main_id,b.otype,b.sp_type FROM ident i JOIN basic b ON i.oidref=b.oid WHERE i.id='Gaia DR3 {g}'")); print(" refs:", tap(f"SELECT r.bibcode FROM ident i JOIN has_ref h ON h.oidref=i.oidref JOIN ref r ON r.oidbib=h.oidbibref WHERE i.id='Gaia DR3 {g}'"))
    except Exception as ex: print(" SIMBAD HOLE", type(ex).__name__)
    try:
        v = requests.get("https://www.aavso.org/vsx/index.php", params=dict(view="api.list", ra=ra, dec=dec, radius=0.0014, format="json"), timeout=60).json()
        o = v.get("VSXObjects", {}).get("VSXObject", []) if isinstance(v.get("VSXObjects"), dict) else []
        print(" VSX:", [(x.get("Name"), x.get("VariabilityType"), x.get("Period")) for x in o])
    except Exception as ex: print(" VSX HOLE", type(ex).__name__)
    try:
        T = Vizier(columns=["_r"], row_limit=2).query_region(SkyCoord(ra, dec, unit="deg"), radius=5 * u.arcsec)
        print(" VizieR:", [t.meta.get("name") for t in T if not re.match(r"^(I/|II/|IV/|V/|VI/)", t.meta.get("name", ""))])
    except Exception as ex: print(" VizieR HOLE", type(ex).__name__)
    for q in [f'full:"{g}"'] + [f'full:"{n}"' for n in names]:
        try:
            r = requests.get("https://api.adsabs.harvard.edu/v1/search/query", params=dict(q=q, fl="bibcode,title", rows=10), headers=H, timeout=60).json()
            print(" ADS", q, [(d["bibcode"], d["title"][0][:60]) for d in r["response"]["docs"]])
        except Exception as ex: print(" ADS HOLE", q, type(ex).__name__)
