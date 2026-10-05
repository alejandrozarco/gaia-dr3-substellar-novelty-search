import pandas as pd, numpy as np, os
from lcio import ztf
t=pd.read_csv('gates.csv'); F=pd.read_csv('feat_gaia.csv').set_index('Name'); D=pd.read_csv('candidates_full.csv')
M=pd.read_csv('mlfit.csv').set_index('Name')
S=t[t.survive&~t.Name.isin(D.alert)].copy()
manual={
'Gaia21bfr':'excellent achromatic PSPL event (Gaia+ZTF g,r; tE~150 d) but already named in arXiv:2201.12209 (microlensing early-recognition paper) and has Gemini archive data -> literature-known, not novel',
'Gaia21dpb':'excellent achromatic event (Gaia+ZTF g,r) but published: 2026A&A...705A..24P (lens masses of magnified microlensing events) -> not novel',
'Gaia17aqc':'CV-like ZTF outbursts, but J/A+A/705/A247 (ZTF classifier) already labels it CV/Nova and an SDSS spectrum (low S/N) gives z=0.994 (CLASS cat., ApSS 365, 89 Gaia-alert spectra list) -> conflicting/published',
'Gaia18dnu':'LMC carbon star: already in OGLE-III LMC LPV catalogue (AcA 59, 239) and EROS-2 LMC periodic variables -> known variable (VSX 5" check missed it)',
'Gaia19bba':'2-mag rise 2018-19, 3-yr plateau, decline; W1-W2 1.03 W2-W3 3.08, pm 96 sigma (Galactic). FUor/EXor outburst vs RCB-type recovery ambiguous; b=+10.5 with no SFR within 5\'; needs spectrum',
'Gaia24bej':'blue (BP-RP -0.03) irregular 1.1-mag variable, GALEX + 4XMM X-ray source; pm matches LMC -> likely LMC Be/X-ray-binary candidate; type (GCAS/BE vs XB) undetermined',
'Gaia24bne':'single sharp event MJD 60479 (ZTF r 20.7->17.5): PSPL fit acceptable (tE 74 d, u0 0.015, chi2r 1.46) but UG superoutburst equally possible (b=+3.7)',
'Gaia22agi':'repeated small brightenings + one ~1-mag episode (MJD ~59750-59800); pm 9 mas/yr; UG possible but amplitude/recurrence not established',
'Gaia23bxb':'blue (BP-RP 0.52) irregular 2-mag variable at b=-23, pm 10 mas/yr; CV vs other undetermined; Gaia-only',
'Gaia23bhk':'irregular high/low variability in ZTF (1.5 mag), BP-RP 1.24, b=-23; CV (NL/polar) vs AGN undetermined (pm ~5 mas/yr, plx 0.4 sigma)',
'Gaia21dro':'blue (BP-RP 0.27) faint source, 45 Gaia points, few bright points; CV possible; too sparse',
'Gaia24dms':'stochastic ZTF/Gaia variability; Gaia QSO-candidate flag, plx 0.2 sigma, pm ~3.6 sigma -> possible AGN',
'Gaia22ehm':'single short ZTF/Gaia outburst (r 19->16.5, MJD ~59800) at b=+15; one outburst only -> UG not established',
'Gaia14aaw':'single 2-mag outburst 2014 (Gaia only), ZTF flat at r~20.5 2018-2025; UG/flare undetermined',
'Gaia18aje':'Gaia LC mostly at G~17.9 with sporadic points at ~20.5; neighbour G=19.33 at 1.3" -> likely window/blend artefact (or deep EA); not usable',
'Gaia18dnd':'5 Gaia points; alert comment "candidate SN in galaxy pair Mrk 1116" -> extragalactic transient, not a variable star',
'Gaia23cdv':'SPICY flat-spectrum YSO with 1.5-mag dips (UXOR-like); Gaia DR3 classifier labels it LPV; type ambiguous',
'Gaia24awl':'red (BP-RP 3.2) W1-W2 0.85 source with occasional 1-mag dips and late rise; YSO dipper possible; sparse',
'Gaia21bzk':'SPICY Class I YSO, slow 1.2-mag brightening 2020-2023 with earlier 0.7-mag wave; INSA plausible but already a catalogued YSO and amplitude modest',
'Gaia23bbp':'slow monotonic 1.5-mag rise 2018-2023 (G 19->17.4), BP-RP 4.0, W1-W2 0.75; YSO outburst vs obscured LPV undetermined; Gaia-only',
'Gaia24chd':'irregular 2-mag ZTF variability, W1-W2 0.92, b=+6; YSO plausible but no SFR within 5\'',
'Gaia21dht':'irregular, W1-W2 0.76, near DNe/MoC; YSO plausible; sparse ZTF',
'Gaia22cnz':'irregular rising Gaia LC, W1-W2 0.71; YSO plausible; Gaia-only',
'Gaia19bnk':'irregular 2-mag Gaia variability, W1-W2 0.86; neighbour G=19.57 at 2.65"; YSO plausible',
'Gaia23dta':'slow rise from 2023 then 2.5-mag jump at end of Gaia LC (SFR direction); YSO outburst vs microlensing undetermined; no post-2025 data (ATLAS hole)',
'Gaia24cmz':'smooth 1.8-mag rise over final ~1 yr of Gaia LC (PSPL tE~330 d fits) but decline not observed; no ZTF/ATLAS',
'Gaia22bta':'irregular 2.5-mag variability, BP-RP 0.7, near SFR (14 YSO cands within 5\'); sparse; class undetermined',
'Gaia24bzb':'slow 1.5-mag decline 2015-2023 with dips then ZTF re-brightening; class undetermined',
'Gaia22daz':'',
'Gaia17aqc':'CV-like ZTF outbursts, but J/A+A/705/A247 (ZTF classifier) already labels it CV/Nova and an SDSS spectrum (low S/N) gives z=0.994 (CLASS cat.; Gaia-alert spectra list ApSS 365, 89) -> conflicting/published',
'Gaia19baz':'Gaia event (tE~180 d PSPL) but named in arXiv:2201.12209; SIMBAD YSO candidate (Gaia DR3 5885942067141371136 Y*?)',
'Gaia19aqh':'Gaia-only event; named in arXiv:2201.12209',
'Gaia18eaz':'Gaia-only 3-mag event (few transits); named in arXiv:2201.12209',
'Gaia17cfu':'M dwarf (plx 8.4 sigma, M_G 10.1, BP-RP 2.29) with 2 Gaia flares (UV-type), but named in arXiv:2201.12209 -> literature mention; check that paper before filing',
'Gaia18chm':'irregular; neighbour G=20.31 at 1.9"; mentioned in 2019CoSka..49..358G (Terskol follow-up)',
'Gaia20fff':'only 11 Gaia points; unusable',
'Gaia20bjx':'only 9 Gaia points; unusable',
'Gaia22btb':'only 16 Gaia points; neighbours within 3"; unusable',
'Gaia21ejz':'one bright and one faint outlier only; likely artefact',
'Gaia21ftk':'small dips/brightenings (<1 mag in ZTF), BP-RP 0.47; amplitude claim not confirmed',
'Gaia23auz':'irregular <1 mag; amplitude driven by few points',
'Gaia24den':'irregular ~1 mag; eRASS1 source 7.9" (outside error); class undetermined',
'Gaia23bzn':'irregular ~1 mag; 1WGA X-ray source at 4.9"; class undetermined',
'Gaia18cik':'ZTF r rise to 18.8 then dip to >21 below baseline; inconsistent with simple event; possible ZTF source confusion',
'Gaia24arb_':'',
}
rows=[]
for r in S.itertuples():
    n=r.Name; f=F.loc[n]
    if n in manual and manual[n]: reason=manual[n]
    else:
        hasz=os.path.exists(f'ztf/{n}.csv')
        ev='at the end of the Gaia light curve (decline unobserved)' if (f.last_t-f.t_peak)<60 else 'mid-light-curve'
        reason=f'single brightening of {f.amp:.1f} mag {ev}, covered by {int(f.n_bright_pts)} Gaia transit(s)'
        reason+= '; ZTF does not sample the event' if hasz else ('; no ZTF (south)' if r.DEdeg<-31 else '; no ZTF data')
        reason+='; microlensing vs CV outburst vs flare undetermined'
        if r.g_blend=='FLAG': reason+=f'; brighter Gaia neighbour within 3" ({r.nb_brighter3.split(";")[0]})'
    rows.append(dict(alert=n,gaia_dr3=str(int(r.Source)),ra_deg=round(r.RAdeg,5),dec_deg=round(r.DEdeg,5),l=round(r.l,1),b=round(r.b,1),G=round(r.Gmag,2),bp_rp=round(r.BPmag-r.RPmag,2) if r.BPmag==r.BPmag else '',alert_comment=r.Comment,reason=reason))
W=pd.DataFrame(rows); W.to_csv('weak_list.csv',index=False); print(len(W))
print(W[W.alert.isin(manual)][['alert','reason']].to_string())
# hard-gate rejects
R=t[~t.survive]
def why(x):
    w=[]
    if x.g_ml=='FAIL': w.append('OGLE/KMT: '+x.ml_all)
    if x.g_simbad=='FAIL': w.append('SIMBAD: '+x.simbad_le2)
    if x.g_qso=='FAIL': w.append(f'quasar/galaxy: PQSO={x.PQSO:.2f} PGal={x.PGal:.2f}')
    return '; '.join(w)
R=R.assign(reason=R.apply(why,axis=1))[['Name','RAdeg','DEdeg','Comment','reason']]
ads=pd.read_csv('ads_full.csv'); R.to_csv('gate_rejects.csv',index=False); print(R.to_string())
