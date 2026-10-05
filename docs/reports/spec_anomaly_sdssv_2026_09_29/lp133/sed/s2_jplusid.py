import warnings; warnings.filterwarnings('ignore')
from astroquery.vizier import Vizier
for cid in ['II/376','II/377','II/369','II/362','II/371','II/375','II/378','II/379','II/380']:
    try:
        m=Vizier(row_limit=1).get_catalog_metadata(catalog=cid)
        print(cid, list(m['title'])[:1] if 'title' in m.colnames else m)
    except Exception as e:
        print(cid,'ERR',type(e).__name__, str(e)[:100])
for kw in ['JPLUS','Javalambre','J-PLUS DR3','Javalambre Photometric Local Universe']:
    try:
        c=Vizier.find_catalogs(kw)
        print(kw,'->',[(k,v.description[:80]) for k,v in c.items()])
    except Exception as e: print(kw,'ERR',e)
