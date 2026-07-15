# TNS AT (discovery) report draft — DRAFT ONLY, USER FILES

Object is NOT on TNS (cone 60" empty, re-verified 2026-07-14:
https://www.wis-tns.org/search?ra=332.39126&decl=-14.8699&radius=60&coords_unit=arcsec).
Filing this AT report makes the transient visible to spectroscopic classifiers while it is
still at i~21.5 and slowly fading (reachable by 4m+ class).

## Required TNS fields

| Field | Value |
|---|---|
| RA (J2000) | 22:09:33.902 (332.391259 deg) |
| Dec (J2000) | -14:52:11.64 (-14.869900 deg) |
| Position source | mean of 10 Rubin/LSST diaSources, scatter ~0.03" |
| Discovery date (UT) | 2026-07-07.388 (MJD 61228.3877 TAI) |
| Discovery mag | 22.30 (z, difference AB) — same night i = 21.36 |
| Discovery filter | z (LSST) |
| Reporting group | None (individual) |
| Data source | Rubin/LSST public alert stream via Lasair-LSST / Fink brokers; ZTF & ATLAS forced photometry |
| Internal name | Rubin diaObjectId 170635519425249637 |
| AT type | PSN (probable supernova) |
| Host | none catalogued; PS1 DR2 stack-only source PSO J332.3912-14.8697 at 0.71" (r=23.47+-0.19, z=22.94+-0.37, red) = candidate faint host/counterpart. Nearest Legacy DR10 source 9.9" (i-band-only coverage, 5sig depth i~23.9). |
| Last non-detection | MJD 61201.413 (2026-06-10.91), ZTF r, 3-sigma limit 21.1 (ZFPS forced photometry) |

## Remarks (suggested text)

Hostless, still-active transient from the Rubin/LSST public alert stream (diaObjectId
170635519425249637; Fink hostless_candidate/ELEPHANT flag), unreported to TNS as of
2026-07-14. Archival forced photometry recovers the full 30-day light curve: ZTF (ZFPS)
first detects the source at MJD 61206.46 (g=20.87, 4.5 sigma; r=20.83, 4.9 sigma), 22 days
before the first Rubin alert; ATLAS confirms independently at MJD 61213.28 (o=20.50, 5.8
sigma) and 61214.29 (o=20.21, 5.4 sigma). ZTF r stays ~20.7-21.0 from MJD 61206 to 61231
(plateau-like), while Rubin shows i fading 21.36->21.60 over MJD 61228-61235 with r-i ~ 0.
Historical nulls: 707 ZTF nightly stacks (2018-2026) and 1,041 ATLAS nightly stacks
(2015-2026) contain zero >4-sigma epochs before MJD 61206; no Gaia DR3, CatWISE/unWISE,
NSC DR2, or GALEX counterpart. Position stable to <0.1" across 7 days (solar-system object
excluded despite ecliptic latitude -3.3 deg). The slow rise (~5 d), ~25-day r plateau and
faint red PS1-stack candidate host favor a SN II in a dwarf host at z ~ 0.1-0.2; a CV is
disfavored (light-curve shape, no UV/quiescent counterpart to r~23.5, b=-50.5).

## Photometry to attach (AB mags; full machine-readable table in ../photometry_jd_keyed.csv)

| MJD | JD | Facility | Band | Mag / flux | Err |
|---|---|---|---|---|---|
| 61201.413 | 2461201.913 | ZTF (ZFPS) | r | >21.1 (3-sig limit) | — |
| 61206.455 | 2461206.955 | ZTF (ZFPS) | g | 20.87 | 0.24 |
| 61206.461 | 2461206.961 | ZTF (ZFPS) | r | 20.83 | 0.22 |
| 61209.456 | 2461209.956 | ZTF (ZFPS) | i | 20.18 | 0.26 |
| 61210.462 | 2461210.962 | ZTF (ZFPS) | r | 20.69 | 0.17 |
| 61213.279 | 2461213.779 | ATLAS (FP) | o | 20.50 | 0.19 |
| 61214.285 | 2461214.785 | ATLAS (FP) | o | 20.21 | 0.20 |
| 61214.455 | 2461214.955 | ZTF (ZFPS) | r | 20.72 | 0.17 |
| 61217.458 | 2461217.958 | ZTF (ZFPS) | r | 20.84 | 0.22 |
| 61228.388 | 2461228.888 | Rubin/LSST | z | 22.30 (diff) | 0.09 |
| 61228.419 | 2461228.919 | Rubin/LSST | i | 21.36 (diff) | 0.03 |
| 61228.439 | 2461228.939 | ZTF (ZFPS) | r | 20.76 | 0.24 |
| 61230.413 | 2461230.913 | ZTF (ZFPS) | r | 20.74 | 0.18 |
| 61231.415 | 2461231.915 | ZTF (ZFPS) | r | 20.65 | 0.19 |
| 61232.325 | 2461232.825 | Rubin/LSST | r | 21.33 (diff) | 0.02 |
| 61232.355 | 2461232.855 | Rubin/LSST | i | 21.39 (diff) | 0.03 |
| 61235.341 | 2461235.841 | Rubin/LSST | i | 21.57 (diff) | 0.03 |
| 61235.368 | 2461235.868 | Rubin/LSST | z | 21.95 (diff) | 0.08 |

Note: ZTF/ATLAS entries are inverse-variance-weighted nightly stacks of forced difference
photometry (quality cuts documented in ../REPORT.md); Rubin mags are per-diaSource psfFlux
(difference) with same-night pairs averaged where shown.

## Filing caveats for the user

- Rubin year-1 alert usage: alerts are distributed publicly via the selected community
  brokers; check current LSST alert-use policy language before claiming discovery credit,
  and credit "Rubin/LSST alert stream via Lasair-LSST and Fink" in the report.
- Disclose method per project policy: algorithm-found (AI-assisted archival forensics),
  human-refereed, filed by Alexander Keur.
- TNS discovery mag convention: report the first Rubin alert epoch (61228.3877) as
  discovery; the earlier ZTF/ATLAS points go in remarks/photometry as pre-discovery
  detections (they are forced-photometry recoveries, not independent discoveries).
- Calibration caution (referee, 2026-07-15): the ZFPS r "plateau" magnitudes (20.7-21.0,
  MJD 61228-61231) average ~0.4 mag brighter than Rubin r at 61232 (21.33-21.35); the
  same-epoch points agree and a plateau-end drop may contribute, but do not quote the
  ZTF-r plateau level as calibrated against LSST-r — cite each survey's own photometry.
- Label caution: the ATLAS 61213/61214 detections are pre-Rubin CONFIRMATIONS
  (post-ZTF-first-detection at 61206.46), not precursors; and the ZTF event-window
  points are mostly single exposures per night, not stacks.
