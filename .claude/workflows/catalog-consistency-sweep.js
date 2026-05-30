export const meta = {
  name: 'catalog-consistency-sweep',
  description: 'Read-only blast-radius sweep: find every public-facing mention of a claim/source across CANDIDATES.md, dossiers, README, CITATION, and GitHub release notes, and return a precise correction checklist. (Apply + commit + push stay manual — parallel agents must not edit the same files, and publishing needs human confirmation.)',
  whenToUse: 'Before/while retracting or correcting a claim, or as a pre-release audit. args: {query:"<source_id | object name | claim phrase>"} or {audit:true} for a whole-catalog overclaim sweep.',
  phases: [
    { title: 'Sweep' },
    { title: 'Checklist' },
  ],
}

const CWD = '/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27'
// Normalize args: the runtime may deliver it as an object, a JSON string, or a bare value.
const A = (typeof args === 'string')
  ? (() => { const s = args.trim(); try { return (s[0] === '{' || s[0] === '[') ? JSON.parse(s) : { query: s } } catch (e) { return { query: s } } })()
  : (args || {})
const Q = A.query ? String(A.query) : null
const AUDIT = !!A.audit
if (!Q && !AUDIT) throw new Error('pass args: {query:"<source_id|name|phrase>"} or {audit:true}')
const target = Q ? `the claim/object "${Q}"` : 'ANY overclaim (CONFIRMED / STRONG / discovery / mass-gap BH / first-detection language not matching the current verdict in CANDIDATES.md)'
const M = { type: 'object', properties: { surface: { type: 'string' }, hits: { type: 'array', items: { type: 'object' } }, summary: { type: 'string' } }, required: ['surface', 'summary'], additionalProperties: true }
const sweep = (label, prompt) => agent(`READ-ONLY (do not edit anything). cwd ${CWD}. ` + prompt, { label, phase: 'Sweep', agentType: 'Explore', schema: M })

phase('Sweep')
const [cand, doss, front, rel] = await parallel([
  () => sweep('candidates', `In docs/CANDIDATES.md, find every line mentioning ${target}. Quote each with its line number and say whether it is consistent with the object's current verdict or is a stale overclaim.`),
  () => sweep('dossiers', `Across docs/dossiers/*.md, find every dossier mentioning ${target}. For each, report the file, whether it has a ⚠ retraction/DEMOTED/DOWNGRADED banner at the top, and whether the body verdict (One-line/Class/Verdict lines) still asserts a stronger claim than the current status.`),
  () => sweep('frontpage', `In README.md and CITATION.cff, find every mention of ${target} (incl. the "Confirmed candidates" section, badges, and the CITATION abstract). Quote each and flag stale claims.`),
  () => sweep('releases', `Use the gh CLI (read-only: gh release list, gh release view <tag>) for repo alejandrozarco/gaia-dr3-substellar-novelty-search. Find which release notes mention ${target}, and whether each release is flagged SUPERSEDED where appropriate. Report tag + the relevant lines. Do not create/edit/delete releases.`),
])

phase('Checklist')
const checklist = await agent(
  `Synthesize a precise CORRECTION CHECKLIST from these read-only sweeps (target: ${target}).\n` +
  `CANDIDATES.md: ${JSON.stringify(cand)}\nDossiers: ${JSON.stringify(doss)}\nFront page: ${JSON.stringify(front)}\nReleases: ${JSON.stringify(rel)}\n` +
  `Output an ordered, file-by-file checklist of exact edits needed to make the public record consistent (which file, which line/section, old->new), plus which releases need a SUPERSEDED banner. Mark anything that is ALREADY correct as "OK - no change". Note explicitly that the edits + git commit/push + any release changes are to be applied in the main thread (not by this workflow), and that release deletion is never appropriate (use superseded banners + a new version).`,
  { label: 'checklist', phase: 'Checklist', schema: { type: 'object', properties: { edits: { type: 'array', items: { type: 'object', properties: { file: { type: 'string' }, where: { type: 'string' }, change: { type: 'string' } }, required: ['file', 'change'] } }, releases_to_flag: { type: 'array', items: { type: 'string' } }, already_ok: { type: 'array', items: { type: 'string' } } }, required: ['edits'] } }
)
log(`sweep complete: ${checklist.edits.length} edits proposed`)
return { target: Q || 'AUDIT', checklist }
