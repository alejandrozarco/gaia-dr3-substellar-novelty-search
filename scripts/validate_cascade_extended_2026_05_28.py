#!/usr/bin/env python3
"""Cascade validation runner — extended benchmark suite (2026-05-28).

Runs the v2-corrected cascade against:
  Group A: Confirmed dormant black holes (Gaia BH1/BH2/BH3)
  Group B: Shahaf+ 2024 OJAp dormant NS candidates (21 sources)
  Group C: Andrews+ 2022 + Shahaf+ 2023b candidates (40 sources from Table 3 of Shahaf+ 2024)
  Group D: Known false-positive calibrators (4 UMi, phantom-RV A-dwarf, HD 76078)
  Group E: Sub-stellar / stellar binary recovery targets (HD 81040 b, HD 111232 b, HD 188112)

For each source we (a) check our 56,100-row v2 parquet first, (b) fall back to a
live Gaia DR3 ADQL query if not in the pool, (c) apply derive_row_v2 with the
literature primary-mass prior, and (d) classify the cascade outcome.

Output: data/validation_2026_05_28/results.csv + per-group rollups, plus the
markdown report at docs/CASCADE_VALIDATION_EXTENDED_2026_05_28.md.
"""
from __future__ import annotations
import math
import sys
import time
import warnings
from pathlib import Path

import pandas as pd
import numpy as np

warnings.filterwarnings('ignore')

# ---------- Imports from the project ----------
ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')
sys.path.insert(0, str(ROOT))
from scripts.streaming.v2_corrected.consumer_v2 import (
    derive_row_v2,
    photocentric_a_mas,
)

TEST_CSV = ROOT / 'data/validation_2026_05_28/test_set.csv'
PARQUET = ROOT / 'data/derived/main_hunt_derived_v2.parquet'
OUT_CSV = ROOT / 'data/validation_2026_05_28/results.csv'


# ---------- Gaia ADQL query (mirrors web_tool/app.py query_gaia_live) ----------

ADQL = """
SELECT g.source_id, g.ra, g.dec, g.l, g.b,
       g.parallax, g.pmra, g.pmdec,
       g.phot_g_mean_mag, g.bp_rp, g.ruwe,
       g.astrometric_excess_noise_sig, g.non_single_star,
       g.radial_velocity, g.rv_amplitude_robust, g.rv_chisq_pvalue,
       g.rv_nb_transits,
       n.nss_solution_type, n.period, n.eccentricity,
       n.a_thiele_innes, n.b_thiele_innes,
       n.f_thiele_innes, n.g_thiele_innes,
       n.significance,
       n.parallax AS nss_parallax,
       ap.teff_gspphot, ap.logg_gspphot, ap.mass_flame, ap.radius_flame,
       ap.teff_gspspec, ap.logg_gspspec, ap.spectraltype_esphs,
       aps.teff_gspspec_ann, aps.logg_gspspec_ann, aps.radius_flame_spec
FROM gaiadr3.gaia_source AS g
LEFT JOIN gaiadr3.nss_two_body_orbit AS n  USING (source_id)
LEFT JOIN gaiadr3.astrophysical_parameters AS ap USING (source_id)
LEFT JOIN gaiadr3.astrophysical_parameters_supp AS aps USING (source_id)
WHERE g.source_id = {sid}
"""


