"""Persistent store of DESI DR1 coadded spectra for every object in the DESI white-dwarf class table (DESI_CLASS_FINAL.txt,
44,417 rows), retrieved by TARGETID from SPARCL (2026-09-29).
Each chunk file chunks/chunk_NNNNN.npz holds up to 200 spectra: targetid, specprimary flag, survey/program, and flux/ivar
rebinned by 2 onto a common grid (grid.npy, 1.6 A pixels, 3600-9824 A). Failed chunks are listed in holes.txt and retried on rerun.
Usage: python fetch_desi_wd.py   (resumable: existing chunk files are skipped)."""
import os, time, numpy as np, pandas as pd
from sparcl.client import SparclClient
H = os.path.dirname(os.path.abspath(__file__)); CH = os.path.join(H, "chunks"); os.makedirs(CH, exist_ok=True)
T = pd.read_csv(os.path.expanduser("~/claude_projects/white-dwarfs-2026/data/cache/DESI_CLASS_FINAL.txt"), sep=r"\s+", comment=None, dtype=str)
T.columns = [c.lstrip("#") for c in T.columns]
T.to_csv(os.path.join(H, "class_table.csv"), index=False)
ids = sorted(set(int(x) for x in T.DESIID))
c = SparclClient(connect_timeout=30, read_timeout=600)
grid = None; holes = []; N = 200
for k in range(0, len(ids), N):
    fn = os.path.join(CH, f"chunk_{k:05d}.npz")
    if os.path.exists(fn): continue
    ch = ids[k:k + N]
    for a in range(4):
        try:
            f = c.find(outfields=["sparcl_id", "targetid", "specprimary", "program"], constraints={"targetid": ch, "data_release": ["DESI-DR1"]}, limit=2000)
            meta = {r["sparcl_id"]: r for r in f.records}
            R = c.retrieve(uuid_list=list(meta), include=["sparcl_id", "targetid", "wavelength", "flux", "ivar"], limit=2000)
            tid, prim, prog, F, IV = [], [], [], [], []
            for x in R.records:
                w = np.array(x.wavelength); fl = np.array(x.flux, float); iv = np.array(x.ivar, float)
                n2 = len(w) // 2
                if grid is None:
                    grid = 0.5 * (w[0:2*n2:2] + w[1:2*n2:2]); np.save(os.path.join(H, "grid.npy"), grid)
                fr = fl[:2*n2].reshape(-1, 2); ir = iv[:2*n2].reshape(-1, 2); s = ir.sum(1)
                F.append(np.where(s > 0, (fr * ir).sum(1) / np.where(s > 0, s, 1), 0).astype(np.float32)); IV.append(s.astype(np.float32))
                m = meta.get(x.sparcl_id, {}); tid.append(x.targetid); prim.append(bool(m.get("specprimary", True))); prog.append(str(m.get("program", "")))
            np.savez_compressed(fn, targetid=np.array(tid, dtype=np.int64), specprimary=np.array(prim), program=np.array(prog), f=np.array(F), iv=np.array(IV))
            break
        except Exception as ex:
            err = repr(ex)[:200]; time.sleep(30 * (a + 1))
    else: holes.append(f"{k} {err}")
    if (k // N) % 10 == 0: print(k, "of", len(ids), time.strftime("%H:%M:%S"), flush=True)
open(os.path.join(H, "holes.txt"), "w").write("\n".join(holes))
print("DONE; holes:", len(holes), flush=True)
