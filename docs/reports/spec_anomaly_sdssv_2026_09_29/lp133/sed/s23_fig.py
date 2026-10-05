import numpy as np, json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R=json.load(open('j0430_result.json'))
fig,ax=plt.subplots(1,2,figsize=(10,4))
for a,ap in zip(ax,['3arcsec','6arcsec']):
    C=np.loadtxt(f'j0430_controls_{ap}.csv',delimiter=',')
    sel=(C[:,1]>=18.9)&(C[:,1]<=19.5)
    a.hist(C[:,3],bins=np.arange(-0.8,0.8,0.04),color='0.7',label=f'controls all (n={len(C)})')
    a.hist(C[sel,3],bins=np.arange(-0.8,0.8,0.04),histtype='step',color='k',label=f'controls G 18.9-19.5 (n={sel.sum()})')
    t=R[ap]['target']; a.axvline(t['interp_delta'],color='C3',lw=2,label=f"LP 133-754: {t['interp_delta']:+.3f}±{t['interp_err']:.3f}")
    a.axvline(R['prediction']['metric_a_signal'],color='C0',ls='--',label=f"predicted CH: +{R['prediction']['metric_a_signal']:.3f}")
    a.set_xlabel('J0430 - interp(J0410,J0515)  [mag; + = deficit]'); a.set_title(f'J-PLUS DR3 aper-corr {ap}'); a.legend(fontsize=7)
plt.tight_layout(); plt.savefig('lp133_j0430_test.png',dpi=130)
