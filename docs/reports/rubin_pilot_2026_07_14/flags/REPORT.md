# Rubin/LSST broker-flag harvest + Gate 1 (year-1 artifact/genuine ratio)

Rank-2 pilot, stage 1. Run date: 2026-07-14 (UTC). All times keyed by explicit MJD/JD (TAI midpoint,
`midpointMjdTai`); JD = MJD + 2400000.5. Harvest window: `startdate=2026-07-07`, `stopdate=2026-07-14`
= nights MJD 61228-61235 (2026-07-07 ... 2026-07-14). Every alert in the sample carries an assert
`61227 < MJD < 61236`.

## 1. Endpoint survey (what actually works for Rubin/LSST alerts)

| Broker | Status | Base URL / query form |
|---|---|---|
| **Fink/LSST** | **WORKING, primary harvest source** | `https://api.lsst.fink-portal.org` (Swagger at root). Channel query: `GET /api/v1/tags?tag=<tag>&startdate=YYYY-MM-DD&stopdate=YYYY-MM-DD&n=<max>&columns=...` (default n=10 - must raise it; server 504s on very large windows, chunk per-night). Tag list: `GET /api/v1/tags` (no args). Others used: `/api/v1/objects?diaObjectId=`, `/api/v1/sources?diaObjectId=`, `/api/v1/cutouts?diaObjectId=&diaSourceId=&kind=Science|Template|Difference&output-format=PNG`, `/api/v1/schema?endpoint=/api/v1/objects`. |
| **ALeRCE/LSST** | **WORKING, secondary** | `https://api-lsst.alerce.online/` (found in alerce_client `default_config.json`; not in the readthedocs prose). `GET object_api/list_objects?survey=lsst&ra=&dec=&radius=&page_size=` (note: param is `survey`, not `survey_id`; trailing-slash 308s; bare `/objects` 404s). Returns `stamp_classifier_rubin_beta` v2.0.1 class + probability. Stamps at `https://api-lsst.alerce.online/stamps_api`. |
| **Lasair-LSST** | **UNREACHABLE - token gate NOT testable** | `lasair-lsst.lsst.ac.uk` resolves (192.41.122.53) but TCP connect times out (tested twice, 40 s connect timeout); `lasair-ztf.lsst.ac.uk` equally down. So this is a service/network outage on 2026-07-14, **not** a token rejection; whether the old ZTF token authenticates on the LSST instance remains an open gate. Token was read but never transmitted anywhere that responded. |
| SkyBoT (IMCCE) | DOWN today | `vo.imcce.fr/webservices/skybot/skybotconesearch_query.php` - every cone (45-120 s timeouts) failed. SSO check fell back to Rubin's own MPCORB association (`ssObjectId`, Fink `f:is_sso`) + multi-night positional persistence (a diaObject groups detections within ~1 arcsec; >=2 distinct nights at fixed position excludes movers physically). |
| TNS (public search, no auth) | WORKING but rate-limited | `https://www.wis-tns.org/search?ra=&decl=&radius=10&coords_unit=arcsec` (HTML scrape; 429s unless >= ~45 s between queries). Positive control: recovered SN 2026pec at the expected position. |
| Legacy Survey DR10 | WORKING | NOIRLab Datalab TAP sync `https://datalab.noirlab.edu/tap/sync`, `LANG=ADQL`, plain box predicate on `ls_dr10.tractor` (`ra BETWEEN ... AND dec BETWEEN ...`); ADQL geometry (`CONTAINS/POINT/CIRCLE`) and `q3c_radial_query` both fail to translate on that service. |

