# Archival forensics — Rubin diaObject 170587115976392822 = ZTF19abxfaon

**Run:** 2026-07-14, rank-2 pilot stage 2 (unadopted Rubin broker flag).
**Position:** RA 326.82833, Dec -13.4747 (J2000) | l,b = 41.10, -45.00 | ecliptic lat = -0.12 deg | E(B-V) = 0.040 (LS DR10 `ebv`).
**Flag context (stage 1):** Fink/LSST `extragalactic_lt20mag_candidate`; ALeRCE LSST stamp "AGN 0.88"; m_i ~ 18.9 with 15-d slow rise + flicker; TNS cone negative 2026-07-14; no catalogued AGN/Gaia counterpart.

## Verdict: INTERESTING (real, uncatalogued, 8-year ongoing high-amplitude accretion-like variable; broker labels "AGN"/"SN" both unsupported by the archival record)

## Key identification

The Rubin transient is **not new**. It is the ongoing high state of **ZTF19abxfaon**
(ALeRCE: 491 alert detections, MJD 58732.230 - 61235.440, i.e. 2019-09-06 through
2026-07-14 — the night before this run; https://alerce.online/object/ZTF19abxfaon),
coincident within 0.3" of the LS DR10 counterpart (ls_id 10995383192785753, type PSF,
0.04" from the Rubin position). The object is in **no** catalogue of record:
TNS negative (stage-1 cone), VSX negative (VizieR B/vsx cone, 36", 0 rows),
SIMBAD negative (stage 1), no Gaia DR3 source within 10", no radio, no UV, no
mid-IR counterpart. Seven years of public alerts were never adopted by anyone.

## Timeline (all epochs MJD-keyed; full table in `photometry_master_mjd.csv`, 846 rows)

| Epoch (MJD) | Date | Measurement | Source |
|---|---|---|---|
| 56511.230-56511.240 | 2013-08-07 | r = 23.05-23.44 (5 exp., 19 min) — **deep quiescence** | DECam / NSC DR2 meas (id 121553_39) |
| 57613.119 | 2016-08-13 | z = 22.29-22.32 | DECam / NSC DR2 |
| 57956.173, 57987.094 | 2017-07/08 | g = 23.29, 23.45 — **still quiescent** | DECam / NSC DR2 |
| 58285.40 | 2018-06-16 | zr = 20.5 — **first bright detection: turn-on before this date** | ZTF DR (oid 391204300017629) |
| 58363-58696 | 2018-09 - 2019-08 | zr 20.1-21.2, rising | ZTF DR |
| 58372.098 / 58372.107 | 2018-09-11 | r = 23.13 -> 22.03 in 13 min, while ZTF saw ~20.3 three days earlier and zi=20.15 one day later — **either deep brief dips/eclipses or NSC photometry artifact** (see caveats) | DECam / NSC DR2 |
| 58732.230 | 2019-09-06 | first ZTF alert (ZTF19abxfaon) | ZTF alert stream |
| 59100-59250 | 2020 | zr median 18.9, min 18.4 — bright plateau | ZTF DR |
| 59470-59500 | 2021 | zr min **17.98** (brightest recorded), max 21.2 — 3.2-mag swings within one season | ZTF DR |
| 59800-59950 | 2022 | faint state: zr 20.1-21.7 | ZTF DR |
| 60100-60700 | 2023-2024 | active again: zr 18.3-20.6 (105 r alerts in 2024 alone) | ZTF DR + alerts |
| 60850-60900 | 2025 | faint state: zr 20.8-21.6 | ZTF DR |
| 61200-61235.44 | 2026-06/07 | re-brightened: g/r/i ~ 18.5-19.5; **Rubin flags i ~ 18.9 with 15-d rise + flicker** | ZTF alerts + Rubin/Fink flag |

**Amplitude:** r ~ 23.2 (2013 quiescence) to r = 17.98 (2021 peak) = **~5.2 mag**.
**Turn-on window:** between 2017-08-22 (g=23.45, MJD 57987) and 2018-06-16 (zr=20.5, MJD 58285).
PS1 DR2 mean-object at the position has **nDetections = 0** across 2010-2014 epochs
(stack-only entry, objID 91833268283750764) — no outburst reached ~21.5 in that window,
so the 2018 turn-on is the first recorded active state in ~8 years of prior coverage.

## Multiwavelength profile (all null except optical)

- **Gaia DR3:** 0 sources within 10" (consistent: quiescent g~23.4 during 2014-2017 Gaia epoch; `gaia_dr3_cone.csv`).
- **Radio:** NVSS (45"), FIRST (45"), VLASS QL ep.1 (45") all 0 rows (VizieR VIII/65, VIII/92, J/ApJS/255/30) -> **no radio source; disfavors blazar** at the ~0.4 mJy VLASS level.
- **Mid-IR:** CatWISE2020 + AllWISE 0 rows within 10"; LS DR10 forced W1 = 22.1, W2 = 21.8 (noise-level). One single NEOWISE-R frame (MJD 57887.61, W1=16.2) 1.4" off is a **probable passing asteroid** (ecliptic latitude -0.12 deg); no other frame detects it.
- **UV:** GALEX AIS source 7.9" away (NUV=22.7) associates with the neighbouring REX galaxy at 8.6", not the target.
- **PS1 single i=18.65 detection** (MJD 56531.398, 3.5" SE, nDet=1): probable asteroid (ecliptic plane); not the target (target was r~23 that month).
- **X-ray:** no archival X-ray claim made (position not covered by public eROSITA-DE release; not queried).

## SED anomaly resolved

The stage-1 "weird SED" (LS DR10 coadd g=23.3, r=23.1, **i=20.8**, z=21.7 with i
2.3 mag brighter than r) is **variability aliasing across coadd epochs**, not a spectral
feature: the i-band coadd epochs (e.g. MJD 58705.23, i=20.58/20.62, NSC) post-date the
2018 turn-on, while the g/r coadd epochs (2013/2017) are quiescent. No high-z-quasar or
extreme-emission-line interpretation is needed.

## Periodicity: null

Lomb-Scargle on detrended ZTF zr (272 DR points; residual sigma 0.35 mag) gives a forest
of weak alias peaks (best P=0.0951 d, power 0.126); an independent search of the dense
2024 alert season (105 r points) prefers a different period (0.0497 d) and shows no power
at the DR peak. **No reliable period; variability is stochastic flickering.** (Deep-dip /
eclipse hypothesis from the MJD 58372 DECam pair remains open but unproven.)

## Classification assessment

- **Not an artifact:** persistent LS DR10/NSC counterpart at 0.04", 491 positive-difference
  ZTF alerts over 7 yr from two ZTF fields, 346 ZTF DR direct-photometry epochs, DECam
  detections from 2013. Real astrophysical source.
- **ALeRCE-LSST "AGN 0.88" is unsupported:** no WISE IR, no radio, no X-ray record, and a
  5-mag turn-on from a 4-year-stable deep quiescent state is far outside normal AGN
  variability. A hostless extreme turn-on AGN / ambiguous nuclear transient remains
  *possible* but requires spectroscopy.
- **SN labels (ALeRCE-ZTF stamp/LC classifiers) are wrong:** 8 years of recurring outbursts.
- **Best archival hypothesis: a cataclysmic variable** that emerged from a prolonged
  low state in 2017-2018 and has cycled between high (r~18-19.5) and intermediate
  (r~20.5-21.7) states since — VY Scl-like / Z Cam-like behavior; quiescent colors
  (g-r ~ +0.1) are CV-compatible; b = -45 deg halo sightline; possible deep short dips.
- One spectrum in the current bright state (i~18.9) settles CV vs nuclear transient.

## Data caveats

1. The MJD 58372 DECam r = 23.13/22.03 pair conflicts with ZTF r~20.3 bracketing epochs;
   either the source shows >2.7-mag sub-day dips or NSC mag_auto is unreliable for these
   two exposures (c4d_180911_022036 / _023339). Verify at pixel level before citing.
2. Rubin-native photometry could not be retrieved in-session: Fink API unreachable
   (connect timeout, both api.fink-portal.org and fink-portal.org, 2026-07-14);
   ALeRCE public API has no LSST endpoint for this id (404); ANTARES cone API returned
   non-positional results (query ignored — unusable); **lasair.lsst.ac.uk exists but the
   lasair-ztf token returns 401 Invalid token** (gate result: user re-login required for
   the LSST instance). Rubin point in the master CSV is the stage-1 quicklook value,
   marked approximate.
3. ZTF alert magnitudes are difference-image PSF mags (reference contains partial source
   flux, distnr median 0.73"); ZTF DR mags are direct PSF photometry — prefer DR for
   absolute levels.

## Forced photometry status

- **ATLAS FP:** task 4541127 (submitted 2026-07-14, full history mjd>57000). If
  `atlas_fp.txt` exists in this directory the result arrived in-session; otherwise
  retrieve from the fallingstar account queue.
- **ZTF ZFPS:** submitted 2026-07-14, reqId 479166 (registered account email; jd
  2458194.5-2461236.1); IPAC queue latency hours-days; result arrives by email/wget.
  (An identical-position request reqId 479161 from earlier the same day exists — a
  sibling stage of this pilot; either result serves.)
- **DASCH:** skipped — source never plausibly V<15 (quiescent g~23.4, peak r~18.0).
- **ZFPS declination gate:** dec = -13.47 > -31 -> ran.

## Files

- `photometry_master_mjd.csv` — 846 rows, mjd+jd keyed, band/mag/magerr/source/note.
- `lightcurve_master.png` — 2013-2026 overview.
- Raw pulls: `nsc_dr2_meas.csv`, `ztf_dr_lc.csv` (+`_clean`), `ztf_alert_lc.csv`,
  `ztf_alert_nondet.csv`, `alerce_*.json`, `gaia_dr3_cone.csv`, `ls_dr10_tractor.csv`,
  `ls_dr10_detail.csv`, `nsc_dr2_object.csv`, `ps1_dr2_mean.csv`, `ps1_dr2_detections.csv`,
  `catwise2020_cone.csv`, `allwise_cone.csv`, `radio_nvss.csv`, `radio_first.csv`,
  `radio_vlass.csv`, `galex.csv`, `neowise_single.csv`, `vsx_cone.csv`, `ls_dr10_cutout.jpg`.
- Consumer package: `consumer_package/` (AstroNote draft + VSX draft + ingestion notes).

## Checkable-claim URLs

- ALeRCE object: https://alerce.online/object/ZTF19abxfaon (API: https://api.alerce.online/alerts/v1/objects/ZTF19abxfaon)
- ZTF DR LC API: https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20326.82833%20-13.4747%200.000833&FORMAT=csv
- LS DR10 viewer: https://www.legacysurvey.org/viewer?ra=326.82833&dec=-13.4747&layer=ls-dr10&zoom=15
- NSC DR2 via Data Lab TAP (`nsc_dr2.meas`, objectid '121553_39'): https://datalab.noirlab.edu/tap
- PS1 DR2: https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean.csv?ra=326.82833&dec=-13.4747&radius=0.002778
- VizieR TAP (NVSS/FIRST/VLASS/VSX/GALEX): https://tapvizier.cds.unistra.fr/TAPVizieR/tap
- ATLAS FP service: https://fallingstar-data.com/forcedphot/ (task 4541127)
- ZFPS status: https://ztfweb.ipac.caltech.edu/cgi-bin/getForcedPhotometryRequests.cgi (reqId 479166)
