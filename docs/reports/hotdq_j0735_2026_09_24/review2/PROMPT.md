You are a hostile, expert referee (white-dwarf spectroscopy, UV spectroscopy, merger remnants). A team is about to email the PI of
HST SNAP program 17420 (Gaensicke; cc Sahu, Bedard) claiming that Gaia DR3 5208047381438507520 (GALEX J073504.2-794409,
WDJ073504.07-794410.69, TIC 764468822; 96 pc, G 16.56) - catalogued everywhere as a DA - shows photospheric carbon (optical C II in
SDSS-V DR20; C II/C III in their public COS G130M spectrum lfac0z010) and is provisionally a hot DQ with probable hydrogen (DQA).

Read DOSSIER.md, previous_review.md (an earlier independent review whose seven corrections were adopted) and email_draft.md. Raw data
are in raw/ (mwmVisit-0.8.1-95077848.fits: SDSS-V BOSS visit spectra, Astra 0.8.1, rest-framed by the XCSAO velocity for in_stack
visits - undo with lambda = grid*(1+v/c); lfac0z010_x1dsum.fits and per-exposure x1d files: HST/COS). Scripts in scripts/, data in data/.

The earlier review already covered the basics. Go BEYOND it. Your job is to find anything that would embarrass the team or change
the message. Specifically:
1. ALTERNATIVE: at the DA-model temperatures quoted (28-35 kK), hot DA white dwarfs routinely show far-UV C III/C IV, Si III/IV, N V
   from radiative levitation or accretion (e.g. Barstow et al., Koester et al. 2014 COS surveys). Could this star be a hydrogen-
   dominated DA with levitated/accreted carbon (DAZ-like, or a "hot DAQ") rather than a DQ? Test it: do the Balmer lines H-beta to
   H-epsilon have the strength and width expected for a 28-35 kK, log g ~9 DA? Is optical C II 4267/6580 of the observed strength
   possible with trace carbon in a hydrogen atmosphere? Which classification do the data actually support, and how should the email
   phrase it?
2. Consistency of temperature: hot DQs are typically 18-24 kK; the only temperatures quoted are from DA/He fits to photometry
   (28.6 kK GF21; 35 kK XP). What do the COS continuum slope and the C II/C III ionisation balance suggest? Is "hot DQ" even
   consistent with the ions seen (C II strong, C III present, Si II present)?
3. Data quality: single SDSS-V visit - check masks, sky residuals, flux calibration, the XCSAO shift handling (sign and which frame),
   whether any "C II line" coincides with a sky line or instrumental feature; for COS check each exposure separately (do the lines
   appear in every exposure / FP-POS?), geocoronal contamination, the line-spread function, and the interstellar components.
4. Scoop and courtesy: search the web now (ADS, arXiv including 2026 postings, AAS/EuroWD/conference abstracts, HST program 17420
   abstract and any papers from it, Warwick group papers on carbon in massive/merger-remnant white dwarfs, Sahu 2025 follow-ups).
   What is program 17420 actually about? If its science goal is to find carbon in massive white dwarfs, the team has almost certainly
   already seen this - say so and rewrite the email accordingly.
5. Audit the email draft sentence by sentence against the data: every number, every claim ("redder than every spectroscopic DA",
   "listed as DA", velocities, lines, "no published classification"). Flag anything wrong, overstated, or missing that the recipients
   will immediately ask about. Propose a corrected email.
Output a concise report with sections: Verdict; Blocking issues (must fix before sending); Alternative interpretations tested (with
numbers); Data-quality findings; Scoop/prior-work search log (with links); Email audit (claim by claim) and a corrected draft;
Remaining risks. Do not modify files; you may write scratch files under /tmp/hotdq/review2/scratch/.
