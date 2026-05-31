#!/usr/bin/env python3
"""HD 221469 = Gaia DR3 2865472476175772672 -- SB1 mass-function + isotropic-i M2
posterior, the decisive companion-mass constraint.

The PMa dark/luminous run (hd221469_pma_darkluminous_2026_05_31.py) established:
  - SED = single F8 IV-V star (T1~6050 K, R1=1.75 Rsun, L1=3.68 Lsun); a 2.358-Msun
    A-star companion is excluded at 165 sigma (GALEX) / 56-62 sigma (Gaia G/BP).
  - Gaia DR3 has a fully-determined NSS *SB1 spectroscopic orbit*:
        P = 1240.61 +/- 47.5 d (3.40 yr), e = 0.0140 (circular),
        K1 = semi_amplitude_primary = 5.337 +/- 0.127 km/s, significance = 42.1,
        rv_n_obs_secondary = 0 (no double lines / SB2).
  - Kervella's OWN catalog M2_5AU = 725.9 M_Jup = 0.69 Msun (M-dwarf), NOT 2.36 Msun.

So the period is KNOWN. Invert the spectroscopic mass function to get M2.
Standard SB1: f(M) = (M2 sin i)^3 / (M1+M2)^2 = P K1^3 (1-e^2)^(3/2) / (2 pi G).
MC over M1, K1, P, e errors AND isotropic inclination (cos i uniform) -> M2 posterior.

Env: /Users/legbatterij/claude_projects/ostinato/.venv/bin/python (no pip-install).
Output: /tmp/hd221469_sb1.json
"""
from __future__ import annotations
import json, math
import numpy as np
from scipy.optimize import brentq

G_SI  = 6.6743e-11
MSUN  = 1.98892e30
DAY   = 86400.0
RNG   = np.random.default_rng(20260531)

# ---- Gaia DR3 SB1 orbital elements (from /tmp/hd221469_pma.json nss row) ----
P_d, P_e   = 1240.60566317822, 47.5134162902832      # days
ECC, ECC_e = 0.013950722975959482, 0.04199686646461487
K1, K1_e   = 5.3372518964499145, 0.12664377689361572  # km/s, semi_amplitude_primary
SIG        = 42.14
# Primary mass: FLAME mass_flame=1.177; Kervella M1=1.33; SIMBAD F8IV-V.
# Adopt M1 = 1.25 +/- 0.12 Msun (covers FLAME 1.18 & Kervella 1.33).
M1_MU, M1_SD = 1.25, 0.12

# Caller / Kervella catalog numbers for the comparison table
CALLER_M2  = 2.358
KERV_M2_5AU_MJUP = 725.89      # -> 0.693 Msun
MJUP_PER_MSUN    = 1047.57

def mass_function_from_sb1(P_days, K1_kms, e):
    """f(M) in solar masses: f = P K1^3 (1-e^2)^{3/2} / (2 pi G)."""
    P = P_days * DAY
    K = K1_kms * 1000.0
    fM_kg = P * K**3 * (1.0 - e*e)**1.5 / (2.0 * math.pi * G_SI)
    return fM_kg / MSUN

def m2_from_massfn(fM, M1, sini):
    """Solve (M2 sini)^3 / (M1+M2)^2 = fM for M2 (>0). brentq with an expanding
    upper bracket so the near-face-on (small sin i -> very large M2) tail is kept."""
    if sini <= 1e-4:
        return np.inf
    g = lambda m2: (m2*sini)**3 / (M1 + m2)**2 - fM
    lo = 1e-5
    if g(lo) >= 0:        # degenerate (fM<=0); shouldn't happen for real fM>0
        return lo
    hi = 1.0
    for _ in range(40):
        if g(hi) > 0:
            break
        hi *= 2.0          # expand until bracketed (handles M2 >> 100)
    else:
        return np.inf
    try:
        return float(brentq(g, lo, hi))
    except Exception:
        return np.nan

