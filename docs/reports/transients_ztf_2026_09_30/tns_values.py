"""TNS AT-report values for the unreported Galactic outbursts (2026-09-30): position (ALeRCE mean, sexagesimal), discovery = first
ZTF alert detection (UT, magpsf +- sigmapsf, filter), last ZTF non-detection before it (UT, diffmaglim, filter), and a second
detection. Output: tns_values.md."""
import requests, pandas as pd
from astropy.time import Time; from astropy.coordinates import SkyCoord; import astropy.units as u
A = "https://api.alerce.online/ztf/v1"; F = {1: "g-ZTF", 2: "r-ZTF", 3: "i-ZTF"}; out = []
for o in ("ZTF26absimmf", "ZTF26abwacec", "ZTF26abtpoev", "ZTF26abwqsgt", "ZTF26abtoqyd"):
    ob = requests.get(f"{A}/objects/{o}", timeout=60).json(); d = pd.DataFrame(requests.get(f"{A}/objects/{o}/detections", timeout=60).json()).sort_values("mjd")
    n = pd.DataFrame(requests.get(f"{A}/objects/{o}/non_detections", timeout=60).json()); d = d[d.isdiffpos.astype(str).isin(["1", "t", "True"])]
    c = SkyCoord(ob["meanra"] * u.deg, ob["meandec"] * u.deg); s = c.to_string("hmsdms", sep=":", precision=3).split()
    f0 = d.iloc[0]; f1 = d.iloc[1]; ln = n[n.mjd < f0.mjd].sort_values("mjd").iloc[-1]
    t = lambda m: Time(m, format="mjd").iso[:19]
    out.append(f"### {o}\n- RA {s[0]}  Dec {s[1][:-1] if s[1].endswith('0') and False else s[1]}  (deg {ob['meanra']:.6f}, {ob['meandec']:.6f})\n- Discovery: {t(f0.mjd)} UT, {f0.magpsf:.2f} +- {f0.sigmapsf:.2f}, {F[int(f0.fid)]}, P48 - ZTF-Cam\n- Second detection: {t(f1.mjd)} UT, {f1.magpsf:.2f} +- {f1.sigmapsf:.2f}, {F[int(f1.fid)]}\n- Last non-detection: {t(ln.mjd)} UT, > {ln.diffmaglim:.2f}, {F[int(ln.fid)]}\n- Brightest: {d.magpsf.min():.2f} ({F[int(d.loc[d.magpsf.idxmin(), 'fid'])]}), detections {len(d)}, last {t(d.mjd.max())}\n")
open("tns_values.md", "w").write("\n".join(out)); print("\n".join(out))
