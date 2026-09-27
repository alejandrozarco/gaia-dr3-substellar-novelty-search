"""WDJ194901.41+673005.59: quantitative constraints from the existing photometry.

1. Ephemeris coherence and period derivative. Phase of maximum (sinusoid + first harmonic at the fixed adopted frequency
   f0 = 22.6130201 c/d, T0 = BJD_TDB 2459000.00061) fitted per data block: Gaia DR3 G (2014-2017), each TESS SPOC 120-s sector
   (2022-2024; public-repo cache), ATLAS c and o in 3-year blocks (2015-2026). Weighted quadratic fit
   phi(t) = a0 + a1 (t - tm) + 0.5 fdot (t - tm)^2 in cycles -> fdot, P_dot = -fdot/f0^2, compared with the gravitational-wave
   P_dot of a 0.2 + 0.07 Msun binary at this period. (Gaia TCB vs TDB drift over 12 yr ~6 s = 0.0016 cycles: negligible here.)
2. Irradiation model. WD: Teff 18000 K, R1 0.0433 Rsun (SED fit); separation a = 4.208 (M1+M2)^(1/3) P_d^(2/3) Rsun with
   M1 = 0.2, M2 = 0.07. Companion day side approximated as a blackbody at T_d = (T_irr^4 + T_n^4)^(1/4),
   T_irr = T_wd sqrt(R1/a) / 2^(1/4) (uniform redistribution over the day side, zero albedo), night side T_n = 1800 K.
   Predicted semi-amplitude in band X: A_X = 0.5 sin(i) R2^2 [B_X(T_d) - B_X(T_n)] / (R1^2 B_X(T_wd)); solved for R2 sin(i)^(1/2)
   against the measured amplitudes (monochromatic blackbodies at the band pivots: ATLAS c 0.533, o 0.679; Gaia G 0.622,
   BP 0.511, RP 0.777; TESS 0.80 um). Roche-lobe radius (Eggleton 1983) for q = M2/M1 = 0.35 for comparison.
3. Eclipse geometry: eclipses require cos(i) < (R1+R2)/a; the no-eclipse TESS light curve bounds i.
"""
import numpy as np, pandas as pd, glob, warnings; warnings.filterwarnings("ignore")
from astropy.io import fits
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
F0, T0 = 22.6130201, 2459000.00061; P_d = 1 / F0; P_s = P_d * 86400
def phase_fit(t, y, e):
    X = np.vstack([np.ones_like(t)] + [fn(2 * np.pi * k * F0 * (t - T0)) for k in (1, 2) for fn in (np.cos, np.sin)]).T
    W = X / e[:, None]; c = np.linalg.lstsq(W, y / e, rcond=None)[0]; r = y - X @ c
    cov = np.linalg.inv(W.T @ W) * max(np.sum((r / e) ** 2) / (len(t) - 5), 1)
    a = np.hypot(c[1], c[2]); ph = (np.arctan2(c[2], c[1]) / (2 * np.pi))  # phase of maximum in cycles (0 = T0)
    ea = np.sqrt((c[1] ** 2 * cov[1, 1] + c[2] ** 2 * cov[2, 2])) / a
    return (ph + 0.5) % 1 - 0.5, ea / a / (2 * np.pi), a
rows = []
# Gaia G
g = pd.read_csv("gaia_ep.csv")
m = np.isfinite(g.TimeG) & np.isfinite(g.FG) & (g.FG > 0) & (g.GrVFlag == 0)
t = g.TimeG[m].values + 2455197.5; y = g.FG[m].values / np.median(g.FG[m]) - 1; e = g.e_FG[m].values / np.median(g.FG[m])
ph, eph, _ = phase_fit(t, y, e); rows.append(("Gaia G", t.mean(), ph, eph))
# TESS sectors
for p in sorted(glob.glob("../sdssv-white-dwarfs-2026/data/cache/mastDownload/TESS/*1884345742*/*_lc.fits")):
    h = fits.open(p); d = h[1].data; sec = h[0].header["SECTOR"]; q = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"])
    t = d["TIME"][q] + 2457000.0; f = d["PDCSAP_FLUX"][q]; y = f / np.median(f) - 1; e = d["PDCSAP_FLUX_ERR"][q] / np.median(f)
    ph, eph, _ = phase_fit(t, y, e); rows.append((f"TESS S{sec}", t.mean(), ph, eph))
# ATLAS per 3-yr block, both bands separately
from astropy.time import Time; from astropy.coordinates import SkyCoord, EarthLocation; import astropy.units as u
d = pd.read_csv("atlas_fp_J1949.txt", sep=r"\s+"); d.columns = [c.lstrip("#") for c in d.columns]
d = d[(d.duJy > 0) & (d["chi/N"] < 3) & (d.mag5sig > 17.5)].copy()
c0 = SkyCoord(297.25575940, 67.50155413, unit="deg"); tt = Time(d.MJD.values, format="mjd", scale="utc", location=EarthLocation.of_site("greenwich"))
d["bjd"] = (tt.tdb + tt.light_travel_time(c0)).jd; d["y"] = np.nan
for b in "co":
    m = d.F == b; tv = d.loc[m, "bjd"].values; br = np.r_[0, np.where(np.diff(tv) > 60)[0] + 1, m.sum()]; idx = d.index[m]
    for a2, e2 in zip(br[:-1], br[1:]):
        ii = idx[a2:e2]; d.loc[ii, "y"] = d.loc[ii, "uJy"] - d.loc[ii, "uJy"].median()
    s = 1.4826 * np.median(np.abs(d.loc[m, "y"])); d.loc[m & (np.abs(d.y) > 5 * s), "y"] = np.nan