def run():
    fM_med = mass_function_from_sb1(P_d, K1, ECC)
    M2_min = m2_from_massfn(fM_med, M1_MU, 1.0)       # sin i = 1 -> minimum M2

    # --- Monte Carlo: errors on P,K1,e,M1 + isotropic inclination ---
    # NB: Newton on the cubic mis-converges at small sin i (near face-on, M2 huge),
    # truncating the high-mass tail; use brentq per-draw, which is exact.
    N = 120000
    P_s   = RNG.normal(P_d, P_e, N)
    K_s   = RNG.normal(K1, K1_e, N)
    e_s   = np.clip(RNG.normal(ECC, ECC_e, N), 0.0, 0.95)
    M1_s  = np.clip(RNG.normal(M1_MU, M1_SD, N), 0.5, 3.0)
    cosi  = RNG.uniform(0.0, 1.0, N)        # isotropic: cos i uniform in [0,1]
    sini  = np.sqrt(1.0 - cosi**2)

    fM_s = P_s*DAY * (K_s*1000.0)**3 * (1-e_s**2)**1.5 / (2*math.pi*G_SI) / MSUN
    M2_s = np.array([m2_from_massfn(fM_s[i], M1_s[i], sini[i]) for i in range(N)])
    ok = np.isfinite(M2_s) & (M2_s > 0) & (M2_s < 400)
    print(f"  [MC: {ok.mean()*100:.2f}% of {N} draws solved]")
    M2_s = M2_s[ok]

    pct = lambda a, q: float(np.percentile(a, q))
    post = dict(
        median=pct(M2_s, 50), p16=pct(M2_s, 16), p84=pct(M2_s, 84),
        p2_5=pct(M2_s, 2.5), p97_5=pct(M2_s, 97.5), p99=pct(M2_s, 99),
        mean=float(np.mean(M2_s)),
        P_gt_1_0=float(np.mean(M2_s > 1.0)),
        P_gt_1_4=float(np.mean(M2_s > 1.4)),   # Chandrasekhar / WD ceiling
        P_gt_2_2=float(np.mean(M2_s > 2.2)),   # ~TOV NS ceiling
        P_gt_2_358=float(np.mean(M2_s > CALLER_M2)),  # caller's M2_median
        P_gt_3_0=float(np.mean(M2_s > 3.0)),   # lower mass-gap floor
    )

    # what sin i (hence inclination) would the caller's 2.358 Msun require?
    def sini_for_M2(M2_target, M1, fM):
        # (M2 sini)^3/(M1+M2)^2 = fM  ->  sini = (fM (M1+M2)^2)^(1/3)/M2
        return (fM*(M1+M2_target)**2)**(1/3) / M2_target
    sini_caller = sini_for_M2(CALLER_M2, M1_MU, fM_med)
    incl_caller = math.degrees(math.asin(min(sini_caller, 1.0))) if sini_caller <= 1 else None

    # photocentric semi-major axis cross-check (does M2~0.5 explain RUWE=10.6?)
    # a_rel (AU) from Kepler: a^3 = (M1+M2) P_yr^2 ; a1 = a_rel * M2/(M1+M2)
    P_yr = P_d/365.25
    def a_phot_mas(M2, M1, plx_mas=10.728):
        a_rel = ((M1+M2) * P_yr**2)**(1/3)            # AU
        a1_AU = a_rel * M2/(M1+M2)                     # primary about barycentre
        # for a dark companion the photocentre = primary, so a_phot = a1
        return a1_AU * plx_mas                          # AU*mas/AU... = mas (since a_AU*plx[mas/AU? ] )
    # a1[AU] * plx[mas] / 1[AU at plx]?  a1 in AU, angular = a1*plx_arcsec; plx in mas -> a1*plx_mas = mas
    a_phot_05 = a_phot_mas(0.5, M1_MU)
    a_phot_236 = a_phot_mas(CALLER_M2, M1_MU)

    out = dict(
        source_id=2865472476175772672, hd_name='HD 221469',
        sb1_elements=dict(P_d=P_d, P_e=P_e, P_yr=round(P_yr,3),
                          e=ECC, e_e=ECC_e, K1_kms=K1, K1_e=K1_e,
                          significance=SIG, rv_n_obs_secondary=0),
        M1_adopted=dict(mu=M1_MU, sd=M1_SD, note='FLAME 1.18 / Kervella 1.33 -> 1.25+/-0.12'),
        mass_function_Msun=fM_med,
        M2_min_sini1=M2_min,
        M2_posterior_isotropic_i=post,
        caller_M2_median=CALLER_M2,
        sini_required_for_caller_M2=round(float(sini_caller),3),
        incl_required_for_caller_M2_deg=(round(incl_caller,1) if incl_caller else 'sin i > 1 -> IMPOSSIBLE'),
        kervella_M2_5AU_Msun=round(KERV_M2_5AU_MJUP/MJUP_PER_MSUN,3),
        a_phot_check=dict(a_phot_mas_M2_0p5=round(a_phot_05,3),
                          a_phot_mas_M2_2p36=round(a_phot_236,3),
                          ruwe=10.58,
                          note='dark companion: photocentre=primary, a_phot=a1'),
    )
    with open('/tmp/hd221469_sb1.json','w') as f:
        json.dump(out, f, indent=2)

    print('='*74)
    print('HD 221469  SB1 mass function + isotropic-i M2 posterior')
    print('='*74)
    print(f"  SB1 orbit: P={P_d:.1f} d ({P_yr:.2f} yr), e={ECC:.3f}, K1={K1:.3f} km/s, "
          f"sig={SIG:.0f}, n_obs_secondary=0 (no SB2)")
    print(f"  M1 adopted = {M1_MU} +/- {M1_SD} Msun (FLAME 1.18, Kervella 1.33)")
    print(f"  spectroscopic mass function f(M) = {fM_med:.5f} Msun")
    print(f"  M2_min (sin i = 1)               = {M2_min:.3f} Msun")
    print(f"  M2 posterior (isotropic i):")
    print(f"      median = {post['median']:.3f}  [16-84%: {post['p16']:.3f}-{post['p84']:.3f}]  "
          f"[2.5-97.5%: {post['p2_5']:.3f}-{post['p97_5']:.3f}]")
    print(f"      P(M2>1.0)={post['P_gt_1_0']:.3f}  P(M2>1.4)={post['P_gt_1_4']:.3f}  "
          f"P(M2>2.2)={post['P_gt_2_2']:.3f}  P(M2>2.358)={post['P_gt_2_358']:.3f}  "
          f"P(M2>3.0)={post['P_gt_3_0']:.3f}")
    print(f"  caller's M2_median={CALLER_M2} Msun would require sin i = {sini_caller:.3f} "
          f"-> i = {out['incl_required_for_caller_M2_deg']}")
    print(f"  Kervella catalog M2_5AU = {KERV_M2_5AU_MJUP} M_Jup = "
          f"{KERV_M2_5AU_MJUP/MJUP_PER_MSUN:.3f} Msun")
    print(f"  a_phot (mas): M2=0.5 -> {a_phot_05:.2f} mas ; M2=2.36 -> {a_phot_236:.2f} mas "
          f"(RUWE=10.6 ; even ~0.5 Msun gives a large photocentric wobble)")
    print(f"\nJSON -> /tmp/hd221469_sb1.json")
    return out

if __name__ == '__main__':
    run()
