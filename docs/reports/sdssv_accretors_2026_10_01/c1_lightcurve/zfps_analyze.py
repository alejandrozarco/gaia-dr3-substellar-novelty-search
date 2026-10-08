import numpy as np, pandas as pd
cols=[c.strip() for c in [l for l in open('fp_lc.txt') if l.startswith(' index')][0].split(',') if c.strip()]
d=pd.read_csv('fp_lc.txt',comment='#',sep=r'\s+',names=cols,skiprows=0,header=None)
d=d[pd.to_numeric(d['index'],errors='coerce').notna()].apply(pd.to_numeric,errors='ignore')
print('rows',len(d))
q=(d.infobitssci<33554432)&(d.scisigpix<25)&(d.sciinpseeing<4)&(d.forcediffimflux>-99998)&(d.diffimgstatus==1) if 'diffimgstatus' in d else None
print('good',q.sum(), 'chisq median',d.loc[q,'forcediffimchisq'].median())
d=d[q].copy(); f=10**(-0.4*(d.zpdiff-23.9))  # DN -> uJy
d['fl']=d.forcediffimflux*f; d['fe']=d.forcediffimfluxunc*f*np.sqrt(np.maximum(d.forcediffimchisq,1))
d['grp']=d.field.astype(str)+'_'+d.ccdid.astype(str)+'_'+d.qid.astype(str)+'_'+d['filter']+'_'+d.rfid.astype(str)
d['res']=d.fl-d.groupby('grp').fl.transform('median')
for flt,g in d.groupby('filter'):
    mad=1.4826*np.median(np.abs(g.res-np.median(g.res)))
    big=g[g.res>5*mad]
    print(f"{flt}: n={len(g)} groups={g.grp.nunique()} robust scatter {mad:.1f} uJy; median chisq {g.forcediffimchisq.median():.2f}; >5 sigma positive {len(big)}, negative {np.sum(g.res<-5*mad)}")
    # quiescent C1 flux ~91 uJy (G 18.9); 1.5 mag outburst adds ~270 uJy, 2.5 mag ~820
    for dm in (1.0,1.5,2.5): print(f"   {dm} mag outburst adds {91*(10**(0.4*dm)-1):.0f} uJy = {91*(10**(0.4*dm)-1)/mad:.1f} sigma")
    if len(big): 
        b=big.sort_values('jd'); print(b[['jd','res','fe','forcediffimchisq','sciinpseeing']].round(1).to_string(index=False)[:2500])
d.to_csv('clean.csv',index=False)
