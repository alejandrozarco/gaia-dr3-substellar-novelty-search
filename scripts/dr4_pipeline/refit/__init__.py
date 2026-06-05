"""DR4 candidate re-fit engine (lane #116).

Re-fit each standing dormant-compact / substellar candidate's astrometric orbit
from the DR4 per-transit (epoch) astrometry and decide single-body vs multi-body
against the pre-registered thresholds in docs/dr4_preregistration_2026_06_01.md.

Modules:
  model.py       — astrometric orbit forward model + 1-body / accel / 2-body fitters.
  modelselect.py — 1-body vs multi-body via BIC/ΔBIC, F-test, reduced-χ²/F2.
  prereg.py      — per-candidate confirm/refute thresholds + decision wiring.
  synth.py       — synthetic DR4-like epoch-data generator (Gaia scanning model).
  adapter.py     — the DR4 column-mapping seam (only place DR4 names enter).
  run.py         — day-one driver (epoch table -> per-candidate verdict).
  test_refit.py  — end-to-end synthetic tests.

DR4 is not out (2 Dec 2026); everything is exercised on synthetic data until then.
"""
