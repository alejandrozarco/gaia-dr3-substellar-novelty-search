export const meta = {
  name: 'archival-rv-monitor',
  description: 'Re-check a watchlist of candidates for newly-published archival RV epochs (LAMOST/APOGEE/GALAH/RAVE) that could confirm or refute them; re-runs the NSS-locked Keplerian and flags any change vs the last-known epoch count.',
  whenToUse: 'Periodically (e.g. on a schedule), or after a new spectroscopic survey DR. args: {source_ids:[...]} (strings); defaults to the standing watchlist.',
  phases: [{ title: 'Recheck' }, { title: 'Report' }],
}
const DEFAULT_WATCH = [
  '3378588057203660160', // HD 264291 (heavy NS, RV-confirmed)
  '3155543945892767232', // candidate NS (needs more LAMOST phases)
  '5858574810404752256', // triple-favored; new RV could settle
  '4111149395881722496', // HD 157033 (ambiguous; needs clean optical RV)
  '1593152388271709824', // marginal (settling epoch near periastron 2026-01-20)
]
const A = (typeof args === 'string') ? (() => { const s = args.trim(); try { return (s[0] === '{' || s[0] === '[') ? JSON.parse(s) : { source_ids: [s] } } catch (e) { return {} } })() : (args || {})
const WATCH = ((Array.isArray(A) ? A : A.source_ids) || DEFAULT_WATCH).map(String).filter(s => /^\d{5,}$/.test(s))
const PY = '/Users/legbatterij/claude_projects/ostinato/.venv/bin/python'
const CWD = '/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27'
const C = { type: 'object', properties: { source_id: { type: 'string' }, n_epochs: { type: 'integer' }, new_since_dossier: { type: 'boolean' }, verdict_change: { type: 'string' }, note: { type: 'string' } }, required: ['source_id', 'new_since_dossier'], additionalProperties: true }

log(`monitoring ${WATCH.length} candidates for new archival RV`)
phase('Recheck')
const checks = await parallel(WATCH.map(sid => () => agent(
  `cwd ${CWD}, python ${PY} (no pip-install). For Gaia DR3 ${sid}: cone-search archival RV (LAMOST LRS V/164, LAMOST MRS V/162, APOGEE DR17 III/286, GALAH DR3/DR4, RAVE DR6); count epochs and distinct phases. Compare to the epoch count recorded in its dossier under docs/dossiers/ (grep for the source_id). Report whether there are NEW epochs since the dossier, and if >=2 distinct phases now exist, re-run the NSS-locked Keplerian and state whether the verdict would change (corroborate / refute / still inconclusive). Reuse scripts/ns_pool_triage_2026_05_28.py.`,
  { label: `rv:${sid.slice(-5)}`, phase: 'Recheck', agentType: 'general-purpose', schema: C }
)))

const clean = checks.filter(Boolean)
const movers = clean.filter(c => c.new_since_dossier)
phase('Report')
log(`done: ${movers.length}/${clean.length} have new archival RV`)
return { checked: clean.length, with_new_rv: movers.length, movers, all: clean }
