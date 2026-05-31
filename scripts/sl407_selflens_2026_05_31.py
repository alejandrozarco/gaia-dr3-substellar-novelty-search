"""Self-lensing pulse search in Gaia DR3 407572673901190912 (TIC 370354975).

Hypothesis under test: a coherent BRIGHTENING (self-lensing) pulse at orbital
conjunction (phase 0), predicted amplitude ~12.73 mmag, from a putative compact
companion.

Skepticism-first, encoding the prior false-positive lessons:
  (1) Use REAL pipeline products (TESS-SPOC PDCSAP, QLP), NOT hand FFI extraction.
  (2) Assess significance by a PERMUTATION / phase-scramble NULL (empirical FAP),
      NOT a per-cadence noise floor.
  (3) A detection must be a POSITIVE pulse at the PREDICTED conjunction phase,
      COHERENT across sectors, ABOVE the permutation FAP.
  (4) The predicted amplitude assumed a CENTRAL (edge-on, u_min=0) lens crossing.
      We FIRST check the real geometry: the Gaia astrometric inclination sets the
      sky-projected impact parameter at conjunction. If i is far from 90 deg, no
      transit/lens crossing occurs and the pulse is geometrically impossible
      regardless of photometric noise.

Data: ALL TESS sectors via lightkurve (TESS-SPOC + QLP); ZTF DR g/r via IRSA.
Env: ostinato venv. Outputs JSON + report to /tmp. Does NOT touch docs/.
"""
import warnings, json, io, math, sys
warnings.filterwarnings('ignore')
import numpy as np

SID = 407572673901190912
TIC = 370354975
RA, DEC = 22.46263200071673, 54.141219793975935   # ICRS (project parquet / Gaia)

# ---- NSS orbital elements (Gaia DR3 nss_two_body_orbit, AstroSpectroSB1) ----
P      = 1528.9997200957548      # d
P_err  = 115.34777069091797      # d
Tp     = 145.48750817894376      # t_periastron, Gaia ref days (since JD 2457389.0)
Tp_err = 6.209576606750488
ECC    = 0.6058185878650781
# Thiele-Innes (AU)
A_TI, B_TI, F_TI, G_TI = 3.791088578949661, -1.087121049315093, 1.550146108713633, 3.7268652438394003
C_TI, H_TI = 0.9168856035498129, 0.7490553029750704
PLX = 2.532960037017058          # mas (NSS)
# Primary (Gaia astrophysical_parameters)
M1 = 0.9900385141372681          # Msun (FLAME)
R1 = 1.5176609754562378          # Rsun (FLAME); GSP-Phot gives 1.05 -> we test both
R1_gspphot = 1.0468

GAIA_REF_JD = 2457389.0          # Gaia DR3 reference epoch (JD)
BTJD_OFFSET = 2457000.0          # TESS BTJD = JD - 2457000
AU=1.495978707e11; Rsun=6.957e8; Msun=1.98892e30; G_SI=6.6743e-11; c=2.998e8
AU_KM=1.495978707e8

out = {'target': 'Gaia DR3 407572673901190912', 'TIC': TIC, 'ra_deg': RA, 'dec_deg': DEC,
       'NSS': {'solution_type': 'AstroSpectroSB1', 'P_d': P, 'P_err_d': P_err,
               't_periastron_gaia_d': Tp, 't_periastron_err_d': Tp_err, 'ecc': ECC,
               'parallax_mas': PLX, 'M1_Msun': M1, 'R1_Rsun_FLAME': R1, 'R1_Rsun_gspphot': R1_gspphot}}

# ============================================================
# 0. GEOMETRY: is a self-lensing pulse even possible?
# ============================================================
def incl_from_ABFG(A,B,F,G):
    p=A*A+B*B+F*F+G*G; q=A*G-B*F
    a2=0.5*p+math.sqrt(max((0.5*p)**2-q*q,0)); cosi=min(abs(q)/a2,1.0)
    return math.degrees(math.acos(cosi)), math.sqrt(a2)
