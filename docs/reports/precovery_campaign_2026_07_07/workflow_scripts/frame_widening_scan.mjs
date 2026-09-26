export const meta = {
  name: 'frame-widening-discovery-scan',
  description: 'Research pivots/long shots OUTSIDE the exhausted compact-object frame: amateur-persistent niches, under-mined archives, relaxed community-confirm routes, and the unfired GO-IF menu items — web-grounded, ledger-pinned, adversarially verified',
  phases: [
    { title: 'Ledger', detail: 'closed lanes + unfired GO-IF items + toolkit assets' },
    { title: 'Ideate', detail: '7 frame-widened lenses, web-grounded' },
    { title: 'Curate', detail: 'dedup/merge/rank to a distinct shortlist' },
    { title: 'Verify', detail: 'adversarial saturation/credit/data kill per idea' },
    { title: 'Synthesize', detail: 'ranked discovery menu with first gates + honest P(discovery)' },
  ],
}

// ------------------------------------------------------------------
const USER_PROFILE = [
  'WHO: a solo hobbyist (AI-assisted/agentic, ~2 months in), skepticism-first, NO telescope.',
  'Strong existing infrastructure: bulk archival mining (Gaia/TESS/ZTF/ATLAS/DASCH/DESI pipelines),',
  'an 11.3M-row known-object novelty front-filter, masked-periodogram + permutation-FAP discipline,',
  'ATLAS artifact-detection tools, a documented journal/ledger system, and lots of compute patience.',
  'GOAL: a genuine DISCOVERY (or discovery credit) — a new object, a new phenomenon instance, or a',
  'genuinely novel characterization. CV-grade novelties count; the user wants SOMETHING real to find.',
  'TIME: weekends/evenings, ~3-month horizon before Gaia DR4 (2 Dec 2026) takes over.',
  '',
  'TWO ACCEPTABLE CONSTRAINT MODES (label every idea with one):',
  '  (a) STRICT: public archive both finds AND confirms (the old filter).',
  '  (b) COMMUNITY-CONFIRM: archive finds; confirmation/credit flows through an established community',
  '      mechanism that demonstrably works for amateurs in 2025-26 — TNS reports, AAVSO/VSX submissions,',
  '      CBAT, Zooniverse co-authorship pipelines (e.g. Backyard Worlds), pro teams picking up posted',
  '      candidates, MPC for solar-system. The user does NOT need to own a telescope; someone else',
  '      confirming a candidate the user found still = discovery credit.',
  '',
  'META-PRINCIPLE (from the project ledger): win where the data is FRESH or UNDER-EYED + the target is',
  'RARE + the bottleneck is VETTING LABOR (which AI-assistance scales) — not telescope access or',
  'capability, where big teams always win. The 2026-07-05 scan proved the compact-object/Gaia archival',
  'frame is saturated BY SCOOP (the Rix/El-Badry group publishes each recipe within months). So new',
  'ideas must live where pros do NOT compete object-by-object: labor-limited amateur-persistent niches,',
  'genuinely under-eyed datasets, or fresh data windows.',
].join('\n')

// ------------------------------------------------------------------
phase('Ledger')
const ledger = await agent(
  'Produce a compact briefing for an ideation panel. Read these files (Read tool):\n'
  + '  1. ~/.claude/projects/-Users-USER-claude-projects/memory/future_data_mining_ideas.md\n'
  + '     (the discovery-avenue memory: outcomes of every explored lane + the 2026-07-05 exhaustion scan)\n'
  + '  2. ~/claude_projects/gaia-recovered-2026-05-27/docs/reports/discovery_menu_2026_07_03.md\n'
  + '     (the refereed 8-item GO-IF discovery menu + NO-GO kill list)\n'
  + '  3. ~/claude_projects/gaia-recovered-2026-05-27/docs/RESEARCH_LOG.md — read the entries from\n'
  + '     2026-06-01 onward (skim earlier); extract lane outcomes + reusable-tooling notes.\n\n'
  + 'Return FOUR sections, tight and complete:\n'
  + 'A. CLOSED LANES — every lane/idea already tried or killed, one line each: "<lane> — <why dead>".\n'
  + '   Include the 2026-07-05 scan kills (XP-at-scale scooped+target-blind; sub-NSS BH telescope-gated;\n'
  + '   ETV dark-tertiary scooped; falsification-audit seat taken; DESI object hunt scooped; HVS saturated).\n'
  + 'B. UNFIRED GO-IF ITEMS — menu items whose 0.5-2 day gates were NEVER run (ranks 4-8: Mira period\n'
  + '   drift, EB dP/dt, TTP sweep, plate eruption archaeology, ephemeris erratum — plus wishlist items\n'
  + '   never explored, e.g. disk-eclipsing epsilon-Aur analogs #4, stellar streams #6). For each: the\n'
  + '   claimed quarry, the gate, and the menu\'s honest yield estimate.\n'
  + 'C. TOOLKIT ASSETS — reusable data + code in hand (DESI 18,946 SB1 catalog; ~4,400 cached TESS EB\n'
  + '   light curves; 11.3M known-object store; ATLAS artifact trio; DASCH daschlab tooling; XP bulk-CDN\n'
  + '   path; hunt console; masked-LS/perm-FAP discipline; DR4 harnesses).\n'
  + 'D. LESSONS — the FP/artifact lessons any new lane must respect.\n'
  + 'Your ENTIRE returned text is pasted verbatim into downstream prompts. No preamble.',
  { label: 'extract-frame-briefing', phase: 'Ledger', model: 'sonnet', effort: 'low' }
)

