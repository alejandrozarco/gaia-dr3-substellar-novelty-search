export const meta = {
  name: 'substellar-vet',
  description: 'Vet a substellar NSS candidate (Pile B): primary mass + photocentric mass function + inclination-marginalized M2 distribution, the TESS/ZTF dark-companion photometric limit (no ellipsoidal/eclipse => dark across all i), and novelty.',
  whenToUse: 'An M-dwarf super-Jupiter / brown-dwarf candidate. args: {source_id: "<Gaia DR3 id string>"}.',
  phases: [{ title: 'Gather' }, { title: 'Verdict' }],
}
const A = (typeof args === 'string') ? (() => { const s = args.trim(); try { return (s[0] === '{' || s[0] === '[') ? JSON.parse(s) : { source_id: s } } catch (e) { return { source_id: s } } })() : (args || {})
const SID = String(A.source_id || A.sid || '').trim()
if (!/^\d{5,}$/.test(SID)) throw new Error('pass args: {source_id: "<Gaia DR3 id as a string>"}')
const PY = '/Users/legbatterij/claude_projects/ostinato/.venv/bin/python'
const CWD = '/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27'
const S = { type: 'object', properties: { finding: { type: 'string' }, values: { type: 'object' } }, required: ['finding'], additionalProperties: true }

phase('Gather')
const [mass, phot, novelty] = await parallel([
  () => agent(`cwd ${CWD}, python ${PY} (no pip-install). For Gaia DR3 ${SID}: primary M1 (an M dwarf — FLAME/StarHorse or a mass-luminosity relation), NSS P, e, a_phot, photocentric mass function. Report M2 FACE-ON (the minimum), and the inclination-marginalized M2 distribution: P(planet <0.013 M⊙), P(BD 0.013-0.08), P(substellar <0.08), P(stellar >0.08). Be explicit that the headline mass is a minimum and the true mass scales as 1/sin i.`, { label: 'mass', phase: 'Gather', agentType: 'general-purpose', schema: S }),
  () => agent(`cwd ${CWD}, python ${PY}. Fetch all TESS sectors (lightkurve) + ZTF for ${SID}; phase-fold at P and P/2; measure the ellipsoidal/eclipse amplitude LIMIT. A stellar companion would produce ellipsoidal modulation at P/2 — a clean non-detection across the available baseline implies the companion is dark/substellar across all inclinations. Report the amplitude limit + interpretation, and HONESTLY flag if the coverage is too short for the (often long) orbital period (then it is uninformative).`, { label: 'photometry', phase: 'Gather', agentType: 'general-purpose', schema: S }),
  () => agent(`For Gaia DR3 ${SID} (cwd ${CWD}, python ${PY}): SIMBAD otype + bibcodes; any prior planet/BD/companion claim or orbit solution. Novel as an NSS-derived substellar candidate?`, { label: 'novelty', phase: 'Gather', agentType: 'general-purpose', schema: S }),
])

phase('Verdict')
const verdict = await agent(`Substellar verdict for Gaia DR3 ${SID}. Mass: ${JSON.stringify(mass)}. Photometry: ${JSON.stringify(phot)}. Novelty: ${JSON.stringify(novelty)}. Classify: super-Jupiter / brown-dwarf / stellar-at-low-inclination / ambiguous. Default conservative — do NOT claim a planet if a low-inclination stellar companion is allowed and the photometry can't rule it out (the headline mass is the edge-on minimum; the central/true mass can be much higher, ∝1/sin i, possibly into the stellar regime). Output verdict, M2 range (face-on minimum → central-solution → inclination-marginalized), P(substellar), is_novel(bool), the best follow-up, plus journal_entry (a dated entry body for docs/object_journals/${SID}.md) and ledger_rows (one per catalog/method checked: {catalog, query, result, provenance}, including NULL/NOT-IN results — esp. Shahaf / Marcussen & Albrecht 2023 / Bailer-Jones & Kreidberg 2026 / SIMBAD membership).`, { label: 'verdict', phase: 'Verdict', schema: { type: 'object', properties: { verdict: { type: 'string' }, M2: { type: 'string' }, P_substellar: { type: 'string' }, is_novel: { type: 'boolean' }, followup: { type: 'string' }, journal_entry: { type: 'string' }, ledger_rows: { type: 'array', items: { type: 'object', properties: { catalog: { type: 'string' }, query: { type: 'string' }, result: { type: 'string' }, provenance: { type: 'string' } }, required: ['catalog', 'result'] } } }, required: ['verdict'] } })
log(`${SID}: ${verdict.verdict} — main thread: append verdict.journal_entry + ledger_rows via scripts/journal/journal.py`)
return { source_id: SID, verdict }
