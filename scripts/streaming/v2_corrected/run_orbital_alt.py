"""Pull OrbitalAlternative + OrbitalAlternativeValidated rows, apply v2 cascade.

Produces:
    /tmp/orbital_alternative_2026_05_28.md
    /Users/legbatterij/claude_projects/gaia-recovered-2026-05-27/data/derived/main_hunt_derived_v2_alt.parquet
"""
from __future__ import annotations
import math
import sys
import time
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path

import pandas as pd
import polars as pl

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')
DERIVED = ROOT / 'data' / 'derived'
OUTPUT_PARQUET = DERIVED / 'main_hunt_derived_v2_alt.parquet'
REPORT_PATH = Path('/tmp/orbital_alternative_2026_05_28.md')

# Make consumer_v2 importable
sys.path.insert(0, str(ROOT / 'scripts' / 'streaming' / 'v2_corrected'))
from consumer_v2 import derive_row_v2, photocentric_a_mas  # noqa: E402


def _write(report, msg):
    report.write(msg + '\n')
    report.flush()


def main():
    t_start = time.time()
    report = open(REPORT_PATH, 'w')
    _write(report, '# OrbitalAlternative + OrbitalAlternativeValidated ingest')
    _write(report, '')
    _write(report, 'Date: 2026-05-28')
    _write(report, 'Source: `gaiadr3.nss_two_body_orbit` filtered to nss_solution_type IN '
                   "(`OrbitalAlternative`, `OrbitalAlternativeValidated`).")
    _write(report, 'Cascade: v2 corrected (Corrections A/B/C from '
                   '`scripts/streaming/v2_corrected/consumer_v2.py`, M_1 prior = 1.5 M_sun).')
    _write(report, '')

    # ------------------------------------------------------------------
    # Step 1 - pull rows from Gaia
    # ------------------------------------------------------------------
    print('[1/5] Querying Gaia ADQL ...', flush=True)
    from astroquery.gaia import Gaia
    Gaia.MAIN_GAIA_TABLE = 'gaiadr3.gaia_source'
    q = """SELECT n.source_id, n.nss_solution_type, n.period, n.eccentricity,
                  n.significance, n.parallax AS nss_parallax,
                  n.parallax_error AS nss_parallax_error,
                  n.a_thiele_innes, n.b_thiele_innes,
                  n.f_thiele_innes, n.g_thiele_innes,
                  g.ra, g.dec, g.l, g.b,
                  g.parallax, g.parallax_error AS gs_parallax_error,
                  g.phot_g_mean_mag, g.bp_rp,
                  g.ruwe, g.astrometric_excess_noise_sig, g.ipd_frac_multi_peak,
                  g.non_single_star, g.rv_amplitude_robust, g.rv_chisq_pvalue, g.rv_nb_transits,
                  ap.teff_gspphot, ap.logg_gspphot, ap.logg_gspspec, ap.teff_gspspec,
                  ap.mass_flame, ap.radius_flame,
                  aps.teff_gspspec_ann, aps.logg_gspspec_ann
           FROM gaiadr3.nss_two_body_orbit AS n
           JOIN gaiadr3.gaia_source AS g ON g.source_id = n.source_id
           LEFT JOIN gaiadr3.astrophysical_parameters AS ap ON ap.source_id = n.source_id
           LEFT JOIN gaiadr3.astrophysical_parameters_supp AS aps ON aps.source_id = n.source_id
           WHERE n.nss_solution_type IN ('OrbitalAlternative', 'OrbitalAlternativeValidated')
    """
    t0 = time.time()
    job = Gaia.launch_job_async(q, verbose=False)
    df = job.get_results().to_pandas()
    print(f'  {len(df)} rows in {time.time()-t0:.1f}s', flush=True)
    df['source_id'] = df['source_id'].astype('int64')

    # Some sources may legitimately have BOTH OrbitalAlternative and
    # OrbitalAlternativeValidated rows (the validated solution is a
    # re-fit on top of the alternative); the Gaia table stores them as
    # separate rows. We keep both for completeness and dedup later in
    # the parquet by (source_id, nss_solution_type).
    df = df.drop_duplicates(subset=['source_id', 'nss_solution_type']).reset_index(drop=True)
    _write(report, '## Counts')
    _write(report, '')
    _write(report, f'- Total rows pulled: **{len(df)}**')
    by_type = df['nss_solution_type'].value_counts()
    for t, c in by_type.items():
        _write(report, f'- {t}: {c}')
    n_unique_src = df['source_id'].nunique()
    _write(report, f'- Unique source_ids: {n_unique_src}')
    if n_unique_src != len(df):
        _write(report, f'  (Note: {len(df) - n_unique_src} sources have BOTH alternative and validated rows.)')
    _write(report, '')

    # ------------------------------------------------------------------
    # Step 2 - compute a_phot_mas from Thiele-Innes
    # ------------------------------------------------------------------
    print('[2/5] Computing a_phot_mas from Thiele-Innes ...', flush=True)

    def _row_a_phot(r):
        return photocentric_a_mas(
            r['a_thiele_innes'], r['b_thiele_innes'],
            r['f_thiele_innes'], r['g_thiele_innes'],
        )

    df['a_phot_mas'] = df.apply(_row_a_phot, axis=1)

    # ------------------------------------------------------------------
    # Step 3 - check SB2 flag against the same source_ids
    # ------------------------------------------------------------------
    print('[3/5] Checking SB2 flag ...', flush=True)
    src_ids = df['source_id'].astype(int).tolist()
    in_sb2 = set()
    BATCH = 1000
    for i in range(0, len(src_ids), BATCH):
        sub = src_ids[i:i+BATCH]
        ids = ','.join(str(int(x)) for x in sub)
        try:
            sb2 = Gaia.launch_job_async(
                f"SELECT source_id FROM gaiadr3.nss_two_body_orbit "
                f"WHERE source_id IN ({ids}) AND nss_solution_type IN ('SB2','SB2C')",
                verbose=False,
            ).get_results().to_pandas()
            in_sb2.update(int(x) for x in sb2['source_id'])
        except Exception as exc:
            print(f'  SB2 batch err: {exc}', flush=True)
    df['in_sb2'] = df['source_id'].astype(int).isin(in_sb2)
    _write(report, f'- SB2/SB2C cross-match flagged sources: {df["in_sb2"].sum()}')
    _write(report, '')

    # ------------------------------------------------------------------
    # Step 4 - apply v2 cascade
    # ------------------------------------------------------------------
    print('[4/5] Applying v2 cascade ...', flush=True)
    v2_rows = []
    err_count = 0
    for _, r in df.iterrows():
        row_in = {
            'a_phot_mas': r['a_phot_mas'],
            'parallax': r.get('parallax'),
            'nss_parallax': r.get('nss_parallax'),
            'period': r.get('period'),
            'P_d': r.get('period'),
            'eccentricity': r.get('eccentricity'),
            'e': r.get('eccentricity'),
            'bp_rp': r.get('bp_rp'),
            'logg_gspphot': r.get('logg_gspphot'),
            'logg_gspspec_ann': r.get('logg_gspspec_ann'),
            'logg_gspspec': r.get('logg_gspspec'),
            'teff_gspphot': r.get('teff_gspphot'),
            'teff_gspspec_ann': r.get('teff_gspspec_ann'),
            'rv_amplitude_robust': r.get('rv_amplitude_robust'),
            'rv_chisq_pvalue': r.get('rv_chisq_pvalue'),
            'in_sb2': bool(r.get('in_sb2', False)),
            'nss_solution_type': r.get('nss_solution_type'),
        }
        result = derive_row_v2(row_in, M1_prior=1.5)
        if 'error' in result:
            err_count += 1
            result = {k: None for k in [
                'a_phot_mas', 'plx_used', 'plx_source', 'a_phot_AU_v2',
                'P_yr_v2', 'e_v2', 'M1_msun_v2', 'fM_msun_v2', 'M2_msun_v2',
                'class_v2', 'logg_used', 'logg_source', 'cbias_risk_v2',
                'filter29_v2', 'filter30_v2', 'filter30_reason_v2',
                'filter31_v2', 'filter32_v2', 'sini_implied_v2',
                'K_pred_i90_v2', 'tier_v2']}
            result['tier_v2'] = 'ERROR'
        result['source_id'] = int(r['source_id'])
        v2_rows.append(result)
    v2_df = pd.DataFrame(v2_rows)
    print(f'  derive done ({err_count} errors)', flush=True)

    # Merge v2 columns onto the input rows (preserve nss_solution_type col)
    out = df.merge(v2_df.drop(columns=['a_phot_mas']),
                   on='source_id', how='left')
    # Convert pl & write
    out_pl = pl.from_pandas(out)
    out_pl.write_parquet(OUTPUT_PARQUET)
    _write(report, f'- Output parquet: `{OUTPUT_PARQUET.relative_to(ROOT)}` '
                   f'({len(out_pl)} rows, {len(out_pl.columns)} cols)')
    _write(report, f'- Derivation errors (missing plx/period/a_phot): {err_count}')
    _write(report, '')

    # ------------------------------------------------------------------
    # Step 5 - compare to existing v2 + tier summary
    # ------------------------------------------------------------------
    print('[5/5] Tier summary + overlap check ...', flush=True)
    existing = pl.read_parquet(DERIVED / 'main_hunt_derived_v2.parquet')
    existing_ids = set(existing['source_id'].to_list())
    new_ids = set(out_pl['source_id'].to_list())
    overlap = existing_ids & new_ids
    _write(report, '## Overlap with existing v2 catalog')
    _write(report, '')
    _write(report, f'- existing v2 unique sources: {len(existing_ids)}')
    _write(report, f'- new alt unique sources: {len(new_ids)}')
    _write(report, f'- overlap (should be ~0): **{len(overlap)}**')
    _write(report, '')

    _write(report, '## Tier breakdown (tier_v2 value_counts)')
    _write(report, '')
    tier_counts = (out_pl.group_by('tier_v2').len()
                   .sort('len', descending=True))
    _write(report, '| tier_v2 | n |')
    _write(report, '|---|---:|')
    for row in tier_counts.iter_rows(named=True):
        _write(report, f'| {row["tier_v2"]} | {row["len"]} |')
    _write(report, '')

    # Class breakdown
    _write(report, '## class_v2 breakdown')
    _write(report, '')
    cls_counts = (out_pl.group_by('class_v2').len()
                  .sort('len', descending=True))
    _write(report, '| class_v2 | n |')
    _write(report, '|---|---:|')
    for row in cls_counts.iter_rows(named=True):
        _write(report, f'| {row["class_v2"]} | {row["len"]} |')
    _write(report, '')

    # Cross-tab tier_v2 vs nss_solution_type
    _write(report, '## Tier_v2 by nss_solution_type')
    _write(report, '')
    pdf = out.copy()
    ct = pd.crosstab(pdf['tier_v2'].fillna('NULL'), pdf['nss_solution_type'])
    _write(report, '| tier_v2 | ' + ' | '.join(ct.columns.tolist()) + ' |')
    _write(report, '|---|' + '|'.join(['---:'] * len(ct.columns)) + '|')
    for tier, row in ct.iterrows():
        _write(report, f'| {tier} | ' + ' | '.join(str(int(v)) for v in row) + ' |')
    _write(report, '')

    # ------------------------------------------------------------------
    # Top-10 by M_2 in each Tier-1 bucket
    # ------------------------------------------------------------------
    t1_ns = (out_pl.filter(pl.col('tier_v2') == 'Tier-1 NS')
             .sort('M2_msun_v2', descending=True))
    t1_bh = (out_pl.filter(pl.col('tier_v2') == 'Tier-1 BH')
             .sort('M2_msun_v2', descending=True))
    t2 = (out_pl.filter(pl.col('tier_v2').str.starts_with('Tier-2'))
          .sort('M2_msun_v2', descending=True))

    _write(report, f'## Top 10 Tier-1 NS (n={len(t1_ns)})')
    _write(report, '')
    if len(t1_ns) == 0:
        _write(report, '(none)')
    else:
        _write(report, '| source_id | M2 | P_d | e | sini | sig | G | plx | type |')
        _write(report, '|---|---:|---:|---:|---:|---:|---:|---:|---|')
        for r in t1_ns.head(10).iter_rows(named=True):
            sini = r.get('sini_implied_v2')
            sini_s = f'{sini:.3f}' if sini is not None else 'n/a'
            plx = r.get('plx_used')
            plx_s = f'{plx:.3f}' if plx is not None else 'n/a'
            _write(report, f'| {r["source_id"]} | {r["M2_msun_v2"]:.3f} | '
                           f'{r["period"]:.1f} | {r["eccentricity"]:.3f} | '
                           f'{sini_s} | {r["significance"]:.1f} | '
                           f'{r["phot_g_mean_mag"]:.2f} | {plx_s} | '
                           f'{r["nss_solution_type"]} |')
    _write(report, '')

    _write(report, f'## Top 10 Tier-1 BH (n={len(t1_bh)})')
    _write(report, '')
    if len(t1_bh) == 0:
        _write(report, '(none)')
    else:
        _write(report, '| source_id | M2 | P_d | e | sini | sig | G | plx | type |')
        _write(report, '|---|---:|---:|---:|---:|---:|---:|---:|---|')
        for r in t1_bh.head(10).iter_rows(named=True):
            sini = r.get('sini_implied_v2')
            sini_s = f'{sini:.3f}' if sini is not None else 'n/a'
            plx = r.get('plx_used')
            plx_s = f'{plx:.3f}' if plx is not None else 'n/a'
            _write(report, f'| {r["source_id"]} | {r["M2_msun_v2"]:.3f} | '
                           f'{r["period"]:.1f} | {r["eccentricity"]:.3f} | '
                           f'{sini_s} | {r["significance"]:.1f} | '
                           f'{r["phot_g_mean_mag"]:.2f} | {plx_s} | '
                           f'{r["nss_solution_type"]} |')
    _write(report, '')

    # Per-target detail for every Tier-1 (NS + BH combined)
    _write(report, '## Per-target detail - all Tier-1 candidates')
    _write(report, '')
    all_t1 = (out_pl.filter(pl.col('tier_v2').is_in(['Tier-1 NS', 'Tier-1 BH']))
              .sort('M2_msun_v2', descending=True))
    if len(all_t1) == 0:
        _write(report, '(none)')
    else:
        for r in all_t1.iter_rows(named=True):
            sini = r.get('sini_implied_v2')
            sini_s = f'{sini:.3f}' if sini is not None else 'n/a'
            plx = r.get('plx_used')
            plx_s = f'{plx:.3f}' if plx is not None else 'n/a'
            _write(report, f'- **{r["source_id"]}** ({r["tier_v2"]}, '
                           f'{r["nss_solution_type"]}): '
                           f'M_2={r["M2_msun_v2"]:.3f} M_sun, '
                           f'P={r["period"]:.2f} d, e={r["eccentricity"]:.3f}, '
                           f'sini_implied={sini_s}, '
                           f'significance={r["significance"]:.1f}, '
                           f'G={r["phot_g_mean_mag"]:.2f}, '
                           f'plx={plx_s} mas (from {r["plx_source"]}), '
                           f'F#31={r["filter31_v2"]}, F#32={r["filter32_v2"]}')
    _write(report, '')

    # Validated vs Alternative tier strictness
    _write(report, '## Validated vs Alternative comparison')
    _write(report, '')
    for sol_type in ['OrbitalAlternative', 'OrbitalAlternativeValidated']:
        sub = out_pl.filter(pl.col('nss_solution_type') == sol_type)
        n = len(sub)
        if n == 0:
            continue
        n_t1 = sub.filter(pl.col('tier_v2').is_in(['Tier-1 NS', 'Tier-1 BH'])).height
        n_t2 = sub.filter(pl.col('tier_v2').str.starts_with('Tier-2')).height
        n_demo = sub.filter(pl.col('tier_v2').str.starts_with('Demoted')).height
        n_rej = sub.filter(pl.col('tier_v2').str.starts_with('Rejected')).height
        _write(report, f'**{sol_type}** (n={n}):')
        _write(report, f'- Tier-1: {n_t1} ({100*n_t1/n:.1f}%)')
        _write(report, f'- Tier-2: {n_t2} ({100*n_t2/n:.1f}%)')
        _write(report, f'- Demoted: {n_demo} ({100*n_demo/n:.1f}%)')
        _write(report, f'- Rejected (non-compact class): {n_rej} ({100*n_rej/n:.1f}%)')
        _write(report, '')

    _write(report, '## Notes')
    _write(report, '')
    _write(report, '- Cascade math is identical to the published v2 catalog '
                   '(`scripts/streaming/v2_corrected/consumer_v2.py`), M_1 prior = 1.5 M_sun.')
    _write(report, '- a_phot_mas computed from Thiele-Innes coefficients (Halbwachs+ 2023).')
    _write(report, '- plx_source preference order: NSS parallax then gaia_source.parallax.')
    _write(report, '- "OrbitalAlternativeValidated" denotes Gaia DR3 internal QC validation '
                   'of an OrbitalAlternative fit, so Validated rows should tier more '
                   'strictly on average (see the comparison block above).')
    _write(report, '')
    _write(report, f'Runtime: {time.time()-t_start:.1f}s')

    report.close()
    print(f'\nReport written to {REPORT_PATH}', flush=True)
    print(f'Parquet written to {OUTPUT_PARQUET}', flush=True)


if __name__ == '__main__':
    main()
