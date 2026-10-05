import numpy as np, pickle
from astropy.table import Table
R=[x for x in pickle.load(open('phot_target.pkl','rb')) if x and 'err' not in x]
t=Table.read('scene_sources.ecsv'); names=list(t['name'])
inb=names.index('J202239.05+391152.2'); ib=names.index('J202237.40+391159.3')
v='base'
w=np.array([x[v]['wave'] for x in R]); f=np.array([x[v]['flux'][0] for x in R]); fn=np.nan_to_num(np.array([x[v]['flux'][inb] for x in R]))
fb=np.array([x[v]['flux'][ib] for x in R])
mjd=np.array([x[v]['mjd'] for x in R]); ep=np.digitize(mjd,[60900,61100])
# position angle of detector y axis on sky
import sxphot as S
pa=[]
for x in R:
    from astropy.io import fits
    h=S.load('cut/'+x['fn'])['hdr']; pa.append(np.degrees(np.arctan2(h['PC1_2'],h['PC2_2'])))
pa=np.array(pa)
for lo,hi in [(0.75,1.0),(1.0,1.3),(1.3,1.7),(1.7,2.4),(2.4,3.8),(3.8,4.4),(4.4,5.0)]:
    s=[]
    for e in range(3):
        m=(ep==e)&(w>=lo)&(w<hi)
        if m.sum()<2: s.append('   --   '); continue
        s.append(f"n={m.sum():2d} T={np.median(f[m]):6.0f} N={np.median(fn[m]):5.0f} T+N={np.median(f[m]+fn[m]):6.0f} B={np.median(fb[m]):6.0f} PA={np.median(pa[m]):5.0f}")
    print(f"{lo:.2f}-{hi:.2f}", ' | '.join(s))
