# Object journal — Gaia DR3 ztf_ZTF26absimmf

| field | value |
|---|---|
| Canonical key | **Gaia DR3 ztf_ZTF26absimmf** |
| Aliases / names | ZTF26absimmf (RA 98.57865, Dec -6.02497; Monoceros, b -6.5) |
| Current class | Galactic transient: fast rise >= 2.8 mag in 2 d to r 16.65, no quiescent counterpart (PS1/Gaia/2MASS/unWISE none within 4 arcsec) |
| Current status | **reported to TNS as AT 2026adjh (dwarf-nova / WZ Sge-type outburst candidate)** (as of 2026-09-30) |
| Dossier | — |
| CANDIDATES.md | — |
| In DR4 pre-registration | — |

## Cross-check ledger
*Append-only.*

| date | catalog / method | query | result | provenance |
|---|---|---|---|---|
| 2026-09-30 | ALeRCE ZTF alerts (3 detections, prior non-detections) | — | **r > 19.42 on MJD 61285.51, r 16.65 on MJD 61287.50 (2026-09-04), i 18.41 on MJD 61305.47, i 18.77 on MJD 61312.50; drb 1.00; nearest template source 8.3 arcsec** | docs/reports/transients_ztf_2026_09_30/lc_ctx.py |
| 2026-09-30 | VizieR cones 4 arcsec: PS1 DR1, Gaia DR3, 2MASS, unWISE | — | **no source within 4 arcsec in any (PS1 limit ~22): outburst amplitude >= ~5 mag** | docs/reports/transients_ztf_2026_09_30/lc_ctx.py |
| 2026-09-30 | TNS cone 10 arcsec (control AT 2026uxw returned); VSX API 60 arcsec (control SS Cyg returned); CBAT TOCP page; SIMBAD 10 arcsec | — | **none in TNS, VSX, TOCP or SIMBAD (2026-09-30 03:05 UTC)** | docs/reports/transients_ztf_2026_09_30/tns_slow.py |
| 2026-09-30 | ATLAS forced photometry | — | **requested 2026-09-30 (queued)** | ATLAS forced-photometry server (pending) |
| 2026-09-30 | ATLAS forced photometry (4037 points, 972 nights, MJD 57298-61311) | — | **outburst confirmed: o 16.69 (MJD 61287, same night as ZTF), o 16.80 (61288), c 17.64 (61294), o 18.62 (61311); pre-outburst nights o 20.4-20.9 (25 uJy); no earlier night > 5 sigma and > 150 uJy in 2015-2026: a single outburst in 11 years, amplitude >= 5.3 mag, decline ~0.08 mag/d** | docs/reports/transients_ztf_2026_09_30/atlas/ZTF26absimmf.txt |
| 2026-09-30 | TNS AT report (web form; reporter Alex Keur; group None; source ZTF; AT type Other) | — | **designation AT 2026adjh (2026-09-30); discovery 2026-09-04 12:06:19 UT ZTF-r 16.65 +- 0.04; last non-detection ZTF-r > 19.42 on 2026-09-02; photometry ATLAS-o 16.69 (09-04), ATLAS-c 17.62 (09-11), ZTF-i 18.41 (09-22)** | docs/reports/transients_ztf_2026_09_30/atlas_points.txt |

## Status timeline
*Append-only.*

| date | status | reason | by |
|---|---|---|---|
| 2026-09-30 | candidate (nova or WZ Sge-type dwarf-nova outburst, 2026-09) | journal created | journal.py new |
| 2026-09-30 | candidate (WZ Sge-type dwarf-nova superoutburst, 2026-09-04; unreported) | ATLAS confirmation + no prior outbursts | journal.py |
| 2026-09-30 | reported to TNS as AT 2026adjh (dwarf-nova / WZ Sge-type outburst candidate) | TNS report 2026-09-30 | journal.py |

## Entry log
*Append-only, chronological.*

### 2026-09-30 — ATLAS confirms the outburst; no earlier outbursts
- **Did:** ATLAS forced photometry 2015-2026
- **Found:** Single outburst in 11 years, amplitude >= 5.3 mag, slow decline (~0.08 mag/d over 24 d): WZ Sge-type superoutburst candidate of an uncatalogued CV (classical nova excluded at this peak brightness for a Galactic-disc distance)
- **Provenance:** docs/reports/transients_ztf_2026_09_30/

### 2026-09-30 — Reported to TNS: AT 2026adjh
- **Did:** TNS AT report
- **Found:** AT 2026adjh
- **Provenance:** https://www.wis-tns.org/object/2026adjh
