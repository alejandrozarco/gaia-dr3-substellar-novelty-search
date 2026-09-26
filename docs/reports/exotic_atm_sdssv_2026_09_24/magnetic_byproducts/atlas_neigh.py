# ATLAS forced photometry at the positions of the three Gaia neighbours within 14" of Gaia DR3 6021870154194477312; amplitude of a sinusoid at
# 13.929771 c/d per band (same cuts as atlas_6021.py). Token read from ~/.config/atlas/token (never printed).
import os, time, requests, numpy as np, io, pandas as pd
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
BASE = "https://fallingstar-data.com/forcedphot"; H = {"Authorization": "Token " + open(os.path.expanduser("~/.config/atlas/token")).read().strip(), "Accept": "application/json"}
ids = ["6021870154194477312", "6021870158500230656", "6021870154194477696", "6021870158500371840"]
g = pd.read_csv(io.StringIO(requests.post("https://gea.esac.esa.int/tap-server/tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY="SELECT source_id, ra, dec, phot_g_mean_mag FROM gaiadr3.gaia_source WHERE source_id IN (" + ",".join(ids) + ")"), timeout=120).text), dtype={"source_id": str}).set_index("source_id")
f1 = 13.929771; geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
def get(ra, de, fn):
    if os.path.exists(fn): return open(fn).read()
    url = None
    for k in range(6):
        r = requests.post(f"{BASE}/queue/", headers=H, data={"ra": ra, "dec": de, "mjd_min": 57000.0, "send_email": False}, timeout=60)
        if r.status_code == 201: url = r.json()["url"]; break
        time.sleep(30)
    for k in range(240):
        j = requests.get(url, headers=H, timeout=60).json()
        if j.get("finishtimestamp"):
            txt = requests.get(j["result_url"], headers=H, timeout=120).text if j.get("result_url") else ""; requests.delete(url, headers=H, timeout=60); open(fn, "w").write(txt); return txt
        time.sleep(10)
    return ""
for gid in ids:
    r = g.loc[gid]; fn = f"atlas_{gid}.txt" if gid != "6021870154194477312" else "atlas_6021_gaiapos.txt"
    txt = get(r.ra, r.dec, fn); L = [l for l in txt.splitlines() if l.strip()]
    if len(L) < 10: print(gid, "HOLE/empty"); continue
    hdr = L[0].lstrip("#").split(); R = [dict(zip(hdr, l.split())) for l in L[1:]]
    ok = [x for x in R if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]; out = []
    for b in ("o", "c"):
        s = [x for x in ok if x["F"] == b]; med = np.median([float(x["duJy"]) for x in s]); s = [x for x in s if float(x["duJy"]) < 3 * med]
        mjd = np.array([float(x["MJD"]) for x in s]); f = np.array([float(x["uJy"]) for x in s]); e = np.array([float(x["duJy"]) for x in s])
        season = np.floor((mjd - 57000) / 365.25 + 0.3).astype(int)
        for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
        clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e); c0 = SkyCoord(r.ra * u.deg, r.dec * u.deg)
        tt = Time(mjd[clip], format="mjd", scale="utc", location=geo); t = (tt.tdb + tt.light_travel_time(c0)).jd; y = f[clip]; ee = e[clip]
        X = np.vstack([np.ones_like(t), np.sin(2*np.pi*f1*t), np.cos(2*np.pi*f1*t)]).T; W = 1/ee**2
        bb = np.linalg.solve(X.T @ (X*W[:, None]), X.T @ (W*y)); C = np.linalg.inv(X.T @ (X*W[:, None]))
        out.append(f"{b}: n {clip.sum()}, amp {np.hypot(bb[1], bb[2]):.1f} +- {np.sqrt((C[1,1]+C[2,2])/2):.1f} uJy, phase {np.degrees(np.arctan2(bb[2], bb[1])) % 360:.0f} deg")
    sep = 3600 * np.hypot((r.ra - g.loc[ids[0]].ra) * np.cos(np.radians(r.dec)), r.dec - g.loc[ids[0]].dec)
    print(f"{gid} G {r.phot_g_mean_mag:.2f} sep {sep:.1f}\": " + " | ".join(out), flush=True)
