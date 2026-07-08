import json, sys
sys.path.insert(0, "/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27/scripts/precovery")
import bycatch
dets=json.load(open("bycatch_dets.json"))
static=json.load(open("bycatch_static.json"))
# offline identify=False first pass to see tracklets (MPChecker network may be slow); then identify
summ=bycatch.run_bycatch(dets, static_sources=static, identify=True, out_csv="bycatch_tracklets.csv")
keys=["n_detections","n_static_sources","n_tracklets","n_known","n_unknown_candidate","n_unidentified_offline","rejections"]
out={k:summ[k] for k in keys}
json.dump(out, open("bycatch_summary.json","w"), indent=1)
print(json.dumps(out, indent=1))
# list any unknown candidates
for t in summ["tracklets"]:
    if t["classification"]=="unknown_candidate":
        print("UNKNOWN:", t.get("ra_mean"),t.get("dec_mean"),t.get("rate_arcsec_per_hr"),t.get("mpc_all_hits"))
