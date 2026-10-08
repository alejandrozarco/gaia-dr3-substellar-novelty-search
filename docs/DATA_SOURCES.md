# Data-source registry

Append-only record of every archive / service / catalogue tried: what it holds, how to reach it, whether it worked, and
the quirks met. Read this before a new search; add a row (or a dated note) after every attempt, success or failure.
Status: OK = returned data and passed a positive control; EMPTY = no data at the position with the control OK;
FAIL = service error/timeout; HOLE = not searchable (login, embargo, no public archive, coverage gap); BLOCKED = reachable
only through a route we do not use (account registration, user-only action).

Rule of thumb (see also feedback notes): probe every service with a known object first; an empty 200 reply, a header-only
reply or a timeout is a HOLE, never a null.

## Spectra

| Source | Holds | Access | Status / last used | Quirks |
|---|---|---|---|---|
| SDSS DR17 (SPARCL) | legacy SDSS/BOSS spectra | SPARCL client (anonymous) | OK 2026-09-29 | local WD store `~/claude_projects/spectra_store/sdss_dr17_wd/`; DR16 not in SPARCL |
| SDSS DR19/DR20 (SDSS-V BOSS, APOGEE) | MWM/BHM spectra, Astra outputs, VACs | SkyServer SQL (DR20 CAS), SAS (`data.sdss.org/sas/dr20/`) | OK 2026-10-01 | Astra 0.8.1 skipped ~7k mwm_wd spectra; XCSAO velocities on WD visits can be garbage (undo per visit); LineForest H-alpha/He II unusable for CV finding; DR20 APOGEE = DR19 copy (no new APOGEE); `snr` empty for SDSS-V APOGEE visits; local visit store `~/claude_projects/spectra_store/sdssv_dr20` |
| SDSS DR20 VAC eROSITA CVs (Brink+2026) | 587 eROSITA CVs with Gaia ids | `sas/dr20/vac/mwm/white-dwarf/eROSITA_CVs/` | OK 2026-10-01 | not at CDS |
| DESI DR1 | 4.8M star spectra | SPARCL (anonymous), Data Lab | OK 2026-09-29 | no fibres in RA 300-311, Dec 30-48 (Cygnus); `desi_dr1.mws` on Data Lab is coadd-only, per-epoch RVs need the healpix rvtab files; local WD store `~/claude_projects/spectra_store/desi_dr1_wd/` (class table lacks some WDs, e.g. LP 133-754) |
| MWDD (Montreal White Dwarf Database) | literature WD spectra (e.g. Kilic MMT), DESI copies, Gaia XP | star page `spectlist.txt` + plain-text downloads | OK 2026-10-01 | found a third LP 133-754 spectrum not in any other archive; check it for every WD |
| Zenodo supplements | e.g. Kilic+2025 `allfits.pdf` (fit plots incl. spectra) | zenodo.org record files | OK 2026-10-01 | plotted spectra can be digitised from vector PDFs |
| Gaia DR3 XP | low-res mean spectra | Gaia archive datalink / GaiaXPy | OK | only G < 17.65 have sampled spectra |
| Gaia Science Alerts pages | per-epoch raw BP/RP 60-sample arrays (`var spectra`) + alert LC | `gsaweb.ast.cam.ac.uk/alerts/alert/<name>/` (HTML, parse JS vars) | OK 2026-10-01 | uncalibrated, no wavelength or epoch per array (chronological order); alert list ends 2025-01-15 |
| LAMOST LRS DR10-DR12 | low-res spectra | VO cone | OK/EMPTY 2026-10-01 | DR8/DR9 cone replies unparseable; DR12+ beyond public requires a host institution; MRS search not found |
| ESO archive | raw + phase 3 | TAP / web | OK 2026-09/10 | — |
| Keck KOA | all instruments | TAP | OK 2026-10-01 | — |
| Gemini | — | archive.gemini.edu | HOLE (login) | use the CADC mirror |
| CADC (CAOM TAP) | multi-observatory incl. Gemini mirror | TAP | OK 2026-10-01 | footprint matches can be far from the target (IGRINS-2 hit 1.5 deg away): check the target name/position |
| NOIRLab Astro Data Archive | KPNO/CTIO/WIYN | adv_search API | OK 2026-10-01 | WIYN Hydra frames can be embargoed for centuries (fibre assignments unknown) |
| MAST | HST/TESS/GALEX/PS1 | astroquery | OK | — |
| ING (WHT/INT) | ISIS etc. | CASU query | OK/EMPTY 2026-10-01 | — |
| NOT (ALFOSC/FIES/NOTCam) | — | NOT archive | OK/EMPTY 2026-10-01 | last 12 months proprietary headers |
| Liverpool Telescope | SPRAT/FRODOSpec | LT archive | OK/EMPTY 2026-10-01 | — |
| Calar Alto | — | search form | OK/EMPTY 2026-10-01 | covers 2008 to 2025-09 only |
| SMOKA (Subaru/Kiso) | — | fssearch | OK/EMPTY 2026-10-01 | — |
| TNG | — | archive box search | OK/EMPTY 2026-10-01 | — |
| IRSA SSA | Spitzer IRS, ISO, SOFIA, Herschel, IRAS-LRS | SSA | OK 2026-10-01 | IRSA ObsCore TAP returned 0 even for FU Ori (FAIL) - use SSA/SIA; IRTF spectra not searchable |
| SPHEREx QR2 | 0.75-5 um R~40-130 all-sky frames | IRSA SIA `spherex_qr2`; TAP `spherex.plane`/`spherex.artifact`; anonymous S3 section reads (astropy+fsspec, ~7 s per 100 KB) | OK 2026-10-01 (Gaia22apf: 380 frames, controls 0.93-1.04 of 2MASS/WISE) | images MJy/sr with zodi NOT removed (subtract ZODI layer); use the per-pixel `spectral_wcs` wavelength map; QR3 ePSFs (`qr3/epsf`, detector 3 v2) and `qr3/l3_flux_corrections` (multiply pre-QR3 fluxes); IBE cutout always returns the 4.9 MB PSF cube (~11 s); `/ibe/data/spherex/` listings are JS-rendered (use s3fs); `spherex.plane` lacks `dataproduct_subtype`; saturation ~AB 11.3-11.5 at 0.75-2.4 um; 6.15" pixels: fit neighbours jointly; QR3/deep empty at this position; re-run on DR1 (late 2026). Broad bands (H2O 1.4/1.9, CO 2.3, ice 3.0 um) at ~10% for 1-3 mJy; emission lines not measurable |
| MMT, LBT, HET, APO 3.5m, MDM, SAO-6m | — | — | HOLE (no public archive) | — |
| TNS object pages / spectra | classifications, public spectra | `wis-tns.org/object/<name>`; search `?ra=&decl=&radius=&coords_unit=arcsec&format=csv` | OK | Python requests with a browser User-Agent; filing only through the logged-in user browser |

