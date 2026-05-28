"""Amateur-actionable transit candidate list — Kepler-solved next-transit
ephemerides for each headline substellar candidate.

For each candidate with a defined orbital ephemeris (T_peri, omega, e, P):
  - Predict next transit time
  - Transit depth (R_BD / R_*)^2
  - Geometric transit probability R_*/a
  - Instrument tier (8"/12"/16"+) from V mag + depth + duration

Output: amateur_transit_candidates.csv
"""
from __future__ import annotations
import math, sys, warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path
warnings.filterwarnings('ignore')
import polars as pl
from astroquery.gaia import Gaia

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')


def solve_kepler(M, e, tol=1e-10):
    E = M + e * math.sin(M) if e < 0.8 else math.pi
    for _ in range(60):
        dE = (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
        E -= dE
        if abs(dE) < tol: break
    return E


def next_transit_time(P_d, e, omega_rad, T_peri_jd, now_jd):
    nu_tra = math.pi/2 - omega_rad
    E_tra = 2 * math.atan(math.sqrt((1-e)/(1+e)) * math.tan(nu_tra/2))
    M_tra = E_tra - e * math.sin(E_tra)
    T_tra0 = T_peri_jd + (M_tra/(2*math.pi)) * P_d
    k = max(0, math.ceil((now_jd - T_tra0) / P_d))
    return T_tra0 + k * P_d


def amateur_tier(Vmag, depth_mmag, duration_hr):
    if Vmag is None: return 'pro-only (no V)'
    if depth_mmag is None: return 'pro-only (no depth)'
    if Vmag <= 8 and depth_mmag >= 10 and duration_hr <= 8: return '8-10" amateur'
    if Vmag <= 10 and depth_mmag >= 5 and duration_hr <= 10: return '12" amateur'
    if Vmag <= 12 and depth_mmag >= 3: return '16"+ advanced amateur'
    if Vmag <= 14 and depth_mmag >= 2: return 'pro-1m'
    return 'pro-only'


def star_radius_from_mass(M):
    if M is None or M <= 0: M = 1.0
    if M < 1.0: return M**0.8
    return M**0.57


def kepler_a_AU(P_d, M_tot):
    return (M_tot * (P_d/365.25)**2)**(1.0/3)


def main():
    nov = pl.read_csv(ROOT / 'novelty_candidates.csv')
    print(f'Headline candidates: {len(nov)}')

    # Get source IDs
    col = next((c for c in nov.columns if 'source_id' in c.lower()), None)
    if not col:
        print('No source_id column found'); return 1
    src_ids = [int(x) for x in nov[col].drop_nulls().to_list()]
    print(f'Source IDs: {len(src_ids)}')

    ids_str = ','.join(str(x) for x in src_ids)
    q = (f"SELECT nss.source_id, nss.nss_solution_type, nss.period, "
         f"nss.eccentricity, nss.arg_periastron, nss.t_periastron, "
         f"g.ra, g.dec, g.parallax, g.phot_g_mean_mag "
         f"FROM gaiadr3.nss_two_body_orbit nss "
         f"JOIN gaiadr3.gaia_source g ON g.source_id = nss.source_id "
         f"WHERE nss.source_id IN ({ids_str})")
    nss_df = Gaia.launch_job_async(q).get_results().to_pandas()
    print(f'NSS rows: {len(nss_df)}')

    # name + M2 maps
    nm_col = 'name' if 'name' in nov.columns else col
    m2_col = next((c for c in nov.columns if 'm2_mj_marginalized' in c.lower() or 'm2_mj' in c.lower()), None)
    name_map = {int(r[col]): r[nm_col] for r in nov.iter_rows(named=True) if r.get(col) is not None}
    m2_map = {int(r[col]): r[m2_col] for r in nov.iter_rows(named=True) if r.get(col) is not None and m2_col} if m2_col else {}

    R_JUP_PER_RSUN = 1.0 / 0.10049
    M_JUP_PER_MSUN = 1047.348
    now_jd = (datetime.now(timezone.utc).timestamp() / 86400.0) + 2440587.5

    rows = []
    for _, r in nss_df.iterrows():
        sid = int(r['source_id'])
        nm = name_map.get(sid, str(sid))
        P_d = float(r['period']) if r.get('period') is not None else None
        if not P_d or P_d <= 0: continue
        e = float(r.get('eccentricity') or 0.0)
        omega = float(r.get('arg_periastron') or 0.0)
        T_peri = float(r.get('t_periastron') or 0.0) + 2455197.5
        V_G = float(r['phot_g_mean_mag']) if r.get('phot_g_mean_mag') is not None else None
        plx = float(r['parallax']) if r.get('parallax') is not None else None
        dist_pc = 1000.0/plx if plx and plx > 0 else None

        m2_mj = m2_map.get(sid)
        if m2_mj is None: continue
        m2_msun = float(m2_mj) / M_JUP_PER_MSUN

        M1_msun = 1.0
        M_tot = M1_msun + m2_msun
        R_star = star_radius_from_mass(M1_msun)
        R_2 = 1.0  # 1 R_jup BD assumption
        R_star_rj = R_star * R_JUP_PER_RSUN
        depth = (R_2 / R_star_rj)**2
        depth_mmag = depth * 1000

        a_AU = kepler_a_AU(P_d, M_tot)
        a_rsun = a_AU / 0.00465
        p_tra = R_star / a_rsun if a_rsun > 0 else 0
        dur_hr = (R_star/a_rsun) * (P_d*24) / math.pi if a_rsun > 0 else None

        try:
            t_tra_jd = next_transit_time(P_d, e, omega, T_peri, now_jd)
            t_tra_dt = datetime(2000, 1, 1, 12, tzinfo=timezone.utc) + \
                       timedelta(days=(t_tra_jd - 2451545.0))
            t_tra_str = t_tra_dt.strftime('%Y-%m-%d %H:%M UT')
        except Exception:
            t_tra_str = 'N/A'

        tier = amateur_tier(V_G, depth_mmag, dur_hr or 1.0)
        rows.append({
            'name': nm, 'gaia_source_id': sid,
            'ra_deg': float(r['ra']), 'dec_deg': float(r['dec']),
            'V_G': round(V_G, 2) if V_G else None,
            'dist_pc': round(dist_pc, 0) if dist_pc else None,
            'P_d': round(P_d, 2), 'e': round(e, 3),
            'M2_MJ': round(float(m2_mj), 1),
            'transit_depth_pct': round(depth*100, 2),
            'transit_depth_mmag': round(depth_mmag, 1),
            'geometric_p_transit_pct': round(p_tra*100, 2),
            'transit_duration_hr': round(dur_hr, 1) if dur_hr else None,
            'next_transit_UT': t_tra_str,
            'amateur_tier': tier,
        })

    out = pl.DataFrame(rows).sort(['geometric_p_transit_pct', 'amateur_tier'], descending=[True, False])
    out.write_csv(ROOT / 'amateur_transit_candidates.csv')
    print(f'\nSaved {len(out)} candidates -> amateur_transit_candidates.csv')
    print('\nTop 5 by geometric p_transit:')
    print(out.head(5).select(['name', 'V_G', 'P_d', 'M2_MJ',
                                 'transit_depth_mmag', 'geometric_p_transit_pct',
                                 'next_transit_UT', 'amateur_tier']).to_pandas().to_string())
    return 0


if __name__ == '__main__':
    sys.exit(main())
