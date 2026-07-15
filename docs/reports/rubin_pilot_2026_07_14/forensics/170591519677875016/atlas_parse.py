import numpy as np
rows = []
with open("/tmp/rubin_pilot/forensics/170591519677875016/atlas_fp_raw.txt") as f:
    hdr = f.readline()
    for line in f:
        p = line.split()
        if len(p) < 19: continue
        rows.append((float(p[0]), float(p[3]), float(p[4]), p[5], float(p[16])))  # mjd, uJy, duJy, filt, mag5sig
arr = np.array([(m,f,df,fl=='o',m5) for m,f,df,fl,m5 in rows], dtype=float)
mjd, uJy, duJy, iso, m5 = arr.T
print(f"total epochs: {len(mjd)}, MJD {mjd.min():.1f}..{mjd.max():.1f}")
snr = uJy/duJy
print(f"epochs SNR>=5: {(snr>=5).sum()}, SNR>=3: {(snr>=3).sum()} of {len(snr)}")
# nightly bins (per filter)
for filt, mask in [("o", iso==1), ("c", iso==0)]:
    m, f, df = mjd[mask], uJy[mask], duJy[mask]
    nights = np.unique(np.floor(m))
    det_nights = []
    for n in nights:
        sel = (np.floor(m)==n) & (df>0)
        if sel.sum()==0: continue
        w = 1/df[sel]**2
        fw = (f[sel]*w).sum()/w.sum(); ew = 1/np.sqrt(w.sum())
        if fw/ew >= 5:
            mag = -2.5*np.log10(fw*1e-6/3631)
            det_nights.append((n, fw, ew, fw/ew, mag, sel.sum()))
    print(f"filter {filt}: {len(nights)} nights, {len(det_nights)} nights with stacked SNR>=5")
    for n, fw, ew, s, mag, nexp in det_nights:
        print(f"  MJD {n:.0f}: flux={fw:.0f}+/-{ew:.0f} uJy SNR={s:.1f} mag={mag:.2f} nexp={nexp}")
# also SNR>=4 nights count as sanity
