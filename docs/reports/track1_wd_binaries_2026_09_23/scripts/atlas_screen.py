"""ATLAS forced photometry for the southern novelty pool + the same period criteria as the ZTF screen.
Token read from ~/.config/atlas/token, never printed. Jobs are deleted after download."""
import json, os, time, io, math, requests, numpy as np
from astropy.timeseries import LombScargle
tok = open(os.path.expanduser("~/.config/atlas/token")).read().strip()
H = {"Authorization": f"Token {tok}", "Accept": "application/json"}
BASE = "https://fallingstar-data.com/forcedphot"
br = json.load(open("bridge_known.json"))
SPECIAL = ("VSX", "Ritter", "Downes", "Schwope", "SDSS-DR20", "Li+2025", "GF21", "CataclyV", "WhiteDwarf", "Nova", "XrayBin", "EmLine")
south = [o for o in br if not any(any(s in k for s in SPECIAL) for k in o["known"]) and o["dec"] <= -28]
done = {}
if os.path.exists("atlas_screen.json"):
    for o in json.load(open("atlas_screen.json")): done[o["sid"]] = o
print(f"southern novelty pool: {len(south)} ({len(done)} already done)", flush=True)
def queue(o):
    for k in range(6):
        r = requests.post(f"{BASE}/queue/", headers=H, data={"ra": o["ra"], "dec": o["dec"], "mjd_min": 57000.0, "send_email": False}, timeout=60)
        if r.status_code == 201: return r.json()["url"]
        if r.status_code == 429: time.sleep(int(r.json().get("detail", "").split("available in ")[-1].split(" ")[0]) if "available in" in r.text else 30); continue
        time.sleep(10 * (k + 1))
    return None
def fetch(url):
    for k in range(120):
        r = requests.get(url, headers=H, timeout=60)
        if r.status_code == 200:
            j = r.json()
            if j.get("finishtimestamp"):
                if j.get("result_url"):
                    txt = requests.get(j["result_url"], headers=H, timeout=120).text
                    requests.delete(url, headers=H, timeout=60)
                    return txt
                requests.delete(url, headers=H, timeout=60); return ""
        time.sleep(10)
    return None
def analyse(o, txt):
    lines = [l for l in txt.splitlines() if l.strip()]
    hdr = lines[0].lstrip("#").split(); rows = [dict(zip(hdr, l.split())) for l in lines[1:]]
    ok = [r for r in rows if float(r["duJy"]) > 0 and float(r["err"]) == 0 and float(r["chi/N"]) < 10 and float(r["m"]) > 0 and float(r["dm"]) < 0.3]
    t = np.array([float(r["MJD"]) for r in ok]); m = np.array([float(r["m"]) for r in ok]); e = np.array([float(r["dm"]) for r in ok]); b = np.array([r["F"] for r in ok])
    o["n"] = {bb: int((b == bb).sum()) for bb in ("c", "o")}; o["bands"] = {}
    for bb in ("c", "o"):
        s = b == bb
        if s.sum() < 60: continue
        mm = m[s] - np.median(m[s]); clip = np.abs(mm) < 5 * 1.4826 * np.median(np.abs(mm)) + 0.5
        ls = LombScargle(t[s][clip], mm[clip], e[s][clip]); f, pw = ls.autopower(minimum_frequency=0.05, maximum_frequency=48, samples_per_peak=10)
        k = int(np.argmax(pw)); f0 = f[k]; fap = float(ls.false_alarm_probability(pw[k], minimum_frequency=0.05, maximum_frequency=48))
        al = max(float(ls.power(np.linspace(f0 + d - 3e-4, f0 + d + 3e-4, 61)).max()) for d in (-1.00274, -1.0, 1.0, 1.00274) if f0 + d > 0.01)
        ph = (t[s][clip] * f0) % 1; bins = np.array([np.median(mm[clip][(ph >= j / 12) & (ph < (j + 1) / 12)]) for j in range(12)])
        o["bands"][bb] = dict(P=round(1 / f0, 7), power=round(float(pw[k]), 3), alias=round(al, 3), fap=fap, amp=round(float(np.nanmax(bins) - np.nanmin(bins)), 3),
                              near_day=bool(abs(1 / f0 - 1) < 0.03 or abs(1 / f0 - 0.5) < 0.01 or 1 / f0 > 15))
    bb = o["bands"]; good = [v for v in bb.values() if v["fap"] < 1e-8 and not v["near_day"] and v["power"] > v["alias"]]
    agree = len(bb) == 2 and abs(bb["c"]["P"] - bb["o"]["P"]) / bb["c"]["P"] < 3e-4
    o["verdict"] = "COHERENT_2BAND" if (agree and len(good) == 2) else ("COHERENT_1BAND" if good else "none")
todo = [o for o in south if o["sid"] not in done]
for i in range(0, len(todo), 5):
    batch = todo[i:i + 5]; urls = [(o, queue(o)) for o in batch]
    for o, u in urls:
        if not u: o["atlas"] = "HOLE_QUEUE"; done[o["sid"]] = o; continue
        txt = fetch(u)
        if txt is None: o["atlas"] = "HOLE_TIMEOUT"
        elif not txt.strip(): o["atlas"] = "NO_DATA"
        else:
            o["atlas"] = "OK"
            try: analyse(o, txt)
            except Exception as e: o["atlas"] = f"ERROR {type(e).__name__}"
        done[o["sid"]] = o
        if o.get("verdict", "none") != "none":
            print(f"  {o['verdict']:15s} {o['sid']} {o['name']} G={o['G']:.2f} M_G={o['MG']:.2f} dRidge={o['d_ridge']:+.2f} eRASS1={o['in_erass1']} | " +
                  " ".join(f"{k}: P={v['P']} d ({v['P']*24:.3f} h) pow {v['power']}/{v['alias']} amp {v['amp']}" for k, v in o["bands"].items()) + f" | known: {o['known']}", flush=True)
    json.dump(list(done.values()), open("atlas_screen.json", "w"), indent=0, default=str)
    print(f"  progress {len(done)}/{len(south)}", flush=True)
print("ATLAS_SCREEN_DONE", sum(o.get("verdict") == "COHERENT_2BAND" for o in done.values()), "two-band,", sum(o.get("verdict") == "COHERENT_1BAND" for o in done.values()), "one-band,",
      sum(str(o.get("atlas", "")).startswith("HOLE") for o in done.values()), "holes", flush=True)
