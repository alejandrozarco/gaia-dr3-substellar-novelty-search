"""Astrometric-microlensing event predictor (lane #118).

Modules:
  geometry  -- pure-physics core (Einstein radius, magnification, centroid
               shift, closest-approach solver, mass inversion). No network.
  predict   -- Gaia DR3 pipeline: high-PM lenses -> background neighbours ->
               ranked predicted-event table. Network (Gaia TAP).
  validate  -- reproduces the published LAWD 37 event (McGill+2023).
  apply_candidates -- cross-checks the project's compact-object candidate list.
"""
