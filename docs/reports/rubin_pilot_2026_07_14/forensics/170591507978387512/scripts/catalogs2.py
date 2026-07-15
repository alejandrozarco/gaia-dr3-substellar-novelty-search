#!/usr/bin/env python
"""Round 2: datalab (fixed literals), CatWISE (fixed cols), PS1 detections with MJDs, LS DR10 viewer cat."""
import io, json
import requests
import pandas as pd
import numpy as np

RA, DEC = 313.22651, -14.84044
RAD = 0.00416667  # 15 arcsec in deg
D = "/tmp/rubin_pilot/forensics/170591507978387512"

def datalab(q, name):
    r = requests.get("https://datalab.noirlab.edu/tap/sync",
                     params={"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": q}, timeout=180)
    if r.status_code != 200 or r.text.lstrip().startswith("<"):
        print(f"{name}: HTTP {r.status_code} err {r.text[:400]}"); return pd.DataFrame()
    return pd.read_csv(io.StringIO(r.text))

q_ls = (f"SELECT ls_id, ra, dec, type, dered_mag_g, dered_mag_r, dered_mag_i, dered_mag_z, "
        f"dered_mag_w1, dered_mag_w2, snr_g, snr_r, snr_i, snr_z, ebv, "
        f"q3c_dist(ra, dec, {RA}, {DEC})*3600 AS sep_as "
        f"FROM ls_dr10.tractor WHERE q3c_radial_query(ra, dec, {RA}, {DEC}, {RAD}) ORDER BY 16")
ls = datalab(q_ls, "LS DR10")
print("=== LS DR10 tractor within 15\" ==="); print(ls.to_string(index=False) if len(ls) else "EMPTY")
ls.to_csv(f"{D}/cat_lsdr10.csv", index=False)

q_nsc = (f"SELECT id, ra, dec, gmag, rmag, imag, zmag, grms, rrms, irms, zrms, ndet, deltamjd, mjd, "
         f"q3c_dist(ra, dec, {RA}, {DEC})*3600 AS sep_as "
         f"FROM nsc_dr2.object WHERE q3c_radial_query(ra, dec, {RA}, {DEC}, {RAD}) ORDER BY 16")
nsc = datalab(q_nsc, "NSC DR2")
print("\n=== NSC DR2 object within 15\" ==="); print(nsc.to_string(index=False) if len(nsc) else "EMPTY")
nsc.to_csv(f"{D}/cat_nsc_dr2.csv", index=False)

# CatWISE2020 via VizieR (cols: RA_ICRS, DE_ICRS)
q_cw = (f"SELECT Name, RA_ICRS, DE_ICRS, W1mproPM, W2mproPM, e_W1mproPM, e_W2mproPM, "
        f"DISTANCE(POINT('ICRS', RA_ICRS, DE_ICRS), POINT('ICRS', {RA}, {DEC}))*3600 AS sep_as "
        f"FROM \"II/365/catwise\" WHERE 1=CONTAINS(POINT('ICRS', RA_ICRS, DE_ICRS), CIRCLE('ICRS', {RA}, {DEC}, {RAD}))")
r = requests.get("https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync",
                 params={"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": q_cw}, timeout=120)
try:
    cw = pd.read_csv(io.StringIO(r.text))
except Exception:
    cw = pd.DataFrame(); print("CatWISE raw:", r.text[:300])
print("\n=== CatWISE2020 within 15\" ==="); print(cw.to_string(index=False) if len(cw) else "EMPTY")
cw.to_csv(f"{D}/cat_catwise.csv", index=False)

# PS1 detections for the 0.50" object: epochs!
r = requests.get("https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/detection.csv",
                 params={"objID": 90193132266371882,
                         "columns": "[objID,obsTime,filterID,psfFlux,psfFluxErr,infoFlag,infoFlag2,infoFlag3,zp,airMass]"},
                 timeout=120)
try:
    det = pd.read_csv(io.StringIO(r.text))
except Exception:
    det = pd.DataFrame(); print("PS1 det raw:", r.text[:400])
print("\n=== PS1 DR2 detections for objID 90193132266371882 (0.50\") ===")
if len(det):
    det["mag_AB"] = -2.5*np.log10(det["psfFlux"]) + 8.90  # psfFlux in Jy
    filt = {1:"g",2:"r",3:"i",4:"z",5:"y"}
    det["band"] = det["filterID"].map(filt)
    print(det[["obsTime","band","psfFlux","psfFluxErr","mag_AB","infoFlag"]].sort_values("obsTime").to_string(index=False))
else:
    print("EMPTY")
det.to_csv(f"{D}/ps1_detections_closest.csv", index=False)

# LS DR10 viewer catalog API around position (independent check incl. faint sources)
r = requests.get("https://www.legacysurvey.org/viewer/ls-dr10/cat.json",
                 params={"ralo": RA-0.003, "rahi": RA+0.003, "declo": DEC-0.003, "dechi": DEC+0.003}, timeout=120)
try:
    cat = r.json()
    recs = []
    for i in range(len(cat.get("rd", []))):
        cra, cdec = cat["rd"][i]
        sep = np.hypot((cra-RA)*np.cos(np.radians(DEC)), cdec-DEC)*3600
        recs.append(dict(ra=cra, dec=cdec, sep_as=sep, type=cat["sourcetype"][i],
                         **{f"nmag_{b}": (cat.get(f"nanomaggies_{b}") or [None]*99)[i] if cat.get(f"nanomaggies_{b}") else None for b in []}))
    vc = pd.DataFrame(recs).sort_values("sep_as")
    print("\n=== LS DR10 viewer cat (11\" box) ==="); print(vc.head(10).to_string(index=False))
    vc.to_csv(f"{D}/cat_lsdr10_viewer.csv", index=False)
except Exception as e:
    print("viewer cat err:", e, r.text[:200])
