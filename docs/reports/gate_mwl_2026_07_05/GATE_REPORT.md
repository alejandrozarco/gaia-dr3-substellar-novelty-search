# GATE: Multi-wavelength cross-match of the DESI RV-variable catalog

Date: 2026-07-05. Parent catalog: docs/reports/desi_hunt_phase2a_2026_07_05/clean_candidates.csv.gz
(18,946 rows, G=16.0-18.5, all pre-flagged `novel=True` / `known_any=False` by the
existing store front-filter).

## 1. Prior art

- **Method-level (GALEX UV-excess as companion typing)**: ALREADY RUN AND VERDICTED by
  this project — task #121 "Odd-axis C: GALEX UV x astrometry" (2026-06-05,
  RESEARCH_LOG.md). Published: Makarov 2017 (1705.01114), Shahaf+2023 Triage II
  (2309.15143, WD census on Gaia NSS pool via the SAME statistic), Garbutt/Parsons+2024
  WD-pathways X (2403.07985). Verdict then: NO-GO as a standalone hunt; GO only as a
  standing screening add-on to the deep-dive workflow. That verdict was on the Gaia-NSS
  astrometric-binary pool; this lane applies the same published statistic to a
  DIFFERENT parent sample (DESI spectroscopic RV-variables). The underlying method is
  not novel either way.
- **PCEB catalogs (Rebassa-Mansergas)**: SDSS-based WDMS binary series (papers I-XIV+),
  already folds in GALEX + UKIDSS multi-wavelength SEDs for WD temperature/companion
  typing. Field is active and owns the general "spectroscopic-binary x UV/IR SED"
  recipe. No DESI-specific successor found.
- **DESI-specific**: searched for a DESI-DR1-selected multiwavelength binary paper —
  found none. The one existing DESI-DR1 RV-variable publication is Smith 2026 (RNAAS,
  "A High-amplitude Radial Velocity Variable in DESI DR1", Gaia DR3
  3802130935635096832) — a single-object note, not a systematic survey; per the
  paper itself (via WebSearch) that object has a close 0.688" Gaia neighbor (blend
  suspect) and the author ALREADY checked archival GALEX/WISE and found NO UV or IR
  excess. This object is correctly absent from our clean_candidates.csv.gz
  (`smith2026_flagplant` sums to 0 in that file — 0 overlap risk).
- A tangential arXiv hit, "Investigating the Unresolved Binary Population in Gaia DR3
  Using Multi-Wavelength Photometry" (2605.00792), is an independent/amateur-observatory
  paper on RESOLVED WDS visual binaries via 2MASS/Pan-STARRS — different sample and
  method, not competing with this niche.
- **Conclusion**: the DESI-RV-selected x GALEX/WISE/eRASS1 cross-match, AS A DATASET, is
  an unworked niche (nobody has this specific 18,946-object selection). But the METHOD
  (UV-excess companion typing) is thoroughly published and this project has already
  run it once with a NO-GO-standalone verdict on a different pool. This lane is
  therefore, at best, a second application of a known statistic to a novel sample —
  method-validation framing applies, per the CLAUDE.md prior-art-gate rule.

## 2. Cross-match pool sizes (full 18,946 catalog, VizieR via astroquery.XMatch)

Match radius 5" initial pull, tightened to <2.5" (best/unique match kept) for the
"reliable" pool used in all counts below.

| Channel | Catalog | Raw match (<5") | Reliable (<2.5", deduped) | % of 18,946 |
|---|---|---|---|---|
| UV | GALEX AIS (II/335) | 7,257 rows / 7,191 unique | 6,681 | 35.3% |
| X-ray | eRASS1-m (J/A+A/682/A34) | 6 | 6 | 0.03% |
| IR | AllWISE (II/328) | 18,408 rows / 18,359 unique | 18,200 | 96.1% |

Gaia BP-RP colors were fetched (TAP, synchronous chunked query) for 6,550/6,681 of the
GALEX-matched sample to support a UV-excess cut.

