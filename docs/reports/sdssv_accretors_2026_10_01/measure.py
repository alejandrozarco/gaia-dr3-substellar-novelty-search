"""Emission-line EWs (emission POSITIVE, vacuum A, observed frame) on BOSS v6_2_1 spec-lite coadds in spec/.
EW = sum((f/c - 1) dlam) over the line window, c = weighted linear fit to two side bands. Error from ivar.
Also: [O III] 5008, [N II] 6585, [O I] 6302, [S II] 6718/6733, Li 6709 (absorption is negative), blue/red flux ratio.
Output: lines.csv (one row per file)."""
import os, sys, glob, numpy as np, pandas as pd
from astropy.io import fits
from concurrent.futures import ProcessPoolExecutor
D = os.path.dirname(os.path.abspath(__file__))
FEAT = {  # name: (line lo, hi, [(cont lo, hi), ...])
 "Ha": (6534, 6596, [(6470, 6510), (6620, 6660)]),
 "Hb": (4832, 4894, [(4780, 4820), (4905, 4935)]),
 "Hg": (4316, 4368, [(4270, 4300), (4380, 4410)]),
 "HeI4473": (4462, 4484, [(4430, 4455), (4495, 4520)]),
 "HeII4687": (4676, 4698, [(4640, 4665), (4710, 4730)]),
 "HeI5877": (5865, 5890, [(5820, 5855), (5905, 5940)]),
 "HeI6680": (6669, 6692, [(6620, 6655), (6700, 6740)]),
 "HeI7067": (7056, 7079, [(7010, 7045), (7090, 7120)]),
 "OIII5008": (5002, 5014, [(4970, 4995), (5030, 5060)]),
 "NII6585": (6580, 6590, [(6620, 6660), (6600, 6610)]),
 "OI6302": (6296, 6308, [(6260, 6290), (6320, 6350)]),
 "SII6718": (6713, 6738, [(6745, 6780), (6690, 6705)]),
 "CaII8544": (8530, 8558, [(8500, 8525), (8565, 8590)]),
}
def ew(w, f, iv, a, b, cs):
    m = np.zeros_like(w, bool)
    for c0, c1 in cs: m |= (w > c0) & (w < c1)
    m &= (iv > 0) & np.isfinite(f); k = (w > a) & (w < b) & (iv > 0) & np.isfinite(f)
    if m.sum() < 8 or k.sum() < 6: return np.nan, np.nan, np.nan
    p = np.polyfit(w[m], f[m], 1, w=np.sqrt(iv[m])); c = np.polyval(p, w)
    cm = np.median(c[k])
    if cm <= 0: return np.nan, np.nan, np.nan
    dw = np.gradient(w)[k]
    e = float(np.sum((f[k] / c[k] - 1) * dw)); s = float(np.sqrt(np.sum((1 / np.sqrt(iv[k]) / c[k] * dw) ** 2)))
    pk = float(np.max(f[k] / c[k]))
    return e, s, pk
def one(p):
    try:
        with fits.open(p, memmap=False) as h:
            d = h[1].data; w = 10 ** d["LOGLAM"].astype(float); f = d["FLUX"].astype(float); iv = d["IVAR"].astype(float)
            iv[(d["AND_MASK"] > 0)] = 0
            sp = h[2].data[0]; z = h[3].data[0]
            r = dict(fname=os.path.basename(p), sdss_id=str(sp["SDSS_ID"]), catalogid=str(sp["CATALOGID"]), cls=z["CLASS"].strip(), subcls=z["SUBCLASS"].strip(), z=float(z["Z"]), sn=float(z["SN_MEDIAN_ALL"]))
        for k, (a, b, cs) in FEAT.items():
            e, s, pk = ew(w, f, iv, a, b, cs); r[k] = e; r["e_" + k] = s; r["pk_" + k] = pk
        def med(a, b):
            k = (w > a) & (w < b) & (iv > 0); return float(np.median(f[k])) if k.sum() > 10 else np.nan
        r["f4200"] = med(4100, 4300); r["f6100"] = med(6000, 6200); r["f8100"] = med(8000, 8200)
        r["status"] = "ok"
    except Exception as ex:
        r = dict(fname=os.path.basename(p), status=f"ERR {type(ex).__name__} {str(ex)[:60]}")
    return r
if __name__ == "__main__":
    fs = sorted(glob.glob(os.path.join(D, "spec", "spec-*.fits")))
    with ProcessPoolExecutor(6) as ex: R = list(ex.map(one, fs, chunksize=20))
    pd.DataFrame(R).to_csv(os.path.join(D, "lines.csv"), index=False); print(len(R), "measured")
