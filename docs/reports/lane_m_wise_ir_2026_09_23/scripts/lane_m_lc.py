# Lane M step 3: ZTF + NEOWISE light curves for candidates; LS periods, amplitudes per band, IR/optical amplitude ratio
import io, csv, sys, json, subprocess, warnings, numpy as np
warnings.filterwarnings("ignore")
from astropy.timeseries import LombScargle
from astroquery.gaia import Gaia
C = {"J0220+6303": "513958743252720768", "J1226-2304": "3513017956589117056", "J1705+6607": "1635581274974672768", "J1642+0135": "4384149753578863744",
     "J1526-1113(ctl)": "6315134987927550592", "QSVir(ctl)": "3612227169936143360"}
g = Gaia.launch_job("SELECT source_id, ra, dec, pmra, pmdec, parallax, phot_g_mean_mag, bp_rp FROM gaiadr3.gaia_source WHERE source_id IN (" + ",".join(C.values()) + ")").get_results()
def tap(q):
    p = subprocess.run(["curl", "-s", "--max-time", "900", "--data-urlencode", f"QUERY={q}", "--data-urlencode", "FORMAT=csv", "--data-urlencode", "LANG=ADQL",
                        "--data-urlencode", "REQUEST=doQuery", "https://irsa.ipac.caltech.edu/TAP/sync"], capture_output=True, text=True)
    if not p.stdout.startswith("mjd"): raise RuntimeError(p.stdout[:300])
    return list(csv.DictReader(io.StringIO(p.stdout)))
def fit2(t, m, e, f, nh=2):
    cols = [np.ones_like(t)]
    for k in range(1, nh + 1): cols += [np.sin(2*np.pi*k*f*t), np.cos(2*np.pi*k*f*t)]
    X = np.column_stack(cols); w = 1/e**2; p = np.linalg.solve(X.T @ (X*w[:, None]), X.T @ (m*w))
    ph = np.linspace(0, 1, 500, endpoint=False); M = p[0] + sum(p[2*k-1]*np.sin(2*np.pi*k*ph) + p[2*k]*np.cos(2*np.pi*k*ph) for k in range(1, nh + 1))
    return M.max() - M.min()
res = {}
for name, sid in C.items():
    r = g[g["source_id"] == int(sid)][0]; ra0, de0, pmra, pmde = float(r["ra"]), float(r["dec"]), float(r["pmra"]), float(r["pmdec"])
    out = dict(sid=sid, G=float(r["phot_g_mean_mag"]))
    # ZTF by position at epoch ~2021 (PM-propagated)
    dt = 5.0; ra = ra0 + pmra*dt/3.6e6/np.cos(np.radians(de0)); de = de0 + pmde*dt/3.6e6
    url = f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{ra}%20{de}%200.000833&BANDNAME=g,r,i&BAD_CATFLAGS_MASK=32768&FORMAT=CSV"
    q = ""
    for k in range(3):
        q = subprocess.run(["curl", "-sL", "--max-time", "600", url], capture_output=True, text=True).stdout
        if q.startswith("oid"): break
    Z = [x for x in csv.DictReader(io.StringIO(q)) if x["catflags"] == "0" and abs(float(x["sharp"])) < 0.5] if q.startswith("oid") else []
    bands = {}
    if Z:
        zt = np.array([float(x["hjd"]) for x in Z]); zm = np.array([float(x["mag"]) for x in Z]); ze = np.array([float(x["magerr"]) for x in Z])
        zb = np.array([x["filtercode"] for x in Z]); zo = np.array([x["oid"] for x in Z])
        for o in set(zo): zm[zo == o] -= np.median(zm[zo == o])
        for b in ("zg", "zr", "zi"):
            s = zb == b
            if s.sum() < 40: continue
            ls = LombScargle(zt[s], zm[s], ze[s]); f, pw = ls.autopower(minimum_frequency=0.5, maximum_frequency=50, samples_per_peak=10)
            k = int(np.argmax(pw)); bands[b] = dict(n=int(s.sum()), P=1/f[k], power=float(pw[k]), rms=float(1.4826*np.median(np.abs(zm[s]-np.median(zm[s])))))
        out["ztf"] = bands; out["ztf_raw"] = (zt.tolist(), zm.tolist(), ze.tolist(), zb.tolist())
    # NEOWISE + AllWISE
    dt = 1.5; ra = ra0 + pmra*dt/3.6e6/np.cos(np.radians(de0)); de = de0 + pmde*dt/3.6e6
    W = tap(f"SELECT mjd, ra, dec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, qual_frame, qi_fact, saa_sep, moon_masked, cc_flags, nb, na FROM neowiser_p1bs_psd "
            f"WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{ra},{de},{4/3600}))=1")
    wl = []
    for x in W:
        try: w1 = float(x["w1mpro"]); e1 = float(x["w1sigmpro"])
        except ValueError: continue
        if float(x["qual_frame"]) > 0 and float(x["qi_fact"]) > 0 and float(x["saa_sep"]) > 0 and x["moon_masked"][0] == "0" and x["cc_flags"][0] == "0" and x["nb"] == "1" and x["na"] == "0":
            wl.append((float(x["mjd"]), w1, e1))
    wl = np.array(wl)
    if len(wl) > 30:
        wt, wm, we = wl[:, 0] + 2400000.5, wl[:, 1], wl[:, 2]
        ls = LombScargle(wt, wm, we); f, pw = ls.autopower(minimum_frequency=0.5, maximum_frequency=40, samples_per_peak=10)
        k = int(np.argmax(pw)); out["wise"] = dict(n=len(wl), P=1/f[k], power=float(pw[k]), W1=float(np.median(wm)))
        # amplitudes at a common period: take the W1 best period and its double; compare with ZTF at the same frequency
        for lab, PP in (("P_w", 1/f[k]), ("2P_w", 2/f[k])):
            fr = 1/PP; amps = {"W1": fit2(wt, wm, we, fr, 2)}
            if Z:
                for b in ("zg", "zr", "zi"):
                    s = zb == b
                    if s.sum() >= 40: amps[b] = fit2(zt[s], zm[s], ze[s], fr, 2)
            out[f"amp_at_{lab}"] = {kk: round(v, 3) for kk, v in amps.items()}
        out["wise_raw"] = (wt.tolist(), wm.tolist(), we.tolist())
    res[name] = out
    print(name, sid, "G", round(out["G"], 2), "| ZTF:", {b: (v["n"], round(v["P"], 7), round(v["power"], 3)) for b, v in out.get("ztf", {}).items()},
          "| WISE:", {k: (round(v, 7) if isinstance(v, float) else v) for k, v in out.get("wise", {}).items()}, "| amp@Pw:", out.get("amp_at_P_w"), "| amp@2Pw:", out.get("amp_at_2P_w"), flush=True)
json.dump(res, open("lane_m_lc.json", "w"))
