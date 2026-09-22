import sys, pickle; sys.path.insert(0, "/tmp/kk76_fix")
from common import *
from fitlib import offset_arcsec, HV
FB = pickle.load(open("/tmp/kk76_fix/fits/fitB.pkl", "rb"))
R10 = ["ib2k52cvq", "ib2k52cwq", "ib2k52cxq", "ib2k52cyq", "ib2k52czq", "ib2k52d0q", "ib2k52d2q", "ib2k52d3q"]
PRED = dict(zip(R10, FB["pB10"]))
GUIDE = None   # (dRA*cosDec, dDec) arcsec, set from the UVIS frames before the IR frames are measured
res = {}
Gcache = {}
for root in R10:
    fr = load(root)
    ir = fr["h0"]["DETECTOR"] == "IR"
    img = fr["sci"].copy(); img[(fr["dq"] & (4 | 16 | 256)) > 0] = np.nan
    bkg, noise = background(img, 25 if ir else 41); im = img - bkg
    ny, nx = im.shape
    ps = np.sqrt(abs(np.linalg.det(fr["wcs"].pixel_scale_matrix))) * 3600
    ra0, de0 = fr["wcs"].all_pix2world([[nx / 2, ny / 2]], 0)[0]
    key = "IR" if ir else "UVIS"
    if key not in Gcache: Gcache[key] = gaia_cone(ra0, de0, 110.0 if ir else 25.0)
    G = Gcache[key]
    ga = gaia_at_epoch(G, fr["tmid"].jyear)
    det = detect_peaks(im, noise, nsig=6.0, sm=0.8 if ir else 1.0, win=2 if ir else 3)
    gx, gy = fr["wcs"].all_world2pix(ga["ra"], ga["dec"], 0)
    inside = (gx > 4) & (gx < nx - 4) & (gy > 4) & (gy < ny - 4) & ga["has_pm"] & (ga["g"] < 21.0)
    gxy = np.c_[gx, gy]
    off = find_offset(det[:, :2], gxy[inside], search=12 if ir else 30, binsz=0.5 if ir else 1.0)
    pairs = [(k, j) for k, j in match(det[:, :2], gxy, off, tol=1.2 if ir else 2.5) if inside[k]]
    K = np.array([k for k, j in pairs]); J = np.array([j for k, j in pairs])
    dra, dde = fr["wcs"].all_pix2world(det[J, 0], det[J, 1], 0)
    xw, yw = tangent(dra, dde, ra0, de0); xg, yg = tangent(ga["ra"][K], ga["dec"][K], ra0, de0)
    d_xi, d_eta = xg - xw, yg - yw
    keep = np.ones(len(K), bool)
    for _ in range(6):
        mx, my = np.median(d_xi[keep]), np.median(d_eta[keep])
        r = np.hypot(d_xi - mx, d_eta - my); s = 1.4826 * np.median(r[keep]) + 0.003
        nk = r < 3 * s
        if (nk == keep).all(): break
        keep = nk
    sx, sy = d_xi[keep].mean(), d_eta[keep].mean(); rx, ry = d_xi[keep].std(ddof=1), d_eta[keep].std(ddof=1); n = keep.sum()
    A = np.c_[np.ones(n), xw[keep], yw[keep]]
    cx, *_ = np.linalg.lstsq(A, xg[keep], rcond=None); cy, *_ = np.linalg.lstsq(A, yg[keep], rcond=None)
    # predicted target -> pixel through the Gaia-corrected mapping (shift)
    pra, pde = PRED[root]
    if ir:
        uv = [res[k]["meas_minus_predB"] for k in R10[:4] if k in res]
        GUIDE = (np.mean([u[0] for u in uv]), np.mean([u[1] for u in uv]))
        pde_g = pde + GUIDE[1] / 3600.0; pra_g = pra + GUIDE[0] / 3600.0 / np.cos(np.radians(pde))
    pxi, peta = tangent(pra_g, pde_g, ra0, de0) if ir else tangent(pra, pde, ra0, de0)
    wra, wde = untangent(pxi - sx, peta - sy, ra0, de0)
    px, py = fr["wcs"].all_world2pix([[float(wra), float(wde)]], 0)[0]
    # search for the source within 1.5" of the prediction
    rad = (0.3 if ir else 1.2) / ps
    sm = ndimage.gaussian_filter(np.nan_to_num(im), 1.0 if not ir else 0.7)
    yy, xx = np.mgrid[0:ny, 0:nx]
    win = np.hypot(xx - px, yy - py) < rad
    cand = (sm == ndimage.maximum_filter(sm, size=5)) & win & (sm > 5 * (np.nanmedian(np.abs(sm - np.nanmedian(sm))) * 1.4826))
    cy_, cx_ = np.nonzero(cand)
    order = np.argsort(np.hypot(cx_ - px, cy_ - py))          # NEAREST to the prediction first
    cands = [(cx_[i], cy_[i], sm[cy_[i], cx_[i]]) for i in order[:5]]
    best = None
    for (x1, y1, v) in cands:
        ft = fit_source(np.nan_to_num(im), x1, y1, half=5 if ir else 6, sig0=0.6 if ir else 1.0)
        if ft["sx"] < (0.45 if ir else 0.6) or ft["sy"] < (0.45 if ir else 0.6): continue   # too sharp: cosmic ray
        best = ft; break
    if best is None:
        print(root, "NO SOURCE near the prediction; candidates:", cands); continue
    tra, tde = fr["wcs"].all_pix2world([[best["x"], best["y"]]], 0)[0]
    txw, tyw = tangent(tra, tde, ra0, de0)
    ra_s, de_s = untangent(txw + sx, tyw + sy, ra0, de0)
    ra_a, de_a = untangent(cx[0] + cx[1] * txw + cx[2] * tyw, cy[0] + cy[1] * txw + cy[2] * tyw, ra0, de0)
    e_cen = np.hypot(best["ex"], best["ey"]) / np.sqrt(2) * ps
    e_tie = np.hypot(rx, ry) / np.sqrt(2) / np.sqrt(n)
    mo = offset_arcsec(float(ra_s), float(de_s), pra, pde)
    d_aff = offset_arcsec(float(ra_a), float(de_a), float(ra_s), float(de_s))
    res[root] = dict(tmid=HV[root]["isot"], ra=float(ra_s), dec=float(de_s), ra_aff=float(ra_a), dec_aff=float(de_a),
                     shift_xi=sx, shift_eta=sy, rms_xi=rx, rms_eta=ry, nstar=int(n), x=best["x"], y=best["y"],
                     e_cen_arcsec=e_cen, e_tie_arcsec=e_tie, fwhm_pix=2.355 * np.sqrt(best["sx"] * best["sy"]),
                     flux=best["flux"], meas_minus_predB=mo, filt=fr["h0"].get("FILTER"), det=fr["h0"]["DETECTOR"], pixscale=ps)
    print(f"{root} {fr['h0']['DETECTOR']:4s} {fr['h0'].get('FILTER'):6s} stars used {n:3d} Gaia-WCS shift ({sx:+.3f},{sy:+.3f})\" rms ({rx:.3f},{ry:.3f})  "
          f"target ({best['x']:.2f},{best['y']:.2f}) fwhm {res[root]['fwhm_pix']:.2f}px  meas-predB ({mo[0]:+.3f},{mo[1]:+.3f})\"  "
          f"affine-shift ({d_aff[0]:+.3f},{d_aff[1]:+.3f})\"  err cen {e_cen:.3f} tie {e_tie:.3f}")
pickle.dump(res, open("/tmp/kk76_fix/pos2010.pkl", "wb"))
