"""Find the pixel offset between header-WCS positions of Gaia stars and detected stars in a MITSuME frame."""
import sys, glob, numpy as np, pyvo, warnings
from astropy.io import fits
from astropy.wcs import WCS
from scipy.ndimage import maximum_filter, gaussian_filter
warnings.filterwarnings("ignore")
tap = pyvo.dal.TAPService("https://gea.esac.esa.int/tap-server/tap")
G = tap.search("select source_id, ra, dec, phot_g_mean_mag from gaiadr3.gaia_source where 1=contains(point(ra,dec),circle(287.128,9.292,0.26)) and phot_g_mean_mag < 16.5").to_table().to_pandas()
np.save("gaia_ref.npy", G[["ra", "dec", "phot_g_mean_mag"]].values)
def detect(d):
    bg = np.median(d); rms = 1.4826 * np.median(np.abs(d - bg)); s = gaussian_filter(d - bg, 1.0)
    pk = (s == maximum_filter(s, 7)) & (s > 8 * rms / 2)
    y, x = np.nonzero(pk); f = s[y, x]; o = np.argsort(f)[::-1][:300]
    return x[o], y[o]
for fn in sorted(glob.glob("raw/*/*.fits.fz"))[:6]:
    h = fits.open(fn)[1]; d = h.data.astype(float); w = WCS(h.header)
    xs, ys = detect(d); gx, gy = w.all_world2pix(G.ra.values, G.dec.values, 0)
    dx = (xs[:, None] - gx[None, :]).ravel(); dy = (ys[:, None] - gy[None, :]).ravel(); m = (np.abs(dx) < 60) & (np.abs(dy) < 60)
    H, xe, ye = np.histogram2d(dx[m], dy[m], bins=120, range=[[-60, 60], [-60, 60]]); i, j = np.unravel_index(np.argmax(H), H.shape)
    print(fn.split("/")[-1], h.header["FILTER"], "n det", len(xs), "best offset dx", xe[i] + 0.5, "dy", ye[j] + 0.5, "votes", int(H.max()), "median votes", np.median(H))
