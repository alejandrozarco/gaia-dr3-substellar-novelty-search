# Permutation null (flux+error shuffled within each band on the real timestamps; max LS power over 0.05-300 c/d, full grid
# and outside the systematics mask) + injection-recovery amplitude limits, for the detrended combined ZTF series.
# Usage: python permnull_inject.py [K] sid [sid ...]
import sys, os, json, time, math
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import rotlib as RL
from astropy.timeseries import LombScargle
from scipy import stats

os.chdir("/tmp/fanout/rotation")
os.makedirs("perm", exist_ok=True)
META = {r["source_id"]: r for r in json.load(open("data/targets.json")) + json.load(open("data/controls.json"))}
SID_DAY = 1.0027379


def sys_mask(freq, tol=0.003, kmax=6):
    """True where the frequency is in a ZTF systematics family (k x solar/sidereal day, their +-lunar and +-1/yr sidebands), or < 0.1 c/d."""
    m = freq < 0.1
    for k in range(0, kmax + 1):
        for base in (k * 1.0, k * SID_DAY):
            for off in (0.0, 1 / 29.53, -1 / 29.53, 1 / 365.25, -1 / 365.25):
                c = base + off
                if c <= 0: continue
                m |= np.abs(freq - c) < tol
    return m


def load(sid):
    rec = META[sid]
    rows, by = RL.read_oids(f"ztf/{sid}.csv")
    ot = RL.oid_table(by, rec)
    tset = set(o["oid"] for o in ot if o["sep"] < 1.5)
    D = RL.load_lc([r for r in rows if r["oid"] in tset], float(rec["ra"]), float(rec["dec"]))
    t, f, e, bb, bs = RL.combine(D, min_n=20)
    return rec, D, t, f, e, bb


def fastpow(t, y, e, freq):
    return LombScargle(t, y, e).power(freq, method="fast", assume_regular_frequency=True,
                                      method_kwds=dict(trig_sum_kwds=dict(oversampling=3)))


def run(sid, K=40, seed=11):
    rng = np.random.default_rng(seed)
    rec, D, t, f, e, bb = load(sid)
    freq, df = RL.freq_grid(t)
    msk = sys_mask(freq)
    p = fastpow(t, f, e, freq)
    obs_all = float(p.max()); f_all = float(freq[np.argmax(p)])
    pm = np.where(msk, 0, p); obs_m = float(pm.max()); f_m = float(freq[np.argmax(pm)])
    ls = LombScargle(t, f, e)
    thr_bal = float(ls.false_alarm_level(1e-3, minimum_frequency=RL.FMIN, maximum_frequency=RL.FMAX, method="baluev"))
    fap_bal_all = float(ls.false_alarm_probability(obs_all, minimum_frequency=RL.FMIN, maximum_frequency=RL.FMAX, method="baluev"))
    fap_bal_m = float(ls.false_alarm_probability(obs_m, minimum_frequency=RL.FMIN, maximum_frequency=RL.FMAX, method="baluev"))
    mx_all, mx_m = [], []
    t0 = time.time()
    for k in range(K):
        fs, es = f.copy(), e.copy()
        for b in np.unique(bb):
            i = np.where(bb == b)[0]; j = rng.permutation(i)
            fs[i] = f[j]; es[i] = e[j]
        q = fastpow(t, fs, es, freq)
        mx_all.append(float(q.max())); mx_m.append(float(np.where(msk, 0, q).max()))
    mx_all = np.array(mx_all); mx_m = np.array(mx_m)
    # Gumbel fit to the permutation maxima -> extrapolated FAP
    loc, scale = stats.gumbel_r.fit(mx_m)
    fap_gumbel_m = float(stats.gumbel_r.sf(obs_m, loc, scale))
    loc2, scale2 = stats.gumbel_r.fit(mx_all)
    fap_gumbel_all = float(stats.gumbel_r.sf(obs_all, loc2, scale2))
    thr_perm_1e3 = float(stats.gumbel_r.isf(1e-3, loc, scale))
    res = dict(source_id=sid, n=len(t), K=K, obs_max_all=obs_all, f_obs_all=f_all, obs_max_masked=obs_m, f_obs_masked=f_m,
               fap_baluev_all=fap_bal_all, fap_baluev_masked=fap_bal_m,
               fap_perm_emp_all=float((1 + np.sum(mx_all >= obs_all)) / (K + 1)), fap_perm_emp_masked=float((1 + np.sum(mx_m >= obs_m)) / (K + 1)),
               fap_perm_gumbel_all=fap_gumbel_all, fap_perm_gumbel_masked=fap_gumbel_m,
               perm_max_masked_pcts=[float(np.percentile(mx_m, q)) for q in (50, 90, 99)], perm_max_masked_max=float(mx_m.max()),
               thr_baluev_1e3=thr_bal, thr_perm_gumbel_1e3=thr_perm_1e3, masked_fraction=float(msk.mean()), perm_time_s=time.time() - t0)
    # injection-recovery (combined series): recovered if the local LS peak within +-2/T of f_inj exceeds the detection threshold
    thr = max(thr_bal, thr_perm_1e3)
    T = t.max() - t.min()
    ranges = {"5-60min": (24.0, 288.0), "1-24h": (1.0, 24.0), "1-5d": (0.2, 1.0)}
    amps = [0.003, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.05, 0.08]
    inj = {}
    for rn, (fa, fb) in ranges.items():
        rows = []
        for A in amps:
            rec_n = 0; ntr = 12
            for k in range(ntr):
                while True:
                    f0 = math.exp(rng.uniform(math.log(fa), math.log(fb)))
                    if not sys_mask(np.array([f0]), tol=0.006)[0]: break
                ph = rng.uniform(0, 2 * math.pi)
                y = f + A * np.sin(2 * math.pi * f0 * t + ph)
                fr = np.linspace(f0 - 2 / T, f0 + 2 / T, 41)
                pp = LombScargle(t, y, e).power(fr, method="slow")
                rec_n += pp.max() > thr
            rows.append((A, rec_n / ntr))
        inj[rn] = rows
        a90 = next((A for A, fr_ in rows if fr_ >= 0.9), None); a50 = next((A for A, fr_ in rows if fr_ >= 0.5), None)
        inj[rn + "_A50"] = a50; inj[rn + "_A90"] = a90
    res["injection"] = inj; res["injection_threshold_power"] = thr
    return res


if __name__ == "__main__":
    args = sys.argv[1:]
    K = 40
    if args and args[0].isdigit() and len(args[0]) < 5:
        K = int(args[0]); args = args[1:]
    for sid in args:
        t0 = time.time()
        try:
            r = run(sid, K=K)
        except Exception as ex:
            import traceback; traceback.print_exc(); print(sid, "ERROR", ex); continue
        json.dump(r, open(f"perm/{sid}.json", "w"), indent=1)
        inj = r["injection"]
        print(f"{sid} n={r['n']} obs_all={r['obs_max_all']:.4f}@{r['f_obs_all']:.4f} obs_masked={r['obs_max_masked']:.4f}@{r['f_obs_masked']:.4f} "
              f"FAP bal(masked)={r['fap_baluev_masked']:.2g} perm_emp={r['fap_perm_emp_masked']:.3f} perm_gumbel={r['fap_perm_gumbel_masked']:.2g} "
              f"thr_bal={r['thr_baluev_1e3']:.4f} thr_perm={r['thr_perm_gumbel_1e3']:.4f} | A90: 5-60min {inj['5-60min_A90']} 1-24h {inj['1-24h_A90']} 1-5d {inj['1-5d_A90']} "
              f"| {time.time()-t0:.0f}s", flush=True)
