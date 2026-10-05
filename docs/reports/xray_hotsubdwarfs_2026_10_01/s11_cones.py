# Per-survivor: SIMBAD 10" cone (all objects, otypes) + VizieR all-table 3" cone (table list + descriptions). Probe: RR Pic must return its CV tables.
import numpy as np, json, warnings, time; warnings.filterwarnings('ignore')
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astropy.table import Table
import astropy.units as u
M=Table.read('s07_props.ecsv'); S=M[~M['known_cv'].astype(bool)]
v=Vizier(row_limit=5,columns=['*']); v.TIMEOUT=300
sb=Simbad(); sb.add_votable_fields('otype','sp','dim')  # older/newer API tolerant
def cone(ra,de):
    c=SkyCoord(ra,de,unit='deg')
    for k in range(3):
        try: r=v.query_region(c,radius=3*u.arcsec); break
        except Exception as e: r=None; time.sleep(5)
    tabs=[] if r is None else [(t.meta.get('name',''),t.meta.get('description','')[:80],len(t)) for t in r]
    for k in range(3):
        try: s=sb.query_region(c,radius=10*u.arcsec); break
        except Exception as e: s='HOLE'; time.sleep(5)
    sl=[] if s is None else ('HOLE' if isinstance(s,str) else [ (str(x['main_id'] if 'main_id' in s.colnames else x['MAIN_ID']), str(x['otype'] if 'otype' in s.colnames else x['OTYPE'])) for x in s])
    return (tabs if r is not None else 'HOLE'), sl
t,s=cone(98.9003,-62.6401); print('probe RR Pic: tables',len(t),[x[0] for x in t][:12],'simbad',s)
out={}
for r in S:
    gid=int(r['GaiaEDR3']); 
    if str(r['otype'])=='PN': continue
    t,s=cone(float(r['ra_1']),float(r['dec_1'])); out[gid]=dict(tables=t,simbad=s)
    print(gid, str(r['simbad'])[:22],'| SIMBAD10:',s,'| ntab',len(t) if t!='HOLE' else 'HOLE',flush=True)
json.dump(out,open('cones/s11_cones.json','w'),indent=1)
