import warnings; warnings.filterwarnings('ignore')
from astropy.io.votable import parse_single_table
import urllib.request, numpy as np, io
t=parse_single_table('koester_meta.xml').to_table()
print(t.colnames)
for r in t:
    te,lg=float(r['teff']),float(r['logg'])
    if te in (6250,6500,6750,7000,7250) and lg in (9.0,9.25):
        url=r['Access.Reference'] if 'Access.Reference' in t.colnames else r[t.colnames[-1]]
        fn=f'koester/da_{int(te)}_{lg:.2f}.xml'
        urllib.request.urlretrieve(str(url).strip(),fn)
        sp=parse_single_table(fn).to_table()
        np.savetxt(fn.replace('.xml','.txt'),np.c_[np.array(sp.columns[0],float),np.array(sp.columns[1],float)])
        print(te,lg,len(sp),sp.colnames)