// ------------------------------------------------------------------
phase('Ideate')

const IDEA_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    ideas: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          title: { type: 'string' },
          lens: { type: 'string' },
          quarry: { type: 'string', description: 'what would actually be discovered' },
          recipe: { type: 'string', description: 'concrete: what data, what selection, what the discovery looks like, who/what confirms it' },
          data_source: { type: 'string', description: 'specific public dataset(s), public as of 2026-07-07?' },
          constraint_mode: { type: 'string', enum: ['strict', 'community-confirm'] },
          amateur_precedent: { type: 'string', description: 'NAMED example of a solo/amateur/citizen discovery in this niche in 2023-2026, or "none known"' },
          toolkit_fit: { type: 'string', description: 'which existing assets it reuses' },
          why_not_scooped: { type: 'string', description: 'why pros are NOT competing object-by-object here' },
          p_discovery_guess: { type: 'string', description: 'order-of-magnitude honest guess: P(at least one real credited discovery) in ~3 months of weekend effort' },
          first_gate: { type: 'string', description: 'the 0.5-2 day cheapest test that kills or confirms the lane' },
        },
        required: ['title', 'lens', 'quarry', 'recipe', 'data_source', 'constraint_mode', 'amateur_precedent', 'first_gate'],
      },
    },
  },
  required: ['ideas'],
}

const IDEATOR_BASE =
  USER_PROFILE + '\n\n'
  + 'You are ONE lens in an ideation panel researching PIVOTS AND LONG SHOTS that could lead to a real\n'
  + 'discovery. The compact-object/Gaia archival frame is CLOSED (see briefing) — do NOT re-propose\n'
  + 'anything in section A. You are explicitly allowed to leave the old frame: different object classes,\n'
  + 'different wavelengths, different sciences, the community-confirm mode. Use WebSearch/WebFetch\n'
  + 'aggressively — your training is stale and amateur-niche saturation changes monthly; today is\n'
  + '2026-07-07. Verify that named datasets are public NOW and that the amateur precedent is REAL\n'
  + '(name the person/object/paper). 2-5 strong ideas beat 12 vague ones; an empty list is a valid\n'
  + 'answer if your lens is truly barren. Every idea needs a cheap first gate.\n\n'

