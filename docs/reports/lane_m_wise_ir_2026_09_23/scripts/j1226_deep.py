import os
# J1226-2304 = Gaia DR3 3513017956589117056 = WISE J122637.85-230414.2 — deep dive 2026-09-23.
# Tests on the WISE ephemeris P = 0.07968185682 d, W1 maximum T0 = BJD_TDB 2459999.9469779:
#  (1) other surveys' epochs (PS1 grizy 2010-14, SkyMapper i/z 2016-20, DECam/NSC, VHS 2015, 2MASS 1999) folded
#      on the WISE ephemeris: does the modulation reach the red optical / near-IR?
#  (2) WISE per season in flux units: mean flux, semi-amplitude, phase of maximum
#  (3) phase stability -> period-derivative limit;  (4) odd/even cycles (P vs 2P) per season.
import json, numpy as np, pandas as pd
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from astropy.table import Table

REF = os.path.expanduser("~/claude_projects/gaia_local_notes/2026-09-23/j1226_referee")
P, sP = 0.07968185682, 4.16e-8
T0, sT0 = 2459999.9469779, 0.0012
c0 = SkyCoord(186.6576602 * u.deg, -23.0706497 * u.deg)
rng = np.random.default_rng(42)
out = {}

def bjd(mjd_utc, site):
    t = Time(mjd_utc, format="mjd", scale="utc", location=site)
    return (t.tdb + t.light_travel_time(c0)).jd

def phase(b):
    return ((b - T0) / P) % 1.0

def sinfit(ph, y, e):
    """y = m0 + a cos2pi ph + b sin2pi ph ; returns full amplitude, phase of y-maximum, errors via bootstrap."""
    X = np.vstack([np.ones_like(ph), np.cos(2 * np.pi * ph), np.sin(2 * np.pi * ph)]).T; w = 1 / e
    bb, *_ = np.linalg.lstsq(X * w[:, None], y * w, rcond=None)
    A = 2 * np.hypot(bb[1], bb[2]); phmax = (np.arctan2(bb[2], bb[1]) / (2 * np.pi)) % 1
    boot = []
    for _ in range(2000):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(i)) < 4: continue
        b2, *_ = np.linalg.lstsq(X[i] * w[i][:, None], y[i] * w[i], rcond=None); boot.append(2 * np.hypot(b2[1], b2[2]))
    perm = []
    for _ in range(2000):
        pp = rng.permutation(ph); Xp = np.vstack([np.ones_like(pp), np.cos(2 * np.pi * pp), np.sin(2 * np.pi * pp)]).T
        b3, *_ = np.linalg.lstsq(Xp * w[:, None], y * w, rcond=None); perm.append(2 * np.hypot(b3[1], b3[2]))
    return dict(n=len(y), A_full=float(A), phase_of_max=float(phmax), A_boot16_84=[float(np.percentile(boot, 16)), float(np.percentile(boot, 84))],
                p_perm=float(np.mean(np.array(perm) >= A)), m0=float(bb[0]), rms=float(np.std(y)), med_err=float(np.median(e)))

def fixedfit(ph, y, e):
    """y = m0 - A cos(2pi ph): brightening (in mag, y smaller) at W1 maximum phase 0. Returns semi-amplitude A (mag)."""
    X = np.vstack([np.ones_like(ph), -np.cos(2 * np.pi * ph)]).T; w = 1 / e
    bb, res, *_ = np.linalg.lstsq(X * w[:, None], y * w, rcond=None)
    cov = np.linalg.inv((X * w[:, None]).T @ (X * w[:, None])); chi2r = float(np.sum(((y - X @ bb) * w) ** 2) / max(len(y) - 2, 1))
    return dict(A_semi=float(bb[1]), err=float(np.sqrt(cov[1, 1] * max(chi2r, 1))), chi2r=chi2r)

