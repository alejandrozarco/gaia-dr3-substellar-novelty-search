# PLATO field cross-match + confirmation-route analysis (2026-05-17)

Prompted by the NOS article on PLATO ("op zoek naar tweelingzusje van de
aarde"), this note records how the ESA PLATO mission (launch Dec 2026)
intersects our candidate list, and why PLATO is a confirmation route
worth tracking alongside Gaia DR4.

## Why PLATO is complementary to our pipeline

PLATO detects planets/companions by **transit photometry** — it requires
the orbit to be edge-on (inclination i ≈ 90°). Our pipeline detects
companions by:

- **Astrometric wobble** (NSS Orbital) — strongest for face-on orbits
- **RV reflex** (NSS SB1) — inclination-degenerate (measures M_2 sin i)
- **Proper-motion anomaly** (HGCA / Tycho-Gaia) — inclination-dependent

None of our channels require — or favor — edge-on geometry. So PLATO is
exactly orthogonal: it samples the inclination regime our pipeline is
blind to.

**This breaks our single biggest caveat.** Our FLAG-tier candidates
(HD 83408, HD 153386, HD 221068) are mass-ambiguous *because* a high PMa
χ² is consistent with either (a) a substellar companion at moderate
inclination or (b) a stellar companion near face-on, where M_2 sin³(i)
makes the apparent mass small. If PLATO sees a transit, i ≈ 90° is pinned,
sin(i) ≈ 1, and M_2 sin(i) ≈ M_2 → the SB1 minimum mass becomes the true
mass → instant substellar confirmation (or refutation). A 13-80 M_J brown
dwarf has roughly Jupiter radius, producing a ~1-2% transit depth — far
above PLATO's noise floor for V < 11 hosts.

## Field cross-match (27 candidates)

### LOPS2 (confirmed southern long field, 2-yr stare)
Center: galactic (l,b)=(255.94°, -24.62°) → RA=95.32°, Dec=-47.89°.
2232 sq deg (~5.4% of sky).

**0 of 27 candidates in LOPS2** (nearest: HD 11042 at 39.8° from center,
well outside the ~24° field radius). Statistically expected: 27 × 0.054
≈ 1.5; Poisson P(0) ≈ 0.22.

### LOPN1 (provisional northern long field)
Center: galactic (l,b)=(81.56°, +24.62°) → RA=277.19°, Dec=+52.86°.

**2 of 27 candidates in the LOPN1 deep field (≥24 cameras):**

| Candidate   | sep from LOPN1 | P (d) | M_2_marg (MJ) | V    | Channel                       |
|-------------|---------------:|------:|--------------:|-----:|-------------------------------|
| BD+46 2473  | 5.9°           | 496   | 74            | 8.97 | multi-body PMa-excess (inner) |
| BD+37 3282  | 15.5°          | 1015  | 38            | 8.30 | widened-502 Tycho-Gaia CORROB |

**Caveat on LOPN1**: the northern field is *provisional*. PLATO's
confirmed plan is LOPS2 (south) for the first 2 years; the second
long-pointing phase (LOPN1 vs a step-and-stare program) is not yet
finalized. So these 2 are "potential PLATO targets if the northern field
is observed."

## Transit vs asteroseismology: which PLATO product helps us

### Transit detection — unlikely for the 2 in-field candidates
Both in-field candidates have long periods:

- BD+46 2473: P=496 d (1.36 yr). PLATO 2-yr stare → ~1.5 orbits → 1-2
  possible transits *if* edge-on. Geometric transit probability ≈ R_*/a
  ≈ 0.3%.
- BD+37 3282: P=1015 d (2.8 yr). PLATO 2-yr stare → <1 orbit → at most 1
  transit, probably 0. Transit confirmation effectively ruled out.

Neither is a good transit target. Our short-period candidates (HD 22782
P=14 d, HD 221068 P=62 d, HD 156239 P=110 d) would be *excellent* transit
targets — multiple transits per stare, higher geometric probability — but
none of them fall in LOPS2 or LOPN1.

### Asteroseismology — helps both in-field candidates
PLATO's core deliverable for every bright (V<11) in-field star, regardless
of transits, is asteroseismic characterization:

- Stellar **mass** to ~10%
- Stellar **radius** to ~2%
- Stellar **age** to ~10%

For our SB1 / Pourbaix-mass-function candidates, M_1 is the dominant
systematic in the M_2 estimate (we use `mass_flame` or a 1.0 M_sun
fallback). A PLATO asteroseismic M_1 for BD+46 2473 and BD+37 3282 would
directly tighten their M_2 posteriors. This is a real, if modest, gain
that does not depend on transit geometry.

## Net actionable conclusions

1. **2 candidates (BD+46 2473, BD+37 3282) are in the provisional PLATO
   LOPN1 deep field.** If the northern field is observed, both get
   asteroseismic host characterization → tighter M_2. Transit confirmation
   is geometrically unlikely (periods too long).

2. **PLATO is a genuine third confirmation route** alongside Gaia DR4 and
   ground-based RV — and the only one that resolves the mass-inclination
   degeneracy via transit detection. But it only helps short-period
   in-field candidates, of which we currently have none. This argues for:
   - Prioritizing future candidate searches in the LOPS2 / LOPN1
     footprints (where PLATO transit follow-up is automatic);
   - Proposing our short-period candidates (HD 22782, HD 221068,
     HD 156239) as PLATO guest-observer / step-and-stare targets.

3. **Timeline coincidence**: PLATO launches Dec 2026, the same window as
   Gaia DR4. Both land together — DR4 gives epoch astrometry + epoch RV
   (re-fits every candidate's orbit), PLATO gives transit + asteroseismology
   for the ~5-11% of sky in its fields. The README's "paths to
   confirmation" should cite both.

## No version bump

This is an analysis note, not a candidate-list change. Version stays
v1.16.0. Cross-match script results are reproducible via the LOPS2/LOPN1
field-center coords above + `gaiadr3.gaia_source` ra/dec.
