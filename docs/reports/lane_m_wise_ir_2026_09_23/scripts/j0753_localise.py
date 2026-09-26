# VarWISE J075330.99-004209.7 = Gaia DR3 3082614748370926848: bright-minus-faint localisation of the variable W1 flux
# (requested 2026-09-23 after the external review). NEOWISE-R W1 L1b frames (IRSA IBE), phased on P = 0.1053647 d with the phase
# of the light-curve plateau and dip taken from the NEOWISE detections (BJD_TDB, 4-harmonic template). Frames are background-
# subtracted, scaled to MAGZP 22.5, resampled with their own WCS (incl. SIP) onto a 0.5" tangent-plane grid centred on the Gaia
# position propagated to 2019.5, stacked (mean) per phase set; the difference image is centroided with a 2D Gaussian. Registration
# check: centroids of Gaia field stars in the all-frame stack. Uncertainty: bootstrap over frames; repeated per scan direction.
import os, io, json, subprocess, time, warnings, numpy as np
warnings.filterwarnings("ignore")
from concurrent.futures import ThreadPoolExecutor
from astropy.io import ascii, fits
from astropy.wcs import WCS
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
RA16, DE16, PMRA, PMDE = 118.37915389890948, -0.7026847809804327, 8.3706, -8.7146
EP = 2019.5
RA0 = RA16 + PMRA * (EP - 2016.0) / 3.6e6 / np.cos(np.radians(DE16)); DE0 = DE16 + PMDE * (EP - 2016.0) / 3.6e6
P = 0.1053647
c0 = SkyCoord(RA0 * u.deg, DE0 * u.deg); geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
def bjd(mjd):
    t = Time(mjd, format="mjd", scale="utc", location=geo); return (t.tdb + t.light_travel_time(c0)).jd
# --- phase reference from the detections (4-harmonic template)
d = np.genfromtxt("../data/j0753_neowise_lc.csv", delimiter=",", skip_header=1, names=True)
tb = bjd(d["mjd"]); Fd = 10 ** (-0.4 * (d["w1mpro"] - 15.0)); w = d["w1sigmpro"]
ph = (tb / P) % 1
X = np.vstack([np.ones_like(ph)] + [fn(2 * np.pi * k * ph) for k in range(1, 5) for fn in (np.cos, np.sin)]).T
b, *_ = np.linalg.lstsq(X, Fd, rcond=None)
grid = np.linspace(0, 1, 1000, endpoint=False)
tmpl = np.vstack([np.ones_like(grid)] + [fn(2 * np.pi * k * grid) for k in range(1, 5) for fn in (np.cos, np.sin)]).T @ b
fmax, fmin = tmpl.max(), tmpl.min(); ph_min = grid[np.argmin(tmpl)]; ph_max = grid[np.argmax(tmpl)]
def level(p):   # template flux fraction between min (0) and max (1) at phase p
    Xp = np.vstack([np.ones_like(p)] + [fn(2 * np.pi * k * p) for k in range(1, 5) for fn in (np.cos, np.sin)]).T
    return (Xp @ b - fmin) / (fmax - fmin)
print(f"template: dip at phase {ph_min:.3f}, max at {ph_max:.3f}; plateau fraction (level>0.8) {np.mean(level(grid) > 0.8):.2f}, dip fraction (level<0.25) {np.mean(level(grid) < 0.25):.2f}", flush=True)
# --- frames
tab = ascii.read("frames_neo.tbl", format="ipac")
cols = tab.colnames
keep = np.ones(len(tab), bool)
if "qual_frame" in cols: keep &= np.array(tab["qual_frame"]) > 0
if "saa_sep" in cols: keep &= np.array(tab["saa_sep"]) > 0
tab = tab[keep]
os.makedirs("cut", exist_ok=True)
def get(row):
    sid, fn, sg = str(row["scan_id"]), int(row["frame_num"]), str(row["scangrp"])
    fnm = f"cut/{sid}{fn:03d}.fits"
    if os.path.exists(fnm) and os.path.getsize(fnm) > 2880: return fnm
    url = (f"https://irsa.ipac.caltech.edu/ibe/data/wise/neowiser/p1bm_frm/{sg}/{sid}/{fn:03d}/{sid}{fn:03d}-w1-int-1b.fits"
           f"?center={RA0},{DE0}&size=200arcsec&gzip=false")
    for k in range(4):
        p = subprocess.run(["curl", "-s", "--max-time", "300", "-o", fnm, url], capture_output=True)
        if os.path.exists(fnm) and os.path.getsize(fnm) > 2880:
            try:
                fits.getheader(fnm); return fnm
            except Exception: pass
        time.sleep(10 * (k + 1))
    return None