**Fink/LSST tags with API support** (from `GET /api/v1/tags`): `hostless_candidate` (ELEPHANT,
arXiv:2404.18165), `extragalactic_new_candidate`, `extragalactic_lt20mag_candidate`, `most_likely_sn`,
`sn_near_galaxy_candidate`, `in_tns`. **There is no dedicated "anomaly" tag on the LSST instance**
(unlike Fink/ZTF's `/api/v1/anomaly`); the closest oddball feeds are `hostless_candidate` +
`extragalactic_new_candidate`, which is what we harvested.

## 2. Harvest totals (alerts per channel per night)

Nights with flags: MJD 61228 (Jul 7), 61230 (Jul 9), 61231 (Jul 10), 61232 (Jul 11), 61233 (Jul 12),
61234 (Jul 13). MJD 61229 (Jul 8) had zero alerts in every channel (likely weather/engineering).

| channel | total alerts | unique objects | per-MJD breakdown |
|---|---|---|---|
| hostless_candidate (ELEPHANT) | 15 | 10 | 61228:4, 61230:2, 61232:8, 61233:1 |
| extragalactic_new_candidate | 717 | 702 | 61228:30, 61230:181, 61231:275, 61232:150, 61233:71, 61234:10 |
| extragalactic_lt20mag_candidate | 40 | 26 | 61228:3, 61230:11, 61231:15, 61232:6, 61233:5 |
| sn_near_galaxy_candidate | 4,704 | - | 61228:470, 61230:2039, 61231:85, 61232:1237, 61233:873 |
| in_tns | 3,822 | - | 61228:783, 61230:1230, 61231:546, 61232:623, 61233:472, 61234:168 |
| most_likely_sn | >=80,648 (4 nights measured) | 73,457 | 61231:16559, 61232:10410, 61233:5530, 61234:48149; Jul-07/09 windows 504'd |

**Monitored oddball channels (our science feed): 15 + 717 + 40 = 772 alerts / 738 unique objects.**

## 3. Gate 1 measurement - artifact/genuine ratio

**Sample:** 40 unique objects. Census of ALL 10 hostless_candidate objects + random (seed 20260714)
20/702 extragalactic_new + 10/26 extragalactic_lt20mag. Vetting per object:
(a) Fink PNG cutouts Science/Template/Difference, visually inspected (montage_0-3.png);
(b) LS DR10 deep-coadd host check (10 arcsec box, nearest-source separation + tractor type);
(c) Gaia DR3 crossmatch (Fink `xm_gaiadr3` name/parallax/VarFlag);
(d) SSO check: Rubin `ssObjectId` + Fink `is_sso` + multi-night persistence (SkyBoT down, see sec.1);
(e) duplicate/ghost: alert multiplicity per diaObjectId, `isDipole`, `isNegative`, `glint_trail`, all 20 `pixelFlags_*`;
(f) lightcurve trend from `/sources` (MJD-keyed, sorted-assert).

**Result (n = 40):**

| bucket | n | fraction |
|---|---|---|
| ARTIFACT (subtraction residual on static star: weak/offset diff smudge, star present in both science+template, mag 22-24, ndet 1-3) | 15 | 37.5% |
| GENUINE transient (clean positive PSF in diff, empty/host template, multi-night, reliability ~1.0) | 13 | 32.5% |
| GENUINE non-transient astrophysical (AGN 5, stellar outburst 3, variable star 2) | 10 | 25% |
| AMBIGUOUS (single-night faint on-galaxy pair; mover not excludable) | 2 | 5% |

**Artifact : genuine ~ 15 : 23 ~ 0.65 overall -> genuine fraction 57.5% (transient-genuine 32.5%).**

The ratio is strongly channel-dependent - this is the actionable finding:

| channel | artifacts | genuine | note |
|---|---|---|---|
| hostless_candidate | **0/10** | 10/10 | every flag a clean multi-night (2-5 nights, 7-18 d span) transient, reliability 1.00, zero pixel flags, zero negatives |
| extragalactic_lt20mag (bright) | 0/10 | 10/10 | but only ~4/10 are transients; rest AGN/variable stars |
| extragalactic_new faint tail (mag>21.8) | **15/20** | 3/20 (+2 ambig.) | the year-1 incremental-template junk lives here: low-amplitude residuals on stars that ARE in the template |

Cross-broker caveat: ALeRCE's beta stamp classifier labels most hostless-channel objects
"asteroid" (p~0.9) - physically excluded by 7-18-day fixed-position persistence; the beta classifier
apparently reads "point source + empty template" as mover. Trust persistence, not the beta label.

**GATE 1: PASS.** A workable genuine fraction exists (>~20% required; measured 57.5% genuine overall,
32.5% genuine-transient), and the hostless/ELEPHANT channel specifically is essentially pure at
current (tiny) flag rates (~2-3 objects/night all-sky).

## 4. Adoption check

Method: (i) Fink `xm_tns_fullname` on every alert epoch (TNS status at emission); (ii) live TNS cone
(10 arcsec, wis-tns public search, checked 2026-07-14) for all 20 genuine-looking objects - live check
is essential: it caught SN 2026uid (TNS report by group "Rubin" post-dated the Fink alerts);
(iii) ALeRCE class as corroboration. The 20 faint sampled objects were not live-checked (none had
TNS at emission; all junk/stellar).

Of the **13 genuine transients: 6 adopted / 7 unadopted.**
Adopted: SN 2026uid (SLSN-I, Rubin group - was a hostless flag), AT 2026pun (GOTO/ZTF/ATLAS),
SN 2026pec (SN II, ZTF/GOTO/Pan-STARRS), AT 2026soj (Rubin), AT 2026sow (Rubin), AT 2023adht (DESIRT).
Unadopted: 7, all from the hostless channel, all with a negative live TNS cone on 2026-07-14 -
nobody has reported, classified, or visibly followed them up.

## 5. Top 5 unadopted candidates for archival forensics (all southern -> DECam/NSC depth applies)

| # | diaObjectId | RA, Dec (deg) | JD last alert | flag | quick look |
|---|---|---|---|---|---|
| 1 | 170587105461272950 | 334.24962, -18.20795 | 2461235.86 (last src 61235.36) | hostless | 18-day slow riser i 22.07->20.56 (+rollover), faint REX host 1.0" in DR10; same phenotype as SN 2026uid (SLSN-I) which came from this channel; m_i~20.6 |
| 2 | 170591519677875016 | 306.74802, -11.81856 | 2461233.81 | hostless | most isolated: NOTHING in LS DR10 within 3" (nearest = PSF 3.0"), 4 nights, slow fade m_i 20.8->21.1; genuinely hostless at DR10 depth |
| 3 | 170591507978387512 | 313.22651, -14.84044 | 2461235.75 (last src 61235.25) | hostless | 17-day riser z22.3->i21.2 sitting 0.46" from a faint DR10 PSF source - CV outburst vs SN on compact host; oddball |
| 4 | 170635519425249637 | 332.39126, -14.86990 | 2461235.84 (last src 61235.34) | hostless | hostless at 10" scale (nearest DR10 source 9.9" REX), 3 nights, fading after z22.3/i21.36 first night |
| 5 | 170587115976392822 | 326.82833, -13.47470 | 2461232.85 | extragalactic_lt20mag (anomaly-style oddball) | bright m_i~18.9, 15-d slow rise + flicker on a DR10 PSF counterpart (0.04"), NO Gaia DR3 match, no TNS; ALeRCE says AGN:0.88 - AGN vs nuclear transient unresolved |

JD keys above are the last harvested alert (`midpointMjdTai`+2400000.5); full per-epoch MJD/mag/band
series in `flags_sample.csv` and `work/enriched.json`.

## 6. Honest limitations

- Quick-look denominators are small (10 hostless = full census, but 20/702 for the faint channel);
  binomial 1-sigma on the 75% faint-channel artifact rate is +/-10%.
- SkyBoT down -> SSO check leans on Rubin's MPCORB association + persistence; single-night ambiguous
  objects (2/40) could still be movers.
- Lasair-LSST token gate untested (service unreachable) - retest before assuming either way.
- most_likely_sn totals missing 2 of 6 nights (server 504 on those windows).
- "Adopted" = present in TNS on 2026-07-14; a pro survey could be sitting on any of these internally.
- Visual classification of faint (m>22.5) diff smudges is judgment; two borderline calls are
  flagged as overrides in `work/finalize.py`.

## Files
- `/tmp/rubin_pilot/flags/flags_sample.csv` - 40 rows, JD+MJD-keyed, full vetting columns.
- `/tmp/rubin_pilot/flags/montage_0..3.png` - Science/Template/Difference cutout sheets.
- `/tmp/rubin_pilot/work/` - raw channel pulls (`*_7n.json`), `enriched.json`, `hostcheck.json`,
  `tns_now.json`, `alerce_xm.json`, `mls_counts.json`, scripts (`enrich.py`, `hostcheck.py`, `finalize.py`).
