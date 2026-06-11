# Phase-2 archival checks — 2026-06-10 (agent run)

All positions read from `docs/object_journals/` + `docs/dossiers/`; PMs confirmed against Gaia DR3 TAP
(gea.esac.esa.int) by source_id. All queries bounded; outputs in /tmp.

## Check 1 — eRASS1-DE (VizieR J/A+A/682/A34), 30" cones, PM-propagated to epoch 2019.96

Gaia DR3 astrometry (ref epoch 2016.0), propagated +3.96 yr:

| object | J2016 RA,Dec | pmra,pmdec (mas/yr) | 2019.96 RA,Dec |
|---|---|---|---|
| 2909342818326298112 (WDJ060042-293041) | 90.177943, -29.511651 | -18.798, -37.176 | 90.177919, -29.511692 |
| 6092654861665006592 (WG 26) | 212.662216, -47.744345 | -88.754, -14.586 | 212.662071, -47.744361 |

- **WDJ060042: NULL** — no eRASS1 source within 30".
- **WG 26: NULL** — no eRASS1 source within 30".
- **Positive control:** the same query at Object B (112.335086, +9.868546) returns its known eRASS1
  source at RA 112.33504, Dec +9.86852 (RADEErr 3.22") → catalog + query machinery verified; the two
  WD nulls are real catalogue nulls, not query failures.
- Interpretation: both WDs are X-ray quiet at the eRASS1 ~few×10^-14 erg/s/cm2 depth — consistent with
  detached, non-accreting double-degenerate readings.

## Check 2 — GALEX AIS (VizieR II/335) 8" cone on Object B (3161546596480983040)

- Position 112.335086, +9.868546 (J2000≈J2016; total PM 8.2 mas/yr → <0.1" over GALEX epoch offset; negligible vs 8").
- **NULL at 8"** — no AIS source.
- **Coverage check: 0 AIS sources within 5 arcmin** → the field has **no AIS tile**; the null is a
  COVERAGE GAP, not a UV non-detection. It places no constraint on a hot-WD interpretation.
  (Confirms the dossier's suspicion that the GALEX null is uninformative.)

## Check 3 — Deep pointed X-ray on Object B (cones 30")

| catalog | VizieR/TAP | result |
|---|---|---|
| 4XMM-DR13 | IX/69 | **NULL** (30") |
| 4XMM (live XSA EPIC source cat, DR14-era) | nxsa.esac.esa.int TAP, xsa.v_epic_source_cat | **NULL** (30") |
| Chandra CSC 2.1 | IX/70 (Evans+ 2024) | **NULL** (30") |
| Swift 2SXPS | IX/58 | **NULL** (30") |

- **Pointing-log check:** B/xmm (XMM obs log) and B/chandra (Chandra log to 2014): **0 pointings within
  15 arcmin** → the XMM/Chandra nulls are **no-coverage nulls** (the field was never pointed at), not
  deep upper limits. The 2SXPS null may be coverage-limited too (Swift serendipitous coverage is patchy).
- Interpretation: eRASS1 remains the ONLY X-ray detection and its 3.2" error circle the best localisation;
  a targeted Chandra/XMM position is still the missing discriminator (target vs G=13.8 neighbour).

## Check 4 — DASCH DR7 plate photometry on Object B (starglass API)

API: POST https://api.starglass.cfa.harvard.edu/public/dasch/dr7/{querycat,lightcurve} (daschlab contract). Reachable, worked.

Refcat (ATLAS-REFCAT2) within 15": three entries share gsc_bin_index 98956540:
- **ATLAS2_741709764 = Object B itself** (stdmag 18.69, pm_dec -7.6 mas/yr matches Gaia): only **3 plate
  "detections"** at mag 13.7-14.9 = the blend/neighbour mis-matched to its position. Object B (B≈18.7)
  is **below every plate limit** — DASCH cannot see it directly.
- **ATLAS2_741709765 = the G=13.8 neighbour (4.76")** — the blend tracer: 3,576 rows, **437 detections**,
  **407 with reject_flag==0**; clean baseline **median B=13.68, σ=0.34**, span **1889-12-14 → 1989-12-01**.

Blend bright-outlier analysis (candidate-outburst test):
- Epochs ≥1.0 mag brighter than baseline (clean): **7** (1903-03-26 @9.82; 1918-12-24 @11.41; 1920-01-26
  @12.44; 1924-04-30 @12.42; 1927-11-05 @12.21; 1938-03-28 @12.48; 1952-03-27 @12.42).
  Epochs ≥0.5 mag brighter: 16. (Plus 11 more ≥1 mag already auto-rejected by reject_flag.)
- **Every bright outlier sits within ~0.5 mag of its own plate's local limiting magnitude** (e.g. 9.82 vs
  lim 10.21; 11.41 vs 11.64; 12.44 vs 12.47) — the classic DASCH near-threshold false-positive signature.
- **Decisive cross-check, 1938-03-28:** three plates within 10 minutes of each other read 12.48 (ai33913)
  vs **13.74 (rh8210) and 13.58 (ac34202)** — the two simultaneous plates show the blend at baseline,
  directly contradicting the "brightening". 1927-11-05: non-detections at lim≈12.97 both 3 d before and
  3 d after the single 12.21 point. 1918-12-24: non-detection at lim 13.68 two days before the 11.41 point.
  No bright epoch is corroborated by any second plate.
- **VERDICT: NO credible outburst.** 100 yr of blend photometry is flat at B≈13.7 (σ 0.34); all bright
  outliers are uncorroborated single-plate near-limit artifacts. Caveat: an outburst of Object B itself
  would need to exceed B≈13.7 blend level (ΔB≳5 mag from quiescence, nova-like) to register at ≥0.5 mag
  over the blend — DASCH only excludes large-amplitude (nova-scale) events, not dwarf-nova-scale ones.
- Raw lightcurves: /tmp/dasch_lc_9741709765.json, /tmp/dasch_lc_9741709764.json.

## Check 5 — New archival RV epochs (1593152388271709824 + 3155543945892767232)

### 5a. VizieR V/162 (LAMOST DR11, Luo+ 2026) + V/164 (LAMOST DR5), 5" cones

**1593152388271709824** (223.469489, +49.946629):
- V/162/dr11l (LRS): 1 obs — ObsID 455703189, 2016-04-23, MJD 57501, F6 — the known LRS epoch.
- V/162/dr11m + dr11sm (MRS): 2 coadd epochs — ObsID 1125607216 (2023-06-01, MJD 60096, RVbr0=-31.50±0.42)
  and 1126507216 (2023-06-06, MJD 60101, RVbr0=-31.67±0.43) — the two known 2023 MRS epochs.
- V/164/stellar5: ObsID 455703189, HRV=-0.68±10.54 (the known low-S/N LRS RV).
- **RESULT: 3 LAMOST obs = exactly the known census; NO new LAMOST epochs.** (4th census epoch is APOGEE 2017.)
- Bonus: DR11 publishes coadd MRS RVs (-31.5/-31.7 km/s) consistent with the values used in the dossier fit.

**3155543945892767232** (112.196818, +9.794664):
- V/162/dr11l + dr11sl: 2 LRS obs — ObsID 129208159 (2013-03-01, MJD 56352, RV=31.77±2.95) and
  379215215 (2015-10-30, MJD 57325, RV=45.46±3.98). No MRS epochs.
- V/164: same 2 obs (HRV 31.78±3.65 / 45.45±3.61).
- **RESULT: 2 LRS epochs = exactly the known census; NO new epochs.** (Note DR11 e_RV 2.95/3.98 slightly
  differs from DR7's 3.65/3.61 — same RVs.)

### 5b. LAMOST DR12 public queryability

- www.lamost.org/dr12/ is live ("LAMOST DR12 v1.1") BUT all query endpoints
  (/dr12/v1.1/search cone/SQL) redirect to china-vo OAuth login → **COULD-NOT-RUN: login-gated**
  (DR12 not yet open-access internationally; not on VizieR — V/162=DR11 is the newest there).
- Action: re-check after the DR12 international release (or DR12 VizieR ingest).

### 5c. SDSS-V DR19 APOGEE allvisit (SkyServer DR19 SQL, skyserver.sdss.org/dr19)

- DR19 SkyServer SQL is publicly queryable (no auth). Table `apogee_drp_allvisit` (SDSS-V visits):
  - 1593152388271709824 (±36" box): **0 rows — NULL, no SDSS-V visits.**
  - 3155543945892767232 (±36" box): **0 rows — NULL.**
- Legacy `apogeeVisit` (DR17) sanity check: 1593152 returns exactly the known epoch
  2M14535269+4956476, MJD 57894 (2017-05-21), vhelio=-30.967±0.040, SNR 159 — census confirmed; 3155543: 0.
- **RESULT: no new APOGEE epochs in SDSS-V through DR19 for either target.**

## Check 6 — ESO raw archive (TAP http://archive.eso.org/tap_obs, dbo.raw) on HD 157033 (4111149395881722496)

- Position (dossier, J2000 PM-propagated): 260.471259, -23.815745. 120" search box
  (CONTAINS/POINT errors on dbo.raw — known geography-type quirk; used RA/Dec bounding box, RA widened by 1/cos dec).
- Instruments FEROS/HARPS/UVES/XSHOOTER/ESPRESSO: **0 rows.**
- Broadened to ALL instruments, any dp_cat, same 120" box: **0 rows** — ESO has never pointed any
  instrument at this field.
- **Positive control:** same query at Proxima Cen returns HARPS 802, UVES 1751, ESPRESSO 127,
  XSHOOTER 53, FEROS 5 → machinery verified; the HD 157033 null is real.
- Interpretation: no archival ESO high-resolution spectroscopy exists for the PMa candidate; RV
  confirmation remains telescope-gated (V≈10 — an easy FEROS/HARPS target, but nothing in the can).

## Bottom line

- 10/10 checks ran (1 sub-check login-gated: LAMOST DR12).
- New information: (i) GALEX null on Object B is a coverage gap, not a UV non-detection; (ii) XMM/Chandra
  nulls on Object B are no-coverage nulls; (iii) DASCH 100-yr blend photometry flat — no credible outburst
  (nova-scale events excluded; the 7 bright single-plate points are near-limit artifacts, one directly
  contradicted by simultaneous plates); (iv) no new RV epochs anywhere public; (v) ESO archive empty for HD 157033.