## Photometry / time domain

| Source | Access | Status / last used | Quirks |
|---|---|---|---|
| ZTF DR light curves | IRSA LC API | OK | can return header-only 200s (probe a control; never cache 0 rows); 1.44" cones failed where 5" worked |
| ZTF public difference images | IRSA IBE (`ibe/search/ztf/products/sci`, `scimrefdiffimg.fits.fz`, `diffimgpsf.fits`) | OK 2026-10-01 (own forced photometry, 2,027 epochs) | ~112 epochs lack products (mostly 2022-11..2024-05); no i reference for some fields; bright neighbours leave dipole residuals - model them |
| ZTF forced-photometry service (ZFPS) | ztfweb.ipac.caltech.edu | BLOCKED since ~2026-07 (job list empty for the registered email) | results go only to the registered account email; use IBE instead |
| ZTF alerts | ALeRCE API, Lasair-ZTF | OK | Lasair keeps ~30 d; Lasair `crossmatch_tns` join incomplete (check TNS directly); ALeRCE paging can run away (cap pages); asteroids pass >= 2-detection cuts (41 s pairs) - use SkyBoT |
| ATLAS forced photometry | `fallingstar-data.com/forcedphot` (token) | OK but slow; queue stalled 2026-10-01 (positions 100-2,200; a C1 job sat at position ~210-280 for 8+ h without starting) | `m` is a difference magnitude: analyse uJy; reference-image proper-motion drift fakes trends; useless within ~3" of a star ~5 mag brighter (C1, 2026-10-02: chi/N median 58); a queued job can sit 8+ h before starting - poll by the saved task URL, never resubmit |
| Gaia DR3 epoch / vari | Gaia archive | OK | Gaia archive TAP can hang (DR4 preparation, 2026-10); VizieR I/355 as fallback |
| Pan-STARRS DR2 | MAST | OK | — |
| J-PLUS DR3/DR4 | CEFCA TAP | OK 2026-10-01 | not in VizieR (II/376 is VVV); DR4 public without login |
| TESS | MAST/lightkurve | OK | faint (G > 17) sources useless |
| NEOWISE single exposures | IRSA `neowiser_p1bs_psd` | OK 2026-10-01 | cuts cc_flags, moon_masked, nb<=1, qual_frame>0; blended in crowded fields |
| AllWISE multi-epoch | IRSA `allwise_p3as_mep` | OK 2026-10-01 | no `qual_frame` column (ORA-00904) |
| unTimely | NERSC neo7 tiles | OK 2026-10-01 (to 2020.82 only) | no cone search: whole tiles (~680 MB) |
| UKIDSS GPS multi-epoch | WSA SQL form | OK 2026-10-01 | no TAP; HTML reply with a temporary CSV link; gpsDetection has no key to gpsSource (join on an RA/Dec box); UHS not in VizieR (II/374 is something else) |
| IPHAS DR2 | VizieR | OK | VPHAS+ does not reach Dec +39 |
| ASAS-SN Sky Patrol | — | HOLE (account) | catalogue endpoint empty with control OK |
| Fink | — | FAIL (domain unreachable 2026-10-01) | — |
| PTF | IRSA | HOLE where chip gaps | — |
| Herschel Hi-GAL | IRSA | HOLE beyond l > 67.5 | one Herschel PSC table throws ORA-00904 that can be miscounted as rows |
| SCUBA-2 / JCMT | CADC TAP | FAIL (404, 2026-10-01) | — |
| Spitzer Cygnus-X | IRSA `cygx_cat`, `glimpsecygxc` | OK | SEIP can have blank IRAC columns |
| Gaia alerts CSV | `gsaweb.ast.cam.ac.uk/alerts/alert/<name>/lightcurve.csv` | OK | needs redirects followed (`curl -L`); filter null/untrusted rows |