const LENSES = [
  { key: 'amateur-persistent', prompt:
      'LENS 1 — WHERE AMATEURS STILL GET DISCOVERY CREDIT (2024-2026). Web-research where solo/citizen\n'
      + 'hunters demonstrably still make credited discoveries TODAY: SOHO/STEREO comet hunting; Backyard\n'
      + 'Worlds-style brown-dwarf/nearby-mover discovery in unWISE; Planet Hunters TESS / citizen exoplanet\n'
      + 'vetting (long-period single-transit planets); AAVSO/VSX novel-variable submissions; nova/dwarf-nova\n'
      + 'discovery; occultation timing; Kilonova Seekers / transient vetting; supernova hunting (is it fully\n'
      + 'survey-saturated now?). For each live niche: what makes it LABOR-limited (so AI-assistance is an\n'
      + 'edge), the actual credit mechanism, and a named 2024-26 amateur precedent. Prioritize niches where\n'
      + 'the user\'s data-mining infra transfers (time-series, cross-matching, artifact discipline).' },
  { key: 'under-eyed-archives', prompt:
      'LENS 2 — UNDER-EYED PUBLIC ARCHIVES. Datasets that are public but have FEW EYES per terabyte,\n'
      + 'where a systematic solo miner could find something real: Breakthrough Listen open data (radio\n'
      + 'technosignature + incidental astrophysics); VLASS/LOFAR/MeerKAT/ASKAP public radio images+catalogs\n'
      + '(transients, circular radio objects — ORCs were found in ASKAP!); Euclid public data (Q1 released\n'
      + '2025 — strong lenses found by citizen+ML); JWST MAST public archive (serendipitous objects in\n'
      + 'imaging); Chandra/XMM source catalogs oddballs; IceCube/Fermi public event lists; Kepler/K2/TESS\n'
      + 'full-frame images for non-planet phenomena; DASCH century plates (we have tooling!); Pan-STARRS/\n'
      + 'DECaLS imaging for lensed quasars / odd morphologies. For each: is the low-hanging fruit really\n'
      + 'still there in mid-2026, what specifically would the user hunt, and the confirm/credit route.' },
  { key: 'time-domain-oddities', prompt:
      'LENS 3 — TIME-DOMAIN ODDITIES BEYOND COMPACT BINARIES. The user owns strong light-curve tooling +\n'
      + 'FAP discipline + caches (4,400 TESS EBs; ZTF/ATLAS/ASAS-SN/DASCH access). Hunt classes where new\n'
      + 'instances = publishable discoveries: Boyajian-star-like dippers around hot stars; disintegrating/\n'
      + 'evaporating planets (K2-22 analogs); exocomet transit systems (beta Pic analogs in TESS); WD\n'
      + 'transit/pollution systems (WD 1145 analogs — is ZTF WD monitoring saturated?); red-nova PROGENITOR\n'
      + 'prediction (V1309 Sco signature: contact binary with exponentially shrinking period in OGLE/ZTF/\n'
      + 'ASAS-SN — who is doing this systematically in 2026? KIC 9832227 history); vanishing/appearing\n'
      + 'sources (VASCO-style); epsilon-Aurigae-like disk eclipsers (unexplored wishlist item!); very-long-\n'
      + 'period eclipse recoveries. Check saturation per class on the web; name precedents; be honest about\n'
      + 'which are pro-saturated vs labor-limited.' },
  { key: 'solar-system-nearfield', prompt:
      'LENS 4 — SOLAR SYSTEM + NEAR FIELD. Amateur discovery is structurally ALIVE here: SOHO/STEREO\n'
      + 'sungrazer comets (credited to individuals, ongoing); asteroid PREcovery in archival images (MPC\n'
      + 'credit mechanics); new NEO/comet candidate vetting queues; interstellar-object tail-chasing in\n'
      + 'archival ZTF/ATLAS (3I/ATLAS was found July 2025 — is there precovery/archival-characterization\n'
      + 'space left?); trans-Neptunian slow movers in DECaLS/unWISE stacks; Planet-9-adjacent searches\n'
      + '(what remains pre-Rubin?); nearby brown dwarfs / high-PM movers Backyard Worlds missed (the\n'
      + 'user has real cross-match + artifact chops); occultation-derived asteroid shapes/satellites from\n'
      + 'public networks. Which of these are genuinely open to a data-miner WITHOUT a telescope, with what\n'
      + 'credit mechanism, and what would the first gate be? Web-verify the current state (Rubin/LSST may\n'
      + 'have started eating some of these in 2025-26 — check!).' },
  { key: 'repoint-toolkit', prompt:
      'LENS 5 — REPOINT THE EXISTING TOOLKIT AT A NEW QUARRY. Assets in hand (briefing section C): the\n'
      + '18,946-object DESI RV-variable SB1 catalog (novel, uncatalogued, characterized); ~4,400 cached\n'
      + 'TESS EB light curves already artifact-vetted; the 11.3M known-object store; the M2c eclipse-\n'
      + 'depth-variation detector; DASCH tooling; XP bulk-CDN infra. What NON-compact-object discovery\n'
      + 'could each make with modest incremental work? Examples to evaluate (kill freely): circumbinary-\n'
      + 'planet or tertiary-star transits in the cached EBs (transiting CBPs are RARE and prized — check\n'
      + 'whether anyone has swept TESS EBs systematically by 2026); eclipse-timing planets around the\n'
      + 'EBs; the DESI SB1 catalog as a VALUE-ADD public release (catalog paper = a real artifact —\n'
      + 'evaluate honestly against the push policy and RNAAS norms); XP infra pointed at a NARROW\n'
      + 'under-served spectral niche the ledger says is open. Web-check prior art per idea.' },
  { key: 'unfired-menu-items', prompt:
      'LENS 6 — RE-EVALUATE THE UNFIRED GO-IF MENU ITEMS (briefing section B). The 2026-07-03 refereed\n'
      + 'menu left ranks 4-8 with gates never fired: Mira period drift (stellar-evolution-in-action),\n'
      + 'EB orbital-decay dP/dt, transit-timing-variation sweep, DASCH plate eruption archaeology,\n'
      + 'ephemeris erratum hunt — plus never-explored wishlist items (epsilon-Aur disk eclipsers #4,\n'
      + 'stellar streams #6). For each: re-check 2025-26 prior art on the web (has someone published this\n'
      + 'exact sweep since the menu was written?), restate the honest yield, and specify the gate. Then\n'
      + 'RANK them against each other. These are known-quantity long shots — your job is to decide which\n'
      + '(if any) deserve their gate fired NOW vs being killed by fresh scoops.' },
  { key: 'devils-advocate', prompt:
      'LENS 7 — SENIOR DEVIL\'S ADVOCATE. You are a time-domain astronomy veteran who has watched a\n'
      + 'hundred amateurs burn out. Given the briefing and this user\'s real profile (2 months in, AI\n'
      + 'leverage, no telescope, wants a DISCOVERY, 3-month window), answer: (1) What is the single\n'
      + 'highest-P(credited-discovery) move — even if unglamorous? (2) What plausible-sounding pivots\n'
      + 'should they absolutely NOT waste weekends on, and why? (3) Is there a structural blind spot —\n'
      + 'a place where their specific AI-assisted-vetting edge is worth 10x an ordinary amateur\'s\n'
      + 'effort? Propose at most 3 concrete moves, each with a first gate. Web-ground your claims about\n'
      + 'what amateurs actually achieved in 2025-26.' },
]

