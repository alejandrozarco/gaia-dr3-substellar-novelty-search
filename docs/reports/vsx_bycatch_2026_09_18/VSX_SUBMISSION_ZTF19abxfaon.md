# VSX submission draft — ZTF19abxfaon (uncatalogued high-amplitude state-changing variable)
**DRAFT ONLY — filing is the USER's action via their AAVSO/VSX account.**
Prepared 2026-09-18 to the same standard as ZTF18abxnwmb. Supersedes the 2026-07-15
draft in `rubin_pilot_2026_07_14/forensics/170587115976392822/consumer_package/vsx_draft.md`.

## VSX form fields

| Field | Value |
|---|---|
| Primary name (survey ID, manual §V.a) | **ZTF19abxfaon** |
| RA (J2000) | **21 47 18.80** (326.828336) — Legacy Survey DR10 tractor, Gaia-referenced astrometry |
| Dec (J2000) | **−13 28 28.9** (−13.474691) |
| Astrometric ID | **LS DR10 ls_id 10995383192785753** (type PSF, sep 0.04″ from the Rubin position). NOTE: **no Gaia DR3, 2MASS, UCAC4, GSC 2.3, PS1 DR1 or CatWISE counterpart** — no counterpart is FOUND in any of them (optical faintness alone does not establish infrared faintness, and catalogue absence has several possible causes), so LS DR10 is the only astrometric anchor available (manual §III.a permits "another astrometric catalog"). |
| Variability type | **VAR**, with `CV:` proposed in the remarks. The record (REVISION 7) is a turn-on before mid-2018 followed by **repeated ~2-mag reversals** between ~19 and ~21, never returning to the pre-2018 level — VY Scl-like state changing. **Z Cam remains withdrawn** (no dwarf-nova outbursts with standstills). Galactic origin argued from the mid-IR limit, not asserted |
| Maximum (brightest) | **18.34 r** (ZTF zr, MJD 60577.254 = 2024-09-21). **The previously quoted 17.98 is WITHDRAWN** — see REVISION 7: it sits on the single shallowest of 272 zr frames (limitmag 18.29 vs median 20.69) with sharp +0.682 against −0.089…+0.026 for its peers, at airmass 2.03. The adopted value sits on a limitmag 21.04 frame (2.70 mag above the limit), sharp −0.062, with a confirming partner frame at 18.405 seconds later |
| Minimum (faintest) | **23.12 ± 0.08 r** — Legacy Survey DR10 **coadd** (0.564 ± 0.041 nMgy, 13.9σ), which averages the pre-2018 DECam imaging. Preferred over the single NSC exposure of 23.44 (MJD 56511.240), which is one measurement at the frame limit. Both are quoted in the remarks |
| Amplitude | **≈ 4.8 mag observed range** (23.12 − 18.34 ≈ 78× in flux). Revised down from the withdrawn 5.46 (REVISION 7). Still a **cross-system range, NOT a single-passband amplitude** — max is ZTF zr, min is DECam r via the LS DR10 coadd. Quote both filters and uncertainties |
| Period | **NONE.** Deep search (1,687 de-trended ZTF forced-photometry epochs, 8.1 yr): Lomb–Scargle 30 min–2 d null in g/r/i (one marginal 46.6-min r alias refuted by split-sample + colour tests); BLS eclipse search 1.4–48 h null. **Injection–recovery: 20/20 sinusoidal signals of semi-amplitude ≥0.06 mag at P = 1.5–4 h were recovered** — a 95% binomial lower bound of 0.83 on that recovery rate, for those injected waveforms/phases only; it is NOT a completeness proof across all periods, phases, aliases or eclipse duty cycles. **No eclipses were DETECTED under this sampling and these search assumptions** — this does not imply low inclination, and an aperiodic light curve does not imply the system lacks an orbital period. |
| Epoch | Turn-on constrained between **MJD 57987 (2017-08-22, DECam g = 23.45)** and **MJD 58285.400 (2018-06-16, ZTF zr = 21.24 ± 0.26)**; first zr ≤ 20.5 at MJD 58363.27 |
| Discoverer / submitter | A. Keur (independent) |
| Data sources | **Three instruments**: DECam/NOIRLab Source Catalog DR2 (15 epochs, 2013–2019); **ZTF** — three reductions that SHARE exposures and calibration and are therefore NOT independent confirmations: DR PSF photometry (337), alerts via ALeRCE (491), forced photometry (ZFPS req 479161, 2,354 quality epochs); Rubin/LSST alert (Fink, 2026-07-14). **Do not sum these epoch counts as independent measurements.** OUTSTANDING: ZFPS reports reference-relative difference flux; if the ZTF reference for this field/filter was built after the 2018 turn-on it contains the source, which would distort the derived magnitudes. Reference epochs not yet audited. |
| Supporting plot | `vsx_ZTF19abxfaon_lightcurve.png` (13-yr record, magnitude inverted). **No phase plot** — the manual requires one only for periodic variables, and the period search is a documented null. |

## Why this is a variable, not an artifact
**Three instruments** agree — DECam (deep, 2013–2019), ZTF (three non-independent
reductions) and Rubin/LSST. The pre-2018 faint state rests on **seven sparse exposures**:
five consecutive DECam r (23.05–23.44, largely one visit) and two g (23.29, 23.45).
**State it as "faint at the sampled pre-2018 epochs", NOT as "four-plus years of
stability"** — seven exposures cannot exclude unobserved activity in 2013–2017. The bright
state is sampled by hundreds of ZTF epochs.

**The onset bracket crosses filters**: the last faint point is DECam **g**, the first
brighter point is ZTF **zr**, so the bracket carries a colour assumption. The
zr = 21.24 ± 0.26 point should be checked at image level before the onset date is relied on.

