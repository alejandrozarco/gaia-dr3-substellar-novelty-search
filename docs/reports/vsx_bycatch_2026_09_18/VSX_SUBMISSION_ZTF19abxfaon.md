# VSX submission draft — ZTF19abxfaon (uncatalogued high-amplitude variable, one observed transition)
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
| Variability type | **VAR** recommended (see REVISION 2). Large-amplitude variable showing a transition from a sparsely sampled faint state to prolonged activity; **CV candidate**, extragalactic origin unresolved. `CV:` is offered only if the moderator prefers it. **Z Cam is withdrawn** (no dwarf-nova outbursts with standstills are observed); **VY Scl is not demonstrated** (though a rise does not exclude it, since a low state could predate our coverage) |
| Maximum (brightest) | **17.98 r** (ZTF zr, MJD 59218.078 = 2021-01-04) |
| Minimum (faintest) | **23.44 r** (DECam r via NSC DR2, MJD 56511.240 = 2013-08-07) |
| Amplitude | **5.46 mag observed range** (23.44 − 17.98; ≈153× in flux). This is a **cross-system observed range, NOT a single-passband amplitude**: max is ZTF zr, min is DECam r. Quote both filters and uncertainties in the remarks |
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
