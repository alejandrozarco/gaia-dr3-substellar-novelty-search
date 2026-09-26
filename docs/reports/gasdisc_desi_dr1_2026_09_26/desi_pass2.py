"""Ca II triplet emission screen of the stored DESI DR1 white-dwarf spectra (desi_gas_stream.py), same method as the SDSS-V
gas_disc_screen.py pass 2: quadratic continuum 8250-8950 A with the Ca II/O I windows masked, photospheric template = pixel
median of the 100 nearest neighbours in (BP-RP/0.04, M_G/0.2) within the same group, template scaled and subtracted, matched
filter over the narrow and double-peaked emission templates (-400..+400 km/s), z_fake and z_abs controls, per-line z, EW.
Groups from the Amorim+2026 CLASS: H (starting DA, no '+'), nonH (other WD classes, no '+', not CV/AMCVn), MS (contains '+'), CV.
Colours and M_G from the Amorim file (BP-RP, MG); objects without MG use 11.2 + 3.3 (BP-RP). Output desi_pass2.csv."""
import sys, os, glob, numpy as np, pandas as pd, warnings
from scipy.spatial import cKDTree
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts"))
from gas_disc_screen import norm, z, resid, TT, TL, FAKE, WC, XC, WIN, CAT, VEL, C
a = pd.read_csv("/tmp/mwd/desi/DESI_CLASS_FINAL.txt", sep=r"\s+", dtype={"DESIID": str, "edr3id": str})
have = {os.path.basename(p)[:-4] for p in glob.glob("store/*/*.npz")}
t = a[a.DESIID.isin(have)].drop_duplicates("DESIID").reset_index(drop=True)
t["bprp"] = pd.to_numeric(t.bp_rp, errors="coerce"); t["MGv"] = pd.to_numeric(t.MG, errors="coerce")
t["MGf"] = np.where(np.isfinite(t.MGv), t.MGv, 11.2 + 3.3 * t.bprp)
c = t.CLASS.astype(str)
t["grp"] = np.where(c.str.contains("CV|AMCVn"), "CV", np.where(c.str.contains(r"\+"), "MS", np.where(c.str.startswith("DA"), "H", "nonH")))
N = len(t); NC = np.full((N, len(WC)), np.nan, np.float32); WCw = np.zeros((N, len(WC)), np.float32)
for i, tid in enumerate(t.DESIID):
    d = np.load(f"store/{tid[-2:]}/{tid}.npz"); q = norm(d["f_8250"].astype(float), d["iv_8250"].astype(float), XC, WIN)
    if q is not None: NC[i], WCw[i] = q
snc = np.sqrt(np.nanmedian(np.where(WCw > 0, WCw, np.nan), axis=1)); t["snr_cat"] = np.round(snc, 1)
feat = np.vstack([t.bprp.fillna(0) / 0.04, t.MGf.fillna(12) / 0.2]).T; rows = []
for g in ("H", "nonH", "MS", "CV"):
    gi = np.where(t.grp == g)[0]; ref = gi[(snc[gi] > 10) & np.isfinite(feat[gi]).all(1)]
    if len(ref) < 20: ref = gi
    tree = cKDTree(feat[ref]); k = min(101, len(ref))
    for i in gi:
        _, nb = tree.query(feat[i], k=k); nb = ref[np.atleast_1d(nb)]; nb = nb[nb != i][:100]
        row = dict(targetid=t.DESIID.iat[i], name=t["#Name"].iat[i], ra=t["RA(deg)"].iat[i], dec=t["DEC(deg)"].iat[i], cls=t.CLASS.iat[i], grp=g,
                   G=t.G.iat[i], bprp=t.bp_rp.iat[i], MG=t.MG.iat[i], Teff=t.Teff.iat[i], snr_cat=t.snr_cat.iat[i])
        tc = np.nanmedian(np.where(WCw[nb] > 0, NC[nb], np.nan), axis=0)
        rr = resid(NC[i].astype(float), WCw[i].astype(float), tc, WIN) if np.isfinite(NC[i]).sum() > 100 else None
        if rr is not None:
            r, w, s, aa = rr; best = (-1e9, None, 0)
            for n in TT:
                zz = z(TT[n], r, w); kk = int(np.argmax(zz))
                if zz[kk] > best[0]: best = (float(zz[kk]), n, kk)
            zb, nbest, kb = best; win = np.zeros(len(WC), bool)
            for lam in CAT: win |= np.abs(WC / (lam * (1 + VEL[kb] / C)) - 1) * C < 700
            row.update(z_cat=round(zb, 2), template=nbest, v_kms=int(VEL[kb]), noise_scale=round(s, 2),
                       z_lines="/".join(f"{z(T[kb:kb + 1], r, w)[0]:.1f}" for T in TL[nbest]),
                       z_abs=round(float(max((-z(TT[n], r, w)).max() for n in TT)), 2),
                       z_fake=round(float(max(z(FAKE[d][n], r, w).max() for d in FAKE for n in TT)), 2),
                       ew_A=round(float(np.sum((r * np.gradient(WC))[win & (w > 0)])), 2))
        rows.append(row)
pd.DataFrame(rows).to_csv(sys.argv[1] if len(sys.argv) > 1 else "desi_pass2.csv", index=False); print(len(rows), "objects")
