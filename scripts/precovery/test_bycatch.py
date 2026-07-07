"""pytest suite for the bycatch harvester, driven by REAL campaign artifacts.

    /Users/legbatterij/claude_projects/ostinato/.venv/bin/python -m pytest \
        scripts/precovery/test_bycatch.py -v

POSITIVE control: the 6 (330836) Orius detections from the 2009 HW77 verify set.
  The 2013-03-02 and 2015-04-27 same-night pairs must emerge as tracklets with the
  rates computed here from the positions, and the MPC step must resolve both to
  (330836)/2009 HW77 (that assert is skipped-if-offline but RUN live).
NEGATIVE control: stationary NSC detections from the 2001 QT322 verify set (fixed
  stars incl. the spurious short-baseline pair) -> ZERO tracklets survive.
Plus unit tests for the rate window, direction consistency, and static-table rejection.

Read-only w.r.t. docs/: the artifacts are only read, never written.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import pytest

import bycatch as bc

# --------------------------------------------------------------------------- #
# Artifact paths (read-only)
# --------------------------------------------------------------------------- #
REPO = Path(__file__).resolve().parents[2]
CAMP = REPO / "docs/reports/precovery_campaign_2026_07_07/verify"
HW77_CSV = CAMP / "2009_HW77/updated_astrometry.csv"
QT322_JSON = CAMP / "2001_QT322/nsc_real_results.json"

SCRATCH = Path("/tmp/novelty_gate/bycatch")
SCRATCH.mkdir(parents=True, exist_ok=True)


def _online() -> bool:
    if not bc._HAVE_REQUESTS:
        return False
    if os.environ.get("BYCATCH_OFFLINE"):
        return False
    try:
        import requests
        requests.head("https://cgi.minorplanetcenter.net/cgi-bin/mpcheck.cgi", timeout=15)
        return True
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# Fixtures built from the real artifacts
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def hw77_detections():
    """The 6 Orius detections. updated_astrometry.csv column aliases resolve to
    mjd/ra/dec/mag/filter/exposure/obscode automatically."""
    dets = bc.load_detections(HW77_CSV)
    assert len(dets) == 6
    return dets


@pytest.fixture(scope="module")
def qt322_detections():
    """Flatten every in-3sigma stationary detection (the `inb` arrays) into a
    single-exposure detection list, keyed by measid with objectid as group_id."""
    data = json.loads(QT322_JSON.read_text())
    dets = []
    for night in data.values():
        for d in night.get("inb", []):
            dets.append({
                "mjd": d["mjd"], "ra": d["ra"], "dec": d["dec"],
                "mag": d["mag"], "filter": d.get("filter"),
                "id": d["measid"], "group_id": d["objectid"],
                "exposure": d.get("exposure"), "obscode": "W84",
            })
    return bc.load_detections(dets)


# --------------------------------------------------------------------------- #
# Expected rates, computed independently from the positions
# --------------------------------------------------------------------------- #
def _expected_rate(ra1, dec1, mjd1, ra2, dec2, mjd2):
    sep = bc.sep_arcsec(ra1, dec1, ra2, dec2)
    dt_hr = abs(mjd2 - mjd1) * 24.0
    return sep / dt_hr


# 2013-03-02 pair (rows tu2037227 / tu2037424), filter r
EXP_2013 = _expected_rate(246.129500, -26.251832, 56353.32383,
                          246.129491, -26.251832, 56353.32533)
# 2015-04-27 pair (c4d_150427_053222 / _053734), filter VR
EXP_2015 = _expected_rate(260.306990, -32.379144, 57139.22940,
                          260.306891, -32.379149, 57139.23297)


def test_expected_rates_in_window():
    """Sanity: the hand-computed rates are what a wave should see (~0.8 and ~3.5"/hr)."""
    assert 0.5 < EXP_2013 < 1.5, EXP_2013
    assert 3.0 < EXP_2015 < 4.0, EXP_2015


# --------------------------------------------------------------------------- #
# POSITIVE control
# --------------------------------------------------------------------------- #
def test_positive_pairs_emerge(hw77_detections):
    """The two same-night pairs surface as tracklets; the 2-day-apart 2014
    detections do NOT pair (isolated per night)."""
    tracklets, reject = bc.form_tracklets(hw77_detections, bc.BycatchConfig())
    assert len(tracklets) == 2, [t["member_exposures"] for t in tracklets]

    by_night = sorted(tracklets, key=lambda t: t["mjd_start"])
    t2013, t2015 = by_night[0], by_night[1]

    # rates match the independent hand computation
    assert t2013["rate_arcsec_hr"] == pytest.approx(EXP_2013, rel=1e-6)
    assert t2015["rate_arcsec_hr"] == pytest.approx(EXP_2015, rel=1e-6)
    # both inside the default window
    cfg = bc.BycatchConfig()
    for t in (t2013, t2015):
        assert cfg.rate_min_arcsec_hr <= t["rate_arcsec_hr"] <= cfg.rate_max_arcsec_hr
        assert t["n_points"] == 2

    # they are the right exposures
    assert "tu2037227" in t2013["member_exposures"] and "tu2037424" in t2013["member_exposures"]
    assert "c4d_150427_053222" in t2015["member_exposures"]
    assert "c4d_150427_053734" in t2015["member_exposures"]


def test_positive_2014_singletons_do_not_pair(hw77_detections):
    """The 2014-06-27 and 2014-06-29 detections are 2 days apart -> not same-night."""
    tracklets, _ = bc.form_tracklets(hw77_detections, bc.BycatchConfig())
    for t in tracklets:
        assert "c4d_140627_015128" not in t["member_exposures"]
        assert "c4d_140629_021153" not in t["member_exposures"]


@pytest.mark.skipif(not _online(), reason="MPC MPChecker unreachable / offline")
def test_positive_mpc_identifies_orius(hw77_detections):
    """LIVE MPC identification: both same-night tracklets resolve to (330836)/2009 HW77.

    Network-dependent; skipped if offline but RUN when the CGI is reachable.
    """
    cfg = bc.BycatchConfig()
    summary = bc.run_bycatch(hw77_detections, identify=True, cfg=cfg,
                             out_csv=str(SCRATCH / "positive_bycatch_tracklets.csv"))
    assert summary["n_tracklets"] == 2
    assert summary["n_known"] == 2, summary
    for t in summary["tracklets"]:
        d = t["mpc_designation"]
        assert ("Orius" in d) or ("330836" in d) or ("2009 HW77" in d), t
        assert t["mpc_sep_arcsec"] <= cfg.mpc_match_arcsec


# --------------------------------------------------------------------------- #
# NEGATIVE control
# --------------------------------------------------------------------------- #
def test_negative_zero_tracklets_with_static_catalog(qt322_detections):
    """Every QT322 in-3sigma detection is a catalogued stationary star. Supplying the
    NSC mean-object catalog (grouped by objectid) rejects all pairs -> ZERO tracklets.
    This is the decisive false-positive filter; the spurious short-baseline pair dies
    with the rest."""
    static = bc.mean_object_catalog(qt322_detections, group_key="group_id")
    assert len(static) >= 1
    tracklets, reject = bc.form_tracklets(qt322_detections, bc.BycatchConfig(), static)
    assert len(tracklets) == 0, [t["member_ids"] for t in tracklets]
    assert reject["on_static_source"] > 0


def test_negative_static_catalog_is_the_decisive_filter(qt322_detections):
    """Honest demonstration that the static catalog — not the rate floor — is what
    kills the QT322 artifacts (matches the campaign REPORT: 'stationary-source
    rejection is decisive').

    ~0.1" of catalog scatter on the SAME star (objectid 87313_1208) over ~1.5 min
    reads as a few "/hr, so several same-star 'pairs' pass the 0.5"/hr floor and would
    be spurious tracklets. Supplying the mean-object catalog (the star's mean position)
    rejects every one -> the net stays silent only because of the static filter."""
    same_star = [d for d in qt322_detections if d["group_id"] == "87313_1208"]
    assert len(same_star) >= 3
    # WITHOUT the catalog: measurement scatter fabricates in-window tracklets
    tr_nocat, _ = bc.form_tracklets(same_star, bc.BycatchConfig())
    assert len(tr_nocat) > 0, "expected the scatter-induced spurious pairs"
    assert all(bc.BycatchConfig().rate_min_arcsec_hr <= t["rate_arcsec_hr"]
               <= bc.BycatchConfig().rate_max_arcsec_hr for t in tr_nocat)
    # WITH the mean-object catalog: all rejected as sitting on a fixed star
    static = bc.mean_object_catalog(same_star, group_key="group_id")
    tr_cat, reject = bc.form_tracklets(same_star, bc.BycatchConfig(), static)
    assert len(tr_cat) == 0
    assert reject["on_static_source"] >= len(tr_nocat)


def test_negative_full_field_spurious_without_catalog(qt322_detections):
    """The whole QT322 field yields several spurious tracklets with NO static catalog;
    supplying it drives the count to zero. This is the false-positive load the static
    filter carries."""
    tr_nocat, _ = bc.form_tracklets(qt322_detections, bc.BycatchConfig())
    assert len(tr_nocat) > 0
    static = bc.mean_object_catalog(qt322_detections, group_key="group_id")
    tr_cat, _ = bc.form_tracklets(qt322_detections, bc.BycatchConfig(), static)
    assert len(tr_cat) == 0


@pytest.mark.skipif(not _online(), reason="MPC MPChecker unreachable / offline")
def test_negative_full_pipeline_no_candidates(qt322_detections):
    """End-to-end on the negative control: 0 tracklets => 0 known and 0 unknown
    candidates. The novelty net stays silent on a valid null field."""
    static = bc.mean_object_catalog(qt322_detections, group_key="group_id")
    summary = bc.run_bycatch(qt322_detections, static_sources=static, identify=True,
                             out_csv=str(SCRATCH / "negative_bycatch_tracklets.csv"))
    assert summary["n_tracklets"] == 0
    assert summary["n_unknown_candidate"] == 0
    assert summary["n_known"] == 0


# --------------------------------------------------------------------------- #
# Unit tests: rate window, direction consistency, static-table rejection
# --------------------------------------------------------------------------- #
def _det(id_, mjd, ra, dec, mag=20.0, filt="r", group=None):
    return {"mjd": mjd, "ra": ra, "dec": dec, "mag": mag, "filter": filt,
            "id": id_, "group_id": group, "exposure": id_, "obscode": "500"}


def test_rate_window_rejects_below_min():
    """A pair moving 0.3"/hr (below the 0.5 floor) is rejected as stationary."""
    # 0.3" over 1 hr
    d1 = _det("a", 50000.0, 10.0, 0.0)
    d2 = _det("b", 50000.0 + 1 / 24.0, 10.0 + 0.3 / 3600.0, 0.0)
    tr, rj = bc.form_tracklets([d1, d2], bc.BycatchConfig())
    assert tr == [] and rj["stationary_rate"] == 1


def test_rate_window_rejects_above_max():
    """A pair moving 200"/hr (above the 120 ceiling) is rejected as too-fast."""
    d1 = _det("a", 50000.0, 10.0, 0.0)
    d2 = _det("b", 50000.0 + 1 / 24.0, 10.0 + 200.0 / 3600.0, 0.0)
    tr, rj = bc.form_tracklets([d1, d2], bc.BycatchConfig())
    assert tr == [] and rj["too_fast"] == 1


def test_rate_window_accepts_in_band():
    """A 10"/hr pair survives."""
    d1 = _det("a", 50000.0, 10.0, 0.0)
    d2 = _det("b", 50000.0 + 1 / 24.0, 10.0 + 10.0 / 3600.0, 0.0)
    tr, _ = bc.form_tracklets([d1, d2], bc.BycatchConfig())
    assert len(tr) == 1 and tr[0]["rate_arcsec_hr"] == pytest.approx(10.0, rel=1e-3)


def test_triplet_direction_consistent():
    """Three points on a straight, constant-rate track -> one triplet."""
    t0 = 50000.0
    dets = [
        _det("p1", t0, 10.0, 0.0),
        _det("p2", t0 + 0.5 / 24.0, 10.0 + 5.0 / 3600.0, 0.0),
        _det("p3", t0 + 1.0 / 24.0, 10.0 + 10.0 / 3600.0, 0.0),
    ]
    tr, _ = bc.form_tracklets(dets, bc.BycatchConfig())
    trip = [t for t in tr if t["kind"] == "triplet"]
    assert len(trip) == 1
    assert trip[0]["n_points"] == 3


def test_triplet_has_no_redundant_endpoint_pair():
    """A 3-point mover yields exactly ONE tracklet (the triplet) — the
    un-consumed long-baseline endpoint pair (p1,p3) must be deduplicated
    as a subset of the triplet (referee-found defect, fixed)."""
    t0 = 50000.0
    dets = [
        _det("p1", t0, 10.0, 0.0),
        _det("p2", t0 + 0.5 / 24.0, 10.0 + 5.0 / 3600.0, 0.0),
        _det("p3", t0 + 1.0 / 24.0, 10.0 + 10.0 / 3600.0, 0.0),
    ]
    tr, _ = bc.form_tracklets(dets, bc.BycatchConfig())
    assert len(tr) == 1, f"expected 1 deduped tracklet, got {len(tr)}: {tr}"
    assert tr[0]["kind"] == "triplet" and tr[0]["n_points"] == 3


def test_two_independent_movers_not_deduped():
    """Dedup must not merge two DISTINCT movers (disjoint member sets)."""
    t0 = 50000.0
    dets = [
        _det("a1", t0, 10.0, 0.0),
        _det("a2", t0 + 1 / 24.0, 10.0 + 10.0 / 3600.0, 0.0),
        _det("b1", t0, 11.0, 1.0),
        _det("b2", t0 + 1 / 24.0, 11.0 + 10.0 / 3600.0, 1.0),
    ]
    tr, _ = bc.form_tracklets(dets, bc.BycatchConfig())
    assert len(tr) == 2 and all(t["kind"] == "pair" for t in tr)


def test_triplet_direction_inconsistent_no_triplet():
    """A dog-legged third point (90 deg off) does not form a triplet."""
    t0 = 50000.0
    dets = [
        _det("p1", t0, 10.0, 0.0),
        _det("p2", t0 + 0.5 / 24.0, 10.0 + 5.0 / 3600.0, 0.0),
        _det("p3", t0 + 1.0 / 24.0, 10.0 + 5.0 / 3600.0, 5.0 / 3600.0),  # turns north
    ]
    tr, _ = bc.form_tracklets(dets, bc.BycatchConfig())
    assert all(t["kind"] != "triplet" for t in tr)


def test_static_table_rejects_endpoint_on_fixed_star():
    """A perfectly good-rate pair is killed when an endpoint sits on a static source."""
    d1 = _det("a", 50000.0, 10.0, 0.0)
    d2 = _det("b", 50000.0 + 1 / 24.0, 10.0 + 10.0 / 3600.0, 0.0)
    static = [{"ra": 10.0, "dec": 0.0, "id": "star", "ndet": 9}]  # on top of d1
    tr, rj = bc.form_tracklets([d1, d2], bc.BycatchConfig(), static)
    assert tr == [] and rj["on_static_source"] == 1
    # and it survives again when the static source is >1.5" away
    static_far = [{"ra": 10.0 + 5.0 / 3600.0, "dec": 0.0, "id": "star", "ndet": 9}]
    tr2, _ = bc.form_tracklets([d1, d2], bc.BycatchConfig(), static_far)
    assert len(tr2) == 1


def test_magnitude_inconsistency_rejects():
    """Endpoints differing by >1 mag (same filter) are rejected."""
    d1 = _det("a", 50000.0, 10.0, 0.0, mag=20.0)
    d2 = _det("b", 50000.0 + 1 / 24.0, 10.0 + 10.0 / 3600.0, 0.0, mag=22.0)
    tr, rj = bc.form_tracklets([d1, d2], bc.BycatchConfig())
    assert tr == [] and rj["mag_inconsistent"] == 1


def test_mjd_to_ymd_matches_astropy():
    """The stdlib MJD->calendar fallback agrees with the value used for MPC queries."""
    y, mo, d = bc._mjd_to_ymd(56353.32383)
    assert (y, mo) == (2013, 3)
    assert d == pytest.approx(2.32383, abs=1e-4)
