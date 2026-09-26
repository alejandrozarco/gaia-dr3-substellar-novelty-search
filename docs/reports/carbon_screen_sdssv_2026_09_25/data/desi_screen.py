"""Carbon screen (carbon_screen2 method) of DESI DR1 white-dwarf spectra retrieved with SPARCL (by TARGETID), in batches.
Sample: desi_sample.csv (Amorim+2026 DESI DR1 classes; massive DA and DB/DC/DZ not in SDSS-V SnowWhite) plus controls.
DESI coadd wavelengths are vacuum; flux/ivar interpolated onto the screen grid; masked pixels (mask != 0) get ivar 0."""
import sys, os, time, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "/tmp/hotdq/lane_daq")
import carbon_screen as cs, carbon_screen2 as c2
from sparcl.client import SparclClient
c = SparclClient(read_timeout=600)
s = pd.read_csv(sys.argv[1], dtype={"DESIID": str, "edr3id": str}); outf = sys.argv[2]
done = set(pd.read_csv(outf, dtype={"targetid": str}).targetid) if os.path.exists(outf) else set()
todo = [t for t in s.DESIID if t not in done]
meta = s.set_index("DESIID")
fo = open(outf, "a")
if not done: fo.write("targetid,gaia,class,sample,C,C_v,CI,CI_v,CII,CII_v,HeI,HeI_v,snr_med,status\n")
for i in range(0, len(todo), 200):
    ids = [int(t) for t in todo[i:i + 200]]
    for k in range(3):
        try:
            r = c.retrieve_by_specid(ids, include=["specid", "flux", "ivar", "wavelength", "mask"], dataset_list=["DESI-DR1"], limit=1000); break
        except Exception as e:
            print("retrieve error", str(e)[:100], flush=True); time.sleep(30); r = None
    got = {}
    if r is not None:
        for rec in r.records:
            got.setdefault(str(rec["specid"]), rec)
    for t in todo[i:i + 200]:
        m = meta.loc[t]; g = m.edr3id; cl = m.CLASS; sm = m["sample"]
        rec = got.get(t)
        if rec is None: fo.write(f"{t},{g},{cl},{sm},,,,,,,,,,HOLE\n"); continue
        w = np.array(rec["wavelength"], float); f = np.array(rec["flux"], float); iv = np.array(rec["ivar"], float) * (np.array(rec["mask"]) == 0)
        ok = (iv > 0) & np.isfinite(f)
        if ok.sum() < 1000: fo.write(f"{t},{g},{cl},{sm},,,,,,,,,,BADSPEC\n"); continue
        fg = np.interp(cs.grid, w[ok], f[ok], left=np.nan, right=np.nan); ig = np.interp(cs.grid, w[ok], iv[ok], left=0, right=0)
        p = c2.prep(fg, ig)
        if p is None: fo.write(f"{t},{g},{cl},{sm},,,,,,,,,,BADSPEC\n"); continue
        out = {}
        for sp in ("C", "C I", "C II", "He I"):
            cc = c2.contrast(*p, sp); k = int(np.argmax(np.where(c2.INW, cc, -99))); out[sp] = (cc[k], cs.vels[k])
        snr = float(np.nanmedian(f[ok] * np.sqrt(iv[ok])))
        fo.write(f"{t},{g},{cl},{sm}," + ",".join(f"{out[sp][0]:.2f},{out[sp][1]:.0f}" for sp in ("C", "C I", "C II", "He I")) + f",{snr:.1f},ok\n")
    fo.flush(); print(i + 200, len(todo), flush=True)
print("DESI_DONE", flush=True)
