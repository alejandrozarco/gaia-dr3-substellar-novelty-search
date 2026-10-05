import warnings; warnings.filterwarnings('ignore')
from astroquery.vizier import Vizier
for cid in ['II/335/gal_ais','II/312/ais','V/154/sdss16','V/147/sdss12','II/349/ps1','II/246/out','II/319/las9','II/365/catwise','II/363/unwise','II/328/allwise','II/374','II/383','II/384','II/385','II/381','II/382','II/387','II/386']:
    try:
        m=Vizier(row_limit=1).get_catalog_metadata(catalog=cid)
        print(cid, list(m['title'])[:1])
    except Exception as e: print(cid,'ERR',type(e).__name__,str(e)[:80])
