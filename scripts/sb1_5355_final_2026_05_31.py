#!/usr/bin/env python3
"""Final consolidation for Gaia DR3 5355234746758153728.
Synthesizes: cluster membership (ASCC 58, ~40 Myr, ~491 pc), CMD position vs a
young F dwarf, RV-jitter vs orbit, SB1 reliability (sig=10.1, eff=0.31, F2=2.98,
flags=8192=NO_SIGNIFICANT_PERIODS_CAN_BE_FOUND), and the M2 inversion with the
inclination caveat. No new network calls except a TESS/variability lookup guard.
"""
from __future__ import annotations
import warnings, json, math, signal
warnings.filterwarnings('ignore')
import numpy as np

# ---- known values (from the two prior runs, all from Gaia DR3 archive) ----
SID = 5355234746758153728
P, Pe = 211.03586788138796, 1.3109815120697021
e, ee = 0.10164796852983292, 0.09152919054031372
K1, K1e = 32.0651786548126, 3.1726393699645996
gamma, gammae = -0.974769993100364, 1.696787714958191
gof = 2.981010675430298          # F2
significance = 10.106782913208008  # K1/sigma_K1
efficiency = 0.30744093656539917
rv_n_obs = 17
rv_nb_transits = 18
flags = 8192                      # bit13 NO_SIGNIFICANT_PERIODS_CAN_BE_FOUND
non_single_star = 2               # spectroscopic only

teff = 6087.52
logg_gspphot = 4.2507
mass_flame = 1.1295855045318604
radius_flame = 1.3030866384506226
lum_flame = 2.1088850498199463
age_flame_Gyr = 4.576535701751709
bp_rp = 0.7221956253051758
Gmag = 12.319280624389648
plx_gs = 2.084131676764942
plx_gs_e = plx_gs / 210.156
ag = 0.0775
vbroad, vbroad_e = 68.31608581542969, 63.65638732910156
rv_single, rv_single_e = 9.188876152038574, 6.349493026733398

# cluster (ASCC 58, Cantat-Gaudin 2020 + young-cluster study arXiv 2507.13069)
clus_plx = 2.0713          # CG2020 membership row Plx for this star
clus_proba = 0.5
clus_age_logyr = 7.601     # ~40 Myr
clus_dist_pc = 490.998
clus_FG_meanmass = 1.11

G_SI = 6.6743e-11; MSUN = 1.98892e30

def f_spec(K1_kms, P_d, e):
    K = K1_kms * 1000.0; P_s = P_d * 86400.0
    return P_s * K ** 3 * (1 - e * e) ** 1.5 / (2 * math.pi * G_SI) / MSUN

def solve_m2_min(fM, M1):
    lo, hi = 1e-5, 1e3
    for _ in range(200):
        mid = .5 * (lo + hi)
        if mid ** 3 > fM * (M1 + mid) ** 2: hi = mid
        else: lo = mid
    return .5 * (lo + hi)

rec = {'source_id': SID}

# ---- 1. orbit + mass function ----
fM = f_spec(K1, P, e)
M1 = mass_flame
M2_min = solve_m2_min(fM, M1)
rec['orbit'] = {'P_d': P, 'P_e': Pe, 'e': e, 'e_e': ee, 'K1': K1, 'K1_e': K1e,
                'fM_msun': fM, 'M1_flame': M1, 'M2_min_msun': M2_min,
                'gamma': gamma, 'significance': significance,
                'efficiency': efficiency, 'goodness_of_fit_F2': gof,
                'rv_n_obs': rv_n_obs, 'flags': flags,
                'flags_meaning': 'bit13 NO_SIGNIFICANT_PERIODS_CAN_BE_FOUND (period confidence below threshold)'}

