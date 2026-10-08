import sys, os, numpy as np
os.environ["DRY"] = "1"; sys.argv = ["holdout2.py", sys.argv[1]] + sys.argv[2:]
try: exec(open("holdout2.py").read())
except SystemExit: pass
fa, fb = float(os.environ["FA"]), float(os.environ["FB"])
for lab, d in (("ALL", df), ("TESS only", df[df.blk.str.startswith("TESS")]), ("no Gaia", df[df.blk != "Gaia_DR3"])):
    sub = group(d); t = d.t.values; w = 1 / d.e.values ** 2; tc = np.sum(w * t) / np.sum(w)
    fr = np.arange(min(fa, fb) - 3e-4, max(fa, fb) + 3e-4, 2e-6); pw, _ = grid_power(sub, fr, tc)
    ia, ib = np.argmin(abs(fr - fa)), np.argmin(abs(fr - fb)); pk = [fr[i] for i in range(1, len(fr) - 1) if pw[i] >= pw[i-1] and pw[i] >= pw[i+1] and pw[i] > pw.max() - 100]
    print(f"{lab}: best {fr[pw.argmax()]:.7f}; dchi2(best - ours {fa}) {pw.max()-pw[ia]:.1f}; dchi2(best - public {fb}) {pw.max()-pw[ib]:.1f}; local peaks within 100: {[(round(x,6), round(pw.max()-pw[np.argmin(abs(fr-x))],1)) for x in pk]}")
