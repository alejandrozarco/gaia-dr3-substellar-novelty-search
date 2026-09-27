"""WDJ2127+5937 infrared excess: Montreal pure-H synthetic photometry (Table_DA) at GF21 Teff/log g (13777 K / 6.97 -> grid floor 7.0; also 12-16 kK),
scaled to Pan-STARRS DR1 g, r, i (AB; PS1 grizy columns of Table_DA). Observed CatWISE2020 W1 15.84 +- 0.02, W2 15.90 +- 0.04 (Vega); d = 1/plx = 241 pc."""
import sys, numpy as np
L = open(sys.argv[1] if len(sys.argv) > 1 else "Table_DA.txt").readlines(); hdr = L[1].replace("log g", "logg").split()
D = np.array([[float(x) for x in l.split()] for l in L[2:] if len(l.split()) == len(hdr)])
iW1, iW2 = hdr.index("W1"), hdr.index("W2"); ps = [i for i, h in enumerate(hdr) if h == "g"][1]   # second g = Pan-STARRS g
idx = dict(g=ps, r=ps + 1, i=ps + 2, W1=iW1, W2=iW2)
def model(te, lg=7.0):
    q = D[np.isclose(D[:, 1], lg)]; q = q[np.argsort(q[:, 0])]; return {k: np.interp(te, q[:, 0], q[:, c]) for k, c in idx.items()}
obs = dict(g=16.7925, r=17.0284, i=17.3092); W = dict(W1=(15.84, 309.54, 0.02), W2=(15.90, 171.787, 0.04)); DM = 5 * np.log10(241.2 / 10)
for te in (12000, 13777, 16000):
    m = model(te); off = np.mean([obs[b] - m[b] for b in obs]); line = [f"Teff {te}: scale rms {np.std([obs[b] - m[b] for b in obs]):.3f}"]
    for b, (mv, zp, e) in W.items():
        pred = m[b] + off; fo = zp * 10 ** (-0.4 * mv); fp = zp * 10 ** (-0.4 * pred); ex = fo - fp; mc = -2.5 * np.log10(ex / zp)
        line.append(f"{b}: obs {mv:.2f}, WD {pred:.2f}, ratio {fo/fp:.2f}, companion {mc:.2f} (M = {mc - DM:.2f})")
    print("; ".join(line))