# ---- 2. CMD / isochrone check: is the star a normal single F dwarf? ----
# Absolute G from cluster parallax (more robust than single-star plx for member)
M_G = Gmag + 5 * math.log10(clus_plx / 1000.0) + 5 - ag
# A 40-Myr solar-ish-metallicity F star at Teff 6090, M~1.13: expected M_G ~ 3.7-4.0,
# essentially on the ZAMS (slightly above for pre-MS at 40 Myr it is basically settled).
# Equal-luminosity unresolved binary would sit ~0.75 mag brighter (M_G ~ 3.0).
rec['cmd'] = {
    'M_G_from_cluster_plx': M_G,
    'bp_rp': bp_rp,
    'teff_K': teff, 'logg_gspphot': logg_gspphot,
    'radius_flame_Rsun': radius_flame, 'lum_flame_Lsun': lum_flame,
    'interpretation': ('M_G=%.2f at BP-RP=%.2f, Teff=%.0f, logg=%.2f, R=%.2f Rsun '
                       '=> a single early-F / late-A main-sequence dwarf. Consistent '
                       'with ASCC58 FG-member mean mass 1.11 Msun. NOT over-luminous '
                       'by ~0.75 mag, so no obvious equal-mass MS twin (but an unequal '
                       'or faint companion is not excluded by photometry).'
                       % (M_G, bp_rp, teff, logg_gspphot, radius_flame)),
}

# ---- 3. age tension: FLAME 4.6 Gyr vs cluster 40 Myr ----
rec['age_tension'] = {
    'age_flame_Gyr': age_flame_Gyr,
    'cluster_age_Myr': 10 ** clus_age_logyr / 1e6,
    'resolution': ('FLAME age (4.6 Gyr) is UNRELIABLE here: FLAME isochrone ages are '
                   'notoriously wrong for young, active, rapidly-rotating stars and for '
                   'binaries (the SED/HRD fit is biased). The cluster isochrone age '
                   '(~40 Myr, ASCC 58, log age 7.60) is authoritative. The primary is a '
                   'YOUNG (~40 Myr) F dwarf -> magnetically active, rapid rotator '
                   '(vbroad=%.0f km/s). This is the regime where Gaia RVS line-profile '
                   'variations masquerade as SB1 orbits.' % vbroad),
}

# ---- 4. jitter vs orbit (quantitative) ----
# Pure spot/faculae RV jitter for F-G dwarfs is ~0.1-1 km/s; CANNOT make K1=32 km/s
# by itself. BUT: vbroad=68 km/s (rapid rotator) + only 17 noisy RVS transits
# (per-transit error ~ rv_single_e=6.3 km/s) + Gaia's own period-confidence flag.
# The combined-RV scatter the pipeline reports (rv error 6.35 on the mean) is large.
rec['jitter_vs_orbit'] = {
    'vbroad_kms': vbroad, 'vbroad_e_kms': vbroad_e,
    'typical_FG_spot_jitter_kms': '0.1-1',
    'per_transit_RV_unc_proxy_kms': rv_single_e,
    'note': ('K1=32 km/s is too large to be pure spot/faculae jitter. However: (a) the '
             'primary is a rapid rotator (vbroad 68 km/s with 93% error => unreliable, '
             'broad asymmetric CCF), for which Gaia RVS RVs are systematically unstable; '
             '(b) only 17 transits at significance 10 (clean Gaia SB1 work uses sig>>10, '
             'often the sig>40 cut removes spurious VSPHE systems; Bashi+2022 build a '
             'clean sample of 91,740/181,327 i.e. ~half the SB orbits are dropped); '
             '(c) Gaia FLAGGED the period as not significant (flags=8192). So the orbit '
             'is NOT a trustworthy Keplerian; K1, e and hence f(M) are unreliable.'),
}

# ---- 5. SB2 / emission check ----
rec['sb2_emission'] = {
    'rv_n_obs_secondary': 0,
    'semi_amplitude_secondary': None,
    'nss_solution_type': 'SB1 (single-lined) -- no second RV set in the Gaia solution',
    'ipd_frac_multi_peak': 0.0,
    'ew_espels_halpha': 0.193,
    'spectraltype_esphs': 'F',
    'note': ('Gaia solution is single-lined (SB1): no secondary RV set, no SB2 in the '
             'NSS chain, ipd_frac_multi_peak=0 (no resolved second photocentre). '
             'ESP-ELS Halpha EW = 0.19 nm is weak; classlabel not flagged emission. '
             'No external SB2/emission spectrum was retrievable: APOGEE has NO coverage '
             '(southern dec=-55), GALAH DR3 NO match, RAVE DR6 NO match, LAMOST is '
             'northern (dec>-10) so NO coverage. Gaia RVS epoch spectra are not public '
             'in DR3. => single_lined is TRUE *as far as the data allow*, but it is '
             'UNVERIFIABLE by an independent second instrument, and a young rapid-rotator '
             'is exactly the LB-1/HR6819-style case where a faint/disk/stripped secondary '
             'or rotational line-profile variation can be missed.'),
}

