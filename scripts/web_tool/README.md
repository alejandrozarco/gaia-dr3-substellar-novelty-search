# Gaia DR3 Dormant Compact-Object Cascade — Web Tool Prototype

A single-page Streamlit front-end onto the same dormant black-hole / neutron-star
cascade that `scripts/streaming/consumer.py` runs in bulk over the Gaia DR3
non-single-star (NSS) catalog. Drop in any Gaia DR3 `source_id`; the tool pulls
the row + its NSS solution + astrophysical parameters, derives the photocentric
semi-major axis, mass function f(M), and companion mass M_2, then runs the
verdict-ladder Filters #29–#32 to classify the source.

## What the tool does

1. **Input** — one Gaia DR3 `source_id` (sidebar). M_1 prior is set with a slider.
2. **Data pull** — `gaia_source` + `nss_two_body_orbit` + `astrophysical_parameters` +
   `astrophysical_parameters_supp` via `astroquery.gaia`. Falls back to the bundled
   `sample_data/hd1957_demo.parquet` if the ADQL service is slow or unavailable.
3. **Derivation** — photocentric semi-major axis from Thiele-Innes (A, B, F, G),
   mass function f(M), and M_2 via 80-iteration bisection. Math is **identical** to
   `scripts/streaming/consumer.py::derive_chunk` and `apply_filter32.py`.
4. **Filters**
   - **#29 SB2 check** — fails when `nss_solution_type` contains "SB2" or the
     pre-computed `in_sb2` flag is set.
   - **#30 K-giant / chromatic-bias** — fails if BP-RP > 1.2, log g < 2.7, or the
     Teff/logg combination matches a K-giant atmosphere.
   - **#31 RV reality** — `rv_amplitude_robust` vs `rv_chisq_pvalue`
     (PASS at K > 5 km/s with p < 0.05; FAIL at p > 0.5).
   - **#32 Joint astrom + RV** — compares observed K to K_pred(i = 90°);
     ratio above 1.05 implies non-orbital noise and rejects the candidate.
5. **Verdict** — Tier-1 BH / Tier-1 NS / Tier-2 (RV inconclusive) / Demoted / Rejected.
6. **Hipparcos-Gaia Catalog cross-match** — if the source has a HIP entry,
   queries Vizier `J/ApJS/254/42/catalog` (Brandt 2021) with a 20 s timeout;
   on timeout the page just shows "HGCA: skipped" and continues.

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the URL Streamlit prints (default `http://localhost:8501`). In the sidebar:

- The default `source_id` placeholder (`2543788153077017344`) is **HD 1957**,
  which works fully offline using the bundled sample parquet.
- Uncheck "Try live Gaia ADQL" for the fastest, fully-offline demo path.

To refresh the offline sample (e.g. after a new Gaia release), run:

```bash
python build_sample_parquet.py
```

## Input format

| Field | Required | Notes |
|-------|----------|-------|
| `source_id` | yes | Gaia DR3 integer source ID |
| `M_1 prior` | slider | 0.5–3.0 M_⊙, default 1.5; inverts the mass function |
| Live ADQL toggle | optional | When off the app uses `sample_data/hd1957_demo.parquet` |

## Output sections

- **Header KPIs** — M_2, f(M), photocentric a, implied sin i, mass class.
- **Verdict banner** — colour-coded final tier.
- **Panel 1** — orbital phase curve (model K_1 cos f sketch with current K_obs, e).
- **Panel 2** — M_2 vs sin i for the chosen M_1, with BH / NS thresholds annotated.
- **Panel 3** — HR diagram with the candidate on a sketched MS / giant track.
- **Panel 4** — cascade verdict ladder, colour-coded PASS / FAIL / AMBIGUOUS / NO_DATA.
- **HGCA panel** — Hipparcos-Gaia acceleration row when available.
- **Collapsible tables** — full derived parameters, per-filter reasons,
  `gaia_source`, `nss_two_body_orbit`, and the verbatim input row.

## Screenshot description

After running the demo (`source_id = 2543788153077017344`, M_1 = 1.5 M_⊙) the page
shows: top KPI strip listing M_2 ~ 2.2 M_⊙ and `class = dormant_NS_candidate`, an
amber/red verdict banner (HD 1957 fails Filter #30 K-giant and Filter #32 because
K_obs is dominated by chromospheric jitter in a Gaia evolved star), two-by-two
plot grid (phase curve, mass-function ladder, HR diagram with the giant in the
upper-right, and a horizontal bar chart of the four filter verdicts), then the
HGCA row (skipped — no HIP), and four collapsible tables underneath.

## Files

| File | Purpose |
|------|---------|
| `app.py` | The Streamlit page |
| `requirements.txt` | Runtime dependencies |
| `build_sample_parquet.py` | One-off generator for the offline demo row |
| `sample_data/hd1957_demo.parquet` | Pinned Gaia DR3 snapshot for HD 1957 |
| `README.md` | This file |

## Reference

Filter math is reproduced verbatim from
`scripts/streaming/consumer.py` and `scripts/streaming/apply_filter32.py`.
HGCA cross-matches use Brandt T.D. 2021, ApJS 254, 42
(Vizier catalog `J/ApJS/254/42/catalog`).
