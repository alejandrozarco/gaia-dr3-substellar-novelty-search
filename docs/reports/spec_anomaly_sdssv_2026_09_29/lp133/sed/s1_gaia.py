import warnings; warnings.filterwarnings('ignore')
from astroquery.vizier import Vizier
import json
v=Vizier(columns=['**'],row_limit=-1)
r=v.query_constraints(catalog='I/355/gaiadr3',Source='1609392862209121664')
t=r[0]
cols=['RA_ICRS','DE_ICRS','Plx','e_Plx','pmRA','pmDE','Gmag','BPmag','RPmag','BP-RP','RUWE']
d={c:float(t[c][0]) for c in cols}
print(d)
json.dump(d,open('gaia.json','w'),indent=1)
# find J-PLUS catalogues
for kw in ['J-PLUS DR3','J-PLUS']:
    cats=Vizier.find_catalogs(kw)
    for k,c in cats.items(): print(k, '|', c.description)