const rawIdeas = await parallel(
  LENSES.map(l => () => agent(
    IDEATOR_BASE + l.prompt + '\n\n===== FRAME BRIEFING (closed lanes / unfired items / toolkit / lessons) =====\n' + ledger,
    { label: 'ideate:' + l.key, phase: 'Ideate', schema: IDEA_SCHEMA, model: 'opus', effort: 'high' }
  ))
)
const allIdeas = rawIdeas.filter(Boolean).flatMap(r => r.ideas || [])
log('Ideation: ' + allIdeas.length + ' raw ideas from ' + LENSES.length + ' lenses')

// ------------------------------------------------------------------
phase('Curate')

const CURATE_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    shortlist: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          title: { type: 'string' },
          quarry: { type: 'string' },
          recipe: { type: 'string' },
          data_source: { type: 'string' },
          constraint_mode: { type: 'string' },
          amateur_precedent: { type: 'string' },
          toolkit_fit: { type: 'string' },
          first_gate: { type: 'string' },
          merged_from: { type: 'string' },
        },
        required: ['title', 'quarry', 'recipe', 'data_source', 'constraint_mode', 'first_gate'],
      },
    },
    dropped_note: { type: 'string' },
  },
  required: ['shortlist'],
}

const curated = await agent(
  USER_PROFILE + '\n\n'
  + 'You are the CURATOR. Merge/dedup the raw panel ideas below into a distinct shortlist of the most\n'
  + 'promising pivots, ranked best-first. Drop anything that is in the closed-lane list, has no real\n'
  + 'amateur-credit path, or whose first gate costs more than ~2 days. Keep the list honest — 6-12 max.\n'
  + 'Prefer diversity of quarry (do not let one theme eat the list).\n\n'
  + '===== RAW IDEAS =====\n' + JSON.stringify(allIdeas, null, 1) + '\n\n'
  + '===== FRAME BRIEFING =====\n' + ledger,
  { label: 'curate-shortlist', phase: 'Curate', schema: CURATE_SCHEMA, model: 'opus', effort: 'high' }
)
const shortlist = curated.shortlist || []
log('Curated to ' + shortlist.length + ' distinct pivots')

// ------------------------------------------------------------------
phase('Verify')

const VERDICT_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    title: { type: 'string' },
    survives: { type: 'boolean' },
    saturation: { type: 'string', description: 'is the niche pro-saturated or amateur-open as of mid-2026 (cite web evidence)' },
    precedent_real: { type: 'boolean', description: 'did the named amateur precedent check out on the web' },
    data_actually_public: { type: 'boolean' },
    credit_mechanism_real: { type: 'boolean', description: 'does the confirm/credit route demonstrably work for amateurs' },
    p_discovery_3mo: { type: 'string', description: 'calibrated order-of-magnitude P(>=1 credited discovery) in 3 months weekend effort: e.g. <1%, ~5%, ~20%, >50%' },
    effort_shape: { type: 'string', description: 'what the work actually looks like week-to-week' },
    verdict_reason: { type: 'string' },
    recommended_action: { type: 'string', enum: ['fire-gate-now', 'fire-gate-if-top3', 'park', 'kill'] },
  },
  required: ['title', 'survives', 'verdict_reason', 'recommended_action', 'p_discovery_3mo'],
}