with ThreadPoolExecutor(max_workers=4) as ex:
    files = list(ex.map(get, tab))
ok = [i for i, f in enumerate(files) if f]
print(f"frames: {len(tab)} after quality cuts; cutouts retrieved {len(ok)} (holes {len(tab) - len(ok)})", flush=True)
# --- common grid
pix = 0.5; half = 80                       # 161 x 161 px of 0.5" = 80" box
yy, xx = np.mgrid[-half:half + 1, -half:half + 1]
xi = -xx * pix / 3600.0; eta = yy * pix / 3600.0   # east to the left (x increases west), north up
ra0r, de0r = np.radians(RA0), np.radians(DE0)
den = np.cos(de0r) - np.radians(eta) * np.sin(de0r)
ra_g = np.degrees(ra0r + np.arctan2(np.radians(xi), den))
de_g = np.degrees(np.arctan2(np.sin(de0r) + np.radians(eta) * np.cos(de0r), np.hypot(np.radians(xi), den)))
imgs, mjds, crotas = [], [], []
for i in ok:
    try:
        h = fits.open(files[i]); data = h[0].data.astype(float); hd = h[0].header; wc = WCS(hd)
        zp = hd.get("MAGZP", float(tab["magzp"][i]))
        good = np.isfinite(data); med = np.nanmedian(data[good]); mad = 1.4826 * np.nanmedian(np.abs(data[good] - med))
        bk = np.nanmedian(data[good & (np.abs(data - med) < 3 * mad)])
        img = (data - bk) * 10 ** (-0.4 * (zp - 22.5))
        px, py = wc.all_world2pix(ra_g, de_g, 0)
        res = map_coordinates(np.nan_to_num(img), [py, px], order=1, mode="constant", cval=np.nan)
        inside = (px > 1) & (px < data.shape[1] - 2) & (py > 1) & (py < data.shape[0] - 2)
        res[~inside] = np.nan
        if np.isnan(res[half - 10:half + 11, half - 10:half + 11]).any(): continue
        imgs.append(res); mjds.append(float(tab["mjd_obs"][i])); crotas.append(float(np.degrees(np.arctan2(hd["CD2_1"], -hd["CD1_1"]))))
    except Exception as e:
        print("skip", files[i], type(e).__name__, flush=True)
imgs = np.array(imgs); mjds = np.array(mjds); crotas = np.array(crotas)
phs = (bjd(mjds) / P) % 1; lev = level(phs)
bright = lev > 0.8; faint = lev < 0.25
print(f"usable frames {len(imgs)}: bright {bright.sum()}, faint {faint.sum()}", flush=True)
def gauss_fit(im, x0=0.0, y0=0.0, box=14):
    c = half; s = slice(c - box, c + box + 1); sub = im[s, s]; Y, Xg = np.mgrid[-box:box + 1, -box:box + 1] * pix
    m = np.isfinite(sub)
    def f(p): return (p[0] * np.exp(-((Xg - p[1]) ** 2 + (Y - p[2]) ** 2) / (2 * p[3] ** 2)) + p[4] - sub)[m]
    r = least_squares(f, [np.nanmax(sub), x0, y0, 2.6, 0.0], bounds=([-np.inf, -6, -6, 1.0, -np.inf], [np.inf, 6, 6, 6.0, np.inf]))
    return r.x   # amp, x(" west positive), y(" north), sigma("), bkg
