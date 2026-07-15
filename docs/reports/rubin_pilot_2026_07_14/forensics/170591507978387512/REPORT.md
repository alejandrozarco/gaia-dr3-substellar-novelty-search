# Archival forensics: Rubin/LSST diaObject 170591507978387512 (Fink ELEPHANT hostless candidate)

**Date of analysis:** 2026-07-14 (UT)
**Position (Rubin, weighted):** RA 313.2265057, Dec -14.8404352 (ICRS); raErr/decErr ~ 8 mas
**Galactic:** l = 32.58, b = -33.48 (high latitude); SFD E(B-V) = 0.059 (LS DR10 tractor `ebv`)
**Broker flag:** Fink/LSST hostless_candidate (ELEPHANT); `main_label_crossmatch = Fail` (uncatalogued)
**Analyst verdict: MUNDANE — real astrophysical transient, most consistent with a supernova at/near peak on a faint compact counterpart; the CV/precursor hypothesis was tested and rejected; nothing anomalous survives.**

---

## 1. The transient (Fink/LSST alert data)

Five diaSources over three nights (all MJD **TAI**, PSF difference-fluxes converted to AB mag;
full table in `photometry_jd_keyed.csv`):

| MJD (TAI) | UT date | band | mag_diff | mag_total | SNR | reliability |
|---|---|---|---|---|---|---|
| 61218.26954 | 2026-06-27 06:28 | z | 22.273 +/- 0.069 | 21.851 | 15.2 | 0.9991 |
| 61218.29785 | 2026-06-27 07:09 | i | 22.009 +/- 0.047 | 21.808 | 22.8 | 0.9993 |
| 61228.32610 | 2026-07-07 07:50 | i | 21.285 +/- 0.022 | 21.108 | 48.0 | 0.999997 |
| 61228.35199 | 2026-07-07 08:27 | z | 21.672 +/- 0.053 | 21.448 | 20.3 | 0.99995 |
| 61235.24740 | 2026-07-14 05:56 | i | 21.244 +/- 0.025 | 21.106 | 41.9 | 0.99999 |

- **Real:** reliability > 0.999 at every epoch; zero pixel flags (no bad/cr/streak/suspect/edge), not a dipole, not negative, `is_sso = False`, 3 different detectors (88, 152, 91) on 3 nights.
- **Light curve:** rose 0.72 mag (i) in 10.03 d, then flat (-0.04 mag) over the last 6.92 d -> rise-to-plateau over a ~17 d baseline. Blue-ish: i-z = -0.39 (diff) at MJD 61228.
- **Template counterpart exists:** Rubin (year-1 incremental) template fluxes correspond to i ~ 23.9-24.2, z ~ 23.5-23.7 -> difference amplitude ~2.9 mag above template level.
- Fink classifiers: CATS broad class 11 = **SN-like**, score rising 0.86 -> 0.99; SuperNNova SN-vs-others 0.72 -> 0.81; ELEPHANT KS-test science 0.40-0.65 (hostless-ish).

## 2. Quiescent counterpart

**Legacy Survey DR10** (Data Lab `ls_dr10.tractor`): single source `ls_id 10995375804519828`,
type **PSF**, at RA 313.226516, Dec -14.840308 — **0.476" from the Rubin transient**.
- g = 24.73 +/- 0.28 (SNR 3.9, nobs_g = 1); r = 23.72 +/- 0.15 (SNR 7.4, nobs_r = 2); **no i/z coverage at this spot in DR10 (nobs = 0)**; forced W1/W2 fluxes negative (no IR flux).
- g-r = 1.0 +/- 0.3 (weak; 1-2 exposures). LS centroid error at SNR ~7 is ~0.2"/axis, so the 0.48" offset is ~2 sigma — consistent with either coincidence with the source or a small host offset.
- Caveat: the LS DR10 "coadd" here is only 1-2 DECam exposures (epoch ~2016), so this is close to a single-epoch measurement.

