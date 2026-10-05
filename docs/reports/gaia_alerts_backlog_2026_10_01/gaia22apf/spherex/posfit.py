import numpy as np, pickle, sys, sxphot as S
from astropy.table import Table
from astropy.coordinates import SkyCoord
t=Table.read('scene_sources.ecsv'); K=np.array(t['K'],float)
c0=SkyCoord(t['ra'][0],t['dec'][0],unit='deg'); r=SkyCoord(t['ra'],t['dec'],unit='deg').separation(c0).arcsec
inb=list(t['name']).index('J202239.05+391152.2')
sel=np.where((r<1)|((K<15.0)&(r<60))|((K<16.0)&(r<15)))[0]
T=Table.read('phot_target_s2.ecsv'); T=T[(T['qc']==1)&(T['clip']==0)&(T['det']>=4)&(T['epoch']<=1)]
R1={x['fn']:x for x in pickle.load(open('phot_target.pkl','rb')) if x and 'err' not in x}
grid=np.arange(-3,3.01,0.5)
chi=np.zeros((len(grid),len(grid)))
ra0,de0=float(t['ra'][0]),float(t['dec'][0])
for row in T[:60]:
    fr=S.load('cut/'+row['fn']); sh=R1[row['fn']]['shift'][:2]
    for i,da in enumerate(grid):
        for j,dd in enumerate(grid):
            ra=np.array(t['ra']).copy(); de=np.array(t['dec']).copy()
            ra[0]=ra0+da/3600/np.cos(np.radians(de0)); de[0]=de0+dd/3600
            P=S.prepare(fr,ra,de,itarget=0,rfit=6.0)
            chi[i,j]+=S.fit(P,shift=sh,free=sel,eps=0.03,full=False)*(P['good'].sum())
i,j=np.unravel_index(np.argmin(chi),chi.shape)
print('best offset dRA*cosd=%.1f" dDec=%.1f"'%(grid[i],grid[j])); print('dchi2 at (0,0):',chi[len(grid)//2,len(grid)//2]-chi[i,j])
np.save('posfit_chi.npy',chi)
