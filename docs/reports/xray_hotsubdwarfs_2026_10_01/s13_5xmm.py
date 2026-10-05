# Culpan hotsd (61585) + knownhsd x 5XMM-DR15 (HEASARC xmmssc): (a) join on catalogue gaiadr3_source_id, (b) positional 10" real vs Dec+1' shifted control.
# Probe: HD 49798 must be in xmmssc.
import pyvo, numpy as np, time
from astropy.table import Table, vstack
from astroquery.vizier import Vizier
h=pyvo.dal.TAPService('https://heasarc.gsfc.nasa.gov/xamin/vo/tap')
p=h.run_sync("SELECT name, ra, dec, ep_flux, gaiadr3_source_id FROM xmmssc WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',102.0196,-44.3162,0.005))=1").to_table()
print('probe HD49798:',len(p), list(p['name'][:2]), list(p['gaiadr3_source_id'][:2])); assert len(p)>0
cu=Table.read('culpan_hotsd_min.ecsv')
v=Vizier(row_limit=-1,columns=['GaiaEDR3','RA_ICRS','DE_ICRS','Name','SpClass']); kn=v.get_catalogs('J/A+A/662/A40/knownhsd')[0]
print('knownhsd',len(kn))
allt=Table({'gid':np.r_[np.array(cu['GaiaEDR3']),np.array(kn['GaiaEDR3'].filled(0))].astype(np.int64),'ra':np.r_[np.array(cu['RA_ICRS']),np.array(kn['RA_ICRS'])],'dec':np.r_[np.array(cu['DE_ICRS']),np.array(kn['DE_ICRS'])],
  'lst':np.array(['cand']*len(cu)+['known']*len(kn))})
cols="x.name, x.ra AS xra, x.dec AS xdec, x.error_radius, x.ep_flux, x.ep_flux_error, x.ep_1_flux, x.ep_2_flux, x.ep_3_flux, x.ep_det_ml, x.ep_hr2, x.ep_hr3, x.var_flag, x.fvar, x.chi2prob, x.n_obs, x.sum_flag, x.extent, x.gaiadr3_source_id, x.gaia_match_prob, x.classx_class, x.classx_prob_gal_cv, x.classx_prob_star, x.classx_prob_agn, x.classx_prob_gal_xrb"
out={}
for lab,dde in [('dec+1m',1/60.)]:
    res=[]; holes=[]
    for i0 in range(0,len(allt),2000):
        u=allt[i0:i0+2000].copy(); u['dec']=u['dec']+dde
        q=f"""SELECT u.gid, u.lst, u.ra, u.dec, {cols}, DISTANCE(POINT('ICRS',x.ra,x.dec),POINT('ICRS',u.ra,u.dec))*3600 AS sep
        FROM tap_upload.u AS u JOIN xmmssc AS x ON CONTAINS(POINT('ICRS',x.ra,x.dec),CIRCLE('ICRS',u.ra,u.dec,10/3600.))=1"""
        t0=time.time()
        for k in range(3):
            try: r=h.run_sync(q,uploads={'u':u}).to_table(); break
            except Exception as e: print('retry',str(e)[:120]); time.sleep(20); r=None
        if r is None: print(lab,i0,'HOLE',flush=True); holes.append(i0); continue
        res.append(r); print(lab,i0,len(r),f'{time.time()-t0:.0f}s',flush=True)
    R=vstack(res) if res else Table(); R.write(f'xmm/s13_{lab}.ecsv',overwrite=True); out[lab]=R
    s=np.array(R['sep']) if len(R) else np.array([])
    print(lab,'HOLE chunks',holes,'rows',len(R),'uniq stars',len(set(R['u_gid'])) if len(R) else 0,'<2":',(s<2).sum(),'<3":',(s<3).sum(),'<5":',(s<5).sum(),'<10":',(s<10).sum())
