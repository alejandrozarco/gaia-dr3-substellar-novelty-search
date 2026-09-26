# Candidate vetting for a ZTF periodicity: per-band power/amplitude/phase at f0, time-split halves, depth (limitmag) split,
# alias ladder (f0 + k*1.0027 c/d), injection of the fitted signal into prewhitened data (alias discrimination), ZTF neighbour oids
# within 5", and a vetting figure. Usage: python cand_check.py sid f0 [label]
import sys, os, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import rotlib as RL
from astropy.timeseries import LombScargle
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.chdir("/tmp/fanout/rotation")
os.makedirs("cand", exist_ok=True)
META = {r["source_id"]: r for r in json.load(open("data/targets.json")) + json.load(open("data/controls.json"))}
SID = 1.0027379


def local_power(t, f, e, f0, T, n=41):
    fr = np.linspace(f0 - 1.5 / T, f0 + 1.5 / T, n)
    ls = LombScargle(t, f, e); p = ls.power(fr, method="slow"); i = np.argmax(p)
    return float(fr[i]), float(p[i]), ls


def fit(t, f, e, f0):
    r = RL.sine_fit(t, f, e, f0)
    return r["A"], r["eA"], r["phase"]


def check(sid, f0, label=""):
    rec = META[sid]
    rows, by = RL.read_oids(f"ztf/{sid}.csv")
    ot = RL.oid_table(by, rec)
    tset = set(o["oid"] for o in ot if o["sep"] < 1.5)
    D = RL.load_lc([r for r in rows if r["oid"] in tset], float(rec["ra"]), float(rec["dec"]))
    t, f, e, bb, bs = RL.combine(D, min_n=20)
    T = t.max() - t.min()
    out = dict(source_id=sid, f0_in=f0, label=label)
    fc, pc, ls = local_power(t, f, e, f0, T)
    out["comb"] = dict(f=fc, P_h=24 / fc, power=pc, fap_global=float(ls.false_alarm_probability(pc, minimum_frequency=RL.FMIN, maximum_frequency=RL.FMAX, method="baluev")))
    A, eA, ph = fit(t, f, e, fc); out["comb"].update(A=A, eA=eA, phase=ph)
    # per band at the combined frequency; single-trial (local) FAP ~ exp(-power*(N-3)/2) and global Baluev
    out["bands"] = {}
    for b in ("zg", "zr", "zi"):
        if b not in D or D[b]["n"] < 30: continue
        tb, fb, eb = D[b]["t"], D[b]["f"], D[b]["e"]
        lsb = LombScargle(tb, fb, eb); pb = float(lsb.power(np.array([fc]), method="slow")[0])
        Ab, eAb, phb = fit(tb, fb, eb, fc)
        out["bands"][b] = dict(n=len(tb), power_at_f0=pb, single_trial_p=float(lsb.false_alarm_probability(pb, method="single")),
                               A=Ab, eA=eAb, phase=phb, snrA=Ab / eAb if eAb > 0 else None)
    # time split halves (by median time) and depth split (limitmag above/below band median)
    halves = {}
    tm = np.median(t)
    for lab, m in (("first_half", t < tm), ("second_half", t >= tm)):
        lsh = LombScargle(t[m], f[m], e[m]); p = float(lsh.power(np.array([fc]), method="slow")[0])
        Ah, eAh, phh = fit(t[m], f[m], e[m], fc)
        halves[lab] = dict(n=int(m.sum()), power=p, single_trial_p=float(lsh.false_alarm_probability(p, method="single")), A=Ah, eA=eAh, phase=phh)
    L = np.concatenate([D[b]["limitmag"] - np.median(D[b]["limitmag"]) for b in bs]); tt = np.concatenate([D[b]["t"] for b in bs])
    o = np.argsort(tt); L = L[o]
    for lab, m in (("deep_epochs", L >= 0), ("shallow_epochs", L < 0)):
        lsh = LombScargle(t[m], f[m], e[m]); p = float(lsh.power(np.array([fc]), method="slow")[0])
        Ah, eAh, phh = fit(t[m], f[m], e[m], fc)
        halves[lab] = dict(n=int(m.sum()), power=p, single_trial_p=float(lsh.false_alarm_probability(p, method="single")), A=Ah, eA=eAh, phase=phh)
    out["splits"] = halves
    # alias ladder
    lad = []
    for k in range(-3, 4):
        for h in (1,):
            fa = fc + k * SID
            if fa <= 0.05: continue
            fr_, p_, _ = local_power(t, f, e, fa, T)
            lad.append(dict(k=k, f=fr_, power=p_))
    out["alias_ladder"] = lad
    # harmonics / subharmonics
    out["harmonics"] = [dict(mult=m_, f=local_power(t, f, e, fc * m_, T)[0], power=local_power(t, f, e, fc * m_, T)[1]) for m_ in (0.5, 2.0, 3.0) if fc * m_ > 0.05]
    # injection of the fitted sinusoid (random phases) into data prewhitened at fc; is the top peak within +-3.5 c/d still at fc?
    model = RL.sine_fit(t, f, e, fc)["model"]
    resid = f - model + 1
    rng = np.random.default_rng(7); win = []
    fr = np.arange(max(0.06, fc - 3.5), fc + 3.5, 1 / (5 * T))
    for k in range(20):
        y = resid + A * np.sin(2 * np.pi * fc * t + rng.uniform(0, 2 * np.pi))
        p = LombScargle(t, y, e).power(fr, method="fast", assume_regular_frequency=True)
        win.append(float(fr[np.argmax(p)]))
    win = np.array(win)
    out["injection_alias_test"] = dict(n=20, frac_top_at_f0=float(np.mean(np.abs(win - fc) < 2 / T)),
                                       top_freqs=[float(x) for x in np.unique(np.round(win, 3))])
    # residual periodogram after prewhitening (is there anything else?)
    freq, df = RL.freq_grid(t)
    pr = LombScargle(t, resid, e).power(freq, method="fast", assume_regular_frequency=True, method_kwds=dict(trig_sum_kwds=dict(oversampling=3)))
    j = np.argmax(pr); out["prewhitened_best"] = dict(f=float(freq[j]), power=float(pr[j]))
    # ZTF neighbour oids (1.5-5")
    nb = [o_ for o_ in ot if 1.5 <= o_["sep"] < 5.0 and o_["n_good"] >= 30]
    out["neighbour_oids"] = []
    for o_ in nb:
        R = [r for r in rows if r["oid"] == o_["oid"]]
        Dn = RL.load_lc(R, o_["ra"], o_["dec"])
        for b in Dn:
            lsn = LombScargle(Dn[b]["t"], Dn[b]["f"], Dn[b]["e"]); pn = float(lsn.power(np.array([fc]), method="slow")[0])
            An, eAn, _ = fit(Dn[b]["t"], Dn[b]["f"], Dn[b]["e"], fc)
            out["neighbour_oids"].append(dict(oid=o_["oid"], sep=o_["sep"], band=b, mag=o_["mag"], n=Dn[b]["n"], power_at_f0=pn,
                                              single_trial_p=float(lsn.false_alarm_probability(pn, method="single")), A=An, eA=eAn))
    # figure
    fig, ax = plt.subplots(2, 3, figsize=(15, 8))
    for i, (b, col) in enumerate((("zg", "g"), ("zr", "r"), ("zi", "orange"))):
        if b not in D: continue
        a = ax[0, i]; tb, fb = D[b]["t"], D[b]["f"]; ph = (tb * fc) % 1
        a.plot(ph, fb, ".", color=col, ms=1.5, alpha=0.3); a.plot(ph + 1, fb, ".", color=col, ms=1.5, alpha=0.3)
        bins = np.linspace(0, 1, 16); ib = np.digitize(ph, bins) - 1
        mu = np.array([np.mean(fb[ib == k]) if np.sum(ib == k) > 3 else np.nan for k in range(15)])
        se = np.array([np.std(fb[ib == k]) / math.sqrt(max(1, np.sum(ib == k))) if np.sum(ib == k) > 3 else np.nan for k in range(15)])
        xc = 0.5 * (bins[1:] + bins[:-1])
        a.errorbar(np.r_[xc, xc + 1], np.r_[mu, mu], np.r_[se, se], fmt="o", color="k", ms=4)
        sd = 4 * np.nanmax(se) + 2 * out["comb"]["A"]
        a.set_ylim(1 - sd, 1 + sd)
        bi = out["bands"].get(b, {})
        a.set_title(f"{b} n={D[b]['n']} A={100*bi.get('A',0):.2f}+-{100*bi.get('eA',0):.2f}% p1={bi.get('single_trial_p',1):.1e}", fontsize=9)
        a.set_xlabel(f"phase (P = {24/fc:.5f} h)")
    a = ax[1, 0]
    fz = np.linspace(max(0.06, fc - 3.5), fc + 3.5, 20000)
    a.plot(fz, LombScargle(t, f, e).power(fz), "k", lw=0.6)
    for b, col in (("zg", "g"), ("zr", "r")):
        if b in D: a.plot(fz, LombScargle(D[b]["t"], D[b]["f"], D[b]["e"]).power(fz), color=col, lw=0.5, alpha=0.6)
    a.axvline(fc, color="b", ls=":", lw=0.8); a.set_title(f"local periodogram +-3.5 c/d (black=comb)", fontsize=9); a.set_xlabel("c/d")
    a = ax[1, 1]
    labs = list(halves.keys()); a.bar(range(len(labs)), [100 * halves[k]["A"] for k in labs], yerr=[100 * halves[k]["eA"] for k in labs])
    a.set_xticks(range(len(labs))); a.set_xticklabels(labs, fontsize=7); a.set_ylabel("amplitude (%)"); a.set_title("amplitude in data splits", fontsize=9)
    a = ax[1, 2]
    a.plot(freq[::50], pr[::50], "0.4", lw=0.4); a.set_xscale("log"); a.set_title(f"prewhitened residual LS; best {out['prewhitened_best']['f']:.4f} c/d", fontsize=9)
    fig.suptitle(f"{sid} {rec.get('name','')} {label}: f0={fc:.6f} c/d P={24/fc:.5f} h, comb FAP(Baluev,global)={out['comb']['fap_global']:.2g}, A={100*A:.2f}+-{100*eA:.2f}%", fontsize=10)
    fig.tight_layout(); fn = f"cand/{sid}_{fc:.4f}.png"; fig.savefig(fn, dpi=85); plt.close(fig)
    out["figure"] = fn
    json.dump(out, open(f"cand/{sid}_{fc:.4f}.json", "w"), indent=1)
    return out


