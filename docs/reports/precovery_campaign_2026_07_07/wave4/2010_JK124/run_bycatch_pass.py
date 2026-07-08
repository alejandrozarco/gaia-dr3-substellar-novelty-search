#!/usr/bin/env python3
"""Mandatory bycatch pass (rule 5). For each chain night, pull ALL single-exposure
detections in a 5' field across that night's exposures + the NSC mean-object catalog
as static_sources; run bycatch.run_bycatch(identify=True). Log n_unknown_candidate."""
import sys, urllib.request, urllib.parse, csv, math, json, time
sys.path.insert(0,"/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27/scripts/precovery")
import bycatch
TAP="https://datalab.noirlab.edu/tap/sync"
def tap(q,retries=4):
    data=urllib.parse.urlencode({"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q}).encode()
    for i in range(retries):
        try: return urllib.request.urlopen(TAP,data=data,timeout=180).read().decode()
        except Exception as e: last=str(e); time.sleep(3)
    return "ERR "+last

# night: label, center ra/dec, list of exposures (same night)
NIGHTS=[
 ("2014-06-06",243.4776,-29.5435,["c4d_140606_025954_ooi_r_v1","c4d_140606_065522_ooi_r_v1"]),
 ("2015-06-20",244.7440,-29.3947,["c4d_150620_050628_ooi_r_v2","c4d_150620_050928_ooi_r_v2"]),
 ("2016-03-08",247.9622,-29.4666,["c4d_160308_082444_ooi_VR_v1","c4d_160308_082745_ooi_VR_v1"]),
]
R=150.0  # arcsec field radius (tightened for bounded runtime)
summary={}
for label,ra,dec,exps in NIGHTS:
    cosd=math.cos(math.radians(dec)); dra=R/3600/cosd; ddec=R/3600
    dets=[]
    for e in exps:
        q=(f"SELECT measid,ra,dec,mjd,mag_auto,filter,fwhm,class_star,exposure FROM nsc_dr2.meas "
           f"WHERE exposure='{e}' AND ra BETWEEN {ra-dra:.7f} AND {ra+dra:.7f} "
           f"AND dec BETWEEN {dec-ddec:.7f} AND {dec+ddec:.7f}")
        for r in csv.DictReader(tap(q).splitlines()):
            dets.append(dict(id=r["measid"],ra=float(r["ra"]),dec=float(r["dec"]),
                mjd=float(r["mjd"]),mag=float(r["mag_auto"]) if r["mag_auto"] else None,
                filter=r["filter"],exposure=r["exposure"],group_id=label))
    # static mean-object catalog for same field
    q2=(f"SELECT id,ra,dec,ndet FROM nsc_dr2.object WHERE ra BETWEEN {ra-dra:.7f} AND {ra+dra:.7f} "
        f"AND dec BETWEEN {dec-ddec:.7f} AND {dec+ddec:.7f}")
    static=[dict(id=r["id"],ra=float(r["ra"]),dec=float(r["dec"]))
            for r in csv.DictReader(tap(q2).splitlines())]
    out=f"/tmp/precovery_wave4/2010_JK124/bycatch_{label}.csv"
    cfg=bycatch.BycatchConfig(same_night_max_hr=0.5)  # only near-simultaneous pairs -> bounded MPChecker load
    res=bycatch.run_bycatch(dets, static_sources=static, identify=True, cfg=cfg, out_csv=out)
    summary[label]=dict(n_detections=res["n_detections"],n_static=res["n_static_sources"],
        n_tracklets=res["n_tracklets"],n_known=res["n_known"],
        n_unknown_candidate=res["n_unknown_candidate"],n_offline=res["n_unidentified_offline"])
    print(f"{label}: dets={res['n_detections']} static={res['n_static_sources']} "
          f"tracklets={res['n_tracklets']} known={res['n_known']} "
          f"UNKNOWN={res['n_unknown_candidate']} offline={res['n_unidentified_offline']}")
    for t in res["tracklets"]:
        print(f"    [{t['classification']}] rate={t.get('rate_arcsec_hr')}\"/hr pa={t.get('pa_deg')} "
              f"mag={t.get('mag_mean')} members={t.get('member_exposures')} mpc={t.get('mpc_all_hits')}")
json.dump(summary,open("/tmp/precovery_wave4/2010_JK124/bycatch_summary.json","w"),indent=1)
print("\nBYCATCH TOTAL unknown_candidates:",sum(s["n_unknown_candidate"] for s in summary.values()))
