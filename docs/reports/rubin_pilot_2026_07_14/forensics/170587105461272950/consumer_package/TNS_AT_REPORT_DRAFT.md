# DRAFT TNS AT (discovery) report — Rubin diaObject 170587105461272950 / ZTF26abfwqfp

**STATUS: DRAFT ONLY. Filing is the user's personal action via their TNS account.**
Prepared 2026-07-14 by archival-forensics pilot (algorithm-found, human-refereed; AI assistance to be disclosed in remarks per project policy).

## Why this is reportable
- Real, live SN-like transient detected independently by two public surveys
  (Rubin/LSST alerts via Fink; ZTF public alerts via ALeRCE as ZTF26abfwqfp).
- No TNS object within 10 arcsec (TNS public cone search, 2026-07-14; also negative
  per-orchestrator live check and no `xm_tns` at any of 7 Fink alert epochs).
- Neither broker pipeline adopted it: Fink flagged it hostless_candidate (ELEPHANT);
  ALeRCE stamp classifier scored it "bogus" (0.65) from marginal ZTF stamps —
  contradicted by Rubin SNR 70-83 detections with reliability = 1.0.
- Consumer: TNS AT entry makes it visible for spectroscopic classification while
  still near peak (last epoch 2026-07-14, i = 20.75).

## Form fields (TNS "Report new AT")

| Field | Value |
|---|---|
| RA (J2000) | 22:16:59.909 (334.2496225 deg) |
| Dec (J2000) | -18:12:28.611 (-18.2079475 deg) |
| Reporting group | None (personal) |
| Data source | Rubin (public alert stream, via Fink broker) + ZTF (public alert stream, via ALeRCE) |
| Discovery date (UT) | 2026-06-26.369 (MJD/TAI 61217.3685, first Rubin diaSource) |
| Discovery mag | 22.30 (LSST z, PSF difference mag, AB) |
| Filter | z-LSST (or i-LSST 22.07 at 2026-06-26.392 if a single filter is required) |
| Related files | photometry_master.csv (this package) |
| AT type | PSN (possible supernova) |
| Host | Legacy Survey DR10 REX source at RA 334.249416, Dec -18.207745, sep 1.01", g=22.88, i=22.29, z=22.62 (photo-z unavailable) |
| Last non-detection | 2026-06-25.458 (MJD 61216.4583), ZTF i > 19.75 (5-sigma diff. limit). Note: shallower than discovery mag — Rubin has no public forced photometry before first alert; treat as "last prior epoch", not a constraining limit. |

## Photometry to attach (PSF difference AB mags; MJD is TAI, midpointMjdTai)

| MJD (TAI) | UT | Filter | Mag | Err | Source |
|---|---|---|---|---|---|
| 61217.3685 | 2026-06-26 08:50:02 | z-LSST | 22.30 | 0.08 | Rubin diaSource (SNR 13.6) |
| 61217.3934 | 2026-06-26 09:25:51 | i-LSST | 22.07 | 0.04 | Rubin diaSource (SNR 26.3) |
| 61228.3666 | 2026-07-07 08:47:21 | z-LSST | 21.26 | 0.03 | Rubin diaSource (SNR 34.7) |
| 61228.3979 | 2026-07-07 09:32:18 | i-LSST | 20.75 | 0.02 | Rubin diaSource (SNR 70.2) |
| 61228.4394 | 2026-07-07 | r-ZTF | 20.46 | 0.28 | ZTF alert (ZTF26abfwqfp) |
| 61229.4178 | 2026-07-08 | r-ZTF | 20.40 | 0.27 | ZTF alert |
| 61230.4131 | 2026-07-09 | r-ZTF | 20.45 | 0.19 | ZTF alert |
| 61230.4573 | 2026-07-09 | g-ZTF | 20.42 | 0.25 | ZTF alert |
| 61231.4149 | 2026-07-10 | r-ZTF | 20.33 | 0.21 | ZTF alert |
| 61231.4575 | 2026-07-10 | g-ZTF | 20.39 | 0.24 | ZTF alert |
| 61232.3571 | 2026-07-11 08:33:35 | i-LSST | 20.56 | 0.01 | Rubin diaSource (SNR 74.4, peak) |
| 61232.3717 | 2026-07-11 | r-ZTF | 20.20 | 0.20 | ZTF alert |
| 61235.3294 | 2026-07-14 07:53:43 | i-LSST | 20.75 | 0.01 | Rubin diaSource (SNR 82.6) |
| 61235.3556 | 2026-07-14 08:31:31 | z-LSST | 21.30 | 0.05 | Rubin diaSource (SNR 23.8) |

## Suggested remarks text
> Independent recovery from public Rubin/LSST (Fink diaObjectId 170587105461272950)
> and ZTF (ALeRCE ZTF26abfwqfp) alert streams; no prior TNS entry. ~15-day rise
> (i: 22.07 -> 20.56) peaking near MJD 61232, now slowly declining; g-r ~ 0 near
> peak (hot/blue). Point-source difference detections (extendedness < 0.4, no
> dipole/streak/CR flags), 1.01" from a faint Legacy Survey DR10 REX galaxy
> (g = 22.88); Lasair Sherlock (position API): "SN", possible association with
> GALEX ASC J221659.77-181227.3 (2.4"). No counterpart in Gaia DR3 (15"),
> PS1 DR2 (< 2"), CatWISE2020/unWISE (10"), VLASS, or Milliquas; NSC DR2 DECam
> i-band epoch 2019-08-10 shows nothing to i ~ 22.2 at the position; ATLAS forced
> photometry 2015-2026 (task 4542361; atlas_fp.csv in this package, 4,525 epochs)
> shows no precursor: 0/1,023 pre-event nightly stacks at 4 sigma. MW E(B-V)_SFD = 0.027.
> Archival search and drafting AI-assisted (Claude); measurements human-reviewed.

## Ingestion path (concrete)
1. PRIMARY: TNS AT report via https://www.wis-tns.org/ -> "Report new AT" (user's
   personal TNS account; sender = user). This is the codified, named-credit channel
   and the one consumers (spectroscopic classifiers: FLEET, ePESSTO+, SCAT, ZTF/BTS)
   actually watch. Compare: same-night Rubin object 170587114058023168 became
   SN 2026uid (SLSN-I, z=0.936) only after FLEET reported it to TNS.
2. SECONDARY (after TNS name exists): Fink "anomaly"/community tag or Lasair-LSST
   annotation. GATE RESULT 2026-07-14: the ZTF-era Lasair token is REJECTED by the
   LSST instance (https://lasair.lsst.ac.uk/api -> 401 Invalid token; the hostname
   lasair-lsst.lsst.ac.uk does not serve valid TLS). User must re-register/login on
   lasair.lsst.ac.uk before any annotator path is usable.
3. NOT applicable: VSX (not a periodic variable), MPC (not moving), AstroNote
   (an AT report, not a note, is the right first artifact; a note without a TNS
   object has no anchor).