inc_deg, a_mas = incl_from_ABFG(A_TI,B_TI,F_TI,G_TI)
omega = math.atan2(C_TI,H_TI)                          # primary arg periastron (rad)
a1sini = math.hypot(C_TI,H_TI)                         # AU
K1 = 2*math.pi*a1sini*AU_KM/(P*86400.0*math.sqrt(1-ECC*ECC))
fM = (P*86400.0)*(K1*1e3)**3*(1-ECC*ECC)**1.5/(2*math.pi*G_SI)/Msun
def solve_m2(fM,M1,sini):
    lo,hi=1e-5,1e3
    for _ in range(200):
        m=0.5*(lo+hi)
        if (m*sini)**3>fM*(M1+m)**2: hi=m
        else: lo=m
    return 0.5*(lo+hi)
sini=math.sin(math.radians(inc_deg)); M2=solve_m2(fM,M1,sini)
P_yr=P/365.25; a_rel=((M1+M2)*P_yr**2)**(1/3.)*AU

# conjunctions: sin(nu+omega) = +/-1
def conj_geom(target_phase_arg, R1_use):
    nu=(target_phase_arg-omega)%(2*math.pi)
    r=a_rel*(1-ECC*ECC)/(1+ECC*math.cos(nu))
    bproj=r*math.sqrt(max(1-sini**2*math.sin(nu+omega)**2,0))
    rE=math.sqrt(4*G_SI*(M2*Msun)*r/c**2)
    return dict(nu_deg=math.degrees(nu)%360, r_AU=r/AU, bproj_Rsun=bproj/Rsun,
                rE_Rsun=rE/Rsun, b_over_rE=bproj/rE, b_over_R1=bproj/(R1_use*Rsun),
                b_over_rEplusR1=bproj/(rE+R1_use*Rsun))
# mean->phase for conjunction (to know fold phase)
def true_to_phase(nu):
    E=2*math.atan2(math.sqrt(1-ECC)*math.sin(nu/2), math.sqrt(1+ECC)*math.cos(nu/2))
    M=E-ECC*math.sin(E); return (M/(2*math.pi))%1.0
conjA_nu=(math.pi/2-omega)%(2*math.pi); conjB_nu=(3*math.pi/2-omega)%(2*math.pi)
geom = {
    'inclination_deg': round(inc_deg,2), 'a_phot_mas': round(a_mas,4),
    'sin_i': round(sini,4), 'omega_primary_deg': round(math.degrees(omega)%360,2),
    'K1_kms': round(K1,3), 'f_mass_Msun': round(fM,4), 'M2_Msun_astrom_incl': round(M2,3),
    'a_rel_AU': round(a_rel/AU,3), 'a_rel_Rsun': round(a_rel/Rsun,1),
    'conjA': {**conj_geom(math.pi/2,R1), 'fold_phase_from_periastron': round(true_to_phase(conjA_nu),4)},
    'conjB': {**conj_geom(3*math.pi/2,R1), 'fold_phase_from_periastron': round(true_to_phase(conjB_nu),4)},
}
# minimum projected separation over whole orbit
nus=np.linspace(0,2*np.pi,400001)
rr=a_rel*(1-ECC*ECC)/(1+ECC*np.cos(nus))
proj=rr*np.sqrt(np.clip(1-sini**2*np.sin(nus+omega)**2,0,1))
imin=int(np.argmin(proj))
rEmin=math.sqrt(4*G_SI*(M2*Msun)*rr[imin]/c**2)
geom['min_proj_sep_Rsun']=round(proj[imin]/Rsun,1)
geom['min_proj_over_rEplusR1_FLAME']=round(proj[imin]/(rEmin+R1*Rsun),0)
geom['min_proj_over_rEplusR1_gspphot']=round(proj[imin]/(rEmin+R1_gspphot*Rsun),0)
# i required for a crossing: b_min ~ a(1-e) cos i < rE+R1
i_req = 90-math.degrees(math.asin(min((rEmin+R1*Rsun)/(a_rel*(1-ECC)),1.0)))
geom['inclination_required_for_crossing_deg']=round(i_req,2)
geom['geometry_allows_self_lensing']= bool(proj[imin] < 5*(rEmin+R1*Rsun))
geom['note']=('Self-lensing requires the source to pass within ~(rE+R1) of the lens '
              'on the sky. Min projected separation over the orbit is compared to that. '
              'b_min/(rE+R1)>>1 => geometrically impossible; the ~12.73 mmag prediction '
              'assumed a CENTRAL edge-on crossing (u_min=0), inconsistent with i~27 deg.')
