"""Second pass of the SDSS-V gas-disc screen: empirical photospheric templates from colour-magnitude neighbours.
Usage: python pass2.py <out.csv>
Per object (store/<last2>/<sdss_id>.npz from gasdisc_screen.py), Ca II triplet region 8250-8950 A:
  n = f / P2 (quadratic, ivar weights, +-1100 km/s around the Ca II lines and O I 8448.7 masked, 3 x 3-sigma clipping).
  Sample: WD locus (parallax/error > 3 and M_G > 8.5) plus all objects with parallax/error <= 3 (M_G from BP-RP for the
  neighbour search: 11.2 + 3.3 (BP-RP)).
  Template = pixel median of n over the K=100 nearest neighbours in (BP-RP / 0.04, M_G / 0.2) of the same group
  (H: SnowWhite class starting DA without MS; nonH: other WD classes; MS: classes with MS; CV) with coadd S/N_CaT > 10.
  Model n = b + a (template - 1), fitted outside the masked windows; r = n - model; weights w = ivar P2^2 / s^2, with
  s = max(1, 1.4826 MAD of r sqrt(ivar P2^2) outside the windows).
  Matched filter over the Ca II emission templates of gasdisc_screen.py (narrow and double-peaked, -400..+400 km/s):
  z_cat (max), per-line z, EW; null statistics: z_fake = max over the same comb shifted by -2900, +2900, +7500 km/s;
  z_abs = max of -z (absorption-like) at the true positions. Per-visit z at the coadd best template and velocity.
H-alpha region 6400-6750 A: same neighbour-template subtraction (mask +-60 A around 6564.6 for the fit); narrow emission
  kernel (sigma 3 A) scanned over 6430-6720 A: z_hae (max) and its wavelength; z_hae_c within +-400 km/s of H-alpha."""
import sys, os, numpy as np, pandas as pd, warnings
from scipy.spatial import cKDTree
warnings.filterwarnings("ignore")
sys.path.insert(0, "/tmp/hotdq/lane_gasdisc")
from gasdisc_screen import GRID, CAT, OI, HA, VEL, PROF, tmpl, C
ST = "/tmp/hotdq/lane_gasdisc/store"
MC = (GRID > 8250) & (GRID < 8950); WC = GRID[MC]; XC = (WC - 8600) / 350
MH = (GRID > 6400) & (GRID < 6750); WH = GRID[MH]; XH = (WH - 6575) / 175
WIN = np.zeros(len(WC), bool)
for lam in list(CAT) + [OI]: WIN |= np.abs(WC / lam - 1) * C < 1100
HWIN = np.abs(WH - HA) < 60
TT = {n: tmpl(CAT, vp, sg, WC) for n, vp, sg in PROF}
TL = {n: [tmpl([l], vp, sg, WC) for l in CAT] for n, vp, sg in PROF}
FAKE = {d: {n: tmpl(CAT * (1 + d / C), vp, sg, WC) for n, vp, sg in PROF} for d in (-2900, 2900, 7500)}
KC = np.arange(6430, 6721, 1.0); KH = np.exp(-0.5 * ((WH[None, :] - KC[:, None]) / 3.0) ** 2)
KHc = tmpl([HA], 0, 100, WH)

def norm(f, iv, x, mask):
    ok = np.isfinite(f) & (iv > 0); use = ok & ~mask
    for _ in range(3):
        if use.sum() < 60: return None
        p = np.polyfit(x[use], f[use], 2, w=np.sqrt(iv[use])); P = np.polyval(p, x)
        use = use & (np.abs((f - P) * np.sqrt(iv)) < 3)
    if np.median(P) <= 0: return None
    return np.where(ok, f / P, np.nan), np.where(ok, iv * P ** 2, 0.0)

def z(T, r, w):
    den = np.sqrt((T ** 2) @ w); den[den == 0] = np.inf
    return (T @ (w * r)) / den

def resid(n, w, t, mask):
    ok = (w > 0) & np.isfinite(n) & np.isfinite(t); use = ok & ~mask
    if use.sum() < 60: return None
    A = np.vstack([np.ones(use.sum()), t[use] - 1]).T * np.sqrt(w[use])[:, None]
    b, a = np.linalg.lstsq(A, n[use] * np.sqrt(w[use]), rcond=None)[0]
    r = np.where(ok, n - (b + a * (t - 1)), 0.0); ww = np.where(ok, w, 0.0)
    q = r[use] * np.sqrt(w[use]); s = max(1.0, 1.4826 * np.median(np.abs(q - np.median(q))))
    return r, ww / s ** 2, s, a

