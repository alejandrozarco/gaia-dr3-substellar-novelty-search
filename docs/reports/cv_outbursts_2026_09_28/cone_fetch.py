"""For Gaia CV-region targets: ALeRCE ZTF cone search (3 arcsec), keep the nearest object, fetch its alert detections to lc/<oid>.csv.
Targets = the 63 unknowns + VSX stars in the region typed as non-CV. Output targets_oid.csv (source_id, oid, G, group); holes listed."""
import pandas as pd, requests, time, os, re
G = pd.read_csv("gaia_cvregion_gated.csv", dtype={"source_id": str}); os.makedirs("lc", exist_ok=True)
cv = lambda t: bool(re.search(r"UG|NL|\bAM\b|^AM|CV|^N[ABCR]?\b|ZAND|IBWD|DQ|VY|SW|UX", str(t).upper()))
unk = set(pd.read_csv("gaia_unknown.csv", dtype={"source_id": str}).source_id)
G["group"] = ["unknown" if s in unk else ("vsx_nonCV" if (pd.notna(t) and not cv(t) and not ic) else "") for s, t, ic in zip(G.source_id, G.vsx_type, G.in_cvlist)]
T = G[G.group != ""]; rows = []; holes = []
for r in T.itertuples():
    oid = None
    for k in range(3):
        try:
            j = requests.get("https://api.alerce.online/ztf/v1/objects", params=dict(ra=r.ra, dec=r.dec, radius=3, page_size=5), timeout=60).json()
            it = j.get("items", []); oid = it[0]["oid"] if it else ""; break
        except Exception: time.sleep(5)
    if oid is None: holes.append(r.source_id); continue
    if oid and not os.path.exists(f"lc/{oid}.csv"):
        try:
            d = pd.DataFrame(requests.get(f"https://api.alerce.online/ztf/v1/objects/{oid}/detections", timeout=120).json()); d.to_csv(f"lc/{oid}.csv", index=False)
        except Exception: holes.append(r.source_id)
    rows.append(dict(source_id=r.source_id, oid=oid, G=r.phot_g_mean_mag, group=r.group, vsx_type=r.vsx_type, ra=r.ra, dec=r.dec, range_g=r.range_mag_g_fov))
    time.sleep(0.3)
pd.DataFrame(rows).to_csv("targets_oid.csv", index=False); open("cone_holes.txt", "w").write("\n".join(holes))
print(len(T), "targets;", sum(1 for x in rows if x["oid"]), "with a ZTF alert object;", len(holes), "holes")
