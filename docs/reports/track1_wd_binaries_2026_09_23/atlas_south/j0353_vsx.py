# VSX fields for 3eRASS J035311.8-550237 = Gaia DR3 4731701084150029824 from ATLAS forced photometry (o, c; uJy difference fluxes).
# Phases are measured from a reference epoch inside the data (Tref), so the eclipse centre stays near phase 0 for all trial periods.
# Model per band: offset + trapezoid (common centre, total width T, flat fraction) with free depth; offset and depth are linear
# (closed form) for each grid point (centre, T, flat fraction). chi2(P) = grid minimum; period error from delta chi2 = 1 after scaling
# chi2_r to 1; parameter errors from a bootstrap over nights (200 resamples). Out-of-eclipse magnitudes from ATLAS-REFCAT2.
import numpy as np, json
from astropy.coordinates import SkyCoord
import astropy.units as u
exec(open("j0353_eclipse.py").read().split("P0 = 0.0739348;")[0])     # D[band]: t (BJD_TDB), f, e, sv, mjd
Tref = 2460670.38343
def trap(x, T, fr):
    """unit-depth trapezoid profile (0 outside, 1 on the flat bottom) vs phase offset x from centre; total width T, flat width fr*T"""
    a = np.abs(x); tf = fr * T; m = np.zeros_like(a); m[a <= tf / 2] = 1
    r = (a > tf / 2) & (a < T / 2); m[r] = (T / 2 - a[r]) / max(T / 2 - tf / 2, 1e-12); return m
CEN = np.arange(-0.02, 0.02001, 0.0005); TW = np.arange(0.016, 0.0801, 0.002); FR = (0.0, 0.25, 0.5, 0.75, 0.95)
def scan(P, data, full=False):
    best = (np.inf, None)
    ph = {b: ((d["t"] - Tref) / P + 0.5) % 1 - 0.5 for b, d in data.items()}
    for T in TW:
        for fr in FR:
            for c in CEN:
                chi = 0; par = []
                for b, d in data.items():
                    m = trap(ph[b] - c, T, fr); w = 1 / d["e"] ** 2
                    S = np.sum(w); Sm = np.sum(w * m); Smm = np.sum(w * m * m); Sy = np.sum(w * d["f"]); Sym = np.sum(w * d["f"] * m)
                    det = S * Smm - Sm ** 2; off = (Smm * Sy - Sm * Sym) / det; dep = -(S * Sym - Sm * Sy) / det
                    chi += np.sum(w * (d["f"] - off + dep * m) ** 2); par += [off, dep]
                if chi < best[0]: best = (chi, (c, T, fr, *par))
    return best
data = {b: dict(t=D[b]["t"], f=D[b]["f"], e=D[b]["e"]) for b in D}
Ps = 0.1478696 + np.linspace(-1.5e-6, 1.5e-6, 31)
res_scan = [scan(P, data) for P in Ps]; chis = np.array([x[0] for x in res_scan]); j = int(np.argmin(chis))
ndata = sum(len(d["t"]) for d in data.values()); s2 = chis[j] / (ndata - 7)
sl = slice(max(j - 6, 0), j + 7); a, b_, _ = np.polyfit(Ps[sl] - Ps[j], chis[sl], 2); Pbest = Ps[j] - b_ / (2 * a); sigP = np.sqrt(s2 / a)
chi, (c, T, fr, oo, do, oc, dc) = scan(Pbest, data)
T0 = Tref + c * Pbest
print(f"P = {Pbest:.8f} +- {sigP:.8f} d ({Pbest*24:.5f} h); chi2_r {s2:.2f}; delta chi2 curve min at grid index {j}/{len(Ps)-1}")
print(f"T0 (primary minimum) = BJD_TDB {T0:.5f}; total duration {T*Pbest*1440:.1f} min ({T*100:.1f}% of P), flat fraction {fr}; depth o {do:.1f}, c {dc:.1f} uJy")
# bootstrap over nights
rng = np.random.default_rng(7); boot = []
nights = {b: np.floor(d["t"] - 0.3).astype(int) for b, d in data.items()}
for it in range(200):
    bd = {}
    for b, d in data.items():
        un = np.unique(nights[b]); pick = rng.choice(un, len(un)); idx = np.concatenate([np.where(nights[b] == n)[0] for n in pick])
        bd[b] = dict(t=d["t"][idx], f=d["f"][idx], e=d["e"][idx])
    ch, (cb, Tb, frb, _, dob, _, dcb) = scan(Pbest, bd); boot.append((cb, Tb, frb, dob, dcb))
