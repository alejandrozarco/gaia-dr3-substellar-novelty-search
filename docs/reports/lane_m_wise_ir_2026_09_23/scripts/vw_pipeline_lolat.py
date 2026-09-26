# Automated IR-vs-optical amplitude screen: VarWISE below-MS variables NOT covered by the 2026-09-23 high-latitude run (|b| <= 10 deg, plus 24 |b| > 10 deg rows that met the documented cuts but were absent from vw_hilat.csv). Cuts: plx/e_plx > 5, W1 amp > 0.15, below-ridge + p99 envelope, G-W1 consistent, not blended/latent.
# Output: vw_pipeline_lolat.jsonl (one line per target; status OK / HOLE_* recorded, never silently dropped)
import io, csv, json, time, subprocess, warnings, threading, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
warnings.filterwarnings("ignore")
from astropy.timeseries import LombScargle
from astropy.table import Table
from astroquery.xmatch import XMatch
import astropy.units as u
s = pd.read_csv("vw_lolat.csv")
up = Table.from_pandas(s[["designation", "ra", "dec", "gmag"]])
x = XMatch.query(cat1=up, cat2="vizier:I/355/gaiadr3", max_distance=3*u.arcsec, colRA1="ra", colDec1="dec").to_pandas()
x["dG"] = np.abs(x["Gmag"] - x["gmag"]); x = x.sort_values(["designation", "dG"]).drop_duplicates("designation")
x = x[x.dG < 0.3]
print("targets with a Gaia match (|dG|<0.3):", len(x), "of", len(s), flush=True)
done = set()
try:
    for l in open("vw_pipeline_lolat.jsonl"): done.add(json.loads(l)["designation"])
except FileNotFoundError: pass
lock = threading.Lock()
def tap(q):
    for k in range(4):
        p = subprocess.run(["curl", "-s", "--max-time", "600", "--data-urlencode", f"QUERY={q}", "--data-urlencode", "FORMAT=csv", "--data-urlencode", "LANG=ADQL",
                            "--data-urlencode", "REQUEST=doQuery", "https://irsa.ipac.caltech.edu/TAP/sync"], capture_output=True, text=True)
        if p.stdout.startswith("mjd"): return list(csv.DictReader(io.StringIO(p.stdout)))
        time.sleep(10 * (k + 1))
    return None
def amp(t, m, e, f):
    X = np.column_stack([np.ones_like(t), np.sin(2*np.pi*f*t), np.cos(2*np.pi*f*t)]); w = 1/e**2; C = np.linalg.inv(X.T @ (X*w[:, None])); p = C @ (X.T @ (m*w))
    r = m - X @ p; s2 = np.sum(r**2*w)/max(1, len(t)-3); a = np.hypot(p[1], p[2]); ea = np.sqrt(s2*(C[1,1]*p[1]**2 + C[2,2]*p[2]**2)/max(a**2, 1e-12))
    return float(2*a), float(2*ea)