### UV-excess (PCEB) candidate pool
Self-calibrated ridge line: NUV-G vs BP-RP running-median/MAD in 0.15-mag bins, using
the sample's OWN distribution as the "normal" baseline (no external MS template — this
is a known weakness, see Section 3). Candidates flagged where NUV-G is anomalously
BLUE (bright) for their color at >=N sigma:

| Threshold | N candidates | % of GALEX-matched |
|---|---|---|
| > 2 sigma | 106 | 1.62% |
| > 3 sigma | 6 | 0.09% |
| > 4 sigma | 2 | 0.03% |
| > 5 sigma | 1 | 0.02% |

**UV-excess candidate pool (gate deliverable): ~6 candidates at a defensible >=3sigma
cut** (see top-10 table, Section 5) out of 6,528 GALEX+color-matched sources.

### X-ray (eRASS1) pool
6 matches total, all >2" separation (angDist 0.22-4.86"), consistent with the known
eRASS1-DE western-sky-only coverage colliding with this all-sky RV catalog (most of the
18,946 simply have no eROSITA coverage, not "no X-ray"). This channel is coverage-
starved, not physically null — same caveat this project has hit before (RESEARCH_LOG
line ~198).

### IR-excess (WISE) pool
- W1-W2 (AA-quality only, 13,693 sources): >0.2 mag excess = 261; >0.4 mag = 11.
- W2-W3 "red" (>1.0 mag) came back as 17,082/18,200 (94%) — THIS IS A FALSE SIGNAL, not
  a real dust population. W3 photometric quality flag is 'U' (upper limit, not a
  detection) for 16,829/18,200 (92%) of matches at these Gaia G=16-18.5 depths; only
  1,370 have any W3 error estimate and most of those exceed 0.3 mag. W2-W3 excess counts
  are not usable without a W3-detection-quality cut; discard that channel entirely.
- Usable IR-excess pool: the AA-quality W1-W2 pool, ~11-261 depending on threshold,
  unvetted for saturation/blending.

### Joint (any-band-peculiar)
Not computed as a combined statistic — eRASS1 (6) and the WISE W2-W3 (unusable) make a
meaningful "joint" count dominated by coverage/systematics rather than astrophysics.
The only band offering a clean candidate pool is GALEX UV-excess (~6 at 3 sigma).

## 3. False-match-rate reality check (the decisive skepticism item)

- **GALEX astrometric quality is the binding constraint.** Match separations: median
  0.92", 90th pct 2.2", vs WISE's median 0.14", 90th pct 0.47" for the SAME parent
  sample. GALEX's larger PSF (~4-5" FWHM) means many "matches" at 1-2.5" carry
  meaningful blend/false-match probability at G=16-18.5 depths, where the true optical
  counterpart is itself faint and GALEX's own source density is non-trivial. 66/7,191
  GALEX matches had >1 candidate counterpart within 5" (ambiguous), silently resolved
  by taking nearest.