**Two contaminating points were excluded** and are documented rather than hidden: a single
PS1 i = 18.65 detection 3.5″ SE (MJD 56531) and a single NEOWISE W1 = 16.2 frame 1.4″ off
(MJD 57887). The field lies at ecliptic latitude −0.12°, which makes asteroid contamination
plausible, but **no ephemeris or trajectory check has been done** — call these *excluded,
suspect measurements*, not confirmed asteroids.

## The AGN alternative (must be disclosed to the moderator)
*Substantially revised — see REVISION 1. The earlier version of this section overstated
the case against AGN and cited a survey that does not cover this position.*

The ALeRCE **stamp** classifier on the Rubin alert returned "AGN 0.88", and DECaLS DR9
carries a photometric redshift (z ≈ 0.93). The strongest competing reading is **a
previously weak nucleus in a faint, unresolved host undergoing sustained activation** — a
faint pre-event source, prolonged later activity, no detected orbital modulation and
pointlike morphology are all compatible with it.

**Honest status: AGN is disfavoured but NOT excluded.** Arguments, with their real limits:

- **Mid-IR.** AllWISE (2010–2011) predates the bright state. **CatWISE2020 runs to 2018-12-13, so it partially OVERLAPS the turn-on** — it is dominated by pre-event epochs and its combined photometry is not a clean bright-state measurement, but it does not categorically predate the event as an earlier version of this draft claimed. The
  LS DR10 forced values are **noise-level flux estimates, not limits**, and are on the **AB**
  system: W1 = 22.1, W2 = 21.8 AB correspond to ≈ **19.40 / 18.46 Vega**. Quoting them as
  deep Vega limits was an error.
  **NEOWISE-R (2014–2024) DOES cover the bright state** and was queried directly: only
  5 detections within 5″ across ~10 yr, scattered over 1.3–4.4″ with W1 σ = 0.29–0.51 at
  the single-exposure limit — consistent with noise, i.e. **no persistent IR counterpart
  before or after the turn-on**. A rigorous contemporaneous limit requires coadd forced
  photometry (unWISE/unTimely), **not yet done**.
- **Radio. FIRST does NOT cover this position** — verified empirically: 0 FIRST sources
  within 1° of the target versus 279 within 1° of a covered control field. The earlier
  citation of FIRST as a non-detection is **withdrawn**. **NVSS coverage IS confirmed**
  (168 sources within 1° vs 151 at control), so the NVSS non-detection stands; it argues
  against a radio-bright blazar but does not exclude a radio-quiet AGN. VLASS coverage has
  not been verified here — do not quote it until it is.
- **UV.** GALEX covers the field but the mission ended in 2013, **before the turn-on**, so
  it cannot constrain bright-state UV emission.
- **X-ray.** "No counterpart" must name the catalogue, epoch, exposure and flux limit
  before it carries weight. Not yet specified — do not quote it as evidence.
- **Amplitude/timescale.** A 5.46-mag rise sustained for 8 yr is outside *ordinary* AGN
  variability, but it does not exclude every nuclear transient: **SDSS1335+0728**
  (Sánchez-Sáez et al. 2024, arXiv:2406.11983) shows long prior inactivity followed by
  years of nuclear activity. A conventional TDE fits poorly given 8 yr of continued
  irregular activity; a long-lived nuclear transient remains possible.
- **The photo-z.** The better argument is not our coadd-aliasing story but that **Legacy
  explicitly excludes stars from photo-z training and does not identify them**, so a
  stellar object can receive a meaningless redshift. Identify the exact DR9 photo-z product
  and its input exposures before relying on either explanation.
- **Classifier scores.** ALeRCE light-curve classifiers rank CV/Nova 0.95–0.97 on the ZTF
  data. Note that **0.88 vs 0.97 is not a Bayesian contest** — different models, inputs,
  taxonomies and training sets; the published ALeRCE stamp model was trained on ZTF.

**Spectroscopic check (2026-09-18, re-verified 2026-09-19): no spectrum FOUND.**
DESI DR1 (`desi_dr1.zpix`) returns zero rows within 30″, and its coverage here is dense
(1,278 spectra in the surrounding 2×2°, vs 502 in a control field) — **a genuine null.**
SDSS DR17 also returns zero, but **SDSS does NOT COVER this position** (0 spectra in the
same 2×2° box vs 1,633 in the control) — **its null is meaningless and must not be cited.**
Correct wording: *no matching spectrum in DESI DR1*; this is not the same as "no spectrum
exists", and it is evidence about archive contents, not about the object's nature.

**Galactic plausibility.** b = **−45.00°**. High latitude does not exclude a CV, but it
penalises a luminous nova-like interpretation: at M_r = +5 with negligible extinction,
r = 18 implies d ≈ 4 kpc and |z| ≈ 2.8 kpc. That is a population prior requiring
justification, not a measured distance; a less luminous CV implies a smaller distance.
High latitude hurts young-star alternatives (FU Ori, YSO) considerably more.

**Alternatives not previously considered** (flagged by external review, none preferred):
FU Orionis-type YSO (a genuine light-curve-shape match — large rise then years of
brightness — but weak at b = −45° with no star-forming environment or IR evidence);
**R Coronae Borealis recovery** from prolonged dust obscuration, which can mimic a turn-on;
classical nova with the eruption peak falling in the observing gap; symbiotic (hard to
reconcile with the faint optical baseline and absent IR); LMXB (needs contemporaneous
X-ray constraints); microlensing (poor fit if the bright state is intrinsically irregular —
test the profile for achromatic lensing shape rather than relying on a periodicity null).

