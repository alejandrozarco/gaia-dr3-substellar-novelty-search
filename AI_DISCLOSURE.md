# AI disclosure

AI models produced the content of this repository: the pipeline and scripts, the cross-matches, the candidate lists
and dossiers, the figures and the text. The repository owner chose the project, directed the work and decided on scope
and publication. The owner did not check the code, the measurements or the classifications line by line, and no
professional astronomer has reviewed them.

**Models.** Claude models (Anthropic, via Claude Code): Claude Opus 4.7, Opus 4.8, Opus 5 and Opus 5.5 did the work,
and Claude Fable 5 and Fable 5.1 contributed. The commits carry `Co-Authored-By` trailers naming the model used.

**Corrections.** A later re-verification found that earlier headline claims did not hold. A reported CV period and
eclipse were artefacts, and a "confirmed" neutron-star companion was downgraded to a candidate. These were retracted in
release v2.1.0 (see `README.md`, "Confirmed candidates"). Reviews by AI models are not peer review.

**What this means for use.**
- The catalogues are derived from public data (Gaia DR3 and the catalogues in `CATALOG_DEPENDENCIES.md`) by the
  scripts in this repository and can be regenerated from them.
- Candidate classifications, mass estimates and "novel" labels are the output of an AI-run analysis. Treat them as
  leads for independent follow-up, not as discoveries.
- Credit for confirming or refuting any candidate belongs to whoever does that work.
- Questions, checks and corrections: [GitHub issues](https://github.com/alejandrozarco/gaia-dr3-substellar-novelty-search/issues).
