import numpy as np, sys
from astropy.table import Table
T=Table.read(sys.argv[1]); G=(T['qc']==1)&(T['clip']==0)
bands=[('0.75-1.0 (z/Y)',0.75,1.0,None),('J 1.11-1.39',1.11,1.39,1594.),('H 1.50-1.80',1.50,1.80,1024.),('Ks 2.00-2.31',2.00,2.31,666.7),
       ('W1 2.8-3.9',2.8,3.9,309.54),('3.8-4.4 (D5)',3.8,4.4,None),('W2 4.0-5.0',4.0,5.0,171.79)]
print('band | ' + ' | '.join(['2025-04/05','2025-10','2026-05/06']))
for lab,lo,hi,zp in bands:
    s=[]
    for e in range(3):
        m=G&(T['epoch']==e)&(T['wave']>=lo)&(T['wave']<hi)
        if m.sum()<2: s.append('--'); continue
        f=np.array(T['flux'][m]); med=np.median(f); er=1.2533*1.4826*np.median(np.abs(f-med))/np.sqrt(m.sum())
        er=max(er, np.sqrt(np.sum(np.array(T['eflux_tot'][m])**2))/m.sum())
        mag=f"{-2.5*np.log10(med*1e-6/zp):.2f}" if zp else ''
        s.append(f"{med:6.0f}+-{er:4.0f} uJy n={m.sum():2d} {('Vega '+mag) if mag else ''}")
    print(f"{lab:16s} | "+' | '.join(s))
