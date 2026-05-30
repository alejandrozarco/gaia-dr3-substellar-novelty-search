export const meta = {
  name: 'new-data-reingest',
  description: 'Re-run the full discovery pipeline on a new data release: producer cuts -> v2 cascade -> M1 correction -> diff candidate tiers vs the current catalog -> flag movers and new compact candidates. Heavy; runs the project pipeline end-to-end.',
  whenToUse: 'When a new Gaia DR / archive release lands. args: {release: "Gaia DR4"} (a label; the agents locate the actual tables).',
  phases: [{ title: 'Ingest' }, { title: 'Cascade' }, { title: 'Diff' }],
}
const A = (typeof args === 'string') ? (() => { const s = args.trim(); try { return (s[0] === '{') ? JSON.parse(s) : { release: s } } catch (e) { return { release: s } } })() : (args || {})
const REL = String(A.release || 'NEW-RELEASE')
const PY = '/Users/legbatterij/claude_projects/ostinato/.venv/bin/python'
const CWD = '/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27'
const S = { type: 'object', properties: { finding: { type: 'string' }, values: { type: 'object' } }, required: ['finding'], additionalProperties: true }

phase('Ingest')
const ingest = await agent(`cwd ${CWD}, python ${PY} (no pip-install). Ingest the ${REL} NSS / astrometric-binary tables (Orbital, AstroSpectroSB1, OrbitalAlternative, Acceleration) and apply the v2 producer cuts (mirror scripts/streaming/v2_corrected/). Report row counts per channel and the output parquet path.`, { label: 'ingest', phase: 'Ingest', agentType: 'general-purpose', schema: S })

phase('Cascade')
const cascade = await agent(`cwd ${CWD}, python ${PY}. Run the v2 cascade (consumer_v2.derive_row_v2 + tier_label) on the ${REL} ingested rows, THEN apply the M1 correction (select_m1: FLAME -> StarHorse -> TIC) so M2 and tiers are correct from the start (avoid the fixed-M1=1.5 bias). Report tier counts (Tier-1 BH, Tier-1 NS, Tier-2, Characterized). Ingest summary: ${JSON.stringify(ingest)}.`, { label: 'cascade', phase: 'Cascade', agentType: 'general-purpose', schema: S })

phase('Diff')
const diff = await agent(`cwd ${CWD}, python ${PY}. Diff the ${REL} M1-corrected Tier-1 NS/BH candidates against the CURRENT catalog (data/derived/*_M1corrected.parquet + docs/CANDIDATES.md): which source_ids are NEW, which changed tier, which dropped. For the NEW Tier-1 compact candidates, list the top ~15 by significance as follow-up targets (for ns-candidate-deep-dive / pool-second-method-triage). Cascade summary: ${JSON.stringify(cascade)}.`, { label: 'diff', phase: 'Diff', agentType: 'general-purpose', schema: { type: 'object', properties: { new_candidates: { type: 'array', items: { type: 'string' } }, tier_changes: { type: 'string' }, top_followup: { type: 'array', items: { type: 'string' } } }, required: ['tier_changes'] } })
log(`new-data-reingest(${REL}): ${(diff.new_candidates || []).length} new Tier-1 compact candidates`)
return { release: REL, ingest, cascade, diff }
