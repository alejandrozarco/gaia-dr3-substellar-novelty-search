"""Vet the Lasair ZTF26 no-TNS transients with ALeRCE (2026-09-30).
Per object: ALeRCE cone 2 arcsec -> all ZTF object ids at the position and the earliest firstmjd among them (a 'new' object with an
older id at the same place is a recurring source); object stats (ndet, firstmjd, lastmjd); light-curve classifier (top class and
its probability) and stamp classifier; detections (drb, magpsf, fid, isdiffpos) -> number of negative-difference detections,
peak mag, rise and decline in days. Output: alerce_vet.csv."""
import json, time, requests, pandas as pd, numpy as np
A = "https://api.alerce.online/ztf/v1"
def get(url, params=None):
    for k in range(4):
        try:
            r = requests.get(url, params=params, timeout=90)
            if r.status_code == 200: return r.json()
            if r.status_code == 404: return None
        except Exception: pass
        time.sleep(10 * (k + 1))
    return "HOLE"
U = [x for x in json.load(open("no_tns.json")) if x["objectId"].startswith("ZTF26")]; rows = []
for x in U:
    o = x["objectId"]; r = dict(oid=o, ra=x["ramean"], dec=x["decmean"], sherlock=x["classification"], sep=x["separationArcsec"], cat=x["catalogue_table_name"], photoz=x["photoZ"], z=x["z"])
    cone = get(f"{A}/objects", dict(ra=x["ramean"], dec=x["decmean"], radius=2, page_size=50))
    if cone == "HOLE" or cone is None: r["cone"] = "HOLE"
    else:
        items = cone.get("items", []); r["n_oids"] = len(items); r["oids"] = ";".join(i["oid"] for i in items)
        r["first_any"] = min(i["firstmjd"] for i in items) if items else np.nan
    ob = get(f"{A}/objects/{o}")
    if isinstance(ob, dict): r.update(firstmjd=ob.get("firstmjd"), lastmjd=ob.get("lastmjd"), ndet=ob.get("ndethist"), stellar=ob.get("stellar"))
    pr = get(f"{A}/objects/{o}/probabilities")
    if isinstance(pr, list):
        for clf in ("lc_classifier", "stamp_classifier"):
            p = [q for q in pr if q["classifier_name"].startswith(clf) and q.get("ranking") == 1]
            if p: r[clf] = f'{p[0]["class_name"]} {p[0]["probability"]:.2f}'
        top = [q for q in pr if q["classifier_name"] == "lc_classifier" and q.get("ranking") == 1]
    det = get(f"{A}/objects/{o}/detections")
    if isinstance(det, list) and det:
        d = pd.DataFrame(det); r["n_neg"] = int((d.isdiffpos.astype(str).isin(["-1", "f", "False"])).sum()); r["drb_med"] = float(d.drb.median()) if "drb" in d else np.nan
        pk = d.loc[d.magpsf.idxmin()]; r.update(peak_mag=float(pk.magpsf), peak_fid=int(pk.fid), t_peak=float(pk.mjd), rise_d=float(pk.mjd - d.mjd.min()), after_peak_d=float(d.mjd.max() - pk.mjd), ndet_alerts=len(d))
    rows.append(r); print(r, flush=True); time.sleep(1)
pd.DataFrame(rows).to_csv("alerce_vet.csv", index=False); print("DONE", flush=True)
