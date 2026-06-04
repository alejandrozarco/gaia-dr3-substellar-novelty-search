export const meta = {
  name: 'pre-release-audit',
  description: 'Pre-release integrity gate: whole-catalog overclaim sweep + test suite + git/sync check + README/CITATION/CANDIDATES consistency + object-journal consistency. Returns GO / NO-GO + a fix checklist. (Would have caught the README/CITATION "confirmed" misses.)',
  whenToUse: 'Before cutting any GitHub/Zenodo release. args: {} (optional).',
  phases: [{ title: 'Checks' }, { title: 'Gate' }],
}
const PY = '/Users/legbatterij/claude_projects/ostinato/.venv/bin/python'
const CWD = '/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27'

phase('Checks')
const [overclaims, tests, gitst, consistency, journals] = await parallel([
  () => agent(`READ-ONLY (do not edit). cwd ${CWD}. Whole-catalog overclaim sweep: across docs/CANDIDATES.md + docs/dossiers/*.md + README.md + CITATION.cff, find every CONFIRMED / STRONG / "discovery" / mass-gap-BH / first-detection claim and check it matches the object's CURRENT verdict. A downgraded dossier MUST carry a ⚠ retraction/DEMOTED/DOWNGRADED banner at the top. List every stale overclaim (file + line).`, { label: 'overclaims', phase: 'Checks', agentType: 'Explore', schema: { type: 'object', additionalProperties: true, properties: { stale: { type: 'array', items: { type: 'string' } } }, required: ['stale'] } }),
  () => agent(`cwd ${CWD}. Run the test suite: ${PY} -m pytest tests/ -q. Report passed/failed counts and any failure names.`, { label: 'tests', phase: 'Checks', agentType: 'general-purpose', schema: { type: 'object', additionalProperties: true, properties: { passed: { type: 'integer' }, failed: { type: 'integer' } }, required: ['failed'] } }),
  () => agent(`cwd ${CWD}. Read-only git check: is the working tree clean, and is local main == origin/main (everything pushed)? Report clean(bool), pushed(bool), and ahead/behind counts.`, { label: 'git', phase: 'Checks', agentType: 'general-purpose', schema: { type: 'object', additionalProperties: true, properties: { clean: { type: 'boolean' }, pushed: { type: 'boolean' } }, required: ['clean', 'pushed'] } }),
  () => agent(`READ-ONLY. cwd ${CWD}. Cross-check headline consistency: do the README "Confirmed candidates" section, the CITATION.cff abstract, and the CANDIDATES.md headline agree with EACH OTHER and with the actual dossier verdicts (counts of confirmed / strong / candidates)? Flag any inconsistency.`, { label: 'consistency', phase: 'Checks', agentType: 'Explore', schema: { type: 'object', additionalProperties: true, properties: { consistent: { type: 'boolean' }, issues: { type: 'array', items: { type: 'string' } } }, required: ['consistent'] } }),
  () => agent(`cwd ${CWD}. Object-journal consistency gate: run ${PY} scripts/journal/journal.py index && ${PY} scripts/journal/check_consistency.py ; echo EXIT=$?. Report ok (bool: did check_consistency.py exit 0?) and any HARD failure lines (a dossier with no journal, a malformed journal, or INDEX out of sync).`, { label: 'journals', phase: 'Checks', agentType: 'general-purpose', schema: { type: 'object', additionalProperties: true, properties: { ok: { type: 'boolean' }, failures: { type: 'array', items: { type: 'string' } } }, required: ['ok'] } }),
])

phase('Gate')
const gate = await agent(`Release gate decision. Overclaims: ${JSON.stringify(overclaims)}. Tests: ${JSON.stringify(tests)}. Git: ${JSON.stringify(gitst)}. Consistency: ${JSON.stringify(consistency)}. Journals: ${JSON.stringify(journals)}. Decide GO or NO-GO. NO-GO if any stale overclaim, any failing test, an unclean/unpushed tree, a headline inconsistency, or a journal-consistency failure (a dossier with no journal, a malformed journal, or INDEX out of sync). Give the exact blocking items and a fix checklist (edits to apply in the main thread). Reminder: never delete a DOI'd release — supersede it with a banner + a new version.`, { label: 'gate', phase: 'Gate', schema: { type: 'object', properties: { decision: { type: 'string' }, blockers: { type: 'array', items: { type: 'string' } }, checklist: { type: 'array', items: { type: 'string' } } }, required: ['decision'] } })
log(`pre-release-audit: ${gate.decision}`)
return { gate }
