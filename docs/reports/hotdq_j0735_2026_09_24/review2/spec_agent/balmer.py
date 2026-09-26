# Task 1: Balmer-line strengths of the target vs SDSS-V DA controls, identical measurement.
# EW = integral(1 - F/Fc) over +-halfw around lam0*(1+v/c); Fc = straight line through the medians of two sideband windows.
# C II lines (NIST, rel. int >= 50) at +93 km/s are masked (+-4.5 A) and linearly interpolated in ALL spectra (same mask).
# Core depth = 1 - mean normalised flux within +-3 A of line centre.
import sys, json, numpy as np
sys.path.insert(0, "/tmp/hotdq/review2/spec_agent")
from common import *
import pandas as pd
L = json.load(open("/tmp/hotdq/review2/data/nist_vacuum_lines.json"))
cii = sorted(set(round(x[0], 1) for x in L["C II"] if 3800 < x[0] < 7000 and x[1] >= 50))
VT = 93.0
cii_obs = [l * (1 + VT / C) for l in cii]
LINES = {  # name: (lam_vac, halfw, sidebands relative to centre)
    "Halpha":   (6564.61, 60, [(-110, -85), (85, 110)]),
    "Hbeta":    (4862.68, 60, [(-105, -80), (80, 105)]),
    "Hgamma":   (4341.69, 50, [(-100, -85), (90, 110)]),
    "Hdelta":   (4102.89, 40, [(-75, -58), (58, 75)]),
    "Hepsilon": (3971.20, 25, [(-38, -28), (28, 40)]),
}
def measure(v, vel):
    out = {}
    for nm, (l0, hw, sb) in LINES.items():
        try:
            E, eE, cd, n2, cont = ew(v["w"], v["f"], v["iv"], l0, hw, sb, mask_centres=cii_obs, mask_hw=4.5, vel=vel)
        except Exception as ex:
            E, eE, cd = np.nan, np.nan, np.nan
        out[nm] = (E, eE, cd)
    return out
sw = pd.concat([pd.read_csv("/tmp/hotdq/review2/spec_agent/da_pool.csv", skiprows=1), pd.read_csv("/tmp/hotdq/review2/spec_agent/da_massive.csv", skiprows=1)]).drop_duplicates("sdss_id").set_index("sdss_id")
ctrl = [92423903, 62915553, 79919872, 87778573, 57464341, 75044158, 92605802, 96103732, 57579772, 105176520, 98328567, 112550886, 72429783, 76154013, 115901492, 67567164]
rows = []
t = load_visits(TARGET)[0]
m = measure(t, VT)
rows.append(dict(sid=95077848, kind="TARGET", teff=72178, logg=8.75, snr=t["snr"], obs=t["obs"], **{k: m[k][0] for k in m}, **{k + "_e": m[k][1] for k in m}, **{k + "_core": m[k][2] for k in m}))
# also target measured at 0 km/s and with shift NOT undone (sanity)
for sid in ctrl:
    vs = load_visits(f"{SPEC}/mwmVisit-0.8.1-{sid}.fits")
    v = max(vs, key=lambda x: x["snr"])
    m = measure(v, 0.0)
    r = sw.loc[sid]
    bprp = r.bp_mag - r.rp_mag; MG = r.g_mag + 5 * np.log10(r.plx / 100)
    rows.append(dict(sid=sid, kind="DA", teff=r.teff, logg=r.logg, snr=v["snr"], obs=v["obs"], bprp=bprp, MG=MG, **{k: m[k][0] for k in m}, **{k + "_e": m[k][1] for k in m}, **{k + "_core": m[k][2] for k in m}))
df = pd.DataFrame(rows)
pd.set_option("display.width", 250)
cols = ["sid", "kind", "teff", "logg", "snr", "obs", "bprp", "MG"] + [f"{k}" for k in LINES] + [f"{k}_core" for k in LINES]
print(df[cols].round(2).to_string())
da = df[df.kind == "DA"]
tg = df[df.kind == "TARGET"].iloc[0]
print("\nTarget vs DA controls (EW in A):")
for k in LINES:
    x = da[k].values
    print(f"{k:9s} target {tg[k]:6.2f} +- {tg[k+'_e']:.2f} (core {tg[k+'_core']:.3f}) | DA median {np.nanmedian(x):6.2f}, range {np.nanmin(x):6.2f}..{np.nanmax(x):6.2f}, "
          f"core median {np.nanmedian(da[k+'_core']):.3f} range {np.nanmin(da[k+'_core']):.3f}..{np.nanmax(da[k+'_core']):.3f} | ratio target/median {tg[k]/np.nanmedian(x):.2f} | n below target {np.sum(x < tg[k])}/{len(x)}")
df.to_csv("/tmp/hotdq/review2/spec_agent/balmer_ew.csv", index=False)
