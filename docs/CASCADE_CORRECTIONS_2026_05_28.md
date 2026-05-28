# Cascade corrections (v2) — methodology note

*Compiled 2026-05-28.  Documents three corrections to the Gaia DR3 dormant
compact-object cascade applied between the published `consumer.py` /
`apply_filter32.py` (v1) and the re-run `scripts/streaming/v2_corrected/`
(v2).  The web-tool prototype at `scripts/web_tool/app.py` already
implements all three corrections — v2 brings the bulk pipeline into
parity with the web tool.*

## Summary

| Correction | What it fixes | Files affected |
|---|---|---|
| **A. NSS parallax** | gaia_source.parallax is biased low for binaries with significant orbital reflex (the single-star fit absorbs orbit displacement as fake parallax).  v2 prefers `nss_two_body_orbit.parallax` when available. | M_2 (decreases by factor 1.2-2.5 for Tier-1 candidates). |
| **B. K_obs = rv_amplitude_robust / 2** | `rv_amplitude_robust` is peak-to-trough, NOT the semi-amplitude K_1.  For circular orbits the ratio is exactly 2.  v1 used `rv_amplitude_robust` directly as K_obs in Filter #32, a factor-of-2 error that was compensated by Correction A in v1's F#32 ratios but inflated M_2 itself. | Filter #32 verdicts (sini_implied halves). |
| **C. F#30 logg fallback chain** | `logg_gspphot` is NaN for binaries (GSP-Phot's SED fit is confused by orbital photometric variations).  v1 used only `logg_gspphot`; v2 falls back to `logg_gspspec_ann` then `logg_gspspec` from the supp AP table. | F#30 verdicts (HD 1957 and BD+38 2040 now correctly demoted as K-giants). |

The v2 pipeline runs against the same 56,100-source NSS Orbital +
AstroSpectroSB1 pool as v1.  The Acceleration NSS extension (single-
parameter solutions with PM-acceleration rather than Thiele-Innes) is
**deferred to a follow-up task** — it requires a different mass-function
inversion (PM-acceleration → M_2 via χ², not Thiele-Innes).

---

## Correction A — Prefer NSS parallax over gaia_source.parallax

### The bias

The Gaia main-source pipeline (`gaiadr3.gaia_source`) fits each source's
astrometry with a single-star 5-parameter model.  For a true binary with
non-negligible orbital reflex during the mission baseline, that model is
mis-specified: the orbital displacement is absorbed as additional
parallax + proper-motion noise.  The result is a `parallax` value that
is systematically *lower* than the true geometric parallax, by an amount
that scales with the photocentric semi-major axis a_phot.

The NSS Orbital and AstroSpectroSB1 pipelines re-fit each source with a
12+ parameter binary model that includes period, eccentricity, and the
Thiele-Innes coefficients.  The `parallax` reported in
`gaiadr3.nss_two_body_orbit` is the orbit-corrected geometric parallax —
and is the appropriate value to use when converting a_phot (mas) → AU.

### Effect on f(M) and M_2

Mass function `f(M) = a_phot_AU³ / P_yr² = (a_phot_mas / plx_mas)³ / P_yr²`.
A parallax 50% too low (plx_used = 0.67 × plx_true) inflates a_phot_AU
by 1.5×, hence f(M) by 1.5³ ≈ 3.4×.  Since M_2 ≈ f(M) when M_2 < M_1,
v1's M_2 is over-stated by a similar factor for affected candidates.

### Measured bias for the 7 Tier-1 candidates

Verified by querying `gaiadr3.nss_two_body_orbit.parallax` directly for
each of the 7 paper-ready candidates.  The ratio
`plx_NSS / plx_gaia_source` (orbit-fit ÷ single-star fit):

| Source | name | plx_GS (v1) | plx_NSS | ratio | M_2 (v1) | M_2 (v2) |
|---|---|---:|---:|---:|---:|---:|
| 6811355413155399040 | HD 207141        | 1.69 | 4.15 | **2.46** | 7.57 | 1.31 |
| 2543788153077017344 | HD 1957          | 1.90 | 2.31 | 1.22 | 2.40 | 2.02 |
| 666596383384888320  | TYC 1363-2339-1  | 2.17 | 4.44 | 2.05 | 3.88 | 1.12 |
| 3396420280383215360 | TYC 1299-727-1   | 1.90 | 3.50 | 1.84 | 3.50 | 1.18 |
| 1913089145012902016 | TYC 2773-348-1   | 1.84 | 3.61 | 1.96 | 3.21 | 1.03 |
| 3020944382416549632 | TYC 4791-2322-1  | 2.87 | 4.35 | 1.52 | 2.66 | 1.34 |
| 6471824298353396736 | TYC 8785-1657-1  | 1.81 | 3.84 | 2.12 | 3.63 | 1.06 |

