import sys, csv; sys.path.insert(0, "/tmp/kk76_fix")
from fitlib import *
from common import load, background, tangent, untangent
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
F = pickle.load(open("fits/fitCE.pkl", "rb")); POS = F["POS"]; FB = pickle.load(open("fits/fitB.pkl", "rb"))
R06 = ["j9fw91hpq", "j9fw91hqq", "j9fw91hrq", "j9fw91hsq"]; R10 = ["ib2k52cvq", "ib2k52cwq", "ib2k52cxq", "ib2k52cyq"]
PRED10 = dict(zip(["ib2k52cvq", "ib2k52cwq", "ib2k52cxq", "ib2k52cyq", "ib2k52czq", "ib2k52d0q", "ib2k52d2q", "ib2k52d3q"], FB["pB10"]))
# the July (withdrawn) package positions, from its ADES draft
JULY = {}
for l in open("/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27/docs/reports/precovery_campaign_2026_07_07/kk76_refit/ades_draft_88268_2001kk76.psv"):
    if l.startswith("88268"):
        f = [x.strip() for x in l.split("|")]; root = [w for w in f[-1].split() if w.startswith("J9FW")][0].strip(";,").lower()
        JULY[root] = (float(f[9]), float(f[10]))
fig, axs = plt.subplots(2, 4, figsize=(15, 8))
for ax, r in zip(list(axs[0]) + list(axs[1]), R06 + R10):
    fr = load(r); im = fr["sci"] - background(fr["sci"], 41)[0]; p = POS[r]
    ra0, de0 = fr["wcs"].all_pix2world([[im.shape[1] / 2, im.shape[0] / 2]], 0)[0]
    def topix(ra, de):   # true sky -> pixel through the Gaia-corrected mapping
        xi, eta = tangent(ra, de, ra0, de0); wr, wd = untangent(xi - p["shift_xi"], eta - p["shift_eta"], ra0, de0)
        return fr["wcs"].all_world2pix([[float(wr), float(wd)]], 0)[0]
    ps = p["pixscale"]; h = int(round(1.6 / ps)); cx, cy = int(round(p["x"])), int(round(p["y"]))
    st = im[cy - h:cy + h + 1, cx - h:cx + h + 1]; v = np.nanpercentile(st, [3, 99.7])
    ax.imshow(st, origin="lower", cmap="gray_r", vmin=v[0], vmax=v[1], extent=(cx - h - .5, cx + h + .5, cy - h - .5, cy + h + .5))
    ax.plot(p["x"], p["y"], "o", mfc="none", mec="tab:green", ms=18, mew=1.8, label="KK76, Gaia-anchored (this fix)")
    if r in JULY:
        jx, jy = topix(*JULY[r]); ax.plot(jx, jy, "x", color="tab:red", ms=13, mew=2.2, label="July package position (withdrawn)")
        d = np.hypot(*offset_arcsec(*JULY[r], p["ra"], p["dec"]))
        ax.set_title(f"2006 ACS/HRC {r.upper()}\nJuly position is {d:.2f}\" off", fontsize=9)
    else:
        bx, by = topix(*PRED10[r]); ax.plot(bx, by, "+", color="tab:blue", ms=16, mew=2, label="blind prediction from ground+2006 (fit B)")
        d = np.hypot(*offset_arcsec(*PRED10[r], p["ra"], p["dec"]))
        ax.set_title(f"2010 WFC3/UVIS {fr['h0']['FILTER']} {r.upper()}\nblind prediction {d:.2f}\" away", fontsize=9)
    ax.set_xticks([]); ax.set_yticks([])
    ax.plot([cx - h + 3, cx - h + 3 + 0.5 / ps], [cy - h + 3] * 2, "-", color="k", lw=2); ax.text(cx - h + 3, cy - h + 5, '0.5"', fontsize=8)
axs[0, 0].legend(fontsize=7, loc="upper right"); axs[1, 0].legend(fontsize=7, loc="upper right")
fig.suptitle("(88268) 2001 KK76 in public HST frames: corrected (Gaia-anchored) positions. Stamps 3.2\" across, pixel grid of each frame.", fontsize=11)
fig.tight_layout(); fig.savefig("kk76_fix_overview.png", dpi=85); print("ok")