# ---------------- (1) other surveys folded on the WISE ephemeris ----------------
hal = EarthLocation(lat=20.7075 * u.deg, lon=-156.2561 * u.deg, height=3055 * u.m)      # Pan-STARRS
sso = EarthLocation(lat=-31.2733 * u.deg, lon=149.0617 * u.deg, height=1165 * u.m)      # SkyMapper
ctio = EarthLocation(lat=-30.1690 * u.deg, lon=-70.8063 * u.deg, height=2200 * u.m)     # DECam, 2MASS-S
par = EarthLocation(lat=-24.6153 * u.deg, lon=-70.3976 * u.deg, height=2518 * u.m)      # VISTA
ps1 = pd.read_csv(f"{REF}/ps1_det_clean.csv")                                             # psfQfPerfect > 0.9; bjd from obsTime (TAI) at Haleakala
ps1["ph"] = phase(ps1["bjd"].values)
out["ps1"] = {}
for b in "grizy":
    s = ps1[ps1.band == b]
    if len(s) < 5: continue
    out["ps1"][b] = dict(free=sinfit(s.ph.values, s.mag.values, s.err.values), fixed=fixedfit(s.ph.values, s.mag.values, s.err.values),
                         years=[float(Time(s.bjd.min(), format="jd").decimalyear), float(Time(s.bjd.max(), format="jd").decimalyear)])
sm = pd.read_csv("../data/j1226_skymapper_dr4_epochs.csv", comment="#")
sm["bjd"] = bjd(sm["date"].values + sm["exp_time"].values / 2 / 86400, sso); sm["ph"] = phase(sm["bjd"].values)
smc = sm[(sm["flags"] == 0) & (sm["nimaflags"] == 0)]
out["skymapper"] = {b: dict(n=int((smc["filter"] == b).sum()), rows=[(round(float(r.ph), 3), float(r.mag_psf), float(r.e_mag_psf), round(float(Time(r.bjd, format='jd').decimalyear), 2))
                        for r in smc[smc["filter"] == b].itertuples()]) for b in ("i", "z")}
for b in ("i", "z"):
    s = smc[smc["filter"] == b]
    if len(s) >= 4: out["skymapper"][b]["fixed"] = fixedfit(s.ph.values, s.mag_psf.values, s.e_mag_psf.values)
nsc = Table.read(f"{REF}/nsc_meas.ecsv").to_pandas()
nsc["bjd"] = bjd(nsc["mjd"].values, ctio); nsc["ph"] = phase(nsc["bjd"].values)
out["decam_nsc"] = [(r.filter, round(float(r.ph), 3), float(r.mag_auto), float(r.magerr_auto), round(float(Time(r.bjd, format="jd").decimalyear), 2)) for r in nsc.itertuples()]
vhs = {"Y": (57087.124637, 17.0924, 0.0254), "J": (57087.119129, 16.5248, 0.0279), "Ks": (57087.114818, 15.6494, 0.0659)}
out["vhs_dr5"] = {k: dict(phase=round(float(phase(bjd(np.array([v[0]]), par))[0]), 3), mag=v[1], err=v[2]) for k, v in vhs.items()}
jd2m = 2451245.8736
out["2mass"] = dict(phase=round(float(phase(bjd(np.array([jd2m - 2400000.5]), ctio))[0]), 3), J=(16.601, 0.164), H=(16.003, 0.197), K=(15.517, 0.21),
                    phase_sigma_from_ephemeris=float(np.hypot(abs(jd2m - T0) / P * sP / P, sT0 / P)))
# red-optical combination: PS1 z,y + SkyMapper z + DECam z as residuals from each survey/band median
red = []
for b in ("z", "y"):
    s = ps1[ps1.band == b]; red += [(p, m - np.median(s.mag), e, f"ps1_{b}") for p, m, e in zip(s.ph, s.mag, s.err)]
s = smc[smc["filter"] == "z"]; red += [(p, m - np.median(s.mag_psf), e, "sm_z") for p, m, e in zip(s.ph, s.mag_psf, s.e_mag_psf)]
red = np.array([(a, b_, c) for a, b_, c, _ in red])
out["red_zy_combined"] = dict(free=sinfit(red[:, 0], red[:, 1], red[:, 2]), fixed=fixedfit(red[:, 0], red[:, 1], red[:, 2]))

