import warnings; warnings.filterwarnings('ignore')
from astroquery.vizier import Vizier
V=Vizier(columns=["**"],row_limit=-1); V.TIMEOUT=90
cats=['J/A+A/669/A48','J/A+A/686/A65','J/A+A/663/A45','J/MNRAS/499/5508','J/MNRAS/519/2486','J/ApJ/928/20','J/A+A/693/A268','J/A+A/684/A118','J/A+A/700/A71','J/A+A/673/A90','J/A+A/686/A126','J/MNRAS/503/2157','J/A+A/651/A121','J/MNRAS/516/1509','J/AJ/170/199','J/PASA/43/106','J/ApJS/284/72']
for c in cats:
    try: r=V.get_catalogs(c)
    except Exception as e: print(c,'ERR',e); continue
    if len(r)==0: print(c,'NO TABLES (not in VizieR / invalid id)'); continue
    tot=0; hit=[]
    for k in r.keys():
        t=r[k]; tot+=len(t); s=' '.join(' '.join(str(v) for v in row) for row in t.as_array().tolist()) if len(t)<200000 else ''
        for pat in ['21821402','6130942326140307712','120559','181.496','181.49']:
            if pat in s: hit.append((k,pat))
    print(c,len(r),'tables',tot,'rows; desc:',r[0].meta.get('description','')[:60],'| HITS' if hit else '| none',hit[:4],flush=True)