const verdicts = await parallel(
  shortlist.map((idea, i) => () => agent(
    USER_PROFILE + '\n\n'
    + 'You are an ADVERSARIAL VERIFIER. Try to KILL this pivot idea; it survives only on evidence.\n'
    + 'Checks (all web-grounded — today is 2026-07-07):\n'
    + '  1. SATURATION: is this niche actually amateur-open in mid-2026, or did surveys/pro pipelines\n'
    + '     (Rubin/LSST first data!, ZTF-II, Gaia alerts, ATLAS) eat it? Search for 2025-26 activity.\n'
    + '  2. PRECEDENT: verify the named amateur/citizen discovery actually happened as claimed.\n'
    + '  3. DATA: is the named dataset public and practically downloadable at hobby scale?\n'
    + '  4. CREDIT: does the confirm/credit mechanism really deliver amateur credit (find named cases)?\n'
    + '  5. LEDGER: is this secretly a rename of a closed lane in the briefing?\n'
    + '  6. CALIBRATION: estimate P(>=1 credited discovery in ~3 months of weekend effort) honestly,\n'
    + '     given the user\'s AI-assisted vetting edge. State the dominant failure mode.\n'
    + 'Kill freely. A pivot that merely produces "another null campaign" is a KILL — the user wants\n'
    + 'a real chance at a find.\n\n'
    + '===== IDEA ' + (i + 1) + ' =====\n' + JSON.stringify(idea, null, 1) + '\n\n'
    + '===== FRAME BRIEFING (closed lanes) =====\n' + ledger,
    { label: 'verify:' + (idea.title || ('idea' + i)).slice(0, 42), phase: 'Verify', schema: VERDICT_SCHEMA, model: 'opus', effort: 'high' }
  ))
)
const scored = shortlist.map((idea, i) => ({ idea, verdict: verdicts[i] })).filter(x => x.verdict)
const survivors = scored.filter(x => x.verdict.survives)
log('Verification: ' + survivors.length + ' of ' + scored.length + ' pivots survived')

// ------------------------------------------------------------------
phase('Synthesize')

const SYNTH_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    bottom_line: { type: 'string' },
    ranked_menu: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          rank: { type: 'integer' },
          title: { type: 'string' },
          quarry: { type: 'string' },
          one_line: { type: 'string' },
          constraint_mode: { type: 'string' },
          p_discovery_3mo: { type: 'string' },
          first_gate: { type: 'string', description: 'the concrete 0.5-2 day gate to fire, specific enough to execute' },
          toolkit_fit: { type: 'string' },
          why_it_survived: { type: 'string' },
        },
        required: ['rank', 'title', 'quarry', 'one_line', 'p_discovery_3mo', 'first_gate'],
      },
    },
    notable_kills: { type: 'string' },
    recommended_first_move: { type: 'string', description: 'the single thing to do first, and why it beats the others' },
    honest_calibration: { type: 'string', description: 'combined realistic expectation across the whole menu for 3 months' },
  },
  required: ['bottom_line', 'ranked_menu', 'recommended_first_move', 'honest_calibration'],
}

const synthesis = await agent(
  USER_PROFILE + '\n\n'
  + 'You are the SYNTHESIZER. Build the final ranked pivot menu from the verified verdicts below.\n'
  + 'Rank by P(credited discovery) x fit-to-toolkit / effort. Include survivors only (survives=true),\n'
  + 'but mention the most instructive kills. Give each survivor a concrete, executable first gate.\n'
  + 'End with: the single recommended first move, and an honest combined calibration (what 3 months of\n'
  + 'weekends across the top picks realistically yields — do not inflate; the user prizes honesty).\n'
  + 'Note explicitly which picks use the relaxed community-confirm mode (a policy change the user\n'
  + 'should consciously accept) vs strict archive-only.\n\n'
  + '===== VERIFIED VERDICTS =====\n' + JSON.stringify(scored.map(x => ({ idea: x.idea, verdict: x.verdict })), null, 1),
  { label: 'synthesize-menu', phase: 'Synthesize', schema: SYNTH_SCHEMA, model: 'opus', effort: 'xhigh' }
)

return {
  raw_ideas: allIdeas.length,
  shortlisted: shortlist.length,
  survivors: survivors.length,
  synthesis,
  survivor_details: survivors.map(x => ({ idea: x.idea, verdict: x.verdict })),
}