**Relevance to VSX:** the manual states VSX excludes extragalactic objects such as quasars,
though the policy is not an absolute ban. The evidence favours a Galactic accreting system,
but **the moderator must be told the AGN hypothesis is not formally excluded without a
spectrum.** The object is currently ~18.5–19 and reachable by a 2 m class telescope.

## Qualification check against the AAVSO VSX manual
| Requirement | Status |
|---|---|
| Proven variable; no sparse/incomplete light curves | **PASS, overwhelmingly** — 13 yr, 5.46 mag range. NOTE: the ~840 catalogue epochs and 2,354 ZFPS epochs are **overlapping measurement records of shared exposures, NOT unique independent observations** — do not sum them |
| Data-mined submissions held to a higher bar ("do some work, such as period analysis") | **PASS** — full period + eclipse search with injection-tested sensitivity limits (scoped as in the Period field), a quantified null rather than silence |
| Accurate coordinates from an astrometric catalog | **PASS** — LS DR10, Gaia-referenced. Note PSF morphology is not proof of a stellar nature, and the 0.04″ agreement with the Rubin position is a consistency check, not a measure of absolute astrometric accuracy; quote the LS positional uncertainty if the moderator asks |
| Max and min magnitudes | **PASS, with two caveats stated** — (a) cross-system (ZTF zr max vs DECam r min); (b) the faintest single point is not automatically the best faint-state estimate; five consecutive exposures spanning 0.39 mag would be better represented by a weighted flux estimate with uncertainties |
| Period + epoch **for periodic variables** | **N/A** — **no period detected** under the searches and sampling described (not the same as proven aperiodic); turn-on epoch given instead |
| Supporting plot, magnitude inverted | **PASS** |
| Primary name should not be a Gaia designation | **PASS** — ZTF survey ID used |
| Galactic object | **NOT PROVEN.** (Not the *only* open criterion — see the outstanding list in REVISION 6.) No spectrum exists (DESI DR1 + SDSS DR17 both null within 30″, positive-controlled). Disclosed to the moderator rather than glossed |
| Minor-planet check | **PARTIAL** — the source itself persists 8 yr at a fixed position, which establishes it is stationary. The two rejected single-epoch measurements are **suspect, not identified**: no ephemeris or trajectory check was run, so they cannot be called confirmed asteroids |

**Verdict: qualifies as a variable; the Galactic-vs-extragalactic question is NOT closed.**
Recommended action: submit as **VAR** with the AGN alternative disclosed in the remarks,
rather than asserting `CV:`. The object is unambiguously a large-amplitude variable — that
part is overwhelming — but the type and the eligibility question both hinge on a spectrum
that does not currently exist in any public archive.

**Novelty/priority note:** catalogue-clean is not the same as discovery priority. This
object was *detected* by ZTF (hence the ZTF19abxfaon identifier) and alerted on by Rubin;
what is new is that it has never been *classified* or *catalogued as a variable*. TNS was
checked (clean within 60″ on 2026-09-18). State the distinction plainly in the submission.

## Disclosure
Algorithm-found (AI-assisted archival mining of Rubin/ZTF/DECam public data),
human-refereed, filed by the user under their own name.


---

# REVISION LOG (2026-09-18, after external adversarial review)

An external review (OpenAI gpt-6-astra, high reasoning effort, prompted as an adversarial
VSX referee) was commissioned before filing. Its verdict was **hold and correct**. Each of
its claims was independently verified here before being accepted; three were confirmed as
real errors, one was unfair, and its headline recommendation returned a null.

**REVISION 1 — survey constraints corrected (CONFIRMED ERRORS).**
- **FIRST withdrawn.** Verified empirically: 0 FIRST sources within 1° of the target vs
  279 within 1° of a covered control field. We cited a radio survey that never observed
  this position. *An empty catalogue search is not a non-detection.*
- **NVSS retained** — coverage verified (168 within 1° vs 151 at control).
- **GALEX reframed** — the field is covered, but the mission ended in 2013, before the
  turn-on, so it cannot constrain the bright state.
- **WISE corrected** — AllWISE/CatWISE2020 predate the bright state; the LS DR10 forced
  values are noise-level AB estimates (≈19.40/18.46 Vega), not deep Vega limits.
  NEOWISE-R was queried directly and shows no persistent counterpart (5 near-limit
  detections scattered over 1.3–4.4″ in ~10 yr).
- **X-ray and VLASS claims suspended** until catalogue, epoch and flux limit are specified.

**REVISION 2 — classification softened.** Z Cam withdrawn (no standstills observed);
"state cycling" misdescribed a single observed transition; VY Scl not demonstrated (though
not excluded). `VAR` is now the recommended submission type.

**REVISION 3 — logical and provenance errors fixed.**
- "No eclipses → low inclination or non-periodic" was **scientifically wrong** and is removed.
- The 20/20 injection recovery is scoped (95% binomial lower bound 0.83, for the injected
  waveforms only) rather than presented as completeness.
- "Four independent instruments" corrected to **three**, with ZTF's three reductions
  explicitly marked as sharing exposures and calibration.
- "Four-plus years of stability" corrected to "faint at the sampled pre-2018 epochs".
- Asteroid identifications downgraded to "excluded, suspect measurements" (no ephemeris check).
- "Below all their depths" replaced with the measured statement, "no catalogue counterpart found".

**REVISION 4 — new evidence obtained.** DESI DR1 and SDSS DR17 searched for a spectrum:
**zero rows within 30″**, both positive-controlled. The reviewer's highest-impact
suggested check therefore cannot be performed for this object.

