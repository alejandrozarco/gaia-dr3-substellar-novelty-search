"""Fast triage of 42 defensible BH+NS candidates (12+30) via SIMBAD + K_1.

Defensible cuts:
  BH: sig >= 30, RUWE < 10, plx >= 1.5  -> 12 candidates from main hunt
  NS: sig >= 30, RUWE < 5,  plx >= 1.5  -> 30 top by sig from main hunt

Output: triage_fast_2026_05_27.csv
"""
from __future__ import annotations
import math, sys, time, warnings
warnings.filterwarnings('ignore')
from pathlib import Path
import polars as pl

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')


def K1_kms(P, e, M1, M2, sini):
    P_s = P * 86400
    num = (2*math.pi*6.6743e-11/P_s)**(1/3) * (M2*1.989e30) * sini
    den = ((M1+M2)*1.989e30)**(2/3) * math.sqrt(1-e*e)
    return (num/den)/1000


def main():
    hunt_path = ROOT / 'data' / 'intermediate' / 'companions_hunt_all_classes_2026_05_18.csv'
    if not hunt_path.exists():
        print(f'Hunt CSV missing: {hunt_path}'); return 1
    df = pl.read_csv(hunt_path)

    bh = df.filter(
        (pl.col('class') == 'dormant_BH_candidate') &
        (pl.col('significance') >= 30) & (pl.col('ruwe') < 10) &
        (pl.col('parallax') >= 1.5)
    ).sort('significance', descending=True).head(12).with_columns(pl.lit('BH').alias('label'))
    ns = df.filter(
        (pl.col('class') == 'dormant_NS_candidate') &
        (pl.col('significance') >= 30) & (pl.col('ruwe') < 5) &
        (pl.col('parallax') >= 1.5)
    ).sort('significance', descending=True).head(30).with_columns(pl.lit('NS').alias('label'))
    cands = pl.concat([bh, ns])
    print(f'Triaging {len(cands)} (12 BH + 30 NS) ...')

    from astroquery.gaia import Gaia
    ids = ','.join(str(int(x)) for x in cands['source_id'].to_list())
    q = f"""
    SELECT g.source_id, g.phot_g_mean_mag, g.bp_rp, g.ruwe, g.parallax,
           g.rv_amplitude_robust, g.rv_chisq_pvalue, g.rv_nb_transits,
           ap.teff_gspphot, ap.logg_gspphot, ap.mass_flame, ap.radius_flame
    FROM gaiadr3.gaia_source g
    LEFT JOIN gaiadr3.astrophysical_parameters ap ON ap.source_id = g.source_id
    WHERE g.source_id IN ({ids})
    """
    g_df = Gaia.launch_job_async(q).get_results().to_pandas()
    g_map = {int(r['source_id']): r for _, r in g_df.iterrows()}

    from astroquery.simbad import Simbad
    s = Simbad()
    try: s.add_votable_fields('ids', 'otype', 'sp_type')
    except: pass

    results = []
    for ci, c in enumerate(cands.iter_rows(named=True)):
        sid = int(c['source_id'])
        sig = float(c['significance']); P = float(c['P_d']); e = float(c['e'])
        M1 = float(c['M1_msun']); M2 = float(c['M2_msun'])
        m = {'rank': ci+1, 'source_id': sid, 'label': c['label'],
             'nss_type': c['nss_solution_type'], 'sig': sig, 'P_d': P, 'e': e,
             'M1': M1, 'M2_cascade': M2}

        gr = g_map.get(sid)
        if gr is not None:
            for k_src, k_dst in [('phot_g_mean_mag','G'),('bp_rp','BP_RP'),('ruwe','RUWE'),
                                  ('parallax','plx'),('rv_amplitude_robust','K_obs'),
                                  ('rv_chisq_pvalue','rv_pval'),
                                  ('teff_gspphot','Teff'),('logg_gspphot','logg'),
                                  ('mass_flame','M1_FLAME'),('radius_flame','R_FLAME')]:
                v = gr.get(k_src)
                try: m[k_dst] = float(v) if v is not None else None
                except: m[k_dst] = None

        K_obs = m.get('K_obs')
        pval = m.get('rv_pval')
        if K_obs and K_obs > 0 and pval is not None:
            K90 = K1_kms(P, e, M1, M2, 1.0)
            K60 = K1_kms(P, e, M1, M2, math.sin(math.radians(60)))
            m['K_pred_90'] = round(K90, 1); m['K_pred_60'] = round(K60, 1)
            if K_obs > 5 and pval < 0.05:
                m['filter31'] = 'PASS'
            elif pval > 0.5 and K_obs > 5:
                m['filter31'] = 'FAIL_outlier_inflated'
            else:
                m['filter31'] = 'AMBIGUOUS'
        else:
            m['filter31'] = 'NO_DATA'

        try:
            res = s.query_object(f'Gaia DR3 {sid}')
            if res is not None and len(res):
                r = res[0]
                m['simbad'] = str(r.get('main_id') or r.get('MAIN_ID') or '?')[:25]
                m['otype'] = str(r.get('otype') or r.get('OTYPE') or '?')[:8]
                m['sp_type'] = str(r.get('sp_type') or r.get('SP_TYPE') or '')[:10]
            else:
                m['simbad'] = 'NONE'
        except: m['simbad'] = 'ERR'
        time.sleep(0.4)

        cbr = []
        if m.get('BP_RP') is not None and m['BP_RP'] > 1.2: cbr.append('red')
        if m.get('logg') is not None and m['logg'] < 2.7: cbr.append('lowg')
        sp = (m.get('sp_type') or '').upper()
        if any(c in sp for c in ['III','IV','II ']): cbr.append('giant_sp')
        m['cbias_flags'] = '|'.join(cbr) if cbr else 'none'

        score = 0
        if not m.get('otype') or m['otype'] == '*': score += 3
        elif 'SB' not in (m['otype'] or '') and 'V*' not in (m['otype'] or ''): score += 2
        if not cbr: score += 3
        if m['filter31'] == 'PASS': score += 3
        m['lead_score'] = score

        g_str = f'{m["G"]:.2f}' if m.get('G') is not None else '  ?  '
        print(f'[{ci+1:2}/{len(cands)}] {c["label"]} sid={sid} sig={sig:>5.0f} G={g_str:>5} '
              f'M2={M2:>5.2f} | {m.get("simbad","?")[:22]:<22} otype={m.get("otype","?"):<10} '
              f'cbias={m["cbias_flags"]:<15} F31={m["filter31"]:<12} score={score}')
        results.append(m)

    df_out = pl.DataFrame([{k: (str(v) if not isinstance(v, (int, float, bool, type(None))) else v)
                              for k, v in row.items()} for row in results])
    df_out = df_out.sort('lead_score', descending=True)
    df_out.write_csv(ROOT / 'triage_fast_2026_05_27.csv')
    print(f'\nSaved triage_fast_2026_05_27.csv ({len(df_out)} rows)')
    print('\nTop 10:')
    print(df_out.head(10).select(['source_id','label','sig','M2_cascade','simbad','otype',
                                     'cbias_flags','filter31','lead_score']).to_pandas().to_string())
    return 0


if __name__ == '__main__':
    sys.exit(main())
