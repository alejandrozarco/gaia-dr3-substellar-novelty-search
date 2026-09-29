"""Magnitude ranges for the VSX drafts (2026-09-29). Out-of-eclipse levels from ATLAS-REFCAT2 (o ~ (r+i)/2, c ~ (g+r)/2, as for
2MASS J03531244-5502363), corrected to phase 0 with the fitted harmonics; eclipse minima from the fitted depths (eclipse_fit.json).
WDJ1438: outburst peaks from the ATLAS nightly medians (difference flux added to the quiescent level) and outburst episodes
(nights > 5 robust sigma above quiescence with median point S/N > 5, frames with errors > 3x the median dropped, grouped with 15-day gaps). Output: magnitudes.json."""
import numpy as np, json
F = json.load(open("eclipse_fit.json")); V = json.load(open("vsx_fields.json")); out = {}
def mag(fl): return -2.5 * np.log10(fl / 3631e6)
for name in F:
    r = F[name]; rc = V[name]["refcat2"]; g, rr, ii = float(rc["gmag"]), float(rc["rmag"]), float(rc["imag"])
    res = {}
    for b, m0 in (("o", (rr + ii) / 2), ("c", (g + rr) / 2)):
        Fm = 3631e6 * 10 ** (-0.4 * m0); h = r["harm_" + b]; lvl0 = Fm + h[0] + h[2]          # cos(0)=1 terms at phase 0
        dep = r["depth_" + b]; ed = r["e_depth_" + b]; left = lvl0 - dep
        res[b] = dict(mean_mag=m0, mean_uJy=Fm, phase0_uJy=lvl0, depth_uJy=dep, frac=dep / lvl0,
                      min_mag=(mag(left) if left > 2 * ed else None), min_mag_limit=(mag(2 * ed) if left <= 2 * ed else None))
        print(name, b, f"mean {m0:.2f} ({Fm:.0f} uJy), at phase 0 {lvl0:.0f} uJy; depth {dep:.0f}+-{ed:.0f} = {100*dep/lvl0:.0f}%; "
              + (f"minimum {mag(left):.2f}" if left > 2 * ed else f"minimum fainter than {mag(2*ed):.2f} (residual {left:.0f} uJy)"))
    out[name] = res
# WDJ1438 outbursts
L = [l for l in open("atlas_raw/6217118886429978112.txt").read().splitlines() if l.strip()]; hdr = L[0].lstrip("#").split(); R = [dict(zip(hdr, l.split())) for l in L[1:]]
for b in ("o", "c"):
    x = [q for q in R if q["F"] == b and float(q["err"]) == 0 and float(q["chi/N"]) < 10 and float(q["duJy"]) > 0]
    me = np.median([float(q["duJy"]) for q in x]); x = [q for q in x if float(q["duJy"]) < 3 * me]   # drop bad-sky frames (a 5000-uJy-error night once faked a 14.6-mag peak)
    mjd = np.array([float(q["MJD"]) for q in x]); f = np.array([float(q["uJy"]) for q in x]); n = np.floor(mjd); un = np.unique(n)
    nm = np.array([np.median(f[n == k]) for k in un]); qm = np.median(nm); sig = 1.4826 * np.median(np.abs(nm - qm))
    nsnr = np.array([np.median(f[n == k] / np.array([float(q["duJy"]) for q in x])[n == k]) for k in un])
    ob = un[(nm > qm + 5 * max(sig, 10)) & (nsnr > 5)]                                      # outburst night: bright AND each point well detected
    ep = [] if len(ob) == 0 else np.split(ob, np.where(np.diff(ob) > 15)[0] + 1)
    Fq = out["WDJ1438-3051"][b]["mean_uJy"]; peak = nm.max(); pk_mag = mag(Fq + peak - qm)
    out["WDJ1438-3051"][b].update(outburst_episodes=len(ep), outburst_nights=int(len(ob)), peak_nightly_uJy=float(peak), peak_mag=float(pk_mag),
                                    episode_starts_mjd=[int(e[0]) for e in ep])
    print(f"WDJ1438 {b}: {len(ob)} outburst nights in {len(ep)} episodes (MJD {int(un.min())}-{int(un.max())}); brightest nightly median +{peak:.0f} uJy -> {pk_mag:.2f}")
json.dump(out, open("magnitudes.json", "w"), indent=1, default=float)
