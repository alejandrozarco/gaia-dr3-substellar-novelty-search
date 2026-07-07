export const meta = {
  name: 'kk76-hst-refit',
  description: 'Complete the KK76/(88268) HST deliverable: joint find_orb refit of the 4 obscode-250 points with the MPC arc, with/without ephemeris-uncertainty impact, and an ADES draft for user review — refereed. No submission.',
  phases: [
    { title: 'Refit', detail: 'joint OD + uncertainty propagation + ADES draft' },
    { title: 'Referee', detail: 'adversarial reproduction' },
  ],
}

const ENV = [
  'ENVIRONMENT / RULES (binding):',
  '- Network available. Use the EXISTING find_orb console build at',
  '  /tmp/precovery_verify/2001_KN76/build/find_orb/fo (the Orius deep-dive reused it successfully;',
  '  it reads OBS80/ADES obs files; sky-plane ephemeris-uncertainty output via its ephemeris options).',
  '- Fresh /tmp venv for any pip installs; ostinato python usable, never pip-install into it.',
  '- Work dir: /tmp/kk76_refit/. Do NOT edit repo docs/ (read-only context: docs/reports/',
  '  precovery_campaign_2026_07_07/wave3/hst_kk76/candidate_astrometry.csv = the 4 refereed HST',
  '  positions; the Orius ADES draft at verify/2009_HW77/ades_draft_330836_orius.psv = format model).',
  '- Do NOT submit anything anywhere. Designations are strings.',
  '- OBJECT: (88268) = 2001 KK76, TNO, MPC ground arc 2001 -> 2004-05-28 (last obs). The 4 new points:',
  '  HST ACS/HRC 2006-05-02, obscode 250, per-axis sigmas 0.16"/0.10" (USE THESE, not the internal',
  '  tens-of-mas — referee-mandated). Mags are non-standard CLEAR-band lower bounds: do NOT put them',
  '  in the ADES draft as calibrated photometry (omit mag or handle per ADES unfiltered rules).',
  '- KNOWN DATA FIX (referee-flagged): the CSV column jd_tdb_mid actually holds UTC JD — treat',
  '  obsTime_UTC as truth and handle time scales explicitly (TT-UTC ~65 s in 2006 ~ 0.05" along-track).',
].join('\n')

const REFIT_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    fit_without: { type: 'string', description: 'ground-arc-only (2001-2004) fit: elements + key sigmas + n_obs used' },
    fit_with: { type: 'string', description: 'joint fit incl. the 4 HST points: elements + sigmas; points retained? residuals per point?' },
    ephemeris_impact: { type: 'string', description: 'sky-plane 1-sigma uncertainty at 2026-07, 2030-01, 2040-01: without vs with (arcsec) + prediction offset in sigma' },
    consistency: { type: 'string', description: 'do the HST points co-fit the ground arc cleanly (sub-arcsec, no rejections)? any tension?' },
    ades_draft_path: { type: 'string', description: 'drafted ADES PSV for the 4 points (obscode 250, measurer A. Keur, astCat Gaia via HSC30 anchor) — DRAFT ONLY' },
    report_path: { type: 'string' },
    caveats: { type: 'string' },
  },
  required: ['fit_without', 'fit_with', 'ephemeris_impact', 'consistency', 'ades_draft_path', 'report_path'],
}

const REF_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    verdict_stands: { type: 'boolean' },
    headline_numbers_confirmed: { type: 'string' },
    ades_check: { type: 'string', description: 'field-by-field review of the ADES draft (times/scales, positions, sigmas, obscode, astCat, band handling)' },
    issues: { type: 'string' },
  },
  required: ['verdict_stands', 'headline_numbers_confirmed', 'ades_check'],
}

phase('Refit')
const refit = await agent(
  ENV + '\n\n'
  + 'JOB: complete the (88268)/2001 KK76 HST measurement into a fit-validated, ADES-drafted deliverable.\n'
  + 'Steps:\n'
  + '1. Pull the full MPC observation record (get-obs API; verify the arc really ends 2004-05-28 and\n'
  + '   count obs). Save raw.\n'
  + '2. Convert the 4 HST positions from candidate_astrometry.csv into find_orb-ingestible form (ADES\n'
  + '   PSV or OBS80) with obscode 250, correct UTC times, and the 0.16"/0.10" per-axis sigmas.\n'
  + '3. Fit (a) ground-arc-only and (b) joint with the 4 HST points using the existing fo build\n'
  + '   (N-body, same settings both runs). Verify all 4 points are retained with sub-arcsec residuals;\n'
  + '   report per-point residuals and the mean pull.\n'
  + '4. Propagate BOTH covariances to 2026-07-01, 2030-01-01, 2040-01-01 (geocentric 500): sky-plane\n'
  + '   1-sigma uncertainty without vs with, plus the offset between the two predicted positions in\n'
  + '   units of the without-sigma (the bias-detection metric from the Orius analysis).\n'
  + '5. Draft the ADES PSV for USER review, modeled on the Orius draft: header comment block (archival\n'
  + '   HST ACS/HRC frames, program 10514, measurer named, SARC-first instruction, HST obscode 250,\n'
  + '   Gaia-DR3-tied HSC30 astrometric reference), 4 data rows, NO calibrated photometry claims.\n'
  + '   Save to /tmp/kk76_refit/ades_draft_88268_2001kk76.psv.\n'
  + '6. Write REPORT.md + an ephemeris_uncertainty.csv table.\n'
  + 'Honesty rules: if the joint fit rejects any HST point or shows >2-sigma tension, say so plainly —\n'
  + 'that outcome would demote the chain, not be hidden.',
  { label: 'refit:kk76-hst', phase: 'Refit', schema: REFIT_SCHEMA, model: 'opus', effort: 'high' }
)

phase('Referee')
const referee = await agent(
  ENV + '\n\nYou are the ADVERSARIAL REFEREE of the KK76 refit + ADES draft (result below; outputs in\n'
  + '/tmp/kk76_refit/). Checks: (1) independently re-run the with/without fits from the saved obs files\n'
  + 'and reproduce the headline uncertainty numbers at 2030; (2) verify the 4 HST points were weighted\n'
  + 'at 0.16"/0.10" (not tens-of-mas) and all retained; (3) field-by-field ADES draft review — obsTime\n'
  + 'really UTC ISO, positions match candidate_astrometry.csv, obscode 250, no bogus photometry, astCat\n'
  + 'sensible, measurer block present, SARC-first note present; (4) sanity: the joint fit\'s 2006 O-C\n'
  + 'pull should match the wave-3 measurement (~0.29" mean). Correct, do not merely bless.\n\n'
  + '===== CLAIMED =====\n' + JSON.stringify(refit, null, 1),
  { label: 'referee:kk76-refit', phase: 'Referee', schema: REF_SCHEMA, model: 'opus', effort: 'high' }
)

return { refit, referee }
