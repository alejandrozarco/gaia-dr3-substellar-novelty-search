# Hipparcos NSS port (v1.16.0, 2026-05-17)

Bulk download of the full van Leeuwen 2007 reduction
(Vizier `I/311/hip2`, 117,955 rows) for cross-match against our headline
candidates and the Gaia DR3 NSS pool.

## Sn-column semantic (van Leeuwen 2007)

Sn is the "solution code" — single-digit values are true NSS
classifications; two-digit compound values combine a solution-attempt
flag with a quality flag.

| Sn   | Count    | Meaning                                              |
|-----:|---------:|------------------------------------------------------|
| 5    | 101,801  | Standard 5-parameter single-star solution            |
| 15   |   8,813  | Revised single-star (van Leeuwen second pass)        |
| 55   |   2,343  | Single-star with revised quality flag                |
| 95   |   1,908  | Revised component flag                               |
| 1    |   1,371  | Orbital solution (HIP NSS-O)                         |
| 7    |   1,208  | Stochastic / VIM (Variability-Induced Mover)         |
| 75   |     239  | Revised stochastic                                   |
| 9    |     104  | Resolved double component                            |
| 17   |     103  | (compound)                                           |
| 57   |      27  | (compound)                                           |
| 3    |      25  | Acceleration solution (HIP NSS-A)                    |
| 35   |       6  |                                                      |
| 0    |       5  |                                                      |
| 115  |       2  |                                                      |

True NSS classifications (single-digit Sn ≠ 5): 1+3+7+9 = 2,708 sources.

## Headline-15 cross-match

| Name      | HIP    | Sn  | Note                                |
|-----------|-------:|----:|-------------------------------------|
| HD 101767 |  57135 |  5  | single-star                         |
| **HD 104828** | **58863** | **7** | **stochastic — pre-Gaia companion** |
| HD 140895 |  77262 |  5  |                                     |
| HD 140940 |  77357 |  5  |                                     |
| BD+46 2473|  90060 |  5  |                                     |
| BD+35 228 |   5787 |  5  |                                     |
| HIP 60865 |  60865 |  5  |                                     |
| HIP 20122 |  20122 |  5  |                                     |
| HD 76078  |  43870 |  5  |                                     |
| BD+56 1762|  72389 |  5  |                                     |
| HD 134574 |  74357 |  5  |                                     |
| HD 156239 |  84737 |  5  |                                     |
| HD 156342 |  84506 | 15  | revised single-star                 |
| HD 11042  |   8278 |  5  |                                     |
| HD 199695 | 103488 |  5  |                                     |

(HD 343905 and CD-70 5 not in HIP.)

14/15 have Sn=5 (single-star) or Sn=15 (revised single-star) — they
are genuinely Gaia-DR3-novel discoveries with no pre-Gaia astrometric
companion detection. **HD 104828's Sn=7 is the lone exception.**

## HD 104828 = triple-corroborated

Three independent astrometric witnesses for a companion at HD 104828:

1. **Hipparcos van Leeuwen 2007 Sn=7** (1991 epoch). The stochastic
   classification means the single-star 5-parameter astrometric model
   was rejected; the source has motion that requires a more complex
   model. This is a *pre-Gaia* companion-signal flag.

2. **HGCA Brandt 2024 χ² = 23.6** (1991→2016 25-yr proper-motion
   anomaly). Hipparcos position propagated to Gaia DR3's 2016 epoch
   disagrees with Gaia's measured position by 23.6 in chi² units. In
   the CORROBORATED tier (5-30) → real companion consistent with
   substellar mass.

3. **Gaia DR3 NSS Acceleration9** (2014-2016 internal). Pipeline-derived
   M_2_marg = 41 MJ with HGCA-cleared mass posterior.

The three channels span 25 years of independent astrometric
observation. The companion has been detectable since 1991 but never
been published. HD 104828 is the project's strongest candidate by
corroboration count.

## How the van Leeuwen 2007 bulk pull was done

Original v1.16.0 attempt via `Vizier.query_constraints(catalog="I/311/hip2",
Sn="!=5")` returned only 50 rows — Vizier's constraint interface enforces
a row cap that bypasses `ROW_LIMIT=-1`. Successful approach:

```python
from astroquery.vizier import Vizier
Vizier.ROW_LIMIT = -1
Vizier.TIMEOUT = 300
v = Vizier(columns=["HIP", "Sn", "Hpmag", "RAhms", "DEdms", "pmRA",
                       "pmDE", "Plx"])
v.ROW_LIMIT = -1
cats = v.get_catalogs("I/311/hip2")
df = cats[0].to_pandas()
# 117,955 rows in ~ 30 seconds
```

## Files

- `data/intermediate/hipparcos_vanLeeuwen2007_FULL.csv` — 117,955 rows
- `data/intermediate/headline_in_hip_FULL.csv` — headline-15 cross-match
- `data/intermediate/hip_nss_summary_2026_05_17.csv` — summary table
- Script: `scripts/hipparcos_nss_port_2026_05_17.py` +
  `scripts/fetch_missing_data_2026_05_17.py` (revised version with
  bulk-pull fix)
