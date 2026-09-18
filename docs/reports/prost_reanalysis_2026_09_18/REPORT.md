# Prost (probabilistic host association) re-analysis of the 5 Rubin dossiers — 2026-09-18

**Verdict: RAN, but the output is NOT USABLE as science, and Prost's default catalogue
stack is SHALLOWER than what our pilot already used in these fields. My 2026-09-18 claim
that Prost "is exactly the rigorous form" of our depth-limited-hostless argument is
CORRECTED below — in this configuration it cannot answer that question at all.**

astro-prost (Gagliano; PATH successor, arXiv:2102.10627 lineage) installed in a fresh
/tmp venv; demo-default SN priors: offset ~ U(0,10) (fractional), absmag ~ U(-30,+20),
z ~ halfnorm(1e-4, 0.5); likelihoods offset ~ gamma(0.75), absmag ~ SnRateAbsmag(-30,-10);
n_samples=1000; catalogs glade + decals + panstarrs. Raw outputs: prost_results.csv
(3-catalogue run), prost_decals.csv (DECaLS-only control), scripts alongside.

## What came back (3-catalogue run)

| dossier | best cat | P(host) | offset ″ | P(none) | our pilot's host |
|---|---|---|---|---|---|
| R950 unreported SN (=AT 2026uxw) | panstarrs | 0.78 | **18.1** | 1.3e-12 | LS DR10 REX at **1.01″** |
| R637 SN II cand | panstarrs | 0.92 | **10.5** | 1.6e-12 | PS1 stack source at **0.71″** |
| R016 hostless blue | panstarrs | 0.46 | **10.5** | 1.7e-12 | none in LS DR10; Rubin template r=23.96 |
| R512 mundane SN | panstarrs | 0.57 | **11.0** | 3.9e-13 | LS DR10 PSF at **0.48″** |
| R822 ZTF19abxfaon (Galactic CV) | decals | **1.00** | 0.14 | 1.1e-09 | n/a — Galactic |

## Four diagnosed failure modes

1. **COVERAGE — the decisive one.** A DECaLS-only control returns `best_cat = NaN` for all
   four transients: Prost queries **DECaLS DR9**, which has no coverage at these positions.
   These are DES-footprint fields that only entered the Legacy Survey at **DR10** — the
   release our own pipeline queried via NOIRLab Data Lab TAP. So in these fields
   *our ad-hoc association used a deeper catalogue than Prost's default stack.*
2. **SILENT DEGRADATION.** With DECaLS empty it falls through to Pan-STARRS, logging
   "panstarrs does not support conditioning on absmag; falling back to 'offset' only" —
   association collapses to pure geometry/size. That is how an 18.1″ PS1 source beats the
   1.01″ REX galaxy we found for R950. Redshift and absmag columns come back 0.0/NaN.
3. **SELF-ASSOCIATION.** At the CV's position DECaLS DR9 catalogues *the CV itself* as an
   extragalactic source with z_phot = 0.93 ± 0.05, M_r = -21.0; Prost duly returns
   P(host) = 1.000 at 0.14″ — the object associated with itself. A Galactic point source
   must never be fed to a host-association code without a star/galaxy gate.
4. **P(no host) IS NOT WHAT I CLAIMED.** `none_posterior` came back ~1e-12 for every
   object, including the one we argued is hostless at archival depth. With these priors
   the "no host" hypothesis is never competitive, so Prost-as-configured does **not**
   deliver a P(unseen host) number. PATH's explicit P(U) with a depth-tied unseen-host
   prior is the thing that would — that remains unbuilt, by us or here.

## What would actually be needed

Feed it LS DR10 (or Rubin's own deep coadds) instead of DR9; a class-appropriate redshift
prior; a star/galaxy gate before association; and an explicit unseen-host prior tied to
the per-field 5σ depth. Until then our LS DR10 + Rubin-template treatment is the better
measurement in these fields, and Prost's value would be standardisation/quotable
posteriors, **not** better host finding. Net: a real method gap identified, and a real
limit on the off-the-shelf fix.
