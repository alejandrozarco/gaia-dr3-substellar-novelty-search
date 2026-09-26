import warnings; warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier
import astropy.units as u
from astropy.coordinates import SkyCoord
c = SkyCoord(244.7254259862617, -35.90743853686, unit="deg")
V = Vizier(columns=["**", "_r"], row_limit=5000)
for cat in ["B/vsx/vsx", "I/358/vclassre", "I/358/varisum", "J/A+A/674/A22/catalog", "J/A+A/674/A25/vspursig", "J/A+A/674/A33/gspc-wd", "J/MNRAS/508/3877/maincat", "J/ApJ/917/23/table2", "J/ApJ/961/113/table1", "J/ApJS/281/52/table1", "J/A+A/704/A317/tequila", "J/A+A/699/A3/table3", "J/ApJ/984/58/table1", "J/A+A/700/A195/catalog", "J/AJ/158/93/table2", "J/AJ/159/84/table2", "J/A+A/695/A75/catalog", "J/A+A/682/A5/catalog"]:
    t = V.query_region(c, radius=5 * u.arcsec, catalog=cat)
    for x in t:
        print("=====", cat, x.meta.get("description", "")[:90], len(x))
        for col in x.colnames:
            vals = [str(v) for v in x[col][:3]]
            print(f"   {col}: {vals}")