def work(r):
    des = r["designation"]; ra0, de0 = float(r["RAdeg"]), float(r["DEdeg"]); pmra = float(r["pmRA"]) if np.isfinite(r["pmRA"]) else 0.0; pmde = float(r["pmDE"]) if np.isfinite(r["pmDE"]) else 0.0
    out = dict(designation=des, gaia=str(int(r["Source"])), ra=ra0, dec=de0, G=float(r["Gmag"]), bprp=float(r["BP-RP"]), plx=float(r["Plx"]))
    rows = tap(f"SELECT mjd, ra, dec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, qual_frame, qi_fact, saa_sep, moon_masked, cc_flags, nb, na FROM neowiser_p1bs_psd "
               f"WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{ra0},{de0},{5/3600}))=1")
    if rows is None: out["status"] = "HOLE_WISE"; return out
    T = []
    for q in rows:
        try:
            yr = (float(q["mjd"]) - 57388.0)/365.25; rap = ra0 + pmra*yr/3.6e6/np.cos(np.radians(de0)); dep = de0 + pmde*yr/3.6e6
            if np.hypot((float(q["ra"]) - rap)*np.cos(np.radians(de0)), float(q["dec"]) - dep)*3600 > 3: continue
            if not (float(q["qual_frame"]) > 0 and float(q["qi_fact"]) > 0 and float(q["saa_sep"]) > 0 and q["moon_masked"][0] == "0" and q["cc_flags"][0] == "0" and q["nb"] == "1" and q["na"] == "0"): continue
            T.append((float(q["mjd"]) + 2400000.5, float(q["w1mpro"]), float(q["w1sigmpro"]), float(q["w2mpro"]) if q["w2mpro"] else np.nan, float(q["w2sigmpro"]) if q["w2sigmpro"] else np.nan))
        except ValueError: pass
    if len(T) < 40: out["status"] = f"FEW_WISE_{len(T)}"; return out
    T = np.array(T); t, w1, e1, w2, e2 = T.T
    ls = LombScargle(t, w1, e1); f, pw = ls.autopower(minimum_frequency=0.3, maximum_frequency=40, samples_per_peak=10); k = int(np.argmax(pw)); f0 = float(f[k])
    fr = np.linspace(f0 - 2e-4, f0 + 2e-4, 2001); f0 = float(fr[np.argmax(ls.power(fr))])
    m2 = np.isfinite(w2) & np.isfinite(e2)
    out.update(n_wise=len(t), W1=float(np.median(w1)), P=1/f0, pow_w1=float(pw[k]), fap_w1=float(ls.false_alarm_probability(pw[k], minimum_frequency=0.3, maximum_frequency=40)),
               pow_w2=float(LombScargle(t[m2], w2[m2], e2[m2]).power(np.array([f0]))[0]) if m2.sum() > 30 else None)
    out["A_W1"], out["eA_W1"] = amp(t - 2459000, w1, e1, f0)
    if m2.sum() > 30: out["A_W2"], out["eA_W2"] = amp(t[m2] - 2459000, w2[m2], e2[m2], f0)
    out["status"] = "OK_WISE"
    if de0 > -29:
        rap = ra0 + pmra*5/3.6e6/np.cos(np.radians(de0)); dep = de0 + pmde*5/3.6e6
        url = f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{rap}%20{dep}%200.000833&BANDNAME=g,r,i&FORMAT=CSV"
        q = ""
        for k2 in range(3):
            q = subprocess.run(["curl", "-sL", "--max-time", "600", url], capture_output=True, text=True).stdout
            if q.startswith("oid"): break
            time.sleep(10*(k2 + 1))
        if not q.startswith("oid"): out["ztf"] = "HOLE"
        else:
            Z, bad = [], 0
            for z in csv.DictReader(io.StringIO(q)):
                try:
                    if z["catflags"] == "0" and abs(float(z["sharp"])) < 0.5 and float(z["mag"]) < float(z["limitmag"]) - 0.2:
                        float(z["hjd"]); float(z["magerr"]); Z.append(z)
                except (TypeError, ValueError, KeyError):
                    bad += 1          # malformed/truncated row (e.g. a response cut by a network drop): skipped and counted
            out["ztf_malformed_rows"] = bad
            zb = np.array([z["filtercode"] for z in Z]); zt = np.array([float(z["hjd"]) for z in Z]); zm = np.array([float(z["mag"]) for z in Z]); ze = np.array([float(z["magerr"]) for z in Z])
            zo = np.array([z["oid"] for z in Z])
            for o in set(zo): zm[zo == o] -= np.median(zm[zo == o])
            out["ztf"] = {}
            for b in ("zg", "zr", "zi"):
                sb = zb == b
                if sb.sum() >= 20:
                    a, ea = amp(zt[sb] - 2459000, zm[sb], ze[sb], f0)
                    lz = LombScargle(zt[sb], zm[sb], ze[sb]); fz, pz = lz.autopower(minimum_frequency=0.3, maximum_frequency=40, samples_per_peak=5)
                    out["ztf"][b] = dict(n=int(sb.sum()), A=a, eA=ea, pow_at_P=float(lz.power(np.array([f0]))[0]), Pbest=float(1/fz[np.argmax(pz)]), pow_best=float(pz.max()))
    else: out["ztf"] = "SOUTH"
    return out
def safe_work(r):
    try:
        return work(r)
    except Exception as e:     # never let one target kill the run; record it as a hole
        return dict(designation=r["designation"], gaia=str(int(r["Source"])), status=f"HOLE_EXCEPTION {type(e).__name__}: {str(e)[:80]}")
todo = [r for _, r in x.iterrows() if r["designation"] not in done]
print("to do:", len(todo), flush=True)
with ThreadPoolExecutor(max_workers=3) as ex:
    for o in ex.map(safe_work, todo):
        with lock:
            open("vw_pipeline_lolat.jsonl", "a").write(json.dumps(o) + "\n")
            flag = ""
            if o.get("status") == "OK_WISE" and o["pow_w1"] > 0.3 and o["A_W1"] > 0.2:
                zr = o.get("ztf", {}).get("zr") if isinstance(o.get("ztf"), dict) else None
                ratio = o["A_W1"] / max(zr["A"], 0.02) if zr else None
                flag = f"  <-- strong IR period; A_W1/A_r = {ratio:.1f}" if ratio else "  <-- strong IR period (no ZTF r)"
            print(o["designation"], o.get("gaia"), o.get("status"), f"P={o.get('P', 0):.6f} powW1={o.get('pow_w1', 0):.2f} A_W1={o.get('A_W1', 0):.2f}" if o.get("status") == "OK_WISE" else "", flag, flush=True)
print("PIPELINE_DONE", flush=True)
