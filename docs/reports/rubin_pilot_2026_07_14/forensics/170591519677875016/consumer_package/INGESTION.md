# Concrete ingestion paths (user files; nothing submitted by the agent)

CONSUMERS, in order of directness:

1. Fink ELEPHANT (hostless-candidates) team — the flag under test is theirs.
   Path: e-mail contact@fink-broker.org (or Fink Slack #elephant) citing diaObject
   170591519677875016; attach annotation.txt. Our template-flux measurement (r=23.96,
   i~23.9 underlying source) is direct feedback on their hostless label, and the ATLAS
   pre-discovery onset extends the light curve baseline they publish.

2. TNS AstroNote (tns_astronote_draft.md) — needs the user's TNS account. AstroNotes
   accept archival/photometric follow-up notes on unreported objects; alternatively a
   full AT (discovery) report crediting the Rubin/LSST public alert stream as data
   source with ATLAS FP as pre-discovery — gives the object a citable AT designation
   and named reporter credit (codified channel, matches campaign guardrails).

3. Lasair-LSST annotation (lasair_annotation.json) — GATE RESULT 2026-07-14: the
   LSST instance is lasair.lsst.ac.uk and the old lasair-ztf token does NOT
   authenticate ("Invalid token"). USER ACTION: log in at lasair.lsst.ac.uk with
   institutional/GitHub SSO, copy the new API token to ~/.config/lasair/token_lsst,
   request an annotator topic, then POST the JSON to /api/annotate/.

RESOLVED HOOK (2026-07-14, this session): ZFPS req 479160 completed and downloaded
(zfps_fp_raw.txt) -- 22 usable g+r diff-image epochs MJD 60515-61148, all null (SNR<3,
median depth ~19.5-19.7), no coverage during the event. The no-precursor claim now rests on
ATLAS 11-yr FP + ZTF alerts/DR/ZFPS + PS1 DR2 (2011 y-band 'precursor' at 0.84as adjudicated
as a warp artifact: single-exposure, absent in same-night partner frame, psfQfPerfect=0.54,
SkyBoT-negative). Package is complete; USER files.
