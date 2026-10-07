"""Discovery values per candidate from ALeRCE (2026-10-01): mean position (deg + sexagesimal), first positive detection
(UT, MJD, magpsf+-sigma, filter), all detections, last non-detection before discovery and the deepest limit in the 5 d before.
Output: disc_values.md. Usage: python disc_values.py oid [...]"""
import sys, requests, pandas as pd
from astropy.time import Time; from astropy.coordinates import SkyCoord; import astropy.units as u
A = "https://api.alerce.online/ztf/v1"; F = {1: "g", 2: "r", 3: "i"}; out = []; t = lambda m: Time(m, format="mjd").iso[:19]
for o in sys.argv[1:]:
    ob = requests.get(f"{A}/objects/{o}", timeout=60).json(); d = pd.DataFrame(requests.get(f"{A}/objects/{o}/detections", timeout=60).json()).sort_values("mjd")
    n = pd.DataFrame(requests.get(f"{A}/objects/{o}/non_detections", timeout=60).json()); d = d[d.isdiffpos.astype(str).isin(["1", "t", "True"])]
    c = SkyCoord(ob["meanra"] * u.deg, ob["meandec"] * u.deg); s = c.to_string("hmsdms", sep=":", precision=2).split()
    f0 = d.iloc[0]; L = [f"### {o}", f"- RA {s[0]} Dec {s[1]} (deg {ob['meanra']:.6f} {ob['meandec']:.6f}); l,b = {c.galactic.l.deg:.2f}, {c.galactic.b.deg:.2f}",
        f"- Discovery (first ZTF alert detection): {t(f0.mjd)} UT (MJD {f0.mjd:.5f}), ZTF-{F[int(f0.fid)]} {f0.magpsf:.2f} +- {f0.sigmapsf:.2f}"]
    L.append("- Detections: " + "; ".join(f"MJD {r.mjd:.4f} {F[int(r.fid)]} {r.magpsf:.2f}+-{r.sigmapsf:.2f} drb {r.drb:.3f}" for r in d.itertuples()))
    if len(n):
        b = n[n.mjd < f0.mjd].sort_values("mjd")
        if len(b):
            ln = b.iloc[-1]; L.append(f"- Last non-detection: {t(ln.mjd)} UT (MJD {ln.mjd:.5f}), ZTF-{F[int(ln.fid)]} > {ln.diffmaglim:.2f}")
            b5 = b[b.mjd > f0.mjd - 5]
            if len(b5): dp = b5.loc[b5.diffmaglim.idxmax()]; L.append(f"- Deepest limit within 5 d before: {t(dp.mjd)} UT, ZTF-{F[int(dp.fid)]} > {dp.diffmaglim:.2f}")
        else: L.append("- Last non-detection: none in the alert history (no ZTF visit in the preceding ~30 d)")
    else: L.append("- Last non-detection: none in the alert history (no ZTF visit in the preceding ~30 d)")
    out.append("\n".join(L) + "\n")
open("disc_values.md", "w").write("\n".join(out)); print("\n".join(out))
