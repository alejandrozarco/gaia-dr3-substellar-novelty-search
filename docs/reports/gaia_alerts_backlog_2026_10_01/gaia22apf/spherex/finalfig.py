import numpy as np, pickle, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from astropy.table import Table
T=Table.read('phot_target_s2.ecsv'); G=(T['qc']==1)&(T['clip']==0)
B=pickle.load(open('phot_target_s2_binned.pkl','rb'))
fig,ax=plt.subplots(1,2,figsize=(15,6))
cols=['tab:blue','tab:green','tab:red']; labs=['SPHEREx 2025-04/05','SPHEREx 2025-10','SPHEREx 2026-05/06']
for e in range(3):
    b=B[e]; ax[0].errorbar(b[:,0],b[:,1],b[:,2],fmt='o-',ms=3,lw=1,color=cols[e],label=labs[e])
hist=dict(PS1_2009_14=([0.48,0.62,0.75,0.87,0.96],[6.3,20.9,39.8,63,91]),UGPS_K_2006=([2.2],[560]),AllWISE_2010=([3.35,4.6,11.6,22.1],[571,601,4655,2581]),
          NEOWISE_2021_24=([3.35,4.6],[2023,2275]),MIPS24=([23.7],[8268]))
mk={'PS1_2009_14':'ks','UGPS_K_2006':'k*','AllWISE_2010':'kD','NEOWISE_2021_24':'m^','MIPS24':'kv'}
for k,(w,f) in hist.items(): ax[0].plot(w,f,mk[k],mfc='none' if '2021' not in k else None,ms=8,label=k.replace('_',' '))
ax[0].set_xscale('log'); ax[0].set_yscale('log'); ax[0].set_xlabel('wavelength (um)'); ax[0].set_ylabel('F_nu (uJy)')
ax[0].set_title('Gaia22apf: SPHEREx epochs vs archival (pre-outburst open symbols)'); ax[0].legend(fontsize=7); ax[0].set_xlim(0.4,30)
ax[0].set_xticks([0.5,1,2,3,5,10,20]); ax[0].set_xticklabels(['0.5','1','2','3','5','10','20'])
# ratio plot
b0=B[0]; 
for e in [1,2]:
    b=B[e]; r=[];
    for row in b:
        j=np.argmin(np.abs(np.log(b0[:,0]/row[0])))
        if abs(np.log(b0[j,0]/row[0]))<0.03: r.append((row[0],row[1]/b0[j,1],np.hypot(row[2]/b0[j,1],row[1]*b0[j,2]/b0[j,1]**2)))
    r=np.array(r); ax[1].errorbar(r[:,0],-2.5*np.log10(r[:,1]),2.5/np.log(10)*r[:,2]/r[:,1],fmt='o',color=cols[e],ms=3,label=labs[e]+' minus 2025-04/05')
lam=np.linspace(0.8,5,100)
for AV,ls in [(6,'--')]:
    # Wang & Chen 2019-like: A_l/A_V ~ 0.243*(l/1.25)^-2.07 for NIR; flatten beyond 3 um (~0.04-0.03)
    al=np.where(lam<2.5,0.243*(lam/1.25)**-2.07,np.maximum(0.243*(2.5/1.25)**-2.07*(lam/2.5)**-1.0,0.025))
    ax[1].plot(lam,AV*al,'k'+ls,label=f'extinction dA_V={AV} (approx. NIR law)')
ax[1].invert_yaxis(); ax[1].set_xlabel('wavelength (um)'); ax[1].set_ylabel('fade (mag)'); ax[1].legend(fontsize=8); ax[1].set_title('Chromaticity of the 2025-2026 fade')
ax[1].set_ylim(2.5,-0.5)
plt.tight_layout(); plt.savefig('gaia22apf_spherex_sed_fade.png',dpi=90)
