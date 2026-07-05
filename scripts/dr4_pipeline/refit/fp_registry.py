"""Labeled false-positive registry — the project's own documented retractions.

This is the campaign's **private, source_id-keyed corpus of false positives**:
every candidate/claim the project itself RETRACTED, DOWNGRADED, or REFUTED after
independent re-verification, harvested from the dated, sourced ledgers
(`docs/RESEARCH_LOG.md`, `docs/CANDIDATES.md`, the per-object journals,
`CITATION.cff`) — NOT reconstructed from memory (per the CLAUDE.md
documented-history mandate).

Why it exists (lane #116 self-validation): when Gaia DR4 lands (2 Dec 2026) the
re-fit engine will pass judgement on the standing candidates. Before we trust a
single *new* verdict, the engine must first **reproduce the correct skeptical
verdict on every FP we already know about** — otherwise a regression could let a
known-false signature through as a fresh "discovery". `test_fp_selfvalidation.py`
turns the astrometric rows here into synthetic-DR4 assertion tests; `run.py
--self-validate` runs that gate before any day-one analysis.

Each row also records `owning_subsystem`: the vetting tool that SHOULD catch the
signature. The DR4 astrometric re-fit engine (this directory) only owns the
`dr4-refit-astrometric` rows; photometric-period / ellipsoidal artifacts, SB2 /
luminous-binary contamination, and pure catalogue-crossmatch novelty errors are
owned by other subsystems and are recorded here for completeness and honesty
(the corpus is the deliverable; the engine guards its slice of it).

Provenance strings point at the dated ledger entries; treat those as ground truth
and this file as an index into them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Controlled vocabularies (kept small on purpose; extend deliberately).
FP_CLASSES = {
    'astrometric-mass-overestimate',
    'astrometric-triple-masquerade',
    'inclination-degeneracy-overpromotion',
    'thiele-innes-cosi-bug',
    'photometric-period-artifact',
    'photometric-ellipsoidal-noise',
    'spectroscopic-sb2-stellar',
    'other',
}
OWNING_SUBSYSTEMS = {
    'dr4-refit-astrometric',   # this engine
    'cascade-photometry',
    'spectroscopy-sb2',
    'catalog-crossmatch',
}


@dataclass(frozen=True)
class FPCase:
    key: str
    source_id: Optional[str]        # 19-digit Gaia DR3 source_id (str) or None (method/lane-level)
    object_name: str
    fp_class: str
    signature: str                  # the specific signal that fooled the earlier analysis
    correct_verdict: str            # the skeptical conclusion now
    owning_subsystem: str
    provenance: str
    # Optional numeric oracle for the astrometric self-validation tests.
    oracle: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# THE CORPUS.  Harvested 2026-07-05 from the dated ledgers (agent cross-check of
# RESEARCH_LOG.md + CANDIDATES.md + docs/object_journals/*.md + CITATION.cff).
# HD 76078 is deliberately EXCLUDED: it is a v1-era removed-from-headline SB2
# *benchmark fixture* (tests/data/test_pool.csv, benchmarks.json), not a
# dated-ledger retraction of this campaign — see the harvest NOTES.
# ---------------------------------------------------------------------------
REGISTRY = [
    # ---- method / lane-level corrections (astrometric mass chain) -----------
    FPCase(
        key='thiele-innes-cosi-sqrt-bug', source_id=None,
        object_name='(method-level: Thiele-Innes cos i helper)',
        fp_class='thiele-innes-cosi-bug',
        signature='A stray sqrt around the Campbell relation cos i = |AG-BF|/a^2 biased '
                  'inclination toward face-on, inflating the sin-i-deprojected companion '
                  'mass M2. Fixed at 6 sites / 3 scripts (2026-05-31).',
        correct_verdict='corrected — cos i = |AG-BF|/a^2 (no sqrt); pre-fix M2 outputs stale/biased-high',
        owning_subsystem='dr4-refit-astrometric',
        provenance='RESEARCH_LOG 2026-05-31; project_gaia_incl_helper_bugfix; CITATION.cff v2.2',
        oracle=dict(guard='cosi_no_sqrt', incl_probe_deg=66.4, m2_sin_i_min=1.20),
    ),
    FPCase(
        key='massgap-bh-sin-i-inflation-class', source_id=None,
        object_name='(method-level: rv_amplitude_robust/2 -> sin i)',
        fp_class='astrometric-mass-overestimate',
        signature='Reading rv_amplitude_robust as 2*K1 and back-solving sin i (<1) inflated '
                  'dark-companion masses into the mass-gap-BH range across the pool '
                  '("invented fake mass-gap BHs"). The photocentric mass function is direct.',
        correct_verdict='corrected — M2 for a dark companion comes from f(M) directly; no sin-i inflation',
        owning_subsystem='dr4-refit-astrometric',
        provenance='RESEARCH_LOG 2026-05-28; CANDIDATES.md insight catalog; CITATION.cff',
        oracle=dict(guard='direct_mass_function'),
    ),

    # ---- astrometric object-level: mass overestimate / triple / inclination -
    FPCase(
        key='5858574-massgap-bh-to-triple', source_id='5858574810404752256',
        object_name='Gaia DR3 5858574810404752256',
        fp_class='astrometric-triple-masquerade',
        signature='"M2~=2.82 mass-gap BH" used rv_amplitude_robust/2 to invent sin i~=0.53; '
                  'the direct photocentric f(M) gives M2~=1.48-1.63 (NS-mass, no BH). Shahaf/AMRF '
                  'P(compact)~=0.21-0.355 sits on the triple/ambiguous boundary. (Orbital NSS -> '
                  'the cos-i sqrt bug never applied here; the error was the rv/2 sin-i inflation.)',
        correct_verdict='triple-not-compact (watch-list; NS-mass, not BH) — "mass-gap BH 2.82" FALSIFIED',
        owning_subsystem='dr4-refit-astrometric',
        provenance='RESEARCH_LOG 2026-05-29 & 2026-06-03; docs/object_journals/5858574810404752256.md',
        oracle=dict(guard='triple_masquerade', M2_max_msun=1.7, note='boundary-fragile P(compact)=0.355'),
    ),
    FPCase(
        key='wdj020915-superchandra-framing', source_id='332248057157474176',
        object_name='WDJ020915.51+380425.92',
        fp_class='astrometric-mass-overestimate',
        signature='Framed as a "super-Chandra Type-Ia progenitor" under sin i=1. Full-TI-covariance '
                  'MC: M2=1.32 [1.27-1.38], P(M2>1.4)=8.6%; P=275 d -> non-merging. Weak Keplerian '
                  'fit (F2=+8.39, RUWE=8.79) -> mass provisional / DR4-gated.',
        correct_verdict='DOWNGRADE — not super-Chandra, not a Ia progenitor; novel long-P DD/WD+NS (M_tot>M_Ch)',
        owning_subsystem='dr4-refit-astrometric',
        provenance='RESEARCH_LOG 2026-05-31 & 2026-06-10; docs/object_journals/332248057157474176.md',
        oracle=dict(guard='prereg_downgrade_or_park', in_prereg=True,
                    weak_fit_verdict='PARK', low_mass_verdict='DOWNGRADE'),
    ),
    FPCase(
        key='wdj060042-superchandra-framing', source_id='2909342818326298112',
        object_name='WDJ060042.75-293041.36',
        fp_class='astrometric-mass-overestimate',
        signature='Same "super-Chandra Type-Ia progenitor" over-framing under sin i=1. Full-TI-cov MC: '
                  'M2=1.37 [1.23-1.52], P(M2>1.4)=41% (not confidently >1.4); P=935 d -> non-merging. '
                  'Orbit itself is clean (F2=+0.79) -> the correction is to the framing/mass claim.',
        correct_verdict='DOWNGRADE — not super-Chandra, not a Ia progenitor; novel long-P DD/WD+NS',
        owning_subsystem='dr4-refit-astrometric',
        provenance='RESEARCH_LOG 2026-05-31 & 2026-06-10; docs/object_journals/2909342818326298112.md',
        oracle=dict(guard='prereg_no_false_superchandra', in_prereg=True,
                    anchor_m2_below_msun=1.40, low_mass_verdict='DOWNGRADE'),
    ),
    FPCase(
        key='galex-j033455-bh-to-wd', source_id='3263804373319076480',
        object_name='GALEX J033455+000910',
        fp_class='astrometric-mass-overestimate',
        signature='Reached Tier-1 BH (cascade M2=3.22) on an NSS photocentric mass with NO RUWE gate '
                  '(RUWE=9.35); independent multi-epoch RV (MIKE+FEROS+APOGEE+LAMOST) shows a white '
                  'dwarf, M2<=0.9.',
        correct_verdict='DEMOTED — WD, not a BH (Simon, Lam, El-Badry, Reggiani 2026, arXiv:2603.20371)',
        owning_subsystem='dr4-refit-astrometric',
        provenance='CANDIDATES.md Tier-1 BH pool + no-RUWE-gate note; RESEARCH_LOG 2026-07-05 (scoop)',
        oracle=dict(guard='ruwe_gate', ruwe=9.35, note='no per-object journal; verdict in CANDIDATES.md'),
    ),
    FPCase(
        key='5406907-bh-orbit-spurious', source_id='5406907085973524224',
        object_name='Gaia DR3 5406907085973524224',
        fp_class='astrometric-mass-overestimate',
        signature='"STRONG BH, M2~=4.5" from a single DPAC-rejected OrbitalAlternative solution '
                  '(max|corr|=0.98, TI<->plx/PM degeneracy). rv_amplitude_robust is NULL and '
                  'RV=2.34+/-4.12 over 27 transits shows no variability where P=25 d / M2~=4 predicts '
                  'K1~=100 km/s -> the orbit itself may be spurious.',
        correct_verdict='DOWNGRADE — WEAK/SUSPECT; orbit may be spurious (RV-silent)',
        owning_subsystem='dr4-refit-astrometric',
        provenance='CANDIDATES.md 5406907 DOWNGRADED 2026-05-29; docs/object_journals/5406907085973524224.md',
        oracle=dict(guard='rv_silence_cross_check', P_days=25.0, K1_pred_kms=100.0),
    ),
    FPCase(
        key='hd207141-massgap-bh-to-triple', source_id='6811355413155399040',
        object_name='HD 207141',
        fp_class='astrometric-mass-overestimate',
        signature='Former heaviest-BH candidate (stored M2=7.57). NSS-parallax correction drops '
                  'M2->1.31; M1-correction gives 1.75; Shahaf P(III) very small (read as triple). '
                  '(Open 1.31-vs-1.75 M2 reconciliation.)',
        correct_verdict='DEMOTE — triple-favored, not a BH',
        owning_subsystem='dr4-refit-astrometric',
        provenance='docs/object_journals/6811355413155399040.md (2026-06-10); CANDIDATES.md Demoted',
        oracle=dict(guard='parallax_correction', M2_stored=7.57, M2_corrected_msun=1.31),
    ),
    FPCase(
        key='hd75567-ns-to-triple', source_id='5640825637852070016',
        object_name='HD 75567',
        fp_class='astrometric-triple-masquerade',
        signature='High-sig (295) Tier-1 NS, M2=1.35 dark. Shahaf P(III|A,M1)=0.85 over 322 neighbours '
                  '+ spectroscopic/astrometric a-ratio=1.23 (>1 -> a luminous inner pair pulls the '
                  'photocentre back) -> triple-favored, P(compact)=0.15.',
        correct_verdict='triple-not-compact (downgraded)',
        owning_subsystem='dr4-refit-astrometric',
        provenance='CANDIDATES.md Tier-1 NS pool triage (2026-05-29)',
        oracle=dict(guard='triple_masquerade', a_ratio=1.23),
    ),
    FPCase(
        key='tyc4562-ns-to-triple', source_id='1714530637958169600',
        object_name='TYC 4562-535-1',
        fp_class='inclination-degeneracy-overpromotion',
        signature='High-sig (208) Tier-1 NS, M2=1.26 dark. 448 Shahaf neighbours; a-ratio=1.31; near '
                  'face-on (i~=22 deg) inflates M2. Triple-favored, P(compact)=0.13.',
        correct_verdict='triple-not-compact (downgraded)',
        owning_subsystem='dr4-refit-astrometric',
        provenance='CANDIDATES.md Tier-1 NS pool triage (2026-05-29)',
        oracle=dict(guard='inclination_overpromotion', incl_deg=22.0),
    ),
    FPCase(
        key='2127900-ns-to-triple', source_id='2127900555635640832',
        object_name='Gaia DR3 2127900555635640832',
        fp_class='astrometric-triple-masquerade',
        signature='Tier-1 NS; external RV confirms the OUTER orbit but Shahaf AMRF favors a triple '
                  '~4:1 (P(compact)=0.21); M2=1.45 at the WD/NS edge.',
        correct_verdict='triple-favored (candidate at best)',
        owning_subsystem='dr4-refit-astrometric',
        provenance='CANDIDATES.md Tier-1 NS pool triage',
        oracle=dict(guard='triple_masquerade', p_compact=0.21),
    ),
    FPCase(
        key='wdj205650-superchandra-massjoin-artifact', source_id='1736555475066523008',
        object_name='WDJ205650.56+062149.68',
        fp_class='astrometric-mass-overestimate',
        signature='Stored M_total=2.06 "super-Chandra" was an artifact — the GF21 WD mass was never '
                  'joined into the M1-correction, leaving default M1=1.5; self-consistent inversion '
                  'gives M2=0.26, M_total=0.64. Also headlined as novel but already in Munday+2024 (81-d P).',
        correct_verdict='DOWNGRADE-to-subChandra-DWD + NOVELTY WITHDRAWN (Munday+2024)',
        owning_subsystem='catalog-crossmatch',
        provenance='docs/object_journals/1736555475066523008.md (2026-05-30); CANDIDATES.md Pile E',
        oracle=dict(guard='mass_join_regression', M1_default_buggy=1.5, M1_real_msun=0.38,
                    M_total_artifact=2.06, M_total_correct=0.64),
    ),

    # ---- photometric FPs (owned by the cascade / light-curve vetting) -------
    FPCase(
        key='crts-j051419-cv-period-eclipse', source_id='3233913634323725696',
        object_name='CRTS J051419.8+011120',
        fp_class='photometric-period-artifact',
        signature='The 180.77-min period + "71% eclipse, i~=84 deg" came from folding outburst-INCLUDING '
                  'ZTF data and reading a per-cycle minimum of S/N~0.66 TESS noise; outburst-masked LS '
                  'gives FAP=1.0, only 1-sidereal-day aliases survive, BLS disagrees across bands.',
        correct_verdict='REFUTE — a known SU UMa dwarf nova + 2023 superoutburst; no period/eclipse/inclination',
        owning_subsystem='cascade-photometry',
        provenance='RESEARCH_LOG 2026-05-28; CANDIDATES.md CRTS J051419 RETRACTED; '
                   'docs/object_journals/3233913634323725696.md; CITATION.cff',
    ),
    FPCase(
        key='cv-period-avenue', source_id=None,
        object_name='CV-period pipeline (Pile F, 14 candidate periods)',
        fp_class='photometric-period-artifact',
        signature='The whole CV-period avenue folded outburst-contaminated light curves, read eclipse '
                  'depths as the per-cycle minimum of noise-dominated cadences, and applied no alias '
                  'control. 5/5 tested periods falsified (FAP=1.0 masked-LS; two had ample S/N -> genuine '
                  'false periods, not sensitivity); 9 untested presumed unreliable.',
        correct_verdict='REFUTE — ZERO verified novel periods; objects remain real dwarf novae',
        owning_subsystem='cascade-photometry',
        provenance='RESEARCH_LOG 2026-05-28; CANDIDATES.md Pile F RETRACTION banner; CITATION.cff',
    ),
    FPCase(
        key='galex-j145250-ellipsoidal', source_id='6281177228434199296',
        object_name='GALEX J145250-192225 (1eRASS J145250.2-192230)',
        fp_class='photometric-ellipsoidal-noise',
        signature='The "0.138% ellipsoidal, M2=12.75 Tier-1 BH" rested on a single 27-d TESS sector vs '
                  'P_orb=154 d, so the P/2~=77-d ellipsoidal is unmeasurable — the folded P2P at P/2 is '
                  'indistinguishable from random periods (perm-FAP=0.28). Astrometry also RUWE=6.46 '
                  '(sin i~=0.12 near face-on). Already AMRFClassIII (Halbwachs).',
        correct_verdict='REFUTE ellipsoidal detection; DISPUTED/DEMOTED BH — RUWE-compromised, not novel',
        owning_subsystem='cascade-photometry',
        provenance='CANDIDATES.md Tier-1 BH pool (ellipsoidal retracted 2026-05-28) + no-RUWE-gate; '
                   'findings_register.csv; RESEARCH_LOG 2026-06-10 (F#34, F2=+8.0)',
        oracle=dict(note='also an astrometric RUWE-compromised case; no per-object journal'),
    ),

    # ---- spectroscopic SB2 / luminous-binary contamination -----------------
    FPCase(
        key='6802634-bh-to-luminous-binary', source_id='6802634430521968000',
        object_name='Gaia DR3 6802634430521968000',
        fp_class='spectroscopic-sb2-stellar',
        signature='Flagged "dormant_BH M2~=3.0" under dark-companion + NSS-parallax + sin i=1. Gaia MSC '
                  'prefers a luminous G2V+K3V binary (logpost=589, flags=0); NSS parallax 17 sigma from '
                  'the single-source value; e=0.871 is the Sahlmann+2024 extreme-e FP class; SB2 '
                  'fingerprints (single-star pipelines NaN, RVS auto-template logg=1.0).',
        correct_verdict='DEMOTE — luminous SB2 / suspect NSS solution, NOT a BH',
        owning_subsystem='spectroscopy-sb2',
        provenance='docs/object_journals/6802634430521968000.md (2026-05-28); CANDIDATES.md Demoted',
    ),
    FPCase(
        key='6021285-massgap-bh-sb1-noise', source_id='6021285355771958528',
        object_name='TYC 7350-249-1',
        fp_class='spectroscopic-sb2-stellar',
        signature='Orphan "M2,min=3.36 SB1 dormant-BH" from f(M) on K1=41.3 km/s. Gaia RVS orbit '
                  'statistically rejected (pvalue=0, renorm_gof=41.8, template logg=5.0); astrometry '
                  'forbids a 3.4 M_sun companion (TI null, ipd=0, RUWE=6.99 unmodeled not fitted reflex); '
                  '0 independent RV phases.',
        correct_verdict='REFUTE (DEFLATED) — noisy/contaminated SB1, not a compact companion',
        owning_subsystem='spectroscopy-sb2',
        provenance='docs/object_journals/6021285355771958528.md (2026-06-03, task #108); RESEARCH_LOG 2026-06-03',
    ),
    FPCase(
        key='ns-pool-2129927-superposed-sb1', source_id='2129927539681151872',
        object_name='Gaia DR3 2129927539681151872',
        fp_class='spectroscopic-sb2-stellar',
        signature='Tier-1 NS whose archival spectroscopic f(M) is ~220x the astrometric value -> the RV '
                  'signal comes from a superposed/inner short-period binary, not the astrometric '
                  'companion (also F2=+17.2, extreme).',
        correct_verdict='REFUTE -> demoted (superposed/inner SB, not the astrometric companion)',
        owning_subsystem='spectroscopy-sb2',
        provenance='CANDIDATES.md Tier-1 NS pool triage REFUTED->demoted; RESEARCH_LOG 2026-06-10',
    ),
    FPCase(
        key='ns-pool-1379150-superposed-sb1', source_id='1379150557507688960',
        object_name='Gaia DR3 1379150557507688960',
        fp_class='spectroscopic-sb2-stellar',
        signature='Tier-1 NS with RUWE=20.2 and spectroscopic f(M) ~860x the astrometric value -> '
                  'grossly RV-inconsistent superposed/inner short-period binary, not the astrometric '
                  'companion.',
        correct_verdict='REFUTE -> demoted (superposed/inner SB, not the astrometric companion)',
        owning_subsystem='spectroscopy-sb2',
        provenance='CANDIDATES.md Tier-1 NS pool triage REFUTED->demoted',
    ),
    FPCase(
        key='3155543-confirmed-ns-to-candidate', source_id='3155543945892767232',
        object_name='Gaia DR3 3155543945892767232 (UCAC4 499-043649)',
        fp_class='spectroscopic-sb2-stellar',
        signature='Labeled "CONFIRMED NS (2-channel)" on a LAMOST chi2=0.36 fit that was a 2-point '
                  'free-omega overfit — the external corroboration is only 2 distinct phases at 2.66 '
                  'sigma. Strong Gaia NSS binary, weak external RV; NSS flags bit 13 (F#33).',
        correct_verdict='DOWNGRADE — CANDIDATE (NS-mass), not a confirmed 2-channel NS',
        owning_subsystem='spectroscopy-sb2',
        provenance='CANDIDATES.md Headline + survivor re-verification; docs/object_journals/3155543945892767232.md',
    ),
    FPCase(
        key='hd157033-bh-to-ambiguous', source_id='4111149395881722496',
        object_name='HD 157033 (HIP 84960)',
        fp_class='spectroscopic-sb2-stellar',
        signature='"STRONG BH" rested on APOGEE RVs unreliable for this hot A9/F0 fast rotator (high '
                  'Chi2RV, spurious [Fe/H]=-1.45, VSINI_BAD) and rv_amplitude_robust (~2K1) read as a '
                  'clean K1; Kervella face-value M2=0.45 (M-dwarf); RUWE=0.85 -> no astrometric orbit.',
        correct_verdict='DOWNGRADE — ambiguous 0.4-6 M_sun, NOT a confirmed BH',
        owning_subsystem='spectroscopy-sb2',
        provenance='CANDIDATES.md HD 157033 DOWNGRADED 2026-05-29; docs/object_journals/4111149395881722496.md',
    ),
    FPCase(
        key='5476986-multisurvey-rave-noise', source_id='5476986108823894400',
        object_name='Gaia DR3 5476986108823894400',
        fp_class='spectroscopic-sb2-stellar',
        signature='A "K1=163 km/s" multi-survey BH-regime signal was RAVE pipeline noise (RAVE '
                  'sigma=115 km/s = its noise floor) vs real APOGEE sigma=6.96 km/s.',
        correct_verdict='REFUTE — RAVE-noise artifact, not a real high-amplitude orbit',
        owning_subsystem='spectroscopy-sb2',
        provenance='CANDIDATES.md Demoted/falsified (5476986108823894400)',
    ),

    # ---- catalogue-crossmatch (PMa face-value mass) demotions ---------------
    FPCase(
        key='pile-a-hgca-bh-to-stellar', source_id=None,
        object_name='Pile-A HGCA "BH-class" (7 of 8: CD-46 10032A, HD 173689, HD 16385, '
                    'HD 81825, HD 37943, HD 5514, LP 155-298)',
        fp_class='astrometric-mass-overestimate',
        signature='HGCA/Kervella PMa "BH-class" companions; Kervella H2G2 face-value M2 at the 5-AU '
                  'reference is 0.4-2.9 M_sun -> ordinary stellar binaries, not BHs.',
        correct_verdict='DOWNGRADE — stellar binaries, not BHs',
        owning_subsystem='catalog-crossmatch',
        provenance='CANDIDATES.md Demoted (Pile-A); docs/object_journals/5998932765413064192.md '
                   '(CD-46 10032A), 2091887087360991744.md (HD 173689)',
    ),
]


# ---------------------------------------------------------------------------
# Accessors / validation.
# ---------------------------------------------------------------------------

def by_key(key: str) -> FPCase:
    for c in REGISTRY:
        if c.key == key:
            return c
    raise KeyError(key)


def astrometric_cases():
    """FPs this engine is responsible for guarding (owning_subsystem = dr4-refit-astrometric)."""
    return [c for c in REGISTRY if c.owning_subsystem == 'dr4-refit-astrometric']


def cases_by_subsystem(subsystem: str):
    return [c for c in REGISTRY if c.owning_subsystem == subsystem]


def validate_registry() -> list:
    """Return a list of structural problems (empty == well-formed)."""
    problems = []
    seen_keys = set()
    for c in REGISTRY:
        if c.key in seen_keys:
            problems.append(f'duplicate key: {c.key}')
        seen_keys.add(c.key)
        if c.fp_class not in FP_CLASSES:
            problems.append(f'{c.key}: bad fp_class {c.fp_class!r}')
        if c.owning_subsystem not in OWNING_SUBSYSTEMS:
            problems.append(f'{c.key}: bad owning_subsystem {c.owning_subsystem!r}')
        if c.source_id is not None:
            if not (isinstance(c.source_id, str) and c.source_id.isdigit()
                    and 15 <= len(c.source_id) <= 19):
                problems.append(f'{c.key}: source_id must be a 15-19 digit STRING, got {c.source_id!r}')
        for fld in ('object_name', 'signature', 'correct_verdict', 'provenance'):
            if not getattr(c, fld):
                problems.append(f'{c.key}: empty {fld}')
    return problems


def summary() -> str:
    from collections import Counter
    by_sub = Counter(c.owning_subsystem for c in REGISTRY)
    by_cls = Counter(c.fp_class for c in REGISTRY)
    lines = [f'Labeled-FP registry: {len(REGISTRY)} documented false positives.']
    lines.append('  by owning subsystem: ' + ', '.join(f'{k}={v}' for k, v in sorted(by_sub.items())))
    lines.append('  by fp_class:         ' + ', '.join(f'{k}={v}' for k, v in sorted(by_cls.items())))
    lines.append(f'  astrometric (this engine guards): {len(astrometric_cases())}')
    return '\n'.join(lines)


if __name__ == '__main__':
    probs = validate_registry()
    print(summary())
    if probs:
        print('\nPROBLEMS:')
        for p in probs:
            print('  - ' + p)
        raise SystemExit(1)
    print('\nregistry OK')
