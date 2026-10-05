# Object journal — Gaia DR3 ztf_ZTF26abtoqyd

| field | value |
|---|---|
| Canonical key | **Gaia DR3 ztf_ZTF26abtoqyd** |
| Aliases / names | ZTF26abtoqyd (RA 292.35178, Dec 8.25006; b -4.6) |
| Current class | Galactic transient: rise >= 2 mag within 1-5 d, fading; no Gaia DR3 source within 2 arcsec (CDS XMatch), no PS1/2MASS/unWISE within 4 arcsec |
| Current status | **reported to TNS as AT 2026adjl (dwarf-nova outburst candidate)** (as of 2026-09-30) |
| Dossier | — |
| CANDIDATES.md | — |
| In DR4 pre-registration | — |

## Cross-check ledger
*Append-only.*

| date | catalog / method | query | result | provenance |
|---|---|---|---|---|
| 2026-09-30 | ALeRCE ZTF alerts | — | **last limit 20.69 1.0 d before; first det MJD 61295.2 (2026-09-12) g 18.52 / i 18.53; to g 19.61 / r 19.13 by MJD 61312.1 (20 det); drb ~1.0; single ZTF id at the position** | docs/reports/transients_ztf_2026_09_30/lc_summary.py |
| 2026-09-30 | TNS cone 10 arcsec (control AT 2026uxw returned); VSX API 60 arcsec (control SS Cyg); SIMBAD 10 arcsec; CBAT TOCP | — | **no report in TNS, SIMBAD or TOCP; no VSX entry at the position (2026-09-30)** | docs/reports/transients_ztf_2026_09_30/cat_check.py |
| 2026-09-30 | ATLAS forced photometry (4613 points, 1129 nights, 2015-2026) | — | **outburst detected independently: o 18.78 (MJD 61298), o 18.60 (61299) after o > 19.70 on 61292; no earlier outburst night brighter than ~18.5** | docs/reports/transients_ztf_2026_09_30/atlas_dn.txt |
| 2026-09-30 | VizieR 4 arcsec: PS1 DR1, Gaia DR3, 2MASS, unWISE (lc_ctx.py) | — | **no source within 4 arcsec in any** | docs/reports/transients_ztf_2026_09_30/lc_ctx.py |
| 2026-09-30 | TNS AT report (web form; reporter Alex Keur; group None; source ZTF; AT type Other) | — | **designation AT 2026adjl (2026-09-30); discovery 2026-09-12 05:10:47 UT ZTF-i 18.53 +- 0.08; last non-detection ZTF-i > 19.99 on 2026-09-11; photometry ZTF-g 18.52 (09-12), ATLAS-o 18.81 (09-15), ATLAS-o 18.62 (09-16)** | docs/reports/transients_ztf_2026_09_30/atlas_points.txt |

## Status timeline
*Append-only.*

| date | status | reason | by |
|---|---|---|---|
| 2026-09-30 | candidate (dwarf-nova outburst of an uncatalogued CV, 2026-09) | journal created | journal.py new |
| 2026-09-30 | reported to TNS as AT 2026adjl (dwarf-nova outburst candidate) | TNS report 2026-09-30 | journal.py |

## Entry log
*Append-only, chronological.*

### 2026-09-30 — Reported to TNS: AT 2026adjl
- **Did:** TNS AT report
- **Found:** AT 2026adjl
- **Provenance:** https://www.wis-tns.org/object/2026adjl
