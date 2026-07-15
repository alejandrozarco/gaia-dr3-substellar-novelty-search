# Concrete ingestion paths (user files; nothing submitted by this run)

RANKED:
1. **TNS AstroNote** (primary): the object is transient-stream-relevant, currently
   active, TNS-negative, and misclassified by two broker classifiers. AstroNotes are
   the standard channel for "alert X = archival object Y, likely class Z" reports and
   are read by follow-up spectroscopy programs (SGLF, ePESSTO+ scan AstroNotes daily).
   Path: user's existing TNS account -> AstroNotes -> new note (astronote_draft.md).
   No spectrum required. Named credit codified.
2. **VSX submission** (parallel/alternative): uncatalogued variable with 13-yr archival
   light curve -> vsx_draft.md. Requires the user's AAVSO account (community scan
   2026-07-14: policy verified, named credit; account opening = USER action, task
   already on the community-scan list).
3. **Lasair-LSST annotation** (blocked on auth): lasair.lsst.ac.uk is live but the
   lasair-ztf token returns 401 on it (verified in-session 2026-07-14). Once the user
   re-registers on the LSST instance, an annotator ("archival-forensics" topic) can
   attach this classification directly to diaObject 170587115976392822 so downstream
   Lasair filter users see it. This is the only path that reaches Rubin-broker
   consumers directly.
4. NOT recommended: direct Fink/ALeRCE team e-mail (no codified credit channel);
   TNS transient report (object is 7 years old and non-SN; AstroNote is the honest
   vehicle).

Consumer test (per campaign rule "every lane needs a CONSUMER"):
- AstroNote -> spectroscopic classifiers hunting bright (<19 mag) unclassified
  transients; CV researchers (e.g. VY Scl/Z Cam monitoring programs) get a new
  bright halo CV candidate.
- VSX -> AAVSO observers; the object is at times r~18, reachable by large-amateur
  scopes for state monitoring.