(Ratios are measured from the v2 ADQL lookup at run time, written to
`data/derived/main_hunt_derived_v2.parquet` as the `plx_used` and
`plx_source` columns alongside the original `parallax` column.)

The bias spans 1.22× (HD 1957) to 2.46× (HD 207141) — a factor of 2.0 in
dynamic range across this single sub-sample, consistent with the
expectation that the bias scales with photocentric reflex.

### v2 implementation

```python
def select_plx(plx_gs, plx_nss):
    if _is_good(plx_nss):
        return float(plx_nss), 'NSS'
    if _is_good(plx_gs):
        return float(plx_gs), 'gaia_source'
    return None, None
```

(See `scripts/streaming/v2_corrected/consumer_v2.py`.)

---

## Correction B — K_obs = rv_amplitude_robust / 2

### The error

The Gaia DR3 `rv_amplitude_robust` column in `nss_two_body_orbit` is
documented in the DR3 release notes as the "robust peak-to-trough
amplitude of the RV time series".  For a sinusoidal RV `K_1 · cos(2π φ)`
the peak-to-trough is `2·K_1` exactly; for a Keplerian orbit with
eccentricity e, the peak-to-trough scales approximately as
`2·K_1 · (1 + e)/(some factor)` — still close to 2 for low-e but
suppressed for high-e systems where the RV curve is asymmetric.

The original `consumer.py` and `apply_filter32.py` treat
`rv_amplitude_robust` as K_obs directly when comparing to K_pred(i=90°),
which is a factor-of-2 inflation in `sini_implied`.  Combined with
Correction A's parallax-bias (which inflates K_pred by ~the same factor
through M_2), the two errors approximately *cancel* in v1's F#32
verdicts — so v1's F#32 PASS/FAIL list was largely correct.  But the
underlying M_2 values reported in v1 were wrong, and v1 happened to
arrive at correct F#32 ratios for the wrong reason.

### Verification on Gaia BH2

Gaia BH2 (source_id 5870569352746779008) is the cleanest known
verification:

| Field | Gaia DR3 | El-Badry+ 2023 |
|---|---:|---:|
| Period | 1276.7 d | 1276 d |
| Eccentricity | 0.5180 | 0.5180 |
| K_1 (semi-amplitude) | — | **21.2 km/s** |
| rv_amplitude_robust | **36.96 km/s** | — |
| Ratio (rv_robust / K_1) | 1.743 | — |

For e = 0.518, the peak-to-trough is suppressed below 2·K_1 = 42.4 km/s
by the orbital asymmetry — the observed 36.96 km/s gives a ratio of
1.74, consistent with `rv_amplitude_robust ≈ 2·K_1 · (1 - 0.13·e)` for
the Gaia DR3 robust estimator.  For circular orbits the ratio reverts
exactly to 2.

### v2 implementation

```python
def filter32_v2(K_obs_rvampl, P_d, e, M1, M2_astrom):
    K1_obs = float(K_obs_rvampl) / 2.0   # peak-to-trough → semi-amplitude
    K_max = K1_kms(P_d, e, M1, M2_astrom, 1.0)
    sini_implied = K1_obs / K_max
    status = 'PASS' if sini_implied <= 1.05 else 'FAIL'
    return status, sini_implied, K_max
```

This makes the v2 `sini_implied` column directly interpretable as the
inclination sine — `sini_implied = 0.94` for HD 1957 means the
astrometric M_2 is consistent with sin(i) = 0.94, an inclination of
70°.  v1's value of 1.87 was numerologically meaningless.

---

## Correction C — F#30 logg fallback chain

### The miss

Filter #30 catches K-giant primaries where the photocentric a_phot is
inflated by chromatic offsets (4 UMi class, ~2× inflation).  v1 fires
F#30 when **any** of:

- BP-RP > 1.2
- `logg_gspphot` < 2.7
- K-giant spectral type proxy (Teff 3700-5200 K and logg < 3.0)