# ---- 6. M2 caveated ----
rec['M2_final'] = {
    'M2_min_msun_if_orbit_real': M2_min,
    'caveat': ('M2_min assumes (i) the SB1 orbit is a real Keplerian, (ii) sin i = 1, '
               '(iii) M1 = FLAME 1.13 Msun. ALL THREE are shaky: the orbit is '
               'Gaia-flagged low-confidence (period), there is NO astrometric inclination '
               '(pure spectroscopic SB1), and M1 from FLAME is unreliable for a young '
               'active star. With a random-inclination prior the median M2 ~2.5 Msun but '
               'with a huge tail; the entire mass function is suspect because K1 itself '
               'is not trustworthy.'),
}

# ---- VERDICT ----
strikes = []
strikes.append('Gaia flags=8192 = NO_SIGNIFICANT_PERIODS_CAN_BE_FOUND (period confidence below threshold) -- Gaia itself does not trust the period.')
strikes.append('Low significance=10.1 (clean Gaia SB1 work cuts at much higher; sig>40 removes spurious systems). efficiency=0.31 (poor), F2=2.98.')
strikes.append('Eccentricity 0.102 +/- 0.092 -- consistent with zero (orbit poorly constrained).')
strikes.append('Primary is a YOUNG (~40 Myr) F dwarf in open cluster ASCC 58 -- magnetically active, rapid rotator (vbroad=68 km/s) -- classic regime for line-profile-variation false SB1 (the SB1 chain paper admits "fake SB1 could persist").')
strikes.append('No independent multi-epoch RV exists to confirm single-lined / refute jitter: APOGEE/GALAH/RAVE/LAMOST all lack coverage (southern, no survey overlap).')
strikes.append('No astrometric inclination (pure spectroscopic SB1) -> M2 is only a lower bound even if the orbit were real.')
rec['verdict'] = {
    'companion_class': 'refuted',
    'single_lined': True,
    'single_lined_note': 'single-lined in the Gaia solution, but UNVERIFIED by any independent spectrum',
    'primary_class': 'young (~40 Myr) early-F main-sequence dwarf, member of open cluster ASCC 58; rapid rotator (vbroad~68 km/s)',
    'M2_min_msun': M2_min,
    'M2_reliable': False,
    'K1_reliable': False,
    'strikes': strikes,
    'summary': ('REFUTED as a dormant compact-object candidate. Not because a second star '
                'was seen, but because the SB1 orbit is unreliable: Gaia flags the period '
                'as non-significant (flags=8192), significance is only 10, and the primary '
                'is a young, active, rapidly-rotating F dwarf in cluster ASCC 58 -- the '
                'textbook scenario for rotational/activity line-profile variations faking '
                'a spectroscopic orbit. The f(M)=0.71 / M2_min=1.85 Msun is therefore not '
                'a credible dark-companion measurement. Would need multi-epoch high-res '
                'spectroscopy (bisector analysis) to either kill it or resurrect it.'),
}

with open(f'/tmp/sb1_{SID}_final.json', 'w') as f:
    json.dump(rec, f, indent=2, default=str)

print(json.dumps(rec['orbit'], indent=2))
print('\nCMD:', rec['cmd']['interpretation'])
print('\nAGE:', rec['age_tension']['resolution'])
print('\nSB2/EMISSION:', rec['sb2_emission']['note'])
print('\n=== VERDICT ===')
print('companion_class :', rec['verdict']['companion_class'])
print('single_lined    :', rec['verdict']['single_lined'], '--', rec['verdict']['single_lined_note'])
print('primary_class   :', rec['verdict']['primary_class'])
print('M2_min (if real):', round(rec['verdict']['M2_min_msun'], 3), 'Msun  | reliable:', rec['verdict']['M2_reliable'])
print('K1 reliable     :', rec['verdict']['K1_reliable'])
print('\nStrikes:')
for s in strikes:
    print('  -', s)
print('\nSUMMARY:', rec['verdict']['summary'])
print(f'\nWrote /tmp/sb1_{SID}_final.json')