**Where the reviewer was wrong:** it asserted the novelty check omitted TNS — TNS *was*
checked (clean, 60″, 2026-09-18). Its galactic-latitude correction addressed an imprecision
in the prompt, not in this draft, which never stated b; the verified value (−45.00°) is now
included.

**OUTSTANDING before or alongside filing:**
1. Audit the ZFPS reference-image epochs for this field/filter — if the reference postdates
   the 2018 turn-on it contains the source and distorts the difference photometry.
2. Compute a contemporaneous mid-IR limit from unWISE/unTimely coadds.
3. Specify or drop the X-ray and VLASS constraints.
4. Optionally re-derive the faint state as a weighted flux estimate with uncertainties.


---

# REVISION 5 (2026-09-19) — the two missing checks, now run

Both gaps flagged at the end of REVISION 1 have been closed. **Both outcomes favour the
Galactic (CV) reading.**

## 1. NEOWISE-R: NO mid-IR counterpart — and this test covers the bright state

AllWISE (2010–11) predates the 2017–18 turn-on. CatWISE2020 runs to 2018-12-13 and so only
partially overlaps it, dominated by pre-event epochs — neither gives a clean bright-state test. **NEOWISE-R (2014–2024) does.** Single-exposure query within 5″:

| | detections within 5″ |
|---|---|
| target position | **5** (over ~10 yr; W1 16.2–17.0, at/below the ~16.5 single-exposure limit) |
| **blank-sky control, 60″ away** | **10** |
| position scatter at target | median 3.74″, max 4.37″ |

The target yields FEWER detections than adjacent blank sky, and they scatter over 3–4.4″,
which no real point source does. **There is no mid-IR counterpart.**
(Contrast the sibling object nsc_97192_2072, a probable AGN: 180 NEOWISE detections,
tightly clustered, W1 = 15.4.)

**Why this matters for classification.** In the bright state the object is r ≈ 18.5. Typical
quasar colours are r − W1 ≈ 3.5–5.5 (Vega), implying **W1 ≈ 13–15** — two to three
magnitudes above NEOWISE's limit, an unmissable detection. Even an unusually IR-weak AGN
(r − W1 ≈ 2) would sit at W1 ≈ 16.5, marginally detectable. **A non-detection at this
optical brightness is difficult to reconcile with an AGN**, and is exactly what a
cataclysmic variable (hot accretion disc, no dust) predicts.
This replaces the earlier, invalid version of the argument, which used epochs predating the
bright state and quoted AB fluxes as Vega limits.

## 2. Spectroscopy: DESI covers this field and has no spectrum here

| survey | spectra within 30″ | spectra in surrounding 2×2 deg | verdict |
|---|---|---|---|
| **DESI DR1** (`desi_dr1.zpix`) | **0** | **1,278** (control field: 502) | **genuine null — field densely covered** |
| SDSS DR17 (`sdss_dr17.specobj`) | 0 | **0** (control field: 1,633) | **NO COVERAGE — null is meaningless, do not cite** |

**Do not quote SDSS as a spectroscopic non-detection for this object.** It does not observe
this position. The coverage test that caught this is the same one that withdrew the FIRST
radio claim in REVISION 1.

DESI's null is real and means only that no spectrum has been taken — it is not evidence
about the object's nature either way.

## Net effect

The strongest pro-AGN evidence remains the ALeRCE **stamp** classifier (AGN 0.88) and the
DECaLS DR9 photo-z (~0.93), both of which are weak instruments here: the stamp model was
trained on ZTF, and Legacy excludes stars from photo-z training so a stellar object can
receive a meaningless redshift.

Against them now stands a **contemporaneous, control-verified mid-IR non-detection** at an
optical brightness where an AGN should be an easy WISE source.

**The Galactic CV reading is materially strengthened.** It is still not proven — that needs
a spectrum, and none exists — but the extragalactic alternative is now the weaker of the two.
Recommended submission type remains **VAR** pending review; `CV:` is more defensible than it
was in REVISION 2.


---

# REVISION 6 (2026-09-19) — second adversarial review; internal contradictions repaired

Second independent adversarial review commissioned (gpt-6-astra). **Verdict: HOLD.**
*"File only after an object-specific provenance and photometry audit, actual spectrum
searches, and credible affirmative evidence of Galactic stellar membership, or explicit
moderator agreement to accept the unresolved case; `VAR` plus disclosure alone is
insufficient."*

## Reviewer error caused by a faulty prompt — recorded for honesty

The review's headline finding was *"results from the wrong object — the NEOWISE detections
and DESI/SDSS searches are not evidence about this target."* **That is wrong, and it is our
fault.** The prompt supplied to the reviewer stated that NEOWISE and the spectrum checks had
not been run for this object. They HAD been, at this object's own coordinates
(326.828336, −13.474691), and an independent re-run on 2026-09-19 reproduced them exactly
(5 NEOWISE detections, W1 ≈ 16.7–16.9; DESI/SDSS both zero). The sibling object returns 180
NEOWISE detections at a completely different position. The reviewer reasoned correctly from
a false premise we gave it.
**Lesson: a referee is only as good as its brief; verify the context you hand it.**

## CONFIRMED CONTRADICTIONS — all repaired in this revision

The earlier revisions corrected claims in one part of the document and left the old wording
elsewhere. Every one of these was real:

| was | now |
|---|---|
| title: "state-cycling variable" | "one observed transition" (REVISION 2 withdrew cycling; the title had not been updated) |
| "below all of their depths in quiescence" | "no counterpart is FOUND" — optical faintness does not establish IR faintness |
| "~840 calibrated epochs + 2,354 forced-photometry epochs" | labelled as overlapping records of shared exposures, **not** to be summed |
| "documented aperiodic" | "no period detected under the searches described" |
| minor-planet check "PASS — two asteroid contaminants identified" | "PARTIAL — suspect, not identified; no ephemeris check was run" |
| "CatWISE2020 (2010–2018) predates the bright state" | CatWISE2020 runs to **2018-12-13** and partially OVERLAPS the turn-on |
| "NO spectrum exists" | "no matching spectrum in DESI DR1"; **SDSS does not cover this position** so its null is void |

