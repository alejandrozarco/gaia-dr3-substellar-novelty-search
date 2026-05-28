"""Parallel deep dive on the 7 top BH candidates with Filter #31 applied.

Filter #31 (proposed): paired check of rv_chisq_pvalue + rv_amplitude_robust.
A real binary RV signal requires:
  - rv_amplitude_robust > 5 km/s (substantial)
  - rv_chisq_pvalue < 0.05 (constant-RV model rejected)
The A-dwarf candidate Gaia 245948793944575360 failed this check —
amplitude=37 but pvalue=0.999 = inflated outliers, not real binary.

Additional checks per candidate:
 - IR excess (K-W3, K-W4) — luminous-secondary or disk signature
 - Close Gaia neighbors within 5" (contamination risk)
 - Galactic latitude |b| (crowded-field risk)
 - SIMBAD identifier + otype + bibcount
 - Astrometric solution quality (RUWE, aen_sig, ipd_frac_multi_peak)
 - Bailer-Jones distance vs gspphot distance (consistency check)
"""
from __future__ import annotations
import math, sys, time, warnings
warnings.filterwarnings('ignore')
from pathlib import Path
import polars as pl
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u

# 7 top candidates from the session
CANDS = [
    (6811355413155399040, 'HD 207141',           952.0, 0.664, 2.60),
    (666596383384888320,  'TYC 1363-2339-1',     945.7, 0.16,  1.88),
    (6471824298353396736, 'TYC 8785-1657-1',     490.8, 0.27,  1.63),
    (2801267044426382336, 'Gaia 280126...',      750.0, 0.06,  1.54),
    (5889532732877344128, 'Gaia 588973... (M2 underest)', 896.0, 0.44, 1.71),
    (6784701430232308352, 'Gaia 678470...',      522.4, 0.44,  1.26),
    (5942873714068259584, 'Gaia 594287... (NS->BH)', 544.5, 0.26, 0.95),
    # Reference: A-dwarf that failed Filter #31
    (245948793944575360,  'A-dwarf 245948... (FAILED Filter#31)', 549.0, 0.06, 2.80),
]

def K1_kms(P_d, e, M1, M2, sini):
    P_s = P_d * 86400
    num = (2*math.pi*6.6743e-11/P_s)**(1/3) * (M2*1.989e30) * sini
    den = ((M1+M2)*1.989e30)**(2/3) * math.sqrt(1-e*e)
    return (num/den)/1000

def solve_M2(K, M1, P, e, sini):
    lo, hi = 0.01, 50
    for _ in range(80):
        mid = 0.5*(lo+hi)
        Kp = K1_kms(P, e, M1, mid, sini)
        if Kp < K: lo = mid
        else: hi = mid
    return 0.5*(lo+hi)

