"""Equivalent widths at the approximate UHE feature positions marked by Reindl et al. 2021 (A&A 647, A184, Fig. B.1), avoiding
H I / He II / He I cores: 4495, 4785, 4941, 5243, 5280, 5665, 6060, 6198 A (windows +-12 A; continuum = linear fit to side bands
12-40 A away on both sides). Coadd of in-stack visits."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
POS = [4495, 4785, 4941, 5243, 5280, 5665, 6060, 6198]
def ew(w, f, iv, l, hw=12):
    cs = [(l - hw - 30, l - hw - 3), (l + hw + 3, l + hw + 30)]; m = np.zeros_like(w, bool)
    for a, b in cs: m |= (w > a) & (w < b)
    m &= (iv > 0) & np.isfinite(f); k = (np.abs(w - l) < hw) & (iv > 0) & np.isfinite(f)
    if m.sum() < 8 or k.sum() < 8: return np.nan, np.nan
    p = np.polyfit(w[m], f[m], 1, w=np.sqrt(iv[m])); c = np.polyval(p, w); dw = np.gradient(w)[k]
    return np.sum((1 - f[k] / c[k]) * dw), np.sqrt(np.sum((np.sqrt(1 / iv[k]) / c[k] * dw) ** 2))
S = [("100568930", "WDJ0958-1758", "cand"), ("92169356", "EC 01395-6452", "cand"), ("93074954", "GALEX J0412-3754", "cand"), ("111789298", "GALEX J1913-5330", "cand"),
     ("78658917", "PG 1201-049", "cand"), ("93205750", "Gaia DR3 4866851575967878144", "cand"),
     ("59101580", "WDJ0706+6133", "known DA UHE"), ("63039439", "HS 2115+1148", "known DAO UHE"), ("63152641", "WDJ2101+1356", "known DAO UHE"), ("70107585", "J0254+0058", "known DO UHE"), ("69492080", "WD0101-182", "known DOZ UHE"),
     ("74510696", "J0814+0225", "normal"), ("99327334", "J0629-4158", "normal"), ("92431667", "PN Lo 1", "normal"), ("62051762", "PG 1204+543", "normal"), ("58697654", "PG 0834+501", "normal")]
rows = []
for sid, n, kind in S:
    vs = sdssv.visits(sid); use = [v for v in vs if v["in_stack"]] or vs; w, f, iv = sdssv.coadd(use)[:3]; d = dict(name=n, kind=kind)
    for l in POS:
        e, s = ew(w, f, iv, l); d[str(l)] = f"{e:5.2f}±{s:4.2f}"; d["z" + str(l)] = e / max(s, 0.08)
    rows.append(d)
R = pd.DataFrame(rows); pd.set_option("display.width", 260)
print(R[["name", "kind"] + [str(l) for l in POS]].to_string(index=False))
R.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "uhe_lines.csv"), index=False)