**This is the same failure as the ZTF18abxnwmb eclipse duration: a correction written in one
section and not propagated. Standing rule, now twice earned — when a correction is made,
grep the entire document for the superseded wording.**

## The strongest remaining argument AGAINST a Galactic CV (reviewer's, and it is good)

**Luminosity–scale-height tension.** b = −45.00°. With the draft's assumed M_r = +5
(appropriate for a nova-like/high-state CV) and negligible extinction, r = 18 gives
d ≈ 4 kpc and **|z| ≈ 2.8 kpc above the Galactic plane**. Published CV population studies
use scale heights of a few hundred parsecs. That is uncomfortable for an ordinary
disc-population CV.

**Conditional, not fatal:** M_r is unmeasured; a less luminous system sits closer. But this
is the one substantive anti-CV argument in the file and it must be stated in any submission.

The reviewer also notes the DECaLS photo-z is **not** independent evidence of a galaxy —
Legacy states its photo-z product performs no star–galaxy separation, so a stellar source
can receive a meaningless redshift. That weakens the pro-AGN side.

## OUTSTANDING before filing (none are text edits)

1. **ZFPS flux-reconstruction audit.** A reference containing the source is *normal* for
   difference photometry; the question is whether total flux was correctly reconstructed.
   Reference dates alone do not settle it. Until audited, the ZFPS-derived magnitudes and
   the injection sensitivity that depends on them should be omitted.
2. **Quantitative bright-state mid-IR limit** with uncertainties and coverage — a catalogue
   non-detection is a first step, not the discriminator. LS DR10 WISE incorporates NEOWISE
   through year 7; retrieve fluxes and errors rather than treating two magnitudes as limits.
3. **Measurement uncertainties on the extrema**, and a check that the faintest single point
   is a sound faint-state estimate rather than a downward excursion.
4. **A finding chart** — VSX asks for one where a faint object lacks major-catalogue
   counterparts and identification could be confused. That is exactly this object.
5. **ALeRCE classifier provenance** — record object ID, input survey, model name and
   version. ALeRCE now runs a separate Rubin stamp classifier; citing the published ZTF
   model does not identify what produced the 0.88.
6. **Pre-submission eligibility inquiry to a VSX moderator** is the reviewer's recommended
   route, rather than filing and hoping disclosure settles eligibility.

**Status: HELD. Not filable in its current state.**


---

# REVISION 7 (2026-09-19) — second independent review (Fable); three verified corrections

A second, independent adversarial review was run in parallel with the gpt-6-astra pass,
pointed at the repository files rather than at a summary. It re-derived the numbers from raw
photometry and found three substantive errors, **all verified here before acceptance**.

## 1. The quoted MAXIMUM was a bad measurement — WITHDRAWN

| epoch | mag | limitmag | mag−lim | sharp | airmass |
|---|---|---|---|---|---|
| MJD 59218.078 (**old max, withdrawn**) | 17.976 | **18.29** | −0.31 | **+0.682** | 2.03 |
| MJD 60577.254 (**adopted max**) | 18.337 | 21.04 | −2.70 | −0.062 | 1.60 |
| MJD 60577.254 (partner frame) | 18.405 | 21.34 | −2.94 | +0.026 | 1.38 |

`limitmag 18.29` is **the shallowest of all 272 clean zr frames** (median 20.69; next
shallowest 18.77), and `sharp +0.682` is far outside the −0.089…+0.026 spread of the next
five brightest epochs.
**This is the identical diagnostic signature — shallow frame plus anomalous `sharp` — that
this project used to convict a turn-on-lane candidate as a single-epoch artifact on the same
day (commit 1c1263b). It was applied there and missed here.**

Consequence: **maximum 17.98 → 18.34; amplitude 5.46 → ≈ 4.8.**

## 2. "State cycling" was REAL — REVISION 2 over-corrected, and is reversed

REVISION 2 withdrew the state-cycling description on a reviewer's assertion that it
"misdescribed a single observed transition." **That assertion is false against our own data.**
Clean ZTF zr yearly medians:

| 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| 20.42 | 19.72 | 18.89 | 18.63 | **20.61** | 19.31 | 19.00 | **21.33** |

A turn-on, then **~2-mag reversals in 2022 and 2025 with recoveries in between**, never
returning to the pre-2018 level (~23). That is state changing, and it is VY Scl-like.
**Lesson, and the worst error in this file's history: a confident reviewer assertion was
accepted over data already in hand. Verify the referee against the data, not only the data
against the referee.**

## 3. The strongest Galactic evidence was mislabelled "not yet done"

The draft said a contemporaneous mid-IR limit "requires coadd forced photometry
(unWISE/unTimely), **not yet done**" — two lines after quoting the LS DR10 forced W1/W2,
which **is** exactly that product. LS DR10 force-photometers all imaging through NEOWISE-R
year 7 in the unWISE maps.

| | |
|---|---|
| `nobs_w1` | **192** |
| flux_w1 | 1.425 ± 0.545 nMgy (2.6σ) |
| **3σ limit** | **W1 > 19.27 (Vega)**, on a 2010–2020 coadd including ~2.5 yr of bright state |

