# RNAAS submission steps (USER actions — nothing has been submitted)

Draft prepared 2026-07-15. All requirements below were re-verified against
journals.aas.org on 2026-07-15 (they differ from the older "1000 words,
no abstract" rules — see "Current rules" table).

## Current RNAAS rules (verified 2026-07-15)

| Item | Current rule | Source |
|---|---|---|
| Length | **1,500 words or fewer, including title, headers, captions, and references**, with 150 words reserved for the required abstract. Table *contents* don't count; caption text does. | journals.aas.org/research-note-preparation-guidelines/ |
| Abstract | **Required** since 2020-05-01, **max 150 words** | research-notes page + AASTeX v7 guide |
| Figure/table | **One figure OR one table, not both**; figure must fit a single print page | research-notes page |
| Review | Not peer reviewed, not copy-edited; editor moderates for appropriateness/format | research-notes page |
| Turnaround | "Typically published within 72 hours of manuscript receipt" | preparation guidelines |
| Cost | "Free to read and currently carry no author publication charges" — **$0** | preparation guidelines |
| Indexing | DOI issued, indexed in ADS, citable, archived | scope page |
| Who may submit | **No affiliation or AAS-membership requirement appears in any current guideline page**; RNAAS regularly publishes amateur/citizen-scientist notes (e.g., Exoasteroids citizen-science CV discovery). "Independent researcher" as affiliation is fine. | research-notes + scope pages (checked for restrictions: none stated) |
| Template | AASTeX v7 preferred; RNAAS style option: `\documentclass[RNAAS]{aastex701}` (option exists in aastex62→v7 lineage) | AASTeX guide + Overleaf AAS template |
| AI policy | "Authors are expected to acknowledge and cite the use of any LLM used in manuscript preparation." Responsibility stays with the authors. | journals.aas.org/manuscript-preparation/, policy DOI 10.3847/25c2cfeb.c3619710 |
| ORCID | **Could not verify as a hard requirement** on current public pages (the portal "extracts ORCIDs to help identify authors"). Registering one is free, takes ~2 min, and the draft already carries an ORCID slot. | journals.aas.org/manuscript-preparation/ + submission page |

Note: the IOPscience "Scope" page still says "1,000 words" — that page is
stale; the AAS-side pages (1,500 incl. everything) are authoritative.

## Step-by-step

1. **ORCID (~2 min, free):** register at https://orcid.org/register with
   alexander.keur@gmail.com. Then replace the placeholder
   `0000-0000-0000-0000` in `rnaas_note.tex` (line with `\author[...]`).
2. **Re-run the novelty check** if more than a few days have passed
   (queries listed in `NOVELTY_CHECK.md`); also reconfirm the three TNS names
   (SN 2026uid, AT 2026pun, SN 2026pec) still stand.
3. **Decide the affiliation string.** Draft uses "Independent researcher".
   Optionally add a city/country; not required.
4. **Compile check.** No LaTeX on this machine (`pdflatex` not on PATH), so
   easiest is Overleaf: New Project → Templates → "AASTeX Template for
   submissions to AAS Journals (ApJ-AJ-ApJS-ApJL-PSJ-RNAAS)" → replace the
   body with `rnaas_note.tex` contents (keep `\documentclass[RNAAS]{aastex701}`).
   Verify: abstract ≤150 words, table renders on one page, no `??` citations.
5. **Submit.** Two routes:
   - **Portal:** https://journals.aas.org/submission → unified AAS portal at
     **aas.msubmit.net** → create an account (your action; ~5 min) → New
     Submission → journal: *Research Notes of the AAS* → upload the .tex (the
     note has no figure files) → fill title/abstract/author metadata → submit.
   - **Overleaf direct:** the AAS template's "Submit to AAS journals" menu
     item pushes the project straight into the AAS system.
6. **During submission** you will confirm the standard policies (ethics,
   data). The AI acknowledgment is already in the manuscript per policy; no
   separate AI form was found in the public docs.
7. **Expect** an editor moderation pass (appropriateness/format), then
   publication **typically within ~72 h** of receipt. Cost: **$0**.
8. **After publication:** add the DOI to the repo
   (`docs/reports/rubin_pilot_2026_07_14/` + RESEARCH_LOG) and to any TNS/VSX
   filings that cite the vetting protocol.

## What is in this directory

- `rnaas_note.tex` — the draft (957 words total by RNAAS counting rules,
  abstract 129 words; see `rnaas_note_wordcount.txt`)
- `rnaas_note_wordcount.txt` — per-part word count, method stated
- `wilson_check.py` / `wilson_check_output.txt` — all interval arithmetic
- `NOVELTY_CHECK.md` — arXiv/ADS-adjacent search log with identifiers
- `arxiv_q1.xml` — raw first arXiv API response (provenance)

## Known open items / blockers

- ORCID placeholder must be replaced (blocker for submission, not for review).
- ORCID hard-requirement status unverified — resolve at account creation.
- No local compile performed (no TeX install); Overleaf step 4 covers it.
- Author-name check on two arXiv-only references (Pessi2024, Robinson2024)
  used "et al." — Overleaf/ADS will render fine, but you may want full
  author lists if the editor asks.
