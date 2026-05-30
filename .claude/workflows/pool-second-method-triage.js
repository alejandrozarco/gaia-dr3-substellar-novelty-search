export const meta = {
  name: 'pool-second-method-triage',
  description: 'Triage a list of dark-companion candidates by archival RV: census + NSS-locked Keplerian + classify CORROBORATED/REFUTED/INCONCLUSIVE/NO-RV, with an adversarial verify pass on every CORROBORATED.',
  whenToUse: 'Second-method triage of a candidate pool. args: {source_ids: ["id1","id2",...]} (Gaia DR3 ids as STRINGS).',
  phases: [
    { title: 'Triage' },
    { title: 'Verify' },
  ],
}

// Normalize args: runtime may deliver an object, a JSON string, or a bare value.
const A = (typeof args === 'string')
  ? (() => { const s = args.trim(); try { return (s[0] === '{' || s[0] === '[') ? JSON.parse(s) : { source_ids: [s] } } catch (e) { return { source_ids: [s] } } })()
  : (args || {})
const SIDS = ((Array.isArray(A) ? A : A.source_ids) || []).map(String).filter(s => /^\d{5,}$/.test(s))
if (!SIDS.length) throw new Error('pass args: {source_ids: ["<Gaia DR3 id>", ...]} as STRINGS')
const PY = '/Users/legbatterij/claude_projects/ostinato/.venv/bin/python'
const CWD = '/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27'
const TR = { type: 'object', properties: { source_id: { type: 'string' }, verdict: { type: 'string' }, n_distinct_phases: { type: 'integer' }, K1: { type: 'string' }, fM_rv_vs_phot: { type: 'string' }, M2: { type: 'string' }, note: { type: 'string' } }, required: ['source_id', 'verdict'] }
const VF = { type: 'object', properties: { source_id: { type: 'string' }, holds: { type: 'boolean' }, revised_verdict: { type: 'string' }, why: { type: 'string' } }, required: ['source_id', 'holds', 'revised_verdict'] }

log(`Triaging ${SIDS.length} candidates`)
const results = await pipeline(
  SIDS,
  (sid) => agent(
    `cwd ${CWD}, python ${PY} (no pip-install). Second-method triage of Gaia DR3 ${sid}: fetch its NSS solution (P,e,T0); cone-search archival RV (LAMOST LRS V/164, LAMOST MRS V/162, APOGEE DR17 III/286, GALAH DR3/DR4, RAVE DR6); count DISTINCT phase bins (clustered same-MJD epochs = ONE phase). If >=2 distinct phases, fit the NSS-locked Keplerian (>=1 km/s error floor) and compare spectroscopic f(M)_RV to astrometric f_phot. Classify CORROBORATED (RV varies with the orbit, f's agree) / REFUTED (f_RV >> f_phot => closer/inner binary, or SB2) / INCONCLUSIVE (too few/clustered) / NO_ARCHIVAL_RV. Reuse scripts/ns_pool_triage_2026_05_28.py. Return source_id=${sid}.`,
    { label: `triage:${sid.slice(-5)}`, phase: 'Triage', agentType: 'general-purpose', schema: TR }
  ),
  (tri, sid) => (tri && /CORROBOR/i.test(tri.verdict || ''))
    ? agent(
        `Adversarially verify the CORROBORATED claim for Gaia DR3 ${sid}. Triage said: ${JSON.stringify(tri)}. Re-check independently: are the RV epochs truly at >=3 distinct phases (not clustered in one MJD window)? Is K1 genuinely constrained (not an overfit to one phase, not driven by underestimated errors)? Does f(M)_RV really match f_phot within ~1 sigma? Default to DOWNGRADE unless it clearly holds. Return holds(bool) + revised_verdict + why.`,
        { label: `verify:${sid.slice(-5)}`, phase: 'Verify', agentType: 'general-purpose', schema: VF }
      ).then(v => ({ ...tri, verify: v }))
    : tri
)

const clean = results.filter(Boolean)
const tally = {}
for (const r of clean) { const v = (r.verify && r.verify.revised_verdict) || r.verdict || 'UNK'; tally[v] = (tally[v] || 0) + 1 }
const corroborated = clean.filter(r => /CORROBOR/i.test((r.verify && r.verify.revised_verdict) || r.verdict || '') && (!r.verify || r.verify.holds))
log(`done: ${JSON.stringify(tally)} | ${corroborated.length} survive verification`)
return { n: clean.length, tally, corroborated, all: clean }