def _to_pyfloat(v):
    if v is None:
        return None
    try:
        f = float(v)
        if math.isnan(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def query_gaia_one(source_id: int, timeout_s: int = 45) -> dict | None:
    """Run a single source query against Gaia DR3; return dict or None on failure."""
    try:
        from astroquery.gaia import Gaia
        Gaia.MAIN_GAIA_TABLE = 'gaiadr3.gaia_source'
        job = Gaia.launch_job_async(ADQL.format(sid=int(source_id)))
        tbl = job.get_results()
        if tbl is None or len(tbl) == 0:
            return None
        out = {}
        for c in tbl.colnames:
            val = tbl[c][0]
            # Mask -> None
            try:
                if hasattr(val, 'mask') and val.mask:
                    out[c] = None
                    continue
            except Exception:
                pass
            try:
                if isinstance(val, (np.ndarray,)) or hasattr(val, 'dtype'):
                    if hasattr(val, 'item'):
                        val = val.item()
            except Exception:
                pass
            out[c] = val
        return out
    except Exception as exc:
        print(f'    Gaia query failed for {source_id}: {type(exc).__name__}: {str(exc)[:120]}')
        return None


def _classify(M1, M2):
    """Re-use mass_class but with explicit None handling."""
    if M2 is None:
        return None
    if M2 >= 3.0:
        return 'dormant_BH_candidate'
    if M2 >= 1.2:
        return 'dormant_NS_candidate'
    if M2 >= 0.5:
        return 'WD_or_low_mass_star'
    if M2 >= 0.08:
        return 'M_dwarf_companion'
    if M2 >= 0.013:
        return 'BD_candidate'
    return 'planet_candidate'


def build_row_from_gaia(g: dict) -> dict:
    """Translate a raw Gaia ADQL row into the input shape derive_row_v2 expects."""
    A = _to_pyfloat(g.get('a_thiele_innes'))
    B = _to_pyfloat(g.get('b_thiele_innes'))
    F = _to_pyfloat(g.get('f_thiele_innes'))
    G = _to_pyfloat(g.get('g_thiele_innes'))
    a_phot = photocentric_a_mas(A, B, F, G) if (A is not None and B is not None and F is not None and G is not None) else None

    return {
        'a_phot_mas': a_phot,
        'parallax': _to_pyfloat(g.get('parallax')),
        'nss_parallax': _to_pyfloat(g.get('nss_parallax')),
        'P_d': _to_pyfloat(g.get('period')),
        'eccentricity': _to_pyfloat(g.get('eccentricity')),
        'bp_rp': _to_pyfloat(g.get('bp_rp')),
        'logg_gspphot': _to_pyfloat(g.get('logg_gspphot')),
        'logg_gspspec_ann': _to_pyfloat(g.get('logg_gspspec_ann')),
        'logg_gspspec': _to_pyfloat(g.get('logg_gspspec')),
        'teff_gspphot': _to_pyfloat(g.get('teff_gspphot')),
        'teff_gspspec_ann': _to_pyfloat(g.get('teff_gspspec_ann')),
        'rv_amplitude_robust': _to_pyfloat(g.get('rv_amplitude_robust')),
        'rv_chisq_pvalue': _to_pyfloat(g.get('rv_chisq_pvalue')),
        'nss_solution_type': str(g.get('nss_solution_type') or ''),
        'in_sb2': 'SB2' in str(g.get('nss_solution_type') or ''),
    }


def parquet_row_to_input(row: pd.Series) -> dict:
    """Translate a parquet row (already has all columns) into derive_row_v2 input."""
    return {
        'a_phot_mas': _to_pyfloat(row.get('a_phot_mas')),
        'parallax': _to_pyfloat(row.get('parallax')),
        'nss_parallax': _to_pyfloat(row.get('nss_parallax')),
        'P_d': _to_pyfloat(row.get('P_d')),
        'eccentricity': _to_pyfloat(row.get('e')),
        'bp_rp': _to_pyfloat(row.get('bp_rp')),
        'logg_gspphot': _to_pyfloat(row.get('logg_gspphot')),
        'logg_gspspec_ann': _to_pyfloat(row.get('logg_gspspec_ann')),
        'logg_gspspec': _to_pyfloat(row.get('logg_gspspec')),
        'teff_gspphot': _to_pyfloat(row.get('teff_gspphot')),
        'teff_gspspec_ann': _to_pyfloat(row.get('teff_gspspec_ann')),
        'rv_amplitude_robust': _to_pyfloat(row.get('rv_amplitude_robust')),
        'rv_chisq_pvalue': _to_pyfloat(row.get('rv_chisq_pvalue')),
        'nss_solution_type': str(row.get('nss_solution_type') or ''),
        'in_sb2': bool(row.get('in_sb2', False)),
    }


def run():
    print(f'Loading test set: {TEST_CSV}')
    test = pd.read_csv(TEST_CSV)
    print(f'  {len(test)} test sources across {test["group"].nunique()} groups')

    print(f'Loading v2 parquet: {PARQUET}')
    df = pd.read_parquet(PARQUET)
    df = df.set_index('source_id', drop=False)
    in_pool = set(df.index.tolist())
    print(f'  {len(df)} rows in pool')

    rows_out = []
    for _, t in test.iterrows():
        sid = int(t['source_id'])
        name = t['name']
        group = t['group']
        M1_lit = _to_pyfloat(t.get('M1_lit'))
        M2_lit = _to_pyfloat(t.get('M2_lit'))
        truth = t['truth_class']
        M1_prior = M1_lit if M1_lit is not None and M1_lit > 0 else 1.0

        rec = {
            'group': group, 'name': name, 'source_id': sid,
            'M1_lit': M1_lit, 'M2_lit': M2_lit,
            'P_d_lit': _to_pyfloat(t.get('P_d_lit')),
            'truth_class': truth,
            'M1_prior_used': M1_prior,
        }

        if sid in in_pool:
            rec['source'] = 'parquet'
            row = df.loc[sid]
            inp = parquet_row_to_input(row)
        else:
            rec['source'] = 'live_gaia'
            print(f'  [LIVE] {group} {name} sid={sid}', flush=True)
            g = query_gaia_one(sid)
            if g is None:
                rec.update({
                    'has_nss': False, 'verdict': 'NO_GAIA_DATA', 'M2_v2': None,
                    'tier': 'No Gaia/NSS row', 'cascade_class': None,
                    'plx_used': None, 'plx_source': None,
                    'filter29_v2': None, 'filter30_v2': None, 'filter31_v2': None, 'filter32_v2': None,
                    'filter30_reason_v2': None, 'logg_used': None, 'logg_source': None,
                    'a_phot_mas': None, 'P_d': None,
                })
                rows_out.append(rec)
                time.sleep(0.5)
                continue
            inp = build_row_from_gaia(g)
            rec['a_phot_mas'] = inp['a_phot_mas']
            rec['has_nss'] = bool(inp['a_phot_mas'] is not None and inp['P_d'] is not None)
            time.sleep(0.5)

        # Try the v2 cascade with literature M1 as prior
        try:
            d = derive_row_v2(inp, M1_prior=M1_prior)
        except Exception as exc:
            d = {'error': f'{type(exc).__name__}: {exc}'}

        if 'error' in d:
            rec['verdict'] = 'NO_CASCADE'
            rec['error'] = d['error']
            rec['has_nss'] = inp.get('P_d') is not None and inp.get('a_phot_mas') is not None
            rec['tier'] = d['error']
            rec['M2_v2'] = None
            rec['cascade_class'] = None
            rec['plx_used'] = None
            rec['plx_source'] = None
            rec['filter29_v2'] = rec['filter30_v2'] = rec['filter31_v2'] = rec['filter32_v2'] = None
            rec['filter30_reason_v2'] = None
            rec['logg_used'] = rec['logg_source'] = None
            rec['P_d'] = inp.get('P_d')
            rec['a_phot_mas'] = inp.get('a_phot_mas')
        else:
            rec['verdict'] = 'OK'
            rec['has_nss'] = True
            rec['tier'] = d['tier_v2']
            rec['M2_v2'] = d['M2_msun_v2']
            rec['cascade_class'] = d['class_v2']
            rec['plx_used'] = d['plx_used']
            rec['plx_source'] = d['plx_source']
            rec['filter29_v2'] = d['filter29_v2']
            rec['filter30_v2'] = d['filter30_v2']
            rec['filter31_v2'] = d['filter31_v2']
            rec['filter32_v2'] = d['filter32_v2']
            rec['filter30_reason_v2'] = d['filter30_reason_v2']
            rec['logg_used'] = d['logg_used']
            rec['logg_source'] = d['logg_source']
            rec['P_d'] = inp.get('P_d')
            rec['a_phot_mas'] = inp.get('a_phot_mas')

        # Agreement column: ✓ verify / ✗ disagree / — N/A
        rec['agreement'] = _agreement(truth, rec.get('tier'), rec.get('cascade_class'), rec.get('M2_v2'))

        rows_out.append(rec)
        print(f'  {group} {name}: tier={rec["tier"]} M2={rec.get("M2_v2")} agree={rec["agreement"]}', flush=True)

    out = pd.DataFrame(rows_out)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)
    print(f'\nWrote {OUT_CSV}')
    return out


