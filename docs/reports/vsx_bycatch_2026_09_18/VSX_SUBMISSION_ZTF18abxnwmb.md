# VSX submission draft — ZTF18abxnwmb (detached eclipsing binary)
**DRAFT ONLY — filing is the USER's action via their AAVSO/VSX account.**
Prepared 2026-09-18 from ZTF DR photometry (IRSA), re-derived from source; the earlier
values (from a wiped scratch run) are independently REPRODUCED by this analysis.

## VSX form fields

| Field | Value |
|---|---|
| Name / identifier | ZTF18abxnwmb (= Gaia DR3 2710029878791087616) |
| RA (J2000) | 22 34 25.33 (338.605525 deg) — Gaia DR3 |
| Dec (J2000) | +08 06 59.6 (+8.116548 deg) — Gaia DR3 |
| Variability type | **EA** (detached; flat out-of-eclipse baseline, narrow eclipses, secondary at phase 0.5) |
| Period | **3.727026 ± 0.000082 d** (5 resolved primary eclipses over 3.0 yr, timing rms 23 min; fold-maximisation gives 3.726867 d — quote the timing value) |
| Epoch Min I (HJD) | **2458257.8225 ± 0.0348** |
| Max (out of eclipse) | 12.712 (zr) · 13.263 (zg) · 12.483 (zi) |
| Min I (primary) | 12.928 (zr) · 13.513 (zg) · 12.672 (zi) → depth **0.216 / 0.250 / 0.189 mag** |
| Min II (secondary) | 12.817 (zr) · 13.377 (zg) · 12.593 (zi) → depth **0.105 / 0.114 / 0.110 mag** |
| Band/system | ZTF zg, zr, zi (AB, PSF photometry, catflags==0 only) |
| Eclipse duration | ~0.08 in phase (≈7 h) |
| Discoverer / submitter | A. Keur (independent) |
| Data source | ZTF Data Release PSF photometry via IRSA (2,564 epochs total; 1,146 clean zr), MJD 58252–60969 (7.4 yr) |

## Evidence summary
Folded at P = 3.7268 d with strict quality cuts (catflags==0), the zr light curve is flat
to ±0.007 mag across 20 of 24 phase bins, with a 0.141 mag median dip in bins 18–19 and a
0.049 mag dip in bins 6–7 — exactly 0.5 in phase apart. Per-epoch minima reach 0.216 mag
(primary) and 0.105 mag (secondary). Depths are consistent in all three bands (weak colour
dependence, as expected for a detached system with similar-temperature components).
Lomb–Scargle finds the half-period alias at 1.86340 d with FAP 7.7e-30.

**Caveat carried:** the raw min–max range (1.25 mag in zr) is NOT the amplitude — it is set
by one flagged outlier (catflags=256). Robust (95th–5th pct) range is 0.125 mag. Quote
eclipse depths, not peak-to-peak.

## Novelty (verified 2026-09-18)
VSX cone 30″ = 0 rows · SIMBAD 10″ = no entry · not in TNS. VSX cone parser
positive-controlled on SS Cyg and RR Lyr the same day. Gaia DR3 counterpart at 0.11″:
G = 12.749, BP−RP = 0.969, parallax 1.368 ± 0.025 mas (d ≈ 730 pc), RUWE = 1.20.

## Disclosure (per project policy)
Algorithm-found (AI-assisted archival mining of ZTF alert + DR photometry),
human-refereed, filed by the user under their own name.

---

# Qualification check against the AAVSO VSX manual (read 2026-09-18)

| Manual requirement | Our status |
|---|---|
| Data-mined submissions allowed, but "we are more critical… we expect the submitter to do some work, such as period analysis, rather than just regurgitating survey information" | **PASS, comfortably** — independent period search, 5 resolved eclipse timings, linear ephemeris with 23-min rms, per-band depths, outlier diagnosis |
| "The object must be proven variable"; "Incomplete or sparse light curves can not be accepted" | **PASS** — 2,564 epochs / 7.4 yr (1,146 clean zr); far denser than the manual's "dense coverage" example |
| Accurate coordinates, "no worse than an arcsec or two", from an astrometric catalog | **PASS** — Gaia DR3, mas-level |
| "Please do not use Gaia DR2 names unless there is no other identifier available" | **FIXED** — primary name below is 2MASS; Gaia quoted as cross-ID |
| Max and min magnitudes required | **PASS** (all three bands) |
| "For periodic variables also the period and epoch (time of minimum for eclipsing binaries)" | **PASS** — P and Min I given |
| Supporting evidence: time-series plot (brightest at top) **and** a phase plot for periodic variables | **PASS** — `vsx_ZTF18abxnwmb_lc_phase.png` (both panels, magnitude inverted) |
| "Do not attach the light curves provided by survey web sites" | **PASS** — plots are our own from IRSA DR photometry |
| Minor-planet check ("vermin of the sky") | **PASS** — Gaia parallax 1.368 mas + proper motion; fixed position across 7.4 yr |
| VSX is primarily a catalog of **Galactic** variables | **PASS** — d ≈ 730 pc |
| One submission per user/group per day | noted (only one object is being submitted) |
| Requires a VSX/AAVSO login | **USER ACTION** — register at aavso.org/vsx registration |

**Verdict: this object qualifies on every criterion in the manual.** Data-mined EA
submissions are explicitly welcome, and the manual's higher bar for data-mined work
(do real analysis, not regurgitation) is exactly what the eclipse-timing ephemeris
satisfies.

## Cross-identifications (use a non-Gaia primary name, per manual §V.b)

- **Primary name suggestion: 2MASS J22342534+0806596** (J=11.489, H=11.148, K=11.065, AAA)
- UCAC4 491-149200 · GSC 2.3 N0OM002947 · PS1 DR1 117743386055230375
- Survey ID to quote (manual §V.a): **ZTF18abxnwmb**
- Gaia DR3 2710029878791087616 (cross-ID only)

## Two items to settle at submission time
1. **Passband**: manual prefers V. Our calibrated values are ZTF zg/zr/zi (Sloan-like);
   submit with band explicitly flagged, or transform. UCAC4 carries APASS photometry for
   this star (≈13.69 / ≈13.10 in the B/V columns) — **verify the column mapping before
   quoting a V magnitude**; do not assert it from this note.
2. A finding chart is optional at G=12.7 (manual: most 14th-mag stars are identifiable
   from DSS with good coordinates) but cheap to add if a moderator asks.
