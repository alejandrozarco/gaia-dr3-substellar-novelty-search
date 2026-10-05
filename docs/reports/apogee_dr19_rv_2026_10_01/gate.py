import os
"""Gate a candidate list (gate_in.csv: gaia, ra, dec, sdss_id) against Gaia DR3 (gaia_source, astrophysical_parameters FLAME,
NSS tables, vari_classifier_result, vari_eclipsing_binary), SIMBAD (by Gaia DR3 id + 5" cone), local VSX/known store (5"),
the repo dark-companion target lists (rv_dr20_crosscheck targets.csv: unified list, Shahaf+2024, AMRF-III), APOGEE DR17 Joker VAC
and DR17 SB2 VAC (by APOGEE_ID from CAS). Failed service calls are written as HOLE."""
import sys, io, requests, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,os.path.expanduser('~/claude_projects/gaia-recovered-2026-05-27/scripts/gates'))
from astroquery.gaia import Gaia
from astropy.io import fits
c=pd.read_csv('gate_in.csv',dtype={'gaia':str})
ids=",".join(c.gaia)
def gq(sql):
    try: return Gaia.launch_job(sql).get_results().to_pandas()
    except Exception as e: print('HOLE gaia',str(e)[:200]); return None
gs=gq(f"SELECT source_id, ruwe, ipd_frac_multi_peak, ipd_gof_harmonic_amplitude, non_single_star, phot_g_mean_mag, bp_rp, parallax, parallax_over_error, radial_velocity, rv_nb_transits, rv_amplitude_robust, rv_chisq_pvalue, phot_variable_flag FROM gaiadr3.gaia_source WHERE source_id IN ({ids})")
ap=gq(f"SELECT source_id, mass_flame, radius_flame, lum_flame, age_flame, evolstage_flame, teff_gspphot, logg_gspphot, radius_gspphot FROM gaiadr3.astrophysical_parameters WHERE source_id IN ({ids})")
nss=gq(f"SELECT source_id, nss_solution_type, period, semi_amplitude_primary, eccentricity FROM gaiadr3.nss_two_body_orbit WHERE source_id IN ({ids})")
acc=gq(f"SELECT source_id, nss_solution_type FROM gaiadr3.nss_acceleration_astro WHERE source_id IN ({ids})")
nls=gq(f"SELECT source_id, nss_solution_type FROM gaiadr3.nss_non_linear_spectro WHERE source_id IN ({ids})")
vc=gq(f"SELECT source_id, best_class_name, best_class_score FROM gaiadr3.vari_classifier_result WHERE source_id IN ({ids})")
eb=gq(f"SELECT source_id, frequency FROM gaiadr3.vari_eclipsing_binary WHERE source_id IN ({ids})")
for d in (gs,ap,nss,acc,nls,vc,eb):
    if d is not None: d.columns=[x.lower() for x in d.columns]; d['source_id']=d.source_id.astype(str)
out=c.copy().set_index('gaia')
if gs is not None: out=out.join(gs.set_index('source_id'))
if ap is not None: out=out.join(ap.set_index('source_id'))
nssall=pd.concat([x for x in (nss,acc,nls) if x is not None])
out['gaia_nss']=[";".join(nssall[nssall.source_id==g].nss_solution_type.astype(str)) if len(nssall) else '' for g in out.index]
out['gaia_vari']=[";".join(vc[vc.source_id==g].best_class_name.astype(str)) if vc is not None else 'HOLE' for g in out.index]
out['gaia_eb']=[(g in set(eb.source_id)) if eb is not None else 'HOLE' for g in out.index]
# SIMBAD
TAP="https://simbad.cds.unistra.fr/simbad/sim-tap/sync"
sim=[]
for g,r in out.iterrows():
    q=f"SELECT b.main_id, b.otype, b.nbref FROM ident i JOIN basic b ON i.oidref=b.oid WHERE i.id='Gaia DR3 {g}'"
    try:
        t=requests.get(TAP,params=dict(request='doQuery',lang='adql',format='csv',query=q),timeout=60)
        if t.status_code!=200: raise Exception(t.status_code)
        d=pd.read_csv(io.StringIO(t.text))
        if len(d)==0:
            q2=f"SELECT TOP 3 main_id, otype, nbref, DISTANCE(POINT('ICRS',ra,dec),POINT('ICRS',{r.ra},{r.dec}))*3600 AS sep FROM basic WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{r.ra},{r.dec},5./3600))=1 ORDER BY sep"
            t=requests.get(TAP,params=dict(request='doQuery',lang='adql',format='csv',query=q2),timeout=60); d=pd.read_csv(io.StringIO(t.text))
            sim.append('cone:'+";".join(f"{a}|{b}|{n}|{s:.1f}\"" for a,b,n,s in zip(d.main_id,d.otype,d.nbref,d.sep)) if len(d) else 'none')
        else: sim.append(";".join(f"{a}|{b}|nbref={n}" for a,b,n in zip(d.main_id,d.otype,d.nbref)))
    except Exception as e: sim.append('HOLE')
