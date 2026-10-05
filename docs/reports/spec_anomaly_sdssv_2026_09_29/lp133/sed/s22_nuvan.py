import warnings; warnings.filterwarnings('ignore')
import numpy as np
from astropy.table import Table, unique
T=Table.read('nuvctrl_guvcat.ecsv'); T.sort('_r'); T=unique(T,keys='gid',keep='first')
ok=np.isfinite(np.array(T['NUVmag'],float))&(np.nan_to_num(np.array(T['e_NUVmag'],float),nan=9)<0.3)
T=T[ok]; c=np.array(T['NUVmag'],float)-np.array(T['G'],float)
print('controls with NUV err<0.3:',len(T))
tgt=21.661-19.234
for lo,hi,glo in [(6200,7300,7.0),(6400,7000,7.0),(6400,7000,8.6),(6200,7300,8.8)]:
    s=(T['TeffH']>=lo)&(T['TeffH']<=hi)&(T['loggH']>=glo)
    v=c[s]; med=np.median(v); sig=1.4826*np.median(abs(v-med))
    print(f'Teff {lo}-{hi} logg>={glo}: n={s.sum()} NUV-G median {med:.2f} MADsig {sig:.2f}; 5-95pct {np.percentile(v,5):.2f}..{np.percentile(v,95):.2f}; target {tgt:.2f} -> {(tgt-med)/sig:+.1f} sig; frac bluer {np.mean(v<=tgt):.3f}')
# trend with logg in 6400-7000
s=(T['TeffH']>=6400)&(T['TeffH']<=7000)
for a,b in [(7,7.9),(7.9,8.2),(8.2,8.5),(8.5,8.9),(8.9,9.6)]:
    q=s&(T['loggH']>=a)&(T['loggH']<b)
    if q.sum(): print(f' logg {a}-{b}: n={q.sum()} median NUV-G {np.median(c[q]):.2f}')
