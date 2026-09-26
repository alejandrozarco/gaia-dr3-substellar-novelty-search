# TESS SPOC 120-s (PDCSAP) and K2 light-curve periodograms for stars with MAST short-cadence data.
# QUALITY==0, per-sector median normalisation, 5-sigma MAD clip, 1.5-d running-median high-pass (TESS/K2 systematics), LS 0.5-300 c/d
# (TESS: periods < 2 d only), Baluev FAP, per-sector consistency, CROWDSAP (contamination), injection-recovery limits.
# Usage: python tess_analyze.py [sid ...]
import sys, os, json, glob, math, time
import numpy as np
from astropy.io import fits
from astropy.timeseries import LombScargle
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter

os.chdir("/tmp/fanout/rotation")
os.makedirs("results_tess", exist_ok=True)
META = {r["source_id"]: r for r in json.load(open("data/targets.json")) + json.load(open("data/controls.json"))}
FMIN, FMAX = 0.5, 300.0


def running_median_detrend(t, f, win=1.5):
    # median in +-win/2 day windows evaluated on a coarse grid, interpolated
    g = np.arange(t.min(), t.max() + 0.1, 0.1)
    med = np.array([np.median(f[np.abs(t - x) < win / 2]) if np.sum(np.abs(t - x) < win / 2) > 20 else np.nan for x in g])
    ok = np.isfinite(med)
    if ok.sum() < 2: return f
    return f / np.interp(t, g[ok], med[ok])


def load_tess(sid, kind="tess"):
    files = sorted(glob.glob(f"{kind}/{sid}_*.fits"))
    segs = []
    for fn in files:
        if kind == "tess" and "-s_lc.fits" not in fn: continue
        with fits.open(fn) as h:
            d = h[1].data; hd0 = h[0].header; hd1 = h[1].header
            t = np.array(d["TIME"], float)
            fl = np.array(d["PDCSAP_FLUX"], float); fe = np.array(d["PDCSAP_FLUX_ERR"], float); q = np.array(d["QUALITY"] if "QUALITY" in d.columns.names else d["SAP_QUALITY"], int)
            ok = np.isfinite(t) & np.isfinite(fl) & np.isfinite(fe) & (q == 0) & (fe > 0)
            if ok.sum() < 200: continue
            t, fl, fe = t[ok], fl[ok], fe[ok]
            med = np.median(fl)
            if not np.isfinite(med) or med <= 0: continue
            f = fl / med; e = fe / med
            mad = 1.4826 * np.median(np.abs(f - 1)); k = np.abs(f - 1) < 5 * mad
            t, f, e = t[k], f[k], e[k]
            f = running_median_detrend(t, f)
            sector = hd0.get("SECTOR", hd0.get("CAMPAIGN", -1))
            segs.append(dict(fn=os.path.basename(fn), sector=int(sector) if sector is not None else -1, t=t, f=f, e=e,
                             crowdsap=hd1.get("CROWDSAP"), flfrcsap=hd1.get("FLFRCSAP"), tessmag=hd0.get("TESSMAG", hd0.get("KEPMAG")),
                             ticid=hd0.get("TICID", hd0.get("KEPLERID")), rms=float(np.std(f)), n=int(len(t)),
                             cadence_s=float(np.median(np.diff(t)) * 86400)))
    return segs


