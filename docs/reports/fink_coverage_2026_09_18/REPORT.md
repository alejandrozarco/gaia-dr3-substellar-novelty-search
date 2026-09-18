# Fink science-module coverage map — what the competitor already runs (2026-09-18)

Motivation: three encounters in a row (ELEPHANT scoop of AT 2026uxw; the ELEPHANT results
paper; the TDE "Lost and Found" paper) show Fink systematically working the archival tail
of its own streams with purpose-built classifiers. This is their coverage, so we can see
what is left.

## A. Running on the RUBIN/LSST stream — MEASURED from a live alert record (not docs)

Source: api.lsst.fink-portal.org `/api/v1/tags` + a full alert packet (fink_science 8.52.0,
fink_broker 5.0rc0, lsst.v11_1). Four classifiers:

| field | module | target |
|---|---|---|
| `f:clf_cats_class` / `_score` | CATS | broad multiclass (class 11 = SN-like) |
| `f:clf_snnSnVsOthers_score` | SuperNNova | SN vs. others |
| `f:clf_earlySNIa_score` | Early SN Ia | young Ia for spectroscopic triggering |
| `f:clf_elephant_kstest_science` / `_template` | **ELEPHANT** | hostless extragalactic transients |

Ten per-alert crossmatches: SIMBAD (otype), TNS (fullname/type/redshift), Gaia DR3
(name/Plx/VarFlag), **VSX (Type)**, **GCVS (Type)**, Legacy DR8 (zphot/pstar/fqual),
Mangrove (HyperLEDA+2MASS host, ang_dist, lum_dist), SPICY (YSO class), 3HSP (blazars),
4LAC (Fermi AGN).

Filters/tags exposed: hostless_candidate, extragalactic_new_candidate,
extragalactic_lt20mag_candidate, extragalactic_svom, most_likely_sn,
sn_near_galaxy_candidate, in_tns, faint_trails, fast_transient_gvom,
remove_unlikely_transients, uniform_sample. **There is still NO anomaly-detection tag on
the LSST instance** (re-confirmed today; it exists on ZTF).

## B. Running on ZTF (~200k alerts/night; the larger, older set)

Early SN Ia · kilonova / fast transients · AGN · **Solar System objects** · **anomaly
detection** · hostless (ELEPHANT) · superluminous SNe · **TDE** (new, A&A 2026,
arXiv:2511.19016 + arXiv:2507.17499) · orphan GRB afterglows · **microlensing** ·
multiclass classifiers. Release 2.9 (2026) adds: a new anomaly-detection module, a
**time-series transformer** for transient classification, and further catalogue
associations. ZTF Fink API hosts (api.fink-portal.org, fink-portal.org) were TCP-dead
from here today — use the LSST instance or the docs.

## C. Gap analysis — where this leaves us

1. **Detection of uncatalogued variables is ALREADY automated.** VSX *and* GCVS are
   crossmatched on every single alert, so "this variable is in no catalogue" is a field
   they compute, not a discovery we alone can make. Our ZTF19abxfaon find was never
   hidden — it was simply **not pursued**.
2. **Therefore the gap is FOLLOW-THROUGH, not identification.** Every Fink module targets
   transients (SN/Ia/SLSN/TDE/KN/GRB-afterglow/microlensing) or labels contaminants
   (AGN/blazar/YSO). None of them ends in a VSX submission for a persistent Galactic
   variable. That remains our space — and it is defensible precisely because it is
   unglamorous.
3. **Anomaly detection is the live competitive front on ZTF** (and being upgraded in 2.9),
   so "weird object on ZTF" is contested. **On Rubin it is absent** — the one genuine
   structural opening on that stream, for as long as it lasts.
4. **General classification is getting stronger** (time-series transformer, 2.9). Lanes
   whose edge is "a classifier mislabelled it" have a shrinking half-life — our four
   pilot INTERESTING objects all rested on year-1 stamp-classifier misses.
