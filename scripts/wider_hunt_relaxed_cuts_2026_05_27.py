"""2nd-pass wider hunt with relaxed cuts.

Relaxed: G < 14 (catches BH1-class), parallax >= 0.5, P 100-3500 d.
Tightened: significance >= 30 (vs 12 in main hunt) for robustness.
Restricts to Orbital + AstroSpectroSB1 + OrbitalTargetedSearchValidated.

Output: data/intermediate/wider_hunt_2026_05_27.csv
"""
from __future__ import annotations
import math
import sys
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

import polars as pl
import pandas as pd
from astroquery.gaia import Gaia

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')


def photocentric_a_mas(A, B, F, G):
    u = 0.5 * (A*A + B*B + F*F + G*G)
    v = A*G - B*F
    disc = max(0, u*u - v*v)
    return math.sqrt(u + math.sqrt(disc))


def solve_m2(fM_Msun, M1_Msun):
    lo, hi = 1e-4, 1e3
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if mid**3 > fM_Msun * (M1_Msun + mid)**2:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def mass_class(m2):
    if m2 >= 3.0: return 'dormant_BH_candidate'
    if m2 >= 1.2: return 'dormant_NS_candidate'
    if m2 >= 0.5: return 'WD_or_low_mass_star'
    if m2 >= 0.08: return 'M_dwarf_companion'
    if m2 >= 0.013: return 'BD_candidate'
    return 'planet_candidate'


def main():
    print('Querying wider NSS pool (sig>=30, plx>=0.5, G<14, P 100-3500) ...')
    q = """
    SELECT nss.source_id, nss.nss_solution_type, nss.period, nss.eccentricity,
           nss.significance, nss.a_thiele_innes, nss.b_thiele_innes,
           nss.f_thiele_innes, nss.g_thiele_innes,
           g.parallax, g.parallax_error, g.phot_g_mean_mag, g.bp_rp,
           g.ruwe, g.non_single_star, g.ipd_frac_multi_peak,
           g.astrometric_excess_noise, g.astrometric_excess_noise_sig,
           g.rv_amplitude_robust, g.rv_chisq_pvalue
    FROM gaiadr3.nss_two_body_orbit AS nss
    JOIN gaiadr3.gaia_source AS g ON g.source_id = nss.source_id
    WHERE nss.nss_solution_type IN ('Orbital','AstroSpectroSB1','OrbitalTargetedSearchValidated')
      AND nss.significance >= 30
      AND nss.period BETWEEN 100 AND 3500
      AND g.parallax >= 0.5
      AND g.phot_g_mean_mag < 14
      AND nss.a_thiele_innes IS NOT NULL
      AND nss.b_thiele_innes IS NOT NULL
    """
    pool = pl.from_pandas(Gaia.launch_job_async(q).get_results().to_pandas())
    print(f'Pool size: {len(pool)}')

    src_ids = ','.join(str(int(x)) for x in pool['source_id'].to_list())
    q_sb2 = f"""
    SELECT source_id FROM gaiadr3.nss_two_body_orbit
    WHERE source_id IN ({src_ids}) AND nss_solution_type IN ('SB2','SB2C')
    """
    sb2 = Gaia.launch_job_async(q_sb2).get_results().to_pandas()
    sb2_ids = set(int(x) for x in sb2['source_id'])
    print(f'In SB2/SB2C: {len(sb2_ids)}')

    print('Pulling FLAME M_1 + Teff + log g ...')
    chunks = []
    ids_list = [int(x) for x in pool['source_id'].to_list()]
    for i in range(0, len(ids_list), 3000):
        sub = ids_list[i:i+3000]
        ids = ','.join(str(x) for x in sub)
        qf = (f"SELECT source_id, mass_flame, teff_gspphot, logg_gspphot "
              f"FROM gaiadr3.astrophysical_parameters WHERE source_id IN ({ids})")
        chunks.append(Gaia.launch_job_async(qf).get_results().to_pandas())
    flame = pl.from_pandas(pd.concat(chunks, ignore_index=True))
    flame = flame.with_columns(pl.col('source_id').cast(pl.Int64))
    pool = pool.with_columns(pl.col('source_id').cast(pl.Int64))
    pool = pool.join(flame, on='source_id', how='left')

    rows = []
    for r in pool.iter_rows(named=True):
        A, B, F, G = r['a_thiele_innes'], r['b_thiele_innes'], r['f_thiele_innes'], r['g_thiele_innes']
        if None in (A, B, F, G):
            continue
        a_phot_mas = photocentric_a_mas(A, B, F, G)
        plx = r['parallax']
        if not (plx and plx > 0):
            continue
        a_phot_AU = a_phot_mas / plx
        P_yr = r['period'] / 365.25
        if P_yr <= 0:
            continue
        fM = a_phot_AU**3 / P_yr**2
        M1 = r['mass_flame'] if r['mass_flame'] and r['mass_flame'] > 0.05 else 1.0
        M2 = solve_m2(fM, M1)
        in_sb2 = int(r['source_id']) in sb2_ids
        cls = mass_class(M2)
        bp_rp = r['bp_rp'] if r['bp_rp'] else None
        logg = r['logg_gspphot'] if r['logg_gspphot'] else None
        cbias_risk = (bp_rp and bp_rp > 1.2) or (logg and logg < 2.7)
        rows.append({
            'source_id': r['source_id'],
            'nss_solution_type': r['nss_solution_type'],
            'P_d': r['period'], 'e': r['eccentricity'],
            'significance': r['significance'],
            'a_phot_mas': round(a_phot_mas, 4),
            'parallax': plx, 'G': r['phot_g_mean_mag'], 'bp_rp': r['bp_rp'],
            'ruwe': r['ruwe'],
            'M1_msun': round(M1, 3),
            'fM_msun': round(fM, 4),
            'M2_msun': round(M2, 4),
            'in_sb2': in_sb2,
            'rv_amplitude_robust': r['rv_amplitude_robust'],
            'Teff': r['teff_gspphot'], 'logg': r['logg_gspphot'],
            'cbias_risk': cbias_risk,
            'class': cls,
        })

    df = pl.DataFrame(rows)
    out = ROOT / 'data' / 'intermediate' / 'wider_hunt_2026_05_27.csv'
    df.write_csv(out)
    print(f'\nSaved {len(df)} rows -> {out}')
    print('\nClass distribution:')
    print(df.group_by('class').len().sort('len', descending=True).to_pandas().to_string(index=False))

    KNOWN = {4373465352415301632: 'BH1', 5870569352746779008: 'BH2', 4318465066420528000: 'BH3'}
    print('\nKnown Gaia BHs in wider hunt:')
    for sid, nm in KNOWN.items():
        f = df.filter(pl.col('source_id') == sid)
        if len(f):
            r = f.row(0, named=True)
            print(f'  {nm}: class={r["class"]}, M2={r["M2_msun"]:.2f}, sig={r["significance"]:.1f}')


if __name__ == '__main__':
    sys.exit(main() or 0)
