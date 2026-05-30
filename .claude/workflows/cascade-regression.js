export const meta = {
  name: 'cascade-regression',
  description: 'Validate the v2 cascade against frozen truth sets: known dormant BH/NS (should pass Tier-1), known SB2/triple/stellar binaries (should be rejected/demoted), and the Shahaf+2023 compact-vs-triple labels. Reports recall, specificity, agreement, and any regressions.',
  whenToUse: 'After any change to consumer_v2.py / filters / thresholds, or as a pre-release gate, to confirm the engine still works. args: {} (optional).',
  phases: [{ title: 'Run' }, { title: 'Score' }],
}
const PY = '/Users/legbatterij/claude_projects/ostinato/.venv/bin/python'
const CWD = '/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27'
const R = { type: 'object', properties: { set: { type: 'string' }, n: { type: 'integer' }, correct: { type: 'integer' }, rate: { type: 'string' }, misses: { type: 'array', items: { type: 'string' } } }, required: ['set', 'rate'], additionalProperties: true }

phase('Run')
const [pos, neg, shahaf] = await parallel([
  () => agent(`cwd ${CWD}, python ${PY} (no pip-install). Run the v2 cascade (scripts/streaming/v2_corrected/consumer_v2.py: derive_row_v2 + tier_label, reuse the bundled fixtures in tests/) on the frozen KNOWN dormant-compact-object POSITIVES (e.g. Gaia BH2 = 5870569352746779008, plus the project's positive test set). Each SHOULD classify Tier-1 BH or NS. Report recall = fraction correctly Tier-1, and list any misses with the demotion reason.`, { label: 'positives', phase: 'Run', agentType: 'general-purpose', schema: R }),
  () => agent(`cwd ${CWD}, python ${PY}. Run the v2 cascade on the frozen NEGATIVE control set (known SB2 / resolved stellar binaries / chromatic K-giants — e.g. HD 1957, and the negative_control fixtures under tests/ + data). Each SHOULD be rejected or demoted (NOT Tier-1 compact). Report specificity = fraction correctly rejected, and list any false positives that slipped to Tier-1.`, { label: 'negatives', phase: 'Run', agentType: 'general-purpose', schema: R }),
  () => agent(`cwd ${CWD}, python ${PY}. For the project's M1-corrected Tier-1 NS/BH candidates (data/derived/*_M1corrected.parquet) that are ALSO in Shahaf+2023 (Vizier J/MNRAS/518/2991), compare our compact classification vs Shahaf PIII (compact probability). Report agreement rate and notable disagreements (we say compact while Shahaf PIII<0.5 = likely triple, or vice versa).`, { label: 'shahaf-xcheck', phase: 'Run', agentType: 'general-purpose', schema: R }),
])

phase('Score')
const score = await agent(`Cascade regression scorecard. Positives (recall): ${JSON.stringify(pos)}. Negatives (specificity): ${JSON.stringify(neg)}. Shahaf cross-check: ${JSON.stringify(shahaf)}. Compare against the project's documented baselines (recall ~93%, high specificity). Output PASS/FAIL and flag any regression that must be investigated before a release.`, { label: 'scorecard', phase: 'Score', schema: { type: 'object', properties: { recall: { type: 'string' }, specificity: { type: 'string' }, shahaf_agreement: { type: 'string' }, regressions: { type: 'array', items: { type: 'string' } }, verdict: { type: 'string' } }, required: ['verdict'] } })
log(`cascade-regression: ${score.verdict}`)
return { score }
