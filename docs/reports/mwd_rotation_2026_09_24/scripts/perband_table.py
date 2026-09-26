# Per-band (g, r, i, comb) best peaks outside the systematics mask, from results/<sid>.json top-10 lists, with Baluev FAP.
import json, glob, os, sys
import numpy as np
sys.path.insert(0, 'scripts')
from permnull_inject import sys_mask
T = {r["source_id"]: r for r in json.load(open("data/targets.json")) + json.load(open("data/controls.json"))}
for fn in sorted(glob.glob("results/*.json")):
    z = json.load(open(fn)); sid = z["source_id"]
    if z.get("status") != "OK": print(sid, z.get("status")); continue
    s = f"{sid:>20s} {T[sid].get('group','')[:9]:9s} G={z['G']:.2f} "
    for lab in ("zg", "zr", "zi", "comb"):
        if lab not in z["pgram"]: continue
        top = [p for p in z["pgram"][lab]["top"] if not sys_mask(np.array([p["freq"]]))[0]]
        if not top: s += f"| {lab}: all top-10 masked "; continue
        p = top[0]
        s += f"| {lab}: {p['freq']:.4f} c/d ({p['P_h']:.3f} h) FAP={p['fap_baluev']:.1e} A={100*p['amp']:.2f}% "
    print(s)
