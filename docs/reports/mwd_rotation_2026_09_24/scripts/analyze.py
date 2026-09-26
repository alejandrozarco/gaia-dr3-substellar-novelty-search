# Per-star ZTF periodogram analysis. Usage: python analyze.py [sid ...]  (default: every star with ztf/<sid>.csv)
# Writes results/<sid>.json, results/<sid>_pgram.npz (max-binned periodograms for plotting) and plots/<sid>_ls.png.
import sys, os, json, glob, math, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import rotlib as RL
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.chdir("/tmp/fanout/rotation")
os.makedirs("results", exist_ok=True)
META = {r["source_id"]: r for r in json.load(open("data/targets.json")) + json.load(open("data/controls.json"))}


def maxbin(freq, p, nb=30000):
    """log-spaced max-binning for plotting"""
    edges = np.logspace(np.log10(freq[0]), np.log10(freq[-1]), nb + 1)
    idx = np.searchsorted(freq, edges)
    fx, px = [], []
    for a, b in zip(idx[:-1], idx[1:]):
        if b > a:
            j = a + np.argmax(p[a:b]); fx.append(freq[j]); px.append(p[j])
    return np.array(fx), np.array(px)


def analyse(sid, match_radius=1.5):
    rec = META[sid]
    fn = f"ztf/{sid}.csv"
    rows, by = RL.read_oids(fn)
    ot = RL.oid_table(by, rec)
    tgt = [o for o in ot if o["sep"] < match_radius]
    nbr = [o for o in ot if o["sep"] >= match_radius]
    res = dict(source_id=sid, name=rec.get("name", ""), group=rec.get("group", ""), G=float(rec["phot_g_mean_mag"]),
               oids_target=tgt, oids_other=nbr,
               gaia_neighbours_5as=[dict(source_id=n["source_id"], sep=float(n["sep"]), G=float(n["phot_g_mean_mag"]) if n["phot_g_mean_mag"] else None)
                                    for n in rec["neighbours_10as"] if float(n["sep"]) < 5])
    if not tgt:
        res["status"] = "NO_TARGET_OID"; return res
    tset = set(o["oid"] for o in tgt)
    R = [r for r in rows if r["oid"] in tset]
    D = RL.load_lc(R, float(rec["ra"]), float(rec["dec"]))
    res["bands"] = {b: dict(n=D[b]["n"], n_raw=D[b]["n_raw"], rms=D[b]["rms"], med_err=D[b]["med_err"], med_mag=D[b]["med_mag"],
                            span_d=float(D[b]["t"].max() - D[b]["t"].min()), n_keys=int(len(np.unique(D[b]["key"]))))
                    for b in D}
    series = {}
    for b in ("zg", "zr", "zi"):
        if b in D and D[b]["n"] >= 60:
            series[b] = (D[b]["t"], D[b]["f"], D[b]["e"])
    ntot = sum(D[b]["n"] for b in D if D[b]["n"] >= 20)
    if len([b for b in ("zg", "zr") if b in series]) >= 1 or ntot >= 60:
        t, f, e, bb, bs = RL.combine(D, bands=("zg", "zr", "zi"), min_n=20)
        series["comb"] = (t, f, e)
        res["comb_bands"] = bs
    if "comb" not in series:
        res["status"] = "TOO_FEW_POINTS"; return res
    res["status"] = "OK"
    tc = series["comb"][0]
    freq, df = RL.freq_grid(tc)
    res["grid"] = dict(fmin=RL.FMIN, fmax=RL.FMAX, df=df, nfreq=len(freq), span_d=float(tc.max() - tc.min()))
    out = {}
    PG = {}
    for lab, (t, f, e) in series.items():
        ls, p = RL.periodogram(t, f, e, freq)
        idx = RL.top_peaks(freq, p, n=10)
        peaks = []
        for i in idx:
            f0, p0 = RL.refine_peak(ls, freq[i], df)
            fap = float(ls.false_alarm_probability(p0, minimum_frequency=RL.FMIN, maximum_frequency=RL.FMAX, method="baluev"))
            fit = RL.sine_fit(t, f, e, f0)
            peaks.append(dict(freq=float(f0), P_h=float(24 / f0), power=float(p0), fap_baluev=fap, amp=float(fit["A"]), eamp=float(fit["eA"])))
        # 1-5 d window (0.2-1 c/d)
        m = (freq >= 0.2) & (freq <= 1.0)
        j = np.where(m)[0][np.argmax(p[m])]
        f1, p1 = RL.refine_peak(ls, freq[j], df)
        fap1 = float(ls.false_alarm_probability(p1, minimum_frequency=0.2, maximum_frequency=1.0, method="baluev"))
        fit1 = RL.sine_fit(t, f, e, f1)
        thr = float(ls.false_alarm_level(1e-3, minimum_frequency=RL.FMIN, maximum_frequency=RL.FMAX, method="baluev"))
        out[lab] = dict(n=len(t), top=peaks, best_1to5d=dict(freq=float(f1), P_d=float(1 / f1), power=float(p1), fap_baluev_window=fap1,
                                                              amp=float(fit1["A"]), eamp=float(fit1["eA"])),
                        power_thr_fap1e3=thr)
        fx, px = maxbin(freq, p)
        PG[lab] = (fx, px)
    res["pgram"] = out
    # spectral window of the combined sampling
    W, wpk = RL.window_peaks(tc, freq)
    res["window_peaks"] = wpk
    fx, px = maxbin(freq, W); PG["window"] = (fx, px)
    np.savez_compressed(f"results/{sid}_pgram.npz", **{k + "_f": v[0] for k, v in PG.items()}, **{k + "_p": v[1] for k, v in PG.items()})
    # alias notes for the best combined peak
    best = out["comb"]["top"][0]
    res["best_alias_notes"] = RL.alias_notes(best["freq"], wpk)
    # plot
    plot(sid, res, D, series, PG)
    return res


