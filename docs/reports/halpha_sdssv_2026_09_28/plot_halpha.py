"""Vetting plots for the H-alpha screen: for each sdss_id, the normalised coadd with its fitted neighbour template, the coadd residual
with the matched-filter position, and the per-visit residuals (offset). Usage: python plot_halpha.py <screen.csv> id1,id2,... [outdir]"""
import os, sys, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = os.path.dirname(os.path.abspath(__file__)); sys.argv = [sys.argv[0], "--out", "/dev/null", "--ids", sys.argv[2]] + (["--limit", "0"])
outdir = "plots"; os.makedirs(os.path.join(D, outdir), exist_ok=True)
src = open(os.path.join(D, "screen_halpha.py")).read(); exec(src.split("ids = A.ids.split")[0])
for sid in A.ids.split(","):
    tm, nn, sc = template(sid); d = np.load(os.path.join(D, "halpha_store", sid[-2:], f"{sid}.npz")); n_c = NC[sid]; e_c = EC[sid]
    model = fit_template(n_c, e_c, tm) if tm is not None else np.ones(len(W)); r_c = n_c - model
    fig, ax = plt.subplots(3, 1, figsize=(9, 9), sharex=True); ax[0].plot(W, n_c, "k", lw=0.8, label="coadd"); ax[0].plot(W, model, "r", lw=0.8, label=f"template ({nn} neighbours)"); ax[0].legend(); ax[0].set_ylabel("normalised flux")
    ax[1].plot(W, r_c, "k", lw=0.8); ax[1].fill_between(W, -np.sqrt(e_c ** 2 + (sc if sc is not None else 0) ** 2), np.sqrt(e_c ** 2 + (sc if sc is not None else 0) ** 2), color="0.8"); ax[1].axhline(0, color="r", lw=0.5); ax[1].set_ylabel("coadd residual")
    for i in range(len(d["mjd"])):
        n_i = d["n"][i].astype(float); e_i = d["e"][i].astype(float); r_i = n_i - (fit_template(n_i, e_i, tm) if tm is not None else 1); ax[2].plot(W, r_i + 0.15 * i, lw=0.6, label=f"MJD {d['mjd'][i]} S/N {d['snr'][i]:.0f}")
    ax[2].legend(fontsize=7); ax[2].set_ylabel("visit residuals (offset)"); ax[2].set_xlabel("wavelength (A)"); ax[0].set_title(f"{sid}  {T.loc[sid].classification if sid in T.index else ''}  G {T.loc[sid].g_mag if sid in T.index else ''}")
    for a in ax: a.axvline(HA, color="b", lw=0.4, alpha=0.5)
    fig.tight_layout(); fig.savefig(os.path.join(D, outdir, f"{sid}.png"), dpi=110); plt.close(fig); print("plot", sid)
