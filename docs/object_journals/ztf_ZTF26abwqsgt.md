# Object journal — Gaia DR3 ztf_ZTF26abwqsgt

| field | value |
|---|---|
| Canonical key | **Gaia DR3 ztf_ZTF26abwqsgt** |
| Aliases / names | ZTF26abwqsgt (RA 284.93743, Dec -10.57877; b -6.6) |
| Current class | Galactic transient: rise >= 2 mag within 1-5 d, fading; no Gaia DR3 source within 2 arcsec (CDS XMatch), no PS1/2MASS/unWISE within 4 arcsec |
| Current status | **reported to TNS as AT 2026adjk (dwarf-nova outburst candidate)** (as of 2026-09-30) |
| Dossier | — |
| CANDIDATES.md | — |
| In DR4 pre-registration | — |

## Cross-check ledger
*Append-only.*

| date | catalog / method | query | result | provenance |
|---|---|---|---|---|
| 2026-09-30 | ALeRCE ZTF alerts | — | **last limit 20.68 5.0 d before; first det MJD 61305.1 (2026-09-22) g 18.15 / r 18.18; faded to g 18.98 / r 19.17 by MJD 61308.2 (8 det); drb ~1.0; single ZTF id at the position** | docs/reports/transients_ztf_2026_09_30/lc_summary.py |
| 2026-09-30 | TNS cone 10 arcsec (control AT 2026uxw returned); VSX API 60 arcsec (control SS Cyg); SIMBAD 10 arcsec; CBAT TOCP | — | **no report in TNS, SIMBAD or TOCP; no VSX entry at the position (2026-09-30)** | docs/reports/transients_ztf_2026_09_30/cat_check.py |
| 2026-09-30 | ATLAS forced photometry (4372 points, 1058 nights, 2015-2026) | — | **outburst detected independently: o 18.24 on MJD 61305 (limit o > 19.48 on 61299); no earlier outburst night brighter than ~18.5** | docs/reports/transients_ztf_2026_09_30/atlas_dn.txt |
| 2026-09-30 | VizieR 4 arcsec: PS1 DR1, Gaia DR3, 2MASS, unWISE (lc_ctx.py) | — | **no source within 4 arcsec in any** | docs/reports/transients_ztf_2026_09_30/lc_ctx.py |
| 2026-09-30 | TNS AT report (web form; reporter Alex Keur; group None; source ZTF; AT type Other) | — | **designation AT 2026adjk (2026-09-30); discovery 2026-09-22 03:30:59 UT ZTF-r 18.18 +- 0.06; last non-detection ZTF-r > 20.06 on 2026-09-17; photometry ZTF-g 18.15 (09-22), ATLAS-o 18.14 (09-22), ATLAS-o 19.29 (09-28)** | docs/reports/transients_ztf_2026_09_30/atlas_points.txt |

## Status timeline
*Append-only.*

| date | status | reason | by |
|---|---|---|---|
| 2026-09-30 | candidate (dwarf-nova outburst of an uncatalogued CV, 2026-09) | journal created | journal.py new |
| 2026-09-30 | reported to TNS as AT 2026adjk (dwarf-nova outburst candidate) | TNS report 2026-09-30 | journal.py |

## Entry log
*Append-only, chronological.*

### 2026-09-30 — Reported to TNS: AT 2026adjk
- **Did:** TNS AT report
- **Found:** AT 2026adjk
- **Provenance:** https://www.wis-tns.org/object/2026adjk