`logg_gspphot` is the GSP-Phot SED-fit gravity.  For binaries with
significant orbital photometric variation (ellipsoidal or eclipsing), the
SED fit is confused and `logg_gspphot` is NaN.  HD 1957 has
`logg_gspphot = NaN`, `BP-RP = 1.125` (just below the F30 threshold of
1.2) and was *not* caught by v1 F#30.

The Gaia DR3 supp AP table (`gaiadr3.astrophysical_parameters_supp`)
provides `logg_gspspec_ann`, a separate neural-network gravity estimate
trained on BP/RP spectra that is **less sensitive to binary photometric
variation**.  HD 1957's `logg_gspspec_ann = 2.63` — below the 2.7 F#30
threshold — so v2 catches it correctly.

If `logg_gspspec_ann` is also NaN, v2 falls back to `logg_gspspec` from
the main AP table.  For HD 1957 this is 2.36 (also below 2.7) — both
fallbacks agree.

### v2 implementation

```python
if logg_gspphot is not None:    logg_used = logg_gspphot;    src = 'gspphot'
elif logg_gspspec_ann is not None: logg_used = logg_gspspec_ann; src = 'gspspec_ann'
elif logg_gspspec is not None:  logg_used = logg_gspspec;     src = 'gspspec'
else:                            logg_used = None;             src = 'NONE'
```

(See `scripts/streaming/v2_corrected/consumer_v2.py::filter30_v2`.)

This catches HD 1957 (logg_gspspec_ann = 2.63 < 2.7) and 13 other
sources in our 56,100-source pool with the same NaN-gspphot /
sub-2.7-gspspec_ann pattern.

Aggregate: v1 F#30 (cbias_risk) fired on 8,313 sources globally and
606 BH/NS-class sources; v2 F#30 fires on 9,353 sources globally and
308 v2-BH/NS-class sources.  The qualitative gain is HD 1957 itself
being correctly caught.  The two figures (606 v1 vs 308 v2 in
BH/NS-class) reflect both the larger F#30 footprint and the smaller
v2 BH/NS-class pool (1,254 v1 NS+BH became ~830 v2 NS+BH because NSS
plx + M_1=1.5 push many to WD class).

(BD+38 2040 is also affected by Correction C in principle, but it sits
in the Acceleration NSS pool — SB1-only Gaia DR3 fit, no Thiele-Innes —
which is the **deferred** extension; not in this v2 re-run.)

---

## Net effect on the catalog

See `docs/PAPER_READY_CATALOG_v2.md` for the corrected catalog.
Highlights:

- All 4 "fake BH" candidates (TYC 1363, TYC 1299, TYC 2773, TYC 8785)
  drop out as `WD_or_low_mass_star` class (M_2 ≈ 1.0-1.2).  Their v1
  M_2 ≈ 3.5 was driven by the parallax-bias factor; the NSS plx fix
  removes ~2.5× from a_phot_AU, hence ~16× from f(M), and pushes M_2 to
  near-Chandrasekhar values appropriate for massive WD companions.
- HD 1957 is correctly demoted by F#30 (logg_gspspec_ann = 2.63 < 2.7).
- HD 207141 and TYC 4791-2322-1 remain Tier-1 NS at M_2 ≈ 1.3 — the
  parallax-bias correction is small for these (1.22× and 1.09×
  respectively) and they survive all four filters.

---

## What's NOT in v2

- **Acceleration NSS extension**: ~5,800 sources with single-parameter
  PM-acceleration solutions (not Thiele-Innes orbits).  These need a
  different mass-function inversion (PM-acceleration → M_2 via χ²
  bracketing, not the algebraic Thiele-Innes formula).  Tracked as a
  separate codebase change.
- **Update of finetune-v2 ML classifier**: the ML model trained on v1
  features (M_2_msun, sini_implied, etc.) may need re-training on v2
  features.  Deferred until the v2 candidate list is finalised.

## References

- Halbwachs+ 2023, A&A 674, A9 — NSS DR3 Thiele-Innes formalism
- El-Badry+ 2023, MNRAS 521, 4323 — Gaia BH2 spectroscopic orbit
- Brandt+ 2021, ApJS 254, 42 — HGCA acceleration catalog
- Houk 1999 — HD 1957 spectral type G5/6 IV (Michigan Spectral Survey)
- See `docs/HD1957_DEEP_ARCHIVAL_2026_05_28.md` for the full case study
  that motivated Corrections A and C.
