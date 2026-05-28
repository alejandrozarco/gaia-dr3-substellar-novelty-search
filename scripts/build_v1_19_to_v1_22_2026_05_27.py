"""Build novelty_candidates_v1.19.csv through v1.22.csv from v1.18 + hunt CSVs.

v1.18 (32) + top 5 BH + top 5 NS from defensible hunt = v1.19 (42 rows)
v1.19 - 4 K-giant/K1-fail false positives                = v1.20 (38 rows)
v1.20 + 3 triage-vetted leads (TYC 1363, Gaia 678470, Gaia 594287) = v1.21 (41)
v1.21 + 4 wider-hunt leads (2801267, 245948 A-dwarf, 3586834, 5889532) = v1.22 (45)

Identified false positives removed in v1.20:
  HD 18220, 48 Psc (K-giant SB1 chromatic bias)
  HD 147132, TYC 436-126-1 (K_1 reality check fail)

Note: v1.23 (post-Filter #31 deep dive) would remove A-dwarf + several
others; we keep v1.22 as the documented state, with FINAL_VERDICT showing
the post-deep-dive interpretation.
"""
from __future__ import annotations
import sys
from pathlib import Path
import polars as pl

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')

# Source-id -> (V, name) of additions per version, with notes
# (Reconstructed from chat transcripts)
M_JUP_PER_MSUN = 1047.348


def make_bh_ns_row(template_schema, sid, V, name, P, M2_msun, ruwe, notes, cls,
                    category='companions_hunt_2026_05_18'):
    row = {c: None for c in template_schema.columns}
    row['name'] = name
    row['gaia_dr3_source_id'] = sid
    row['vmag'] = V
    row['nss_pool'] = 'nss_orbital'
    row['p_orb_d'] = str(round(P, 1))
    row['m2_mj_marginalized_median'] = int(round(M2_msun * M_JUP_PER_MSUN))
    row['category'] = category
    row['penoyre_ruwe_value'] = ruwe
    row['p_substellar_marginalized'] = 0.0
    row['filters_passed'] = 'N/A_hunt_class'
    row['status_tentative_only'] = f'TENTATIVE_HUNT_2026_05_18'
    row['notes'] = notes
    row['fp_risk_tier'] = 'high' if ruwe and ruwe > 5 else 'medium'
    row['companion_class'] = cls
    return row


