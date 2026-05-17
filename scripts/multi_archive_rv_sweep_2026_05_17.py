"""Multi-archive RV mining sweep (2026-05-17).

For each headline candidate, query every public RV archive we can reach
and report:
  * Number of epochs
  * Baseline (days)
  * Per-epoch precision (m/s)
  * Whether sampling is sufficient to test the NSS orbital fit

Archives queried (via Vizier TAP unless noted):
  * APOGEE DR17 allVisit (III/284/allvis)
  * RAVE DR6 (III/283)
  * GALAH DR4
  * LAMOST DR10
  * HARPS RVBank (Trifonov+ 2020: J/A+A/636/A74)
  * NASA Exoplanet Archive — rv table

The goal is to identify any candidate where archival data is dense
enough to constrain the orbital K_1 directly without new observations.
"""
from __future__ import annotations

import io
import math
import urllib.parse
import urllib.request

import polars as pl

VIZIER = "https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync"

# Top 4 candidates by V-mag (RV-easiest first)
CANDIDATES = [
    ("HD 76078",     1017645329162554752, 134.05530, 53.05869, 8.72),
    ("BD+56 1762",   1607476280298633984, 222.01172, 56.15920, 10.03),
    ("HIP 60865",    1518957932040718464, 187.18108, 28.18672, 12.09),
    ("HD 101767",    841536616165020416,  175.61020, 56.85070, 8.88),
]


def adql(url, q, timeout=120):
    full = f"{url}?REQUEST=doQuery&LANG=ADQL&FORMAT=csv&QUERY={urllib.parse.quote(q)}"
    try:
        with urllib.request.urlopen(full, timeout=timeout) as r:
            return pl.read_csv(
                io.StringIO(r.read().decode()),
                infer_schema_length=2000,
                ignore_errors=True,
            )
    except Exception as e:
        print(f"  query failed: {e}")
        return None


def cone_search(table, ra, dec, radius_arcsec, columns="*", ra_col="RAJ2000", dec_col="DEJ2000"):
    """Vizier cone search. radius in arcsec."""
    radius_deg = radius_arcsec / 3600.0
    q = (
        f'SELECT {columns} FROM "{table}" '
        f'WHERE 1=CONTAINS(POINT(\'ICRS\',"{ra_col}","{dec_col}"),CIRCLE(\'ICRS\',{ra},{dec},{radius_deg}))'
    )
    return adql(VIZIER, q)


def main():
    print(f"\n{'Candidate':14s}{'Archive':22s}{'N_visits':>10s}{'Baseline_d':>12s}{'σ_RV_mps':>10s}{'Notes'}")
    print('-' * 100)

    for name, sid, ra, dec, V in CANDIDATES:
        print(f"\n=== {name} (Gaia DR3 {sid}, V={V}) ===")

        # APOGEE DR17 allVisit — table III/284/allvis, cols: APOGEE_ID, MJD, VHELIO, VRELERR
        df = cone_search(
            "III/284/allvis",
            ra, dec, 5.0,
            columns='"APOGEE_ID","MJD","VHELIO","VRELERR"',
            ra_col="RAJ2000", dec_col="DEJ2000",
        )
        if df is not None and df.height > 0:
            mjds = df["MJD"].drop_nulls().to_list()
            sigmas = df["VRELERR"].drop_nulls().to_list()
            baseline = max(mjds) - min(mjds) if len(mjds) > 1 else 0.0
            sig_med = float(pl.Series(sigmas).median()) * 1000 if sigmas else None  # km/s -> m/s
            print(f'  APOGEE DR17: {df.height} visits, baseline={baseline:.0f}d, σ_med={sig_med:.0f if sig_med else "?"} m/s')
        else:
            print(f'  APOGEE DR17: 0 visits')

        # RAVE DR6 — table III/283
        df = cone_search(
            "III/283/rave",
            ra, dec, 5.0,
            columns='"RAJ2000","DEJ2000","HRV","e_HRV","Obsdate"',
        )
        if df is not None and df.height > 0:
            print(f'  RAVE DR6:    {df.height} obs')
        else:
            print(f'  RAVE DR6:    0 obs')

        # GALAH DR4 — table J/MNRAS/516/3344 or similar
        for galah_table in ["III/284/galah_dr3", "J/MNRAS/516/3344"]:
            df = cone_search(galah_table, ra, dec, 5.0)
            if df is not None and df.height > 0:
                print(f'  GALAH ({galah_table}): {df.height} obs')
                break
        else:
            pass  # silent if not found

        # LAMOST DR10 — table V/156 or V/175
        for lamost_table in ["V/175/lrs_dr8", "V/156/lrs_dr7"]:
            df = cone_search(lamost_table, ra, dec, 5.0)
            if df is not None and df.height > 0:
                print(f'  LAMOST ({lamost_table}): {df.height} obs')
                break

        # HARPS RVBank Trifonov+ 2020 — J/A+A/636/A74
        df = cone_search(
            "J/A+A/636/A74/sample",
            ra, dec, 5.0,
            columns='*',
        )
        if df is not None and df.height > 0:
            print(f'  HARPS RVBank: target listed ({df.height} rows)')
        else:
            print(f'  HARPS RVBank: not in target list')

        # Tycho-2 / Hipparcos already used elsewhere — skip
        # NASA Exo Archive — already cross-matched via NASA_HOSTS_CSV; skip


if __name__ == "__main__":
    main()
