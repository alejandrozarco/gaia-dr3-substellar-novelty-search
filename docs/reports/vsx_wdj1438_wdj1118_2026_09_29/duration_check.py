"""Model-light eclipse duration (2026-09-29): with the fitted period and epoch, bin each band in 0.01 phase; the out-of-eclipse
reference is the fitted offset + harmonics (no eclipse term); the duration is the contiguous run of bins around phase 0 whose
weighted mean lies more than 3 sigma below that reference, requiring both bands to agree within one bin. Also the half-depth width."""
import numpy as np, json
exec(open("eclipse_fit.py").read().split("CEN = ")[0])
F = json.load(open("period_refine.json")); out = {}   # refined period and epoch
for name, s in STARS.items():
    r = F[name]; D, _ = load(s); P, T0 = r["P"], r["T0_BJD_TDB"]; res = {}
    for b in ("o", "c"):
        d = D[b]; ph = ((d["t"] - T0) / P + 0.5) % 1 - 0.5; w = 1 / d["e"] ** 2
        A = design(ph, np.zeros_like(ph))[:, :5]; oot = np.abs(ph) > 0.2
        coef = np.linalg.lstsq(A[oot] * np.sqrt(w[oot])[:, None], d["f"][oot] * np.sqrt(w[oot]), rcond=None)[0]; resid = d["f"] - A @ coef
        ed = np.arange(-0.25, 0.2501, 0.01); cen = (ed[:-1] + ed[1:]) / 2; mb = np.full(len(cen), np.nan); eb = np.full(len(cen), np.nan)
        for i in range(len(cen)):
            m = (ph >= ed[i]) & (ph < ed[i + 1])
            if m.sum() > 3: mb[i] = np.sum(resid[m] * w[m]) / np.sum(w[m]); eb[i] = 1 / np.sqrt(np.sum(w[m]))
        low = mb < -3 * eb; i0 = int(np.argmin(np.abs(cen))); lo = i0; hi = i0
        while lo - 1 >= 0 and low[lo - 1]: lo -= 1
        while hi + 1 < len(cen) and low[hi + 1]: hi += 1
        depth = -np.nanmin(np.convolve(np.nan_to_num(mb), np.ones(3) / 3, "same")[max(i0 - 3, 0): i0 + 4])
        half = mb < -depth / 2; hl = i0; hh = i0
        while hl - 1 >= 0 and half[hl - 1]: hl -= 1
        while hh + 1 < len(cen) and half[hh + 1]: hh += 1
        res[b] = dict(first_bin=float(ed[lo]), last_bin=float(ed[hi + 1]), duration_phase=float(ed[hi + 1] - ed[lo]), duration_min=float((ed[hi + 1] - ed[lo]) * P * 1440),
                      half_depth_width_phase=float(ed[hh + 1] - ed[hl]), depth_uJy=float(depth))
        print(f"{name} {b}: >3 sigma below reference from {ed[lo]:+.2f} to {ed[hi+1]:+.2f} -> {100*(ed[hi+1]-ed[lo]):.0f}% of P ({(ed[hi+1]-ed[lo])*P*1440:.1f} min); "
              f"half-depth width {100*(ed[hh+1]-ed[hl]):.0f}%; binned depth {depth:.0f} uJy")
    out[name] = res
json.dump(out, open("duration_check.json", "w"), indent=1)
