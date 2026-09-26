# Review screen outputs: flag strong IR periods not at WISE-orbit aliases, with IR/optical amplitude ratio
import json, sys, numpy as np
F_ORB = 1/0.065631  # WISE orbital frequency (c/d), ~15.237
def alias(f):
    for k in range(1, 5):
        if abs(f - k*F_ORB) < 0.4: return f"k={k} orbit"
    for k in range(1, 5):
        for j in (-1, 1):
            if abs(f - (k*F_ORB + j*0.0)) < 0.25: return "orbit"
    return ""
for fn in sys.argv[1:]:
    rows = [json.loads(l) for l in open(fn)]
    ok = [o for o in rows if o.get("status") == "OK_WISE"]
    holes = [o for o in rows if o.get("status", "").startswith("HOLE")]
    print(f"== {fn}: {len(rows)} done, {len(ok)} with WISE, {len(holes)} holes, {sum(1 for o in rows if o.get('status','').startswith('FEW'))} too few epochs")
    for o in ok:
        f = 1/o["P"]; al = alias(f)
        if o["pow_w1"] < 0.25 or o["A_W1"] < 0.15: continue
        z = o.get("ztf") if isinstance(o.get("ztf"), dict) else {}
        zr = z.get("zr") or z.get("zg")
        ratio = o["A_W1"]/max(zr["A"], 0.02) if zr else None
        zp = ", ".join(f"{b}: Pbest {v['Pbest']:.6f} pow {v['pow_best']:.2f} A@Pw {v['A']:.3f}+-{v['eA']:.3f} (n={v['n']})" for b, v in z.items()) if z else str(o.get("ztf"))
        print(f"  {o['designation']} Gaia {o['gaia']} G={o['G']:.2f} BP-RP={o['bprp']:.2f} plx={o['plx']:.2f} | W1 P={o['P']:.7f} pow={o['pow_w1']:.2f} A_W1={o['A_W1']:.2f}+-{o['eA_W1']:.2f}"
              f"{' A_W2=%.2f' % o['A_W2'] if o.get('A_W2') else ''} | ratio={ratio if ratio is None else round(ratio, 1)} {'[ALIAS '+al+']' if al else ''}\n      ZTF: {zp}")
