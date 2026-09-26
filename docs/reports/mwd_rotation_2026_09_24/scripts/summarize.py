# Compile ZTF (detrended pass) + permutation/injection + TESS/K2 results into data/rotation_summary.csv and a printed table.
import json, os, glob, csv, math, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import rotlib as RL
os.chdir("/tmp/fanout/rotation")
T = json.load(open("data/targets.json")); C = json.load(open("data/controls.json"))
VERDICT = json.load(open("data/verdicts.json")) if os.path.exists("data/verdicts.json") else {}
rows = []
for rec in T + C:
    sid = rec["source_id"]
    r = dict(source_id=sid, name=rec.get("name", ""), group=rec.get("group", ""), G=round(float(rec["phot_g_mean_mag"]), 2),
             dec=round(float(rec["dec"]), 2), B_MG=rec.get("B_Ha_MG", ""),
             nb5=";".join(f"{float(n['sep']):.1f}\"/G{float(n['phot_g_mean_mag']):.1f}" for n in rec["neighbours_10as"]
                          if float(n["sep"]) < 5 and n["phot_g_mean_mag"]))
    fz = f"results/{sid}.json"
    if os.path.exists(fz):
        z = json.load(open(fz)); r["ztf_status"] = z.get("status")
        if z.get("status") == "OK":
            c = z["pgram"]["comb"]; b = c["top"][0]
            r.update(ztf_n=c["n"], ztf_bands="+".join(f"{k[1]}{v['n']}" for k, v in z["bands"].items()), ztf_span_d=round(z["grid"]["span_d"]),
                     ztf_best_f=round(b["freq"], 5), ztf_best_P_h=round(b["P_h"], 5), ztf_best_amp_pct=round(100 * b["amp"], 2),
                     ztf_best_fap_baluev=f"{b['fap_baluev']:.2g}", ztf_best_sysflag="; ".join(RL.alias_notes(b["freq"], z["window_peaks"])),
                     ztf_1to5d_P_d=round(c["best_1to5d"]["P_d"], 4), ztf_1to5d_fapw=f"{c['best_1to5d']['fap_baluev_window']:.2g}")
            for band in ("zg", "zr"):
                if band in z["pgram"]:
                    bb = z["pgram"][band]["top"][0]
                    r[f"{band}_best_f"] = round(bb["freq"], 5); r[f"{band}_best_fap"] = f"{bb['fap_baluev']:.2g}"
    else:
        r["ztf_status"] = "no ZTF DR24 (dec<-31)" if float(rec["dec"]) < -31 else ("J2159: prior analysis" if sid == "1980205739970324224" else "no file")
    fp = f"perm/{sid}.json"
    if os.path.exists(fp):
        p = json.load(open(fp))
        r.update(perm_K=p["K"], masked_best_f=round(p["f_obs_masked"], 5), masked_best_P_h=round(24 / p["f_obs_masked"], 5),
                 masked_fap_baluev=f"{p['fap_baluev_masked']:.2g}", masked_fap_perm_emp=f"{p['fap_perm_emp_masked']:.3f}",
                 masked_fap_perm_gumbel=f"{p['fap_perm_gumbel_masked']:.2g}",
                 A90_5_60min=p["injection"]["5-60min_A90"], A90_1_24h=p["injection"]["1-24h_A90"], A90_1_5d=p["injection"]["1-5d_A90"],
                 A50_5_60min=p["injection"]["5-60min_A50"], A50_1_24h=p["injection"]["1-24h_A50"], A50_1_5d=p["injection"]["1-5d_A50"])
    for kind in ("tess", "k2"):
        ft = f"results_tess/{sid}_{kind}.json"
        if os.path.exists(ft):
            q = json.load(open(ft))
            if q.get("status") == "OK":
                key = "all" if "all" in q["pgram"] else list(q["pgram"].keys())[0]
                v = q["pgram"][key]
                r.update({f"{kind}_sectors": "+".join(str(s["sector"]) for s in q["segments"]), f"{kind}_n": v["n"],
                          f"{kind}_best_P_h": round(v["best_P_h"], 5), f"{kind}_fap": f"{v['fap_baluev']:.2g}", f"{kind}_amp_pct": round(100 * v["amp"], 2),
                          f"{kind}_crowdsap": ";".join(f"{s['crowdsap']:.2f}" if s.get("crowdsap") is not None else "NA" for s in q["segments"]),
                          f"{kind}_A90_5_60min": v.get("injection", {}).get("5-60min_A90"), f"{kind}_A90_1_24h": v.get("injection", {}).get("1-24h_A90")})
    W = json.load(open("data/window_1to5d.json")) if os.path.exists("data/window_1to5d.json") else {}
    if sid in W and "comb" in W[sid]:
        r.update(ztf_1to5d_masked_P_d=round(W[sid]["comb"]["P_d"], 4), ztf_1to5d_masked_fapw=f"{W[sid]['comb']['fap_window']:.2g}")
    r["verdict"] = VERDICT.get(sid, "")
    r["evidence_files"] = ";".join(x for x in (f"plots/{sid}_ls.png" if os.path.exists(f"plots/{sid}_ls.png") else "",
                                              f"plots/{sid}_tess.png" if os.path.exists(f"plots/{sid}_tess.png") else "") if x)
    rows.append(r)
keys = []
for r in rows:
    for k in r:
        if k not in keys: keys.append(k)
with open("data/rotation_summary.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
print("wrote data/rotation_summary.csv", len(rows), "rows")