out['geometry'] = geom
print(f'[GEOM] i={inc_deg:.1f} deg, M2~{M2:.2f} Msun, a_rel={a_rel/AU:.2f} AU')
print(f'[GEOM] min projected sep = {proj[imin]/Rsun:.0f} Rsun ; rE+R1 = {(rEmin+R1*Rsun)/Rsun:.2f} Rsun '
      f'-> b_min/(rE+R1) = {proj[imin]/(rEmin+R1*Rsun):.0f}')
print(f'[GEOM] i required for a lens crossing: >{i_req:.1f} deg  -> self-lensing geometrically '
      f'{"POSSIBLE" if geom["geometry_allows_self_lensing"] else "EXCLUDED"}')

# ============================================================
# 1. TESS: download ALL sectors via lightkurve (real pipeline products)
# ============================================================
import lightkurve as lk
tess={}
sr_all = lk.search_lightcurve(f'TIC {TIC}', mission='TESS')
authors=sorted(set(str(a) for a in sr_all.table['author'])) if len(sr_all) else []
tess['search_n_products']=int(len(sr_all)); tess['authors']=authors
# Keep only products whose target_name is THIS TIC (avoid the 4-arcsec neighbour TIC 370354977)
def target_ok(row):
    tn=str(row['target_name'])
    return (str(TIC) in tn) or (tn==str(TIC))
sr = lk.search_lightcurve(f'TIC {TIC}', mission='TESS', author=('SPOC','TESS-SPOC','QLP'))
print(f'[TESS] {len(sr_all)} products; authors={authors}; {len(sr)} SPOC/TESS-SPOC/QLP')

# one product per sector: prefer SPOC(2min)>TESS-SPOC>QLP, shorter exptime
rank={'SPOC':0,'TESS-SPOC':1,'QLP':2}
by_sector={}
for i,row in enumerate(sr.table):
    tn=str(row['target_name'])
    if not (str(TIC) in tn): continue
    sec=str(row['mission']); a=str(row['author'])
    try: expt=float(row['exptime'])
    except: expt=9999.0
    rk=(rank.get(a,9),expt)
    if sec not in by_sector or rk<by_sector[sec][0]:
        by_sector[sec]=(rk,i,a,expt)
tess['sectors_selected']={k:{'author':v[2],'exptime_s':v[3]} for k,v in by_sector.items()}
print(f'[TESS] {len(by_sector)} unique sectors for TIC {TIC}: {tess["sectors_selected"]}')

all_t,all_f,all_fe,all_sec=[],[],[],[]
dl_log=[]
for sec,(rk,i,a,expt) in sorted(by_sector.items()):
    row=sr[int(i)]
    try:
        lc=row.download(download_dir='/tmp/lk_cache_sl407')
        if lc is None:
            dl_log.append({'sector':sec,'author':a,'status':'None'}); continue
        flux=None; fcol=None
        for cand in ('pdcsap_flux','kspsap_flux','sap_flux','det_flux','flux'):
            if cand in lc.colnames and np.isfinite(np.asarray(lc[cand],float)).sum()>50:
                flux=np.asarray(lc[cand],float); fcol=cand; break
        if flux is None:
            dl_log.append({'sector':sec,'author':a,'status':'no usable flux'}); continue
        t=np.asarray(lc.time.value,float)
        ecol=None
        for cand in (fcol.replace('flux','flux_err'),'flux_err','pdcsap_flux_err','kspsap_flux_err','sap_flux_err'):
            if cand in lc.colnames: ecol=cand; break
        fe=np.asarray(lc[ecol],float) if ecol else np.full_like(flux,np.nan)
        q=np.asarray(lc['quality'],float) if 'quality' in lc.colnames else np.zeros_like(t)
        m=np.isfinite(t)&np.isfinite(flux)&(q==0)
        if m.sum()<50: m=np.isfinite(t)&np.isfinite(flux)
        t,flux,fe=t[m],flux[m],fe[m]
        med=np.nanmedian(flux)
        if not np.isfinite(med) or med==0:
            dl_log.append({'sector':sec,'author':a,'status':'bad median'}); continue
        f=flux/med; fe=fe/med
        all_t.append(t); all_f.append(f); all_fe.append(fe)
        all_sec.append(np.full(t.shape,len(dl_log)))
        dl_log.append({'sector':sec,'author':a,'fcol':fcol,'exptime_s':expt,'n':int(m.sum()),
                       't0_btjd':float(t.min()),'t1_btjd':float(t.max()),'status':'ok'})
    except Exception as ex:
        dl_log.append({'sector':sec,'author':a,'status':f'ERR {type(ex).__name__}: {ex}'[:160]})
