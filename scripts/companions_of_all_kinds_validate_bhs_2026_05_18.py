"""Validate cascade methodology against Gaia BH1, BH2, BH3.

Pulls full Gaia DR3 + NSS rows for the three confirmed BHs and runs the
same Thiele-Innes -> photocentric a -> Kepler M_2 derivation. Compares
recovered M_2 to literature values.

BH1 (El-Badry 2023a, source 4373465352415301632, P=185.6d, M_BH=9.62)
BH2 (5870569352746779008, P=1276.7d, M_BH=8.94)
BH3 (4318465066420528000, P=4253d, M_BH=32.7 — not in NSS due to P > DR3 baseline)
"""
from __future__ import annotations
import math, sys, warnings
warnings.filterwarnings('ignore')
from astroquery.gaia import Gaia

KNOWN = {
    4373465352415301632: ('Gaia BH1', 9.62, 185.6),
    5870569352746779008: ('Gaia BH2', 8.94, 1276.7),
    4318465066420528000: ('Gaia BH3', 32.7,  4253.0),
}


def photocentric_a_mas(A, B, F, G):
    u = 0.5*(A*A+B*B+F*F+G*G); v = A*G-B*F
    disc = max(0, u*u-v*v)
    return math.sqrt(u + math.sqrt(disc))


def solve_m2(fM, M1):
    lo, hi = 0.01, 1000
    for _ in range(100):
        mid = 0.5*(lo+hi)
        if mid**3 > fM * (M1+mid)**2: hi = mid
        else: lo = mid
    return 0.5*(lo+hi)


def main():
    ids = ','.join(str(x) for x in KNOWN)
    q = f"""
    SELECT g.source_id, g.parallax, g.phot_g_mean_mag, g.bp_rp, g.ruwe,
           nss.nss_solution_type, nss.period, nss.eccentricity, nss.significance,
           nss.a_thiele_innes, nss.b_thiele_innes, nss.f_thiele_innes, nss.g_thiele_innes,
           ap.mass_flame
    FROM gaiadr3.gaia_source g
    LEFT JOIN gaiadr3.nss_two_body_orbit nss ON nss.source_id = g.source_id
    LEFT JOIN gaiadr3.astrophysical_parameters ap ON ap.source_id = g.source_id
    WHERE g.source_id IN ({ids})
    """
    df = Gaia.launch_job_async(q).get_results().to_pandas()
    print('=== Gaia BH validation ===')
    print(f'{"Object":<10} {"NSS_type":<25} {"P_d":>8} {"sig":>6} {"a_phot":>7} '
          f'{"M1":>5} {"M2_rec":>7} {"M_BH_lit":>9} {"Bias":>6}')
    for sid, (name, M_lit, P_lit) in KNOWN.items():
        rows = df[df['source_id'] == sid]
        if not len(rows):
            print(f'{name:<10} (no Gaia row)')
            continue
        for _, r in rows.iterrows():
            nss = r['nss_solution_type']
            if nss is None:
                print(f'{name:<10} (no NSS row — expected for BH3, P > DR3 baseline)')
                continue
            A = r['a_thiele_innes']; B = r['b_thiele_innes']
            F = r['f_thiele_innes']; G_ti = r['g_thiele_innes']
            if None in (A, B, F, G_ti):
                print(f'{name:<10} {nss:<25} NO Thiele-Innes')
                continue
            a_phot = photocentric_a_mas(A, B, F, G_ti)
            plx = r['parallax']
            if not (plx and plx > 0): continue
            P_yr = r['period'] / 365.25
            fM = (a_phot/plx)**3 / P_yr**2
            M1 = r['mass_flame'] if r['mass_flame'] and r['mass_flame'] > 0.05 else 1.0
            M2 = solve_m2(fM, M1)
            bias = M2 / M_lit
            print(f'{name:<10} {nss:<25} {r["period"]:>8.1f} {r["significance"]:>6.1f} '
                  f'{a_phot:>7.3f} {M1:>5.2f} {M2:>7.2f} {M_lit:>9.2f} {bias:>5.2f}x')
    return 0


if __name__ == '__main__':
    sys.exit(main())