def plot(sid, res, D, series, PG):
    fig, ax = plt.subplots(3, 2, figsize=(14, 11))
    a = ax[0, 0]
    for lab, col in (("comb", "k"), ("zg", "g"), ("zr", "r"), ("zi", "orange")):
        if lab in PG:
            a.plot(PG[lab][0], PG[lab][1], col, lw=0.5, alpha=0.9 if lab == "comb" else 0.6, label=lab)
    a.axhline(res["pgram"]["comb"]["power_thr_fap1e3"], color="b", ls="--", lw=0.8, label="Baluev FAP 1e-3 (comb)")
    a.set_xscale("log"); a.set_xlabel("frequency (c/d)"); a.set_ylabel("LS power"); a.legend(fontsize=7)
    a.set_title(f"{sid} {res['name'][:28]} G={res['G']:.2f}  ZTF DR24 LS 0.05-300 c/d")
    a = ax[0, 1]
    a.plot(PG["window"][0], PG["window"][1], "0.3", lw=0.5); a.set_xscale("log"); a.set_title("spectral window (combined sampling)")
    a.set_xlabel("frequency (c/d)")
    a = ax[1, 0]
    m = (PG["comb"][0] >= 0.15) & (PG["comb"][0] <= 1.2)
    for lab, col in (("comb", "k"), ("zg", "g"), ("zr", "r")):
        if lab in PG:
            mm = (PG[lab][0] >= 0.15) & (PG[lab][0] <= 1.2)
            a.plot(PG[lab][0][mm], PG[lab][1][mm], col, lw=0.6, label=lab)
    a.set_title("zoom 0.15-1.2 c/d (periods 0.8-6.7 d)"); a.set_xlabel("frequency (c/d)"); a.legend(fontsize=7)
    # fold at best combined peak
    best = res["pgram"]["comb"]["top"][0]
    for k, (a, f0, lab) in enumerate(((ax[1, 1], best["freq"], "best global peak"),
                                      (ax[2, 0], res["pgram"]["comb"]["best_1to5d"]["freq"], "best 1-5 d peak"))):
        for b, col in (("zg", "g"), ("zr", "r"), ("zi", "orange")):
            if b not in D: continue
            t, f = D[b]["t"], D[b]["f"]
            ph = (t * f0) % 1
            a.plot(ph, f, ".", color=col, ms=1.2, alpha=0.25)
            bins = np.linspace(0, 1, 21); ib = np.digitize(ph, bins) - 1
            mu = [np.median(f[ib == i]) if np.sum(ib == i) > 3 else np.nan for i in range(20)]
            se = [1.2533 * np.std(f[ib == i]) / np.sqrt(max(1, np.sum(ib == i))) if np.sum(ib == i) > 3 else np.nan for i in range(20)]
            a.errorbar(0.5 * (bins[1:] + bins[:-1]), mu, se, fmt="o", color=col, mec="k", ms=4)
        sd = max(0.02, 3 * np.std(D["zr"]["f"] if "zr" in D else D["zg"]["f"]) / 2)
        a.set_ylim(1 - sd, 1 + sd)
        a.set_title(f"fold {lab}: f={f0:.5f} c/d  P={24/f0:.4f} h ({1/f0:.4f} d)"); a.set_xlabel("phase")
    a = ax[2, 1]
    for b, col in (("zg", "g"), ("zr", "r"), ("zi", "orange")):
        if b in D:
            a.plot(D[b]["t"] - 2458000, D[b]["f"], ".", color=col, ms=1.5, alpha=0.5)
    a.set_xlabel("BJD_TDB - 2458000"); a.set_ylabel("normalised flux"); a.set_title("light curve")
    fig.tight_layout(); fig.savefig(f"plots/{sid}_ls.png", dpi=90); plt.close(fig)


if __name__ == "__main__":
    sids = sys.argv[1:] or [os.path.basename(x)[:-4] for x in sorted(glob.glob("ztf/*.csv")) if "test" not in x]
    for sid in sids:
        if sid not in META: continue
        t0 = time.time()
        try:
            res = analyse(sid)
        except Exception as ex:
            import traceback; traceback.print_exc(); res = dict(source_id=sid, status="ERROR " + repr(ex))
        json.dump(res, open(f"results/{sid}.json", "w"), indent=1, default=float)
        msg = f"{sid} {res.get('status')} {time.time()-t0:.0f}s"
        if res.get("status") == "OK":
            b = res["pgram"]["comb"]["top"][0]; w = res["pgram"]["comb"]["best_1to5d"]
            msg += (f" n={res['pgram']['comb']['n']} best f={b['freq']:.5f} P={b['P_h']:.4f} h pow={b['power']:.4f} FAP={b['fap_baluev']:.2g} "
                    f"A={100*b['amp']:.2f}% | 1-5d: P={w['P_d']:.3f} d FAPw={w['fap_baluev_window']:.2g} | " +
                    " ".join(f"{k}:{v['n']}" for k, v in res["bands"].items()))
        print(msg, flush=True)
