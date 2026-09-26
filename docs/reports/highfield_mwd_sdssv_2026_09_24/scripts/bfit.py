# Crude field estimator for magnetic DA white dwarfs: centred-dipole field distribution x Schimeczek & Wunner Balmer
# transition data (wavelengths, dipole strengths, initial-state energies vs B; DaRUS-2118) -> opacity template per Balmer
# series; the normalised spectrum is fitted as ln F = poly(lambda) - sum_s A_s tau_s(lambda) (linear least squares, A_s >= 0)
# over a grid of polar field Bp, inclination i and intrinsic line width sigma.  This is NOT a radiative-transfer model:
# it gives a field RANGE and tests whether a hydrogen-in-B pattern explains the features at all (chi2 vs a no-field model).
# Angular factors: pi components ~ sin^2(psi), sigma components ~ (1+cos^2 psi)/2, psi = angle(B, line of sight).
# Lower-level populations: Boltzmann factor on the initial-state energy (kT from the photometric Teff).
import numpy as np, re, glob, os
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import nnls
import hfield as H
KT_RY_PER_K = 8.617333e-5 / 13.605693
LG = np.arange(3500.0, 10000.0, 2.0)            # opacity wavelength grid (vacuum A)

def _load():
    out = []
    for (d, nu) in H.LOWER:
        mi, mf = [int(x) for x in re.match(r"m_([+-]?\d+)_to_([+-]?\d+)", d).groups()]
        kind = "pi" if mi == mf else "sigma"
        for fn in sorted(glob.glob(os.path.join(H.HERE, "h2db", "transitions", d, f"nu_{nu}_to_*.tsv"))):
            a = np.loadtxt(fn, comments="#")
            if a.ndim != 2 or len(a) < 3: continue
            beta, dE, S, Ei = a.T
            ok = dE > 0.02
            if ok.sum() < 3: continue
            lam = H.LAM_RY / dE[ok]
            if lam.max() < 3500 or lam.min() > 10000: continue
            l0 = lam[0]
            n_up = min(range(3, 16), key=lambda n: abs(l0 - H.LAM_RY / (0.25 - 1 / n**2)))
            out.append(dict(B=beta[ok] * H.B0_G / 1e6, lam=lam, f=dE[ok] * S[ok], Ei=Ei[ok], kind=kind, n_up=n_up))
            if d.startswith("m_+1_to_+1"):
                # the database lists the pi transitions of 2p(+-1) once, with the initial energy of the LOWER (m=+1 in the
                # file convention) state; the mirror (m=-1) state has the same transition energies and strengths and an
                # initial energy higher by 4*beta Ry (checked against the sigma files, 2026-09-24) -> add it explicitly
                out.append(dict(B=beta[ok] * H.B0_G / 1e6, lam=lam, f=dE[ok] * S[ok], Ei=Ei[ok] + 4 * beta[ok], kind=kind, n_up=n_up))
    return out
TR = _load()
BG = np.concatenate([np.linspace(0.0, 2, 41)[1:], np.logspace(np.log10(2.05), np.log10(1500), 500)])   # MG
LAMG = np.full((len(TR), len(BG)), np.nan); FG = np.zeros_like(LAMG); EG = np.zeros_like(LAMG)
for k, t in enumerate(TR):
    LAMG[k] = np.interp(BG, t["B"], t["lam"], left=np.nan, right=np.nan)
    FG[k] = np.interp(BG, t["B"], t["f"], left=0, right=0)
    EG[k] = np.interp(BG, t["B"], t["Ei"], left=np.nan, right=np.nan)
KIND = np.array([t["kind"] for t in TR]); NUP = np.array([t["n_up"] for t in TR])
GROUP = np.where(NUP == 3, 0, np.where(NUP == 4, 1, np.where(NUP == 5, 2, 3)))     # Ha, Hb, Hg, Hd+
PMW = np.ones(len(TR))

