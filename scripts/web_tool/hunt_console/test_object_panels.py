"""Offline tests for object_panels' pure helpers (no Streamlit runtime, no network).

    PYTHONPATH=scripts/web_tool/hunt_console:scripts python scripts/web_tool/hunt_console/test_object_panels.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import object_panels as op  # noqa: E402

N_PASS = N_FAIL = 0


def check(label, cond, extra=""):
    global N_PASS, N_FAIL
    if cond:
        N_PASS += 1; print(f"[PASS] {label}")
    else:
        N_FAIL += 1; print(f"[FAIL] {label} {extra}")


findings = {
    "gaia_dr3_source_id": "6048007439673413760",
    "ra": 250.55517, "dec": -23.220485,
    "classification": "KNOWN SU UMa dwarf nova",
    "names": {"asassn": "ASASSN-14gb", "vsx": "ASASSN-14gb"},
    "known_in_catalogs": ["AAVSO VSX (UGSU)"],
    "evidence": {"distance_pc": 392, "ruwe": 1.175, "orbital_period_d": 0.066,
                 "orbital_period_min": 95, "bp_rp_mean": 0.814, "M_G_quiescent": 9.47},
}
crow = {"id": "6048007439673413760", "ra": 250.55517, "dec": -23.220485,
        "score": 0.0, "bp_rp": 0.81}

# pluck: top-level, evidence, crow, and contains-mode
check("pluck finds a top-level findings field", op.pluck(findings, crow, "classification") == "KNOWN SU UMa dwarf nova")
check("pluck reaches into the evidence dict", op.pluck(findings, crow, "distance_pc") == 392)
check("pluck falls back to the candidate row", op.pluck(None, crow, "score") == 0.0)
check("pluck contains-mode matches a substring key", op.pluck(findings, crow, "period", contains=True) is not None)
check("pluck returns None when nothing matches", op.pluck(findings, crow, "nonexistent_key") is None)

# _num
check("_num parses a float", op._num("3.14") == 3.14)
check("_num returns None on garbage", op._num("not a number") is None)
check("_num returns None on NaN", op._num(float("nan")) is None)

# coords + source id
check("_coords reads ra/dec", op._coords(findings, crow) == (250.55517, -23.220485))
check("source_id_of prefers the explicit id", op.source_id_of("x", findings, crow) == "6048007439673413760")
check("source_id_of falls back to tid", op.source_id_of("TID123", None, None) == "TID123")

# external links
links = op.external_links("6048007439673413760", 250.55517, -23.22)
check("external_links includes SIMBAD", "simbad" in links.lower())
check("external_links includes Aladin", "aladin" in links.lower())
check("external_links empty-safe without coords", isinstance(op.external_links("x", None, None), str))

# plot-kind classification
check("_kind: phase fold", op._kind("ztf_phasefold_123.png") == "Phase fold")
check("_kind: light curve", op._kind("lightcurve_gaia.png") == "Light curve")
check("_kind: SED", op._kind("sed_123.png") == "SED")
check("_kind: spectrum", op._kind("spectrum_sdss_vs_desi.png") == "Spectrum")
check("_kind: finder", op._kind("finder_123.png") == "Finder")

# period resolution (days, or minutes/1440)
check("_period_days reads orbital_period_d", abs(op._period_days(findings, crow) - 0.066) < 1e-9)
check("_period_days converts minutes when only minutes present",
      abs(op._period_days({"evidence": {"orbital_period_min": 95}}, None) - 95/1440.0) < 1e-9)
check("_period_days None when no period", op._period_days({"evidence": {}}, None) is None)

print(f"\n{'='*48}\n{N_PASS} passed, {N_FAIL} failed\n{'='*48}")
sys.exit(1 if N_FAIL else 0)
