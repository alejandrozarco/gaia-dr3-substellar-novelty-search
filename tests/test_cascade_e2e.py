"""End-to-end cascade tests for the v2 corrected cascade.

Runs derive_row_v2 (scripts/streaming/v2_corrected/consumer_v2.py) over the
bundled offline sample row (scripts/web_tool/sample_data/hd1957_demo.parquet)
and checks the full single-source derivation.

No network access required.

The pre-cleanup v1 e2e tests re-ran pipeline_v9.reclassify_pool_to_v9 on the
v8 verdicts recorded in test_pool.csv. Those v8/v9 cascade stages were deleted
(commit 5fac35c); the tests are pruned. The v2 cascade consumes raw Gaia NSS
columns (Thiele-Innes, nss_parallax, mass_flame, logg_*) rather than v8
verdicts, so the bundled parquet is the right offline fixture for it.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import consumer_v2 as c2

SAMPLE_PARQUET = (
    Path(__file__).resolve().parents[1]
    / "scripts" / "web_tool" / "sample_data" / "hd1957_demo.parquet"
)
HD_1957 = 2543788153077017344


@pytest.fixture(scope="module")
def hd1957_row() -> dict:
    """The bundled HD 1957 offline sample, with a_phot_mas pre-computed from
    its Thiele-Innes coefficients (the form derive_row_v2 consumes)."""
    df = pd.read_parquet(SAMPLE_PARQUET)
    row = df.iloc[0].to_dict()
    row["a_phot_mas"] = c2.photocentric_a_mas(
        row["a_thiele_innes"], row["b_thiele_innes"],
        row["f_thiele_innes"], row["g_thiele_innes"],
    )
    return row


def test_sample_parquet_is_hd1957(hd1957_row):
    assert int(hd1957_row["source_id"]) == HD_1957


def test_derive_row_v2_runs_clean_on_sample(hd1957_row):
    """The full v2 derivation must complete without an error key and return
    all the documented v2 output columns."""
    out = c2.derive_row_v2(hd1957_row)
    assert "error" not in out, out
    for key in ("M1_msun_v2", "M2_msun_v2", "class_v2", "filter29_v2",
                "filter30_v2", "filter31_v2", "filter32_v2", "tier_v2"):
        assert key in out


def test_hd1957_mass_function_in_NS_class(hd1957_row):
    """HD 1957's astrometric mass function alone (M_1=1.5 default) puts M_2
    in the NS-mass band — which is exactly why the K-giant F#30 demotion
    matters: the inflated mass would otherwise look like a Tier-1 NS."""
    out = c2.derive_row_v2(hd1957_row)
    assert out["class_v2"] == "dormant_NS_candidate"
    assert 1.2 <= out["M2_msun_v2"] < 3.0


def test_hd1957_demoted_by_f30_kgiant(hd1957_row):
    """The end-to-end verdict for HD 1957 is an F#30 K-giant demotion:
    logg_gspphot=2.63 < 2.7 (and Teff=4771 K is in the K-giant window)."""
    out = c2.derive_row_v2(hd1957_row)
    assert out["filter30_v2"] == "FAIL"
    assert out["tier_v2"] == "Demoted (failed F#30 K-giant chromatic)"
