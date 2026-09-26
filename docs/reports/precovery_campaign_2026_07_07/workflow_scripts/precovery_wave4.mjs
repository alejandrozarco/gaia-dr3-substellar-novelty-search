export const meta = {
  name: 'precovery-wave4',
  description: 'Wave 4: execute the referee-salvaged trio (2007 HV90, 2002 KW14, 2010 JK124) through the hardened recover->referee->pixel pipeline with the mandatory bycatch net and the two wave-3 tooling repairs (get-obs arc-ends; self-arc test). Measurement only, no submission.',
  phases: [
    { title: 'Recover', detail: 'gated-window archival search per target' },
    { title: 'Referee', detail: 'adversarial check per target' },
    { title: 'Pixel', detail: 'cutout verification for surviving chains' },
    { title: 'Synthesize', detail: 'wave state + user handoff' },
  ],
}

const ENV = [
  'ENVIRONMENT / RULES (binding):',
  '- Network available; REAL archival work. Fresh /tmp venv for pip installs; NEVER pip-install into',
  '  the ostinato venv (~/claude_projects/ostinato/.venv — its python may be used).',
  '- Work dirs: /tmp/precovery_wave4/<designation>/. Do NOT edit the gaia repo docs/ (read-only',
  '  context: docs/reports/precovery_campaign_2026_07_07/ — wave3/recut/ holds the gate rows +',
  '  wave3_targets.csv; verify/2009_HW77/ is the worked confirmed-chain example; gate_r1_REPORT.md',
  '  documents the tooling stack).',
  '- Do NOT register accounts. Do NOT submit anything anywhere. Designations are strings.',
  '',
  'STANDING RULES (all hardened from campaign failures; violations void the result):',
  '1. datetime_jd-keyed ephemerides, asserted per epoch (or one epoch per Horizons call). Time-axis',
  '   alignment must be asserted in EVERY comparison (photometry included).',
  '2. NOIRLab cutouts use the _ooi_ science product.',
  '3. Catalog PSF positions + honest per-axis sigmas.',
  '4. Per-epoch imaging existence via SSOIS AT the search epoch (never whole-arc footprint counts).',
  '5. BYCATCH pass mandatory after each primary field search: PYTHONPATH=<repo>/scripts/precovery,',
  '   bycatch.run_bycatch(detections, static_sources=<survey mean-object catalog — MANDATORY>,',
  '   identify=True); log n_unknown_candidate; unknowns = referee-review leads, never claims.',
  '6. Chain discipline: motion-consistent multi-detection chains; stationary-source rejection (deep-',
  '   coadd blank-test where possible); mag sanity ~1.5 mag; +1 deg offset negative control; honest',
  '   per-epoch search_log.csv.',
  '7. NEW (wave-3 repair): arc-end comes from a fresh MPC get-obs parse at run time — never from a',
  '   cached campaign CSV column. Report the parsed arc-end in your output.',
  '8. NEW (wave-3 repair): SELF-ARC TEST before searching any window — if the object\'s own MPC record',
  '   contains observations INSIDE the intended search window (or the frames you would search were',
  '   taken by a station already contributing those epochs), the window adds nothing: mark',
  '   SELF_ARC_SKIP for that window and say so. Only genuinely post-arc / gap windows count.',
].join('\n')

const TARGETS = [
  { desig: '2007 HV90', note: 'referee-verified: 28 DECam frames within +/-45 d of 2017-07-01; gate SMIA 0.30" / SMAA 0.58", V~22.9, gal b=+15.7. Referee says arc-end ~2016 — re-verify via get-obs and confirm the 2017 window is genuinely post-arc.' },
  { desig: '2002 KW14', note: 'referee-verified: 16 DECam frames within +/-45 d of 2017-07-01; gate SMIA 0.21" / SMAA 0.54", V~21.8, gal b=+12.8. Referee CORRECTED the arc-end to ~2015 (not 2009) — real leverage is ~+2 yr; re-verify and apply the self-arc test.' },
  { desig: '2010 JK124', note: 'referee-verified: 8 DECam frames within +/-45 d of 2017-07-01; gate SMIA 0.57" / SMAA 3.06", V~21.6, gal b=+13.3; arc-end ~2014. Larger along-track — use the full ellipse honestly.' },
]

const RECOVER_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    designation: { type: 'string' },
    outcome: { type: 'string', enum: ['CANDIDATE_CHAIN', 'NULL_SEARCHED', 'UNUSABLE_UNCERTAINTY', 'NO_ARCHIVAL_COVERAGE', 'SELF_ARC_SKIP', 'BLOCKED'] },
    parsed_arc_end: { type: 'string', description: 'arc-end date from the fresh get-obs parse (rule 7)' },
    self_arc_check: { type: 'string', description: 'rule-8 result for each searched window' },
    epochs_searched: { type: 'integer' },
    archives_used: { type: 'string' },
    chain_evidence: { type: 'string' },
    negative_control: { type: 'string' },
    bycatch_summary: { type: 'string' },
    report_path: { type: 'string' },
  },
  required: ['designation', 'outcome', 'parsed_arc_end', 'self_arc_check', 'epochs_searched', 'chain_evidence', 'bycatch_summary', 'report_path'],
}