# ---------------- (2) WISE per season in flux units ----------------
w = pd.read_csv(f"{REF}/target_w1_clean_model.csv")
w["m1"] = w.w1mpro - w.zp
w["F1"] = 309.54e3 * 10 ** (-0.4 * w.m1); w["eF1"] = w.F1 * w.w1sigmpro / 1.0857                     # mJy (W1 Vega zero point 309.54 Jy)
w["F2"] = 171.787e3 * 10 ** (-0.4 * w.w2mpro); w["eF2"] = w.F2 * w.w2sigmpro / 1.0857
w["ph"] = phase(w.bjd.values); w["E"] = np.round((w.bjd.values - T0) / P).astype(int)
w = w.sort_values("bjd"); seas = np.cumsum(np.r_[0, np.diff(w.bjd.values) > 60]); w["season"] = seas
rows = []
for k, s in w.groupby("season"):
    if len(s) < 8: continue
    r = dict(season=int(k), year=round(float(Time(s.bjd.mean(), format="jd").decimalyear), 2), n=len(s))
    for band in ("1", "2"):
        F, eF = s[f"F{band}"].values, s[f"eF{band}"].values
        ok = np.isfinite(F) & np.isfinite(eF) & (eF > 0)
        X = np.vstack([np.ones(ok.sum()), np.cos(2 * np.pi * s.ph.values[ok]), np.sin(2 * np.pi * s.ph.values[ok])]).T; wt = 1 / eF[ok]
        bb, *_ = np.linalg.lstsq(X * wt[:, None], F[ok] * wt, rcond=None); cov = np.linalg.inv((X * wt[:, None]).T @ (X * wt[:, None]))
        chi2r = float(np.sum(((F[ok] - X @ bb) * wt) ** 2) / max(ok.sum() - 3, 1)); sc = np.sqrt(max(chi2r, 1))
        amp = float(np.hypot(bb[1], bb[2])); eamp = float(np.sqrt((bb[1] ** 2 * cov[1, 1] + bb[2] ** 2 * cov[2, 2]) / max(amp ** 2, 1e-12)) * sc)
        r[f"W{band}_mean_mJy"] = round(float(bb[0]), 4); r[f"W{band}_emean"] = round(float(np.sqrt(cov[0, 0]) * sc), 4)
        r[f"W{band}_semiamp_mJy"] = round(amp, 4); r[f"W{band}_esemiamp"] = round(eamp, 4)
        r[f"W{band}_phase_of_max"] = round(float((np.arctan2(bb[2], bb[1]) / (2 * np.pi)) % 1), 3)
        r[f"W{band}_ephase"] = round(float(eamp / max(amp, 1e-9) / (2 * np.pi)), 3)
        # odd/even cycles (P_orb = 2P test): separate semi-amplitudes
        if band == "1":
            oe = {}
            for par_ in (0, 1):
                m = ok & (s.E.values % 2 == par_)
                if m.sum() >= 5:
                    Xo = np.vstack([np.ones(m.sum()), np.cos(2 * np.pi * s.ph.values[m]), np.sin(2 * np.pi * s.ph.values[m])]).T; wo = 1 / eF[m]
                    bo, *_ = np.linalg.lstsq(Xo * wo[:, None], F[m] * wo, rcond=None); co = np.linalg.inv((Xo * wo[:, None]).T @ (Xo * wo[:, None]))
                    oe["even" if par_ == 0 else "odd"] = (round(float(np.hypot(bo[1], bo[2])), 4), round(float(bo[0]), 4), int(m.sum()),
                                                          round(float(np.sqrt(co[1, 1] + co[2, 2]) / np.sqrt(2) * sc), 4))
            r["W1_odd_even_semiamp_mean_n_err"] = oe
    rows.append(r)
