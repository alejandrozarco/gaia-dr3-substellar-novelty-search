# Ideation scan v6 (2026-09-20) — two independent reviews, and the one place they collide

Two reviewers gated the same 10 curated lanes independently:
- **Opus gates** — one adversarial agent per lane, each running its own prior-art searches and
  live archive queries. Output: `MENU_opus_gates.md`, `gate_verdicts.json`.
- **Astra** (gpt-6-astra, single call over all 10) — `astra_independent_review.txt`.

## Where they agree

| lane | Opus | Astra |
|---|---|---|
| Gaia DR4 day-1 single-eclipse / single-dip | GO_CANDIDATE | GO_CANDIDATE |
| Reference-poisoned outbursters | GO_CANDIDATE | GO_CANDIDATE |
| Faint southern dwarf-nova census (DES-SN5YR, **Stage 1 only**) | GO_CANDIDATE | GO_CANDIDATE |
| Deep/total eclipsing white-dwarf binaries | **NO_GO** | **NO_GO** |
| Post-Gaia northern microlensing | GO_CANDIDATE (0.88) | MARGINAL |
| Non-thermal Galactic mismatch | NO_GO | MARGINAL |

Three lanes carry a two-reviewer GO_CANDIDATE. Both independently killed the eclipsing-WD lane.

## Where they collide — and the collision is decisive

**Lane 9, "pre-reference frozen-state census"** (Gaia DR3 bright stars absent from, or ≥2.5 mag
fainter than, the ZTF reference):

- **Astra ranked it FIRST and named it the Monday start**, calling it "the most credible
  structural argument here" — a source already faint before the reference is absent from both
  reference-seeded light curves and subsequent difference alerts. Its critique was entirely
  methodological (G ≠ r; propagate positions to every epoch, 300 mas/yr = 2.4″ by 2024; check
  reference END dates not just start; 30 Gaia observations ≠ 30 FoV visits).
- **Opus ranked it MARGINAL and falsified the premise outright**, citing a fact Astra never
  raised: **ASAS-SN Sky Patrol v2.0 (arXiv:2304.03791)** serves light curves for a target list
  that is not built from its own images.

### Independent verification of the contested fact (2026-09-20)

The ASAS-SN service host resolved but would not connect (IRSA returned 200 in the same minute,
so it was not a local network problem), so the proposed empirical test — query 1,000 Gaia stars
at 15 < G < 16.5 and measure what fraction return light curves — **could not be run**. The paper
was checked instead:

| claim | verdict |
|---|---|
| **98,602,587** stellar targets from **ATLAS REFCAT2**, mean **g < 18.5**, r1 > 20″ | **CONFIRMED** |
| queryable by **Gaia DR2** identifier (also TESS, AllWISE, SDSS, REFCAT2, 2MASS) | **CONFIRMED** (DR2; DR3 not stated) |
| limits **V ~ 17.5**, **g ~ 18.5**; saturation ~g 12.5 | **CONFIRMED** |
| nightly all-sky since late 2017, data from late 2011 | **CONFIRMED** |
| "**reference-independent**" photometry | **FALSE** — ASAS-SN *is* image subtraction: frames are subtracted from a reference, then reference-image photometry is added back to the differential curve |

**So Opus's kill stands, but its stated reason is wrong.** ASAS-SN is not reference-independent.
The correct reason is sharper: **ASAS-SN's target list comes from an EXTERNAL catalogue
(REFCAT2, built on Gaia/PS1), not from its own reference image.** It therefore does not inherit
ZTF's reference-seeding blind spot, which is the entire structural escape Lane 9 was built on —
and because reference photometry is added back, its light curves report total flux, so a fade
shows up as a fade. Tier 0 (Gaia G ≤ 16.5) sits comfortably inside g < 18.5, so essentially the
whole parent sample already has open, queryable light curves spanning the claimed fade window.

**Verdict: Lane 9 is NOT the Monday start.** Astra's first choice fails on a fact it did not
check. The remaining cheap test (measure the actual ASAS-SN return fraction for Tier-0 targets)
should still be run when the service is reachable, because it bounds how complete that coverage
really is — but the premise "invisible by construction" is already falsified.

## What this says about using two reviewers

Astra's critique of Lane 9 was *entirely* methodological and every point was fair. It still
reached the wrong verdict, because the lane does not fail on method — it fails on a survey
existing that the lane never mentions. Opus found it by querying archives during the gate rather
than reasoning from the lane's own text. That is the same asymmetry seen on ZTF19abxfaon, where
the reviewer pointed at the repository caught what the reviewer given a summary could not.

**Rule: a reviewer that only reads the proposal can audit its logic; only a reviewer that
queries the archives can audit its premises.** Run both, and when they disagree, check whose
claim is falsifiable and falsify it.

## Traps both reviewers flagged

- **SPHEREx Galactic-plane engine** — Opus MARGINAL, Astra NO_GO: *"the clearest engineering
  trap: a survey-quality crowded-field spectrophotometry project disguised as a catalogue
  search."* Both noted the line physics is attractive and the extraction burden is concealed.
- **Deep/total eclipsing WD binaries** — killed by both; the northern premise is contradicted by
  an explicit published search.
- **Speed of the field:** Opus's gates shot two lanes with papers **less than three weeks old**
  (van Roestel+2026, arXiv:2609.08923, ~2026-09-08). Prior-art screening has a shelf life of
  weeks, not years.

## The July-2026 question, answered

July's scan concluded the remaining solo surface is *"PROPAGATION LABOR — the measured-but-never-
filed gap between professional catalogues and MPC/VSX/TNS registries — not discovery."*

Astra's answer, which is the better-argued of the two and is adopted here:

> "[The July conclusion] conflated **photons already measured**, **phenomena already recognized**,
> and **recognized phenomena not yet registered**. Only the last is necessarily propagation. Your
> EB appears to occupy the second gap: the signal existed, but its meaning had not been extracted.
> However, three selected successes, two still provisional, following many closed lanes do not
> establish a rich remaining discovery surface. They are entirely consistent with **sparse
> discoveries concentrated in specific selection failures, surrounded by many null searches**.
> The corrected conclusion is: **propagation is more predictable; discovery remains possible but
> requires a demonstrated selection gap, enough surviving population, and archive-only evidence
> strong enough to finish the claim.** Your results justify rejecting "discovery is over." They
> do not justify accepting the yield forecasts in these ten proposals."

Opus's framing of the same point, from the menu: nine of the ten surviving lanes are the same
species — **absence as signal**, where a source is selected because an archive that should have
measured it did not. That convergence "is what is left after the detection-based surface was
cleared," and it carries a structural tax: an absence is also produced by every pipeline
pathology, so five of ten lanes were downgraded on an **unmeasured false-positive floor** rather
than on prior art.

**Both reviewers independently landed on the same operational requirement**: no absence-based
lane may be believed until it has measured its own false-positive rate against injected
recoveries on its own configuration. That is the rule this session learned five times over.