def stack(sel): return np.nanmean(imgs[sel], axis=0)
D = stack(bright) - stack(faint); A = stack(np.ones(len(imgs), bool))
pD = gauss_fit(D); pA = gauss_fit(A)
# --- registration check with Gaia field stars (G < 17.5) inside the box
q = (f"SELECT ra, dec, pmra, pmdec, phot_g_mean_mag FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT(ra,dec), CIRCLE({RA16},{DE16},{75/3600})) "
     f"AND phot_g_mean_mag < 17.5")
import urllib.parse, csv
out = subprocess.run(["curl", "-sL", "--max-time", "120", "https://gea.esac.esa.int/tap-server/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT=csv&QUERY=" + urllib.parse.quote(q)], capture_output=True, text=True).stdout
stars = list(csv.DictReader(io.StringIO(out)))
offs = []
for s in stars:
    ra = float(s["ra"]) + float(s["pmra"] or 0) * (EP - 2016) / 3.6e6 / np.cos(np.radians(DE16)); de = float(s["dec"]) + float(s["pmdec"] or 0) * (EP - 2016) / 3.6e6
    dx = -(ra - RA0) * np.cos(np.radians(DE0)) * 3600; dy = (de - DE0) * 3600      # grid x positive west
    if np.hypot(dx, dy) < 5 or abs(dx) > 34 or abs(dy) > 34: continue
    ix, iy = int(round(half + dx / pix)), int(round(half + dy / pix)); box = 12
    sub = A[iy - box:iy + box + 1, ix - box:ix + box + 1]
    if sub.shape != (2 * box + 1, 2 * box + 1) or np.isnan(sub).any(): continue
    Y, Xg = np.mgrid[-box:box + 1, -box:box + 1] * pix
    r = least_squares(lambda p: (p[0] * np.exp(-((Xg - p[1]) ** 2 + (Y - p[2]) ** 2) / (2 * p[3] ** 2)) + p[4] - sub).ravel(), [sub.max(), 0, 0, 2.6, 0])
    if r.x[0] > 0 and r.x[3] < 5: offs.append((float(s["phot_g_mean_mag"]), float(r.x[1]), float(r.x[2])))
offs = np.array(offs)
reg = (np.median(offs[:, 1]), np.median(offs[:, 2])) if len(offs) else (0.0, 0.0)
# --- bootstrap and scan-direction split
rng = np.random.default_rng(11); bi, fi = np.where(bright)[0], np.where(faint)[0]; bs = []
for k in range(200):
    Db = np.nanmean(imgs[rng.choice(bi, len(bi))], axis=0) - np.nanmean(imgs[rng.choice(fi, len(fi))], axis=0)
    bs.append(gauss_fit(Db)[1:3])
bs = np.array(bs)
asc = np.cos(np.radians(crotas)) > 0
split = {}
for lab, m in (("crota cos>0", asc), ("crota cos<0", ~asc)):
    if (bright & m).sum() >= 8 and (faint & m).sum() >= 8:
        split[lab] = [float(v) for v in gauss_fit(stack(bright & m) - stack(faint & m))[1:3]] + [int((bright & m).sum()), int((faint & m).sum())]
res = dict(object="VarWISE J075330.99-004209.7 = Gaia DR3 3082614748370926848", epoch=EP, n_frames=int(len(imgs)), n_bright=int(bright.sum()), n_faint=int(faint.sum()),
           diff_centroid_arcsec=[float(pD[1]), float(pD[2])], diff_sigma_arcsec=float(pD[3]), diff_amp=float(pD[0]),
           diff_centroid_registered=[float(pD[1] - reg[0]), float(pD[2] - reg[1])], boot_sd=[float(bs[:, 0].std()), float(bs[:, 1].std())],
           mean_image_centroid=[float(pA[1]), float(pA[2])], registration_offset_median=[float(reg[0]), float(reg[1])], n_reg_stars=int(len(offs)),
           reg_star_offsets=offs.tolist(), scan_split=split, note="x positive = west, y positive = north; offsets relative to Gaia DR3 propagated to 2019.5")