## Catalogues / cross-match

| Source | Access | Status | Quirks |
|---|---|---|---|
| VSX | API `aavso.org/vsx/index.php?view=api.list&ra=&dec=&radius=&format=json`, `view=api.object&ident=` | OK via Python requests 2026-10-01 | curl gets a Cloudflare challenge; control AM Her; VizieR B/vsx copy can be stale; VSX accepts type Microlens |
| SIMBAD | TAP / astroquery | OK | a failed lookup returns empty (never score as 'catalogued'); measurement tables miss published values - read refs |
| VizieR | astroquery | OK | an invalid catalogue id returns an all-table cone silently |
| CDS XMatch | — | FAIL intermittently (504, 2026-10-01) | use multi-cone VizieR |
| Non-VizieR id lists | `data/external_catalogs/recent_id_lists/` | OK | Schwope+2026 eRASS1 CVs, Swan+2026 DESI DR1 WDs (+ vote log); grep by Gaia id |
| eROSITA DR1 / eRASS:3 (DR2, 2026-07-31) | eROSITA-DE archive / VizieR | OK | western Galactic hemisphere (l > 180) only |
| 5XMM-DR15 (2026-06-05) | XMM SSC | OK | — |
| LoTSS-DR3 | VizieR TAP | FAIL for joins (timeouts even for 2 rows) | batched cones work |
| OGLE EWS / KMTNet alert lists | web lists | OK 2026-10-01 | OGLE EWS paused 2020-21 |
| ADS | API (token) | OK | full text misses source ids in tables; arXiv sources by grep |
| ATel | astronomerstelegram.org | OK (crawl by number) | not indexed by ADS full text |

## Access not used (would need a new account - user decision)

S-PLUS DR5, Lasair-LSST personal token, Rubin data-rights products (DP2/EDP2), LAMOST beyond the public release.

## Notes 2026-10-05 (fresh transient sweep)

