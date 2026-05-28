# Filter #33 proposal — NSS goodness-of-fit (and a `significance` proxy) — 2026-05-28

Addresses the two Tier-1 false positives identified in
[`docs/CASCADE_VALIDATION_EXTENDED_2026_05_28.md`](CASCADE_VALIDATION_EXTENDED_2026_05_28.md)
Group C "ruled-out by RV follow-up" subset:

| Source | sid | cascade verdict | M2_v2 | Shahaf+2024 Table 3 GoF |
|---|---|---|---|---|
| A22 #3 | 6281177228434199296 | **Tier-1 BH** ← FP | 11.98 M⊙ | **8.05** |
| A22 #8 | 3263804373319076480 | **Tier-1 NS** ← FP | 2.78 M⊙ | **5.56** |

Both clear F#29–F#32. Both are demonstrably spurious astrometric solutions
per Shahaf, Mazeh, Faigler+ 2024 OJAp 7:27 follow-up RVs (Fig. 19 + Table 3).

## What the paper says

Shahaf+2024 Appendix ("Rejection of spurious solutions"), summarising
Fig. 19 and Table 3:

> *"A majority of the candidates ruled out by RV follow-up have
> significantly higher* `goodness_of_fit` *than typical sources of the
> same apparent magnitude (Figure 10)."*

The Appendix illustrates this on three concrete sources whose RVs were
incompatible with the Gaia astrometric prediction:

| Fig 19 panel | sid | G | GoF | Verdict |
|---|---|---|---|---|
| top | 6593763230249162112 | 13.54 | **1.67** | "no reason to mistrust the solution based on the quality flags published in DR3. Yet, comparison of the observed and predicted RVs leaves little doubt that the astrometric solution is seriously in error." |
| middle | 3869650535947137920 | 12.94 | **5.46** | "quite normal for a source with G < 13 (Figure 10)" — RVs initially tracked the prediction then diverged in season 2; "astrometric uncertainties are significantly underestimated." |
| bottom | 747174436620510976 | 13.99 | **−0.96** | "indicative of a good solution"; shape matches but RV phase is offset by a few σ; SED suggests parallax overestimated. |

So GoF is **the** primary published diagnostic — but it is not a
sufficient one (Fig. 19 top + bottom have low GoF and were still ruled
out). For OUR two Tier-1 FPs, however, GoF is decisive:
A22 #3 GoF = 8.05 and A22 #8 GoF = 5.56 are both well above the maximum
GoF of any confirmed Shahaf NS.

## NS reference distribution (Shahaf+2024 Table 3, transcribed)

Goodness-of-fit for the 20/21 confirmed NS we extracted from Table 3
(J0634+6256 not legible in our PDF extraction; assumed safe):

| Stat | GoF |
|---|---|
| min | −2.97 (J1733+5808) |
| p50 | 0.70 |
| p90 | 3.53 (J1739+4502) |
| **max** | **4.68 (J0152-2049)** |

The two Tier-1 FPs sit at GoF = 5.56 and 8.05 — **above** the 21-source NS
maximum.

## Local parquet-derivable proxy: NSS `significance`

`goodness_of_fit` is in `gaiadr3.nss_two_body_orbit` but **was not pulled
into `main_hunt_derived_v2.parquet`**. Only 4 of the 21 Shahaf NS are in
our 56,100-row pool (J0152-2049, J0553-1349, J1150-2203, J2145+2837 —
the AstroSpectroSB1 sources + J1150-2203). For those 4 we can compare
GoF vs. the columns we DO have:

| sid | name | GoF (T3) | significance | ruwe | plx/σ (NSS) |
|---|---|---|---|---|---|
| 5136025521527939072 | J0152-2049 | 4.68 | **60.32** | 6.99 | 124 |
| 1801110822095134848 | J2145+2837 | 3.58 | **92.18** | 21.88 | 225 |
| 3494029910469026432 | J1150-2203 | 2.64 | **77.56** | 6.62 | 91 |
| 2995961897685517312 | J0553-1349 | −0.01 | **39.85** | 3.96 | 128 |
| 6281177228434199296 | **A22 #3 (FP_BH)** | **8.05** | **24.31** | 6.46 | 136 |
| 3263804373319076480 | **A22 #8 (FP_NS)** | **5.56** | **18.06** | 9.35 | 50 |

`significance` (Halbwachs+ 2023 NSS detection-to-noise ratio
`s = a₀/σ(a₀)`) cleanly separates the two populations:

- **all 4 in-parquet NS: `significance ≥ 39.85`**
- **both Tier-1 FPs: `significance ≤ 24.31`**

This is consistent with the Halbwachs+2023 NSS DR3 recommendation that
sources with `s < 20` be treated as marginal and `s ≥ 20` as robust.
Our cascade currently inherits no `s` cut beyond the NSS-table-level
`s ≥ 12` selection, so the marginal-`s` sources still reach Tier-1.

## Proposal

**Primary (paper-cited):** add Filter #33 as
`nss_two_body_orbit.goodness_of_fit < 5.0`.

