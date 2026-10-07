"""Detections for every ALeRCE fresh object (alerce_fresh.csv), 6 threads; failures recorded as HOLE (never as empty).
Output: dets.parquet-like CSV (dets_all.csv) and det_holes.txt"""
import requests, time, pandas as pd
from concurrent.futures import ThreadPoolExecutor
A = "https://api.alerce.online/ztf/v1"; d = pd.read_csv("alerce_fresh.csv")
def get(o):
    for k in range(4):
        try:
            r = requests.get(f"{A}/objects/{o}/detections", timeout=90)
            if r.ok: return o, r.json()
        except Exception: pass
        time.sleep(5 * (k + 1))
    return o, "HOLE"
rows, holes = [], []
with ThreadPoolExecutor(6) as ex:
    for i, (o, js) in enumerate(ex.map(get, d.oid)):
        if js == "HOLE" or not isinstance(js, list): holes.append(o); continue
        for x in js: x["oid"] = o; rows.append(x)
        if i % 200 == 0: print(i, flush=True)
D = pd.DataFrame(rows); D.to_csv("dets_all.csv", index=False); open("det_holes.txt", "w").write("\n".join(holes))
print("rows", len(D), "objects", D.oid.nunique(), "holes", len(holes)); print(D.columns.tolist())
