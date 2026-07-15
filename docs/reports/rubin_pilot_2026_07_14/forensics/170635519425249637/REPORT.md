# Archival forensics: Rubin/LSST diaObject 170635519425249637

**Date:** 2026-07-14 | **Position:** RA 332.39126, Dec -14.8699 (J2000; +-~6 mas over 10 epochs)
**Galactic:** l=42.60, b=-50.48 | **Ecliptic lat:** -3.28 deg | **Field:** LSST WFD "lowdust", observation_reason `pairs_iz_33.0`
**Broker flag:** Fink hostless_candidate (ELEPHANT) | **Verdict: INTERESTING**

## Headline

Real, still-active, unreported extragalactic-transient candidate with a **30-day,
three-survey forced-photometry light curve**. ZTF/ZFPS first detects it at MJD 61206.46
(g 4.5 sigma + r 4.9 sigma, same night) — **22 days before Rubin's first alert** — with the
rise bracketed by a clean r non-detection at 61201.41. ATLAS independently confirms at
MJD 61213.28 (o=20.50+-0.19, 5.8 sigma) and 61214.28 (o=20.21+-0.20, 5.4 sigma). Historical
control: 0/660 ZTF and 0/1,039 ATLAS pre-event nightly stacks exceed 4 sigma (2015-2026).
Rubin caught the object post-peak. TNS cone (60") is empty - re-verified live today
(https://www.wis-tns.org/search?ra=332.39126&decl=-14.8699&radius=60&coords_unit=arcsec).
Light-curve shape (~5-d rise, ~25-d r plateau at 20.7-21.0, slow i fade, late g-r
reddening), r-i ~ 0, SN-like broker scores, and a red PS1-stack-only candidate host at
0.71" (r=23.47) make a **SN II at z~0.1-0.2 in a faint dwarf host** the leading
interpretation (plateau disfavors Ia; shape+no UV/quiescent-blue counterpart disfavor CV).

## Rubin alert record (via Fink LSST API; MJD TAI, AB mag = 31.4 - 2.5 log10(nJy))

| MJD | band | diff mag | sci mag | SNR | reliability |
|---|---|---|---|---|---|
| 61228.3877 | z | 22.30 | 21.94 | 11.3 | 0.996 |
| 61228.4188 | i | 21.36 | 21.28 | 38.7 | 1.000 |
| 61232.3248 | r | 21.33 | 21.26 | 44.6 | 1.000 |
| 61232.3267 | r | 21.35 | 21.27 | 38.7 | 1.000 |
| 61232.3541 | i | 21.40 | 21.33 | 23.6 | 1.000 |
| 61232.3560 | i | 21.38 | 21.31 | 32.3 | 1.000 |
| 61235.3406 | i | 21.54 | 21.41 | 42.6 | 1.000 |
| 61235.3415 | i | 21.60 | 21.42 | 42.5 | 1.000 |
| 61235.3677 | z | 21.89 | 21.68 | 14.1 | 1.000 |
| 61235.3686 | z | 22.21 | 21.98 | 6.4 | 0.906 |

10 diaSources, 3 nights, positionally stable to ~6 mas (ALeRCE sigmara/dec ~ 1.8e-6 deg)
-> **solar-system object excluded** despite ecliptic latitude -3.3 deg. isDipole/isNegative all
False. Fink CATS broad class = 11 = "SN-like" (mapping verified in fink-broker source,
`fink_broker/rubin/science.py` mapping_cats_general: 0:"SN-like"->11), score 0.87-0.90;
snnSnVsOthers 0.72-0.80.

**Broker disagreement diagnosed:** ALeRCE `stamp_classifier_rubin_beta` v201 says bogus 0.90,
but its own successor v202 (20260421) says asteroid 0.81 / bogus 0.17. Two beta stamp models
contradicting each other on the same stamps, while the lightcurve-level evidence (10 epochs,
SNR up to 44, mas-stable) is unambiguous -> the disagreement reflects year-1 stamp-model
immaturity, not the data. Fink per-source reliability 0.91-1.00.

**Template-residual note:** scienceFlux - psfFlux(diff) is positive in all 10 epochs
(~600-1750 nJy ~ 23.3-24.4 AB) -> either a real underlying ~24 mag source, or transient light
baked into the incremental year-1 template. Since ATLAS shows the transient bright on
MJD 61213-61217, template contamination is possible if template epochs include late June 2026;
provenance not exposed in the alert. Treat as a hint, not a measurement.

## ATLAS forced photometry (fallingstar; token job 4541122; 4,841 epochs MJD 57227-61235)

- Quality cuts: chi/N < 10, err flag 0, 0 < duJy < 100; nightly inverse-variance stacks
  (n>=2), keyed by weighted-mean MJD (asserts on epoch ranges; no positional alignment).
- **1,041 nightly stacks over 11.0 yr; SNR distribution mean -0.07, sigma=1.16; exactly 2 nights
  exceed 4 sigma and both are in the pre-Rubin window:**

| mean MJD | band | n | flux (uJy) | SNR | mag AB |
|---|---|---|---|---|---|
| 61213.279 | o | 8 | 22.8+-3.9 | 5.8 | 20.50+-0.19 |
| 61213.465 | c | 5 | 14.4+-5.1 | 2.8 | 21.00 |
| 61214.285 | o | 4 | 29.8+-5.6 | 5.4 | 20.21+-0.20 |
| 61214.582 | c | 4 | 15.6+-5.0 | 3.1 | 20.92 |
| 61216.292 | o | 4 | 23.1+-6.5 | 3.6 | 20.49 |
| 61217.249 | o | 4 | 29.1+-8.6 | 3.4 | 20.24 |

  At the Rubin discovery epochs ATLAS stacks give 7-11 uJy at 0.5-1.5 sigma - consistent with
  the o-equivalent of i~21.3. Preceding nights: 61210.55 o 11.1+-5.4 (2.1 sigma) -> rise was
  fast (few days or less) or just below stack depth.
- **Prior-outburst null:** the 4 historical single-exposure spikes (MJD 58462.27 c 17.3,
  58660.63 o 15.1, 58826.24 o 16.4, 58830.20 o 18.3) all FAIL same-night reproduction -
  absent in 3-8 flanking exposures minutes apart, PSF-fit chi/N 85-3043 -> artifacts/movers
  (ecliptic lat -3.3 deg). No genuine precursor activity 2015-07 -> 2026-06.

## ZTF forced photometry (ZFPS reqId 479165 — COMPLETED 2026-07-14 10:10 UT, downloaded and analyzed)

- 1,084 epochs JD 2458268.94-2461234.94 (MJD 58268.4-61234.4), g/r/i. Quality cuts
  (infobitssci=0, scisigpix<25, seeing<4"), fluxes to AB uJy via per-epoch zpdiff, nightly
  inverse-variance stacks keyed by weighted-mean MJD -> **707 nightly stacks**.
- **INDEPENDENT CONFIRMATION + RISE RECOVERY: 12 stacks exceed 4 sigma and ALL fall in
  MJD 61206-61231; zero >4-sigma nights in 660 historical stacks 2018-2026 (max 2.5 sigma).**

| mean MJD | band | flux (uJy) | SNR | mag AB |
|---|---|---|---|---|
| 61206.455 | g | 16.2+-3.6 | 4.5 | 20.87 |
| 61206.461 | r | 16.9+-3.4 | 4.9 | 20.83 |
| 61209.456 | i | 30.8+-7.4 | 4.2 | 20.18 |
| 61210.420 | g | 15.7+-3.7 | 4.3 | 20.91 |
| 61210.462 | r | 19.3+-3.0 | 6.3 | 20.69 |
| 61214.455 | r | 18.7+-2.9 | 6.4 | 20.72 |
| 61217.458 | r | 16.8+-3.4 | 5.0 | 20.84 |
| 61228.439 | r | 18.0+-3.9 | 4.6 | 20.76 |
| 61229.418 | r | 14.6+-3.4 | 4.2 | 20.99 |
| 61230.413 | r | 18.4+-3.1 | 5.9 | 20.74 |
| 61231.415 | r | 19.9+-3.4 | 5.8 | 20.65 |
| 61231.458 | g | 13.2+-3.0 | 4.4 | 21.10 |

- **Rise bracketed:** last clean non-detection MJD 61201.413 (r, 3-sig limit 21.1); marginal
  2.4-3.0-sigma flux already at 61203-61205 (g/i/r); first >4-sigma 61206.46 (g+r same
  night, coherent) — i.e. detection 22 days before the first Rubin alert.
- **Shape:** ZTF r stays 20.65-20.99 from 61206 through 61231 (~25-day plateau) while g
  fades relative to r (late g-r ~ +0.45). ZTF reference epochs end 2018 (refjdend ~2458444)
  -> no template contamination on the ZTF side.
- ZTF alert archive (ALeRCE cone 15"): only ZTF21ablcehn, a single-detection (ndet=1) object
  at 6.6" offset, MJD 59407.33 (2021-07-12) - unrelated junk by the ndet=1 rule.
  Lasair-ZTF cone (15"): empty. (ZTF never alerted in 2026: single-epoch diff SNR ~4-6 is
  below the 2-detection alert bar — exactly why forced photometry was needed.)

## Host / counterpart forensics

| Archive | Result |
|---|---|
| Legacy Survey DR10 (Data Lab ls_dr10.tractor) | Nearest source 9.92" (REX i=22.29); second 10.61" (REX i=21.50 = the CatWISE/unWISE source). **Field is i-band-only** (nobs g/r/z = 0, nobs_i=4), 5-sigma PSF depth i~23.91 -> "hostless" is an i-band statement; a red host can hide. |
| NSC DR2 (Data Lab) | 0 objects within 30" (coverage real: 39 objects/2', 760/6') -> no DECam-era (~2013-2019) detection at position. |
| PS1 DR2 mean/detections | No detection at the position (<0.7") in any single epoch 2010-2014. Two nDet=1 entries at 1.49" (i=21.41, MJD 56912.417) and 2.25" (r=20.30, MJD 56247.218) lie in different directions in a junk-dense field -> not prior outbursts of this source. |
| **PS1 DR2 stack** | **Stack-only source 0.71" away** = PSO J332.3912-14.8697 (objID 90153323911726695), primaryDetection=1: g=23.99+-0.31, **r=23.47+-0.19 (5.7 sigma)**, i=23.95+-0.33, z=22.94+-0.37, y=22.60+-0.80; ng..ny=0 (never seen in single epochs). Solid in r, red overall - candidate quiescent counterpart or dwarf host, invisible to DR10's i-only coverage. (Re-verified stage 2 via MAST stack API.) |
| Gaia DR3 | Nothing within 21" (nearest: G=19.7 star at 21.2"). |
| CatWISE2020 / unWISE | Nothing within 10.5" (nearest = the 10.6" REX). No IR AGN counterpart. |
| GALEX GUVcat | Nothing within 15" - no UV source (mildly disfavors CV). |
| SIMBAD | Empty within 30". |
| DASCH | **Skipped by policy** - object never plausibly V<15 (peak o~20.2). |
| TNS | Empty within 60", re-verified live 2026-07-14. |

## Interpretation

- **Real astrophysical transient:** yes, beyond reasonable doubt (10 epochs / 3 nights /
  mas-stable + independent ATLAS 5.8+5.4 sigma pre-discovery detection at the same position).
- **Timeline:** rise within a few days before MJD ~61213; peak o~20.2 around MJD 61214-61217;
  decline ~0.08 mag/d to i~21.3 by 61228, slowing to ~0.03 mag/d (i) by 61235. Fast-then-slow
  decline is SN-like; classic dwarf-nova declines do not flatten at +2 weeks.
- **Class:** SN II (plateau) at z~0.1-0.2 in a faint dwarf host is the best fit: the
  ~25-day ZTF r plateau at 20.65-20.99 rules against a Ia (which fades ~1 mag in r over
  +17 d past peak); peak r~20.7 -> M_r ~ -17.6 at z~0.1, and the PS1-stack host candidate
  (r=23.47, z=22.94) -> M_z ~ -15.4 dwarf, consistent. A halo dwarf nova (quiescence r~23.5,
  amplitude ~2.8 mag) is strongly disfavored: 30+ day flat-topped outbursts are not DN-like,
  no UV/GALEX source, b=-50 CV density. AGN/TDE disfavored: no WISE counterpart, no
  variability in 11 yr of ATLAS + 8 yr of ZTF forced photometry.
- **Why unadopted:** hostless -> skipped by host-targeted SN workflows; ALeRCE beta stamp
  classifier called it bogus/asteroid; nobody reported to TNS. This is exactly the
  "unadopted-tail" population the lane targets.

## Honest caveats

1. ~~ZFPS is the confirming dataset~~ **RESOLVED: ZFPS confirms** — 12 independent ZTF
   nightly detections spanning MJD 61206-61231, same position, zero historical false
   positives in 660 control nights. The ATLAS pre-discovery detection is no longer the
   load-bearing evidence.
2. z-band first-epoch color (i-z ~ -0.9) is bluer than typical SNe; single 11-sigma z point,
   noisy z pair on 61235 (1.9 sigma internal scatter) -> colors indicative, not precise.
3. The 0.71" PS1 stack counterpart is 3-4 sigma per band and stack-only; could be noise.
4. Rubin template provenance unknown -> template-residual "host" hint is degenerate with
   template contamination by the transient itself.

## Files

- `photometry_jd_keyed.csv` - **1,760 rows**, every row keyed by MJD+JD (asserted offsets
  and anchor-row asserts): 10 Rubin epochs (Fink/Lasair cross-checked), 1,041 ATLAS nightly
  stacks, **707 ZTF ZFPS nightly stacks**, 2 flagged offset PS1 detections.
- `atlas_fp_parsed.csv` (4,841 raw epochs), `atlas_nightly_stacks.csv`
- `zfps_req479165_lc.txt` (raw ZFPS), `zfps_req479165_good.csv` (777 quality-cut epochs),
  `zfps_nightly_stacks.csv` (707 stacks)
- `lsst_photometry_mjd.csv` (10 diaSources incl. per-epoch ra/dec, from public Lasair-LSST
  object page), `lasair_object_page.html`
- `fink_object.json`, `fink_sources.json`, `alerce_lc.json`, `datalab_catalogs.json`,
  `catalogs.json`, `catalogs2.json`, `catalogs3.json`, `ps1_detections_3as.csv`,
  `ps1_dr2_stack_3as.csv`, `ps1_dr2_mean_30as.csv`, `lsdr10_30as.csv`, `nsc_dr2_30as.csv`,
  `gaia_dr3_30as.ecsv`
- Consumer package: `consumer_package/TNS_AT_report_draft.md` (primary path),
  `consumer_package/lasair_annotation.txt`, `consumer_package/README_ingestion.md`

## Stage-2 verification pass (2026-07-14 evening, independent re-run)

A second session re-ran the stack from scratch and verified the stage-1 claims:

- **ATLAS stacks reproduced exactly** from `atlas_fp_parsed.csv` with independent code:
  1,041 stacks, only 2 nights >4 sigma (61213.279 o 5.79 sig; 61214.285 o 5.37 sig),
  SNR distribution mean -0.07 / sigma 1.17. Anchor rows asserted by MJD+band.
- **Rubin photometry cross-checked across brokers:** the public Lasair-LSST object page
  (https://lasair.lsst.ac.uk/objects/170635519425249637/) embeds all 10 diaSources; values
  match the Fink-derived table to the last digit. Per-epoch positions: RA/Dec spread 0.09"
  over 6.98 d (keyed by diaSourceId with asserts after catching a blob-order/mjd-order
  misalignment - the positional-alignment bug class struck again and was caught).
- **TNS cone re-verified empty** (0 result rows, live 2026-07-14 ~19:45 UT).
- **PS1 stack counterpart re-verified** via MAST `stack` catalog (see host table).
- **ZFPS results retrieved and analyzed** (the decisive new dataset; section above).
- Gate results logged: lasair-ztf token = 401 on lasair-lsst API (fresh registration
  needed for the annotation path); api.fink-portal.org unreachable from this network
  tonight (stage-1 used api.lsst.fink-portal.org successfully at 16:32 local); ALeRCE v2
  lightcurve API does not accept an "lsst" survey_id (only ztf) as of tonight.
- Housekeeping: duplicate ATLAS task 4542396 cancelled before running; duplicate ZFPS
  reqId 479183 (submitted before stage-1's completed 479165 was discovered) left to expire.

## Data sources (URLs)

- Fink LSST API: https://api.lsst.fink-portal.org/api/v1/objects and /api/v1/sources
  (main api.fink-portal.org unreachable today; LSST instance verified live)
- ALeRCE client (survey='lsst' and 'ztf'): https://alerce.readthedocs.io/
- ATLAS FP: https://fallingstar-data.com/forcedphot/ (task 4541122)
- ZFPS: https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi (reqId 479165, completed 2026-07-14 10:10 UT; lightcurve retrieved)
- Astro Data Lab (ls_dr10.tractor, nsc_dr2.object): https://datalab.noirlab.edu/
- PS1 DR2 (MAST): https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/
- Gaia DR3 (ESA TAP), VizieR II/365 (CatWISE2020), II/363 (unWISE), II/335 (GUVcat)
- TNS live cone: https://www.wis-tns.org/search?ra=332.39126&decl=-14.8699&radius=60&coords_unit=arcsec
- CATS class mapping: https://raw.githubusercontent.com/astrolabsoftware/fink-broker/master/fink_broker/rubin/science.py
