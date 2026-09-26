import json, csv, io, math, subprocess, time, numpy as np
from astropy.table import Table
from astropy.timeseries import LombScargle, BoxLeastSquares
br = json.load(open("bridge_known.json"))
SPECIAL = ("VSX", "Ritter", "Downes", "Schwope", "SDSS-DR20", "Li+2025", "GF21", "CataclyV", "WhiteDwarf", "Nova", "XrayBin", "EmLine")
pool = [o for o in br if not any(any(s in k for s in SPECIAL) for k in o["known"])]
north = [o for o in pool if o["dec"] > -28]
print(f"novelty pool {len(pool)} (no VSX/CV/WD/emission-line identification); ZTF-reachable {len(north)}", flush=True)
for i, o in enumerate(north): o["tid"] = i
Table(dict(tid=[o["tid"] for o in north], ra=[o["ra"] for o in north], dec=[o["dec"] for o in north])).write("up_north.xml", format="votable", overwrite=True)
Q = ("SELECT u.tid, o.oid, o.filtercode FROM ztf_objects_dr24 o, TAP_UPLOAD.t u WHERE CONTAINS(POINT('ICRS',o.ra,o.dec),"
     "CIRCLE('ICRS',u.ra,u.dec,0.000694))=1 AND (o.filtercode='zg' OR o.filtercode='zr')")
p = subprocess.run(["curl", "-s", "--max-time", "900", "-F", "REQUEST=doQuery", "-F", "LANG=ADQL", "-F", "FORMAT=csv", "-F", "UPLOAD=t,param:tbl",
                    "-F", "tbl=@up_north.xml", "-F", f"QUERY={Q}", "https://irsa.ipac.caltech.edu/TAP/sync"], capture_output=True, text=True)
assert p.stdout.startswith("tid,oid"), p.stdout[:300]
X = {}
for r in csv.DictReader(io.StringIO(p.stdout)): X.setdefault(int(r["tid"]), []).append(r["oid"])
print(f"ZTF objects for {len(X)} of {len(north)}", flush=True)
res = []
for o in north:
    oids = X.get(o["tid"], [])
    if not oids: o["ztf"] = "NO_ZTF"; res.append(o); continue
    url = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?" + "&".join(f"ID={x}" for x in oids) + "&BAD_CATFLAGS_MASK=32768&FORMAT=CSV"
    rows = None
    for k in range(4):
        q = subprocess.run(["curl", "-sL", "--max-time", "600", url], capture_output=True, text=True)
        if q.stdout.startswith("oid"): rows = list(csv.DictReader(io.StringIO(q.stdout))); break
        time.sleep(8 * (k + 1))
    if rows is None: o["ztf"] = "HOLE"; res.append(o); continue
    rows = [x for x in rows if x["catflags"] == "0" and abs(float(x["sharp"])) < 0.5 and float(x["mag"]) < float(x["limitmag"]) - 0.3]
    t = np.array([float(x["hjd"]) for x in rows]); m = np.array([float(x["mag"]) for x in rows]); e = np.array([float(x["magerr"]) for x in rows])
    ob = np.array([x["oid"] for x in rows]); b = np.array([x["filtercode"] for x in rows])
    for q_ in set(ob): m[ob == q_] -= np.median(m[ob == q_])
    o["ztf"] = "OK"; o["n"] = {bb: int((b == bb).sum()) for bb in ("zg", "zr")}; o["bands"] = {}
    for bb in ("zg", "zr"):
        s = b == bb
        if s.sum() < 50: continue
        ls = LombScargle(t[s], m[s], e[s]); f, pw = ls.autopower(minimum_frequency=0.05, maximum_frequency=48, samples_per_peak=10)
        k = int(np.argmax(pw)); f0 = f[k]; fap = float(ls.false_alarm_probability(pw[k], minimum_frequency=0.05, maximum_frequency=48))
        al = max(float(ls.power(np.linspace(f0 + d - 3e-4, f0 + d + 3e-4, 61)).max()) for d in (-1.00274, -1.0, 1.0, 1.00274) if f0 + d > 0.01)
        ph = (t[s] * f0) % 1; bins = np.array([np.median(m[s][(ph >= j / 12) & (ph < (j + 1) / 12)]) for j in range(12)])
        o["bands"][bb] = dict(P=round(1 / f0, 7), power=round(float(pw[k]), 3), alias=round(al, 3), fap=fap, amp=round(float(np.nanmax(bins) - np.nanmin(bins)), 3),
                              rms=round(float(1.4826 * np.median(np.abs(m[s]))), 3), near_day=bool(abs(1 / f0 - 1) < 0.03 or abs(1 / f0 - 0.5) < 0.01 or 1 / f0 > 15))
    bb = o["bands"]
    good = [v for v in bb.values() if v["fap"] < 1e-8 and not v["near_day"] and v["power"] > v["alias"]]
    agree = len(bb) == 2 and abs(bb["zg"]["P"] - bb["zr"]["P"]) / bb["zg"]["P"] < 3e-4
    o["verdict"] = "COHERENT_2BAND" if (agree and len(good) == 2) else ("COHERENT_1BAND" if good else "none")
    res.append(o)
    if o["verdict"] != "none":
        print(f"  {o['verdict']:15s} {o['sid']} {o['name']} G={o['G']:.2f} M_G={o['MG']:.2f} dRidge={o['d_ridge']:+.2f} eRASS1={o['in_erass1']} | " +
              " ".join(f"{k}: P={v['P']} d ({v['P']*24:.3f} h) pow {v['power']}/{v['alias']} amp {v['amp']}" for k, v in bb.items()) + f" | known: {o['known']}", flush=True)
json.dump(res, open("ztf_screen.json", "w"), indent=0, default=str)
print("ZTF_SCREEN_DONE", sum(o.get("verdict") == "COHERENT_2BAND" for o in res), "two-band,", sum(o.get("verdict") == "COHERENT_1BAND" for o in res), "one-band,",
      sum(o.get("ztf") == "NO_ZTF" for o in res), "no ZTF,", sum(o.get("ztf") == "HOLE" for o in res), "holes", flush=True)
