"""CH G-band index (1 - mean flux 4285-4316 A / median continuum 4235-4262 + 4322-4332 A; as for LP 133-754) over every stored
SDSS/BOSS DR17 spectrum of a Gentile Fusillo et al. (2021) white dwarf with TeffH < 9000 K (2026-09-29). S/N > 3.
Output: ch_sweep_sdss.csv (one row per spectrum), sorted by significance."""
import os, glob, numpy as np, pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); g = np.load(os.path.join(H, "grid.npy"))
W = pd.read_csv(os.path.join(H, "gf21_sdssspec.csv"), dtype={"GaiaEDR3": str}).drop_duplicates("GaiaEDR3").set_index("GaiaEDR3")
cool = set(W.index[W.TeffH < 9000])
band = (g > 4285) & (g < 4316); cm = ((g > 4235) & (g < 4262)) | ((g > 4322) & (g < 4332)); snw = (g > 4500) & (g < 5500)
rows, seen = [], set()
for fn in sorted(glob.glob(os.path.join(H, "chunks", "*.npz"))):
    d = np.load(fn)
    for s_, gg, f, iv in zip(d["sparcl_id"], d["gaia"], d["f"], d["iv"]):
        if s_ in seen or str(gg) not in cool: continue
        seen.add(s_); sn = float(np.nanmedian(f[snw] * np.sqrt(np.clip(iv[snw], 0, None))))
        if not sn > 3: continue
        c = np.nanmedian(f[cm])
        if not c > 0: continue
        e = 1 / np.sqrt(np.where(iv[band] > 0, iv[band], np.nan)) / c; i = 1 - np.nanmean(f[band] / c); ee = np.sqrt(np.nansum(e**2)) / max(np.isfinite(e).sum(), 1)
        rows.append(dict(sparcl_id=str(s_), gaia=str(gg), snr=sn, ch=i, e=ee, z=i / ee if ee > 0 else np.nan))
D = pd.DataFrame(rows)
for col in ("WDJname", "specClass", "TeffH", "MassH", "Gmag"): D[col] = W[col].reindex(D.gaia).values
D = D.sort_values("z", ascending=False); D.to_csv(os.path.join(H, "ch_sweep_sdss.csv"), index=False)
print(len(D), "spectra of", D.gaia.nunique(), "cool white dwarfs; index median %.3f" % D.ch.median())