json.dump(res, open("../data/j0753_localise.json", "w"), indent=1); print(json.dumps({k: v for k, v in res.items() if k != "reg_star_offsets"}, indent=1))
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(13, 4.5)); ext = [half * pix, -half * pix, -half * pix, half * pix]
for a, (im, lab) in zip(ax, ((stack(bright), f"bright phases (n={bright.sum()})"), (stack(faint), f"faint phases (n={faint.sum()})"), (D, "bright minus faint"))):
    v = np.nanpercentile(im, [5, 99.7]); a.imshow(im, origin="lower", extent=ext, cmap="gray_r", vmin=v[0], vmax=v[1])
    a.plot(0, 0, "+", color="tab:red", ms=14, mew=1.5); a.set_title(lab, fontsize=9); a.set_xlim(20, -20); a.set_ylim(-20, 20)
    a.set_xlabel('arcsec (east left)'); a.set_ylabel('arcsec (north up)')
ax[2].plot(-pD[1], pD[2], "x", color="tab:blue", ms=10)
fig.suptitle("J0753-0042 NEOWISE W1: red + = Gaia DR3 position at 2019.5; blue x = difference-image centroid", fontsize=10)
plt.tight_layout(); plt.savefig("../figures/j0753_localise.png", dpi=110)
# --- scan-direction systematics: target and Gaia field stars (G < 19.5) in the MEAN images per scan direction
np.savez_compressed("j0753_stack_arrays.npz", imgs=imgs, mjds=mjds, crotas=crotas, lev=lev)
q2 = (f"SELECT ra, dec, pmra, pmdec, phot_g_mean_mag FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT(ra,dec), CIRCLE({RA16},{DE16},{50/3600})) "
      f"AND phot_g_mean_mag < 19.5")
out2 = subprocess.run(["curl", "-sL", "--max-time", "120", "https://gea.esac.esa.int/tap-server/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT=csv&QUERY=" + urllib.parse.quote(q2)], capture_output=True, text=True).stdout
def cen_at(im, dx, dy, box=10):
    ix, iy = int(round(half + dx / pix)), int(round(half + dy / pix))
    sub = im[iy - box:iy + box + 1, ix - box:ix + box + 1]
    if sub.shape != (2 * box + 1, 2 * box + 1) or np.isnan(sub).any(): return None
    Y, Xg = np.mgrid[-box:box + 1, -box:box + 1] * pix
    r = least_squares(lambda p: (p[0] * np.exp(-((Xg - p[1]) ** 2 + (Y - p[2]) ** 2) / (2 * p[3] ** 2)) + p[4] - sub).ravel(), [np.nanmax(sub), 0, 0, 2.6, 0],
                      bounds=([0, -4, -4, 1.0, -np.inf], [np.inf, 4, 4, 5.0, np.inf]))
    return r.x
rows = []
for lab, m in (("cos>0", asc), ("cos<0", ~asc)):
    Am = np.nanmean(imgs[m], axis=0)
    t = cen_at(Am, 0, 0)
    rows.append((lab, "J0753 (mean image)", 0.0, 0.0, None if t is None else (round(float(t[1]), 2), round(float(t[2]), 2))))
    for s in csv.DictReader(io.StringIO(out2)):
        ra = float(s["ra"]) + float(s["pmra"] or 0) * (EP - 2016) / 3.6e6 / np.cos(np.radians(DE16)); de = float(s["dec"]) + float(s["pmdec"] or 0) * (EP - 2016) / 3.6e6
        dx = -(ra - RA0) * np.cos(np.radians(DE0)) * 3600; dy = (de - DE0) * 3600
        if np.hypot(dx, dy) < 3 or abs(dx) > 36 or abs(dy) > 36: continue
        c = cen_at(Am, dx, dy)
        if c is not None and c[0] > 0: rows.append((lab, f"Gaia G={float(s['phot_g_mean_mag']):.1f}", round(dx, 1), round(dy, 1), (round(float(c[1]), 2), round(float(c[2]), 2))))
print("\nscan-direction centroids in mean images (offset of the fitted centroid from the Gaia position, arcsec, x west / y north):")
for r in rows: print("  ", r)
