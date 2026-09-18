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
| Period | **3.727023 ± 0.000063 d** (night-resampled bootstrap on the folded eclipse contrast; see CORRECTION below) |
| Epoch Min I (HJD) | **2458257.856 ± 0.029** (±41 min — set by sampling, not by a measured contact) |
| Max (out of eclipse) | 12.712 (zr) · 13.263 (zg) · 12.483 (zi) |
| Min I (primary) | 12.928 (zr) · 13.513 (zg) · 12.672 (zi) → depth **0.216 / 0.250 / 0.189 mag** |
| Min II (secondary) | 12.817 (zr) · 13.377 (zg) · 12.593 (zi) → depth **0.105 / 0.114 / 0.110 mag** |
| Band/system | ZTF zg, zr, zi (AB, PSF photometry, catflags==0 only) |
| Eclipse duration | **0.057 in phase = 5.7% of period ≈ 5.1 h** — see DURATION CORRECTION at end. **The value entered at submission was 10%, which is ~1.75× too long.** |
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


---

# CORRECTION (2026-09-18, before filing) — the ephemeris justification was wrong

Plotting the five "resolved eclipses" individually exposed the error: each is a single
night of 3–5 ZTF exposures spanning ~12 minutes, all at the same magnitude. **No ingress
or egress is sampled anywhere in the dataset** (largest within-night span of in-eclipse
points: well under an hour). They are therefore not measured minima, and the quoted
"5 eclipse timings, rms 23 min" overstated what the data support.

**Refit properly:** a 2-D grid search over (P, T₀) maximising the mean in-eclipse depth,
with a 120-iteration bootstrap resampling whole nights:

- **P = 3.727023 ± 0.000063 d** — value essentially unchanged (3.727026 → 3.727023), but
  now justified by *phase coherence of 36 in-eclipse nights over 7.4 yr* rather than by
  five pseudo-timings.
- **Min I (HJD) = 2458257.856 ± 0.029** (±41 min; the uncertainty reflects where in the
  eclipse the sampling happens to fall).
- Eclipse duration ≈ **8.9 h** (0.10 in phase) from the 60-bin fold; folded primary depth
  0.177 mag, per-epoch maximum depth 0.216 mag.

Nothing about the classification changes — it is an EA, and the period is solid. Only the
epoch precision and the stated provenance change. `ZTF18abxnwmb_five_eclipses.png` is kept
in this folder as the evidence that forced the correction.


---

# DURATION CORRECTION (2026-09-18, after filing)

The document carried **two inconsistent eclipse durations** — the form table said ~0.08 in
phase (≈7 h), the earlier CORRECTION section said 0.10 (8.9 h); that correction updated one
section and not the other. **The value actually entered in the VSX wizard was 10%**
(confirmed from the submission session record: "Period / Epoch / Eclipse duration =
3.727023 d · HJD 2458257.856 · 10%").

**Re-derived per-epoch** (not binned) from the 1,146 clean zr epochs, folded on
P = 3.727023 d with the primary centred on phase 0. Out-of-eclipse baseline
zr = 12.7088, σ = 0.0177 (n = 462); in-eclipse = points more than 3σ faint:

- The eclipse is a **contiguous** structure from phase **−0.0303 to +0.0264**, with egress
  resolved in the fold (depth falls smoothly 0.19 → 0.058 between phase +0.019 and +0.025).
- **Duration = 0.057 in phase = 5.7% of period = 5.1 h.**
- Centre lies at phase −0.002, i.e. **T₀ is confirmed correct**; no ephemeris shift needed.

**METHODOLOGICAL TRAP, recorded because it nearly reversed this result.** A naive 3σ
bracket over all faint points gives 0.120 in phase (12%) — which would have appeared to
*confirm* the filed 10%. That span is produced by a **single** point at phase +0.0894 with
depth 0.064 (3.6σ), isolated by 0.063 in phase from the nearest in-eclipse point. One
straggler inflated the duration by more than 2×. **A min-to-max span over threshold-passing
points is not a duration measurement unless the points are contiguous** — the same
"span criterion" flaw already banked from the turn-on pilot, reappearing in a different guise.

Unaffected and independently reproduced: baseline zr = 12.712 (matches the quoted maximum),
folded primary depth 0.170–0.184 (matches the stated 0.177), secondary centred at phase
0.500. **Classification (EA), period, epoch and depths all stand.**

IMPACT ON THE FILED RECORD: eclipse duration is an optional VSX field, entered as **10%**
against a measured **5.7%**. Worth a short correction note to the moderator; nothing else
in the submission is affected. The passband entries were verified correct from the session
record: max 12.712 and min 12.928 both submitted under band **"r"** (Sloan r from the VSX
passband list), NOT V — so the unresolved APASS/UCAC4 column-mapping question never reached
the filing.
