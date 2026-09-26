# Hydrogen Balmer transitions in a magnetic field of arbitrary strength, from the Schimeczek & Wunner "Hydrogen Database"
# (DaRUS doi:10.18419/DARUS-2118; method: Schimeczek & Wunner 2014, Comp. Phys. Commun. 185, 614; ApJS 212, 26).
# Files: transitions/m_<mi>_to_<mf>/pi_z_<pi>_to_<pf>/nu_<i>_to_<f>.tsv with columns beta, transition energy [Ry],
# dipole strength, initial-state energy [Ry]; beta = B / 4.70103e9 G.
# Balmer lower states (n=2): 2s0 = (m 0, pi +1, nu 2); 2p0 = (m 0, pi -1, nu 1); 2p-1 = (m -1, pi +1, nu 1); 2p+1 = (m +1, pi +1, nu 1).
# pi transitions (dm=0) of 2p+-1 are identical in energy for +m/-m, the database lists them once (m_+1_to_+1).
# Wavelengths: vacuum, lambda = 911.7633 A / dE[Ry] (hydrogen Rydberg R_H, reproduces H-alpha 6564.7 A at B=0).
import glob, os, re, numpy as np
B0_G = 4.70103e9
LAM_RY = 911.7633
HERE = os.path.dirname(os.path.abspath(__file__))
LOWER = [("m_0_to_0/pi_z_+1_to_-1", 2), ("m_0_to_+1/pi_z_+1_to_+1", 2), ("m_0_to_-1/pi_z_+1_to_+1", 2),
         ("m_0_to_0/pi_z_-1_to_+1", 1), ("m_0_to_+1/pi_z_-1_to_-1", 1), ("m_0_to_-1/pi_z_-1_to_-1", 1),
         ("m_-1_to_0/pi_z_+1_to_+1", 1), ("m_-1_to_-2/pi_z_+1_to_+1", 1), ("m_+1_to_+1/pi_z_+1_to_-1", 1),
         ("m_+1_to_0/pi_z_+1_to_+1", 1), ("m_+1_to_+2/pi_z_+1_to_+1", 1)]
LOWER_NAME = {("m_0_to_0/pi_z_+1_to_-1", 2): "2s0", ("m_0_to_+1/pi_z_+1_to_+1", 2): "2s0", ("m_0_to_-1/pi_z_+1_to_+1", 2): "2s0",
              ("m_0_to_0/pi_z_-1_to_+1", 1): "2p0", ("m_0_to_+1/pi_z_-1_to_-1", 1): "2p0", ("m_0_to_-1/pi_z_-1_to_-1", 1): "2p0",
              ("m_-1_to_0/pi_z_+1_to_+1", 1): "2p-1", ("m_-1_to_-2/pi_z_+1_to_+1", 1): "2p-1", ("m_+1_to_+1/pi_z_+1_to_-1", 1): "2p+-1",
              ("m_+1_to_0/pi_z_+1_to_+1", 1): "2p+1", ("m_+1_to_+2/pi_z_+1_to_+1", 1): "2p+1"}

def load_balmer(root=os.path.join(HERE, "h2db", "transitions"), lam_min=3000.0, lam_max=12000.0):
    """Return list of dicts: name, B_MG (array), lam (array, vac A), S (dipole strength), f (~ dE*S, relative osc. strength)."""
    out = []
    for (d, nu) in LOWER:
        for fn in sorted(glob.glob(os.path.join(root, d, f"nu_{nu}_to_*.tsv"))):
            nf = int(re.search(r"_to_(\d+)\.tsv$", fn).group(1))
            a = np.loadtxt(fn, comments="#")
            if a.ndim != 2 or len(a) < 3: continue
            beta, dE, S = a[:, 0], a[:, 1], a[:, 2]
            ok = dE > 0.02
            if ok.sum() < 3: continue
            lam = np.full_like(dE, np.nan); lam[ok] = LAM_RY / dE[ok]
            if np.nanmax(lam) < lam_min or np.nanmin(lam) > lam_max: continue
            out.append(dict(name=f"{LOWER_NAME[(d, nu)]}->{d.split('/')[0].split('_to_')[1]}{d.split('/')[1].split('_to_')[1]}#{nf}",
                            dir=d, nu_i=nu, nu_f=nf, B_MG=beta * B0_G / 1e6, lam=lam, S=S, f=dE * S, lam0=lam[0]))
    return out

def on_grid(tr, Bgrid):
    """Interpolate every transition onto a common B grid (MG) -> arrays lam[ntr, nB], f[ntr, nB]."""
    L = np.full((len(tr), len(Bgrid)), np.nan); F = np.zeros_like(L)
    for i, t in enumerate(tr):
        m = np.isfinite(t["lam"])
        L[i] = np.interp(Bgrid, t["B_MG"][m], t["lam"][m], left=np.nan, right=np.nan)
        F[i] = np.interp(Bgrid, t["B_MG"][m], t["f"][m], left=0, right=0)
    return L, F

if __name__ == "__main__":
    tr = load_balmer()
    print(len(tr), "Balmer transitions loaded")
    Bg = np.array([0.0, 1.0, 10.0, 100.0, 300.0, 1000.0])
    L, F = on_grid(tr, Bg)
    # zero-field check and linear Zeeman check (H-alpha, 1 MG: expected +-4.67e-13*lam^2*B = +-20.1 A)
    i_ha = [i for i, t in enumerate(tr) if abs(t["lam0"] - 6564.7) < 3]
    print("H-alpha components at B=0:", np.round(L[i_ha, 0], 2), "\n  at 1 MG:", np.round(L[i_ha, 1], 1))
    for lab, l0 in (("Hbeta", 4862.7), ("Hgamma", 4341.7)):
        ii = [i for i, t in enumerate(tr) if abs(t["lam0"] - l0) < 3]
        print(lab, len(ii), "components; B=0 range", np.round(np.nanmin(L[ii, 0]), 2), np.round(np.nanmax(L[ii, 0]), 2))
