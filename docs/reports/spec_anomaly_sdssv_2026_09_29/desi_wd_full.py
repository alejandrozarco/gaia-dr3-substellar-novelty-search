"""DESI DR1 white dwarfs beyond the DESI class table (2026-09-29). LP 133-754 is in DESI DR1 but not in DESI_CLASS_FINAL.txt, so the
CH sweep over that table was incomplete.
1. SPARCL metadata for all DESI-DR1 spectype STAR spectra in 2-degree RA strips -> meta/strip_RRR.csv (holes.txt on failure).
2. Match to Gentile Fusillo et al. (2021) white dwarfs with Pwd > 0.5 (gf21_pwd05.csv) within 1.5 arcsec -> matches.csv.
3. For matches with TeffH < 9000 K whose TARGETID is not in the class-table store (../class_table.csv), retrieve the spectra and
   measure the CH G-band index (1 - mean 4285-4316 A over the median of 4235-4262 and 4322-4332 A) -> ch_new.csv.
Resumable."""
import os, time, numpy as np, pandas as pd
from sparcl.client import SparclClient
H = os.path.dirname(os.path.abspath(__file__)); M = os.path.join(H, "meta"); os.makedirs(M, exist_ok=True)
c = SparclClient(connect_timeout=30, read_timeout=900); holes = []
for ra0 in range(0, 360, 2):
    fn = os.path.join(M, f"strip_{ra0:03d}.csv")
    if os.path.exists(fn): continue
    for a in range(4):
        try:
            f = c.find(outfields=["sparcl_id", "targetid", "ra", "dec", "specprimary"], constraints={"data_release": ["DESI-DR1"], "spectype": ["STAR"], "ra": [ra0, ra0 + 2], "dec": [-90, 90]}, limit=500000)
            if len(f.records) >= 500000: raise RuntimeError("limit reached")
            pd.DataFrame([dict(sparcl_id=r["sparcl_id"], targetid=r["targetid"], ra=r["ra"], dec=r["dec"], prim=r["specprimary"]) for r in f.records]).to_csv(fn, index=False); break
        except Exception as ex: err = repr(ex)[:150]; time.sleep(30 * (a + 1))
    else: holes.append(f"strip {ra0} {err}")
print("strips done; holes", holes, flush=True)
if not os.path.exists(os.path.join(H, "matches.csv")):
    from astropy.coordinates import SkyCoord; import astropy.units as u
    Mt = pd.concat([pd.read_csv(os.path.join(M, x)) for x in sorted(os.listdir(M)) if os.path.getsize(os.path.join(M, x)) > 10], ignore_index=True)
    W = pd.read_csv(os.path.join(H, "gf21_pwd05.csv"), dtype={"GaiaEDR3": str})
    cw = SkyCoord(W.RA_ICRS.values * u.deg, W.DE_ICRS.values * u.deg); cs = SkyCoord(Mt.ra.values * u.deg, Mt.dec.values * u.deg)
    isp, iw, sep, _ = cw.search_around_sky(cs, 1.5 * u.arcsec)
    X = Mt.iloc[isp].reset_index(drop=True); X["gaia"] = W.GaiaEDR3.values[iw]; X["TeffH"] = W.TeffH.values[iw]; X["MassH"] = W.MassH.values[iw]; X["Pwd"] = W.Pwd.values[iw]; X["Gmag"] = W.Gmag.values[iw]; X["sep"] = sep.arcsec
    X.to_csv(os.path.join(H, "matches.csv"), index=False); print("DESI STAR spectra:", len(Mt), "matched to GF21:", len(X), "white dwarfs", X.gaia.nunique(), flush=True)
X = pd.read_csv(os.path.join(H, "matches.csv"), dtype={"gaia": str})
known = set(pd.read_csv(os.path.join(H, "..", "class_table.csv")  # DESI class-table store (fetch_desi_wd.py), dtype=str).DESIID.astype(np.int64))
todo = X[(X.TeffH < 9000) & ~X.targetid.isin(known)].drop_duplicates("sparcl_id")
print("cool (TeffH < 9000) spectra not in the class table:", len(todo), "of", int((X.TeffH < 9000).sum()), flush=True)
out = os.path.join(H, "ch_new.csv"); rows = pd.read_csv(out).to_dict("records") if os.path.exists(out) else []; done = {r["sparcl_id"] for r in rows}
ids = [s for s in todo.sparcl_id if s not in done]; info = todo.set_index("sparcl_id")
def idx(w, f, iv, band=(4285, 4316), cont=((4235, 4262), (4322, 4332))):
    ok = iv > 0; cm = (((w > cont[0][0]) & (w < cont[0][1])) | ((w > cont[1][0]) & (w < cont[1][1]))) & ok; bm = (w > band[0]) & (w < band[1]) & ok
    if cm.sum() < 5 or bm.sum() < 5: return np.nan, np.nan
    cc = np.average(f[cm], weights=iv[cm]); b = np.average(f[bm], weights=iv[bm])
    return 1 - b / cc, np.hypot(1 / np.sqrt(iv[bm].sum()) / cc, b / np.sqrt(iv[cm].sum()) / cc ** 2)
for k in range(0, len(ids), 200):
    for a in range(3):
        try:
            R = c.retrieve(uuid_list=ids[k:k + 200], include=["sparcl_id", "targetid", "wavelength", "flux", "ivar"], limit=1000); break
        except Exception: time.sleep(30 * (a + 1)); R = None
    if R is None: holes.append(f"retrieve {k}"); continue
    for x in R.records:
        w, f, iv = np.array(x.wavelength), np.array(x.flux, float), np.array(x.ivar, float); ch, e = idx(w, f, iv)
        sn = float(np.nanmedian((f * np.sqrt(np.clip(iv, 0, None)))[(w > 4500) & (w < 5500)])); r0 = info.loc[x.sparcl_id]
        rows.append(dict(sparcl_id=x.sparcl_id, targetid=x.targetid, gaia=r0.gaia, TeffH=r0.TeffH, MassH=r0.MassH, Gmag=r0.Gmag, snr=sn, ch=ch, e=e, z=ch / e if e and e > 0 else np.nan))
        if np.isfinite(ch) and e > 0 and ch / e > 5 and sn > 3: np.savez(os.path.join(H, f"spec_{x.targetid}.npz"), w=w, f=f, iv=iv)
    pd.DataFrame(rows).to_csv(out, index=False); print(k, len(rows), time.strftime("%H:%M:%S"), flush=True)
open(os.path.join(H, "holes.txt"), "w").write("\n".join(holes)); print("DONE; holes", len(holes), flush=True)
