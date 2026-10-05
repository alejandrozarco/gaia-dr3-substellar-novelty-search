"""Archival search for Galactic outbursts hidden among ALeRCE 'supernova' classifications (2026-09-30).
All ZTF objects whose ALeRCE light-curve classifier ranks SNIa, SNII, SNIbc or SLSN first (probability >= 0.4) and >= 5 detections
are paged (1000 per request, all pages; a failed page is retried 4x and then recorded in sn_plane_holes.txt). Kept: |b| < 15 deg.
Output: sn_plane_all.csv (all kept objects with ALeRCE stats)."""
import requests, time, pandas as pd, numpy as np, os, astropy.units as u
from astropy.coordinates import SkyCoord
A = "https://api.alerce.online/ztf/v1/objects"; rows = []; holes = []
for cls in ("SNIa", "SNII", "SNIbc", "SLSN"):
    page = 1
    while True:
        js = None
        for k in range(4):
            try:
                r = requests.get(A, params=dict(classifier="lc_classifier", class_name=cls, ranking=1, probability=0.4, ndet=[5, 100000], page_size=1000, page=page, count="false"), timeout=180)
                if r.ok: js = r.json(); break
            except Exception: pass
            time.sleep(15 * (k + 1))
        if js is None: holes.append(f"{cls} page {page}"); page += 1; continue
        it = js.get("items", [])
        if not it: break
        for x in it: rows.append(dict(oid=x["oid"], cls=cls, prob=x.get("probability"), ra=x["meanra"], dec=x["meandec"], ndet=x["ndet"], firstmjd=x["firstmjd"], lastmjd=x["lastmjd"], stellar=x.get("stellar")))
        print(cls, page, len(it), len(rows), flush=True)
        if len(it) < 1000: break
        page += 1
D = pd.DataFrame(rows).drop_duplicates("oid"); b = SkyCoord(D.ra.values * u.deg, D.dec.values * u.deg).galactic.b.deg; D["b"] = b
D[np.abs(D.b) < 15].to_csv("sn_plane_all.csv", index=False); open("sn_plane_holes.txt", "w").write("\n".join(holes))
print("total", len(D), "plane", int((np.abs(D.b) < 15).sum()), "holes", len(holes), flush=True)
