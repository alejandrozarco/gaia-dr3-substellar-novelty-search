import sys, json, pickle, subprocess, os, urllib.parse, math
sys.path.insert(0, "/tmp/kk76_fix")
import numpy as np
from astropy.time import Time
FO = "/private/tmp/claude-501/-Users-USER-claude-projects/5bae4473-7497-4a6b-8bf6-3ecc9abd4295/scratchpad/fo_build/find_orb/fo"
GROUND = os.path.expanduser("~/claude_projects/gaia-recovered-2026-05-27/docs/reports/precovery_campaign_2026_07_07/kk76_refit/arc_kk76.obs")
PACK = "88268K01K76K"
HV = pickle.load(open("/tmp/kk76_fix/hst_vectors.pkl", "rb"))

def date_field(jd):
    t = Time(jd, format="jd", scale="utc"); d = t.datetime
    frac = (d.hour * 3600 + d.minute * 60 + d.second + d.microsecond / 1e6) / 86400.0
    return f"{d.year:4d} {d.month:02d} {d.day + frac:09.6f}"          # 17 chars

def ra_field(ra):
    s = (ra / 15.0) * 3600.0; s = round(s, 3)
    hh = int(s // 3600); mm = int((s - hh * 3600) // 60); ss = s - hh * 3600 - mm * 60
    return f"{hh:02d} {mm:02d} {ss:06.3f}"                               # 12 chars

def dec_field(dec):
    sgn = "-" if dec < 0 else "+"; s = round(abs(dec) * 3600.0, 2)
    dd = int(s // 3600); mm = int((s - dd * 3600) // 60); ss = s - dd * 3600 - mm * 60
    return f"{sgn}{dd:02d} {mm:02d} {ss:05.2f}"                         # 12 chars

def axis(v):
    return f"{'-' if v < 0 else '+'} {abs(v):9.4f} "

def hst_obs(root, ra, dec, sig_ra, sig_dec):
    v = HV[root]; jd = v["jd"]
    L1 = list(" " * 80); L1[0:12] = PACK; L1[14] = "S"
    df = date_field(jd); L1[15:32] = df
    L1[32:44] = ra_field(ra); L1[44:56] = dec_field(dec); L1[77:80] = "250"
    L2 = list(" " * 80); L2[0:12] = PACK; L2[14] = "s"; L2[15:32] = df; L2[32] = "1"
    L2[34:46] = axis(v["X"]); L2[46:58] = axis(v["Y"]); L2[58:70] = axis(v["Z"]); L2[77:80] = "250"
    return [f"#Sigmas {sig_ra:.3f}x{sig_dec:.3f}", "".join(L1), "".join(L2)]

def write_obs(fn, hst_rows, ground=True):
    lines = open(GROUND).read().splitlines() if ground else []
    for r in hst_rows: lines += hst_obs(*r)
    open(fn, "w").write("\n".join(lines) + "\n")

def run_fo(obsfile, outdir):
    os.makedirs(outdir, exist_ok=True)
    p = subprocess.run([FO, obsfile, "-O", outdir, "-q"], capture_output=True, text=True, timeout=600)
    E = json.load(open(os.path.join(outdir, "elements.json")))
    ob = list(E["objects"].values())[0]
    return ob

def horizons_pred(el, jd_utc_list, center="500@-48"):
    base = "https://ssd.jpl.nasa.gov/api/horizons.api"
    q = el["elements"]
    params = {"format": "json", "COMMAND": "';'", "OBJ_DATA": "NO", "MAKE_EPHEM": "YES", "EPHEM_TYPE": "OBSERVER",
              "CENTER": center, "QUANTITIES": "1", "ANG_FORMAT": "DEG", "EXTRA_PREC": "YES", "CSV_FORMAT": "YES",
              "TIME_TYPE": "UT", "TLIST_TYPE": "JD", "TLIST": " ".join(f"{j:.7f}" for j in jd_utc_list),
              "EPOCH": f"{q['epoch']:.6f}", "ECLIP": "J2000", "EC": f"{q['e']:.13f}", "QR": f"{q['q']:.12f}",
              "TP": f"{q['Tp']:.8f}", "OM": f"{q['asc_node']:.12f}", "W": f"{q['arg_per']:.12f}", "IN": f"{q['i']:.12f}"}
    url = base + "?" + urllib.parse.urlencode(params)
    js = json.loads(subprocess.run(["curl", "-sL", "--max-time", "180", url], capture_output=True, text=True).stdout)
    txt = js["result"]
    if "$$SOE" not in txt: raise RuntimeError(txt[-1500:])
    body = txt.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
    out = [(float(l.split(",")[3]), float(l.split(",")[4])) for l in body]
    assert len(out) == len(jd_utc_list)
    return out

def offset_arcsec(ra1, de1, ra0, de0):
    """(ra1,de1) minus (ra0,de0), as (dRA*cos(dec), dDec) arcsec"""
    return ((ra1 - ra0 + 180) % 360 - 180) * np.cos(np.radians(de0)) * 3600, (de1 - de0) * 3600
