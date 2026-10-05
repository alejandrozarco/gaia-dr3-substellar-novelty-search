# Gaia DR3 XP sampled spectra for all 159 objects; H-alpha index = mean flux 650-662 nm / linear continuum from 615-635 and 680-700 nm.
# Control: the 120 gate-known CVs (should show emission) and the known hot subdwarfs (absorption).
import numpy as np, warnings; warnings.filterwarnings('ignore')
from astroquery.gaia import Gaia
from astropy.table import Table
M=Table.read('s07_props.ecsv')
ids=[int(i) for i,h in zip(M['GaiaEDR3'],M['has_xp_continuous']) if str(h) in ('True','true','1')]
print('with XP',len(ids))
d=Gaia.load_data(ids=ids,data_release='Gaia DR3',retrieval_type='XP_SAMPLED',data_structure='INDIVIDUAL',format='votable',valid_data=False)
res={}
for k,v in d.items():
    t=v[0].to_table()
    sid=int(t.meta.get('source_id', k.split('_')[-1].split('.')[0].split(' ')[-1])) if False else None
    for row in [t]:
        pass
    # each file has wavelength, flux, flux_error; source id is in file name
    import re
    m=re.search(r'(\d{15,19})',k); sid=int(m.group(1))
    w=np.array(t['wavelength'],float); f=np.array(t['flux'],float); e=np.array(t['flux_error'],float)
    c1=(w>=615)&(w<=635); c2=(w>=680)&(w<=700); l=(w>=650)&(w<=662)
    p=np.polyfit(np.r_[w[c1],w[c2]],np.r_[f[c1],f[c2]],1); cont=np.polyval(p,w[l])
    idx=np.mean(f[l])/np.mean(cont); err=np.sqrt(np.sum(e[l]**2))/l.sum()/np.mean(cont)
    res[sid]=(idx,err)
    Table({'wavelength':w,'flux':f,'flux_error':e}).write(f'xp/{sid}.ecsv',overwrite=True)
M['Ha_idx']=[res.get(int(i),(np.nan,np.nan))[0] for i in M['GaiaEDR3']]; M['e_Ha_idx']=[res.get(int(i),(np.nan,np.nan))[1] for i in M['GaiaEDR3']]
M.write('s07_props.ecsv',overwrite=True)
kc=M['known_cv'].astype(bool)
for lab,sel in [('known CV',kc),('known hsd (culpan_known)',np.array(M['src'])=='culpan_known'),('survivors',~kc)]:
    x=np.array(M['Ha_idx'][sel],float); x=x[np.isfinite(x)]
    print(lab,len(x),'percentiles 10/50/90:',np.round(np.percentile(x,[10,50,90]),3))
