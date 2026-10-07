import numpy as np, warnings; warnings.filterwarnings('ignore')
from astropy.timeseries import LombScargle
rng=np.random.default_rng(5)
for s in [64,99,100,101]:
    t,y,tc=np.load(f'ap_s{s}.npy'); fr=np.arange(5,215.99,0.002)
    p=LombScargle(t,y).power(fr,method='fast'); o=np.argsort(p)[::-1]; pk=[]
    for j in o:
        if all(abs(fr[j]-z)>0.1 for z in pk): pk.append(fr[j])
        if len(pk)==3: break
    pv={z:p[np.abs(fr-z).argmin()] for z in pk}
    mx=[]
    for k in range(300):
        mx.append(LombScargle(t,rng.permutation(y)).power(fr,method='fast').max())
    mx=np.array(mx)
    print(f'S{s}: top peaks '+'; '.join(f'{z:.3f} c/d P={pv[z]:.5f} shuffleFAP={max((mx>=pv[z]).mean(),1/300):.3g}{"(<)" if (mx>=pv[z]).mean()==0 else ""}' for z in pk)+f' | shuffle max-power 50/99/max: {np.percentile(mx,50):.5f}/{np.percentile(mx,99):.5f}/{mx.max():.5f}',flush=True)
# combined S99-101
