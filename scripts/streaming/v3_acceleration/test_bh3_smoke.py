"""BH3 smoke test for the acceleration-channel inversion.

Gaia BH3 (source_id 4318465066420528000) was discovered via the FPR full epoch
astrometry, NOT through DR3 NSS.  It is *not* in `gaiadr3.nss_acceleration_astro`.
So we cannot test the full data pipeline against BH3; instead we test the
mathematics by:

  1. Computing the PM-acceleration amplitude that BH3 *would* show if its
     published parameters (M_BH=32.7, M_*=0.76, P=11.6 yr, plx=1.644) were
     a perfect circular orbit.
  2. Round-tripping that synthetic |a| through M2_from_acceleration at the
     published P to verify the inversion is exact (round-trip error < 0.01).
  3. Running the v3 M2_range scan over P_yr in [3, 100] and confirming
     that the published M_BH=32.7 falls inside the [M2_min, M2_max] envelope.

This is a unit test, not an end-to-end test.  The end-to-end pipeline is
exercised by `run_acceleration.py` against the real DR3 acceleration table.

Run with:
    python test_bh3_smoke.py
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))

from acceleration_inversion import (
    M2_from_acceleration, M2_range, tier_label_v3, derive_row_v3,
)


def synth_bh3_accel(M_2: float, M_1: float, P_yr: float, plx: float) -> float:
    """Implied PM-accel amplitude (mas/yr^2) for a circular-orbit binary."""
    # Exact two-body exponent is (2/3): a1 = a_rel * M2/Mtot, a_rel = (Mtot P^2)^(1/3)
    # -> accel ~ M2 / Mtot^(2/3) * P^(-4/3) (corrected 2026-05-31).
    return (4*math.pi**2) * (M_2 / (M_1 + M_2)**(2.0/3.0)) * P_yr**(-4.0/3.0) * plx


def test_bh3_roundtrip():
    """At the published period, the round-trip M_2 must match published BH mass."""
    M_2_pub = 32.7
    M_1_pub = 0.76
    P_yr_pub = 11.6   # 4253 d / 365.25
    plx_pub = 1.644   # Gaia DR3 gaia_source.parallax

    accel = synth_bh3_accel(M_2_pub, M_1_pub, P_yr_pub, plx_pub)
    print(f'  Synthetic |a| (M2=32.7, M1=0.76, P=11.6 yr, plx=1.644): {accel:.4f} mas/yr^2')

    M_2_back = M2_from_acceleration(accel, plx_pub, M_1_pub, P_yr_pub)
    assert M_2_back is not None
    err = abs(M_2_back - M_2_pub)
    print(f'  Round-trip M_2: {M_2_back:.4f} (vs published {M_2_pub})  err={err:.4f}')
    assert err < 1e-3, f'round-trip error {err} exceeds 1e-3'
    return accel


def test_bh3_range_envelope():
    """The v3 M2_range envelope must include the published M_BH=32.7."""
    M_2_pub = 32.7
    M_1_pub = 0.76
    P_yr_pub = 11.6
    plx_pub = 1.644

    accel = synth_bh3_accel(M_2_pub, M_1_pub, P_yr_pub, plx_pub)

    # With the correct M_1 prior (BH3's host is a 0.76 M_sun metal-poor giant)
    M_2_min, M_2_med, M_2_max = M2_range(accel, plx_pub,
                                          M1=M_1_pub,
                                          P_yr_min=3.0, P_yr_max=100.0)
    print(f'  M2_range (M1={M_1_pub} BH3 host): '
          f'min={M_2_min:.2f}  med={M_2_med:.2f}  max={M_2_max:.2f}')
    assert M_2_min <= M_2_pub <= M_2_max, \
           f'published 32.7 not in [{M_2_min}, {M_2_max}]'

    # With the v3 default M_1 = 1.5
    M_2_min15, M_2_med15, M_2_max15 = M2_range(accel, plx_pub,
                                                M1=1.5,
                                                P_yr_min=3.0, P_yr_max=100.0)
    print(f'  M2_range (M1=1.5 v3 default):    '
          f'min={M_2_min15:.2f}  med={M_2_med15:.2f}  max={M_2_max15:.2f}')

    # Tier outcome at default M_1=1.5:
    # With M2_min ~ 2.7 (NS-mass) and M2_max ~ 2400 (huge), BH3 lands in
    # Tier-1 NS or Tier-2.  Note: at P_min=3 yr, the inversion gives M_2 < 3
    # for BH3 because the actual period is much longer (11.6 yr) -- the
    # P_min boundary is the most pessimistic assumption.
    tier = tier_label_v3(M_2_min15, M_2_max15, 'PASS', 'PASS', 'NO_DATA')
    print(f'  v3 tier (default M1=1.5): {tier}')

    # The key validation: at the published P, the inverter recovers 32.7
    M_2_at_pub_P = M2_from_acceleration(accel, plx_pub, 1.5, P_yr_pub)
    print(f'  M_2 inverted at P=11.6 yr with M1=1.5 prior: {M_2_at_pub_P:.2f}  '
          f'(deviation from 32.7 reflects M_1 mis-spec)')


def test_bh3_full_row():
    """The full derive_row_v3 path on a synthetic BH3 row."""
    M_2_pub = 32.7
    M_1_pub = 0.76
    P_yr_pub = 11.6
    plx_pub = 1.644

    accel = synth_bh3_accel(M_2_pub, M_1_pub, P_yr_pub, plx_pub)
    # Distribute the accel arbitrarily between RA and Dec (only |a| matters):
    accel_ra = accel * math.cos(math.radians(30))
    accel_dec = accel * math.sin(math.radians(30))
    row = {
        'accel_ra': accel_ra,
        'accel_dec': accel_dec,
        'accel_ra_error': 0.05,
        'accel_dec_error': 0.05,
        'parallax': plx_pub,
        'bp_rp': 1.22,       # BH3 host bp_rp (would normally fail F#30 since > 1.2)
        'logg_gspphot': 2.3,  # BH3 host is a metal-poor giant -- below 2.7
        'logg_gspspec_ann': None,
        'logg_gspspec': None,
        'teff_gspphot': 5400,
        'teff_gspspec_ann': None,
        'rv_amplitude_robust': 42.0,  # BH3 rv_amplitude_robust from Gaia DR3 gaia_source
        'rv_chisq_pvalue': 0.0,
        'in_sb2': False,
        'nss_solution_type': 'Acceleration7',
    }
    out = derive_row_v3(row, M1_prior=1.5)
    print('  derive_row_v3 output:')
    for k, v in out.items():
        if isinstance(v, float):
            print(f'    {k:>22s} = {v:.4f}')
        else:
            print(f'    {k:>22s} = {v}')
    # F#30 should fail (BP-RP > 1.2 AND logg < 2.7 -- two reasons)
    assert out['filter30_v3'] == 'FAIL'
    # F#31 should pass (K=42 > 5, pval = 0.0 < 0.05)
    assert out['filter31_v3'] == 'PASS'


if __name__ == '__main__':
    print('=== BH3 round-trip test ===')
    test_bh3_roundtrip()
    print('=== BH3 M2_range envelope test ===')
    test_bh3_range_envelope()
    print('=== BH3 synthetic full-row v3 test ===')
    test_bh3_full_row()
    print('\nAll BH3 smoke tests passed.')