- No independent field-density-based false-match-rate estimate was computed (e.g. via
  offset-position control fields) in this cheap gate — that is exactly the next-step
  work a full lane would need, and it is not free: at these depths GALEX AIS's own
  source density (~a few times higher than Gaia's blue tail) means a random-offset
  control test is needed before trusting any single UV-excess flag as real.
  Recommendation if greenlit: rerun the top candidates with a shifted-position (e.g.
  +30", +60") control cross-match to estimate the chance-coincidence rate directly.
- **WISE is much more reliable positionally** (median 0.14") but its W3 band is
  essentially non-detected at this depth (92% upper limits) — the "dusty/symbiotic"
  channel promised in the brief is NOT deliverable with AllWISE at G=16-18.5; would
  need unWISE/CatWISE coadds for any real depth gain, itself a scope increase.
- **Self-calibrated ridge line caveat**: the NUV-G vs BP-RP baseline was derived from
  the sample's own median (no external isochrone/model atmosphere), and 97% of the
  sample sits in a narrow BP-RP=0.55-1.15 band (G-K dwarfs) — there is almost no blue
  or very-red baseline to calibrate against, and the bins outside that core have only
  1-10 sources (statistically fragile). This is a real gate-level shortcut, not a
  publication-grade excess statistic; the "6 candidates at 3 sigma" number should be
  read as "6 objects worth a two-component SED fit," not as 6 confirmed PCEBs.

## 4. Confirmability walk-through (one hypothetical UV-excess candidate)

RV-variable (already established from DESI: multi-epoch chi2 p<1e-3, dRV>5sigma,
single-lined) + GALEX NUV excess above the MS locus for its BP-RP:
- **Is it archive-confirmable without a telescope?** Partially. A rigorous 2-component
  (cool MS + hot WD blackbody or model-atmosphere) SED fit using Gaia G/BP/RP + 2MASS
  JHK + GALEX NUV/FUV (this project already has this exact machinery, e.g.
  `scripts/wdj205650_sed_2026_05_30.py`'s `companion_excess_sigma`) CAN, in the best
  case, show the excess is well-fit by an added hot WD component and estimate its
  Teff/radius — archive-only, no new data. That is a real "PCEB candidate" outcome.
- **What it can't do archive-only**: distinguish a genuine WD companion from (a) a
  chance UV-bright interloper within the blend radius (needs deeper imaging or a
  tighter-PSF UV instrument — telescope-gated), or (b) an active chromosphere/flare
  contributing NUV excess in a single-lined RV-variable that is actually a close dMe/
  active-binary system (needs simultaneous photometry or higher-cadence UV — also
  telescope/archive-gated depending on ZTF/other survey coverage). The RV-variability
  itself is the corroborating "there IS a companion" evidence (this project's core
  asset), which is a genuine advantage over a UV-excess-alone search — but it does not
  by itself distinguish WD-companion from a stellar/active companion.
- **Net**: archive-confirmable as "candidate PCEB, SED-consistent with a hot WD
  component" — a real, if modest, deliverable. NOT confirmable as a definitive PCEB
  (would want a real spectrum, e.g. to see WD Balmer lines / Halpha, or an orbital
  period from ZTF/ASAS-SN photometry corroborating the RV period) at full rigor.

## 5. Novelty (front-filter)

- All 18,946 rows are ALREADY flagged `novel=True` by the existing pipeline's
  multi-catalog store (VSX full 10.3M rows + SIMBAD + Milliquas + binary-mass ingests),
  applied upstream of this gate.
- Independently re-checked the top 10 UV-excess-sigma candidates via a fresh SIMBAD
  cone search (5"): 0/10 have any SIMBAD entry. Consistent with the store's novel flag.
- No dedicated PCEB-catalog cross-check was run in this cheap gate (Rebassa-Mansergas
  catalogs are SDSS-selected and mostly brighter/different footprint; a real lane would
  want an explicit crossmatch against the ~2,248-object DR7 WDMS list + the
  Kruckow+2021 839-object PCEB catalog before calling anything "novel PCEB").

### Top-10 UV-excess PCEB candidates (gate output, unvetted beyond the above)

| source_id | ra | dec | gaia_g | bp_rp | NUVmag | sep(") | excess_sigma |
|---|---|---|---|---|---|---|---|
| 5097036946581138688 | 59.9413 | -17.7084 | 17.11 | 1.033 | 16.05 | 2.41 | 9.41 |
| 4416902933658832000 | 234.7205 | 1.0879 | 18.30 | 1.062 | 21.13 | 2.38 | 4.00 |
| 4440613554018885376 | 253.6129 | 5.4998 | 18.20 | 0.857 | 21.25 | 1.62 | 3.38 |
| 3057667314873438464 | 114.5377 | -4.0642 | 16.42 | 0.912 | 19.55 | 1.15 | 3.24 |
| 3667938663905524864 | 213.5187 | 3.4407 | 18.12 | 1.236 | 21.51 | 2.08 | 3.05 |
| 3251040001097677568 | 56.3686 | -2.1968 | 18.16 | 0.871 | 21.42 | 1.69 | 3.04 |
| 4356687522233455616 | 244.5269 | -4.5855 | 17.81 | 1.005 | 21.38 | 1.18 | 2.96 |
| 3195668629882699136 | 61.0946 | -8.3441 | 18.29 | 1.134 | 21.90 | 2.47 | 2.92 |
| 6225554756251615744 | 223.4506 | -26.7958 | 17.42 | 0.950 | 20.76 | 0.38 | 2.91 |
| 4395492483035648512 | 258.8135 | 9.2870 | 18.06 | 0.858 | 21.40 | 0.63 | 2.91 |

Standout: source_id 5097036946581138688 -- NUVmag=16.05 is unusually bright for a
BP-RP=1.03 (K-dwarf-like) star; GALEX detection flags are clean (no artifact flag,
star-like morphology nS/G=0.999, small positional error), separation 2.41" (not the
tightest, so blend risk is not negligible). Worth a dedicated 2-component SED fit if
this lane proceeds, BUT this is 1 object, not a population result.

## 6. VERDICT: MARGINAL

**The decisive numbers**: of the three promised channels, only GALEX UV-excess yields a
non-trivial pool (6,681 reliable matches -> ~6 candidates at a defensible 3-sigma cut),
eRASS1 is coverage-starved to 6 total matches (not a viable channel for this sample),
and WISE's promised "dusty/symbiotic" W2-W3 channel is unusable at this depth (92% W3
non-detections) -- exactly the same AllWISE-saturation/depth lesson this project
already learned in the 2026-06-05 IR-nova lane, now on the opposite (faint, not
saturated-bright) failure mode.

Reasons this is not a clean GO:
1. The UV-excess METHOD is already published and this project already ran it (NO-GO
   standalone verdict, 2026-06-05, task #121) -- applying it to a new parent sample is
   incremental, not a new discovery avenue.
2. The GALEX-side false-match risk is real and unquantified here (median separation
   0.92", no control-field chance-coincidence estimate yet) -- the brief's own
   skepticism flag. A full lane must add an offset-control test before trusting any
   individual flag.
3. The eRASS1 and WISE-dust channels promised in the brief are effectively dead at
   these depths/coverage -- only 1 of 3 advertised channels is real.
4. The surviving UV-excess pool is small (~6 candidates at 3 sigma out of 18,946) and
   each requires a proper 2-component SED fit (not just the crude ridge-line cut used
   here) before even calling it a "PCEB candidate" -- modest yield for the effort of
   building out a full lane.

Reasons it is not a clean NO-GO:
1. The DATASET (DESI-RV-selected sample) is confirmed unworked by anyone else -- no
   scoop risk beyond the single already-handled Smith 2026 object.
2. RV-variability is a genuine second piece of corroborating evidence (a real
   advantage over UV-excess-alone searches like Makarov 2017) -- a positive UV-excess
   hit on an already-RV-confirmed binary is a somewhat stronger claim than either
   signal alone.
3. A small (~6-15 object) candidate list is real, archive-confirmable (2-component SED
   fit, no telescope) work, consistent with the no-telescope-filter guardrail, and this
   project already has the SED-fit code (`companion_excess_sigma`) reusable off the
   shelf.

**Recommendation**: do NOT build a full lane/pipeline for this. If pursued at all, treat
it as a SMALL, bounded side-task: run the proper 2-component SED fit (reusing existing
code) on the ~6-15 sigma-flagged candidates only, add an offset-control false-match
check first, and frame any writeup as "a handful of DESI RV-variables with candidate
hot-WD SED excess" -- method-validation framing per the prior-art-gate rule, not a new
discovery lane. Do not invest in eRASS1 or WISE-dust channels for this sample --
coverage/depth kill them structurally.
