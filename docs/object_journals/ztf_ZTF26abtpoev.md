# Object journal — Gaia DR3 ztf_ZTF26abtpoev

| field | value |
|---|---|
| Canonical key | **Gaia DR3 ztf_ZTF26abtpoev** |
| Aliases / names | ZTF26abtpoev (RA 289.34140, Dec -3.24887; Aquila, b -7.2) |
| Current class | Galactic transient: rise >= 2.4 mag in <= 1 d to i 17.83, decline ~0.2-0.3 mag/d; no counterpart within 4 arcsec (PS1/Gaia/2MASS/unWISE) |
| Current status | **reported to TNS as AT 2026adjj (dwarf-nova outburst candidate)** (as of 2026-09-30) |
| Dossier | — |
| CANDIDATES.md | — |
| In DR4 pre-registration | — |

## Cross-check ledger
*Append-only.*

| date | catalog / method | query | result | provenance |
|---|---|---|---|---|
| 2026-09-30 | ALeRCE ZTF alerts (16 detections) | — | **last non-detections i > 20.20, g > 20.60 (MJD 61294.22-61294.23); first detection i 17.83 on MJD 61295.22 (2026-09-12); g 18.32 next night; g 19.30-19.35, r 19.37 by MJD 61302; drb ~1.0** | docs/reports/transients_ztf_2026_09_30/lc_ctx.py |
| 2026-09-30 | VizieR 4 arcsec (PS1 DR1, Gaia DR3, 2MASS, unWISE); TNS 10 arcsec (control AT 2026uxw); VSX 60 arcsec (control SS Cyg); SIMBAD 10 arcsec; CBAT TOCP | — | **no counterpart in any catalogue; no report in TNS, SIMBAD or TOCP; VSX nearest entry Gaia DR3 4213047224404035584 (EA, 0.278 d) at 58.4 arcsec, unrelated (2026-09-30)** | docs/reports/transients_ztf_2026_09_30/cat_check.py |
| 2026-09-30 | ATLAS forced photometry | — | **requested 2026-09-30 (queued)** | ATLAS forced-photometry server (pending) |
| 2026-09-30 | ATLAS forced photometry (4155 points, 978 nights, 2015-2026) | — | **outburst detected independently: o 19.33 (MJD 61298), o 18.72 (61299) after o > 19.92 on 61292; no earlier outburst night brighter than ~18.5** | docs/reports/transients_ztf_2026_09_30/atlas_dn.txt |
| 2026-09-30 | TNS AT report (web form; reporter Alex Keur; group None; source ZTF; AT type Other) | — | **designation AT 2026adjj (2026-09-30); discovery 2026-09-12 05:12:49 UT ZTF-i 17.83 +- 0.07; last non-detection ZTF-g > 20.60 on 2026-09-11; photometry ZTF-g 18.32 (09-13), ATLAS-o 18.76 (09-16)** | docs/reports/transients_ztf_2026_09_30/atlas_points.txt |

## Status timeline
*Append-only.*

| date | status | reason | by |
|---|---|---|---|
| 2026-09-30 | candidate (dwarf-nova outburst of an uncatalogued CV, 2026-09-12) | journal created | journal.py new |
| 2026-09-30 | reported to TNS as AT 2026adjj (dwarf-nova outburst candidate) | TNS report 2026-09-30 | journal.py |

## Entry log
*Append-only, chronological.*

### 2026-09-30 — Reported to TNS: AT 2026adjj
- **Did:** TNS AT report
- **Found:** AT 2026adjj
- **Provenance:** https://www.wis-tns.org/object/2026adjj