tess['download_log']=dl_log
n_ok=sum(1 for d in dl_log if d.get('status')=='ok')
tess['n_sectors_ok']=n_ok
print(f'[TESS] downloaded {n_ok} sectors OK')
out['TESS']=tess

if n_ok==0:
    out['FATAL_TESS']='no TESS sectors downloaded'
    json.dump(out, open('/tmp/sl407_selflens.json','w'), indent=1, default=str)
    print('NO TESS DATA');
else:
    t=np.concatenate(all_t); f=np.concatenate(all_f); fe=np.concatenate(all_fe)
    segid=np.concatenate(all_sec).astype(int)
    o=np.argsort(t); t,f,fe,segid=t[o],f[o],fe[o],segid[o]
    tess['n_points']=int(t.size); tess['baseline_d']=float(t.max()-t.min())
    tess['baseline_in_P']=float((t.max()-t.min())/P)
    mad=np.median(np.abs(f-np.median(f))); tess['raw_rms_ppm']=float(1.4826*mad*1e6)
    print(f'[TESS] N={t.size}, baseline={tess["baseline_d"]:.0f} d ({tess["baseline_in_P"]:.2f} P), raw rms~{tess["raw_rms_ppm"]:.0f} ppm')

    # ---- per-sector detrend (median filter) + ZERO each sector median ----
    from scipy.ndimage import median_filter
    def detrend(ts,fs,fes,win_d=1.0):
        oo=np.argsort(ts); ts,fs,fes=ts[oo],fs[oo],fes[oo]
        dt=np.median(np.diff(ts)) if ts.size>5 else 0.02
        w=max(11,int(win_d/max(dt,1e-4)));  w+= (w%2==0)
        w=min(w,max(11,(fs.size//2)*2-1))
        tr=median_filter(fs,size=w,mode='nearest')
        res=fs/tr-1.0
        s=1.4826*np.median(np.abs(res-np.median(res)))
        keep=np.abs(res-np.median(res))<5*s
        return ts[keep],res[keep],(fes[keep] if np.isfinite(fes).any() else np.full(int(keep.sum()),s))
    dt_t,dt_r,dt_e=[],[],[]
    for s in np.unique(segid):
        m=segid==s
        if m.sum()<50: continue
        a_,b_,c_=detrend(t[m],f[m],fe[m])
        b_=b_-np.median(b_)
        dt_t.append(a_); dt_r.append(b_); dt_e.append(c_)
    t2=np.concatenate(dt_t); r2=np.concatenate(dt_r); e2=np.concatenate(dt_e)
    oo=np.argsort(t2); t2,r2,e2=t2[oo],r2[oo],e2[oo]
    e2=np.where(np.isfinite(e2)&(e2>0),e2,np.nanmedian(e2[np.isfinite(e2)&(e2>0)]))
    det_rms=float(1.4826*np.median(np.abs(r2-np.median(r2)))*1e6)
    tess['detrended_rms_ppm']=det_rms; tess['n_detrended']=int(t2.size)
    print(f'[TESS] detrended N={t2.size}, residual rms~{det_rms:.0f} ppm')

    # ---- fold phase: 0 = periastron in Gaia ref days; convert TESS BTJD -> Gaia-ref-day ----
    # Gaia ref day = JD - 2457389.0 ; TESS BTJD = JD - 2457000.0  => Gaia_day = BTJD - 389.0
    t2_gaia = t2 + BTJD_OFFSET - GAIA_REF_JD
    phase = ((t2_gaia - Tp) % P) / P
    # conjunction phases (fold-phase from periastron)
    phi_conjA = geom['conjA']['fold_phase_from_periastron']
    phi_conjB = geom['conjB']['fold_phase_from_periastron']
    out['fold_phases'] = {'periastron':0.0, 'conjA_superior':phi_conjA, 'conjB_inferior':phi_conjB}

    # phase coverage (the honesty check for P=1529 d vs ~27 d sectors)
    occ=np.zeros(200,bool); occ[(phase*200).astype(int).clip(0,199)]=True
    ph_s=np.sort(phase); gaps=np.diff(np.concatenate([ph_s,[ph_s[0]+1]]))
    sec_phases=[]
    for d in dl_log:
        if d.get('status')!='ok': continue
        tc=0.5*(d['t0_btjd']+d['t1_btjd'])+BTJD_OFFSET-GAIA_REF_JD
        sec_phases.append(round(((tc-Tp)%P)/P,4))
    cov={'phase_frac_covered_200bin':round(float(occ.mean()),3),
         'largest_phase_gap':round(float(gaps.max()),3),
         'sector_center_phases':sec_phases,
         'phase_window_near_conjA_covered': bool(np.any(np.abs(((phase-phi_conjA+0.5)%1)-0.5)<0.02)),
         'phase_window_near_conjB_covered': bool(np.any(np.abs(((phase-phi_conjB+0.5)%1)-0.5)<0.02))}
    out['coverage']=cov
    print(f'[COVER] phase frac covered={cov["phase_frac_covered_200bin"]:.3f}, largest gap={cov["largest_phase_gap"]:.3f}')
    print(f'[COVER] sector center phases={sec_phases}')
    print(f'[COVER] conjA(phi={phi_conjA:.3f}) sampled={cov["phase_window_near_conjA_covered"]}, '
          f'conjB(phi={phi_conjB:.3f}) sampled={cov["phase_window_near_conjB_covered"]}')

    # ---- PULSE STATISTIC at a given fold-phase ----
    # Self-lensing = a positive, narrow brightening near conjunction. We measure the
    # weighted-mean residual in a window around the target phase (matched ~ eclipse/pulse
    # duration). Duration ~ R1 crossing time / orbital motion at conj. For a wide orbit
    # the pulse FWHM in phase is tiny; use a small window (+/-0.5% phase = ~7.6 d).
    def pulse_amp(phi0, ph, rr, ee, half_win=0.01):
        d=np.abs(((ph-phi0+0.5)%1)-0.5)
        m=d<half_win
        if m.sum()<3: return np.nan, np.nan, int(m.sum())
        w=1.0/np.clip(ee[m],1e-6,None)**2
        amp=np.sum(rr[m]*w)/np.sum(w)            # weighted mean residual (fractional flux)
        n=int(m.sum())
        return amp, n, m.sum()
    # signed amplitude (mmag): positive = brightening
    def to_mmag(frac): return -2.5/np.log(10)*frac*1e3   # brightening (frac>0) -> negative mmag (brighter); report +mmag brighter
    # We report pulse as +mmag of BRIGHTENING: amp_frac>0 => brighter => +mmag
    for win in (0.005,0.01,0.02):
        ampA,nA,_=pulse_amp(phi_conjA,phase,r2,e2,win)
        ampB,nB,_=pulse_amp(phi_conjB,phase,r2,e2,win)
        out.setdefault('pulse_measure',{})[f'half_win_{win}']={
            'conjA_amp_frac':None if not np.isfinite(ampA) else round(ampA,6),
            'conjA_amp_mmag_brighter':None if not np.isfinite(ampA) else round(2.5/np.log(10)*ampA*1e3,4),
            'conjA_n':nA,
            'conjB_amp_frac':None if not np.isfinite(ampB) else round(ampB,6),
            'conjB_amp_mmag_brighter':None if not np.isfinite(ampB) else round(2.5/np.log(10)*ampB*1e3,4),
            'conjB_n':nB}
    print('[PULSE] window measures:', json.dumps(out['pulse_measure'], default=str))

    # ---- PERMUTATION / PHASE-SCRAMBLE NULL (empirical FAP) ----
    # Null: the pulse statistic (max positive windowed brightening) at random
    # fold-phases / scrambled phases contains no real signal. If the conjunction
    # amplitude is NOT an outlier vs this null, no detection; the null sets the limit.
    rng=np.random.default_rng(11)
    HALF=0.01
    # statistic = signed brightening amplitude (mmag) in the matched window
    def stat_at(phi0, ph):
        d=np.abs(((ph-phi0+0.5)%1)-0.5); m=d<HALF
        if m.sum()<3: return np.nan
        w=1.0/np.clip(e2[m],1e-6,None)**2
        return 2.5/np.log(10)*(np.sum(r2[m]*w)/np.sum(w))*1e3   # +mmag brighter
    obsA=stat_at(phi_conjA,phase); obsB=stat_at(phi_conjB,phase)
    # (a) random-phase null: same data, statistic at random phases
    nrand=5000
    null_rand=np.array([stat_at(rng.uniform(0,1),phase) for _ in range(nrand)])
    null_rand=null_rand[np.isfinite(null_rand)]
    # (b) phase-scramble null: shuffle the residuals (destroy any phase coherence),
    #     re-measure at the TRUE conjunction phase -> distribution of the conj statistic
    nscr=5000
    null_scrA=np.empty(nscr)
    idx=np.arange(r2.size)
    for k in range(nscr):
        rp=r2[rng.permutation(idx)]
        d=np.abs(((phase-phi_conjA+0.5)%1)-0.5); m=d<HALF
        w=1.0/np.clip(e2[m],1e-6,None)**2
        null_scrA[k]=2.5/np.log(10)*(np.sum(rp[m]*w)/np.sum(w))*1e3
    # FAP for a POSITIVE pulse: fraction of null >= observed (one-sided, brightening)
    fap_randA=float(np.mean(null_rand>=obsA)) if np.isfinite(obsA) else None
    fap_randB=float(np.mean(null_rand>=obsB)) if np.isfinite(obsB) else None
    fap_scrA=float(np.mean(null_scrA>=obsA)) if np.isfinite(obsA) else None
    # 3-sigma upper limit on a brightening pulse from the null spread:
    sig_null=float(np.std(null_scrA))
    ul_3sig_mmag=float(3*sig_null)         # symmetric noise => 3sigma brightening UL
    ul_rand_997=float(np.percentile(null_rand,99.7)) if null_rand.size else None
    detected = bool((fap_scrA is not None and fap_scrA<0.01) and (obsA>0) and geom['geometry_allows_self_lensing'])
    out['permutation_test']={
        'window_half_phase':HALF, 'window_d':round(2*HALF*P,1),
        'obs_conjA_mmag_brighter':None if not np.isfinite(obsA) else round(obsA,4),
        'obs_conjB_mmag_brighter':None if not np.isfinite(obsB) else round(obsB,4),
        'perm_FAP_conjA_phasescramble':fap_scrA,
        'perm_FAP_conjA_randphase':fap_randA, 'perm_FAP_conjB_randphase':fap_randB,
        'null_scramble_std_mmag':round(sig_null,4),
        'null_randphase_p99.7_mmag':None if ul_rand_997 is None else round(ul_rand_997,4),
        'UPPER_LIMIT_3sigma_brightening_mmag':round(ul_3sig_mmag,3),
        'predicted_pulse_mmag_central_crossing':12.73,
        'detected':detected,
        'note':('FAP is one-sided for a BRIGHTENING pulse at the PREDICTED conjunction phase, '
                'from a phase-scramble (and random-phase) null. Detection requires FAP<0.01 AND '
                'obs>0 AND geometry permitting. 3sigma UL from null spread.')}
    print(f'[PERM] obs conjA={obsA:.3f} mmag, conjB={obsB:.3f} mmag (brighter+)')
    print(f'[PERM] phase-scramble FAP(conjA)={fap_scrA:.4f}; random-phase FAP(conjA)={fap_randA:.4f}')
    print(f'[PERM] null scramble std={sig_null:.3f} mmag -> 3sigma brightening UL < {ul_3sig_mmag:.2f} mmag')
    print(f'[PERM] >>> detected={detected} <<<')

    json.dump(out, open('/tmp/sl407_selflens.json','w'), indent=1, default=str)
    np.savez('/tmp/sl407_tess_fold.npz', phase=phase, resid=r2, err=e2, t_btjd=t2)
    print('SAVED /tmp/sl407_selflens.json and /tmp/sl407_tess_fold.npz')