def main():
    v118 = pl.read_csv(ROOT / 'novelty_candidates_v1.18.csv', infer_schema_length=10000)
    print(f'v1.18: {len(v118)}')

    # ---- v1.19: + 5 BH + 5 NS from defensible hunt ----
    V119_BH = [
        (6696544512063546624, 10.27, 'Gaia DR3 6696544512063546624', 666.0, 3.28, 9.02,
         'CD-34 14408 SB*; sig=123; M2_astrom=3.28'),
        (6811355413155399040,  8.72, 'Gaia DR3 6811355413155399040', 951.9, 7.57, 9.85,
         'HD 207141 F-subgiant; sig=95; K_obs=31.5 (Filter#31 PASS)'),
        (4433039709908858496,  8.74, 'Gaia DR3 4433039709908858496', 312.4, 3.28, 5.52,
         'HD 147132 SB* G6IV/V; K_obs=11.2 << K_pred — FALSE POSITIVE'),
        (4277855016732107520, 11.25, 'Gaia DR3 4277855016732107520', 424.4, 13.66, 9.31,
         'TYC 436-126-1; K_obs=4.94 << K_pred=66.7 — FALSE POSITIVE'),
        (6471824298353396736, 10.81, 'Gaia DR3 6471824298353396736', 490.8, 3.63, 5.70,
         'TYC 8785-1657-1 SB*; K_obs=28.6 = K_pred(60deg)=29.1 — CONSISTENT'),
    ]
    V119_NS = [
        (5824775105747810688, 12.89, 'Gaia DR3 5824775105747810688', 624.8, 1.29, 4.90,
         'sig=120; AstroSpectroSB1; UCAC4 source'),
        (1921518825784578176,  7.83, 'Gaia DR3 1921518825784578176', 706.7, 2.35, 2.43,
         'HD 224381 G5 SB*; sig=117'),
        (5065286383666887680,  7.43, 'Gaia DR3 5065286383666887680', 209.6, 1.65, 4.49,
         'HD 18220 K2III SB* — K-GIANT FALSE POSITIVE'),
        (4850049251588903936, 11.48, 'Gaia DR3 4850049251588903936', 469.7, 1.86, 4.72,
         'TYC 7572-1359-1; sig=111'),
        (2792902058745994752,  5.41, 'Gaia DR3 2792902058745994752', 623.0, 2.24, 4.95,
         '48 Psc K5III SB* — K-GIANT FALSE POSITIVE'),
    ]

    new_rows = []
    for sid, V, name, P, M2, ruwe, notes in V119_BH:
        new_rows.append(make_bh_ns_row(v118, sid, V, name, P, M2, ruwe, notes,
                                         'dormant_BH_candidate'))
    for sid, V, name, P, M2, ruwe, notes in V119_NS:
        new_rows.append(make_bh_ns_row(v118, sid, V, name, P, M2, ruwe, notes,
                                         'dormant_NS_candidate'))
    new_df = pl.DataFrame(new_rows, schema=v118.schema)
    v119 = pl.concat([v118, new_df])
    v119.write_csv(ROOT / 'novelty_candidates_v1.19.csv')
    print(f'v1.19: {len(v119)} (= 32 + 5 BH + 5 NS)')

    # ---- v1.20: - 4 false positives ----
    REMOVE = {
        5065286383666887680,   # HD 18220 K2III SB*
        2792902058745994752,   # 48 Psc K5III SB*
        4433039709908858496,   # HD 147132 K_1 fail
        4277855016732107520,   # TYC 436-126-1 K_1 fail
    }
    # Use NULL-safe filter: drop rows whose source_id is in REMOVE; keep NULL source_ids
    v120 = v119.filter(
        pl.col('gaia_dr3_source_id').is_in(list(REMOVE)).fill_null(False).not_()
    )
    v120.write_csv(ROOT / 'novelty_candidates_v1.20.csv')
    print(f'v1.20: {len(v120)} (after K-giant + K_1 reality check pruning)')

    # ---- v1.21: + 3 triage-vetted leads ----
    V121_NEW = [
        (666596383384888320, 9.90, 'TYC 1363-2339-1', 945.7, 3.94, 5.71,
         'F-subgiant Teff=6797 logg=3.86; ZERO SIMBAD refs; K_obs=23.17=K_pred(60deg); e=0.16 circular; INAUGURAL TARGET'),
        (6784701430232308352, 11.75, 'Gaia DR3 6784701430232308352', 522.4, 3.55, 6.72,
         'F-G dwarf; K_obs=31.7~K_pred(60deg)=32.4; no SIMBAD literature'),
        (5942873714068259584, 12.96, 'Gaia DR3 5942873714068259584', 544.5, 3.98, 4.02,
         'K-dwarf; K_obs=32.1 > K_pred for M2=1.21 — M_2 UNDERestimated, promoted NS->BH'),
    ]
    new_rows = []
    for sid, V, name, P, M2, ruwe, notes in V121_NEW:
        row = make_bh_ns_row(v120, sid, V, name, P, M2, ruwe, notes, 'dormant_BH_candidate',
                              category='companions_hunt_triage_2026_05_27')
        row['filters_passed'] = 'TRIAGE_TIER1'
        row['status_tentative_only'] = 'TENTATIVE_TRIAGE_2026_05_27'
        row['fp_risk_tier'] = 'low'
        new_rows.append(row)
    new_df = pl.DataFrame(new_rows, schema=v120.schema)
    v121 = pl.concat([v120, new_df])
    v121.write_csv(ROOT / 'novelty_candidates_v1.21.csv')
    print(f'v1.21: {len(v121)} (after +3 triage-vetted leads)')

    # ---- v1.22: + 4 wider-hunt leads ----
    V122_NEW = [
        (2801267044426382336, 12.59, 'UCAC4 550-001501 / Gaia 2801267044426382336', 750.0, 6.95,
         8.04, 'F-subgiant Teff=5861 logg=3.82; sig=85; K_obs=38.3=K_pred(90deg)=39.2; e=0.06; zero SIMBAD'),
        (3586834017613414784, 12.47, 'Gaia DR3 3586834017613414784', 591.5, 8.0,
         4.93, 'F-dwarf Teff=6140 logg=4.06; sig=71; K_obs=41.4 fits i~75 with M2~8; NOT IN SIMBAD'),
        (245948793944575360, 11.80, 'A-dwarf / Gaia 245948793944575360', 548.7, 6.05,
         4.97, 'A-DWARF rare class HR 6819-style; K_obs=37.2=K_pred(90)=36.9 BUT rv_chisq_pvalue=0.999 -> FAILS Filter #31'),
        (5889532732877344128, 12.67, 'UCAC4 198-113624 / Gaia 5889532732877344128', 896.0, 13.0,
         4.85, 'F-subgiant; sig=45; K_obs=53.9>>K_pred(90)=27.8 — M_2 UNDERESTIMATED; possibly stellar BH ~13'),
    ]
    new_rows = []
    for sid, V, name, P, M2, ruwe, notes in V122_NEW:
        row = make_bh_ns_row(v121, sid, V, name, P, M2, ruwe, notes, 'dormant_BH_candidate',
                              category='wider_hunt_2026_05_27')
        row['nss_pool'] = 'nss_orbital_widerHunt'
        row['filters_passed'] = 'WIDER_HUNT_TIER1'
        row['status_tentative_only'] = 'TENTATIVE_WIDER_HUNT_2026_05_27'
        row['fp_risk_tier'] = 'low'
        new_rows.append(row)
    new_df = pl.DataFrame(new_rows, schema=v121.schema)
    v122 = pl.concat([v121, new_df])
    v122.write_csv(ROOT / 'novelty_candidates_v1.22.csv')
    print(f'v1.22: {len(v122)} (after +4 wider-hunt leads)')

    print('\n=== Final v1.22 composition ===')
    print(v122.group_by('companion_class').len().sort('len', descending=True).to_pandas().to_string(index=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