boot = np.array(boot); eb = boot.std(axis=0)
print(f"bootstrap (200 x nights): sigma centre {eb[0]*Pbest*1440:.2f} min, duration {eb[1]*Pbest*1440:.2f} min, depth o {eb[3]:.1f}, c {eb[4]:.1f} uJy; flat fraction values {np.unique(boot[:,2], return_counts=True)}")
from astroquery.vizier import Vizier
t = Vizier(columns=["**"], row_limit=5).query_region(SkyCoord(58.3013 * u.deg, -55.0437 * u.deg), radius=4 * u.arcsec, catalog="J/ApJ/867/105/refcat2")[0]
g, rr, ii = float(t["gmag"][0]), float(t["rmag"][0]), float(t["imag"][0]); print(f"ATLAS-REFCAT2 g {g:.3f} r {rr:.3f} i {ii:.3f}")
cmag = (g + rr) / 2; omag = (rr + ii) / 2      # approximate band centres (c: 420-650 nm, o: 560-820 nm)
res = dict(P=Pbest, sigP=sigP, chi2r=s2, T0_BJD_TDB=T0, eT0_min=eb[0] * Pbest * 1440, duration_min=T * Pbest * 1440, e_duration_min=eb[1] * Pbest * 1440,
           duration_pct=T * 100, flat_fraction=fr, depth_o_uJy=do, e_depth_o=eb[3], depth_c_uJy=dc, e_depth_c=eb[4], refcat2=dict(g=g, r=rr, i=ii),
           o_mag_approx=omag, c_mag_approx=cmag, n_o=len(data["o"]["t"]), n_c=len(data["c"]["t"]),
           t_first=float(min(d["t"].min() for d in data.values())), t_last=float(max(d["t"].max() for d in data.values())))
for b, m0, dep in (("o", omag, do), ("c", cmag, dc)):
    F = 3631e6 * 10 ** (-0.4 * m0); frac = dep / F; res[f"{b}_frac_depth"] = frac; res[f"{b}_min_mag"] = m0 - 2.5 * np.log10(1 - frac)
    print(f"{b}: out of eclipse ~{m0:.2f} ({F:.0f} uJy); depth {dep:.0f} uJy = {frac*100:.0f}% -> minimum ~{res[f'{b}_min_mag']:.2f}")
json.dump(res, open("j0353_vsx_values.json", "w"), indent=1, default=float)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(2, 2, figsize=(11, 6), gridspec_kw=dict(width_ratios=[2, 1]))
for r_, (b, off, dep) in enumerate((("o", oo, do), ("c", oc, dc))):
    d = data[b]; ph = ((d["t"] - T0) / Pbest + 0.5) % 1 - 0.5; w = 1 / d["e"] ** 2
    for k, (xl, nb) in enumerate(((0.5, 50), (0.08, 32))):
        ed = np.linspace(-xl, xl, nb + 1); cen = (ed[:-1] + ed[1:]) / 2
        mb = [np.sum(d["f"][(ph >= ed[i]) & (ph < ed[i + 1])] * w[(ph >= ed[i]) & (ph < ed[i + 1])]) / np.sum(w[(ph >= ed[i]) & (ph < ed[i + 1])]) for i in range(nb)]
        er = [1 / np.sqrt(np.sum(w[(ph >= ed[i]) & (ph < ed[i + 1])])) for i in range(nb)]
        ax = axs[r_, k]; ax.errorbar(cen, mb, er, fmt="o", ms=3, color="k"); x = np.linspace(-xl, xl, 1000); ax.plot(x, off - dep * trap(x, T, fr), color="tab:red", lw=1)
        ax.set_xlim(-xl, xl); ax.set_xlabel("orbital phase"); ax.set_ylabel("ATLAS difference flux (uJy)")
        ax.set_title(f"ATLAS {b} (n={len(d['t'])}), P = {Pbest:.7f} d, phase 0 = BJD_TDB {T0:.5f}", fontsize=8)
plt.tight_layout(); plt.savefig("j0353_vsx_fold.png", dpi=100); print("figure ok")