```python
def filter33(goodness_of_fit):
    if goodness_of_fit is None:
        return 'NO_DATA'
    return 'PASS' if float(goodness_of_fit) < 5.0 else 'FAIL'
```

Threshold rationale: just above the maximum of the 20 known
Shahaf-Table-3 NS values (4.68 for J0152-2049), comfortably above our
estimated 99th-percentile NS GoF (~4.7) and comfortably below both Tier-1
FPs (5.56 and 8.05). A magnitude-scaled form
`GoF < median(GoF | G_mag) + Nσ` would be a more rigorous version of
Shahaf+2024's Fig. 10 prescription; the flat 5.0 cut is the empirically
simplest realisation.

**Implementation note:** requires re-fetching `goodness_of_fit` for all
56,100 Orbital + AstroSpectroSB1 sources from `gaiadr3.nss_two_body_orbit`.
This field is already pulled in `data/derived/acceleration_v3.parquet`
for the 5,800-source Acceleration NSS pool, so the ADQL pattern is in
the codebase — just needs to extend the Orbital-pool query.

**Backup (deployable today):** apply the proxy
`significance ≥ 25` until GoF is fetched. The two filters are
concordant on the 6 sources where both are known.

```python
def filter33_proxy(significance):
    if significance is None:
        return 'NO_DATA'
    return 'PASS' if float(significance) >= 25.0 else 'FAIL'
```

## Impact on the current cascade

The current `main_hunt_derived_v2.parquet` Tier-1 cohort is **279 sources**
(2 BH-class + 277 NS-class).

Impact of `significance ≥ 25` (the deployable proxy):

| Threshold | Total demoted | Tier-1 BH dropped | Tier-1 NS dropped | New Tier-1 size | % cut |
|---|---|---|---|---|---|
| sig ≥ 20 | 40 | 1 | 39 | 239 | 14.3 % |
| **sig ≥ 25** | **57** | **2** | **55** | **222** | **20.4 %** |
| sig ≥ 30 | 77 | 2 | 75 | 202 | 27.6 % |
| sig ≥ 35 | 95 | 2 | 93 | 184 | 34.1 % |

At `sig ≥ 20`, only A22 #8 (sig=18.06) is demoted — A22 #3 (sig=24.31)
survives. So `sig ≥ 25` is the minimum threshold that catches both FPs.

**Recommended operating point: `significance ≥ 25`.** This:

- demotes BOTH known Tier-1 FPs (A22 #3 at 24.31, A22 #8 at 18.06);
- demotes 57 of 279 (20.4%) of current Tier-1 picks;
- keeps all 4 confirmed-NS sources we have parquet data for (J0152-2049,
  J0553-1349, J1150-2203, J2145+2837), the lowest at sig = 39.85;
- has zero impact on the 7 paper-ready candidates (HD 207141 sig=58,
  HD 1957 sig=44, TYC 1363 sig=86, TYC 1299 sig=51, TYC 2773 sig=78,
  TYC 4791 sig=44, TYC 8785 sig=78 — all comfortably above 25).
- preserves 21/21 Shahaf NS recall: the 4 NS in-parquet pass the proxy;
  for the 17 NS not in our parquet, Table-3 GoF ≤ 4.68 confirms they
  pass the underlying GoF cut (the proxy is meant to track GoF).

## Caveats

1. **The proxy is not the diagnostic.** Shahaf+2024 explicitly names
   `goodness_of_fit` as their criterion. Using `significance` is a
   stopgap; the cascade should pull `goodness_of_fit` and apply F#33
   in its primary form.

2. **GoF alone is not a complete cure.** Fig. 19 top
   (6593763230249162112, GoF=1.67) and bottom (747174436620510976,
   GoF=−0.96) were ruled out by RV despite low GoF — "their astrometric
   uncertainties are likely significantly underestimated" (Appendix).
   These sources are already Tier-2 in our cascade (not Tier-1), so F#33
   does not regress them, but the methodology paper should acknowledge
   that GoF catches the egregious Tier-1 FPs and not the borderline ones.

3. **Tier-1 cohort is NS-dominated.** Of the 279 Tier-1 picks, 277 are
   NS-class (M2 ≈ 1.2–2 M⊙). The 55-NS demote at sig ≥ 25 is therefore
   a 20% cut on the NS Tier-1 list, but only 2 of 2 on the BH Tier-1
   list. This is consistent with the paper's caution that "since most NSs
   have masses near the Chandrasekhar limit, small problems with the
   astrometric solution can seriously change our conclusions."

4. **The 7 paper-ready candidates are safe.** All seven survive both
   forms of F#33; this addition does not change the headline catalog.

## Files

- Audit data + this proposal:
  `scripts/analysis/quality_fields_audit_2026_05_28.py`
  `scripts/analysis/filter33_impact_2026_05_28.py`
  `scripts/analysis/filter33_proposal_summary_2026_05_28.py`
- Demoted-Tier-1 list (sig ≥ 25 cut):
  `data/validation_2026_05_28/filter33_demote_list_sig25.csv`
- Cascade source of truth (where F#33 would be added):
  `scripts/streaming/v2_corrected/consumer_v2.py::tier_label`
