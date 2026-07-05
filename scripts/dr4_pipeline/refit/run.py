"""Day-one DR4 driver for the candidate re-fit engine.

Ties the pieces together for the actual DR4 drop (2 Dec 2026): given a DR4
epoch-astrometry table for one candidate (already pulled to /tmp by the Step-1
TAP query in the pre-registration doc), it
  1. maps the DR4 columns -> canonical EpochData (adapter.epoch_table_to_epochdata),
  2. fits 1-body / +accel / 2-body and model-selects (modelselect.select_model),
  3. applies the candidate's pre-registered confirm/refute thresholds
     (prereg.decide), and
  4. prints the DR3-prediction-vs-DR4-measurement-vs-threshold verdict and emits
     a machine-readable dict (for /tmp/dr4_reanalysis_<name>.md hand-off — the
     main thread integrates into CANDIDATES.md / dossiers; this engine does not).

This module performs NO archive I/O itself (agents work foreground, write to
/tmp, do not edit docs/).  It either reads a local epoch table you pass on the
command line, or — with --demo — runs on a freshly synthesised DR4-like table so
the end-to-end path is exercised today, before DR4 exists.

Usage:
  # Today (synthetic), all four candidates, "headline-true" world:
  python run.py --demo

  # On DR4 day, a real epoch table (parquet/csv/fits) for one candidate:
  python run.py --source-id 332248057157474176 \
                --epoch-table /tmp/dr4_wdj020915_epochs_2026_12_02.parquet \
                [--parallax 11.94] [--m1 0.718] [--psi-unit rad]

stdlib + numpy + scipy + (pandas/astropy only if reading those file formats).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adapter import epoch_table_to_epochdata
from modelselect import select_model, summarize
from prereg import PREREG, decide
import synth
from synth import make_epoch_data


def _self_validate_gate(verbose=True):
    """Run the labeled-FP self-validation guards; return 0 (pass) / 1 (fail).

    Wired to `--self-validate` and run automatically before the real day-one
    analysis (unless --skip-self-validate). The engine must reproduce every
    documented astrometric false positive with the correct skeptical verdict
    before any NEW verdict is trusted (lane #116 insurance)."""
    import fp_registry
    from test_fp_selfvalidation import run_self_validation
    print(fp_registry.summary())
    print('\nDR4 day-one self-validation against the labeled-FP registry:')
    ok, failures = run_self_validation(verbose=verbose)
    if ok:
        print('\nSELF-VALIDATION PASSED — the engine reproduces every documented '
              'astrometric FP with the correct skeptical verdict.')
        return 0
    print('\n*** SELF-VALIDATION FAILED — DO NOT TRUST NEW VERDICTS ***')
    for f in failures:
        print('  [FAIL] ' + f)
    return 1


def _load_table(path):
    """Load an epoch table from parquet / csv / fits into a dict-of-arrays."""
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.parquet', '.pq'):
        import pandas as pd
        return pd.read_parquet(path)
    if ext in ('.csv', '.tsv'):
        import pandas as pd
        return pd.read_csv(path, sep='\t' if ext == '.tsv' else ',')
    if ext in ('.fits', '.fit'):
        from astropy.table import Table
        return Table.read(path)
    raise ValueError(f'unsupported epoch-table format: {ext}')


def analyze_candidate(source_id, ep, parallax=None, m1=None, P0=None):
    """Run the engine on one EpochData; return (Decision, SelectionResult)."""
    pr = PREREG[source_id]
    if P0 is None:
        P0 = pr.P_dr3
    P2_guess = max(3.0 * P0, 0.8 * float(ep.t.max() - ep.t.min()))
    sel = select_model(ep, P0=P0, e0=pr.e_dr3, P2_guess=P2_guess)
    dec = decide(source_id, sel, parallax_mas=parallax, M1=m1)
    return dec, sel


def _report(source_id, dec, sel):
    pr = PREREG[source_id]
    print('=' * 78)
    print(f'CANDIDATE  {pr.name}  (Gaia DR3 {source_id})')
    print(f'  headline : {pr.headline}')
    print(f'  DR3 anchor: a_phot={pr.a_phot_dr3} mas, '
          f'i={pr.incl_dr3}°, F2={pr.f2_dr3}, P={pr.P_dr3} d')
    print('-' * 78)
    print(summarize(sel))
    print('-' * 78)
    print(f'PRE-REGISTERED VERDICT: {dec.verdict}')
    print(f'  {dec.detail}')
    if dec.followup:
        print(f'  follow-up: {dec.followup}')
    print('=' * 78)


def main(argv=None):
    ap = argparse.ArgumentParser(description='DR4 candidate re-fit engine (day-one driver).')
    ap.add_argument('--source-id', help='19-digit Gaia DR3 source_id (one of the 4 candidates).')
    ap.add_argument('--epoch-table', help='Path to the DR4 epoch-astrometry table (parquet/csv/fits).')
    ap.add_argument('--parallax', type=float, default=None,
                    help='DR4 refined parallax (mas); defaults to the DR3 anchor.')
    ap.add_argument('--m1', type=float, default=None,
                    help='DR4-refined primary mass (M_sun); defaults to the pre-registered M1.')
    ap.add_argument('--psi-unit', default='rad', choices=['rad', 'deg'],
                    help="Scan-angle unit in the DR4 table (default rad).")
    ap.add_argument('--column-map', default=None,
                    help='Optional JSON file mapping DR4 column names -> EpochData fields.')
    ap.add_argument('--demo', action='store_true',
                    help='Run on synthetic DR4-like data for all 4 candidates (today).')
    ap.add_argument('--self-validate', action='store_true',
                    help='Run the labeled-FP self-validation gate (fp_registry) and exit. '
                         'Asserts the engine reproduces every documented astrometric false '
                         'positive with the correct skeptical verdict.')
    ap.add_argument('--skip-self-validate', action='store_true',
                    help='Skip the automatic self-validation gate on the real day-one path '
                         '(NOT recommended — the gate is day-one insurance).')
    ap.add_argument('--json-out', default=None, help='Write the verdict dict(s) to this JSON path.')
    args = ap.parse_args(argv)

    # --- Labeled-FP self-validation gate ---------------------------------
    # Before trusting any NEW verdict, the engine must reproduce every
    # documented astrometric false positive with the correct skeptical verdict.
    if args.self_validate:
        return _self_validate_gate()

    results = {}

    if args.demo:
        print('# DEMO MODE — synthetic DR4-like epoch data, "headline-true" world.\n')
        for sid, truth in synth.CANDIDATE_TRUTH.items():
            t = dict(truth)
            # For WDJ020915 use a_phot=8.0 so the knife-edge M2 clears the floor
            # in the headline-true world (see test_refit docstring).
            if sid == '332248057157474176':
                t['a_phot_mas'] = 8.0
            ep = make_epoch_data(pmra=10.0, pmdec=-12.0, omega_deg=45.0,
                                 Omega_deg=120.0, n_transits=90, seed=7, **t)
            dec, sel = analyze_candidate(sid, ep, parallax=t['parallax_mas'])
            _report(sid, dec, sel)
            results[sid] = _verdict_dict(sid, dec, sel)
    else:
        if not args.source_id or not args.epoch_table:
            ap.error('provide --source-id and --epoch-table (or use --demo).')
        sid = args.source_id
        if sid not in PREREG:
            ap.error(f'{sid} is not one of the 4 pre-registered candidates: {list(PREREG)}')
        # Day-one insurance: reproduce every documented FP before trusting a new verdict.
        if not args.skip_self_validate:
            print('# Running labeled-FP self-validation gate before the real analysis...\n')
            if _self_validate_gate(verbose=False) != 0:
                print('\nABORTING: self-validation failed — fix the regression before '
                      'trusting any DR4 verdict (or pass --skip-self-validate to override).')
                return 1
            print()
        column_map = None
        if args.column_map:
            with open(args.column_map) as fh:
                column_map = json.load(fh)
        table = _load_table(args.epoch_table)
        ep = epoch_table_to_epochdata(table, column_map=column_map, psi_unit=args.psi_unit)
        dec, sel = analyze_candidate(sid, ep, parallax=args.parallax, m1=args.m1)
        _report(sid, dec, sel)
        results[sid] = _verdict_dict(sid, dec, sel)

    if args.json_out:
        with open(args.json_out, 'w') as fh:
            json.dump(results, fh, indent=2, default=float)
        print(f'\nwrote {args.json_out}')
    return 0


def _verdict_dict(sid, dec, sel):
    one = sel.one_body
    return dict(
        source_id=sid, name=dec.name, verdict=dec.verdict, detail=dec.detail,
        model_verdict=dec.model_verdict, followup=dec.followup,
        f2_single=sel.f2_single, chi2_red_single=one.chi2_red,
        a_phot_fit=dec.a_phot_fit, incl_fit=dec.incl_fit, P_fit=one.P, e_fit=one.e,
        M2_fit=dec.M2_fit,
        dbic_accel=sel.dbic_accel, dbic_two=sel.dbic_two, accel_snr=sel.accel_snr,
        checks=dec.checks,
    )


if __name__ == '__main__':
    sys.exit(main())