def analyse(sid, kind="tess"):
    segs = load_tess(sid, kind)
    rec = META.get(sid, {})
    res = dict(source_id=sid, name=rec.get("name", ""), G=float(rec["phot_g_mean_mag"]) if rec else None, kind=kind,
               segments=[{k: v for k, v in s.items() if k not in ("t", "f", "e")} for s in segs])
    if not segs:
        res["status"] = "NO_DATA"; return res
    fmax = FMAX if kind == "tess" else min(FMAX, 0.5 * 86400 / segs[0]["cadence_s"] * 0.98)
    fmin = FMIN if kind == "tess" else 0.3
    out = {}
    PG = {}
    groups = [(f"S{s['sector']}", [s]) for s in segs] + ([("all", segs)] if len(segs) > 1 else [])
    for lab, G in groups:
        t = np.concatenate([s["t"] for s in G]); f = np.concatenate([s["f"] for s in G]); e = np.concatenate([s["e"] for s in G])
        T = t.max() - t.min(); df = 1 / (5 * T)
        if lab == "all" and (fmax - fmin) / df > 8e6:
            df = (fmax - fmin) / 8e6
        freq = np.arange(fmin, fmax, df)
        ls = LombScargle(t, f, e)
        p = ls.power(freq, method="fast", assume_regular_frequency=True, method_kwds=dict(trig_sum_kwds=dict(oversampling=3)))
        i = np.argmax(p)
        fr = np.linspace(freq[i] - 2 * df, freq[i] + 2 * df, 81); pp = ls.power(fr, method="slow"); j = np.argmax(pp)
        f0, p0 = float(fr[j]), float(pp[j])
        fap = float(ls.false_alarm_probability(p0, minimum_frequency=fmin, maximum_frequency=fmax, method="baluev"))
        X = np.vstack([np.ones_like(t), np.sin(2 * np.pi * f0 * t), np.cos(2 * np.pi * f0 * t)]).T
        w = 1 / e; b, *_ = np.linalg.lstsq(X * w[:, None], f * w, rcond=None)
        A = float(math.hypot(b[1], b[2]))
        # amplitude noise level: median amplitude over the grid ~ sqrt(pi/N)*sigma
        sig = float(np.std(f)); a_noise = math.sqrt(math.pi / len(t)) * sig
        top = []
        pk = np.argsort(p)[::-1]
        for k in pk:
            if all(abs(freq[k] - x) > 10 * df for x in top): top.append(float(freq[k]))
            if len(top) == 5: break
        thr = float(ls.false_alarm_level(1e-3, minimum_frequency=fmin, maximum_frequency=fmax, method="baluev"))
        out[lab] = dict(n=len(t), span_d=float(T), best_f=f0, best_P_h=24 / f0, power=p0, fap_baluev=fap, amp=A, sigma_pt=sig,
                        amp_noise_mean=a_noise, top5_f=top, thr_power_1e3=thr)
        if lab in ("all",) or len(segs) == 1:
            # injection-recovery (amplitude limits) on this group
            rng = np.random.default_rng(5)
            inj = {}
            for rn, (fa, fb) in {"5-60min": (24.0, 288.0), "1-24h": (1.0, 24.0)}.items():
                rows = []
                for Ai in (0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.12, 0.2):
                    ok_n = 0
                    for kk in range(10):
                        fi = math.exp(rng.uniform(math.log(max(fa, fmin)), math.log(min(fb, fmax)))); ph = rng.uniform(0, 2 * np.pi)
                        y = f + Ai * np.sin(2 * np.pi * fi * t + ph)
                        frr = np.linspace(fi - 2 / T, fi + 2 / T, 41)
                        ok_n += LombScargle(t, y, e).power(frr, method="slow").max() > thr
                    rows.append((Ai, ok_n / 10))
                inj[rn] = rows
                inj[rn + "_A90"] = next((a for a, x in rows if x >= 0.9), None)
            out[lab]["injection"] = inj
        # keep a max-binned periodogram for the plot
        nb = 20000; edges = np.logspace(np.log10(freq[0]), np.log10(freq[-1]), nb + 1); idx = np.searchsorted(freq, edges)
        fx = []; px = []
        for a, bb in zip(idx[:-1], idx[1:]):
            if bb > a:
                jj = a + np.argmax(p[a:bb]); fx.append(freq[jj]); px.append(p[jj])
        PG[lab] = (np.array(fx), np.array(px), thr, t, f, f0)
    res["pgram"] = out; res["status"] = "OK"
    # plot
    labs = list(PG.keys())
    fig, ax = plt.subplots(len(labs), 2, figsize=(13, 2.6 * len(labs)), squeeze=False)
    for r_, lab in enumerate(labs):
        fx, px, thr, t, f, f0 = PG[lab]
        a = ax[r_, 0]; a.plot(fx, px, "k", lw=0.5); a.axhline(thr, color="b", ls="--", lw=0.8); a.set_xscale("log")
        a.set_title(f"{sid} {lab} n={len(t)} best {f0:.4f} c/d ({24/f0:.4f} h) FAP={out[lab]['fap_baluev']:.2g} A={100*out[lab]['amp']:.2f}%", fontsize=8)
        a = ax[r_, 1]; ph = (t * f0) % 1; bins = np.linspace(0, 1, 21); ib = np.digitize(ph, bins) - 1
        mu = [np.mean(f[ib == i]) for i in range(20)]; se = [np.std(f[ib == i]) / np.sqrt(max(1, np.sum(ib == i))) for i in range(20)]
        a.errorbar(0.5 * (bins[1:] + bins[:-1]), mu, se, fmt="o", ms=3); a.set_title("fold at best peak (20 bins)", fontsize=8)
    fig.tight_layout(); fig.savefig(f"plots/{sid}_{kind}.png", dpi=80); plt.close(fig)
    return res


if __name__ == "__main__":
    args = sys.argv[1:]
    kind = "tess"
    if args and args[0] in ("tess", "k2"):
        kind = args[0]; args = args[1:]
    sids = args or sorted(set(os.path.basename(x).split("_")[0] for x in glob.glob(f"{kind}/*.fits")))
    for sid in sids:
        t0 = time.time()
        try:
            r = analyse(sid, kind)
        except Exception as ex:
            import traceback; traceback.print_exc(); r = dict(source_id=sid, status="ERROR " + repr(ex))
        json.dump(r, open(f"results_tess/{sid}_{kind}.json", "w"), indent=1, default=float)
        if r.get("status") == "OK":
            s = " | ".join(f"{k}: n={v['n']} f={v['best_f']:.4f} P={v['best_P_h']:.3f}h FAP={v['fap_baluev']:.2g} A={100*v['amp']:.2f}% sig={100*v['sigma_pt']:.1f}%"
                           + (f" A90(5-60m)={v['injection']['5-60min_A90']} A90(1-24h)={v['injection']['1-24h_A90']}" if 'injection' in v else "")
                           for k, v in r["pgram"].items())
            cs = [x.get("crowdsap") for x in r["segments"]]
            print(f"{sid} {kind} G={r['G']} crowdsap={cs} :: {s} ({time.time()-t0:.0f}s)", flush=True)
        else:
            print(sid, kind, r.get("status"), flush=True)
