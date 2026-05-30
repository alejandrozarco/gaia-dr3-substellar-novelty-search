export const meta = {
  name: 'wd-binary-sed-vet',
  description: 'Vet a white-dwarf-primary NSS candidate (Pile E): SED 2-component fit to exclude M-dwarf / hot-WD companions, photocentric mass function, Type-Ia (M_total vs Chandrasekhar) assessment, and novelty.',
  whenToUse: 'A WD-primary + dark-companion candidate. args: {source_id: "<Gaia DR3 id string>"}.',
  phases: [{ title: 'Gather' }, { title: 'Verdict' }],
}
const A = (typeof args === 'string') ? (() => { const s = args.trim(); try { return (s[0] === '{' || s[0] === '[') ? JSON.parse(s) : { source_id: s } } catch (e) { return { source_id: s } } })() : (args || {})
const SID = String(A.source_id || A.sid || '').trim()
if (!/^\d{5,}$/.test(SID)) throw new Error('pass args: {source_id: "<Gaia DR3 id as a string>"}')
const PY = '/Users/legbatterij/claude_projects/ostinato/.venv/bin/python'
const CWD = '/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27'
const S = { type: 'object', properties: { finding: { type: 'string' }, values: { type: 'object' } }, required: ['finding'], additionalProperties: true }

phase('Gather')
const [sed, mass, novelty] = await parallel([
  () => agent(`cwd ${CWD}, python ${PY} (no pip-install). SED of Gaia DR3 ${SID}: gather GALEX FUV/NUV, SDSS/SkyMapper ugriz, Pan-STARRS grizy, 2MASS JHK, AllWISE W1-W4. Fit a 2-component (WD + companion) SED. EXCLUDE an M-dwarf companion (W1/W2 IR excess) and a hot-WD companion (GALEX NUV / blue-optical excess) at the achievable sigma. Report M1(WD) from cooling models (Gentile Fusillo 2021 if present) and which companion classes survive (cool DD / M-dwarf / dark-NS).`, { label: 'sed', phase: 'Gather', agentType: 'general-purpose', schema: S }),
  () => agent(`cwd ${CWD}, python ${PY}. NSS solution + photocentric mass function for ${SID}; solve M2 at the WD M1 (GF21/cooling-track). Report P, e, M1, M2, M_total, and whether M_total exceeds the Chandrasekhar mass (1.4 M⊙) — which, IF the companion is also a WD, flags a Type-Ia-progenitor candidate; otherwise sub-Chandrasekhar.`, { label: 'mass', phase: 'Gather', agentType: 'general-purpose', schema: S }),
  () => agent(`For Gaia DR3 ${SID} (cwd ${CWD}, python ${PY}): SIMBAD otype + bibcodes; presence in Gentile Fusillo 2021 WD catalog; any prior binarity study. Novel as a WD-binary characterization?`, { label: 'novelty', phase: 'Gather', agentType: 'general-purpose', schema: S }),
])

phase('Verdict')
const verdict = await agent(`WD-binary verdict for Gaia DR3 ${SID}. SED: ${JSON.stringify(sed)}. Mass: ${JSON.stringify(mass)}. Novelty: ${JSON.stringify(novelty)}. Classify the system (WD+WD double-degenerate / WD+M-dwarf / WD+dark-NS) and the Type-Ia status (Type-Ia-progenitor ONLY if M_total > 1.4 AND the companion is a WD; else sub-Chandrasekhar). Default conservative. Output verdict, M_total, type_ia(bool), is_novel(bool), and the single best follow-up (usually a first RV epoch / X-shooter or HARPS).`, { label: 'verdict', phase: 'Verdict', schema: { type: 'object', properties: { verdict: { type: 'string' }, M_total: { type: 'string' }, type_ia: { type: 'boolean' }, is_novel: { type: 'boolean' }, followup: { type: 'string' } }, required: ['verdict'] } })
log(`${SID}: ${verdict.verdict}`)
return { source_id: SID, verdict }
