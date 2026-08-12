# Novelty check — channel-resolved artifact rate for Rubin/LSST year-1 public broker channels

Date of check: 2026-07-15 (draft prep; measurement dated 2026-07-14/15).
Claim under test: *no published measurement of channel-resolved artifact rates
for the live Rubin/LSST year-1 public alert-broker channels exists.*

**VERDICT: claim stands — PROCEED.** Nothing found (arXiv API + web search,
searched through 2026-07-15) that measures artifact/bogus rates per public
broker channel on the live Rubin year-1 stream. Closest works are ZTF-era
purity studies, DP1 (commissioning, static) analyses, and system papers with
no alert-quality numbers. The note's wording is calibrated accordingly ("We
are not aware of a published, channel-resolved artifact-rate measurement for
the live year-1 stream") — an ADS full-text sweep behind a login was NOT run,
so the claim is phrased as awareness, not exhaustive proof.

## Method

1. arXiv API (`export.arxiv.org/api/query`), 11 queries, sorted by
   submittedDate descending, run 2026-07-15 (raw first response saved as
   `arxiv_q1.xml`):
   - Q1 `"Rubin" AND "alert stream"`
   - Q2 `("LSST" OR "Rubin") AND "broker" AND ("purity" OR "artifact" OR "bogus")`
   - Q3 `"incremental template" AND ("LSST" OR "Rubin")`
   - Q4 `"hostless" AND ("LSST" OR "Rubin")`
   - Q5 `("real-bogus" OR "real/bogus") AND ("Rubin" OR "LSST")`
   - Q6 `"Fink" AND "LSST"`
   - Q7 `"alert production" AND ("Rubin" OR "LSST")` (0 hits)
   - Q8 `("Rubin" OR "LSST") AND "commissioning" AND ("alerts" OR "difference imaging")`
   - Q9 `"Data Preview 1" AND ("Rubin" OR "LSST")`
   - Q10 `("Rubin" OR "LSST") AND "vetting" AND "transient"`
   - Q11 `"stamp classifier" AND ("Rubin" OR "LSST")`
2. Web searches (3) for year-1 artifact/bogus/purity measurements of Rubin
   broker channels.
3. Abstract-level scope checks (WebFetch) on every near-miss candidate below.

## Near-miss candidates examined and why they do NOT scoop

| Identifier | Title / scope | Why not a scoop |
|---|---|---|
| arXiv:2605.22407 (Durgesh, Pessi, Ishida, Peloton; 2026-05-21) | Hostless extragalactic transients in Fink: ELEPHANT results | **ZTF** data (2023-09 → 2025-12); pipeline accuracy 0.84 on ZTF; notes ELEPHANT processes Rubin alerts since 2026-02 but reports **no Rubin channel artifact rates** (abstract checked 2026-07-15) |
| arXiv:2507.22864 (v2) | Extragalactic transients in Rubin **Data Preview 1** | DP1 = LSSTComCam commissioning (2024-11/12), static release, not the live alert stream; reports detection counts, **no formal artifact rates** (abstract checked) |
| arXiv:2603.19541 (2026-03-20) | Rubin Prompt Processing System | Architecture/throughput/latency paper; **no alert-quality numbers** (abstract checked) |
| arXiv:2603.23786 (2026-03-24) | The Vera C. Rubin Observatory Data Preview 1 | DP1 release paper (commissioning, static) |
| arXiv:2602.12955 (2026-02-13) | AHA: anomaly detection in the **ZTF** alert stream | ZTF, not Rubin |
| arXiv:2601.10454 (2026-01-15) | Alertissimo: orchestration of LSST broker streams | Tooling paper, no purity measurement |
| arXiv:2606.28645 (2026-06-26) | GOATS (Gemini/NOIRLab follow-up infrastructure for Rubin alerts) | Infrastructure, no purity measurement |
| arXiv:2607.28510 (2026-07-30*) | Uncertainty-aware TDE classification | Classifier paper. *Listed date from arXiv API result; postdates check window edge — title/scope clearly not a channel artifact-rate measurement |
| arXiv:2411.19796 (Robinson et al.) | Incremental templates in Year 1 (solar-system focus) | Predicts template-coverage effects; **no measured alert artifact rates**; cited as context in the note |
| arXiv:2404.18165 (Pessi et al. 2024) | ELEPHANT pipeline paper | Method paper (ZTF); cited in the note |
| arXiv:2008.03309 (Carrasco-Davis et al.) | ALeRCE real-time stamp classifier | ZTF-era; its Rubin beta successor is what we document miscalling; cited |
| arXiv:2507.22156 (v4) | Early transient discovery for LSST via **DECam** difference imaging | DECam, not Rubin channels |

## Residual risk

- arXiv is near-complete for astro-ph but not total; a pure-ADS or
  broker-internal technical note (e.g., a Fink/ALeRCE blog or LSE document)
  could exist without arXiv posting. Web searches surfaced none.
- The RNAAS moderation window (~72 h) is short; re-run Q1/Q2/Q4 immediately
  before actual submission if more days elapse (one command:
  `python3 wilson_check.py` is not it — rerun the arXiv queries in this file).