def _agreement(truth, tier, cls, m2):
    """Classify the cascade outcome vs truth label."""
    if tier is None or tier in ('No Gaia/NSS row',) or (isinstance(tier, str) and 'missing' in tier):
        # No NSS row = expected for BH3, otherwise N/A
        if truth == 'BH' and tier and ('missing' in tier or 'NSS' in tier):
            return 'N/A (no NSS row — expected)'
        return 'N/A'
    if truth == 'BH':
        return 'verify' if tier == 'Tier-1 BH' else (
            'partial' if (cls in ('dormant_BH_candidate', 'dormant_NS_candidate') or (m2 and m2 >= 1.2))
            else 'disagree'
        )
    if truth == 'NS':
        return 'verify' if tier in ('Tier-1 NS', 'Tier-1 BH', 'Tier-2 (RV inconclusive — needs follow-up)') and (
            cls in ('dormant_NS_candidate', 'dormant_BH_candidate')
        ) else (
            'partial' if (m2 and m2 >= 1.2) else 'disagree'
        )
    if truth in ('K-giant_FP',):
        # Want F#30 to fire
        if tier and 'F#30' in tier:
            return 'verify'
        return 'disagree' if (m2 and m2 >= 1.2 and cls in ('dormant_BH_candidate','dormant_NS_candidate')) else 'partial'
    if truth == 'phantom_FP':
        if tier and 'F#31' in tier:
            return 'verify'
        return 'partial'
    if truth == 'SB2_FP':
        if tier and 'F#29' in tier:
            return 'verify'
        return 'disagree' if (m2 and m2 >= 1.2 and cls in ('dormant_BH_candidate','dormant_NS_candidate')) else 'partial'
    if truth == 'planet':
        if cls in ('planet_candidate', 'BD_candidate'):
            return 'verify'
        if cls == 'M_dwarf_companion' and m2 and m2 < 0.1:
            return 'partial'
        return 'disagree'
    if truth == 'sdB_WD_binary':
        return 'partial'  # short period; cascade may or may not fire as compact
    if truth == 'sdB_NS_WD':
        return 'partial'
    if truth in ('ultra_WD', 'ruled_out', 'unknown'):
        return 'N/A'
    return 'N/A'


if __name__ == '__main__':
    run()
