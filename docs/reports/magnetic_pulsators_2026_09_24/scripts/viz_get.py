# Download full VizieR catalogues (all tables) with astroquery, save each table as raw/viz_<catalog with / -> _>__<table>.csv
import sys, time, warnings; warnings.filterwarnings('ignore')
from astroquery.vizier import Vizier
V = Vizier(columns=['**'], row_limit=-1); V.TIMEOUT = 300
for cat in sys.argv[1:]:
    for k in range(3):
        try:
            tl = V.get_catalogs(cat); break
        except Exception as e:
            err = repr(e); time.sleep(10)
    else:
        print('HOLE', cat, err); continue
    for t in tl:
        name = t.meta.get('name', cat)
        fn = 'raw/viz_' + name.replace('/', '_') + '.csv'
        t.to_pandas().to_csv(fn, index=False)
        print(cat, '->', name, len(t), 'rows', t.colnames[:25])
