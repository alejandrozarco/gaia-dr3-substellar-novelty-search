# DRAFT — TNS Astronomical Transient (AT) report
# Target: Rubin/LSST diaObjectId 170587105461272950 (via Fink broker)
# STATUS: DRAFT ONLY. Filing is the USER's personal action (TNS account required).
# Prepared 2026-07-14 by archival-forensics pipeline; all epochs MJD(TAI)-keyed
# (TAI-UTC = 37 s; negligible at reporting precision, UTC conversions given).

## Why file
Real, currently-active transient near/just past peak (i ~ 20.5), detected on 4
nights over 18 days by Rubin/LSST, distributed publicly by Fink, and NOT on TNS
(live cone search 10", 2026-07-14: zero matches). No pro group has adopted it
(no xm_tns at any of 7 alert epochs). A TNS AT entry is the codified path that
puts it in front of spectroscopic classifiers while it is still bright enough
to classify.

## Form fields (TNS "Report new AT")
- RA (J2000):  334.2496225  = 22:17:19.909
- Dec (J2000): -18.2079475  = -18:12:28.61
  (Rubin diaObject mean; per-epoch scatter < 0.1")
- Discovery date (UT): 2026-06-26 08:50:01  (MJD_TAI 61217.3685, first diaSource, z band)
- Discovery mag: 22.30 +/- 0.08 (AB, LSST z, difference flux)
- Filter at discovery: z (LSST)
- Reporting group: none (individual reporter)
- Data source: Rubin Observatory LSST public alert stream, retrieved via the
  Fink community broker (diaObjectId 170587105461272950); alerts are public
  per Rubin Data Policy (RDO-013).
- Discoverer(s)/internal name: [USER decides; suggest citing "Fink/LSST alert
  stream, hostless-transient (ELEPHANT) channel" in remarks]
- AT type: PSN (probable supernova)

## Photometry to attach (AB mags, LSST difference psfFlux; MJD are TAI)
| MJD(TAI)     | UT                  | band | mag    | err   |
|--------------|---------------------|------|--------|-------|
| 61217.36850  | 2026-06-26 08:50:01 | z    | 22.298 | 0.077 |
| 61217.39338  | 2026-06-26 09:25:51 | i    | 22.071 | 0.040 |
| 61228.36665  | 2026-07-07 08:47:22 | z    | 21.257 | 0.031 |
| 61228.39786  | 2026-07-07 09:32:18 | i    | 20.752 | 0.015 |
| 61232.35708  | 2026-07-11 08:33:35 | i    | 20.558 | 0.014 |
| 61235.32940  | 2026-07-14 07:53:43 | i    | 20.753 | 0.013 |
| 61235.35565  | 2026-07-14 08:31:31 | z    | 21.300 | 0.044 |
(All 7 diaSources: Rubin reliability 0.9987-1.0000, SNR 14-83, point-like,
no pixel flags, not dipoles.)

- Last non-detection: [fill from ATLAS forced photometry — see atlas_fp.txt /
  photometry CSV; ZTF public survey has zero detections at the position
  2018-2026; Rubin firstDiaSourceMjdTai = 61217.3685 implies no earlier alert
  in the 2026 campaign]

## Remarks (suggested text)
Slow riser: z 22.30 / i 22.07 on 2026-06-26, i peaks at 20.56 on 2026-07-11,
then fades 0.20 mag in i by 2026-07-14; i-z ~ -0.5 near peak (blue).
Faint candidate host in Legacy Survey DR10: REX source at RA 334.2494164,
Dec -18.2077450 (offset 1.01", ~1.4 r_e), g=22.79, i=22.25, z=22.59;
LS DR10 photo-z unconstrained. No counterpart in Gaia DR3, PS1 DR2 (>4.9"),
CatWISE2020, or NOIRLab NSC DR2 (field covered; 94 NSC objects within 2').
No precursor activity: ZTF 2018-2026 (public light curves) zero detections;
NSC DR2 (DECam, 2012-2019) empty at position; ATLAS forced photometry
[2015-2026: fill result]. Galactic b = -53.4 deg (low extinction sky).
Consistent with a young supernova in a faint dwarf host; photometric typing
is not possible from 7 points in 2 bands — spectroscopic classification
encouraged while i ~ 20.7.

## Etiquette caveat (for the USER, not for the report)
Rubin alerts are world-public and TNS accepts individual reports with proper
data-source attribution, but broker teams may operate their own TNS reporting
bots for LSST. Before filing, optionally check with the Fink team (see
fink_contact_note.md) that this object is not in their reporting queue —
double reports are merged by TNS but courtesy wins goodwill.