if __name__ == "__main__":
    sid = sys.argv[1]; f0 = float(sys.argv[2]); lab = sys.argv[3] if len(sys.argv) > 3 else ""
    o = check(sid, f0, lab)
    c = o["comb"]
    print(f"{sid} {lab} f={c['f']:.6f} P={c['P_h']:.5f} h pow={c['power']:.4f} FAPglob={c['fap_global']:.2g} A={100*c['A']:.2f}+-{100*c['eA']:.2f}%")
    for b, v in o["bands"].items():
        print(f"   {b}: n={v['n']} p_single={v['single_trial_p']:.2g} A={100*v['A']:.2f}+-{100*v['eA']:.2f}% phase={v['phase']:.2f}")
    for k, v in o["splits"].items():
        print(f"   {k}: n={v['n']} p_single={v['single_trial_p']:.2g} A={100*v['A']:.2f}+-{100*v['eA']:.2f}% phase={v['phase']:.2f}")
    print("   alias ladder:", " ".join(f"k{x['k']:+d}:{x['f']:.4f}/{x['power']:.4f}" for x in o["alias_ladder"]))
    print("   harmonics:", " ".join(f"x{x['mult']}:{x['f']:.4f}/{x['power']:.4f}" for x in o["harmonics"]))
    print("   injection alias test:", o["injection_alias_test"])
    print("   prewhitened best:", o["prewhitened_best"])
    for x in o["neighbour_oids"]:
        print(f"   neighbour oid {x['oid']} sep={x['sep']:.1f}\" {x['band']} mag={x['mag']:.2f} n={x['n']} p_single={x['single_trial_p']:.2g} A={100*x['A']:.2f}+-{100*x['eA']:.2f}%")
    print("   figure:", o["figure"])
