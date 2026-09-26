import os
import sys; sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts"))
import numpy as np; import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from sdssv import star_spectrum
L = [("2246631460497465472", "68942299", "LSPM J2028+6701"), ("3987356721738829184", "80729520", "GALEX J103612.8+203228"), ("6915353300288749440", "114797603", "GALEX J205808.2-042002 (DESI: DA, Kilic+2026)"), ("4867935694432066304", "93212597", "Gaia DR3 4867935694432066304")]
fig, ax = plt.subplots(4, 2, figsize=(13, 11))
for i, (g, sid, nm) in enumerate(L):
    lam, f, iv, snr = star_spectrum(sid)
    for j, (l0, lo, hi, k) in enumerate([(6564.61, 6300, 6830, 20.13), (4862.68, 4660, 5060, 11.04)]):
        m = (lam > lo) & (lam < hi) & (iv > 0); y = gaussian_filter1d(f[m], 1.5); y /= np.median(y)
        a = ax[i, j]; a.plot(lam[m], y, "k", lw=0.7); a.axvline(l0, color="grey", ls=":")
        for B in (2, 4, 6, 8, 10):
            a.plot([l0 - B * k, l0 + B * k], [1.18 + 0.02 * B] * 2, "|-", color="C%d" % (B // 2), lw=0.6, ms=4)
        a.set_title(f"{nm} S/N {snr:.0f} ({'Ha' if j == 0 else 'Hb'}); bars = linear sigma positions at 2-10 MG", fontsize=8); a.set_ylim(0.3, 1.45)
plt.tight_layout(); plt.savefig("four_leads.png", dpi=80)
