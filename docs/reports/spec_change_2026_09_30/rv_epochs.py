"""Absolute Balmer-core velocities and epochs of the SDSS/DESI spectra of the radial-velocity candidates (2026-09-30).
Velocity per spectrum = inverse-variance mean over lines of c (mu / lambda_vac - 1) from rv_fit_spectra.csv (vacuum, barycentric
frames of both pipelines; includes the white dwarf's gravitational redshift). SDSS epochs from SPARCL metadata (mjd).
Usage (SPARCL client required): python rv_epochs.py <gaia> [...] -> printed table."""
import sys, pandas as pd, numpy as np, os
from sparcl.client import SparclClient
H = os.path.dirname(os.path.abspath(__file__)); C = 299792.458; L = {"Ha": 6564.61, "Hb": 4862.68, "Hg": 4341.69}
F = pd.read_csv(os.path.join(H, "results", "rv_fit_spectra.csv"), dtype={"gaia": str}); cl = SparclClient(connect_timeout=30, read_timeout=300)
for g in sys.argv[1:]:
    for r in F[F.gaia == g].itertuples():
        vs = {k: (C * (getattr(r, f"mu_{k}") / l - 1), C * getattr(r, f"e_{k}") / l) for k, l in L.items() if np.isfinite(getattr(r, f"mu_{k}"))}
        w = np.array([1 / e**2 for v, e in vs.values()]); v = np.array([v for v, e in vs.values()]); vm = (w * v).sum() / w.sum(); ev = 1 / np.sqrt(w.sum())
        if r.spec.startswith("S:"):
            try: res = cl.find(outfields=["sparcl_id", "mjd", "data_release"], constraints={"sparcl_id": [r.spec[2:]]}); ep = f"{res.records[0]['data_release']} MJD {res.records[0]['mjd']}"
            except Exception as ex: ep = "epoch HOLE"
        else: ep = "DESI DR1 coadd"
        print(g, r.spec[:14], ep, "| lines", {k: f"{a:.0f}+-{b:.0f}" for k, (a, b) in vs.items()}, "| mean %.0f +- %.0f km/s" % (vm, ev), flush=True)
