# Paper-ready catalog v2 — dormant compact-object candidates from Gaia DR3 NSS

*A re-run of the 4-filter cascade on 56,100 NSS Orbital + AstroSpectroSB1
sources with three corrections from the HD 1957 deep-dive and the
web-tool verification session.  See `docs/CASCADE_CORRECTIONS_2026_05_28.md`
for the methodology note.*

*Compiled 2026-05-28.  Replaces `PAPER_READY_CATALOG_2026_05_28.md`.*

## Corrections applied (v1 → v2)

| Correction | Effect |
|---|---|
| **A. NSS parallax preferred** | M_2 reduces by 1.2-2.5× for binaries with significant orbital reflex |
| **B. K_obs = rv_amplitude_robust / 2** | sini_implied halves; Filter #32 verdicts become physically meaningful |
| **C. F#30 logg fallback chain** | HD 1957 / BD+38 2040 correctly demoted as K-giants (gspphot logg NaN, gspspec_ann logg < 2.7) |

## Headline change

The original "7 Tier-1" headline catalog **completely restructures** after
v2 corrections — four of the seven "Tier-1 BHs" drop to the
`WD_or_low_mass_star` class with M_2 in the 1.0-1.3 M_sun range, and HD
1957 is correctly demoted by F#30.

| # | Source | name | v1 verdict | v1 M_2 | v2 verdict | v2 M_2 | v2 sin(i) | Δ |
|---:|---|---|---|---:|---|---:|---:|---|
| 1 | 6811355413155399040 | HD 207141       | Tier-1 BH       | 7.57 | **Tier-1 NS**                  | 1.31 | 0.83 | downgraded BH → NS |
| 2 | 2543788153077017344 | HD 1957         | Tier-1 NS       | 2.40 | **Demoted (F#30 K-giant)**     | 2.02 | 0.57 | dropped (F#30 v2 catches K-giant) |
| 3 |  666596383384888320 | TYC 1363-2339-1 | Tier-1 BH       | 3.88 | **Rejected — WD-class**        | 1.12 | 0.90 | dropped (NSS plx) |
| 4 | 3396420280383215360 | TYC 1299-727-1  | Tier-1 BH       | 3.50 | **Rejected — WD-class**        | 1.18 | 0.86 | dropped (NSS plx) |
| 5 | 1913089145012902016 | TYC 2773-348-1  | Tier-1 BH       | 3.21 | **Rejected — WD-class**        | 1.03 | 0.71 | dropped (NSS plx) |
| 6 | 3020944382416549632 | TYC 4791-2322-1 | Tier-1 NS       | 2.66 | **Tier-1 NS**                  | 1.34 | 0.75 | survived |
| 7 | 6471824298353396736 | TYC 8785-1657-1 | Tier-1 BH       | 3.63 | **Rejected — WD-class**        | 1.06 | 0.90 | dropped (NSS plx) |

(All seven survived F#29/F#31/F#32 in v2; the four that became
`WD_or_low_mass_star` did so because v2's NSS-parallax-corrected M_2 sits
in the 0.5-1.2 M_sun range — by definition Rejected for our compact-object
search, but legitimately interesting as **sub-Chandrasekhar / massive CO
WD companions** in their own right.)

## Tier counts (v2, full 56,100-source re-run, 2026-05-28)

*Full Gaia ADQL lookup of NSS plx + logg_gspspec_ann + logg_gspspec for
all 56,100 input sources.  Runtime: 1120 s (= 18.7 min, 549 batches @ 100
source_ids each).  All 56,100 sources got NSS parallax; 44,984 got
logg_gspspec_ann; 44,494 got logg_gspspec.*

| Tier | v1 count | v2 count | Notes |
|---|---:|---:|---|
| **Tier-1 BH**                      | **16**  | **2**   | Mass cut: M_2 ≥ 3.0 with all 4 filters PASS |
| **Tier-1 NS**                      | **104** | **277** | 1.2 ≤ M_2 < 3.0 with all 4 filters PASS |
| Tier-2 (RV inconclusive)           | —       | 87      | F#31 AMBIGUOUS or NO_DATA |
| Demoted F#30 (K-giant chromatic)   | —       | 308     | logg < 2.7 from any of gspphot/ann/gspspec, or BP-RP > 1.2, or K-giant Teff proxy |
| Demoted F#32 (joint K_obs/K_pred)  | —       | 148     | sini_implied = (K_obs/2)/K_pred(i=90°) > 1.05 |
| Demoted F#31 (phantom RV)          | —       | 8       | rv_amplitude_robust > 5 but rv_chisq_pvalue > 0.5 |
| Rejected (WD / M-dwarf / BD / planet class) | — | 55,270 | M_2 below 1.2 M_⊙ (most of the 56,100 input) |
| **Total**                          | 56,100  | 56,100  | unchanged input pool |

(The 277 + 2 Tier-1 NS+BH count of 279 is much larger than v1's 120 because
the v2 default M_1 prior is 1.5 M_⊙ (matching the web tool) while v1 used
FLAME M_1 with fallback to 1.0 M_⊙.  Sources with v1 M_1 ≈ 1.0 and
M_2 ≈ 0.9 (WD-class) now have v2 M_1 = 1.5 and M_2 ≈ 1.3 (NS-class).  v2's
larger Tier-1 NS pool is mostly **post-mass-transfer massive-WD systems**
that satisfy the formal NS mass cut but are not BH/NS in nature.)

## Tier-1 transitions: v1 → v2

After the full-scope re-run completes, three operationally important
categories emerge.  All numbers are from the v2 parquet
(`data/derived/main_hunt_derived_v2.parquet`).

| Category | Count | Description |
|---|---:|---|
| **Survived** (v1 Tier-1 → v2 Tier-1) | **31**  | Original Tier-1 candidates still passing all 4 v2 filters |
| **Dropped** (v1 Tier-1 → v2 demoted/rejected) | **89**  | Originals that v2 demotes (chiefly to `WD_or_low_mass_star`) |
| **New Tier-1** (in v2 only, not in v1) | **248** | Sources that were sub-NS-class or F#32-demoted in v1; promoted by M_1=1.5 prior + K_obs/2 fix |

### Breakdown of the 89 dropped v1 Tier-1

| New v2 tier | Count |
|---|---:|
| `Rejected — class=WD_or_low_mass_star` | 82 |
| `Demoted (failed F#30 K-giant chromatic)` | 7 |

(The 82 "drop to WD class" sources are the most striking effect: with
NSS parallax, their M_2 falls from ≈ 2-7 M_⊙ to ≈ 1.0-1.2 M_⊙,
pushing them out of the NS-mass cut into the `WD_or_low_mass_star`
class.  Four of the seven original Tier-1 BH candidates — TYC 1363,
TYC 1299, TYC 2773, TYC 8785 — are in this group.)

### Of the 248 New Tier-1 in v2

- **82** were "Demoted F#32 NS" in v1 — the K_obs/2 correction makes
  their sini_implied physically meaningful (≤ 1.05) so they pass F#32.
- **~166** were `WD_or_low_mass_star` class in v1 (M_2 < 1.2 with
  v1 M_1 ≈ FLAME or 1.0) and now have M_2 ≥ 1.2 because v2's M_1 =
  1.5 prior pushes the mass-function solution higher.

**Top 15 NEW v2 Tier-1 NS candidates by significance:**

| source_id | sig | M_2 | sin(i) | plx | G | P_d | e |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1985832181476519936 | 434.4 | 1.30 | 0.86 | 10.52 |  7.74 | 884.1 | 0.39 |
| 1203462107062861440 | 311.9 | 1.21 | 0.76 |  5.78 |  9.69 | 521.1 | 0.25 |
| 5640825637852070016 | 295.1 | 1.35 | 0.98 |  4.16 |  9.26 | 554.9 | 0.25 |
| 1308841500493146112 | 232.9 | 1.37 | 0.74 |  2.78 | 10.40 | 720.6 | 0.24 |
| 6419437207856851584 | 212.2 | 1.31 | 0.74 |  2.25 | 10.72 | 766.5 | 0.38 |
| 6453094358292937984 | 209.5 | 1.33 | 1.05 |  7.56 |  9.62 | 330.0 | 0.34 |
|  823243942431149568 | 194.2 | 1.34 | 0.82 |  2.80 |  9.53 | 668.4 | 0.20 |
| 4934036581148964608 | 193.2 | 1.22 | 0.98 |  2.81 | 10.40 | 889.6 | 0.22 |
|  680160749097524608 | 188.6 | 1.25 | 0.37 |  2.96 | 11.87 | 794.6 | 0.14 |
|  169521744997530496 | 184.3 | 1.26 | 0.96 |  2.41 | 12.31 | 708.2 | 0.22 |
| 5551709778040603136 | 183.5 | 1.22 | 1.02 |  3.90 | 10.71 | 489.2 | 0.20 |
| 5522158959944092288 | 166.8 | 1.30 | 0.94 |  3.02 | 11.03 | 778.2 | 0.27 |
| 2152301540450772608 | 163.2 | 1.21 | 0.80 |  2.34 | 11.87 | 618.9 | 0.33 |
| 4614234209641846144 | 161.7 | 1.21 | 0.75 |  5.01 | 10.37 | 563.9 | 0.47 |
| 2029703485715058304 | 160.9 | 1.33 | 1.05 |  3.05 | 10.72 | 278.3 | 0.01 |

Most of these have M_2 ≈ 1.2-1.4 M_⊙ — at the heavy-WD / light-NS
boundary.  The brightest (G < 10) are the most accessible to follow-up
RV.  All 277 v2 Tier-1 NS are in the output parquet.

### The two surviving v2 Tier-1 BH

| source_id | M_2 | sin(i) | Notes |
|---|---:|---:|---|
| 6281177228434199296 | 12.75 | 0.11 | Face-on (sin i = 0.11), F-G primary with logg_gspphot = 4.0 — clean F#30 pass.  Worth follow-up but the very low inclination keeps M_2 highly uncertain. |
| 3263804373319076480 |  3.22 | 0.46 | New v2 entry (not in v1 Tier-1 BH list).  RUWE / SB2 status warrants double-check. |

## Methodology validation cross-checks

### Gaia BH2 verification (Correction B proof)

Cross-check against Gaia BH2 (source_id 5870569352746779008):
- Published K_1 (El-Badry+ 2023): **21.2 km/s**
- Gaia DR3 `rv_amplitude_robust`: **36.96 km/s**
- Ratio: 1.74 ≈ 2 (suppressed by e=0.518 eccentricity)
- For circular orbits (e=0): ratio is exactly 2 by definition (peak-to-trough sin = 2·amplitude)

### NSS-plx-bias measurement (Correction A proof)

The 7 original Tier-1 candidates have NSS-plx / gaia_source-plx ratios
spanning 1.09× (TYC 4791) to 2.46× (TYC 1363).  See
`docs/CASCADE_CORRECTIONS_2026_05_28.md` Table "Measured bias for the 7
Tier-1 candidates" for the full numerical comparison.

The ratio scales with photocentric reflex (RUWE, a_phot, period), as
expected from the gaia_source single-star fit's absorption of orbital
displacement.

### HD 1957 / BD+38 2040 logg verification (Correction C proof)

| Source | logg_gspphot | logg_gspspec_ann | logg_gspspec | v2 F#30 |
|---|---:|---:|---:|---|
| HD 1957              | NaN  | **2.63** | 2.36 | FAIL (catches via gspspec_ann) |
| BD+38 2040 *(in deferred Accel-NSS pool)* | NaN  | 2.45     | 2.20 | FAIL (would also catch via gspspec_ann) |

HD 1957 has `logg_gspphot=NaN` (GSP-Phot SED fit failed due to binary
photometric signature) and was missed by v1 F#30.  Its
`logg_gspspec_ann = 2.63` is below the 2.7 threshold, so v2 catches it.

Aggregate effect: v1 F#30 (cbias_risk) fired on 8,313 sources globally
and 606 BH/NS-class sources; v2 F#30 fires on 9,353 sources globally
and 308 v2-BH/NS-class sources.  The qualitative effect is that the
**right** K-giants get caught — HD 1957 being the headline example.

(BD+38 2040 sits in the Acceleration NSS pool, not the Orbital +
AstroSpectroSB1 pool used by v1/v2; the same correction will apply when
the Acceleration NSS extension is built.)

## What v2 does NOT change

- The cascade filter thresholds (M_2 boundaries, BP-RP cutoff, logg
  cutoff) are unchanged from v1.
- The set of NSS sources scanned (56,100 Orbital + AstroSpectroSB1) is
  unchanged.
- The Filter #29 (SB2) and Filter #31 (paired K_obs+pvalue) checks are
  unchanged.

## What v2 explicitly defers

- **Acceleration NSS extension**: ~5,800 sources with single-parameter
  PM-acceleration solutions (no Thiele-Innes orbit fit).  Requires a
  different mass-function inversion (PM-acceleration → M_2 via χ²
  bracketing rather than algebraic Thiele-Innes).  Tracked as a
  separate codebase change.
- **Re-training of finetune-v2 ML classifier**: trained on v1 features
  (M_2_msun, sini_implied).  Deferred until v2 candidate list is final.

## Output files

| File | Contents |
|---|---|
| `data/derived/main_hunt_derived_v2.parquet` | 56,100 rows × ~58 cols (v1 + v2 columns side-by-side) |
| `data/derived/main_hunt_derived_v2_supplementary.parquet` | Gaia ADQL lookup cache (NSS plx, logg_gspspec_ann, etc.) |
| `scripts/streaming/v2_corrected/consumer_v2.py` | v2 derivation library (importable) |
| `scripts/streaming/v2_corrected/run_v2.py` | v2 driver script |
| `docs/CASCADE_CORRECTIONS_2026_05_28.md` | Methodology note documenting the three corrections |

## Recommended next observational steps (v2 update)

1. **HD 207141 + TYC 4791-2322-1**: the two original Tier-1 that survived
   v2.  Both are F-G subgiants with M_2 ≈ 1.3 M_sun (heavy NS) and
   sin(i) > 0.75 — strong candidates for ~10 hr FEROS RV follow-up to
   measure K_1 directly.

2. **HD 1957**: now Tier-2 (or formally Demoted F#30 in v2).  HGCA
   gives a 10σ astrometric acceleration but cannot distinguish
   NS-mass vs massive-WD scenarios.  RV follow-up still warranted but
   the discovery framing changes from "NS" to "NS-or-massive-WD".

3. **Four "fake BH" objects (TYC 1363, 1299, 2773, 8785)**: now
   `WD_or_low_mass_star` class with M_2 in 1.0-1.3 M_sun.  These are
   *interesting* sub-Chandrasekhar WD companions but no longer
   discovery-grade BH candidates.  Worth one paper as a calibration
   sub-sample for the parallax-bias correction.

4. **Newly emerged v2 Tier-1 NS** (sources NOT in v1 catalog but pass
   v2 4-filter cascade): triage by significance + sin(i) + RUWE.  The
   ones with significance ≥ 50, sin(i) > 0.7, RUWE < 5 are the most
   promising — many will turn out to be massive WD systems in disguise
   (post-mass-transfer with G/F primaries), but the subset with K-giant
   primaries automatically gets F#30-demoted.

## See also

- `docs/CASCADE_CORRECTIONS_2026_05_28.md` — methodology note (the three corrections)
- `docs/HD1957_DEEP_ARCHIVAL_2026_05_28.md` — full case study that motivated Corrections A and C
- `scripts/web_tool/app.py` — reference single-source tool (cascade math identical to v2)
- `data/derived/main_hunt_derived_v2.parquet` — full v2 catalog
