import numpy as np, pickle, sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from astropy.table import Table
R=[x for x in pickle.load(open('phot_target.pkl','rb')) if x and 'err' not in x]
t=Table.read('scene_sources.ecsv'); names=list(t['name'])
ib=names.index('J202237.40+391159.3'); i12=names.index('J202237.65+391157.3'); inb=names.index('J202239.05+391152.2')
v='base'
w=np.array([x[v]['wave'] for x in R]); f=np.array([x[v]['flux'][0] for x in R]); e=np.array([x[v]['eflux'][0] for x in R])
mjd=np.array([x[v]['mjd'] for x in R]); det=np.array([x[v]['det'] for x in R])
fb=np.array([x[v]['flux'][ib]+np.nan_to_num(x[v]['flux'][i12]) for x in R])
fn=np.array([x[v]['flux'][inb] for x in R])
fig,ax=plt.subplots(3,1,figsize=(11,13))
sc=ax[0].scatter(w,f,c=mjd,s=8,cmap='coolwarm'); plt.colorbar(sc,ax=ax[0]); ax[0].set_ylim(-500,4000); ax[0].set_ylabel('target uJy')
ax[1].scatter(mjd,f/np.interp(w,*zip(*sorted(zip(w,f)))) if False else f,c=w,s=8); ax[1].set_ylabel('target uJy vs MJD (colour=wave)'); ax[1].set_ylim(-500,4000)
sc=ax[2].scatter(w,fb,c=mjd,s=8,cmap='coolwarm'); ax[2].set_yscale('log'); ax[2].set_ylabel('s16+s12 uJy')
plt.savefig('diag_time.png',dpi=70)
print(np.histogram(mjd,bins=np.arange(60760,61220,30)))
