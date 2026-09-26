# Batch line measurement for the SnowWhite CV selection. For every object: barycentric re-coadd of the mwmVisit spectra
# (XCSAO shift undone per visit), emission EWs of Balmer/He I/He II lines on the coadd, per-visit H-alpha EW, the per-visit
# xcsao_v_rad values, and the same measurement on the pipeline mwmStar coadd (to see what the XCSAO artefact does).
# Output: lines_all.csv (one row per object). EW sign convention: positive = emission.
import numpy as np, pandas as pd, json, os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "/tmp/fanout/cv")
from cvspec import load_visits, load_star, coadd, measure_all, line_ew, LINES, WINDOWS, HALF

sw = pd.read_csv("sw_cv_x2.csv")
rows = []
for _, r in sw.iterrows():
    sid = int(r.sdss_id)
    rec = dict(sdss_id=sid, gaia=int(r.gaia_dr3_source_id))
    fv = f"spec/mwmVisit-0.8.1-{sid}.fits"; fs = f"spec/mwmStar-0.8.1-{sid}.fits"
    if not os.path.exists(fv):
        rec["status"] = "NO_VISIT_FILE"; rows.append(rec); continue
    try:
        vis = load_visits(sid)
    except Exception as e:
        rec["status"] = f"VISIT_READ_ERROR {e}"[:80]; rows.append(rec); continue
    rec["n_vis"] = len(vis)
    rec["v_xcsao"] = ";".join(f"{v['v_xcsao']:.0f}" for v in vis)
    rec["vis_snr"] = ";".join(f"{v['snr']:.1f}" for v in vis)
    rec["vis_mjd"] = ";".join(str(v["mjd"]) for v in vis)
    rec["max_abs_vx"] = max([abs(v["v_xcsao"]) for v in vis], default=np.nan)
    good = [i for i, v in enumerate(vis) if v["snr"] > 1.0]
    lam, fl, iv, n = coadd(vis, use=good if good else None)
    rec["n_coadd"] = n
    ok = np.isfinite(fl) & (iv > 0)
    if ok.sum() < 500:
        rec["status"] = "EMPTY_COADD"; rows.append(rec); continue
    # coadd S/N in 5000-6000 A (median flux*sqrt(ivar))
    b = ok & (lam > 5000) & (lam < 6000)
    rec["snr_coadd"] = float(np.nanmedian(fl[b] * np.sqrt(iv[b]))) if b.sum() else np.nan
    m = measure_all(lam, fl, iv)
    for k, d in m.items():
        rec[f"{k}_ew"] = d["ew"]; rec[f"{k}_sig"] = d["sig"]; rec[f"{k}_fwhm"] = d["fwhm"]
    # continuum slope proxies (blue/red flux ratio)
    def med(a, b_):
        s = ok & (lam > a) & (lam < b_); return float(np.nanmedian(fl[s])) if s.sum() > 10 else np.nan
    rec["f4000_4200"] = med(4000, 4200); rec["f5500_5700"] = med(5500, 5700); rec["f7400_7600"] = med(7400, 7600); rec["f8700_8900"] = med(8700, 8900)
    # per-visit H-alpha and H-beta EW (barycentric frame)
    ha_v, hb_v = [], []
    for v in vis:
        g = (v["ivar"] > 0) & np.isfinite(v["flux"])
        if g.sum() < 500:
            ha_v.append(np.nan); hb_v.append(np.nan); continue
        ha_v.append(line_ew(v["lam"][g], v["flux"][g], v["ivar"][g], LINES["Ha"], half=HALF["Ha"], windows=WINDOWS["Ha"])["ew"])
        hb_v.append(line_ew(v["lam"][g], v["flux"][g], v["ivar"][g], LINES["Hb"], half=HALF["Hb"], windows=WINDOWS["Hb"])["ew"])
    rec["Ha_ew_visits"] = ";".join(f"{x:.1f}" for x in ha_v); rec["Hb_ew_visits"] = ";".join(f"{x:.1f}" for x in hb_v)
    # pipeline mwmStar coadd (rest frame per Astra): H-alpha EW there, to flag the XCSAO artefact
    if os.path.exists(fs):
        try:
            st = load_star(sid)
            for s in st[:1]:
                g = (s["ivar"] > 0) & np.isfinite(s["flux"])
                d = line_ew(s["lam"][g], s["flux"][g], s["ivar"][g], LINES["Ha"], half=HALF["Ha"], windows=WINDOWS["Ha"])
                rec["Ha_ew_mwmStar"] = d["ew"]; rec["mwmStar_snr"] = s["snr"]; rec["mwmStar_vrad"] = s["v_rad"]
        except Exception as e:
            rec["mwmStar_err"] = str(e)[:60]
    rec["status"] = "OK"
    rows.append(rec)
out = pd.DataFrame(rows)
out.to_csv("lines_all.csv", index=False)
print(out.status.value_counts())
