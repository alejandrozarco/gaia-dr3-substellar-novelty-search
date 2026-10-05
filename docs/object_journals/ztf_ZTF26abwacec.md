# Object journal — Gaia DR3 ztf_ZTF26abwacec

| field | value |
|---|---|
| Canonical key | **Gaia DR3 ztf_ZTF26abwacec** |
| Aliases / names | ZTF26abwacec (RA 288.92825, Dec -4.04148; Aquila, b -7.2) |
| Current class | Galactic transient: rise >= 2.8 mag in 1 d to g 17.47 (g-r ~ -0.1), decline ~0.3 mag/d; no counterpart within 4 arcsec (PS1/Gaia/2MASS/unWISE) |
| Current status | **reported to TNS as AT 2026adji (dwarf-nova outburst candidate)** (as of 2026-09-30) |
| Dossier | — |
| CANDIDATES.md | — |
| In DR4 pre-registration | — |

## Cross-check ledger
*Append-only.*

| date | catalog / method | query | result | provenance |
|---|---|---|---|---|
| 2026-09-30 | ALeRCE ZTF alerts (15 detections) | — | **last non-detections g > 20.40 (MJD 61301.14), r > 20.33 (61301.17); first detection g 17.47 / r 17.55 on MJD 61302.13-61302.17 (2026-09-19), i 17.57 next night; g 19.08-19.29 and r 19.10-19.32 by MJD 61306-61312; drb ~1.0** | docs/reports/transients_ztf_2026_09_30/lc_ctx.py |
| 2026-09-30 | VizieR 4 arcsec (PS1 DR1, Gaia DR3, 2MASS, unWISE); TNS 10 arcsec (control AT 2026uxw); VSX 60 arcsec (control SS Cyg); SIMBAD 10 arcsec; CBAT TOCP | — | **no counterpart in any catalogue (amplitude >= ~4.5 mag); no report in TNS, VSX, SIMBAD or TOCP (2026-09-30)** | docs/reports/transients_ztf_2026_09_30/cat_check.py |
| 2026-09-30 | ATLAS forced photometry | — | **requested 2026-09-30 (queued)** | ATLAS forced-photometry server (pending) |
| 2026-09-30 | ATLAS forced photometry (3908 points, 980 nights, 2015-2026) | — | **outburst detected independently: o 18.39 on MJD 61305 (limit o > 19.73 on 61299); no earlier night > 5 sigma and > 150 uJy (outbursts brighter than ~18.5 excluded 2015-2026)** | docs/reports/transients_ztf_2026_09_30/atlas_dn.txt |
| 2026-09-30 | TNS AT report (web form; reporter Alex Keur; group None; source ZTF; AT type Other) | — | **designation AT 2026adji (2026-09-30); discovery 2026-09-19 03:09:00 UT ZTF-g 17.47 +- 0.05; last non-detection ZTF-r > 20.33 on 2026-09-18; photometry ZTF-r 17.55 (09-19), ATLAS-o 18.34 (09-22), ATLAS-o 19.23 (09-28)** | docs/reports/transients_ztf_2026_09_30/atlas_points.txt |

## Status timeline
*Append-only.*

| date | status | reason | by |
|---|---|---|---|
| 2026-09-30 | candidate (dwarf-nova outburst of an uncatalogued CV, 2026-09-19) | journal created | journal.py new |
| 2026-09-30 | reported to TNS as AT 2026adji (dwarf-nova outburst candidate) | TNS report 2026-09-30 | journal.py |

## Entry log
*Append-only, chronological.*

### 2026-09-30 — Reported to TNS: AT 2026adji
- **Did:** TNS AT report
- **Found:** AT 2026adji
- **Provenance:** https://www.wis-tns.org/object/2026adji