const REF_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    designation: { type: 'string' },
    outcome_stands: { type: 'boolean' },
    final_outcome: { type: 'string', enum: ['CANDIDATE_CHAIN', 'NULL_SEARCHED', 'UNUSABLE_UNCERTAINTY', 'NO_ARCHIVAL_COVERAGE', 'SELF_ARC_SKIP', 'BLOCKED'] },
    spot_check: { type: 'string' },
    issues: { type: 'string' },
  },
  required: ['designation', 'outcome_stands', 'final_outcome', 'spot_check'],
}

const PIXEL_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    designation: { type: 'string' },
    verdict: { type: 'string', enum: ['CONFIRMED', 'WEAKENED', 'REFUTED', 'BLOCKED'] },
    detections_checked: { type: 'integer' },
    pixel_evidence: { type: 'string' },
    updated_astrometry_path: { type: 'string' },
    report_path: { type: 'string' },
  },
  required: ['designation', 'verdict', 'detections_checked', 'pixel_evidence', 'report_path'],
}

phase('Recover')
const results = await pipeline(
  TARGETS,
  t => agent(
    ENV + '\n\nTARGET: "' + t.desig + '" — ' + t.note + '\n'
    + 'MISSION: real archival precovery/recovery attempt per rules 1-8. Steps: fresh MPC get-obs parse\n'
    + '(rule 7) -> self-arc test on the 2017-07 DECam window (rule 8) -> re-derive per-night ephemeris\n'
    + '+ 3-sigma boxes for the SSOIS-confirmed frames -> NSC DR2 catalog search re-centered per night\n'
    + '(transient non-mean-object sources, mag sanity) -> Datalink _ooi_ cutout inspection where\n'
    + 'inconclusive -> full chain discipline incl. +1 deg negative control -> MANDATORY bycatch pass\n'
    + '(rule 5). Write REPORT.md + search_log.csv (+ candidate_astrometry.csv if a chain emerges) under\n'
    + '/tmp/precovery_wave4/' + t.desig.replace(' ', '_') + '/. Honest buckets; a fake chain is the only failure.',
    { label: 'recover:' + t.desig, phase: 'Recover', schema: RECOVER_SCHEMA, model: 'opus', effort: 'high' }
  ),
  (res, t) => {
    if (!res) return null
    return agent(
      ENV + '\n\nADVERSARIAL REFEREE for the wave-4 attempt on "' + t.desig + '" (outputs under\n'
      + '/tmp/precovery_wave4/). If CANDIDATE_CHAIN: re-derive ephemerides (jd-keyed), re-check every\n'
      + 'detection (separation, motion, stationary rejection vs deep catalogs/coadds, magnitude), re-run\n'
      + 'the negative control; demote on ANY failed guard. If NULL/other: spot-check 2 nights (correct\n'
      + 'centering, adequate depth, full window coverage) — mis-centered/shallow boxes VOID absence\n'
      + 'claims. Verify rules 7+8 were actually applied (re-parse get-obs yourself) and the bycatch CSV\n'
      + 'exists with an honest unknown count.\n\n===== CLAIMED =====\n' + JSON.stringify(res, null, 1),
      { label: 'referee:' + t.desig, phase: 'Referee', schema: REF_SCHEMA, model: 'opus', effort: 'high' }
    ).then(ref => ({ target: t.desig, result: res, referee: ref }))
  },
  (staged, t) => {
    if (!staged) return null
    const isChain = staged.referee && staged.referee.outcome_stands !== false
      && staged.referee.final_outcome === 'CANDIDATE_CHAIN'
    if (!isChain) return Promise.resolve({ ...staged, pixel: null })
    return agent(
      ENV + '\n\nPIXEL VERIFIER for the referee-approved chain on "' + t.desig + '" (astrometry under\n'
      + '/tmp/precovery_wave4/' + t.desig.replace(' ', '_') + '/). For EACH detection: FITS cutout of the exact\n'
      + 'exposure (_ooi_), PSF-like unblended source vs field stars (same-night sibling check — not a CR),\n'
      + 're-centroid, moving-object test (absent at position in other epochs / deep coadds). Emit\n'
      + 'updated_astrometry.csv + REPORT.md. CONFIRMED only if every detection passes.',
      { label: 'pixel:' + t.desig, phase: 'Pixel', schema: PIXEL_SCHEMA, model: 'opus', effort: 'high' }
    ).then(px => ({ ...staged, pixel: px }))
  }
)

phase('Synthesize')
const SYNTH_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    headline: { type: 'string' },
    per_target: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          designation: { type: 'string' },
          final_state: { type: 'string' },
          one_line: { type: 'string' },
          submission_ready: { type: 'boolean' },
        },
        required: ['designation', 'final_state', 'one_line'],
      },
    },
    bycatch_report: { type: 'string' },
    user_actions: { type: 'string' },
    campaign_learnings: { type: 'string' },
    next_recommendation: { type: 'string' },
  },
  required: ['headline', 'per_target', 'bycatch_report', 'user_actions'],
}
const synthesis = await agent(
  'Synthesize precovery wave 4 (refereed + pixel-verified results below). Per target: final state,\n'
  + 'one line, submission-ready flag. Aggregate bycatch. Exact USER actions (we submit nothing).\n'
  + 'Learnings + next recommendation. No inflation.\n\n'
  + '===== WAVE-4 RESULTS =====\n' + JSON.stringify(results.filter(Boolean), null, 1),
  { label: 'synthesize-wave4', phase: 'Synthesize', schema: SYNTH_SCHEMA, model: 'opus', effort: 'xhigh' }
)

return { wave: results.filter(Boolean), synthesis }
