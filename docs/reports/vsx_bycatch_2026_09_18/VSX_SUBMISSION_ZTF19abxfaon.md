# VSX submission draft — ZTF19abxfaon (uncatalogued high-amplitude state-cycling variable)
**DRAFT ONLY — filing is the USER's action via their AAVSO/VSX account.**
Prepared 2026-09-18 to the same standard as ZTF18abxnwmb. Supersedes the 2026-07-15
draft in `rubin_pilot_2026_07_14/forensics/170587115976392822/consumer_package/vsx_draft.md`.

## VSX form fields

| Field | Value |
|---|---|
| Primary name (survey ID, manual §V.a) | **ZTF19abxfaon** |
| RA (J2000) | **21 47 18.80** (326.828336) — Legacy Survey DR10 tractor, Gaia-referenced astrometry |
| Dec (J2000) | **−13 28 28.9** (−13.474691) |
| Astrometric ID | **LS DR10 ls_id 10995383192785753** (type PSF, sep 0.04″ from the Rubin position). NOTE: **no Gaia DR3, 2MASS, UCAC4, GSC 2.3, PS1 DR1 or CatWISE counterpart** — the star is below all of their depths in quiescence, so LS DR10 is the only astrometric anchor available (manual §III.a permits "another astrometric catalog"). |
| Variability type | **CV:** (uncertain) — VY Scl / Z Cam-like state cycling. See "AGN alternative" below; if the moderator prefers, **VAR** is acceptable pending spectroscopy |
| Maximum (brightest) | **17.98 r** (ZTF zr, MJD 59218.078 = 2021-01-04) |
| Minimum (faintest) | **23.44 r** (DECam r via NSC DR2, MJD 56511.240 = 2013-08-07) |
| Amplitude | ≈ **5.5 mag** (note the max is ZTF zr, the min DECam r — closely related but not identical systems; state this in the remarks) |
| Period | **NONE.** Deep search (1,687 de-trended ZTF forced-photometry epochs, 8.1 yr): Lomb–Scargle 30 min–2 d null in g/r/i (one marginal 46.6-min r alias refuted by split-sample + colour tests); BLS eclipse search 1.4–48 h null. **Injection–recovery: a coherent semi-amplitude ≥0.06 mag at P = 1.5–4 h would have been recovered 20/20.** No eclipses → low-inclination system, or non-periodic. |
| Epoch | Turn-on constrained between **MJD 57987 (2017-08-22, DECam g = 23.45)** and **MJD 58285.400 (2018-06-16, ZTF zr = 21.24 ± 0.26)**; first zr ≤ 20.5 at MJD 58363.27 |
| Discoverer / submitter | A. Keur (independent) |
| Data sources | DECam/NOIRLab Source Catalog DR2 (15 epochs, 2013–2019); ZTF DR PSF photometry (337); ZTF alerts via ALeRCE (491); ZTF forced photometry (ZFPS req 479161, 2,354 quality epochs); Rubin/LSST alert (Fink, 2026-07-14) |
| Supporting plot | `vsx_ZTF19abxfaon_lightcurve.png` (13-yr record, magnitude inverted). **No phase plot** — the manual requires one only for periodic variables, and the period search is a documented null. |

## Why this is a variable, not an artifact
Four independent instruments/reductions agree: DECam (deep, 2013–2019), ZTF DR PSF
photometry, ZTF alerts, and Rubin/LSST. The 2013–2017 quiescent state is measured on five
consecutive DECam r exposures (23.05–23.44) and two g exposures (23.29, 23.45); the bright
state is sampled by hundreds of ZTF epochs. **Two contaminating points were excluded** and
are documented rather than hidden: a single PS1 i = 18.65 detection 3.5″ SE (MJD 56531)
and a single NEOWISE W1 = 16.2 frame 1.4″ off (MJD 57887) — both probable passing
asteroids, the field sitting at ecliptic latitude −0.12°.

## The AGN alternative (must be disclosed to the moderator)
The ALeRCE **stamp** classifier on the Rubin alert returned "AGN 0.88", and DECaLS DR9
carries a photometric redshift (z ≈ 0.93) for the source. Both are disfavoured:
- **No mid-IR counterpart** — CatWISE2020 and AllWISE are empty within 10″; LS DR10 forced
  W1 = 22.1, W2 = 21.8 (noise level). An AGN at that optical brightness would show hot dust.
- **No radio** (NVSS, FIRST, VLASS QL), **no UV** (GALEX), **no X-ray** counterpart.
- **A 5.5-mag turn-on from 4+ years of stability is outside normal AGN variability.**
- The DECaLS photo-z is unreliable here: the coadd mixes pre- and post-turn-on epochs
  (the same aliasing that makes LS DR10 report i = 20.81 against r = 23.12).
- ALeRCE's **light-curve** (not stamp) classifiers on the ZTF data rank **CV/Nova 0.95–0.97**.
**Relevance to VSX:** the manual states VSX excludes extragalactic objects such as quasars.
The evidence favours a Galactic CV, but the moderator should be told the AGN hypothesis is
not formally excluded without a spectrum. A spectrum settles it; the object is currently
~18.5–19 and reachable by a 2 m class telescope.

## Qualification check against the AAVSO VSX manual
| Requirement | Status |
|---|---|
| Proven variable; no sparse/incomplete light curves | **PASS, overwhelmingly** — 13 yr, ~840 calibrated epochs + 2,354 forced-photometry epochs, 5.5 mag |
| Data-mined submissions held to a higher bar ("do some work, such as period analysis") | **PASS** — full period + eclipse search with injection–recovery sensitivity limits, a quantified null rather than silence |
| Accurate coordinates from an astrometric catalog | **PASS** — LS DR10, sub-arcsec (Gaia-referenced) |
| Max and min magnitudes | **PASS** (with the cross-system caveat stated) |
| Period + epoch **for periodic variables** | **N/A** — documented aperiodic; turn-on epoch given instead |
| Supporting plot, magnitude inverted | **PASS** |
| Primary name should not be a Gaia designation | **PASS** — ZTF survey ID used |
| Galactic object | **ARGUED, not proven** — see AGN alternative above |
| Minor-planet check | **PASS** — two asteroid contaminants identified and excluded; the source itself persists across 8 yr at a fixed position |

**Verdict: qualifies, with one honest flag** — the Galactic-vs-AGN question is the only
criterion not fully closed, and it is disclosed rather than glossed. If a moderator is
uncomfortable, the fallback is to submit as **VAR** with the same evidence.

## Disclosure
Algorithm-found (AI-assisted archival mining of Rubin/ZTF/DECam public data),
human-refereed, filed by the user under their own name.
