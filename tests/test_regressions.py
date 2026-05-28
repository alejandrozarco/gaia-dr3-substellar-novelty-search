"""Regression tests for the v2 corrected cascade.

Target: scripts/streaming/v2_corrected/consumer_v2.py.

Each test pins a specific behaviour of the v2 cascade so it cannot silently
regress. The headline regressions are the two reference sources from the
HD 1957 deep-dive / BH2 cross-check, plus a guard on each of the three v2
corrections.

The pre-cleanup v1 regression suite asserted on the v8_verdict / v9b_verdict
columns baked into tests/data/test_pool.csv. Those columns are frozen outputs
of the deleted v1 cascade stages (Filter #28 exoplanet.eu, conditional-RUWE
re-sync, Sahlmann FP, Kervella substitute, SIMBAD visual-double, v11 SB2 by
source-id, the WD-host /tmp manifests). They exercised removed v1 code, not the
v2 cascade, so they are pruned. The SB2 idea survives into v2 as Filter #29 and
is re-tested here against consumer_v2.derive_row_v2.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

import consumer_v2 as c2


# ---------------------------------------------------------------------------
# Reference source 1 — Gaia BH2 (5870569352746779008) → compact-mass verdict
# ---------------------------------------------------------------------------
#
# El-Badry+ 2023 (MNRAS 521): a giant primary (M_1 ~ 0.93 M_sun) with a ~8.9
# M_sun dark companion, P=1276.7 d, e=0.5176, NSS parallax ~0.853 mas. The full
# astrometric data is not bundled offline, so we feed the published orbital
# parameters (with a_phot back-computed from them) through derive_row_v2 — this
# pins the *cascade*, not a live Gaia pull.
BH2_SOURCE_ID = 5870569352746779008


def _bh2_row() -> dict:
    P_d, e, plx_nss, M1, M2 = 1276.7, 0.5176, 0.8528, 0.93, 8.94
    P_yr = P_d / 365.25
    fM = M2 ** 3 / (M1 + M2) ** 2
    a_phot_AU = (fM * P_yr ** 2) ** (1.0 / 3.0)
    a_phot_mas = a_phot_AU * plx_nss
    return {
        "source_id": BH2_SOURCE_ID,
        "a_phot_mas": a_phot_mas,
        "parallax": 0.82,            # biased gaia_source value
        "nss_parallax": plx_nss,     # unbiased orbit-fit value
        "period": P_d,
        "eccentricity": e,
        "mass_flame": M1,            # giant primary FLAME mass
        "bp_rp": 0.9,
        "logg_gspphot": 3.5,         # subgiant — not a K-giant, F#30 should PASS
        "logg_gspspec_ann": None,
        "logg_gspspec": None,
        "teff_gspphot": 5500.0,      # outside the 3700-5200 K-giant window
        "teff_gspspec_ann": None,
        "rv_amplitude_robust": 36.96,
        "rv_chisq_pvalue": 0.0,
        "in_sb2": False,
        "nss_solution_type": "AstroSpectroSB1",
    }


def test_bh2_pinned_to_compact_object_tier1():
    """Gaia BH2 must land in the dormant-BH compact-object class with a
    Tier-1 BH verdict, all four filters passing."""
    out = c2.derive_row_v2(_bh2_row())
    assert "error" not in out, out
    assert out["class_v2"] == "dormant_BH_candidate"
    assert out["M2_msun_v2"] >= 3.0
    assert out["filter29_v2"] == "PASS"
    assert out["filter30_v2"] == "PASS"
    assert out["filter31_v2"] == "PASS"
    assert out["filter32_v2"] == "PASS"
    assert out["tier_v2"] == "Tier-1 BH"


def test_bh2_uses_nss_parallax_not_gaia_source():
    """Correction A regression: with both parallaxes present, BH2 must use
    the NSS parallax. Using the biased gaia_source value would inflate M_2."""
    out = c2.derive_row_v2(_bh2_row())
    assert out["plx_source"] == "NSS"
    assert out["plx_used"] == 0.8528


# ---------------------------------------------------------------------------
# Reference source 2 — HD 1957 (2543788153077017344) → F#30 K-giant demotion
# ---------------------------------------------------------------------------
SAMPLE_PARQUET = (
    Path(__file__).resolve().parents[1]
    / "scripts" / "web_tool" / "sample_data" / "hd1957_demo.parquet"
)
HD_1957 = 2543788153077017344


def _hd1957_row() -> dict:
    df = pd.read_parquet(SAMPLE_PARQUET)
    row = df.iloc[0].to_dict()
    row["a_phot_mas"] = c2.photocentric_a_mas(
        row["a_thiele_innes"], row["b_thiele_innes"],
        row["f_thiele_innes"], row["g_thiele_innes"],
    )
    return row


def test_hd1957_demoted_by_f30_kgiant():
    """HD 1957: M_2 inversion lands in the NS-mass band, but the source is a
    K-giant (logg=2.63 < 2.7, Teff=4771 K) whose photocentric chromatic bias
    inflates M_2. Filter #30 must fire and demote it."""
    row = _hd1957_row()
    assert int(row["source_id"]) == HD_1957
    out = c2.derive_row_v2(row)
    assert out["filter30_v2"] == "FAIL"
    assert out["tier_v2"] == "Demoted (failed F#30 K-giant chromatic)"


# ---------------------------------------------------------------------------
# Correction B regression — rv_amplitude_robust is peak-to-trough (K_obs/2)
# ---------------------------------------------------------------------------

def test_correction_b_k_obs_halved_in_f32():
    """If the /2 conversion regressed (treating rv_amplitude_robust as K_1
    directly), the implied sin i would double. Feed K_obs = 2*K_pred(i=90)
    and require sin i ≈ 1.0 (i.e. the /2 was applied)."""
    P_d, e, M1, M2 = 1276.7, 0.5176, 0.93, 8.94
    K_max = c2.K1_kms(P_d, e, M1, M2, 1.0)
    status, sini, _ = c2.filter32_v2(2.0 * K_max, P_d, e, M1, M2)
    assert status == "PASS"
    assert abs(sini - 1.0) < 1e-6


# ---------------------------------------------------------------------------
# Correction C regression — F#30 logg fallback survives gspphot=NaN
# ---------------------------------------------------------------------------

def test_correction_c_logg_fallback_catches_binary_with_nan_gspphot():
    """gspphot logg is NaN for many binaries; the fallback to logg_gspspec_ann
    is what catches HD 1957-class K-giants. If the fallback regressed, F#30
    would PASS (logg_used=None) and the K-giant would leak through."""
    status, risk, logg_used, logg_source, _ = c2.filter30_v2(
        bp_rp=0.9,
        logg_gspphot=float("nan"),
        logg_gspspec_ann=2.63,
        logg_gspspec=None,
        teff_gspphot=4771.0,
    )
    assert logg_source == "gspspec_ann"
    assert status == "FAIL"
