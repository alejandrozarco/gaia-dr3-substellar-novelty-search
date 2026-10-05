import json, numpy as np
from astroquery.gaia import Gaia
Gaia.ROW_LIMIT=-1
r=json.load(open('gaia_row.json'))
q=f"""select source_id,ra,dec,parallax,parallax_error,pmra,pmra_error,pmdec,pmdec_error,phot_g_mean_mag,bp_rp,ruwe,radial_velocity,
DISTANCE(POINT({r['ra']},{r['dec']}),POINT(ra,dec)) as sep
from gaiadr3.gaia_source where 1=CONTAINS(POINT(ra,dec),CIRCLE({r['ra']},{r['dec']},1.2)) and parallax>5"""
t=Gaia.launch_job_async(q).get_results(); t.write('cone_plx5.fits',overwrite=True)
print('rows plx>5 within 1.2 deg:',len(t))
t['sep_as']=t['sep']*3600
p0,e0=r['parallax'],r['parallax_error']
dplx=np.abs(t['parallax']-p0)/np.hypot(t['parallax_error'],e0)
theta=t['sep_as']
s_au=theta*1000/p0
dmu=np.hypot(t['pmra']-r['pmra'],t['pmdec']-r['pmdec'])
sdmu=np.sqrt(((t['pmra']-r['pmra'])**2*(t['pmra_error']**2+r['pmra_error']**2)+(t['pmdec']-r['pmdec'])**2*(t['pmdec_error']**2+r['pmdec_error']**2)))/np.maximum(dmu,1e-9)
dmu_orb=0.44*p0**1.5*np.maximum(theta,1e-3)**-0.5
dvt=4.74047*dmu/p0
for i in np.argsort(dplx):
    if dplx[i]<5 or abs(t['parallax'][i]-p0)<3:
        print('%d sep=%.1f" (%.3f pc) plx=%.2f+-%.2f (%.1fsig) pm=(%.1f,%.1f) dmu=%.1f (orb lim %.2f) dvt=%.1f km/s G=%.2f bp_rp=%s ruwe=%.2f'%(t['source_id'][i],theta[i],s_au[i]/206265,t['parallax'][i],t['parallax_error'][i],dplx[i],t['pmra'][i],t['pmdec'][i],dmu[i],dmu_orb[i],dvt[i],t['phot_g_mean_mag'][i],t['bp_rp'][i],t['ruwe'][i]))
# El-Badry-like bound-pair criterion within 1 pc
sel=(theta<3600*1.08)&(dplx<3)&(dmu<dmu_orb+2*sdmu)&(t['source_id']!=int(1609392862209121664))
print('EB21-like candidates:',sel.sum())
# looser comoving: dvt<10 km/s and plx within 3 sigma, within 1 pc
sel2=(theta<3600*1.08)&(dplx<3)&(dvt<10)&(t['source_id']!=int(1609392862209121664))
print('loose (dvt<10 km/s, plx 3sig) :',sel2.sum())
# any comoving within 5 pc projected (5.4 deg) - separate query later
print('N within 1 pc projected with plx within 3sig:',((theta<3600*1.08)&(dplx<3)).sum()-1)