Expected W1 at r ≈ 19: quasar with a dust torus ≈ **14.3** (excluded by ~5 mag); IR-weak AGN
≈ **16.3** (excluded by ~3 mag); hot dust-free accretion disc ≈ 17.8 or fainter (consistent).
The measured colour is **r − W1 ≈ −0.6** — very blue, which is what an accretion disc looks
like and what an AGN does not. Even allowing for coadd dilution of the bright state, a normal
torus would appear at ~80σ.

**This, not the spectrum, is the primary Galactic argument. Promoted accordingly.**

## 4. Further corrections applied

- **Photo-z was misquoted.** Not "z ≈ 0.93": LS DR10 gives median **1.118**, mean 1.267,
  σ 0.430, **95% range 0.778–2.270**, `training = f`, no spectroscopic z. A galaxy-trained
  estimate with that range on a **PSF** source is content-free. Quote the range or drop it.
- **ZTF reference epochs, previously "OUTSTANDING", resolved in one query.** Both zr
  references (field 391 ccd 4 q 3; field 340 ccd 14 q 2) were built from 28 and 23 frames,
  **2018-06-07 → 2018-11-21** — entirely post-turn-on, containing the source at its 2018
  level. Therefore **a ZFPS "non-detection" means "at the 2018 reference level", not
  "faint"**, and ZFPS difference magnitudes are biased faint. Any ZFPS-derived magnitude or
  injection sensitivity must be recomputed before use, or omitted.
- **Minimum re-derived** from the LS DR10 coadd (23.12 ± 0.08, 13.9σ) rather than a single
  NSC exposure at the frame limit.
- **The MJD 58372 DECam pair must be disclosed**: r = 23.13 and 22.03 thirteen minutes apart
  on 2018-09-11, while ZTF measured 20.34/20.36 three days earlier. Either the source drops
  ≥2.8 mag within hours, or NSC single-exposure photometry is unreliable by 1–3 mag here —
  and the same photometry supplied the old minimum. **Unresolved; state it rather than drop it.**
- The inclination error ("consistent with a low-inclination system") still survives in
  `rubin_pilot_2026_07_14/forensics/170587115976392822/consumer_package/astronote_draft.md`,
  in `RESEARCH_LOG.md`, and in the object journal. **If the AstroNote is ever sent, the error
  ships.** Fix before any use.

## Net effect on classification

The Galactic CV reading is **materially stronger** than at REVISION 6: the object genuinely
cycles between states, the mid-IR coadd limit excludes a dusty AGN by ~5 mag, the source is
PSF-like, and the photo-z that anchored the extragalactic case is content-free.

The one substantive counter-argument remains the **population prior**: a sustained
accretion-disc high state at M_r ≈ +4…+6 puts r ≈ 19 at d ≈ 3–8 kpc and |z| ≈ 2–6 kpc at
b = −45°, where nova-likes are rare. The reviewer explicitly rejects the escape offered in
an earlier note — that a less luminous disc sits closer — on the grounds that a disc that
faint does not hold r ≈ 19 for eight years. **That objection stands unanswered and must be
carried into any filing.**

**Status: still HELD, but the blocking issue has changed.** It is no longer "we need a
spectrum" — this reviewer's position is that no spectrum is needed to file a **VAR**. The
remaining blockers are the plot regeneration, the MJD 58372 pair, and the ledger rows.


---

# REVISION 8 (2026-09-19) — the MJD 58372 DECam pair is RESOLVED

The last blocking item. Both parts resolve, and the second one is **new evidence for the
classification**.

## Part 1 — the 13-minute 1.1 mag difference is INSTRUMENTAL

`c4d_180911_022036_ooi_r_ls9` → r = 23.133 ± 0.125; `c4d_180911_023339_ooi_r_ls9`
→ r = 22.026 ± 0.073, 13 minutes later. Both `flags = 0`, both real detections, formally
a 7.6σ difference.

**Control: 368 objects measured in BOTH exposures within ~6′ of the target.**

| mag | n | scatter (A−B) | max \|A−B\| |
|---|---|---|---|
| 17–19 | 27 | 0.007–0.017 | 0.05 |
| 20 | 34 | 0.070 | 0.36 |
| 21 | 67 | 0.111 | 0.43 |
| 22 | 125 | 0.221 | 0.62 |
| **23** | **108** | **0.282** | **1.107** |

Our target's +1.107 **is the maximum of the mag-23 bin**, and **1 of 305** faint objects
exceeding 1.0 mag. Against the empirical scatter that is 3.9σ — about the expected extreme
of 305 draws. **No astrophysical variability is required; this is the tail of faint-end
single-exposure scatter.**

Adopted combined value: weighted mean **r = 22.31 ± 0.06 (formal)**, and with the empirical
exposure-pair systematic, **r ≈ 22.3 ± 0.3**.

## Part 2 — the DECam-vs-ZTF discrepancy is CENSORING, not conflict

ZTF said zr = 20.146 ± 0.147 on MJD 58366.32, **1.13 mag above that frame's limit — a secure
detection.** DECam then measured r ≈ 22.3 on MJD 58372.10. That looked irreconcilable.

It is not. **ZTF DR light curves list only DETECTIONS.** With a limiting magnitude near
20.5–21.3, ZTF *cannot* record this source at r ≈ 22–23 — those epochs produce no row at all.
DECam, 2+ mag deeper, sees what ZTF is blind to.

| MJD | instrument | r | note |
|---|---|---|---|
| 58363.27 | ZTF | 20.48 | at frame limit |
| **58366.32** | **ZTF** | **20.15** | **secure, 1.13 mag above limit** |
| 58369.36 | ZTF | 20.34 / 20.36 | |
| **58372.10** | **DECam** | **≈ 22.3 ± 0.3** | **below ZTF's limit — invisible to ZTF** |
| 58378.02 | DECam | z = 21.39 | recovering |
| 58406.02 | DECam | z = 21.49 | |

