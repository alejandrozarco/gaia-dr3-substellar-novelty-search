# Verify two ATLAS COHERENT_1BAND flags of the southern track-1 screen (eRASS:3 x Gaia WD+M bridge objects):
# 4731701084150029824 (3eRASS J035311.8-550237, o: P 0.0739348 d) and 4791412846234632320 (3eRASS J043649.2-440056, o: P 0.332719 d).
# uJy only; v3 gates (drop err>0, chi/N>10, duJy > 3x band median); per-season median subtraction; LS 0.5-50 c/d per band;
# c-band amplitude at the o-band frequency; permutation null (flux+error pairs shuffled within season) for the o-band maximum
# over the full search; BJD_TDB; Gaia neighbours within 12".
import numpy as np, json, requests
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from astropy.timeseries import LombScargle
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
T = {"4731701084150029824": (58.30184, -55.04399, 0.0739348), "4791412846234632320": (69.20518, -44.01596, 0.332719)}
fr = np.arange(0.5, 50, 2e-5); out = {}
for sid, (ra, dec, P0) in T.items():
    c0 = SkyCoord(ra * u.deg, dec * u.deg)
    L = [l for l in open(f"atlas_raw/{sid}.txt").read().splitlines() if l.strip()]; hdr = L[0].lstrip("#").split(); R = [dict(zip(hdr, l.split())) for l in L[1:]]
    ok = [x for x in R if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]
    D = {}
    for b in ("o", "c"):
        s = [x for x in ok if x["F"] == b]; med = np.median([float(x["duJy"]) for x in s]); s = [x for x in s if float(x["duJy"]) < 3 * med]
        mjd = np.array([float(x["MJD"]) for x in s]); f = np.array([float(x["uJy"]) for x in s]); e = np.array([float(x["duJy"]) for x in s])
        season = np.floor((mjd - 57000) / 365.25 + 0.3).astype(int)
        for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
        clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e)
        t = Time(mjd[clip], format="mjd", scale="utc", location=geo); t = (t.tdb + t.light_travel_time(c0)).jd
        D[b] = (t, f[clip], e[clip], season[clip])
    res = {}
    for b, (t, f, e, sv) in D.items():
        ls = LombScargle(t, f, e); p = ls.power(fr, method="fast"); i = np.argmax(p)
        X = np.vstack([np.ones_like(t), np.sin(2 * np.pi * t / P0), np.cos(2 * np.pi * t / P0)]).T; bb, *_ = np.linalg.lstsq(X / e[:, None], f / e, rcond=None)
        C = np.linalg.inv((X / e[:, None]).T @ (X / e[:, None])); r = (f - X @ bb) / e; s2 = max(r @ r / (len(f) - 3), 1)
        res[b] = dict(n=int(len(t)), best_P=float(1 / fr[i]), best_power=float(p[i]), fap_best=float(ls.false_alarm_probability(p[i], minimum_frequency=0.5, maximum_frequency=50, method="baluev")),
                      power_at_P0=float(ls.power(np.array([1 / P0]))[0]), amp_at_P0_uJy=float(np.hypot(bb[1], bb[2])), amp_err_uJy=float(np.sqrt((C[1, 1] + C[2, 2]) / 2 * s2)),
                      phase_at_P0=float(np.arctan2(bb[2], bb[1])), median_err=float(np.median(e)))
    # permutation null on o-band (full search), 60 shuffles
    t, f, e, sv = D["o"]; rng = np.random.default_rng(5); null = []
    for k in range(60):
        f2, e2 = f.copy(), e.copy()
        for s in np.unique(sv):
            m = np.where(sv == s)[0]; pm = rng.permutation(m); f2[m] = f[pm]; e2[m] = e[pm]
        null.append(LombScargle(t, f2, e2).power(fr[::5], method="fast").max())
    res["o"]["perm_null_max_95"] = float(np.percentile(null, 95)); res["o"]["perm_null_max"] = float(np.max(null))
    res["o"]["p_perm"] = float((np.sum(np.array(null) >= res["o"]["best_power"]) + 1) / 61)
    q = f"SELECT source_id, phot_g_mean_mag, bp_rp, parallax, DISTANCE(POINT({ra},{dec}), POINT(ra,dec))*3600 AS sep FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT(ra,dec), CIRCLE({ra},{dec},{12/3600})) ORDER BY sep"
    g = requests.get("https://gea.esac.esa.int/tap-server/tap/sync", params=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="json", QUERY=q), timeout=120).json()["data"]
    res["neighbours"] = [[str(x[0]), round(x[1], 2), x[2] and round(x[2], 2), x[3] and round(x[3], 2), round(x[4], 2)] for x in g]
    out[sid] = res
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.2))
    for a, b in zip(ax, ("o", "c")):
        t, f, e, _ = D[b]; ph = (t / P0) % 1; o_ = np.argsort(ph); nb = 20; edges = np.linspace(0, 1, nb + 1)
        mb = [np.average(f[(ph >= edges[k]) & (ph < edges[k + 1])], weights=1 / e[(ph >= edges[k]) & (ph < edges[k + 1])] ** 2) for k in range(nb)]
        a.plot(ph, f, ",", color="0.7"); a.plot((edges[:-1] + edges[1:]) / 2, mb, "o-", color="k"); a.set_ylim(np.percentile(f, 1), np.percentile(f, 99))
        a.set_title(f"{sid} ATLAS {b}: fold P = {P0} d", fontsize=8)
    plt.tight_layout(); plt.savefig(f"verify_{sid}.png", dpi=90); plt.close()
    print(sid, json.dumps(res, indent=None)[:1500])
json.dump(out, open("verify_flags.json", "w"), indent=1)