**Everything else is empty within 10-15":** Gaia DR3 (nearest source 13.3", G = 17.2 — unrelated), CatWISE2020, unWISE, 2MASS, GALEX AIS, SIMBAD, VSX, Downes CV catalog, NSC DR2 object table, VLASS ep.1 / NVSS / FIRST radio. **TNS cone empty** (live web search 2026-07-14, 15" radius).

## 3. Precursor-outburst hypothesis: tested and REJECTED

PS1 DR2 contains a mean object (`90193132266371882`, nDet = 2) built from exactly two i-band
catalog detections near the position:
- MJD 55089.31201 (2009-09-15), i = 21.59, sep 0.43"
- MJD 56472.50493 (2013-06-29), i = 21.15, sep 0.75"

Taken at face value these would be ~2.5-3 mag outbursts in 2009/2013 -> recurrent dwarf nova, not a SN. Forensics:

1. **Field control (30" aperture):** 202 i-band catalog detections but only 2 real LS-DR10 sources to r ~ 24.5 in the same area -> the skycell is littered with spurious threshold detections. The junk population has psfQfPerfect ~ 0.45-0.72; genuine sources in the same data have 0.97-1.00. **Both candidate precursors have psfQfPerfect = 0.64/0.65 — junk class.** (Naive uniform-density Poisson chance of 2 junk hits within 0.8" was ~8e-4, which is why pixel-level verification was mandatory rather than statistics alone.)
2. **Same-night reproduction test (decisive):** each blip night has a second i warp minutes apart.
   Pixel-level cutouts of all four warps (`fitscut`, `i.55089_*.fits`, `i.56472_*.fits`):
   - 55089.31126 warp ("detection"): masked pixels in core, center pixel negative, no PSF profile; partner warp 55089.30380 (-7 min): SNR ~ 2.3, nothing.
   - 56472.50426 warp ("detection"): masked columns through the stamp, diffuse counts, no PSF core; partner warp 56472.51576 (+16 min): SNR ~ 0.9, nothing. A real i = 21.15 source is a 5-8 sigma detection in a single PS1 i warp — the partner warps rule it out.
   **Both PS1 blips are masked-pixel artifacts.** (Same failure mode as precovery-campaign rule 10: single-warp catalog entries that do not reproduce in same-night partner frames are not real.)

## 4. History-of-nondetections (all archives)

| Archive | Window | Depth | Result |
|---|---|---|---|
| PS1 warps (i) | 2009-07 to 2014-09, 42 warps / ~17 nights | i ~ 21.5/warp (approx) | No credible detection (2 catalog blips rejected as artifacts) |
| DECam / NSC DR2 | MJD 57523.34 (2016-05-15), g+r | g ~ 23.4, r ~ 23.0 (from faintest neighbours) | Nothing at position (quiescent) |
| ZTF public DRs (IRSA lc API) | 2018-03 to ~2025 | r ~ 20.5-21/epoch | 0 epochs — no catalog source within 4" |
| Lasair-ZTF alert archive | 2018-06 to 2026 | alert threshold ~ 20.5 | 0 alerts within 5" |
| ATLAS forced photometry | 2015-10 to 2026-07 | o/c ~ 19.5-20/epoch | task 4541137 queued 14:31 UT; see section 5 / addendum |
| DASCH | 1885-1992 | B ~ 14-15 | **Skipped, justified:** quiescence i ~ 24, observed amplitude ~3 mag -> never plausibly V < 15 |
| ZTF forced photometry (ZFPS) | — | — | **Attempted; blocked:** dec -14.8 > -31 so in footprint, but the ZFPS account is revoked (known since 2026-07-01, RESEARCH_LOG); live submission today returned "e-mail address is unknown" |

## 5. ATLAS forced photometry

Task queued 2026-07-14 14:31 UT (fallingstar-data.com, RA 313.22651 Dec -14.84044, MJD > 50000).
Result lands in this directory as `atlas_fp_raw.txt` (+ addendum note) when the queue serves it.
Expected outcome given source brightness: pure non-constraining limits (quiescence 24, outburst
21.2, both far below ATLAS single-epoch depth ~19.5); ATLAS only excludes *bright* historical
outbursts (mag <~ 19.5 sustained) over 2015-2026.

## 6. Interpretation

- **Artifact?** No. Multi-night, multi-detector, reliability > 0.999, no pixel flags, and a coincident deep-archive counterpart.
- **Solar system?** No. Recurrent position over 17 d; `is_sso False`.
- **CV / dwarf nova?** Testable prediction was archival precursors; the only precursor evidence (PS1 2009/2013) is demonstrably artifact. Remaining CV evidence is weak: PSF morphology of the quiescent source. Against: 10-day rise then plateau (DN rise is ~1-2 d), 17+ d bright phase at only ~3 mag amplitude, blue-but-not-extreme color, no GALEX UV, no WISE. Not excluded, but no positive evidence.
- **AGN?** Uncatalogued, no WISE (forced W1/W2 negative), no radio, KS-hostless. A r = 23.7 AGN flaring ~3 mag with a 10-d rise is possible but rare; no positive evidence.
- **SN (favored):** rise time, plateau at peak, i-z color, CATS SN-like 0.99, and amplitude all fit a normal SN near maximum. If Ia at peak (M_i ~ -18.7): z ~ 0.19, mu ~ 39.9 -> the LS counterpart (r = 23.7 -> M_r ~ -16.2) is a compact dwarf host, PSF-like at LS seeing/depth. The 0.48" offset (~2 sigma) fits a SN slightly offset from a compact host. A core-collapse SN at lower z on an even fainter host also fits.

**Bottom line: real, uncatalogued, probable supernova at i ~ 21.1 near peak, on/near a faint
compact source (dwarf-host candidate), not on TNS as of 2026-07-14. Precursor/CV hypothesis
tested and rejected at the pixel level. Ordinary object, clean forensic story.**

## 7. Files

- `photometry_jd_keyed.csv` — every epoch used, JD+MJD keyed, timescale column (TAI for Rubin, UTC others), detections/limits/artifact rows labelled
- `fink_object.json`, `fink_sources.json` — raw Fink/LSST API payloads
- `lsdr10_tractor.csv`, `lsdr10_full.csv`, `lsdr10_env30.csv` — Legacy Survey DR10
- `nsc_object_20as.csv` — NSC DR2 field objects (coverage tracer)
- `ps1_dr2_mean.csv`, `ps1_dr2_detections.csv`, `ps1_dr2_detections_30as.csv`, `ps1_warp_files.csv`, `i.5*_cut.fits` — PS1 evidence incl. warp cutouts
- `gaia_dr3_cone.csv`, `ztf_irsa_lc.csv` — nulls
- `annotation_draft.md` — consumer package (draft only; USER files)

## 8. Checkable sources

- Fink LSST API: https://api.lsst.fink-portal.org (POST /api/v1/objects, /api/v1/sources, diaObjectId=170591507978387512)
- Astro Data Lab query: https://datalab.noirlab.edu/query (ls_dr10.tractor, nsc_dr2.object)
- PS1 DR2 MAST: https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/ ; warps: https://ps1images.stsci.edu/cgi-bin/ps1filenames.py + fitscut.cgi
- IRSA ZTF LC API: https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves
- Lasair-ZTF cone: https://lasair-ztf.lsst.ac.uk/api/cone/
- TNS search (empty): https://www.wis-tns.org/search?ra=313.22651&decl=-14.84044&radius=15&coords_unit=arcsec
- ATLAS FP: https://fallingstar-data.com/forcedphot/ (task 4541137)
- ELEPHANT pipeline: arXiv:2605.22407 ; CATS classifier: arXiv:2404.08798 (broad class 11 = SN-like)

## Addendum (2026-07-14, end of session)

- ATLAS FP task 4541137 was still in queue at session close; background pollers were downloading
  to `atlas_fp_raw.txt`. Resume command:
  `GET https://fallingstar-data.com/forcedphot/queue/4541137/` with the token from
  `~/.config/atlas/token` (Authorization: Token ...; Accept: application/json), then GET result_url.
  Expected: non-constraining limits only (o/c ~19.5 << outburst 21.2), so no conclusion depends on it.
- ALeRCE multisurvey lookup for diaObjectId 170591507978387512 (survey_id=lsst): 404 object-not-found
  (not ingested or different id scheme); Fink is the only broker with this object exposed.
