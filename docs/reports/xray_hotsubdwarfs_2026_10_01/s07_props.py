# Gaia DR3 properties (gaia_source, BJ distances, vari_summary, NSS) + 2MASS/AllWISE xmatch + Lx, Lx/Lbol for the gate survivors (39) and all 159 for reference.
import numpy as np, pyvo, time
from astropy.table import Table, join, unique
from astroquery.xmatch import XMatch
import astropy.units as u
T=Table.read('s06_gate_master.ecsv')
g=unique(Table.read('s01_culpan_x_dr2mg.ecsv'),keys='GaiaEDR3'); k=Table.read('s03_knownhsd_x_dr2mg.ecsv')
fx={int(r['GaiaEDR3']):(float(r['MLFlux1']),float(r['s_MLFlux1']),float(r['DetLike0']),float(r['pany']),float(r['SepGDR3ERO']),float(r['posErr']),int(r['FlagOpt'])) for r in g}
for r in k: fx.setdefault(int(r['GaiaEDR3']),(float(r['MLFlux1']),float(r['s_MLFlux1']),float(r['DetLike0']),float(r['pany']),float(r['SepGDR3ERO']),float(r['posErr']),int(r['FlagOpt'])))
gaia=pyvo.dal.TAPService('https://gea.esac.esa.int/tap-server/tap')
ids=','.join(str(int(i)) for i in T['GaiaEDR3'])
q='''SELECT s.source_id, s.ra, s.dec, s.parallax, s.parallax_error, s.ruwe, s.phot_g_mean_mag, s.bp_rp, s.phot_variable_flag, s.non_single_star, s.has_xp_continuous, s.phot_bp_rp_excess_factor,
 s.phot_g_n_obs, s.phot_g_mean_flux_over_error, d.r_med_geo, d.r_lo_geo, d.r_hi_geo
 FROM gaiadr3.gaia_source AS s LEFT JOIN external.gaiaedr3_distance AS d ON d.source_id=s.source_id WHERE s.source_id IN ('''+ids+')'
G=gaia.run_sync(q).to_table(); print('gaia rows',len(G))
V=gaia.run_sync('SELECT v.* FROM gaiadr3.vari_summary AS v WHERE v.source_id IN ('+ids+')').to_table(); print('vari_summary',len(V))
N=gaia.run_sync('SELECT n.source_id, n.nss_solution_type, n.period FROM gaiadr3.nss_two_body_orbit AS n WHERE n.source_id IN ('+ids+')').to_table(); print('nss',len(N))
V.write('s07_vari_summary.ecsv',overwrite=True); N.write('s07_nss.ecsv',overwrite=True)
G.rename_column('source_id','GaiaEDR3'); M=join(T,G,keys='GaiaEDR3',join_type='left')
M['Fx']=[fx[int(i)][0] for i in M['GaiaEDR3']]; M['e_Fx']=[fx[int(i)][1] for i in M['GaiaEDR3']]; M['DetLike0']=[fx[int(i)][2] for i in M['GaiaEDR3']]
M['pany']=[fx[int(i)][3] for i in M['GaiaEDR3']]; M['sepX']=[fx[int(i)][4] for i in M['GaiaEDR3']]; M['posErr']=[fx[int(i)][5] for i in M['GaiaEDR3']]; M['FlagOpt']=[fx[int(i)][6] for i in M['GaiaEDR3']]
d=np.array(M['r_med_geo'].filled(np.nan),float)
M['Lx']=4*np.pi*(d*3.086e18)**2*np.array(M['Fx'])
# optical flux ratio (Rodriguez+ convention style): fopt from G: log fG = -0.4 G - 4.86 (approx, erg/s/cm2 over Gaia G band)
M['logFxFopt']=np.log10(np.array(M['Fx']))-(-0.4*np.array(M['phot_g_mean_mag'])-4.86)
# Lbol: assume hot subdwarf BC_G=-2.9 (Teff~30kK), extinction from Culpan E(BP/RP)c *~ A_G ~ 2*E(BP-RP) (rough)
cu={int(r['GaiaEDR3']):float(r['E(BP/RP)c']) if 'E(BP/RP)c' in r.colnames and not np.ma.is_masked(r['E(BP/RP)c']) else np.nan for r in g}
M['ebr']=[cu.get(int(i),np.nan) for i in M['GaiaEDR3']]
AG=2.0*np.nan_to_num(np.array(M['ebr']),nan=0.0)
MG=np.array(M['phot_g_mean_mag'])-5*np.log10(d/10)-AG
M['MG0']=MG
M['Lbol']=3.828e33*10**(-0.4*(MG-2.9-4.74))
M['logLxLbol']=np.log10(M['Lx']/M['Lbol'])
# 2MASS + AllWISE
cc=Table({'GaiaEDR3':M['GaiaEDR3'],'ra':M['ra_1'] if 'ra_1' in M.colnames else M['ra'],'dec':M['dec_1'] if 'dec_1' in M.colnames else M['dec']})
for lab,cat,cols in [('2mass','vizier:II/246/out',['Jmag','Hmag','Kmag']),('wise','vizier:II/328/allwise',['W1mag','W2mag','W3mag'])]:
    r=XMatch.query(cat1=cc,cat2=cat,max_distance=3*u.arcsec,colRA1='ra',colDec1='dec'); r.sort('angDist')
    dd={}
    for x in r: dd.setdefault(int(x['GaiaEDR3']),[float(x[c]) if not np.ma.is_masked(x[c]) else np.nan for c in cols])
    for j,cn in enumerate(cols): M[cn]=[dd.get(int(i),[np.nan]*3)[j] for i in M['GaiaEDR3']]
    print(lab,len(dd))
M['G_J']=M['phot_g_mean_mag']-M['Jmag']; M['G_W1']=M['phot_g_mean_mag']-M['W1mag']; M['J_H']=M['Jmag']-M['Hmag']; M['W1_W2']=M['W1mag']-M['W2mag']
M.write('s07_props.ecsv',overwrite=True)