**This records a real ~2.2 mag drop in 5.8 days, and a recovery within ~6 days.**

### Why this matters for the classification

1. **It is direct evidence of fast, deep state changes** — exactly VY Scl behaviour, and it
   strengthens the REVISION 7 reinstatement of state changing over "one transition".
2. **It shows the ZTF light curve is CENSORED, so every ZTF-only statement about this object
   is biased bright.** The annual zr medians in REVISION 7 are medians *of detections*; the
   true low states are deeper than they appear. "Never returning to the pre-2018 level"
   remains supported by the DECam data, but must not be argued from ZTF alone.
3. The pair should be **disclosed and explained** in the submission, not dropped — it is the
   single best-sampled low-state measurement in the record.

**With this resolved, the outstanding blockers from REVISION 6/7 are cleared except the
population-prior objection (M_r vs |z| at b = −45°), which is argumentative rather than
factual, and the ledger/finding-chart items.**

---

# REVISION 9 (2026-09-19) — NEAR-INFRARED DETECTION; the scale-height objection is answered

A systematic survey of the photometric archives VSX and the variable-star literature actually
use (ASAS-SN, ZTF, CRTS, SuperWASP, NSVS, ATLAS, TESS, Gaia epoch photometry, plus the deep
imaging catalogues) turned up **one source not previously used for this object, and it is
decisive for the distance.**

## VHS DR5 (VISTA Hemisphere Survey) — first near-IR detection

| | |
|---|---|
| separation | **0.167″** |
| epoch | **MJD 56090.30 = 2012-06-12 — PRE turn-on** |
| **J (Vega, ap3)** | **19.8268 ± 0.1790** |
| Y (Vega, ap3) | 20.8605 |
| classification | Jclass = −1 (stellar), Yclass = 1 (extended), pStar = pGal = **0.486** — ambiguous |
| extinction | E(B−V) = 0.0405, A_J = 0.038 (negligible) |

The epoch matters: 2012 is contemporaneous with the DECam faint state, so this is the
**quiescent** near-IR, not the bright state.

## The colour identifies the donor

Faint state r(AB) = 23.12 with J(Vega) = 19.83 gives **r − J (Vega) = 3.13**.

| spectral type | r − J (Vega) |
|---|---|
| K | ~1.5 |
| M0 | ~2.2 |
| **M3–M4** | **3.1–3.5** ← observed 3.13 |
| M6 | ~4.5 |

That is the signature of an **M3–M4 dwarf donor** — exactly what dominates the near-IR of a
cataclysmic variable in a low state, when the disc has faded and the secondary shows through.

## An independent distance, and it resolves the standing objection

Taking the near-IR as donor-dominated:

| donor | M_J | d | \|z\| at b = −45° |
|---|---|---|---|
| M2 | 8.2 | 2.12 kpc | 1.50 kpc |
| **M3** | **8.7** | **1.68 kpc** | **1.19 kpc** |
| **M4** | **9.2** | **1.34 kpc** | **0.94 kpc** |
| M5 | 9.9 | 0.97 kpc | 0.68 kpc |

**This is the third independent line converging on d ≈ 1.3–1.7 kpc**, after (i) the
self-consistency of the bright and faint states with CV absolute magnitudes (M_r ≈ +8 in the
high state implies M_r ≈ +12.7 in quiescence, textbook white-dwarf-dominated), and (ii) the
same argument's distance of ≈1.3 kpc.

**The standing counter-argument assumed M_r = +4…+6 for a sustained nova-like high state and
derived d = 3–8 kpc, |z| = 2–6 kpc — a population problem.** The near-IR removes the
assumption: the donor's absolute magnitude is far better constrained than the disc's, and it
puts the system at **|z| ≈ 0.9–1.2 kpc**. That is high, and still requires an old-population
CV, but it is no longer the several-kiloparsec outlier the objection was built on.

## Honest limits

- The J detection is 5.6σ (0.179 mag); Y is a single measurement.
- **VHS's own morphology is ambiguous** (pStar = pGal = 0.486), so this does not settle
  star-vs-galaxy on its own. A red r − J is also achievable by a galaxy at z ≈ 1.
- The donor interpretation assumes the near-IR is secondary-dominated. That is standard for
  CVs in low states but is an assumption, not a measurement.
- What makes the CV reading hold together is the **combination**: the M3–M4 colour, the
  unWISE limit W1 > 19.27 Vega excluding an AGN torus by ~5 mag, the point-source morphology
  in the bright state, and above all the **2.16 mag drop in 5.8 days** — a timescale no
  luminous AGN at a cosmological distance can produce.

## Surveys checked and what each can say

| survey | covers target? | verdict |
|---|---|---|
| **VHS DR5** | **yes** | **J = 19.83 (2012) — the new constraint above** |
| PTF / iPTF | yes (506 rows within 2′) | epochs 2009-06 → 2014-11 only, **none after**; cannot constrain the 2017–18 turn-on. Non-detection consistent with r ≈ 23 vs PTF's R ≈ 21 limit |
| SkyMapper DR4 | yes (64 sources within 3′) | genuine non-detection |
| SDSS | **no coverage** | null is void |
| PS1 DR1 | no rows | r ≈ 23.1 is at the PS1 stack limit |
| DELVE DR2, DES DR2 | no coverage | void |
| CRTS / ASAS-SN / SuperWASP / NSVS / TESS | n/a | depth V ≈ 15–20, far too shallow for r ≈ 23; CRTS also ended 2013, before the turn-on |
| Gaia epoch photometry | no source | below Gaia's limit in quiescence |

---

