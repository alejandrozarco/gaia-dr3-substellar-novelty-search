"""Ca II triplet EW structure function across the gas-disc timeline sample (timeline_clean.csv): all same-star pairs, stars with
mean EW >= 5 A and >= 3 spectra. delta = |EW_i - EW_j| / mean(EW_i, EW_j); noise_delta = sqrt(s_i^2 + s_j^2) / mean with
s = sqrt(err^2 + (0.1 EW + 1)^2) (the campaign's systematic floor). Excluded: SDSS J0738+1835 (photospheric Ca II absorption
confounds the EW), the Gaia J0611-6931 2021-08-22 X-shooter spectrum (S/N 18, continuum rms 0.15), and the WD J2133+2428 2025
spectrum is replaced by its spike-filtered EW (0.76 A; cr_check.py). Bins in delta-t; per bin: pairs, stars, median delta,
median noise_delta, fraction of pairs with |dEW| > 3 sigma. Output: structure_function.csv, structure_function.png"""
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
t = pd.read_csv("timeline_clean.csv", dtype={"gaia": str})
t = t[t.name != "SDSS J0738+1835"]; t = t[~((t.name == "Gaia J0611-6931") & (t.date_utc == "2021-08-22"))]
t.loc[(t.name == "WD J2133+2428") & (t.date_utc == "2025-05-24"), "ew_A"] = 0.76
t = t.dropna(subset=["mjd", "ew_A"])
t["s"] = np.sqrt(t.ew_err_A ** 2 + (0.1 * t.ew_A.abs() + 1) ** 2)
st = t.groupby("name").agg(n=("ew_A", "size"), m=("ew_A", "mean")); keep = st[(st.n >= 3) & (st.m >= 5)].index
rows = []
for n, s in t[t.name.isin(keep)].groupby("name"):
    s = s.sort_values("mjd").reset_index(drop=True)
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            a, b = s.iloc[i], s.iloc[j]; m = (a.ew_A + b.ew_A) / 2
            if m <= 0: continue
            rows.append(dict(name=n, dt_yr=abs(b.mjd - a.mjd) / 365.25, delta=abs(a.ew_A - b.ew_A) / m, noise=np.hypot(a.s, b.s) / m,
                             sig=abs(a.ew_A - b.ew_A) / np.hypot(a.s, b.s)))
p = pd.DataFrame(rows)
bins = [0, 0.01, 0.1, 1, 3, 10, 30]; lab = ["<4 d", "4 d-5 wk", "5 wk-1 yr", "1-3 yr", "3-10 yr", "10-30 yr"]
p["bin"] = pd.cut(p.dt_yr, bins, labels=lab, include_lowest=True)
out = p.groupby("bin", observed=False).agg(pairs=("delta", "size"), stars=("name", "nunique"), median_delta=("delta", "median"),
                                           median_noise=("noise", "median"), frac_gt3sig=("sig", lambda x: np.mean(x > 3)))
print("stars:", len(keep), sorted(keep)); print(out.round(3).to_string())
# per-star contribution in the long bins
print(p[p.dt_yr > 3].groupby("name").agg(pairs=("delta", "size"), med=("delta", "median"), f3=("sig", lambda x: np.mean(x > 3))).round(2).sort_values("med").to_string())
out.to_csv("structure_function.csv"); p.to_csv("structure_function_pairs.csv", index=False)
fig, ax = plt.subplots(figsize=(6, 4.2))
ax.scatter(p.dt_yr * 365.25, p.delta, s=4, alpha=.25, color="grey")
c = np.sqrt(np.array(bins[:-1]) * np.array(bins[1:])); c[0] = 0.003
ax.plot(np.array([0.002, 0.03, 0.3, 1.7, 5.5, 17]) * 365.25, out.median_delta, "ro-", label="median |dEW|/EW")
ax.plot(np.array([0.002, 0.03, 0.3, 1.7, 5.5, 17]) * 365.25, out.median_noise, "b--", label="median noise")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("time between spectra (days)"); ax.set_ylabel("|dEW| / mean EW"); ax.legend(fontsize=8)
ax.set_title(f"Ca II triplet emission: {len(keep)} stars, {len(p)} pairs", fontsize=9); plt.tight_layout(); plt.savefig("structure_function.png", dpi=90)
# equal weight per star: median over stars of the per-star median delta in each bin
eq = p.groupby(["bin", "name"], observed=True).delta.median().groupby("bin", observed=False).agg(["size", "median"]).rename(columns={"size": "stars", "median": "star_median_delta"})
print(eq.round(3).to_string()); eq.to_csv("structure_function_equal_weight.csv")
