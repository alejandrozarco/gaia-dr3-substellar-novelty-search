import json, warnings, urllib.request, numpy as np
warnings.filterwarnings("ignore")
from astropy.table import Table
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
s = Table.read("lane_m_below.fits")
# main-sequence G-W1 vs BP-RP (rough, from Pecaut & Mamajek-like colours): interpolate
cref = np.array([0.8, 1.0, 1.4, 1.8, 2.0, 2.3, 2.6, 2.9, 3.3, 3.8, 4.2]); gw = np.array([1.35, 1.7, 2.2, 2.65, 2.95, 3.45, 3.9, 4.35, 4.95, 5.6, 6.1])
exc = np.array(s["Gmag"]) - np.array(s["w1"]) - np.interp(np.array(s["BP-RP"]), cref, gw)
s["GW1_excess"] = exc
cons = s[(exc < 2.0)]
print(f"colour-consistent (G-W1 within +2 mag of the MS relation): {len(cons)} of {len(s)}")
sim = Simbad(); sim.add_votable_fields("otype", "ids")
def vsx(ra, dec, r=0.0028):
    url = f"https://vsx.aavso.org/index.php?view=api.list&ra={ra}&dec={dec}&radius={r}&format=json"
    j = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
    v = j.get("VSXObjects") or {}; o = v.get("VSXObject", []) if isinstance(v, dict) else []
    return [o] if isinstance(o, dict) else o
out = []
for r in cons:
    ra, de = float(r["RAJ2000"]), float(r["DEJ2000"])
    hv = vsx(ra, de, 0.0042)  # 15 arcsec
    try:
        st = sim.query_region(SkyCoord(ra*u.deg, de*u.deg), radius=10*u.arcsec)
        sname = "; ".join(f"{a} [{b}]" for a, b in zip(st["main_id"], st["otype"])) if st is not None and len(st) else "-"
    except Exception as e: sname = f"ERR {e}"
    vx = "; ".join(f"{h.get('Name')} [{h.get('VariabilityType')}, P={h.get('Period')}]" for h in hv) if hv else "-"
    print(f"{r['wise']} Gaia {r['Source']} G={r['Gmag']:.2f} BP-RP={r['BP-RP']:.2f} d={1000/r['Plx']:.0f}pc MG={r['MG']:.2f} dR={r['d_ridge']:+.2f} P={r['P']:.4f} ({r['P']*24:.2f} h) Wamp={r['amp']:.2f} W1={r['w1']:.2f} W1-W2={r['w1']-r['w2']:+.2f} GW1exc={r['GW1_excess']:+.2f}\n     VSX15: {vx}\n     SIMBAD10: {sname}")
    out.append(dict(wise=str(r["wise"]), gaia=str(r["Source"]), ra=ra, dec=de, G=float(r["Gmag"]), bprp=float(r["BP-RP"]), plx=float(r["Plx"]), MG=float(r["MG"]),
                    d_ridge=float(r["d_ridge"]), P=float(r["P"]), wamp=float(r["amp"]), w1=float(r["w1"]), w2=float(r["w2"]), vsx=vx, simbad=sname))
json.dump(out, open("lane_m_consistent.json", "w"), indent=1)
