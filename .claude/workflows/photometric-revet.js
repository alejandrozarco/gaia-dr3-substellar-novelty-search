export const meta = {
  name: 'photometric-revet',
  description: 'Rigorously re-test a claimed photometric period/eclipse (CV or ellipsoidal) with outburst-masked Lomb-Scargle/BLS + permutation FAP on ZTF, and the real SPOC product (not per-eclipse minima) on TESS. Built to catch the false-positive mode that sank the CV-period avenue.',
  whenToUse: 'Verify or falsify a claimed orbital period / eclipse. args: {source_id:"...", claimed_period_min: <number>, ra?: <deg>, dec?: <deg>}.',
  phases: [
    { title: 'Detect' },
    { title: 'Verdict' },
  ],
}

const A = (typeof args === 'string') ? (() => { try { return JSON.parse(args.trim()) } catch (e) { return {} } })() : (args || {})
const SID = String(A.source_id || '').trim()
const Pmin = Number(A.claimed_period_min)
if (!/^\d{5,}$/.test(SID) || !(Pmin > 0)) throw new Error('pass args: {source_id:"<id string>", claimed_period_min:<number>}')
const PY = '/Users/legbatterij/claude_projects/ostinato/.venv/bin/python'
const CWD = '/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27'
const D = { type: 'object', properties: { detected: { type: 'boolean' }, finding: { type: 'string' }, values: { type: 'object' } }, required: ['detected', 'finding'], additionalProperties: true }

phase('Detect')
const [ztf, tess] = await parallel([
  () => agent(
    `cwd ${CWD}, python ${PY} (no pip-install). ZTF re-vet of Gaia DR3 ${SID}, claimed P=${Pmin} min. Re-fetch the ZTF light curve from IRSA nph_light_curves (cone 5", g/r/i, catflags==0). Per band: MASK OUTBURSTS (>0.75 mag brighter than the per-band median; eclipses preserved), report per-cadence S/N. Run Lomb-Scargle on the MASKED data (freq 0.5-20/d): peak period + analytic + bootstrap FAP, the power+FAP AT the claimed period, and whether the top peaks are 1-sidereal-day aliases. Run BLS on masked flux: best period PER BAND (do the bands AGREE with each other and with the claim?). Compare masked vs unmasked. Reuse scripts/crts_j051419_ztf_recheck.py. Verdict: real period / not-supported (FAP~1 at claim, bands disagree, only 1-day aliases).`,
    { label: 'ztf', phase: 'Detect', agentType: 'general-purpose', schema: D }
  ),
  () => agent(
    `cwd ${CWD}, python ${PY} (no pip-install). TESS re-vet of Gaia DR3 ${SID}, claimed P=${Pmin} min. Fetch the ACTUAL SPOC/TESS-SPOC/QLP light curve via lightkurve.search_lightcurve (NOT per-eclipse minima, NOT a custom faint-FFI extraction). Report per-cadence S/N (a source with per-cadence S/N<1 cannot have its eclipse detected — say so). Mask outbursts, fold at the claimed P, measure the binned deepest-dip significance with a PERMUTATION FAP over ~2000 random periods (and an apples-to-apples refined-null FAP: optimize the period over +-0.3% on random periods too). Reuse scripts/crts_j051419_spoc_recheck.py. Verdict: eclipse real / min-of-noise / uninformative (too faint).`,
    { label: 'tess', phase: 'Detect', agentType: 'general-purpose', schema: D }
  ),
])

phase('Verdict')
const verdict = await agent(
  `Skeptical judge for the claimed P=${Pmin} min of Gaia DR3 ${SID}. ZTF: ${JSON.stringify(ztf)}. TESS: ${JSON.stringify(tess)}. ` +
  `A period/eclipse is REAL only if: outburst-masked LS shows significant power at the claimed P (not just 1-day aliases), BLS agrees across bands, and any TESS eclipse is a genuine binned dip (low permutation/refined-null FAP) — NOT a min-of-noise artifact at per-cadence S/N<1. Default to NOT_SUPPORTED. Output: verdict in {confirmed, not_supported, uninformative}; the decisive numbers; what (if anything) is real (e.g. outbursts can be real even when the period is not).`,
  { label: 'verdict', phase: 'Verdict', schema: { type: 'object', properties: { verdict: { type: 'string' }, decisive: { type: 'string' }, what_survives: { type: 'string' } }, required: ['verdict'] } }
)
log(`${SID} P=${Pmin}min -> ${verdict.verdict}`)
return { source_id: SID, claimed_period_min: Pmin, verdict }
