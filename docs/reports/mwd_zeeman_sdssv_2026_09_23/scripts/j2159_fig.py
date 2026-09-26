# Figure: SDSS-V DR20 BOSS spectrum of J2159+5102 (Gaia DR3 1980205739970324224) vs a non-magnetic DA of similar temperature
# (SnowWhite DA, Teff 11,148 K, log g 8.35, Gaia DR3 458685159848886528), with linear-Zeeman pi/sigma positions for the fitted field.
import numpy as np, subprocess, os
from astropy.io import fits
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
def get(sid, v="0.8.1"):
    fn = f"/tmp/mwd/spec/mwmStar-{v}-{sid}.fits"
    if not os.path.exists(fn):
        subprocess.run(["curl", "-s", "-m", "180", "-o", fn, f"https://data.sdss.org/sas/dr20/spectro/astra/{v}/spectra/star/{str(sid)[-4:-2]}/{str(sid)[-2:]}/mwmStar-{v}-{sid}.fits"])
    h = fits.open(fn); d = h[1].data[0] if len(h[1].data) else h[2].data[0]
    return np.array(d["wavelength"]), np.array(d["flux"]), np.array(d["ivar"])
lt, ft, it = get(65378167); lc, fc, ic = get(54797138)
def smooth(y, n=3): return np.convolve(y, np.ones(n) / n, mode="same")
B = 5.6; K = lambda l0: 4.67e-13 * l0 ** 2 * B * 1e6
lines = {r"H$\alpha$": 6564.61, r"H$\beta$": 4862.68, r"H$\gamma$": 4341.69}
fig = plt.figure(figsize=(12, 7.5)); gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.1])
ax = fig.add_subplot(gs[0, :]); m = (lt > 3700) & (lt < 9000)
nt = np.median(ft[(lt > 5200) & (lt < 5400)]); nc = np.median(fc[(lc > 5200) & (lc < 5400)])
ax.plot(lc[m], smooth(fc[m]) / nc + 0.6, color="0.55", lw=0.6, label="non-magnetic DA, Teff 11,150 K (Gaia DR3 458685159848886528), offset +0.6")
ax.plot(lt[m], smooth(ft[m]) / nt, color="k", lw=0.6, label="J2159+5102 (Gaia DR3 1980205739970324224), SDSS-V APO, MJD 60625")
ax.set_xlim(3700, 9000); ax.set_ylim(0, 2.6); ax.set_xlabel("vacuum wavelength (Å)"); ax.set_ylabel("normalised flux"); ax.legend(fontsize=8, loc="upper right")
for k, (nm, l0) in enumerate(lines.items()):
    a = fig.add_subplot(gs[1, 2 - k]); w = (lt > l0 - 260) & (lt < l0 + 260); wc = (lc > l0 - 260) & (lc < l0 + 260)
    nt2 = np.median(ft[w][np.abs(lt[w] - l0) > 220]); nc2 = np.median(fc[wc][np.abs(lc[wc] - l0) > 220])
    a.plot(lc[wc], smooth(fc[wc]) / nc2 + 0.5, color="0.55", lw=0.7); a.plot(lt[w], smooth(ft[w]) / nt2, color="k", lw=0.7)
    for off, col in ((-K(l0), "tab:red"), (0, "tab:blue"), (K(l0), "tab:red")):
        a.axvline(l0 + off, color=col, ls=":", lw=1)
    a.set_title(f"{nm}: π (blue) and σ± (red) for B = {B} MG", fontsize=9); a.set_xlim(l0 - 260, l0 + 260); a.set_ylim(0.3, 1.8); a.set_xlabel("Å")
fig.suptitle("J2159+5102: Zeeman-split Balmer lines (linear-splitting field scale ≈ 5.6 MG); listed as a new ZZ Ceti by Vincent et al. 2020", fontsize=10)
plt.tight_layout(); plt.savefig("/tmp/mwd/j2159/j2159_spectrum.png", dpi=110)
print("ok")
