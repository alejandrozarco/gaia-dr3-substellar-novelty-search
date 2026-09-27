"""Uniform deep-dive checks for short-period white dwarfs with a red-rising modulation.

Per star (Gaia DR3 id, frequency c/d, t_max BJD_TDB):
1. SED: GALEX AIS FUV/NUV; Pan-STARRS DR1 g r i z (Dec > -30) or SkyMapper DR4 g r i z (south, treated as SDSS g r i z); Gaia G/BP.
   Montreal pure-H synthetic colours (Table_DA) at log g 7.0; Teff 8-60 kK; E(B-V) 0 to the SFD total column (IRSA DUST service;
   fallback 0.1); A/E(B-V): FUV 4.89, NUV 7.24, g 3.17, r 2.27, i 1.68, z 1.32, y 1.09, G 2.74, BP 3.37, RP 2.04. Free magnitude offset ->
   radius relative to the log g 7.0 model radius at d = 1/parallax. Residuals reported for all bands including RP and y.
2. Gaia colour vs phase: per-transit BP-RP (variability-rejected transits removed) against cos(2 pi phase) (phase 0 = t_max); Spearman.
3. Geometry: separation for M1 = 0.2 (or GF21 H mass if larger) + M2 = 0.07 Msun; Roche-lobe-filling mean density 107 P_h^-2 g/cm3;
   substellar-point temperature T_WD (R_WD / a)^0.5.
Usage: python companion_deepdive.py <gaia_dr3> <freq_cd> <t_max_bjd> [out_prefix]"""
import sys, os, io, requests, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier; from astroquery.gaia import Gaia
import astropy.units as u; from astropy.coordinates import SkyCoord
from scipy.stats import spearmanr
H = os.path.dirname(os.path.abspath(__file__)); gid, f0, tmax = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); pre = sys.argv[4] if len(sys.argv) > 4 else gid
V = Vizier(columns=["**"], row_limit=3); V.TIMEOUT = 200
g = V.query_constraints(catalog="I/355/gaiadr3", Source=gid)[0][0]; ra, dec = float(g["RA_ICRS"]), float(g["DE_ICRS"]); plx = float(g["Plx"]); c = SkyCoord(ra, dec, unit="deg")
obs = {"G": (float(g["Gmag"]), 0.02), "BP": (float(g["BPmag"]), max(float(g["e_BPmag"]), 0.02)), "RP": (float(g["RPmag"]), max(float(g["e_RPmag"]), 0.02))}
def q(cat, r):
    t = V.query_region(c, radius=r * u.arcsec, catalog=cat); return t[0][0] if len(t) else None
x = q("II/335/galex_ais", 3)
if x is not None:
    for b, m, e in (("FUV", "FUVmag", "e_FUVmag"), ("NUV", "NUVmag", "e_NUVmag")):
        if not np.ma.is_masked(x[m]): obs[b] = (float(x[m]), max(float(x[e]), 0.03))
if dec > -30:
    x = q("II/349/ps1", 1.5)
    if x is not None:
        for b in "grizy":
            if not np.ma.is_masked(x[f"{b}mag"]): obs[b] = (float(x[f"{b}mag"]), max(float(x[f"e_{b}mag"]), 0.02))
else:
    x = q("II/379/smssdr4", 2)
    if x is not None:
        for b in "griz":
            for col in (f"{b}PSF", f"{b}mag"):
                if col in x.colnames and not np.ma.is_masked(x[col]): obs[b] = (float(x[col]), max(float(x[f"e_{col}"]) if f"e_{col}" in x.colnames and not np.ma.is_masked(x[f"e_{col}"]) else 0.03, 0.03)); break
try:
    txt = requests.get(f"https://irsa.ipac.caltech.edu/cgi-bin/DUST/nph-dust?locstr={ra}+{dec}+equ+j2000&regSize=2.0", timeout=60).text.replace("\n", "")
    ebv_max = float(txt.split("<refPixelValueSFD>")[1].split("(mag)")[0])
except Exception:
    ebv_max = 0.1
