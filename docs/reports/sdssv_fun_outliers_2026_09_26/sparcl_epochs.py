"""Extra epochs for the RV candidates: SPARCL spectra (SDSS-DR17, BOSS-DR17, DESI-DR1) within 3 arcsec; H-alpha, H-beta, H-gamma
velocities against the star's SDSS-V BOSS coadd template (same method as exp_rv.py), three-line consensus."""
import sys, os, time, numpy as np, pandas as pd, requests, io
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import gas_disc_epochs as GE
sys.path.insert(0, "/tmp/hotdq/lane_fun"); import exp_rv_lib as L
C = {"63204464": "1764456441613885952", "68457205": "2190010593106909568", "67925204": "2153427951457223040", "75637719": "3185643733834595456",
     "75536894": "3168889066411928192", "78937310": "3646912496889350784"}
g = pd.read_csv(io.StringIO(requests.post("https://gea.esac.esa.int/tap-server/tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv",
      QUERY="SELECT source_id, ra, dec FROM gaiadr3.gaia_source WHERE source_id IN (" + ",".join(C.values()) + ")"), timeout=120).text), dtype={"source_id": str}).set_index("source_id")
V = pd.read_csv("cand_visits.csv", dtype={"sdss_id": str}); rows = []
for sid, gid in C.items():
    T = L.template(V[V.sdss_id == sid])
    for k in range(5):
        try: sp = GE.sparcl_spectra(float(g.loc[gid].ra), float(g.loc[gid].dec)); break
        except Exception: time.sleep(20); sp = []
    for s in sp:
        res = L.lines(s["w"], s["f"], s["iv"], T); v, e, nl = L.consensus(res)
        rows.append(dict(sdss_id=sid, gaia=gid, dataset=s["dataset"], date=s["date"], mjd=s["mjd"], **{f"v_{n}": round(x[0], 1) for n, x in res.items()}, v=v, e=e, n_lines=nl))
    print(sid, len(sp), "SPARCL spectra", flush=True)
pd.DataFrame(rows).to_csv("sparcl_epochs.csv", index=False); print(pd.DataFrame(rows).to_string())
