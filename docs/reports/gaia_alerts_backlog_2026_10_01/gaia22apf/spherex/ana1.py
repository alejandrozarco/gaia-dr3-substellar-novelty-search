import numpy as np, pickle, sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from astropy.table import Table
R=[x for x in pickle.load(open(sys.argv[1],'rb')) if x and 'err' not in x]
t=Table.read(sys.argv[2]); names=list(t['name'])
ids={'target':0,'nb6':names.index('J202239.05+391152.2'),'s12':names.index('J202237.65+391157.3'),'s16':names.index('J202237.40+391159.3')}
sh=np.array([x['shift'] for x in R]); print('shift median',np.median(sh[:,:2],0),'std',np.std(sh[:,:2],0))
fig,ax=plt.subplots(4,1,figsize=(11,16),sharex=True)
for j,(lab,i) in enumerate(ids.items()):
    for v,col in [('base','k'),('deep','r'),('r4','b'),('noeps','g')]:
        w=np.array([x[v]['wave'] for x in R]); f=np.array([x[v]['flux'][i] for x in R]); e=np.array([x[v]['eflux'][i] for x in R])
        ax[j].errorbar(w+0.005*'kbrg'.index(col),f,e,fmt='.',color=col,ms=3,alpha=0.6,label=v)
    ax[j].set_ylabel(lab+' uJy'); ax[j].legend(fontsize=7)
    if lab=='s16': ax[j].set_yscale('log')
ax[-1].set_xlabel('um'); plt.savefig(sys.argv[3],dpi=70)
v='base'
w=np.array([x[v]['wave'] for x in R]); chi=np.array([x[v]['chi2r'] for x in R]); det=np.array([x[v]['det'] for x in R])
for d in range(1,7): print(d,'n',np.sum(det==d),'chi2r med %.2f'%np.median(chi[det==d]),'corr tgt-nb6 med %.2f'%np.nanmedian([x[v]['corr'].get(ids['nb6'],np.nan) for x in R if x[v]['det']==d]))
