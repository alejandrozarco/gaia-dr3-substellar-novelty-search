"""WDJ2052-0324 infrared excess: Montreal pure-H synthetic photometry (Tables/Table_DA; Holberg & Bergeron 2006) interpolated in Teff and
log g, scaled to SDSS DR16 griz (AB; u excluded). Observed: VHS DR5 J, Ks (Vega; VISTA ~ 2MASS for a blue star), CatWISE2020 W1/W2 (Vega).
Teff/log g cases: Kilic+2026 DESI fit 18357/7.26; Swan DR1 21395/7.47; GF21 photometric 16231/7.12 (grid floor 7.0 used below 7.0)."""
import numpy as np
L = open("Table_DA.txt").readlines(); hdr = L[1].replace("log g", "logg").split()
D = np.array([[float(x) for x in l.split()] for l in L[2:] if len(l.split()) == len(hdr)])
idx = {n: hdr.index(n) for n in ("Teff", "logg", "Ks", "W1", "W2")}; idx["J"] = hdr.index("J"); ug = hdr.index("u")
for k, n in enumerate("griz"): idx[n] = ug + 1 + k
def model(teff, logg):
    out = {}
    for n in ("J", "Ks", "W1", "W2", "g", "r", "i", "z"):
        v = []
        for lg in (7.0, 7.5):
            s = D[np.isclose(D[:, idx["logg"]], lg)]; s = s[np.argsort(s[:, 0])]; v.append(np.interp(teff, s[:, 0], s[:, idx[n]]))
        out[n] = np.interp(max(logg, 7.0), [7.0, 7.5], v)
    return out
obs_ab = dict(g=17.271, r=17.574, i=17.795, z=17.958)
vega = dict(J=(17.5841, 1594.0, 0.04), Ks=(17.0349, 666.7, 0.06), W1=(16.537, 309.54, 0.036), W2=(16.393, 171.787, 0.092))
for teff, lg in ((16231, 7.12), (18357, 7.26), (21395, 7.47)):
    m = model(teff, lg); res = [obs_ab[b] - m[b] for b in obs_ab]; dm = np.mean(res)
    print(f"Teff {teff} logg {lg}: griz scale offset {dm:.3f} (rms {np.std(res):.3f})")
    for b, (mv, zp, err) in vega.items():
        pred = m[b] + dm; fo = zp * 10 ** (-0.4 * mv) * 1e6; fp = zp * 10 ** (-0.4 * pred) * 1e6; ex = fo - fp
        print(f"   {b}: obs {mv:.2f} ({fo:.0f} uJy), WD model {pred:.2f} ({fp:.0f} uJy): ratio {fo/fp:.2f}, excess {ex:.0f} +- {fo*err/1.086:.0f} uJy -> {(-2.5*np.log10(ex/1e6/zp)) if ex > 0 else float('nan'):.2f} mag")
