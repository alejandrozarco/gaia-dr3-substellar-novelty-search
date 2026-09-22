import sys, json, pickle; sys.path.insert(0, "/tmp/kk76_fix")
from common import *

FRAMES = ["j9fw91hpq", "j9fw91hqq", "j9fw91hrq", "j9fw91hsq"]
START = {"j9fw91hpq": (529.3, 543.5), "j9fw91hqq": (534.3, 545.0), "j9fw91hrq": (531.8, 547.9), "j9fw91hsq": (526.7, 546.5)}
res = {}
F = [load(r) for r in FRAMES]
# one Gaia query covering all 4 HRC frames
c = F[0]["wcs"].all_pix2world([[512, 512]], 0)[0]
G = gaia_cone(c[0], c[1], 40.0)
print(f"Gaia DR3 within 40\" of HRC centre: {len(G)} sources")
for fr in F:
    img = fr["sci"].copy(); img[(fr["dq"] & (4 | 8 | 16 | 32 | 256)) > 0] = np.nan    # bad/hot/saturated px
    bkg, noise = background(img, 41); im = img - bkg
    det = detect_components(im, noise, nsig=5.0, sm=1.5, minpix=8)
    jy = fr["tmid"].jyear
    ga = gaia_at_epoch(G, jy)
    gx, gy = fr["wcs"].all_world2pix(ga["ra"], ga["dec"], 0)
    inside = (gx > 5) & (gx < im.shape[1] - 5) & (gy > 5) & (gy < im.shape[0] - 5)
    gxy = np.c_[gx, gy]
    off = find_offset(det[:, :2], gxy[inside], search=90, binsz=1.0)
    pairs = match(det[:, :2], gxy, off, tol=4.0)
    pairs = [(k, j) for k, j in pairs if inside[k]]
    ra0, de0 = fr["wcs"].all_pix2world([[512, 512]], 0)[0]
    dra, dde = fr["wcs"].all_pix2world(det[[j for k, j in pairs], 0], det[[j for k, j in pairs], 1], 0)
    xw, yw = tangent(dra, dde, ra0, de0)
    xg, yg = tangent(ga["ra"][[k for k, j in pairs]], ga["dec"][[k for k, j in pairs]], ra0, de0)
    d_xi, d_eta = xg - xw, yg - yw
    use = np.array([ga["has_pm"][k] for k, j in pairs])
    # iterative 3-sigma clip on the shift
    keep = use.copy()
    for _ in range(5):
        mx, my = np.median(d_xi[keep]), np.median(d_eta[keep])
        r = np.hypot(d_xi - mx, d_eta - my)
        s = 1.4826 * np.median(r[keep]) + 0.005
        newk = use & (r < 3 * s)
        if (newk == keep).all(): break
        keep = newk
    sx, sy = d_xi[keep].mean(), d_eta[keep].mean()
    rx, ry = d_xi[keep].std(ddof=1), d_eta[keep].std(ddof=1)
    n = keep.sum()
    # affine (6-par) as a cross-check
    A = np.c_[np.ones(n), xw[keep], yw[keep]]
    cx, *_ = np.linalg.lstsq(A, xg[keep], rcond=None); cy, *_ = np.linalg.lstsq(A, yg[keep], rcond=None)
    # target
    x0, y0 = START[fr["root"]]
    sub = im[int(y0) - 5:int(y0) + 6, int(x0) - 5:int(x0) + 6]
    pk = np.unravel_index(np.nanargmax(ndimage.gaussian_filter(np.nan_to_num(sub), 1.0)), sub.shape)
    x1, y1 = int(x0) - 5 + pk[1], int(y0) - 5 + pk[0]
    ft = fit_source(np.nan_to_num(im), x1, y1, half=6, sig0=1.2)
    tra, tde = fr["wcs"].all_pix2world([[ft["x"], ft["y"]]], 0)[0]
    txw, tyw = tangent(tra, tde, ra0, de0)
    ra_s, de_s = untangent(txw + sx, tyw + sy, ra0, de0)
    ra_a, de_a = untangent(cx[0] + cx[1] * txw + cx[2] * tyw, cy[0] + cy[1] * txw + cy[2] * tyw, ra0, de0)
    # pixel scale for centroid error
    ps = np.sqrt(abs(np.linalg.det(fr["wcs"].pixel_scale_matrix))) * 3600
    e_cen = np.hypot(ft["ex"], ft["ey"]) / np.sqrt(2) * ps
    e_tie = np.hypot(rx, ry) / np.sqrt(2) / np.sqrt(n)
    res[fr["root"]] = dict(tmid=fr["tmid"].isot, jd=fr["tmid"].jd, ra=float(ra_s), dec=float(de_s),
                           ra_aff=float(ra_a), dec_aff=float(de_a), shift_xi=sx, shift_eta=sy, rms_xi=rx, rms_eta=ry,
                           nstar=int(n), nmatch=len(pairs), x=ft["x"], y=ft["y"], ex_pix=ft["ex"], ey_pix=ft["ey"],
                           e_cen_arcsec=e_cen, e_tie_arcsec=e_tie, fwhm_pix=2.355 * np.sqrt(ft["sx"] * ft["sy"]),
                           nmask=ft["nmask"], pixscale=ps)
    d_aff = np.hypot((ra_a - ra_s) * np.cos(np.radians(de_s)), de_a - de_s) * 3600
    print(f"{fr['root']}  t={fr['tmid'].isot}  det={len(det)}  matched={len(pairs)} used={n}  "
          f"Gaia-WCS shift=({sx:+.3f},{sy:+.3f})\" rms=({rx:.3f},{ry:.3f})\"")
    print(f"      target pix=({ft['x']:.2f},{ft['y']:.2f}) +/-({ft['ex']:.2f},{ft['ey']:.2f})px  fwhm={res[fr['root']]['fwhm_pix']:.2f}px  "
          f"masked={ft['nmask']}  RA,Dec={ra_s:.7f} {de_s:+.7f}  (affine differs by {d_aff:.3f}\")  "
          f"err: centroid {e_cen:.3f}\" + tie {e_tie:.3f}\"")
pickle.dump(res, open("pos2006.pkl", "wb"))
