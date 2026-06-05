"""DR4 column-mapping seam (the ingestion adapter).

DR4 is not out (2 Dec 2026); the exact epoch-astrometry table + column names
are not final.  ALL assumptions about DR4 column names live HERE, in one thin
adapter, so that when the real schema is published only this file changes — the
fitter (model.py), the selector (modelselect.py), and the decision logic
(prereg.py) consume the canonical internal `EpochData` and never see a DR4
column name.

ASSUMED DR4 PRODUCT (shared with the rehunt sibling pipeline, lane #117):
  (a) an epoch-astrometry table keyed by source_id with, per transit, roughly:
        - an observation time          (TCB days or Barycentric JD)
        - the along-scan abscissa      (the AL measurement, mas or the residual
                                         w.r.t. a reference; we treat it as the
                                         modelled AL coordinate)
        - the scan angle psi           (radians or degrees)
        - the AL parallax factor       (dimensionless)
        - the per-transit AL sigma     (mas)
  (b) an expanded nss_two_body_orbit with the re-derived Thiele-Innes A,B,F,G,
      P, e, T0, parallax, significance, goodness_of_fit (F2), inclination,
      and the 12x12 correlation vector.

DEFAULT_EPOCH_MAP below is a best-guess mapping using DR3-style naming
conventions extended to the expected DR4 epoch table.  Override it by passing a
custom `column_map` dict (or loading one from YAML/JSON) once ESA publishes the
datamodel — see scripts/dr4_pipeline/refit/README.md ("DR4 column-mapping seam").

stdlib + numpy only (astropy.table accepted if available, but not required).
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np

from model import EpochData

# Best-guess DR4 epoch-astrometry column names -> canonical EpochData fields.
# (Names are PLACEHOLDERS to be confirmed against the published DR4 datamodel.)
DEFAULT_EPOCH_MAP = {
    't':          ['t_tcb', 'obs_time', 'epoch', 'time', 'transit_time', 't_obs'],
    'w':          ['abscissa_al', 'w_al', 'al_obs', 'centroid_al', 'abscissa'],
    'psi':        ['scan_angle', 'psi', 'theta_scan', 'position_angle_scan'],
    'par_factor': ['parallax_factor_al', 'plx_factor_al', 'parallax_factor', 'ppfact_al'],
    'sigma':      ['sigma_al', 'abscissa_error_al', 'al_error', 'w_error', 'centroid_al_error'],
}

# Angle unit of the scan-angle column: 'rad' or 'deg'.  DR3 NSS scan angles are
# in radians; set per the published DR4 datamodel.
DEFAULT_PSI_UNIT = 'rad'


def _first_present(colnames, candidates):
    cset = {c.lower(): c for c in colnames}
    for cand in candidates:
        if cand.lower() in cset:
            return cset[cand.lower()]
    return None


def epoch_table_to_epochdata(
    table,
    *,
    column_map: Optional[dict] = None,
    psi_unit: str = DEFAULT_PSI_UNIT,
    t_ref: Optional[float] = None,
) -> EpochData:
    """Map a DR4 epoch-astrometry table (one source) onto canonical EpochData.

    `table` may be a dict-of-arrays, a pandas.DataFrame, or an astropy Table —
    anything with a `.colnames`/`.keys()` and column indexing.  `column_map`
    overrides DEFAULT_EPOCH_MAP (give the *resolved* DR4 name per field, or a
    list of candidates).  This is the ONLY place DR4 column names enter.
    """
    cmap = dict(DEFAULT_EPOCH_MAP)
    if column_map:
        for k, v in column_map.items():
            cmap[k] = v if isinstance(v, (list, tuple)) else [v]

    # Resolve column names from whatever container we were handed.
    if hasattr(table, 'colnames'):
        colnames = list(table.colnames)
        getcol = lambda name: np.asarray(table[name], float)
    elif hasattr(table, 'columns'):       # pandas
        colnames = list(table.columns)
        getcol = lambda name: np.asarray(table[name].values, float)
    else:                                  # dict-like
        colnames = list(table.keys())
        getcol = lambda name: np.asarray(table[name], float)

    resolved = {}
    for field_, cands in cmap.items():
        name = _first_present(colnames, cands)
        if name is None:
            raise KeyError(f"DR4 epoch table is missing a column for '{field_}'. "
                           f"Tried {cands}; available={colnames}. "
                           f"Update adapter.DEFAULT_EPOCH_MAP for the published DR4 schema.")
        resolved[field_] = getcol(name)

    psi = resolved['psi']
    if psi_unit == 'deg':
        psi = np.radians(psi)

    return EpochData(
        t=resolved['t'], w=resolved['w'], psi=psi,
        par_factor=resolved['par_factor'], sigma=resolved['sigma'], t_ref=t_ref,
    )


# Best-guess DR4 nss_two_body_orbit field map (for the cascade re-run seam; the
# rehunt sibling owns the cascade itself — here we just normalise the anchor row
# the decision logic compares against).
DEFAULT_NSS_MAP = {
    'period':          ['period', 'p', 'orbital_period'],
    'eccentricity':    ['eccentricity', 'ecc', 'e'],
    'parallax':        ['parallax', 'plx'],
    'a_thiele_innes':  ['a_thiele_innes'],
    'b_thiele_innes':  ['b_thiele_innes'],
    'f_thiele_innes':  ['f_thiele_innes'],
    'g_thiele_innes':  ['g_thiele_innes'],
    'significance':    ['significance', 'sig'],
    'goodness_of_fit': ['goodness_of_fit', 'f2', 'gof'],
    'inclination':     ['inclination', 'incl', 'i'],
}


def normalize_nss_row(row, column_map: Optional[dict] = None) -> dict:
    """Normalise one DR4 nss_two_body_orbit row to canonical keys (best-effort)."""
    cmap = dict(DEFAULT_NSS_MAP)
    if column_map:
        for k, v in column_map.items():
            cmap[k] = v if isinstance(v, (list, tuple)) else [v]
    keys = list(row.keys()) if hasattr(row, 'keys') else list(getattr(row, 'colnames', []))
    out = {}
    for field_, cands in cmap.items():
        name = _first_present(keys, cands)
        out[field_] = (row[name] if name is not None else None)
    return out
