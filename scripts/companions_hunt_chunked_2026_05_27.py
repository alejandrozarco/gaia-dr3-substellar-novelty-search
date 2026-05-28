"""Companions-of-all-kinds hunt — RA-chunked version.

Splits the NSS+gaia_source JOIN query by RA into 12 30-degree chunks so
each individual query is small enough to complete quickly even when the
Gaia archive is slow. Concatenates chunk results, then runs the same
Thiele-Innes -> M_2 derivation as the original.

Output: data/intermediate/companions_hunt_all_classes_2026_05_18.csv
"""
from __future__ import annotations
import math
import sys
import time
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


def mass_class(m2_msun, in_sb2):
    if m2_msun >= 3.0:
        return 'stellar_BH_imposter' if in_sb2 else 'dormant_BH_candidate'
    if m2_msun >= 1.2:
        return 'stellar_overflow' if in_sb2 else 'dormant_NS_candidate'
    if m2_msun >= 0.5:
        return 'WD_or_low_mass_star'
    if m2_msun >= 0.08:
        return 'M_dwarf_companion'
    if m2_msun >= 0.013:
        return 'BD_candidate'
    return 'planet_candidate'


def fetch_ra_chunk(ra_min, ra_max):
    q = f"""
    SELECT nss.source_id, nss.nss_solution_type, nss.period, nss.eccentricity,
           nss.significance, nss.a_thiele_innes, nss.b_thiele_innes,
           nss.f_thiele_innes, nss.g_thiele_innes,
           g.parallax, g.phot_g_mean_mag, g.bp_rp,
           g.ruwe, g.astrometric_excess_noise_sig,
           g.rv_amplitude_robust, g.rv_chisq_pvalue
    FROM gaiadr3.nss_two_body_orbit AS nss
    JOIN gaiadr3.gaia_source AS g ON g.source_id = nss.source_id
    WHERE nss.nss_solution_type IN ('Orbital','AstroSpectroSB1','OrbitalTargetedSearchValidated','OrbitalTargetedSearch')
      AND nss.significance >= 12
      AND nss.period BETWEEN 100 AND 3000
      AND g.parallax >= 1.0
      AND g.phot_g_mean_mag < 13
      AND nss.a_thiele_innes IS NOT NULL
      AND nss.b_thiele_innes IS NOT NULL
      AND g.ra >= {ra_min} AND g.ra < {ra_max}
    """
    for attempt in range(3):
        try:
            return Gaia.launch_job_async(q).get_results().to_pandas()
        except Exception as e:
            print(f'  RA {ra_min}-{ra_max} attempt {attempt+1}: ERR {type(e).__name__}: {str(e)[:80]}')
            time.sleep(10)
    return None


def main():
    CHUNK_SIZE_DEG = 30  # 12 chunks
    chunks = []
    for ra_min in range(0, 360, CHUNK_SIZE_DEG):
        ra_max = ra_min + CHUNK_SIZE_DEG
        t0 = time.time()
        print(f'Fetching RA {ra_min}-{ra_max} deg ...', flush=True)
        df = fetch_ra_chunk(ra_min, ra_max)
        if df is None or len(df) == 0:
            print(f'  empty')
            continue
        dt = time.time() - t0
        print(f'  {len(df)} rows in {dt:.1f}s', flush=True)
        chunks.append(df)
    if not chunks:
        print('All chunks failed.'); return 1
    pool_df = pd.concat(chunks, ignore_index=True)
    print(f'\nTotal pool: {len(pool_df)}')
    pool = pl.from_pandas(pool_df)

    # SB2 cross-flag (single query against the source_ids)
    src_ids_list = pool['source_id'].to_list()
    sb2_ids = set()
    for i in range(0, len(src_ids_list), 3000):
        sub = src_ids_list[i:i+3000]
        ids = ','.join(str(int(x)) for x in sub)
        q_sb2 = f"""
        SELECT source_id FROM gaiadr3.nss_two_body_orbit
        WHERE source_id IN ({ids}) AND nss_solution_type IN ('SB2','SB2C')
        """
        try:
            sb2 = Gaia.launch_job_async(q_sb2).get_results().to_pandas()
            sb2_ids.update(int(x) for x in sb2['source_id'])
        except Exception as e:
            print(f'  SB2 chunk {i}: ERR')
    print(f'In SB2/SB2C: {len(sb2_ids)}')

    # FLAME M_1
    print('Pulling FLAME M_1 ...')
    chunks_f = []
    for i in range(0, len(src_ids_list), 3000):
        sub = src_ids_list[i:i+3000]
        ids = ','.join(str(int(x)) for x in sub)
        try:
            qf = f"SELECT source_id, mass_flame FROM gaiadr3.astrophysical_parameters WHERE source_id IN ({ids})"
            chunks_f.append(Gaia.launch_job_async(qf).get_results().to_pandas())
        except Exception as e:
            print(f'  FLAME chunk {i}: ERR')
    flame = pl.from_pandas(pd.concat(chunks_f, ignore_index=True))
    flame = flame.with_columns(pl.col('source_id').cast(pl.Int64))
    pool = pool.with_columns(pl.col('source_id').cast(pl.Int64))
    pool = pool.join(flame, on='source_id', how='left')

    # Derive M_2 + class
    rows = []
    for r in pool.iter_rows(named=True):
        A, B, F, G = r['a_thiele_innes'], r['b_thiele_innes'], r['f_thiele_innes'], r['g_thiele_innes']
        if None in (A, B, F, G): continue
        a_phot_mas = photocentric_a_mas(A, B, F, G)
        plx = r['parallax']
        if not (plx and plx > 0): continue
        a_phot_AU = a_phot_mas / plx
        P_yr = r['period'] / 365.25
        if P_yr <= 0: continue
        fM = a_phot_AU**3 / P_yr**2
        M1 = r['mass_flame'] if r['mass_flame'] and r['mass_flame'] > 0.05 else 1.0
        M2 = solve_m2(fM, M1)
        in_sb2 = int(r['source_id']) in sb2_ids
        cls = mass_class(M2, in_sb2)
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
            'rv_chisq_pvalue': r['rv_chisq_pvalue'],
            'class': cls,
        })

    df = pl.DataFrame(rows)
    out = ROOT / 'data' / 'intermediate' / 'companions_hunt_all_classes_2026_05_18.csv'
    df.write_csv(out)
    print(f'\nSaved {len(df)} rows -> {out}')
    print('\nClass distribution:')
    print(df.group_by('class').len().sort('len', descending=True).to_pandas().to_string(index=False))


if __name__ == '__main__':
    sys.exit(main() or 0)