def surface(Bp, inc_deg, n=24):
    """Visible-hemisphere sampling of a centred dipole: returns field strengths (MG), cos psi, weights."""
    mu = (np.arange(n) + 0.5) / n; ph = (np.arange(2 * n) + 0.5) / (2 * n) * 2 * np.pi
    MU, PH = np.meshgrid(mu, ph, indexing="ij"); st = np.sqrt(1 - MU**2)
    x, y, z = st * np.cos(PH), st * np.sin(PH), MU          # z = line of sight
    i = np.radians(inc_deg); mx, my, mz = np.sin(i), 0.0, np.cos(i)
    mdotr = mx * x + my * y + mz * z
    Bx, By, Bz = (3 * mdotr * x - mx) * Bp / 2, (3 * mdotr * y - my) * Bp / 2, (3 * mdotr * z - mz) * Bp / 2
    Bm = np.sqrt(Bx**2 + By**2 + Bz**2); cpsi = np.abs(Bz) / np.maximum(Bm, 1e-9)
    w = MU * (1 - 0.5 + 0.5 * MU)                            # projected area x linear limb darkening (u=0.5)
    return Bm.ravel(), cpsi.ravel(), (w / w.sum()).ravel()

def templates(Bp, inc, sigA, teff):
    Bm, cpsi, w = surface(Bp, inc)
    ib = np.clip(np.searchsorted(BG, Bm), 1, len(BG) - 1)
    lam = LAMG[:, ib]; f = FG[:, ib]; Ei = EG[:, ib]
    Emin = np.nanmin(np.where(NUP[:, None] >= 3, Ei, np.nan), axis=0)
    boltz = np.exp(-(Ei - Emin[None, :]) / (KT_RY_PER_K * teff))
    ang = np.where(KIND[:, None] == "pi", 1 - cpsi[None, :]**2, (1 + cpsi[None, :]**2) / 2)
    wt = f * boltz * ang * w[None, :] * PMW[:, None]
    T = np.zeros((4, len(LG)))
    ok = np.isfinite(lam) & np.isfinite(wt)
    idx = np.clip(((lam - LG[0]) / 2.0).astype(int), 0, len(LG) - 1)
    for g in range(4):
        m = ok & (GROUP[:, None] == g) & (lam > LG[0]) & (lam < LG[-1])
        T[g] = np.bincount(idx[m], weights=wt[m], minlength=len(LG))
        T[g] = gaussian_filter1d(T[g], sigA / 2.0)
        if T[g].max() > 0: T[g] /= T[g].max()
    return T

def fit(lam, fnorm, err, teff, Bps=None, incs=(0, 30, 60, 90), sigs=(8, 16, 30), npoly=4, mask=None, lo=3800, hi=9000):
    """Returns dict with chi2 grid, best parameters, best model, and the no-field (B=0) comparison."""
    if Bps is None: Bps = np.logspace(np.log10(1.0), np.log10(1200), 90)
    m = (lam > lo) & (lam < hi) & np.isfinite(fnorm) & (fnorm > 0.05) & (err > 0) & np.isfinite(err)
    if mask is not None: m &= mask
    x = lam[m]; y = np.log(fnorm[m]); sy = err[m] / fnorm[m]; W = 1 / sy
    xs = (x - 6000) / 3000; P = np.vstack([xs**k for k in range(npoly)]).T
    best = (np.inf,); grid = np.full((len(Bps), len(incs), len(sigs)), np.nan)
    for a, Bp in enumerate(Bps):
        for b, inc in enumerate(incs):
            for c, sg in enumerate(sigs):
                T = templates(Bp, inc, sg, teff)
                Ti = np.array([np.interp(x, LG, T[g]) for g in range(4)]).T
                A = np.hstack([-Ti, P, -P])                     # A_s >= 0 for templates; poly coeffs via +/- split
                coef, rn = nnls(A * W[:, None], y * W)
                chi2 = rn**2; grid[a, b, c] = chi2
                if chi2 < best[0]: best = (chi2, Bp, inc, sg, coef)
    # no-field reference: polynomial only
    cp, *_ = np.linalg.lstsq(P * W[:, None], y * W, rcond=None); chi0 = np.sum(((y - P @ cp) * W) ** 2)
    chi2, Bp, inc, sg, coef = best
    T = templates(Bp, inc, sg, teff); Ti = np.array([np.interp(lam, LG, T[g]) for g in range(4)]).T
    Pl = np.vstack([((lam - 6000) / 3000)**k for k in range(npoly)]).T
    model = np.exp(-Ti @ coef[:4] + Pl @ (coef[4:4 + npoly] - coef[4 + npoly:]))
    return dict(grid=grid, Bps=np.array(Bps), incs=incs, sigs=sigs, chi2=chi2, chi2_nofield=chi0, npix=int(m.sum()),
                Bp=Bp, inc=inc, sig=sg, A=coef[:4], model=model, used=m)