d = d[np.isfinite(d.y)]; MEAN = {"c": 205.0, "o": 183.0}
for b in "co":
    x = d[d.F == b]
    for lo, hi in ((2015, 2019), (2019, 2022), (2022, 2027)):
        yr = Time(x.bjd.values, format="jd").decimalyear; m = (yr >= lo) & (yr < hi)
        if m.sum() > 100:
            ph, eph, _ = phase_fit(x.bjd.values[m], x.y.values[m] / MEAN[b], x.duJy.values[m] / MEAN[b])
            rows.append((f"ATLAS {b} {lo}-{hi}", x.bjd.values[m].mean(), ph, eph))
O = pd.DataFrame(rows, columns=["block", "t_mid", "phase", "e_phase"]); print(O.round(4).to_string(index=False))
tm = np.average(O.t_mid, weights=1 / O.e_phase ** 2); dt = O.t_mid - tm
X = np.vstack([np.ones(len(O)), dt, 0.5 * dt ** 2]).T; W = X / O.e_phase.values[:, None]
cf, *_ = np.linalg.lstsq(W, O.phase.values / O.e_phase.values, rcond=None); r = O.phase.values - X @ cf
chi2 = np.sum((r / O.e_phase.values) ** 2); cov = np.linalg.inv(W.T @ W) * max(chi2 / (len(O) - 3), 1)
fdot, efdot = cf[2], np.sqrt(cov[2, 2])  # cycles/d^2
Pdot = -fdot / F0 ** 2; ePdot = efdot / F0 ** 2  # s/s (dimensionless)
print(f"\nQuadratic ephemeris over {O.t_mid.max()-O.t_mid.min():.0f} d: fdot = {fdot:.2e} +- {efdot:.2e} c/d^2; chi2/dof {chi2:.1f}/{len(O)-3}")
print(f"P_dot = {Pdot:.2e} +- {ePdot:.2e} s/s; |P_dot| 3-sigma < {abs(Pdot)+3*ePdot:.2e}")
# GW P_dot for m1, m2
G, cc, Msun = 6.674e-11, 2.998e8, 1.989e30
for m1, m2 in ((0.2, 0.07), (0.2, 0.05), (0.3, 0.07)):
    Mc = ((m1 * m2) ** 0.6 / (m1 + m2) ** 0.2) * Msun
    Pdot_gw = -(96 / 5) * (2 * np.pi) ** (8 / 3) * (G * Mc / cc ** 3) ** (5 / 3) * P_s ** (-8 / 3) * P_s
    print(f"GW P_dot ({m1}+{m2} Msun): {Pdot_gw:.2e} s/s; timescale P/Pdot {abs(P_s/Pdot_gw)/3.15e7/1e6:.0f} Myr")
# 2. irradiation model
Rsun = 6.957e8; Twd, R1 = 18000.0, 0.0433
a_R = 4.208 * (0.27) ** (1 / 3) * P_d ** (2 / 3)  # Rsun
Tirr = Twd * np.sqrt(R1 / a_R) / 2 ** 0.25; Tn = 1800.0; Td = (Tirr ** 4 + Tn ** 4) ** 0.25
print(f"\na = {a_R:.3f} Rsun; T_sub = {Twd*np.sqrt(R1/a_R):.0f} K; day side (redistributed) T_d = {Td:.0f} K")
h, kB = 6.626e-34, 1.381e-23
B = lambda lam, T: 1 / (lam ** 5 * (np.exp(h * cc / (lam * kB * T)) - 1))
bands = {"ATLAS c": (0.533e-6, 0.130), "ATLAS o": (0.679e-6, 0.197), "Gaia G": (0.622e-6, 0.156), "Gaia BP": (0.511e-6, 0.16), "Gaia RP": (0.777e-6, 0.27), "TESS": (0.80e-6, 0.35)}
print(f"Roche lobe (Eggleton, q=0.35): R_L2 = {a_R * 0.49 * 0.35**(2/3) / (0.6 * 0.35**(2/3) + np.log(1 + 0.35**(1/3))):.4f} Rsun")
print("band    A_obs   R2*sqrt(sin i) [Rsun]: redistributed day side / substellar-temperature day side")
Tsub = Twd * np.sqrt(R1 / a_R)
for k, (lam, A) in bands.items():
    out = []
    for Tday in (Td, Tsub):
        ratio = (B(lam, Tday) - B(lam, Tn)) / B(lam, Twd)
        out.append(R1 * np.sqrt(2 * A / ratio))  # sin i = 1
    print(f"{k:8s} {A:.3f}  {out[0]:.4f} / {out[1]:.4f}")
# 3. eclipse geometry for R2 = 0.09
for R2 in (0.07, 0.09, 0.11):
    imin = np.degrees(np.arccos((R1 + R2) / a_R)); print(f"R2 = {R2}: eclipses require i > {imin:.1f} deg (prob {100*(R1+R2)/a_R:.0f}% for random i); none seen")
# figure
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.errorbar(Time(O.t_mid.values, format="jd").decimalyear, O.phase * P_s / 60, O.e_phase * P_s / 60, fmt="o", ms=4)
ts = np.linspace(O.t_mid.min(), O.t_mid.max(), 200)
ax.plot(Time(ts, format="jd").decimalyear, (cf[0] + cf[1] * (ts - tm) + 0.5 * fdot * (ts - tm) ** 2) * P_s / 60, "r-", lw=1)
ax.set_xlabel("year"); ax.set_ylabel("O-C of maximum (min)"); ax.set_title("WDJ194901.41+673005.59: time of maximum vs the linear ephemeris", fontsize=9)
plt.tight_layout(); plt.savefig("ephemeris_oc.png", dpi=90)