L = open(os.path.join(H, "Table_DA.txt")).readlines(); hdr = L[1].replace("log g", "logg").split(); D = np.array([[float(v) for v in l.split()] for l in L[2:] if len(l.split()) == len(hdr)])
ps = [i for i, h in enumerate(hdr) if h == "g"][1]; sd = [i for i, h in enumerate(hdr) if h == "g"][0]
col = {"FUV": hdr.index("FUV"), "NUV": hdr.index("NUV"), "G": hdr.index("G3"), "BP": hdr.index("G3_BP"), "RP": hdr.index("G3_RP")}
col.update({b: (ps if dec > -30 else sd) + k for k, b in enumerate("griz")}); col["y"] = ps + 4
R = {"FUV": 4.89, "NUV": 7.24, "g": 3.17, "r": 2.27, "i": 1.68, "z": 1.32, "y": 1.09, "G": 2.74, "BP": 3.37, "RP": 2.04}
fit_b = [b for b in ("FUV", "NUV", "g", "r", "i", "z", "G", "BP") if b in obs]; DM = 5 * np.log10(1000 / plx / 10)
qq = D[np.isclose(D[:, 1], 7.0)]; qq = qq[np.argsort(qq[:, 0])]; best = []
for te in np.arange(8000, 60001, 250):
    mod = {b: np.interp(te, qq[:, 0], qq[:, col[b]]) for b in col}
    for ebv in np.arange(0, ebv_max + 0.005, 0.01):
        res = np.array([obs[b][0] - R[b] * ebv - DM - mod[b] for b in fit_b]); w = np.array([1 / max(obs[b][1], 0.03) ** 2 for b in fit_b])
        off = np.sum(res * w) / np.sum(w); best.append((np.sum((res - off) ** 2 * w), te, ebv, off))
best.sort(); chi0, te0, eb0, off0 = best[0]; ok = [b for b in best if b[0] <= chi0 + 4]
Msun, Rsun, Gc = 1.989e33, 6.957e10, 6.674e-8
def rad(te, off):
    m = np.interp(te, qq[:, 0], qq[:, 2]); return np.sqrt(Gc * m * Msun / 1e7) / Rsun * 10 ** (-0.2 * off)
rwd = rad(te0, off0); mod = {b: np.interp(te0, qq[:, 0], qq[:, col[b]]) for b in col}
resid = {b: round(obs[b][0] - R[b] * eb0 - DM - mod[b] - off0, 3) for b in obs}
VE = Vizier(columns=["**"], row_limit=-1); VE.TIMEOUT = 200; e = VE.query_constraints(catalog="I/355/epphot", Source=gid); e = e[0].to_pandas() if len(e) else None; cp = (np.nan, np.nan, np.nan, np.nan, 0)
if e is not None:
    m = np.isfinite(e.FBP) & np.isfinite(e.FRP) & (e.FBP > 0) & (e.FRP > 0) & (e.BPrVFlag == 0) & (e.RPrVFlag == 0)
    ph = ((e.TimeBP[m].values + 2455197.5 - tmax) * f0) % 1; cl = -2.5 * np.log10(e.FBP[m].values / e.FRP[m].values); cl -= np.median(cl)
    rho, p = spearmanr(np.cos(2 * np.pi * ph), cl); mx = cl[np.cos(2 * np.pi * ph) > 0.5]; mn = cl[np.cos(2 * np.pi * ph) < -0.5]; cp = (rho, p, mx.mean(), mn.mean(), int(m.sum()))
gf = V.query_constraints(catalog="J/MNRAS/508/3877/maincat", GaiaEDR3=gid); m1 = max(0.2, float(gf[0][0]["MassH"])) if len(gf) and not np.ma.is_masked(gf[0][0]["MassH"]) else 0.2
Ph = 24 / f0; a = 4.208 * (m1 + 0.07) ** (1 / 3) * (Ph / 24) ** (2 / 3); rho_rl = 107 / Ph ** 2; tsub = te0 * np.sqrt(rwd / a)
out = dict(gaia_dr3=gid, P_min=round(1440 / f0, 3), n_sed_bands=len(fit_b), sed_chi2=round(chi0, 1), teff=int(te0), teff_lo=int(min(b[1] for b in ok)), teff_hi=int(max(b[1] for b in ok)),
           ebv=round(eb0, 2), ebv_sfd=round(ebv_max, 3), radius_rsun=round(rwd, 4), resid=resid, colour_phase_spearman=round(cp[0], 2), colour_phase_p=float(f"{cp[1]:.2g}"),
           bprp_max=round(cp[2], 3), bprp_min=round(cp[3], 3), n_transits=cp[4], m1_assumed=round(m1, 2), a_rsun=round(a, 3), rho_rochelobe=round(rho_rl, 1), t_substellar=int(tsub))
print(out); pd.DataFrame([{**{k: v for k, v in out.items() if k != "resid"}, **{f"resid_{b}": v for b, v in resid.items()}}]).to_csv(os.path.join(H, f"deepdive_{pre}.csv"), index=False)
