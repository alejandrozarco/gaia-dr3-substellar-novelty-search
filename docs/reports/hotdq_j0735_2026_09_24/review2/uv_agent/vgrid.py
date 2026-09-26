import numpy as np, sys
sys.path.insert(0,'.')
from load import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
A=load("lfac0zeiq_x1d.fits"); B=load("lfac0zeoq_x1d.fits")
c=2.99792458e5
LL=[('C III',1175.711),('C III',1247.383),('C II',1323.93),('C II',1334.532),('C II',1335.708),('C I',1328.833),('C I',1260.735),('C I',1193.03),
('Si II',1260.422),('Si II',1264.738),('Si II',1193.29),('Si II',1190.416),('Si II',1304.37),('Si II',1309.276),('Si III',1206.5),('Si III',1417.237),
('Si IV',1393.755),('Si IV',1402.77),('N V',1238.821),('N V',1242.804),('S II',1250.578),('S II',1253.805),('S II',1259.518),('O I',1302.168),('N I',1199.55),('C II',1230.01),('C III',1296.33),('C I',1355.848)]
n=len(LL); nc=4; nr=int(np.ceil(n/nc))
fig,ax=plt.subplots(nr,nc,figsize=(18,2.6*nr))
for a,(nm,l0) in zip(ax.flat,LL):
    for X,cc in [(A,'C0'),(B,'C3')]:
        for seg,d in X.items():
            W,F,E,fr=binspec(d['w'],d['f'],d['e'],d['q'],3)
            v=(W/l0-1)*c; s=(np.abs(v)<700)&(fr>0.5)
            if s.sum()<5: continue
            a.plot(v[s],F[s]/np.median(F[s]),color=cc,lw=0.7)
    a.axvline(0,color='k',ls=':'); a.axvline(90,color='m',ls='--')
    a.set_title(f"{nm} {l0}",fontsize=9); a.set_xlim(-700,700); a.set_ylim(0,1.8)
plt.tight_layout(); plt.savefig('vgrid.png',dpi=65)