# REVISION 10 (2026-09-20) — the two remaining items verified; ALeRCE provenance retrieved

REVISION 8 closed with: *"the outstanding blockers from REVISION 6/7 are cleared except the
population-prior objection … and the ledger/finding-chart items."* REVISION 9 then answered the
population-prior objection. **No status line was written after REVISION 9**, so the headline at the
top of this document still reads "HELD" from REVISION 6 and is stale. The remaining items were
checked one by one.

## Item-by-item verification of the six REVISION 6 blockers

| # | item | state |
|---|---|---|
| 1 | ZFPS flux-reconstruction audit | **DONE** (rev 7): a ZFPS "non-detection" means *at the 2018 reference level*, not faint; ZFPS difference magnitudes are biased faint and are excluded from the quoted extrema |
| 2 | Quantitative bright-state mid-IR limit | **DONE**: unWISE W1 > 19.27 Vega, excluding an AGN torus by ~5 mag |
| 3 | Uncertainties on the extrema | **DONE** (rev 7): max 17.98 **withdrawn** → 18.34 on frame-quality grounds; min re-derived as 23.12 ± 0.08 from the LS DR10 coadd (13.9σ) rather than a single exposure |
| 4 | Finding chart | **DONE this revision** — `ZTF19abxfaon_finding_chart.png` |
| 5 | ALeRCE classifier provenance | **PARTIAL** — ZTF side fully retrieved below; the Rubin side could not be reached |
| 6 | Pre-submission moderator eligibility inquiry | **USER ACTION** by design, not a defect of the package |

## Item 4 — finding chart produced

`ZTF19abxfaon_finding_chart.png`: two panels from Legacy Survey DR10 grz — a 5′ × 5′ pointing
field and a 52″ × 52″ identification zoom, with N/E compass, scale bars, and **8 comparison stars
from PS1 DR2 (r = 16.37–18.16)** labelled A–H with g and r magnitudes.

Two deliberate choices. A ninth, brighter star at r = 13.65 was **excluded**: it is saturated in the
coadd with visible diffraction spikes and a bleed trail, and would be unusable as a photometric
comparison. And the chart carries an explicit warning that **the DR10 coadd averages mostly
pre-2018 DECam imaging, where the object sits near its faint state (r ≈ 23.1)** — it is currently
r ≈ 18.5–19 and will appear far brighter at the telescope. A finding chart that silently showed the
faint state would mislead an observer into doubting the identification.

## Item 5 — ALeRCE provenance, and a correction that matters

The blocker was that "ALeRCE stamp classifier AGN 0.88" did not identify *which* model produced it.
The **ZTF-side** record is now retrieved in full from the ALeRCE API: oid `ZTF19abxfaon`,
**ndet = 660**, firstmjd 58732.23, **lastmjd 61303.25 (still being detected as of 2026-09-19/20)**,
`corrected = True`, `stellar = False`. Nineteen classifiers report, with names and versions:

| classifier | version | top class | p |
|---|---|---|---|
| LC_classifier_ATAT_forced_phot (beta) | 0.3.1 | **CV/Nova** | **0.954** |
| LC_classifier_ATAT_forced_phot (beta) | 1.0.0 | **CV/Nova** | **0.936** |
| lc_classifier_stochastic | hierarchical_rf_1.1.0 | **CV/Nova** | **0.888** |
| lc_classifier_BHRF_forced_phot_stochastic | 2.1.0 | CV/Nova | 0.672 |
| stamp_classifier_2025_beta | 2.1.1_beta | SN | 0.920 |
| stamp_classifier | stamp_classifier_1.0.4 | SN | 0.705 |

**Across all nineteen ZTF-side classifiers the maximum AGN probability is 0.069** (stamp_classifier
1.0.0); the light-curve classifiers put AGN at 0.012–0.031. On ZTF data, ALeRCE does not support an
AGN reading at all — its best models call this a CV.

**A coincidence that should be checked, not asserted.** The value 0.88 appears in the ZTF record as
**CV/Nova 0.8880** from `lc_classifier_stochastic`. This document attributes "AGN 0.88" to the
*Rubin* stamp classifier, which is a different pipeline on different data, so this is **not proof of
a transcription error** — but the numerical coincidence is close enough that the Rubin-side value
should be re-read from its source before "AGN 0.88" is repeated in a submission.

**What could not be done from here:** the ALeRCE **LSST/Rubin** API endpoints
(`/lsst/v1/objects/170587115976392822`, `…/probabilities`, `/v2/objects/…`) all failed to respond.
The Rubin-side model name, version and probability therefore remain unverified, and item 5 stays
**PARTIAL**. Note also that the Rubin public alert stream has been dark since MJD 61235, so the
Rubin-side record is in any case a snapshot of a stalled feed.

## Item — ledger rows verified complete

`docs/object_journals/170587115976392822.md` carries a 15-row cross-check ledger, and it already
includes rows for the two newest evidence items: **NSC DR2 meas — MJD 58372 exposure pair**
(rev 8) and **VHS DR5 near-IR** (rev 9). It was last committed with REVISION 9, so it is current.
This item is **DONE**.

## Status

**The package's own blockers are cleared.** What remains is (a) the Rubin-side ALeRCE provenance,
unreachable from this machine and weak evidence in any case given the ZTF-side result and the
mid-IR limit, and (b) the moderator eligibility inquiry, which is the user's action by design.
`stellar = False` from ALeRCE is recorded here as an honest point against the stellar reading,
though that flag derives from star–galaxy separation that is unreliable for faint blue objects.

**This revision does not itself authorise filing.** It records that the technical blockers listed
in REVISION 6 are closed, and that the "HELD" headline at line 333 is stale and should be read
together with this section.
