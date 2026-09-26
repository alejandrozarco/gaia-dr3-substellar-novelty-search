# EC 10246-2707 = TIC 193092806 = Gaia DR3 5468670738602933504, TESS sector 100 SPOC 2-min + 20-s.
# Question (PHT Talk, paulearth): what are the "shallower and ~30 min longer dips" (e.g. day ~1.1599)
# in the binned PHT subject? Test: fold unbinned data; then re-bin at 10/20/30 min and measure each eclipse.
import glob, numpy as np
from astropy.io import fits
P = 0.1185079936
def load(pattern):
    f = glob.glob(pattern)[0]
    d = fits.getdata(f, 1); h = fits.getheader(f, 1)
    t = d["TIME"]; fl = d["PDCSAP_FLUX"]; q = d["QUALITY"]
    ok = np.isfinite(t) & np.isfinite(fl) & (q == 0)
    return t[ok], fl[ok] / np.nanmedian(fl[ok]), d["TIME"][np.isfinite(d["TIME"])][0]
t, f, tfirst = load("mastDownload/TESS/*s0100*-s/*s_lc.fits")
tf, ff, _ = load("mastDownload/TESS/*s0100*a_fast/*lc.fits")
print(f"sector 100 2-min: {len(t)} good cadences, BTJD {t[0]:.4f}-{t[-1]:.4f} (first cadence in file {tfirst:.4f})")
# primary eclipse epoch: fold, find minimum of a fine phase-binned curve
ph = ((t - t[0]) / P) % 1
nb = 400; idx = (ph * nb).astype(int)
prof = np.array([np.median(f[idx == k]) if np.any(idx == k) else np.nan for k in range(nb)])
kmin = np.nanargmin(prof); T0 = t[0] + (kmin + 0.5) / nb * P
# refine T0 with the 20-s data: centroid of points within the deepest 30% of the eclipse
phf = (((tf - T0) / P + 0.5) % 1) - 0.5
sel = np.abs(phf) < 0.06
c = np.polyfit(phf[sel], ff[sel], 2); T0 += (-c[1] / (2 * c[0])) * P
ph = (((t - T0) / P + 0.5) % 1) - 0.5; phf = (((tf - T0) / P + 0.5) % 1) - 0.5
# fine profile from 20-s data
def profile(phase, flux, nb):
    e = np.linspace(-0.5, 0.5, nb + 1); m = 0.5 * (e[1:] + e[:-1])
    v = np.array([np.median(flux[(phase >= e[k]) & (phase < e[k + 1])]) if np.any((phase >= e[k]) & (phase < e[k + 1])) else np.nan for k in range(nb)])
    return m, v
m20, v20 = profile(phf, ff, 600)
base_p = np.nanmedian(v20[(np.abs(m20) > 0.09) & (np.abs(m20) < 0.13)])   # just outside primary
depth_p = base_p - np.nanmin(v20[np.abs(m20) < 0.05])
inecl = np.abs(m20) < 0.2
halfp = m20[inecl][v20[inecl] < base_p - 0.5 * depth_p]
# contacts: where the profile drops below baseline by > 3% of depth
cont = m20[inecl][v20[inecl] < base_p - 0.03 * depth_p]
print(f"T0 (primary, BTJD) = {T0:.5f}")
print(f"primary: depth {depth_p:.3f} (rel. to local baseline {base_p:.3f}); FWHM {(halfp.max()-halfp.min())*P*1440:.1f} min; first-to-last contact ~{(cont.max()-cont.min())*P*1440:.1f} min")
m2 = np.abs(np.abs(m20) - 0.5) < 0.2
ms = np.where(m20 < 0, m20 + 1, m20)[m2]; vs = v20[m2]; o = np.argsort(ms); ms, vs = ms[o], vs[o]
# secondary: compare the phase-0.5 region with a smooth reflection fit excluding |ph-0.5|<0.06
w = np.abs(ms - 0.5) > 0.06
cc = np.polyfit(ms[w] - 0.5, vs[w], 4); resid = vs - np.polyval(cc, ms - 0.5)
depth_s = -np.nanmin(resid[np.abs(ms - 0.5) < 0.03])
hs = ms[(np.abs(ms - 0.5) < 0.06) & (resid < -0.5 * depth_s)]
print(f"secondary (phase 0.5, after removing the reflection hump): depth {depth_s:.4f}; FWHM {(hs.max()-hs.min())*P*1440:.1f} min")
print(f"reflection effect peak-to-peak (outside eclipses): {np.nanmax(v20[np.abs(m20)>0.1]) - np.nanmin(v20[np.abs(m20)>0.1]):.3f}")
# binned 'PHT-like' light curves
for B in (10, 20, 30):
    bw = B / 1440.
    e = np.arange(tfirst, t[-1] + bw, bw); k = np.digitize(t, e) - 1
    tb = np.array([t[k == j].mean() for j in np.unique(k)]); fb = np.array([f[k == j].mean() for j in np.unique(k)])
    n0 = int(np.ceil((t[0] - T0) / P)); n1 = int(np.floor((t[-1] - T0) / P))
    rows = []
    for n in range(n0, n1 + 1):
        Tn = T0 + n * P
        near = np.abs(tb - Tn) < 0.045
        if near.sum() < 5: continue
        loc = np.abs(tb - Tn) < 0.025
        if not loc.any(): continue
        base = np.median(fb[near & ~loc]) if (near & ~loc).any() else np.nan
        d = base - fb[loc].min()
        wid = (np.sum(fb[loc] < base - 0.5 * d)) * B
        off = ((Tn - tfirst) / bw) % 1           # eclipse centre position inside its bin (0.5 = bin centre)
        rows.append((n, Tn, Tn - tfirst, d, wid, off))
    r = np.array(rows)
    cen = np.abs(r[:, 5] - 0.5) < 0.2; edge = ~cen
    print(f"\n{B}-min bins: {len(r)} primary eclipses; apparent depth {r[:,3].min():.3f}-{r[:,3].max():.3f} (true {depth_p:.3f});"
          f" eclipse near bin centre: depth {np.median(r[cen,3]):.3f}, half-depth width {np.median(r[cen,4]):.0f} min;"
          f" eclipse near bin edge: depth {np.median(r[edge,3]):.3f}, width {np.median(r[edge,4]):.0f} min")
    j = np.argmin(np.abs(r[:, 2] - 1.1599))
    print(f"   eclipse nearest day 1.1599 after the first cadence: day {r[j,2]:.4f}, apparent depth {r[j,3]:.3f}, width {r[j,4]:.0f} min, centre at bin fraction {r[j,5]:.2f}")
    # alternation / beat pattern
    print("   first 12 eclipses (day, depth, width):", "; ".join(f"{x[2]:.3f} {x[3]:.3f} {x[4]:.0f}" for x in r[:12]))
# anything odd around day 1.16 in the unbinned data? residuals from the fold
mm, vv = profile(ph, f, 200)
tmpl = np.interp(ph, mm, vv, period=1)
res = f - tmpl
win = np.abs((t - tfirst) - 1.1599) < 0.1
print(f"\nunbinned residual rms, whole sector {np.std(res):.4f}; within +-0.1 d of day 1.1599: {np.std(res[win]):.4f}, min {res[win].min():.4f}, n {win.sum()}")
print("phase of day 1.1599 after first cadence:", round((((tfirst + 1.1599 - T0) / P + 0.5) % 1) - 0.5, 3))
