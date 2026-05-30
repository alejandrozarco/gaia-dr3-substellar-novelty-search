export const meta = {
  name: 'ns-candidate-deep-dive',
  description: 'Skeptical deep-dive of one Gaia DR3 dark-companion candidate: mass derivation + archival RV + AMRF triple-vs-compact + Gaia quality + novelty, with an adversarial synthesis verdict.',
  whenToUse: 'Full workup + verdict on a single NS/BH/dark-companion candidate. args: {source_id: "<19-digit Gaia DR3 id as a STRING>"}.',
  phases: [
    { title: 'Gather' },
    { title: 'Verdict' },
  ],
}

const A = (typeof args === 'string') ? (() => { const s = args.trim(); try { return (s[0] === '{' || s[0] === '[') ? JSON.parse(s) : { source_id: s } } catch (e) { return { source_id: s } } })() : (args || {})
const SID = String(A.source_id || A.sid || '').trim()
if (!/^\d{5,}$/.test(SID)) throw new Error('pass args: {source_id: "<Gaia DR3 id as a string>"} (19-digit id; must be a string to avoid float truncation)')
const PY = '/Users/legbatterij/claude_projects/ostinato/.venv/bin/python'
const CWD = '/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27'
const S = { type: 'object', properties: { finding: { type: 'string' }, values: { type: 'object' } }, required: ['finding'], additionalProperties: true }
const ga = (label, prompt) => agent(prompt, { label, phase: 'Gather', agentType: 'general-purpose', schema: S })

phase('Gather')
const [nss, rv, gaia, amrf, novelty] = await parallel([
  () => ga('nss+mass', `cwd ${CWD}, python ${PY} (astroquery/numpy/scipy; no pip-install). For Gaia DR3 source_id ${SID}: query gaiadr3.nss_two_body_orbit (nss_solution_type, period, eccentricity, significance, Thiele-Innes A,B,F,G and spectroscopic C,H if AstroSpectroSB1, parallax, t_periastron). Compute photocentric a_phot (sqrt(u+sqrt(u^2-v^2))), f(M)=a_phot_AU^3/P_yr^2, and solve M2 at the best M1 (FLAME, else StarHorse/TIC). If AstroSpectroSB1, derive the spectroscopic K1 from C,H (resolve units to AU — see scripts/prime3_deepdive_2026_05_29.py). Report nss_solution_type, P, e, sig, a_phot, parallax, M1+source, fM, M2.`),
  () => ga('archival-rv', `cwd ${CWD}, python ${PY}. Archival-RV census for Gaia DR3 ${SID}: cone-search (5") Vizier LAMOST LRS V/164/stellar5, LAMOST MRS V/162/dr11sm, APOGEE DR17 III/286, GALAH DR3/DR4, RAVE DR6; collect (MJD, RV, err). Using the NSS P and T0, count DISTINCT orbital-phase bins (be skeptical: epochs clustered within a small MJD window are ONE phase, not many). If >=2 distinct phases, fit the NSS-locked Keplerian (fix P,e,T0; fit K1,gamma,omega) with a >=1 km/s error floor; report K1+/-err, chi2/dof, spectroscopic f(M)_RV vs astrometric f_phot. Verdict: corroborated / refuted (f_RV >> f_phot => inner/closer binary) / inconclusive / no-archival-RV. Reuse scripts/ns_pool_triage_2026_05_28.py.`),
  () => ga('gaia-quality', `cwd ${CWD}, python ${PY}. Gaia DR3 gaia_source for ${SID}: ruwe, ipd_frac_multi_peak, phot_bp_rp_excess_factor, rv_nb_transits, rv_amplitude_robust, rv_chisq_pvalue, radial_velocity, radial_velocity_error. State whether Gaia shows genuine RV variability, and note that high single-star ruwe is EXPECTED for an NSS binary (not disqualifying on its own).`),
  () => ga('amrf-triple', `cwd ${CWD}, python ${PY}. Compute the Shahaf+2019 AMRF for Gaia DR3 ${SID} (reuse scripts/prime3_deepdive_2026_05_29.py) and run the triple-vs-compact test — the discrimination the cascade mass function CANNOT make. Query Shahaf+2023 Triage I (Vizier J/MNRAS/518/2991) for this source_id: if present report A (AMRF), M2min, PII (inner-binary/triple prob), PIII (compact prob). If ABSENT, compute a calibrated P(compact|A,M1) from the full Triage-I table (nearest-neighbours in A,M1). If AstroSpectroSB1, also report spectroscopic/astrometric semi-major-axis ratio (>1 => luminous inner pair). Verdict: compact-favored vs triple-favored, with P(compact).`),
  () => ga('novelty', `For Gaia DR3 ${SID} (cwd ${CWD}, python ${PY} astroquery.simbad): SIMBAD otype + ALL bibcodes; membership in Shahaf+2023, Mueller-Horn+2026, Halbwachs+2023, El-Badry Gaia-BH series. Genuinely novel (no prior compact-object/binary characterization) or already published? Report otype, n_bibcodes, key refs, novel(yes/no).`),
])

phase('Verdict')
const verdict = await agent(
  `Skeptical synthesis judge for Gaia DR3 ${SID}. Default to the LESS exciting interpretation unless the evidence forces otherwise.\n` +
  `NSS+mass: ${JSON.stringify(nss)}\nArchival RV: ${JSON.stringify(rv)}\nGaia quality: ${JSON.stringify(gaia)}\nAMRF/triple: ${JSON.stringify(amrf)}\nNovelty: ${JSON.stringify(novelty)}\n` +
  `Hard-won rules: (1) the astrometric mass function cannot tell a single dark companion from a hierarchical triple — defer to AMRF P(compact); (2) low chi2/dof on few or single-phase RV epochs is NOT a detection; (3) M2 from the photocentric mass function needs no sin i — never inflate it via rv_amplitude/2; (4) present in Shahaf/literature => not novel. ` +
  `Output: verdict in {compact-favored, triple-favored, ambiguous, refuted, not-compact}; M2 best+range; P(compact); is_novel; 2-3 decisive facts; key caveats; the single highest-value follow-up (and whether it needs telescope time).`,
  { label: 'synthesis', phase: 'Verdict', schema: { type: 'object', properties: { verdict: { type: 'string' }, M2: { type: 'string' }, P_compact: { type: 'string' }, is_novel: { type: 'boolean' }, decisive_facts: { type: 'array', items: { type: 'string' } }, caveats: { type: 'string' }, followup: { type: 'string' } }, required: ['verdict', 'M2', 'is_novel'] } }
)

log(`${SID}: ${verdict.verdict} (novel=${verdict.is_novel})`)
return { source_id: SID, verdict }
