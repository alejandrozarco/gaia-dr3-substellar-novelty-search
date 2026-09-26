# NEOWISE-R + AllWISE single-exposure photometry at PM-propagated Gaia positions; fold on the ZTF period
import sys, json, io, csv, subprocess, numpy as np
from astroquery.gaia import Gaia
T = {"J1526": ("6315134987927550592", 0.09379696), "J1435": ("6285270400986331136", 0.09725693), "J0541": ("3016053028844771456", 0.04721686)}
g = Gaia.launch_job("SELECT source_id, ra, dec, pmra, pmdec, phot_g_mean_mag FROM gaiadr3.gaia_source WHERE source_id IN (" + ",".join(v[0] for v in T.values()) + ")").get_results()
def tap(q):
    p = subprocess.run(["curl", "-s", "--max-time", "600", "--data-urlencode", f"QUERY={q}", "--data-urlencode", "FORMAT=csv", "--data-urlencode", "LANG=ADQL",
                        "--data-urlencode", "REQUEST=doQuery", "https://irsa.ipac.caltech.edu/TAP/sync"], capture_output=True, text=True)
    return list(csv.DictReader(io.StringIO(p.stdout))), p.stdout[:200]
out = {}
for name, (sid, P) in T.items():
    r = g[g["source_id"] == int(sid)][0]
    ra0, de0, pmra, pmde = float(r["ra"]), float(r["dec"]), float(r["pmra"]), float(r["pmdec"])
    # position at epoch 2017.5 (middle of the NEOWISE span 2014-2024) for the query; per-point offsets checked below
    dt = 1.5
    ra = ra0 + pmra * dt / 3.6e6 / np.cos(np.radians(de0)); de = de0 + pmde * dt / 3.6e6
    rows = []
    for tab, cols in (("neowiser_p1bs_psd", "mjd, ra, dec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, qual_frame, qi_fact, saa_sep, moon_masked, cc_flags, nb, na"),
                      ("allwise_p3as_mep", "mjd, ra, dec, w1mpro_ep, w1sigmpro_ep, w2mpro_ep, w2sigmpro_ep, 1 as qual_frame, qi_fact, saa_sep, moon_masked, cc_flags, nb, na")):
        q = f"SELECT {cols} FROM {tab} WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{ra},{de},{4/3600}))=1"
        rr, head = tap(q)
        if not rr and not head.startswith("mjd"): print(name, tab, "QUERY PROBLEM:", head); continue
        for x in rr:
            x["tab"] = tab
            for b in ("w1mpro", "w1sigmpro", "w2mpro", "w2sigmpro"):
                if b + "_ep" in x: x[b] = x.pop(b + "_ep")
        rows += rr
        print(name, tab, len(rr), "rows")
    good = []
    for x in rows:
        try:
            w1 = float(x["w1mpro"]); e1 = float(x["w1sigmpro"])
        except ValueError: continue
        yr = (float(x["mjd"]) - 57204.5) / 365.25 + 2015.5 - 2016.0
        rap = ra0 + pmra * yr / 3.6e6 / np.cos(np.radians(de0)); dep = de0 + pmde * yr / 3.6e6
        sep = np.hypot((float(x["ra"]) - rap) * np.cos(np.radians(de0)), float(x["dec"]) - dep) * 3600
        ok = (float(x["qual_frame"]) > 0 and float(x["qi_fact"]) > 0 and float(x["saa_sep"]) > 0 and x["moon_masked"][0] == "0" and x["cc_flags"][0] == "0"
              and int(x["nb"]) == 1 and int(x["na"]) == 0 and sep < 2.5)
        if ok: good.append((float(x["mjd"]), w1, e1, sep, x["tab"]))
    good = np.array([(a, b, c, d) for a, b, c, d, _ in good])
    print(f"{name}: {len(rows)} rows, {len(good)} clean (W1)")
    if len(good) < 20: continue
    t, m, e = good[:, 0], good[:, 1], good[:, 2]
    # BJD-ish: use MJD directly (light-travel correction < 8.3 min = 0.06 cycles; we test coherence, not absolute phase)
    visits = np.round((t - t.min()) / 30).astype(int)
    print(f"  W1 median {np.median(m):.2f}, robust sigma {1.4826*np.median(np.abs(m-np.median(m))):.3f}, median err {np.median(e):.3f}, n visits {len(set(visits))}, "
          f"span {t.min():.0f}-{t.max():.0f}")
    from astropy.timeseries import LombScargle
    f0 = 1 / P
    ls = LombScargle(t, m, e)
    fr = np.linspace(f0 * 0.98, f0 * 1.02, 20001); pw = ls.power(fr)
    k = int(np.argmax(pw))
    print(f"  LS near f0 (+-2%): peak at P={1/fr[k]:.8f} d power {pw[k]:.3f}; power at ZTF P {ls.power(np.array([f0]))[0]:.3f}; at 2P {ls.power(np.array([f0/2]))[0]:.3f}")
    fw, pww = ls.autopower(minimum_frequency=0.5, maximum_frequency=40, samples_per_peak=10)
    kk = int(np.argmax(pww)); print(f"  global LS 0.5-40 c/d: best P={1/fw[kk]:.7f} d power {pww[kk]:.3f}; FAP {ls.false_alarm_probability(pww[kk], minimum_frequency=0.5, maximum_frequency=40):.2e}")
    ph = (t * f0) % 1
    bins = [np.median(m[(ph >= j/10) & (ph < (j+1)/10)]) if ((ph >= j/10) & (ph < (j+1)/10)).sum() > 3 else np.nan for j in range(10)]
    print("  W1 binned fold (10 bins):", " ".join(f"{b:.2f}" for b in bins), f"  range {np.nanmax(bins)-np.nanmin(bins):.3f}")
    out[name] = dict(t=t.tolist(), m=m.tolist(), e=e.tolist(), P=P)
json.dump(out, open("neowise.json", "w"))
