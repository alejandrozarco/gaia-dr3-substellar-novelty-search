import warnings; warnings.filterwarnings('ignore')
import pyvo, numpy as np, json
s=pyvo.dal.TAPService('https://datalab.noirlab.edu/tap')
g=json.load(open('gaia.json'))
RA0,DE0=g['RA_ICRS'],g['DE_ICRS']
def pos(ep):
    dt=ep-2016.0
    return RA0+g['pmRA']*dt/3.6e6/np.cos(np.radians(DE0)), DE0+g['pmDE']*dt/3.6e6
cols="ra,dec,type,brick_primary,release,ref_cat,ref_id,ref_epoch,pmra,pmdec,flux_g,flux_ivar_g,flux_r,flux_ivar_r,flux_i,flux_ivar_i,flux_z,flux_ivar_z,flux_w1,flux_ivar_w1,flux_w2,flux_ivar_w2,flux_w3,flux_ivar_w3,flux_w4,flux_ivar_w4,fracflux_g,fracflux_r,fracflux_z,fracflux_w1,fracflux_w2,fracflux_w3,fracflux_w4,nobs_g,nobs_r,nobs_z,nobs_w1,nobs_w2,nobs_w3,nobs_w4,maskbits,fitbits,mw_transmission_g,mw_transmission_r,mw_transmission_z"
for tab in ['ls_dr9.tractor_n','ls_dr10.tractor','ls_dr11.tractor_n','ls_dr11.tractor']:
    c=cols if 'dr9' not in tab else cols.replace('flux_i,flux_ivar_i,','')
    for attempt in range(2):
        try:
            t=s.search(f"SELECT {c} FROM {tab} WHERE ra BETWEEN {RA0-0.0097} AND {RA0+0.0097} AND dec BETWEEN {DE0-0.0056} AND {DE0+0.0056}").to_table(); break
        except Exception as e:
            print(tab,'ERR',str(e)[:200]); t=None
            c=c.replace('flux_i,flux_ivar_i,','').replace('fracflux_w3,fracflux_w4,','')
    if t is None: continue
    print('==',tab,len(t))
    for r in t:
        ep=r['ref_epoch'] if r['ref_epoch']>0 else 2015.5
        pr,pd=pos(ep if r['ref_cat'].strip() else 2016.8)
        sp=3600*np.hypot((r['ra']-pr)*np.cos(np.radians(DE0)),r['dec']-pd)
        d={k:(round(float(r[k]),3) if isinstance(r[k],(float,np.floating)) else r[k]) for k in t.colnames}
        print(f' sep={sp:.2f}"',d)
    t.write(f'ls_{tab.replace(".","_")}.ecsv',overwrite=True)