if __name__ == "__main__":
    sw = pd.read_csv("/tmp/hotdq/lane_gasdisc/sw_all.csv", dtype=str)
    o = pd.read_csv("/tmp/hotdq/lane_gasdisc/full_out.csv", dtype={"sdss_id": str}); o = o[o.status == "OK"].drop_duplicates("sdss_id")
    t = o[["sdss_id"]].merge(sw, on="sdss_id")
    t["bprp"] = t.bp_mag.astype(float) - t.rp_mag.astype(float); plx = t.plx.astype(float)
    t["MG"] = np.where(plx > 0, t.g_mag.astype(float) + 5 * np.log10(np.where(plx > 0, plx, 1) / 100), np.nan)
    good = plx / t.e_plx.astype(float) > 3
    t = t[(good & (t.MG > 8.5)) | ~good].reset_index(drop=True); good = t.plx.astype(float) / t.e_plx.astype(float) > 3
    t["MGf"] = np.where(good, t.MG, 11.2 + 3.3 * t.bprp); t["plx_ok"] = good
    c = t.classification.fillna("")
    t["grp"] = np.where(c.str.contains("CV"), "CV", np.where(c.str.contains("MS"), "MS", np.where(c.str.startswith("DA"), "H", "nonH")))
    N = len(t); NC = np.full((N, len(WC)), np.nan, np.float32); WCw = np.zeros((N, len(WC)), np.float32)
    NH = np.full((N, len(WH)), np.nan, np.float32); WHw = np.zeros((N, len(WH)), np.float32); vis = [None] * N
    for i, sid in enumerate(t.sdss_id):
        try: d = np.load(f"{ST}/{sid[-2:]}/{sid}.npz")
        except Exception: continue
        a = norm(d["f_8250"].astype(float)[:len(WC)], d["iv_8250"].astype(float)[:len(WC)], XC, WIN)
        if a is not None: NC[i], WCw[i] = a
        b = norm(d["f_6400"].astype(float)[:len(WH)], d["iv_6400"].astype(float)[:len(WH)], XH, HWIN)
        if b is not None: NH[i], WHw[i] = b
        vis[i] = (d["vf_8250"].astype(float)[:, :len(WC)], d["viv_8250"].astype(float)[:, :len(WC)], d["mjd"])
    snc = np.sqrt(np.nanmedian(np.where(WCw > 0, WCw, np.nan), axis=1)); t["snr_cat"] = np.round(snc, 1)
    feat = np.vstack([t.bprp / 0.04, t.MGf / 0.2]).T
    rows = []
    for g in ("H", "nonH", "MS", "CV"):
        gi = np.where(t.grp == g)[0]; ref = gi[(snc[gi] > 10) & np.isfinite(feat[gi]).all(1)]
        if len(ref) < 20: ref = gi
        tree = cKDTree(feat[ref]); k = min(101, len(ref))
        for i in gi:
            _, nb = tree.query(feat[i], k=k); nb = ref[np.atleast_1d(nb)]; nb = nb[nb != i][:100]
            row = dict(sdss_id=t.sdss_id.iat[i], gaia=t.gaia_dr3_source_id.iat[i], cls=t.classification.iat[i], grp=g,
                       plx_ok=bool(t.plx_ok.iat[i]), G=round(float(t.g_mag.iat[i]), 2), bprp=round(float(t.bprp.iat[i]), 3), MG=round(float(t.MG.iat[i]), 2), snr_cat=t.snr_cat.iat[i])
            tc = np.nanmedian(np.where(WCw[nb] > 0, NC[nb], np.nan), axis=0)
            rr = resid(NC[i].astype(float), WCw[i].astype(float), tc, WIN) if np.isfinite(NC[i]).sum() > 100 else None
            if rr is not None:
                r, w, s, a = rr; best = (-1e9, None, 0)
                for n in TT:
                    zz = z(TT[n], r, w); kk = int(np.argmax(zz))
                    if zz[kk] > best[0]: best = (float(zz[kk]), n, kk)
                zb, nbest, kb = best
                row.update(z_cat=round(zb, 2), tmpl=nbest, v=int(VEL[kb]), s_cat=round(s, 2), a_cat=round(a, 2),
                           z_lines="/".join(f"{z(T[kb:kb+1], r, w)[0]:.1f}" for T in TL[nbest]),
                           z_abs=round(float(max((-z(TT[n], r, w)).max() for n in TT)), 2),
                           z_fake=round(float(max(z(FAKE[d][n], r, w).max() for d in FAKE for n in TT)), 2))
                win = np.zeros(len(WC), bool)
                for lam in CAT: win |= np.abs(WC / (lam * (1 + VEL[kb] / C)) - 1) * C < 700
                row["ew_cat"] = round(float(np.sum((r * np.gradient(WC))[win & (w > 0)])), 2)
                pv = []
                if vis[i] is not None and vis[i][0].shape[0] > 1:
                    for vf, viv in zip(vis[i][0], vis[i][1]):
                        q = norm(vf, viv, XC, WIN)
                        if q is None: pv.append("nan"); continue
                        qq = resid(q[0], q[1], tc, WIN)
                        pv.append("nan" if qq is None else f"{z(TT[nbest][kb:kb+1], qq[0], qq[1])[0]:.1f}")
                row["z_visits"] = "/".join(pv); row["mjds"] = "/".join(str(m) for m in vis[i][2]) if vis[i] is not None else ""
            th = np.nanmedian(np.where(WHw[nb] > 0, NH[nb], np.nan), axis=0)
            rh = resid(NH[i].astype(float), WHw[i].astype(float), th, HWIN) if np.isfinite(NH[i]).sum() > 100 else None
            if rh is not None:
                r, w, s, a = rh; zz = z(KH, r, w); kk = int(np.argmax(zz))
                row.update(z_hae=round(float(zz[kk]), 2), hae_wl=float(KC[kk]), z_hae_c=round(float(z(KHc, r, w).max()), 2), s_ha=round(s, 2))
            rows.append(row)
    pd.DataFrame(rows).to_csv(sys.argv[1], index=False); print(len(rows), "rows")
