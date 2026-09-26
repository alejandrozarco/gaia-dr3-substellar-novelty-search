"""Differential aperture photometry of Gaia DR3 4307667617377160704 in MITSuME Akeno frames (SMOKA request P06USER0925100419FT).
Header TAN WCS (checked against Gaia: offsets < 1 px); comparison stars = Gaia DR3 14 < G < 16.5 within 9 arcmin, no Gaia source
brighter than G+3 within 10 arcsec; positions recentred per frame (flux-weighted centroid in 7x7), target forced at its WCS position
plus the median comparison offset; aperture radius r (px, 1.63"/px), background median in an annulus 8-14 px; ensemble = sum of
comparison fluxes; BJD_TDB at mid-exposure."""
import glob, sys, numpy as np, pandas as pd, pyvo, warnings
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
warnings.filterwarnings("ignore")
R = float(sys.argv[1]) if len(sys.argv) > 1 else 2.5
TRA, TDE = 287.097272, 9.226177
tap = pyvo.dal.TAPService("https://gea.esac.esa.int/tap-server/tap")
A = tap.search(f"select ra, dec, phot_g_mean_mag as g from gaiadr3.gaia_source where 1=contains(point(ra,dec),circle({TRA},{TDE},0.16)) and phot_g_mean_mag < 20").to_table().to_pandas()
cs = SkyCoord(A.ra.values * u.deg, A.dec.values * u.deg)
comp = []
for i, r in A[(A.g > 14) & (A.g < 16.5)].iterrows():
    sep = cs[i].separation(cs).arcsec; bright = (sep > 0.1) & (sep < 10) & (A.g.values < r.g + 3)
    if not bright.any(): comp.append((r.ra, r.dec, r.g))
comp = np.array(comp); print("comparison stars", len(comp))
site = EarthLocation(lat=35.78 * u.deg, lon=138.50 * u.deg, height=900 * u.m); tc = SkyCoord(TRA * u.deg, TDE * u.deg)
def aper(d, x, y):
    xi, yi = int(round(x)), int(round(y)); c = d[yi - 15:yi + 16, xi - 15:xi + 16]
    gy, gx = np.mgrid[yi - 15:yi + 16, xi - 15:xi + 16]; rr = np.hypot(gx - x, gy - y); ann = (rr > 8) & (rr < 14); d = c
    bg = np.median(d[ann]); ap = rr < R
    return float(np.sum(d[ap] - bg)), float(np.sqrt(np.sum(np.clip(d[ap], 1, None)) * 1.2 + ap.sum() * (1.4826 * np.median(np.abs(d[ann] - bg)) * 1.2) ** 2) / 1.2)
rows = []
for fn in sorted(glob.glob("raw/*/*.fits.fz")):
    h = fits.open(fn)[1]; hd = h.header; d = h.data.astype(float); w = WCS(hd)
    cx, cy = w.all_world2pix(comp[:, 0], comp[:, 1], 0); ok = (cx > 25) & (cx < 1045) & (cy > 25) & (cy < 995)
    offs = []; fl = []
    for x0, y0 in zip(cx[ok], cy[ok]):
        xi, yi = int(round(x0)), int(round(y0)); s = d[yi - 3:yi + 4, xi - 3:xi + 4] - np.median(d[yi - 10:yi + 11, xi - 10:xi + 11])
        s = np.clip(s, 0, None)
        if s.sum() <= 0 or d[yi - 1:yi + 2, xi - 1:xi + 2].max() > 55000: offs.append((np.nan, np.nan)); fl.append(np.nan); continue
        gy, gx = np.mgrid[-3:4, -3:4]; ox = (s * gx).sum() / s.sum() + xi - x0; oy = (s * gy).sum() / s.sum() + yi - y0
        offs.append((ox, oy)); fl.append(aper(d, x0 + ox, y0 + oy)[0])
    if len(offs) < 5:
        rows.append(dict(frame=fn.split('/')[-1][:12], band=hd['FILTER'].strip(), n_comp=len(offs), note='few comparisons in frame')); continue
    offs = np.array(offs); dx, dy = np.nanmedian(offs[:, 0]), np.nanmedian(offs[:, 1])
    tx, ty = w.all_world2pix([[TRA, TDE]], 0)[0]; ft, et = aper(d, tx + dx, ty + dy)
    fl = np.array(fl); ens = np.nansum(fl[np.isfinite(fl) & (fl > 0)])
    t = Time(hd["JD"] + hd["EXPTIME"] / 2 / 86400, format="jd", scale="utc", location=site)
    bjd = (t.tdb + t.light_travel_time(tc, kind="barycentric")).jd
    rows.append(dict(frame=fn.split("/")[-1][:12], band=hd["FILTER"].strip(), bjd=bjd, airmass=hd.get("AIRMASS"), exptime=hd["EXPTIME"], dx=dx, dy=dy,
                     n_comp=int(np.isfinite(fl).sum()), f_target=ft, e_target=et, f_ens=ens, rel=ft / ens, e_rel=et / ens, bg=hd.get("BG-LEVEL")))
df = pd.DataFrame(rows); df.to_csv(f"phot_r{R}.csv", index=False)
df = df[df.get("n_comp", 0) >= 5] if "note" not in df else df[df.note.isna()]
for b, g in df.groupby("band"):
    rel = g.rel / np.median(g.rel); print(b, len(g), "median target S/N", round(np.median(g.f_target / g.e_target), 1), "rms %", round(100 * np.std(rel), 1), "median err %", round(100 * np.median(g.e_rel / g.rel), 1), "median |offset| px", round(np.median(np.hypot(g.dx, g.dy)), 2))
