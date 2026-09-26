# microlensing — astrometric-microlensing event predictor (lane #118)

Predicts upcoming **astrometric microlensing** events: a foreground star (the
*lens*) whose gravity bends the light of a chance-aligned background *source*,
shifting the source's apparent centroid by up to ~`θ_E/(2√2)` and magnifying it.
The centroid shift `δθ` and the magnification `A` both scale with the lens mass
through the angular Einstein radius `θ_E = √(κ·M_L·π_rel)`, so a **measured**
deflection yields a **model-independent gravitational mass** of the lens — even
for an otherwise dark or faint lens (white dwarf, neutron star, black hole). This
is the one mass probe in this project that needs **no luminous companion**.

## Why this lane exists (and its honest limits)

Every other method in this repo needs the dark object to betray itself through a
*luminous companion* (a Gaia NSS astrometric/spectroscopic orbit, an X-ray
accretion signature, an eclipse). Astrometric microlensing is different: the lens
mass is weighed gravitationally, companion-free. **But** there is a hard catch,
and we state it up front:

> **You cannot pre-target a lens you cannot see.** The predictor needs the lens's
> Gaia astrometry (position + proper motion + parallax) to compute *when* and
> *how close* it passes a background source. An **isolated, truly dark** remnant
> emits no light, has no Gaia entry, and therefore **cannot be put on a
> predicted-event list**. Those objects are found only by *monitoring* — Rubin/LSST
> catching the centroid wobble or magnification of a random background star in
> real time, then inferring an unseen lens. This predictor weighs **known**
> foreground objects (and the brightest of them, a high-proper-motion nearby star,
> is almost never the dark remnant we hunt).

So the scientific edge here is narrow and specific:
1. **DR4-readiness.** Gaia DR4 (2 Dec 2026) overhauls *every* astrometric input,
   which re-derives *every* predicted epoch and impact parameter. The physics core
   (`geometry.py`) and the queries are version-agnostic — point `GAIA_TABLE` at
   `gaiadr4.gaia_source` and re-run. Re-runnability *is* the deliverable.
2. **The candidate cross.** We check whether any of *our* compact/substellar
   candidates (`docs/CANDIDATES.md`) — or a high-mass / white-dwarf lens — has an
   upcoming event that would independently weigh its (dark) mass.

This is also **semi-crowded prior art**: predicting astrometric microlensing from
Gaia is an established sub-field (Klüter+2018 A&A 615 L11 & A&A 620 A175;
McGill+2018/2019/2020; Bramich 2018 A&A 618 A44; Klüter+2022; the DR3 update
Kluter+2024 MNRAS 527 1177). Run `scripts/litcheck/prior_art.py "astrometric
microlensing prediction Gaia"` before treating any predicted event as novel. The
honest framing: **this is a method re-implementation + a DR4-ready re-runnable
tool + a candidate cross-check, not a novel discovery channel.**

## Layout

| file | role | network |
|---|---|---|
| `geometry.py` | pure-physics core: `θ_E`, `A(u)`, centroid shift `δθ(u)` (dark-lens + luminous-blend), closest-approach solver (PM + annual parallax), `predict_event`, and the **mass-from-shift inversion**. Deterministic, unit-tested. | none |
| `predict.py` | pipeline: Gaia DR3 high-μ lenses → background neighbours along each lens's 2024–2030 track → ranked predicted-event table (CSV+JSON to `/tmp`). | Gaia TAP |
| `validate.py` | reproduces the published **LAWD 37** event (McGill+2023): `θ_E`, TCA epoch, impact parameter, mass inversion. | 1 fast Gaia query (cached fallback) |
| `apply_candidates.py` | (A) tests whether our candidates are viable lenses 2024–2030; (B) flags predicted events whose lens is a project candidate or a **white-dwarf-locus** object. | Gaia TAP |
| `../../tests/test_microlensing.py` | 13 offline unit tests (physics + LAWD 37 closure). | none |

## The physics (`geometry.py`)

- **Einstein radius** `θ_E[mas] = √(κ · M_L[M⊙] · π_rel[mas])`, `κ = 8.146 mas/M⊙`
  (computed from constants; lit. 8.144). `π_rel = π_L − π_S`. Equivalent textbook
  form `θ_E = √((4GM/c²)(1/D_L − 1/D_S))` is also provided.
- **Magnification** `A(u) = (u²+2)/(u√(u²+4))`, `u = sep/θ_E`.
- **Centroid shift.** For a **dark** lens (no lens light), the light-centroid of
  the unresolved major+minor images is `δθ = u/(u²+2)·θ_E`, peaking at `u=√2`,
  `δθ_max = θ_E/(2√2) = 0.354 θ_E`. A **luminous** lens of flux ratio `g=F_L/F_S`
  blends in (`centroid_shift_blended`) and suppresses the shift (→0 as `g→∞`). At
  large `u` the major-image deflection `≈ θ_E/u` (the McGill+2023 regime).
- **Closest approach.** The lens sky-track = proper motion + annual parallax
  (Earth barycentric ephemeris via astropy, validated to <0.1 mas); a dense-grid
  scan + parabolic refinement finds the time of minimum separation. No closed
  form — the parallactic loop matters for nearby high-π lenses.
- **Inversion.** `mass_from_centroid_shift(δθ, u, π_rel)` turns a *measured* shift
  into a lens mass — the science return.

## Run

```bash
PY=~/claude_projects/ostinato/.venv/bin/python

# validate against the published LAWD 37 event
$PY scripts/microlensing/validate.py

# predict events in a field (CLI; default ~Barnard's-Star field)
$PY scripts/microlensing/predict.py --ra 176.46 --dec -64.84 --radius 1.5 \
    --pm-min 150 --mass 0.5 --prefix my_events    # -> /tmp/my_events.csv

# cross-check the project's candidate list
$PY scripts/microlensing/apply_candidates.py      # -> /tmp/ml_candidate_crosscheck.json

# offline unit tests
$PY -m pytest tests/test_microlensing.py -q
```

### Gaia-TAP gotchas baked into the queries (DR4-evolution server)
- A literal `<` in an async-job query is XML-escaped to `&lt;` and breaks ADQL —
  all comparisons are written with `>` (operands flipped).
- `ORDER BY` on a *computed expression* (e.g. `pmra²+pmdec²`) is rejected — we
  sort client-side instead.
- `SQRT(pmra²+pmdec²)` over a wide cone times out — the PM cut uses
  `(pmra²+pmdec²) > pm_min²`, and a **parallax floor** (default 5 mas) prunes the
  table first (high-μ lenses are nearby anyway, so this loses ~nothing).

## DR4 re-run

When Gaia DR4 lands (2 Dec 2026): set `predict.GAIA_TABLE = "gaiadr4.gaia_source"`
and `predict.GAIA_REF_JYEAR` to the DR4 reference epoch, then re-run. DR4's
overhauled astrometry (10× longer baseline) re-derives every predicted epoch and
impact parameter; the math in `geometry.py` is unchanged. This is the lane's main
standing value.
