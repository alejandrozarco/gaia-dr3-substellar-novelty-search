# J0753 = Gaia DR3 3082614748370926848: two-component SED decomposition at the Gaia distance.
# Component 1: empirical M dwarf (mtemplate.csv, interpolated in M_J). Component 2: blackbody (T, R). Bands: Gaia G/BP/RP (Vega),
# PS1 grizy (AB; means over a variable source, 0.1 mag adopted errors), VHS J/Ks (Vega; 2011). Monochromatic effective wavelengths.
# Also: M-dwarf-only fit for comparison; distance varied over the parallax 1-sigma range.
import numpy as np, json
T_ = np.genfromtxt("../data/mdwarf_template.csv", delimiter=",", skip_header=1, names=True)
bands = ["G", "BP", "RP", "g", "r", "i", "z", "y", "J", "Ks"]
obs = dict(G=19.795, BP=20.798, RP=18.752, g=20.981, r=20.173, i=19.120, z=18.813, y=18.328, J=17.514, Ks=16.389)
err = dict(G=0.05, BP=0.13, RP=0.05, g=0.10, r=0.10, i=0.10, z=0.10, y=0.10, J=0.20, Ks=0.27)
lam = dict(G=0.6230, BP=0.5110, RP=0.7770, g=0.4866, r=0.6215, i=0.7545, z=0.8679, y=0.9633, J=1.235, Ks=2.159)      # micron
zp = dict(G=3228.8, BP=3552.0, RP=2554.9, g=3631.0, r=3631.0, i=3631.0, z=3631.0, y=3631.0, J=1594.0, Ks=666.7)        # Jy (Vega Gaia/2MASS, AB PS1)
def mag2jy(b, m): return zp[b] * 10 ** (-0.4 * m)
def mtempl(MJ):
    return {b: np.interp(MJ, T_["MJ_centre"], T_[b]) for b in bands}
h, c, k = 6.626e-27, 2.998e10, 1.381e-16; Rsun, pc = 6.957e10, 3.0857e18
def bb_jy(b, T, R, d_pc):
    nu = c / (lam[b] * 1e-4); B = 2 * h * nu ** 3 / c ** 2 / np.expm1(h * nu / (k * T))
    return np.pi * B * (R * Rsun / (d_pc * pc)) ** 2 * 1e23
Fobs = np.array([mag2jy(b, obs[b]) for b in bands]); eF = Fobs * np.array([err[b] for b in bands]) / 1.0857
def fit(d_pc):
    dm = 5 * np.log10(d_pc / 10); best = (np.inf, None); bestM = (np.inf, None)
    for MJ in np.arange(8.6, 11.0, 0.02):
        tm = mtempl(MJ); FM = np.array([mag2jy(b, tm[b] + dm) for b in bands])
        chiM = np.sum(((Fobs - FM) / eF) ** 2)
        if chiM < bestM[0]: bestM = (chiM, MJ)
        for T in np.exp(np.linspace(np.log(3000), np.log(40000), 70)):
            unit = np.array([bb_jy(b, T, 1.0, d_pc) for b in bands])          # flux for R = 1 Rsun
            # best-fitting R^2 scale (linear, non-negative) given the M dwarf
            s = max(np.sum(unit * (Fobs - FM) / eF ** 2) / np.sum(unit ** 2 / eF ** 2), 0.0)
            chi = np.sum(((Fobs - FM - s * unit) / eF) ** 2)
            if chi < best[0]: best = (chi, (MJ, T, np.sqrt(s)))
    return best, bestM
res = {}
for lab, plx in (("plx", 2.7229), ("plx+1sig", 2.7229 + 0.5424), ("plx-1sig", 2.7229 - 0.5424)):
    d = 1000 / plx; (chi, (MJ, T, R)), (chiM, MJM) = fit(d)
    res[lab] = dict(d_pc=d, MJ=MJ, T=T, R_Rsun=R, chi2=chi, chi2_Monly=chiM, MJ_Monly=MJM)
    print(f"{lab}: d = {d:.0f} pc | M dwarf + blackbody: M_J {MJ:.2f}, T {T:.0f} K, R {R:.4f} Rsun ({R*109.1:.2f} Earth radii), chi2 {chi:.1f} (10 bands, 3 params) "
          f"| M dwarf only: M_J {MJM:.2f}, chi2 {chiM:.1f}")
# chi2 contour in (T, R) at the nominal distance, M_J free
d = 1000 / 2.7229; dm = 5 * np.log10(d / 10); grid = []
for T in np.exp(np.linspace(np.log(3000), np.log(40000), 60)):
    unit = np.array([bb_jy(b, T, 1.0, d) for b in bands]); bestc = np.inf; bestR = None
    for MJ in np.arange(8.6, 11.0, 0.02):
        tm = mtempl(MJ); FM = np.array([mag2jy(b, tm[b] + dm) for b in bands])
        s = max(np.sum(unit * (Fobs - FM) / eF ** 2) / np.sum(unit ** 2 / eF ** 2), 0.0); chi = np.sum(((Fobs - FM - s * unit) / eF) ** 2)
        if chi < bestc: bestc, bestR = chi, np.sqrt(s)
    grid.append((T, bestR, bestc))
grid = np.array(grid); cmin = grid[:, 2].min(); ok = grid[:, 2] < cmin + 2.3 * max(cmin / 7, 1)       # 68% for 2 params, chi2 scaled to chi2_r
print(f"68% region (chi2 scaled to chi2_r = {cmin/7:.2f}): T {grid[ok,0].min():.0f}-{grid[ok,0].max():.0f} K, R {grid[ok,1].min():.4f}-{grid[ok,1].max():.4f} Rsun")
res["T_range_68"] = [float(grid[ok, 0].min()), float(grid[ok, 0].max())]; res["R_range_68"] = [float(grid[ok, 1].min()), float(grid[ok, 1].max())]
json.dump(res, open("sed_fit.json", "w"), indent=1, default=float)