out["wise_seasons"] = rows
# (3) phase of maximum vs time -> period correction and derivative
S = pd.DataFrame(rows)
tt = np.array([Time(y, format="decimalyear").jd for y in S.year]); E = (tt - T0) / P
phm = S.W1_phase_of_max.values.copy(); phm[phm > 0.5] -= 1.0; ep = np.maximum(S.W1_ephase.values, 0.005)
X = np.vstack([np.ones_like(E), E, 0.5 * E ** 2]).T; wt = 1 / ep
bb, *_ = np.linalg.lstsq(X * wt[:, None], phm * wt, rcond=None); cov = np.linalg.inv((X * wt[:, None]).T @ (X * wt[:, None]))
chi2r = float(np.sum(((phm - X @ bb) * wt) ** 2) / max(len(E) - 3, 1))
# phase(E) = const + dnu*E + 0.5*Pdot*E^2 (cycles) with phase measured as a delay of maximum -> Pdot = bb[2]
out["timing"] = dict(E_range=[float(E.min()), float(E.max())], Pdot=float(bb[2]), Pdot_err=float(np.sqrt(cov[2, 2]) * np.sqrt(max(chi2r, 1))),
                     linear_term_cycles_per_cycle=float(bb[1]), chi2r=chi2r)
json.dump(out, open("../data/j1226_deep_results.json", "w"), indent=1, default=float)

# ---------------- report ----------------
print("PS1 folded on the WISE ephemeris (free-phase sinusoid; phase_of_max = phase of the FAINTEST point, W1 max is at 0.0):")
for b, v in out["ps1"].items():
    f, x = v["free"], v["fixed"]
    print(f"  {b}: n={f['n']:2d} years {v['years'][0]:.1f}-{v['years'][1]:.1f} rms {f['rms']:.3f} err {f['med_err']:.3f} | free A_full {f['A_full']:.3f} "
          f"(boot {f['A_boot16_84'][0]:.3f}-{f['A_boot16_84'][1]:.3f}) faintest at phase {f['phase_of_max']:.2f}, p_perm {f['p_perm']:.3f} | "
          f"fixed (bright at W1 max) semi-amp {x['A_semi']:+.3f} +- {x['err']:.3f} (chi2r {x['chi2r']:.1f})")
f, x = out["red_zy_combined"]["free"], out["red_zy_combined"]["fixed"]
print(f"  PS1 z+y + SkyMapper z combined: n={f['n']} free A_full {f['A_full']:.3f} faintest at {f['phase_of_max']:.2f} p_perm {f['p_perm']:.3f} | fixed semi-amp {x['A_semi']:+.3f} +- {x['err']:.3f}")
for b in ("i", "z"):
    v = out["skymapper"][b]; print(f"  SkyMapper {b}: n={v['n']} fixed {v.get('fixed')} rows (phase, mag, err, yr): {v['rows']}")
print("  DECam/NSC (filter, phase, mag_auto, err, yr):", out["decam_nsc"])
print("  VHS DR5:", out["vhs_dr5"]); print("  2MASS:", out["2mass"])
print("\nWISE per season (flux mJy; phase of max relative to the ephemeris):")
for r in rows:
    print(f"  {r['year']:.2f} n={r['n']:2d} | W1 mean {r['W1_mean_mJy']:.4f}+-{r['W1_emean']:.4f} semi-amp {r['W1_semiamp_mJy']:.4f}+-{r['W1_esemiamp']:.4f} "
          f"(pulsed {r['W1_semiamp_mJy']/r['W1_mean_mJy']:.2f}) max@{r['W1_phase_of_max']:.3f}+-{r['W1_ephase']:.3f} | W2 mean {r['W2_mean_mJy']:.4f} "
          f"semi {r['W2_semiamp_mJy']:.4f}+-{r['W2_esemiamp']:.4f} | odd/even {r.get('W1_odd_even_semiamp_mean_n_err')}")
print("\ntiming:", out["timing"])