- SkyBoT: object names can contain "|" (e.g. G!kún||'hòmdímà), which breaks a pipe-split parse - take the separation as the 5th field from the right. The service can crash on a request (SIGBUS) while other requests answer.
- ALeRCE: detections from an alert's previous-detection history carry no drb score, so a drb >= 0.8 cut drops them; stamps at `avro.alerce.online/get_stamp?oid=&candid=&type=&format=png|fits`; the `/forced_photometry` endpoint returns 404; non-detections after the last alert are not reported (coverage unknown).
- Lasair-ZTF: `jdmin` is the first alert inside its ~30-day window, not the true first detection (old AGN/variables appear "fresh"); its TNS join missed 15 of 37 reported objects in this sweep.
- TNS search: 20 s between requests drew 429s with 5-min waits; 30 s ran clean (~31 s per object).
- ATLAS forced photometry: jobs waited 13-21 h on 2026-10-01; not usable for same-day vetting.

## Note 2026-10-07: ATLAS times are exposure START

- ATLAS forced-photometry `MJD` is "Modified Julian date of the start of the exposure (all exposures are 30s). [Not corrected to Solar System barycentre]" (fallingstar-data.com/forcedphot/resultdesc/). Add +15 s before barycentring. Periods are unaffected; epochs/eclipse times from ATLAS-only fits are 15 s early. Found by a leave-one-season-out test (WDJ0303-4206: ATLAS eclipses 8-25 s early vs TESS until corrected). Affected epochs to re-derive: WDJ1118-5442 (corrected 2026-10-07), WDJ0303-4206 (public white-dwarfs-2026 eclipse script), J0353, J0753, J1949 (valley EB), and any other ATLAS-based T0.
- 2026-10-07 follow-ups: Gaia epoch-photometry `TimeG + 2455197.5` is BJD in TCB, not TDB (~19 s offset at present); ZTF IRSA light-curve `mjd` start/mid convention not yet verified.
- 2026-10-07 sweep quirks: SkyBoT returns HTTP 204 with an empty body when no asteroid is in the cone (not a failure); NED redshift flag "PUN" is not treated as spectroscopic; TNS discovery dates can precede the first ZTF alert (other surveys' detections count).
- 2026-10-07 planet-search quirks: VSX API returns a Cloudflare 403 to Python requests with a browser User-Agent but works with the default python-requests User-Agent; NASA Exoplanet Archive TAP rejects `contains(point, circle)` (403 HTML) - use RA/Dec boxes; QLP HLSP files at hlsps/qlp/sNNNN/<tic16 split 4/4/4/4>/..._llc.fits (S105: 200 s, DET_FLUX), target lists in target_lists/; TESS-SPOC HLSP stops at S85, SPOC 2-min at S107 (2026-10); large TAPVizieR uploads to IV/39 hang - use MAST Catalogs.query_criteria(ID=list) in chunks of 2,000; ExoFOP TOI table newest alert 2026-08-27 (QLP TOIs to S98, SPOC to S102).
- 2026-10-07 alert streams: Fink reachable again at new hosts api.ztf.fink-portal.org (ZTF nights to 20261007) and api.lsst.fink-portal.org (LSST last night 20260714) - supersedes the 2026-10-01 "Fink FAIL"; ANTARES REST api.antares.noirlab.edu/v1/loci works anonymously (ZTF + LSST ids only); LS4 alerts not public (SCiMMA/Hopskotch account needed, no broker carries them, 0 LS4 TNS reports in 2026) - re-check monthly (ANTARES survey ids, BOOM src/alert/ls4.rs, TNS group); BlackGEM, GOTO, ATLAS, WFST have no public streams and auto-report to TNS (no first-filer credit there).
- 2026-10-07 (evening): VSX API returned Cloudflare 403 to Python requests even for the AM Her control (both User-Agent variants failing at times); the browser at vsx.aavso.org worked. Treat VSX API failures as HOLES and fall back to the browser or the VizieR B/vsx copy. Several VizieR ids for 2024-2026 sdB pulsator papers do not exist and return all-catalogue dumps (J/A+A/686/A65, 700/A71, 673/A90, 686/A126, 651/A121, J/PASA/43/106).
- 2026-10-07: ZTF IRSA light-curve `mjd` is also the exposure START (hjd - heliocentric(mjd) = 15.00 s on every row tested; 30-s exposures): add exptime/2 before barycentring. ZTF-based epochs before this date are 15 s early (periods fine). Gaia DR3 epoch photometry times are TCB (convert to TDB).

- **MAST short-cadence coverage by TIC id (2026-10-08):** a TIC-id query misses SPOC 2-min/20-s data filed under a duplicate TIC (TIC 10011123 has S33/S87 2-min + S87 20-s under TIC 10011121). Check coverage by position (~15" cone) instead. TESS 2-min target lists for S111+ not yet released (404). SIMBAD returned 503 (maintenance) on 2026-10-07/08; the mirror also failed.

- **ZTF Forced-Photometry Service (2026-10-08):** a request filed 2026-10-01 completed and emailed on 2026-10-08 (~7 days). Download uses the generic HTTP login published in the ZFPS documentation (not the account password). Near a bright neighbour (2.56", 5 mag brighter) the forced PSF fit is dominated by subtraction residuals (median chi2 ~110), no better than own IBE photometry.
- **ALeRCE objects API:** `/ztf/v1/objects?ra=..` (no trailing slash) returned an empty body on 2026-10-08; `/ztf/v1/objects/?ra=..` works.
