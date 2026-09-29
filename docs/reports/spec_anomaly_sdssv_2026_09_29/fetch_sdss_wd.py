"""Persistent store of SDSS/BOSS DR17 spectra (via SPARCL) of the 41,820 white dwarfs with SDSS spectra in Gentile Fusillo et al.
(2021, J/MNRAS/508/3877/sdssspec), built 2026-09-29 for a blind spectral-anomaly search (the SDSS-V and DESI searches found the
CH band in LP 133-754).
Stage 1: SPARCL metadata for all SDSS-DR17 and BOSS-DR17 spectra (every spectype, because unusual white dwarfs are often
classified QSO or GALAXY by the pipeline), in 2-degree RA strips -> meta/strip_RRR.csv. Failed strips go to holes.txt.
Stage 2: match each white dwarf to all spectra within 3 arcsec (Gaia EDR3 positions; SDSS epochs are 2000-2020, so proper motion
up to ~150 mas/yr stays inside) -> matches.csv.
Stage 3: retrieve matched spectra by sparcl_id in chunks of 200, interpolate flux and ivar onto a common grid
(log10 lambda = 3.5800 + 1e-4 n, 3802-9204 A, SDSS pixel spacing) -> chunks/chunk_NNNNN.npz (sparcl_id, targetid, gaia, f, iv).
Resumable: existing strip/chunk files are skipped."""
import os, time, numpy as np, pandas as pd
from sparcl.client import SparclClient
H = os.path.dirname(os.path.abspath(__file__)); M = os.path.join(H, "meta"); CH = os.path.join(H, "chunks")
os.makedirs(M, exist_ok=True); os.makedirs(CH, exist_ok=True)
c = SparclClient(connect_timeout=30, read_timeout=900); holes = []
for ra0 in range(0, 360, 2):
    fn = os.path.join(M, f"strip_{ra0:03d}.csv")
    if os.path.exists(fn): continue
    for a in range(4):
        try:
            f = c.find(outfields=["sparcl_id", "targetid", "ra", "dec", "spectype", "data_release", "specprimary"],
                       constraints={"data_release": ["SDSS-DR17", "BOSS-DR17"], "ra": [ra0, ra0 + 2], "dec": [-90, 90]}, limit=500000)
            rows = [dict(sparcl_id=r["sparcl_id"], targetid=r["targetid"], ra=r["ra"], dec=r["dec"], spectype=r["spectype"], dr=r["data_release"], prim=r["specprimary"]) for r in f.records]
            if len(rows) >= 500000: raise RuntimeError("strip hit the 500k limit")
            pd.DataFrame(rows).to_csv(fn, index=False); break
        except Exception as ex:
            err = repr(ex)[:200]; time.sleep(30 * (a + 1))
    else: holes.append(f"strip {ra0} {err}")
    print("strip", ra0, time.strftime("%H:%M:%S"), flush=True)
W = pd.read_csv(os.path.join(H, "gf21_sdssspec.csv"), dtype={"GaiaEDR3": str})
if not os.path.exists(os.path.join(H, "matches.csv")):
    Mt = pd.concat([pd.read_csv(os.path.join(M, x)) for x in sorted(os.listdir(M))], ignore_index=True)
    from astropy.coordinates import SkyCoord; import astropy.units as u
    cw = SkyCoord(W.RA_ICRS.values * u.deg, W.DE_ICRS.values * u.deg); cs = SkyCoord(Mt.ra.values * u.deg, Mt.dec.values * u.deg)
    isp, iw, sep, _ = cw.search_around_sky(cs, 3 * u.arcsec)  # returns (index into cs, index into cw, separation, distance)
    X = Mt.iloc[isp].reset_index(drop=True); X["gaia"] = W.GaiaEDR3.values[iw]; X["sep"] = sep.arcsec
    X.to_csv(os.path.join(H, "matches.csv"), index=False)
    print("matched spectra:", len(X), "white dwarfs:", X.gaia.nunique(), "of", len(W), flush=True)
X = pd.read_csv(os.path.join(H, "matches.csv"), dtype={"gaia": str})
grid = 10 ** (3.58 + 1e-4 * np.arange(3841)); np.save(os.path.join(H, "grid.npy"), grid)
ids = list(X.sparcl_id); g_of = dict(zip(X.sparcl_id, X.gaia)); N = 200
for k in range(0, len(ids), N):
    fn = os.path.join(CH, f"chunk_{k:05d}.npz")
    if os.path.exists(fn): continue
    for a in range(4):
        try:
            R = c.retrieve(uuid_list=ids[k:k + N], include=["sparcl_id", "targetid", "wavelength", "flux", "ivar"], limit=1000)
            sid, tid, gg, F, IV = [], [], [], [], []
            for x in R.records:
                w = np.array(x.wavelength, float); fl = np.array(x.flux, float); iv = np.array(x.ivar, float)
                F.append(np.interp(grid, w, fl, left=0, right=0).astype(np.float32)); IV.append(np.interp(grid, w, iv, left=0, right=0).astype(np.float32))
                sid.append(x.sparcl_id); tid.append(x.targetid); gg.append(g_of.get(x.sparcl_id, ""))
            np.savez_compressed(fn, sparcl_id=np.array(sid), targetid=np.array(tid, dtype=np.int64), gaia=np.array(gg), f=np.array(F), iv=np.array(IV)); break
        except Exception as ex:
            err = repr(ex)[:200]; time.sleep(30 * (a + 1))
    else: holes.append(f"chunk {k} {err}")
    if (k // N) % 10 == 0: print("chunk", k, "of", len(ids), time.strftime("%H:%M:%S"), flush=True)
open(os.path.join(H, "holes.txt"), "w").write("\n".join(holes))
print("DONE; holes:", len(holes), flush=True)
