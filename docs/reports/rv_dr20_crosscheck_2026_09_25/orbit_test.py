"""Test Gaia DR3 NSS orbits against SDSS-V DR20 visit RVs (APOGEE, BOSS).
Orbital (astrometric): Thiele-Innes -> a_phot, i, omega (Halbwachs et al. 2023 convention); K_pred = 2 pi (a_phot/plx) sin i /
(P sqrt(1-e^2)) x 4.74047 km/s, i.e. the primary's amplitude if the photocentre traces the primary (dark companion).
AstroSpectroSB1 / SB1: catalogue omega and K1.
Model v = gamma_inst + A [cos(omega + nu) + e cos(omega)]; linear fit for A and one gamma per instrument (APOGEE, BOSS).
R = A / K_pred (Orbital: |A|, sign of omega ambiguous). Phase error from P and T_peri errors propagated to each epoch."""
import numpy as np, pandas as pd
V = pd.read_csv("visits_clean.csv", dtype={"gaia": str}); N = pd.read_csv("nss_orbits.csv", dtype={"source_id": str})
T = pd.read_csv("targets.csv", dtype=str).set_index("gaia")
def kepler(M, e):
    E = M.copy()
    for _ in range(50): E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    return 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))
rows = []
for r in N.itertuples():
    v = V[V.gaia == r.source_id].sort_values("t")
    if len(v) < 3: continue
    P = r.period; e = r.eccentricity if np.isfinite(r.eccentricity) else 0.0; Tp = 2457389.0 + r.t_periastron - 2400000.5
    if r.nss_solution_type in ("Orbital", "AstroSpectroSB1") and np.isfinite(r.a_thiele_innes):
        A_, B_, F_, G_ = r.a_thiele_innes, r.b_thiele_innes, r.f_thiele_innes, r.g_thiele_innes
        u = (A_**2 + B_**2 + F_**2 + G_**2) / 2; w = A_ * G_ - B_ * F_; a = np.sqrt(u + np.sqrt((u + w) * (u - w)))
        inc = np.arccos(np.clip(w / a**2, -1, 1)); wpO = np.arctan2(B_ - F_, A_ + G_); wmO = np.arctan2(-B_ - F_, A_ - G_)
        om = (wpO + wmO) / 2; Om = (wpO - wmO) / 2
        if Om < 0: om += np.pi; Om += np.pi
        Kp = 2 * np.pi * (a / r.parallax) * np.sin(inc) / (P / 365.25 * np.sqrt(1 - e**2)) * 4.74047
    else:
        a = inc = np.nan; om = np.radians(r.arg_periastron) if np.isfinite(r.arg_periastron) else np.nan; Kp = np.nan
    if r.nss_solution_type in ("SB1", "AstroSpectroSB1") and np.isfinite(r.arg_periastron):
        om_cat = np.radians(r.arg_periastron)
    else: om_cat = np.nan
    omega = om_cat if r.nss_solution_type in ("SB1", "AstroSpectroSB1") else om
    if not np.isfinite(omega): continue
    M = 2 * np.pi * ((v.t.values - Tp) / P % 1); nu = kepler(M, e); f = np.cos(omega + nu) + e * np.cos(omega)
    insts = sorted(v.inst.unique()); X = np.column_stack([f] + [(v.inst.values == i).astype(float) for i in insts]); W = 1 / v.e.values**2
    if len(v) <= X.shape[1]: continue
    cov = np.linalg.inv(X.T @ (X * W[:, None])); p = cov @ (X.T @ (W * v.rv.values)); res = v.rv.values - X @ p
    chi2 = float(np.sum(W * res**2)); dof = len(v) - X.shape[1]
    Xc = X[:, 1:]; covc = np.linalg.inv(Xc.T @ (Xc * W[:, None])); pc = covc @ (Xc.T @ (W * v.rv.values)); chi2c = float(np.sum(W * (v.rv.values - Xc @ pc)**2))
    dph = np.sqrt((r.t_periastron_error / P)**2 + (((v.t.values - Tp) / P**2) * r.period_error)**2) if np.isfinite(r.period_error) else np.full(len(v), np.nan)
    Kcat = r.semi_amplitude_primary
    rows.append(dict(gaia=r.source_id, sol=r.nss_solution_type, P_d=round(P, 2), e=round(e, 3), inc_deg=round(np.degrees(inc), 1) if np.isfinite(inc) else np.nan,
                     K_pred=round(Kp, 2) if np.isfinite(Kp) else np.nan, K_cat=round(Kcat, 2) if np.isfinite(Kcat) else np.nan,
                     A_fit=round(p[0], 2), A_err=round(np.sqrt(cov[0, 0]), 2), R=round(abs(p[0]) / Kp, 2) if np.isfinite(Kp) and Kp > 0 else np.nan,
                     R_err=round(np.sqrt(cov[0, 0]) / Kp, 2) if np.isfinite(Kp) and Kp > 0 else np.nan,
                     n=len(v), insts="+".join(insts), base_d=round(v.t.max() - v.t.min(), 1), phase_err_max=round(float(np.nanmax(dph)), 3),
                     phase_cover=round(float((v.t.max() - v.t.min()) / P), 2), chi2=round(chi2, 1), dof=dof, chi2_const=round(chi2c, 1),
                     sig=round(r.significance, 1) if np.isfinite(r.significance) else np.nan, gof=r.goodness_of_fit, set=T.set.get(r.source_id, "")))
out = pd.DataFrame(rows); out.to_csv("orbit_test.csv", index=False); print(len(out), "orbits tested"); print(out.sol.value_counts().to_dict())
