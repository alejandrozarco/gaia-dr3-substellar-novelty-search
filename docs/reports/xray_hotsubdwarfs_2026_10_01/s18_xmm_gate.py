# Gate the 5XMM-DR15 hot-subdwarf matches (sep<4" or catalogue Gaia-ID match), excluding objects already in the eRASS:3 set.
import numpy as np, pyvo, re, glob
from astropy.table import Table, join
from astroquery.xmatch import XMatch
import astropy.units as u
g=Table.read('xmm/s13_good.ecsv'); E=Table.read('s07_props.ecsv'); inE=set(int(x) for x in E['GaiaEDR3'])
g=g[[int(x) not in inE for x in g['u_gid']]]; print('5XMM matches not in eRASS:3 good set:',len(g))
sim=pyvo.dal.TAPService('https://simbad.cds.unistra.fr/simbad/sim-tap')
up=Table({'gid':np.array(['Gaia DR3 %d'%i for i in g['u_gid']])})
s=sim.run_sync("SELECT u.gid, b.main_id, b.otype FROM TAP_UPLOAD.u AS u JOIN ident i ON i.id=u.gid JOIN basic b ON i.oidref=b.oid",uploads={'u':up}).to_table()
sd={int(r['gid'].split()[-1]):(str(r['main_id']),str(r['otype'])) for r in s}
c=Table({'gid':g['u_gid'],'ra':g['u_ra'],'dec':g['u_dec']})
cats={'VSX':('vizier:B/vsx/vsx',10,lambda r:f"{r['Name']}|{r['Type']}|P={r['Period']}"),'RK':('vizier:B/cb/cbdata',10,lambda r:str(r['Name'])),'RKlmxb':('vizier:B/cb/lmxbdata',10,lambda r:str(r['Name'])),
      'Downes':('vizier:V/123A/cv',10,lambda r:'Downes'),'Rod1000':('vizier:J/PASP/137/A4201/cv_1000',10,lambda r:'Rod25'),'vclass':('vizier:I/358/vclassre',3,lambda r:str(r['Class']))}
hit={}
for lab,(cat,rad,f) in cats.items():
    try:
        r=XMatch.query(cat1=c,cat2=cat,max_distance=rad*u.arcsec,colRA1='ra',colDec1='dec'); r.sort('angDist')
        for x in r: hit.setdefault((int(x['gid']),lab),f(x))
    except Exception as e: print(lab,'HOLE',str(e)[:80])
ids={}
for a in ['2607.28066','2504.10794','2607.28736']:
    txt=''.join(open(f,errors='ignore').read() for f in glob.glob(f'arxiv/{a}/**/*.tex',recursive=True)); ids[a]=set(int(x) for x in re.findall(r'(?<!\d)(\d{17,19})(?!\d)',txt))
ran=set(int(x) for x in Table.read('a693_a268_tablea9.ecsv')['GaiaDR3'])
wt=set(int(x) for x in Table.read('wangtakata_cvs.ecsv')['GaiaDR3'])|set(int(x) for x in Table.read('wangtakata_cand.ecsv')['GaiaDR3'])
for r in g:
    i=int(r['u_gid']); m,o=sd.get(i,('',''))
    fl=[k for (j,k) in hit if j==i]
    pr=[n for n,s_ in [('Schwope26',ids['2607.28066']),('GEM26',ids['2607.28736']),('Ranaiv25CV',ran),('WangTakata',wt)] if i in s_]
    print(i,r['u_lst'],'E' if r['east'] else 'W','Fx %.1e ML %.0f'%(r['x_ep_flux'],r['x_ep_det_ml']),r['x_classx_class'],'|',m[:28],o,'|',{k:hit[(i,k)] for k in fl},pr)