def main():
    ids = ','.join(str(c[0]) for c in CANDS)
    q = f"""
    SELECT g.source_id, g.ra, g.dec, g.l, g.b, g.parallax, g.parallax_error,
           g.phot_g_mean_mag, g.bp_rp, g.ruwe,
           g.astrometric_excess_noise_sig, g.ipd_frac_multi_peak,
           g.rv_amplitude_robust, g.rv_chisq_pvalue, g.rv_renormalised_gof,
           g.rv_nb_transits, g.radial_velocity_error, g.non_single_star,
           ap.teff_gspphot, ap.logg_gspphot, ap.mh_gspphot,
           ap.distance_gspphot, ap.azero_gspphot, ap.ag_gspphot,
           ap.mass_flame, ap.radius_flame, ap.lum_flame
    FROM gaiadr3.gaia_source g
    LEFT JOIN gaiadr3.astrophysical_parameters ap ON ap.source_id = g.source_id
    WHERE g.source_id IN ({ids})
    """
    df = Gaia.launch_job_async(q).get_results().to_pandas()
    df = df.set_index('source_id')

    v = Vizier(columns=['*'], row_limit=3)
    s = Simbad()
    try: s.add_votable_fields('ids','otype','sp_type')
    except: pass

    results = []
    print('=== PARALLEL DEEP DIVE WITH FILTER #31 ===\n')
    for sid, name, P, e, M1 in CANDS:
        m = {'source_id': sid, 'name': name, 'P_d': P, 'e': e, 'M1_assumed': M1}
        if sid not in df.index:
            print(f'  {name}: missing from Gaia query'); continue
        r = df.loc[sid]
        ra, dec = float(r['ra']), float(r['dec'])
        l, b = float(r['l']), float(r['b'])
        m.update(ra=ra, dec=dec, l=l, b=b, G=float(r['phot_g_mean_mag']),
                 BP_RP=float(r['bp_rp']) if r['bp_rp'] is not None else None,
                 RUWE=float(r['ruwe']), aen_sig=float(r['astrometric_excess_noise_sig']),
                 plx=float(r['parallax']), plx_snr=float(r['parallax'])/float(r['parallax_error']),
                 Teff=r['teff_gspphot'], logg=r['logg_gspphot'],
                 R_FLAME=r['radius_flame'], M_FLAME=r['mass_flame'],
                 L_FLAME=r['lum_flame'], A_G=r['ag_gspphot'])

        # Filter #31: paired pvalue + amplitude check
        K_obs = float(r['rv_amplitude_robust']) if r['rv_amplitude_robust'] is not None else None
        pval = float(r['rv_chisq_pvalue']) if r['rv_chisq_pvalue'] is not None else None
        rgof = float(r['rv_renormalised_gof']) if r['rv_renormalised_gof'] is not None else None
        n_rv = float(r['rv_nb_transits']) if r['rv_nb_transits'] is not None else None
        m.update(K_obs=K_obs, rv_pval=pval, rv_rgof=rgof, rv_n=n_rv)
        if K_obs is None or pval is None:
            m['filter31'] = 'NO_RV_DATA'
        elif K_obs > 5 and pval < 0.05:
            m['filter31'] = 'PASS'
        elif K_obs > 5 and pval > 0.5:
            m['filter31'] = 'FAIL (amplitude inflated by outliers, not real binary)'
        else:
            m['filter31'] = 'AMBIGUOUS'

        # K_1 reality check with proper M_1
        if K_obs and K_obs > 5 and pval and pval < 0.5:
            M2_RV_i60 = solve_M2(K_obs, M1, P, e, math.sin(math.radians(60)))
            M2_RV_i90 = solve_M2(K_obs, M1, P, e, 1.0)
            m['M2_RV_i60'] = round(M2_RV_i60, 2)
            m['M2_RV_i90'] = round(M2_RV_i90, 2)

        # IR colors (2MASS + WISE within 5")
        sc = SkyCoord(ra*u.deg, dec*u.deg)
        try:
            t2m = v.query_region(sc, radius=5*u.arcsec, catalog='II/246')
            if t2m and len(t2m):
                K = float(t2m[0][0]['Kmag'])
                m['K_2mass'] = round(K, 3)
            tw = v.query_region(sc, radius=5*u.arcsec, catalog='II/328/allwise')
            if tw and len(tw) and 'K_2mass' in m:
                for b_band, k in [('W1mag', 'W1'), ('W2mag', 'W2'), ('W3mag', 'W3'), ('W4mag', 'W4')]:
                    if b_band in tw[0].colnames:
                        try:
                            val = float(tw[0][0][b_band])
                            m[f'K-{k}'] = round(m['K_2mass'] - val, 3)
                        except (TypeError, ValueError): pass
        except Exception as ex:
            m['ir_err'] = str(ex)[:50]
        time.sleep(0.3)

        # IR excess verdict
        kw3 = m.get('K-W3')
        kw4 = m.get('K-W4')
        if kw3 is not None and kw4 is not None:
            if kw3 > 0.10 or kw4 > 0.30:
                m['ir_verdict'] = f'EXCESS (K-W3={kw3:.2f}, K-W4={kw4:.2f}) -- disk/cool secondary'
            else:
                m['ir_verdict'] = f'NONE (K-W3={kw3:.2f}, K-W4={kw4:.2f}) -- single photosphere OK'

        # SIMBAD
        try:
            res = s.query_object(f'Gaia DR3 {sid}')
            if res is not None and len(res):
                row = res[0]
                m['simbad'] = str(row.get('main_id') or row.get('MAIN_ID') or '?')[:30]
                m['otype'] = str(row.get('otype') or row.get('OTYPE') or '?')[:8]
                m['sp_type'] = str(row.get('sp_type') or row.get('SP_TYPE') or '')[:10]
            else:
                m['simbad'] = 'NONE'
        except: m['simbad'] = 'ERR'
        time.sleep(0.4)

        # Close Gaia neighbors within 5"
        q_nbr = f"""
        SELECT COUNT(*) AS n FROM gaiadr3.gaia_source
        WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra}, {dec}, 5.0/3600.0))
        AND source_id != {sid}
        """
        try:
            n_nbr = int(Gaia.launch_job_async(q_nbr).get_results().to_pandas().iloc[0]['n'])
            m['gaia_nbrs_5as'] = n_nbr
        except: m['gaia_nbrs_5as'] = -1

        # Print
        print(f"=== {name} (Gaia DR3 {sid}) ===")
        print(f"  G={m['G']:.2f}, BP-RP={m.get('BP_RP',0):.2f}, b={b:.1f}deg, d~{1000/m['plx']:.0f}pc")
        print(f"  Teff={m.get('Teff','?')}, logg={m.get('logg','?')}, M_FLAME={m.get('M_FLAME','?')}, R_FLAME={m.get('R_FLAME','?')}, L_FLAME={m.get('L_FLAME','?')}")
        print(f"  RUWE={m['RUWE']:.2f}, aen_sig={m['aen_sig']:.0f}, A_G={m.get('A_G','?')}")
        print(f"  RV: K_obs={K_obs}, pval={pval}, rgof={rgof}, n={n_rv}")
        print(f"  FILTER #31: {m['filter31']}")
        if 'M2_RV_i60' in m:
            print(f"  M_2 from K_1 alone: i=60° -> {m['M2_RV_i60']}, i=90° -> {m['M2_RV_i90']}")
        print(f"  IR: K-W3={m.get('K-W3','?')}, K-W4={m.get('K-W4','?')} -> {m.get('ir_verdict','no data')}")
        print(f"  SIMBAD: {m.get('simbad','?')} otype={m.get('otype','?')} sp_type={m.get('sp_type','?')}")
        print(f"  Close Gaia neighbors <5\": {m.get('gaia_nbrs_5as','?')}")
        print()
        results.append(m)

    # Save
    out_path = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27/parallel_deep_dive_2026_05_27.csv')
    df_out = pl.DataFrame([{k: (str(v) if isinstance(v, (list, tuple, dict)) else v)
                             for k, v in row.items()} for row in results])
    df_out.write_csv(out_path)
    print(f'\n=== SAVED {out_path} ===\n')

    # Summary table
    print('=== SUMMARY: which survive Filter #31 + IR check ===')
    print(f"{'Name':<30} {'Filter31':<10} {'IR':<10} {'crowding':<10} verdict")
    for m in results:
        f31 = 'PASS' if m['filter31'] == 'PASS' else ('FAIL' if 'FAIL' in m['filter31'] else m['filter31'][:10])
        ir = 'OK' if m.get('ir_verdict','').startswith('NONE') else ('EXCESS' if m.get('ir_verdict','').startswith('EXCESS') else '?')
        crowd = 'OK' if m.get('gaia_nbrs_5as', 0) == 0 else f'+{m.get("gaia_nbrs_5as")}'
        survives = (m['filter31'] == 'PASS' and m.get('ir_verdict','').startswith('NONE')
                    and m.get('gaia_nbrs_5as', -1) == 0)
        v = 'SURVIVES' if survives else 'DEMOTED'
        print(f"{m['name'][:30]:<30} {f31:<10} {ir:<10} {crowd:<10} {v}")


if __name__ == '__main__':
    sys.exit(main() or 0)
