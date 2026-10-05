import numpy as np
from astroquery.gaia import Gaia
from astropy.table import Table, vstack
rows=[l.split() for l in open('../kilic25/Table2_ALL.txt') if not l.startswith('#')]
ids=[];teff=[];mass=[];typ=[]
for r in rows:
    try:
        ids.append(int(r[1])); typ.append(r[2]); 
        # Teff/Mass positions from the end: Teff eTeff Mass eMass logg elogg Munuv
        teff.append(float(r[-7])); mass.append(float(r[-5]))
    except Exception as e: pass
ids=np.array(ids); teff=np.array(teff); mass=np.array(mass); typ=np.array(typ)
print(len(ids))
out=[]
for i in range(0,len(ids),800):
    q="select source_id,ra,dec,parallax,pmra,pmdec,l,b from gaiadr3.gaia_source where source_id in (%s)"%','.join(map(str,ids[i:i+800]))
    out.append(Gaia.launch_job(q).get_results())
t=vstack(out); t.write('kilic25_gaia.fits',overwrite=True)
d={int(s):k for k,s in enumerate(t['source_id'])}
k=np.array([d.get(int(s),-1) for s in ids]); ok=k>=0
print('matched',ok.sum())
vt=np.full(len(ids),np.nan); vt[ok]=4.74047*np.hypot(t['pmra'][k[ok]],t['pmdec'][k[ok]])/t['parallax'][k[ok]]
np.save('kilic25_vt.npy',np.vstack([ids,teff,mass,vt]))
isDA=np.array([x.startswith('DA') for x in typ])
for lab,sel in [('all',ok),('DA 6000-7500K 0.5-0.8Msun',ok&isDA&(teff>6000)&(teff<7500)&(mass>0.5)&(mass<0.8)),
                ('all types M>1.1',ok&(mass>1.1)),('DA M>1.1',ok&isDA&(mass>1.1)),('DA M>1.1 T<10kK',ok&isDA&(mass>1.1)&(teff<10000)),('DA M>1.1 T<8kK',ok&isDA&(mass>1.1)&(teff<8000))]:
    v=vt[sel]
    print('%-28s N=%4d median vt %.1f; frac>48.3 %.2f; percentile of 48.3: %.0f'%(lab,sel.sum(),np.nanmedian(v),(v>48.3).mean(),(v<48.26).mean()*100))
s=ok&isDA&(mass>1.1)&(teff<8000)
for i in np.where(s)[0]: print(ids[i],teff[i],mass[i],round(vt[i],1),typ[i])
