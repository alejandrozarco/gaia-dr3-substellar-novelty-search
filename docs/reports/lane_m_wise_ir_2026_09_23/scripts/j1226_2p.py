import os
# J1226-2304 (Gaia DR3 3513017956589117056): is the orbital period P or 2P? WISE W1 test for an odd/even (subharmonic)
# signal at 2P = 0.15936371 d that is phase-coherent across 14 years, allowing the P-signal to change per season.
#   Test A: per-season mean + per-season P-harmonic + ONE global subharmonic (constant flux amplitude).
#   Test B: same, but the subharmonic scales with each season's P amplitude (constant asymmetry fraction).
# Nulls: (i) 1000 simulations of the per-season P-only model with the actual timestamps and scaled errors;
#        (ii) Test A on the field stars (same frames), which checks the sampling/instrument at the 2P frequency.
import json, numpy as np, pandas as pd
P, T0 = 0.07968185682, 2459999.9469779
REF = os.path.expanduser("~/claude_projects/gaia_local_notes/2026-09-23/j1226_referee")
rng = np.random.default_rng(7)

def seasons(bjd):
    o = np.argsort(bjd); s = np.empty(len(bjd), int); s[o] = np.cumsum(np.r_[0, np.diff(bjd[o]) > 60]); return s

def design(psi, sid, extra=None):
    cols = []
    for k in np.unique(sid):
        m = (sid == k).astype(float)
        cols += [m, m * np.cos(4 * np.pi * psi), m * np.sin(4 * np.pi * psi)]
    X = np.vstack(cols).T
    return X if extra is None else np.hstack([X, extra])

def chi2(X, y, w):
    bb, *_ = np.linalg.lstsq(X * w[:, None], y * w, rcond=None); r = (y - X @ bb) * w
    return float(r @ r), bb

def tests(t, F, eF, min_n=8):
    sid = seasons(t); keep = np.isin(sid, [k for k in np.unique(sid) if (sid == k).sum() >= min_n])
    t, F, eF, sid = t[keep], F[keep], eF[keep], sid[keep]
    psi = ((t - T0) / (2 * P)) % 1.0
    X0 = design(psi, sid); c0, b0 = chi2(X0, F, 1 / eF)
    # per-season error scaling from the P-only fit
    model0 = X0 @ b0; e2 = eF.copy()
    for k in np.unique(sid):
        m = sid == k; r = ((F[m] - model0[m]) / eF[m]); s2 = float(r @ r) / max(m.sum() - 3, 1)
        e2[m] = eF[m] * np.sqrt(max(s2, 1.0))
    w = 1 / e2
    c0, b0 = chi2(X0, F, w); model0 = X0 @ b0
    # per-season P amplitude
    A2 = np.zeros(len(t))
    for i, k in enumerate(np.unique(sid)):
        A2[sid == k] = np.hypot(b0[3 * i + 1], b0[3 * i + 2])
    XA = design(psi, sid, np.vstack([np.cos(2 * np.pi * psi), np.sin(2 * np.pi * psi)]).T); cA, bA = chi2(XA, F, w)
    XB = design(psi, sid, np.vstack([A2 * np.cos(2 * np.pi * psi), A2 * np.sin(2 * np.pi * psi)]).T); cB, bB = chi2(XB, F, w)
    return dict(n=len(t), n_seasons=int(len(np.unique(sid))), dchi2_A=c0 - cA, dchi2_B=c0 - cB,
                sub_amp_A_mJy=float(np.hypot(bA[-2], bA[-1])), sub_phase_A=float((np.arctan2(bA[-1], bA[-2]) / (2 * np.pi)) % 1),
                sub_frac_B=float(np.hypot(bB[-2], bB[-1])), sub_phase_B=float((np.arctan2(bB[-1], bB[-2]) / (2 * np.pi)) % 1)), (t, psi, sid, model0, e2, X0, XA, XB)

w = pd.read_csv(f"{REF}/target_w1_clean_model.csv")
m1 = w.w1mpro - w.zp; F = 309.54e3 * 10 ** (-0.4 * m1.values); eF = F * w.w1sigmpro.values / 1.0857
res, (t, psi, sid, model0, e2, X0, XA, XB) = tests(w.bjd.values, F, eF)
print("target:", json.dumps(res))
# (i) simulations of the P-only model
dA, dB = [], []
for _ in range(1000):
    y = model0 + rng.normal(0, e2)
    wt = 1 / e2
    c0, _ = chi2(X0, y, wt); cA, _ = chi2(XA, y, wt)
    # Test B needs the simulated series' own A2; reuse the true A2 scaling (fixed design) -- conservative enough for a null
    cB, _ = chi2(XB, y, wt)
    dA.append(c0 - cA); dB.append(c0 - cB)
dA, dB = np.array(dA), np.array(dB)
print(f"simulations (P-only, n=1000): dchi2_A 95/99/99.9 pct {np.percentile(dA,95):.1f}/{np.percentile(dA,99):.1f}/{np.percentile(dA,99.9):.1f}; "
      f"p(target A) = {np.mean(dA >= res['dchi2_A']):.4f} | dchi2_B 95/99 pct {np.percentile(dB,95):.1f}/{np.percentile(dB,99):.1f}; p(target B) = {np.mean(dB >= res['dchi2_B']):.4f}")
# (ii) field stars, Test A (and B for completeness), same cleaning as the referee's field table
fm = pd.read_csv(f"{REF}/field_matched.csv")
fm = fm[(fm.nb == 1) & (fm.na == 0) & (fm.qual_frame > 0) & np.isfinite(fm.w1mpro) & np.isfinite(fm.w1sigmpro)]
fres = []
for k, s in fm.groupby("aw_idx"):
    if len(s) < 150: continue
    Fs = 309.54e3 * 10 ** (-0.4 * s.w1mpro.values); eFs = Fs * s.w1sigmpro.values / 1.0857
    try:
        r, _ = tests(s.bjd.values, Fs, eFs)
        fres.append(r)
    except Exception:
        pass
fA = np.array([r["dchi2_A"] for r in fres]); fB = np.array([r["dchi2_B"] for r in fres])
print(f"field stars (n={len(fres)}): dchi2_A median {np.median(fA):.1f}, 95 pct {np.percentile(fA,95):.1f}, max {fA.max():.1f}; "
      f"fraction >= target {np.mean(fA >= res['dchi2_A']):.3f} | dchi2_B median {np.median(fB):.1f} max {fB.max():.1f} fraction >= target {np.mean(fB >= res['dchi2_B']):.3f}")
json.dump(dict(target=res, sim_A_pcts=[float(np.percentile(dA, q)) for q in (50, 95, 99, 99.9)], sim_B_pcts=[float(np.percentile(dB, q)) for q in (50, 95, 99, 99.9)],
               p_sim_A=float(np.mean(dA >= res["dchi2_A"])), p_sim_B=float(np.mean(dB >= res["dchi2_B"])),
               field_n=len(fres), field_A=[float(x) for x in fA], field_B=[float(x) for x in fB]), open("../data/j1226_2p_results.json", "w"), indent=1)