out['simbad']=sim
import local_known
lk=local_known.match(out.reset_index(),'ra','dec',5.0)
out['known_store']=[";".join(f"{a}:{b}:{o}" for a,b,o in zip(lk[lk.idx==i].catalog,lk[lk.idx==i].name,lk[lk.idx==i].otype)) if len(lk) else '' for i in range(len(out))]
T=pd.read_csv(os.path.expanduser('~/claude_projects/gaia-recovered-2026-05-27/docs/reports/rv_dr20_crosscheck_2026_09_25/targets.csv'),dtype=str).set_index('gaia')
out['repo_lists']=[T.set.get(g,'') for g in out.index]
# APOGEE ids from CAS -> DR17 Joker + SB2 VACs
CAS="https://skyserver.sdss.org/dr20/SkyServerWS/SearchTools/SqlSearch"
sq=",".join(str(int(x)) for x in c.sdss_id)
t=requests.get(CAS,params=dict(cmd=f"SELECT DISTINCT sdss_id, sdss4_apogee_id FROM mwm_apogee_allvisit WHERE sdss_id IN ({sq})",format='csv'),timeout=300)
am=pd.read_csv(io.StringIO(t.text.split('\n',1)[1])); am=am[am.sdss4_apogee_id.astype(str).str.startswith('2M')]
J=fits.getdata('apJoker-metadata.fits',1); Jd=pd.DataFrame({'APOGEE_ID':J['APOGEE_ID'].astype(str),'P':np.asarray(J['MAP_P'],dtype=float),'K':np.asarray(J['MAP_K'],dtype=float),'nv':np.asarray(J['n_visits'],dtype=int),'uni':np.asarray(J['unimodal'],dtype=bool)})
S=fits.getdata('apogee_sb2s-v1_0.fits',1); sb2ids=set(np.char.strip(S['OBJID'].astype(str)))
amap=dict(zip(am.sdss_id,am.sdss4_apogee_id))
out['apogee_id']=[amap.get(int(s),'') for s in out.sdss_id]
def jk(a):
    m=Jd[Jd.APOGEE_ID==a]
    return '' if (a=='' or len(m)==0) else f"DR17Joker P={m.P.iloc[0]:.1f} K={m.K.iloc[0]:.1f} nv={m.nv.iloc[0]} uni={m.uni.iloc[0]}"
out['dr17_joker']=[jk(a) for a in out.apogee_id]
out['dr17_sb2vac']=[a in sb2ids for a in out.apogee_id]
out.reset_index().to_csv('gate_out.csv',index=False); print('gated',len(out))
MH=pd.read_csv('mullerhorn_ids.csv',dtype=str); MH['GaiaDR3']=MH.GaiaDR3.str.strip(); MH=MH.drop_duplicates('GaiaDR3').set_index('GaiaDR3')
out=pd.read_csv('gate_out.csv',dtype={'gaia':str})
out['mullerhorn26']=[f"in sample, fit M2={MH.fitcpMass.get(g,'').strip()} P={MH.fitPer.get(g,'').strip()}" if g in MH.index else '' for g in out.gaia]
out.to_csv('gate_out.csv',index=False)
