"""Shared pytest fixtures for the cascade test suite.

The test suite runs entirely offline against tests/data/test_pool.csv,
which is a curated 13-row slice of v9b_scan_full_pool.csv chosen to
exercise every cascade filter path.
"""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl
import pytest

TESTS_DIR = Path(__file__).parent
REPO_ROOT = TESTS_DIR.parent
TEST_POOL_PATH = TESTS_DIR / "data" / "test_pool.csv"

# Make `scripts/` importable for the test modules
sys.path.insert(0, str(REPO_ROOT / "scripts"))


@pytest.fixture(scope="session")
def test_pool() -> pl.DataFrame:
    """Curated 13-row test pool covering all cascade filter paths."""
    return pl.read_csv(TEST_POOL_PATH, schema_overrides={"source_id": pl.Int64})


@pytest.fixture(scope="session")
def known_source_ids():
    """Named source_ids used across many tests."""
    return {
        "HD_185501": 2047188847334279424,   # Sahlmann CONFIRMED_BINARY_FP
        "HD_33636": 3238810137558836352,    # exoplanet.eu match at 9.7" raw / 6.8" PM-corr
        "HD_30246": 3309006602007842048,    # exoplanet.eu match at 1.5" raw
        "BD05_5218": 2744694491118490752,   # exoplanet.eu match
        "HD_222805": 6386542083398391808,   # SIMBAD ** visual double
        "HD_92320": 855523714036230016,     # short-P Kervella substitute
        "HD_5433": 2778298280881817984,     # ruwe=4.06, OrbitalTargetedSearch, was stale-REJECTED
        "HD_89707": 3751763647996317056,    # FLAG → CORROBORATED via Sahlmann promotion
        "HD_76078": 1017645329162554752,    # v1.8.0 headline candidate
        "BD56_1762": 1607476280298633984,   # v1.8.0 headline candidate (Em*)
        "HIP_60865": 1518957932040718464,   # headline candidate (M-dwarf)
        "HIP_20122": 3255968634985106816,   # headline candidate (faint M)
        "HD_140895": 4395581616493055616,   # multi-body inner, HGCA REJECTED stellar
    }
