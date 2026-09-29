"""Vetting of the H-alpha screen output: ranks DA and non-H group objects by coadd and per-visit statistics, applies per-S/N
thresholds derived from the DA null (z above the 99.5th percentile of its coadd-S/N bin), attaches MWDD emission-type flags
(from mwdd_emission_types.json) and the object's Gaia colour/absolute magnitude, and writes vet_list.csv. Usage:
python vet_halpha.py screen_full.csv [mwdd_emission_types.json] [--plots N]"""
import os, sys, json, numpy as np, pandas as pd
D = os.path.dirname(os.path.abspath(__file__)); f = sys.argv[1]; em = json.load(open(sys.argv[2])) if len(sys.argv) > 2 and sys.argv[2].endswith(".json") else {}
nplots = int(sys.argv[sys.argv.index("--plots") + 1]) if "--plots" in sys.argv else 0
N = pd.read_csv(f, dtype={"sdss_id": str, "gaia": str}, low_memory=False); N = N[N.status == "ok"].copy(); print("screened", len(N), N.grp.value_counts().to_dict())
for c in ("G", "bprp", "MG", "nvis", "snr_c", "n_tmpl", "tmpl_scatter", "z_coadd", "v_coadd", "sig_coadd", "npx_coadd", "ew_coadd", "e_ew_coadd", "zb_coadd", "vb_coadd", "sb_coadd", "z_max", "n_vis_z3", "zb_max", "chi2_ew"): N[c] = pd.to_numeric(N[c], errors="coerce")
bad = (N.e_ew_coadd < 0.005) | (N.z_coadd.abs() > 500) | (N.zb_coadd.abs() > 500) | (N.z_max.abs() > 500); print("rows with implausible errors/statistics excluded:", int(bad.sum())); N = N[~bad]
N["wd_locus"] = (N.MG > 8.5) & (N.bprp < 1.0); print("on the white-dwarf locus (M_G > 8.5, BP-RP < 1):", int(N.wd_locus.sum()))
N["mwdd_type"] = N.gaia.map(em).fillna("")
N["snr_bin"] = pd.cut(N.snr_c, [0, 8, 15, 30, 60, 1e9], labels=["<8", "8-15", "15-30", "30-60", ">60"])
da = N[(N.grp == "DA") & N.wd_locus]
thr = {c: da.groupby("snr_bin", observed=True)[c].quantile(0.995).to_dict() for c in ("z_coadd", "zb_coadd", "z_max")}
print("DA 99.5% thresholds by coadd S/N:", {c: {k: round(v, 1) for k, v in d.items()} for c, d in thr.items()})
nh = N[(N.grp == "nonH") & N.wd_locus]; thr_nh = {c: nh.groupby("snr_bin", observed=True)[c].quantile(0.99).to_dict() for c in ("z_coadd", "zb_coadd", "z_max")}
print("non-H 99% thresholds by coadd S/N:", {c: {k: round(v, 1) for k, v in d.items()} for c, d in thr_nh.items()})
for c in thr: N[f"{c}_over"] = N.apply(lambda r: r[c] / ((thr_nh if r.grp == "nonH" else thr)[c].get(r.snr_bin, np.inf)), axis=1)
N["score"] = N[["z_coadd_over", "zb_coadd_over", "z_max_over"]].max(axis=1)
W = N[N.grp.isin(["DA", "nonH"]) & N.wd_locus].copy(); W = W[(W.score > 1) | ((W.chi2_ew > 10) & (W.z_max > 5))].sort_values("score", ascending=False)
W["var"] = (W.chi2_ew > 10) & (W.nvis >= 2) & (W.z_max > 5)
cols = ["sdss_id", "gaia", "cls", "grp", "G", "bprp", "MG", "nvis", "snr_c", "n_tmpl", "z_coadd", "v_coadd", "sig_coadd", "npx_coadd", "ew_coadd", "e_ew_coadd", "zb_coadd", "vb_coadd", "sb_coadd", "z_max", "n_vis_z3", "zb_max", "chi2_ew", "score", "var", "mwdd_type", "z_visits", "ew_visits", "mjds"]
# nebular flag: narrow H-alpha near rest velocity accompanied by a narrow [N II] 6583 line in the coadd residual
import subprocess
def nebular_flags(ids):
    src = open(os.path.join(D, "screen_halpha.py")).read().split("ids = A.ids.split")[0]; ns = {"__file__": os.path.join(D, "screen_halpha.py"), "__name__": "screen_ns"}
    saved = sys.argv; sys.argv = [sys.argv[0], "--out", "/dev/null", "--ids", ",".join(ids)]; exec(src, ns); sys.argv = saved
    out = {}; from astropy.io import fits as _fits; C = 299792.458
    for sid in ids:
        try:
            tm, nn, sc = ns["template"](sid); n_c = ns["NC"][sid]; e_c = ns["EC"][sid]; model = ns["fit_template"](n_c, e_c, tm) if tm is not None else 1.0; r = n_c - model; Wg = ns["W"]
            def zline(lam, width=2.5):
                m = np.abs(Wg - lam) < width; return float((r[m] / e_c[m]).sum() / np.sqrt(m.sum()))
            # ringing and pixel flags on the strongest visit: negative sidelobe ratio within +-20 A of the feature; flagged fraction within +-5 A
            d = np.load(os.path.join(D, "halpha_store", sid[-2:], f"{sid}.npz")); best = (-np.inf, None, None)
            for i in range(len(d["mjd"])):
                n_i = d["n"][i].astype(float); e_i = d["e"][i].astype(float); r_i = n_i - (ns["fit_template"](n_i, e_i, tm) if tm is not None else 1.0)
                k = int(np.nanargmax(np.where(np.isfinite(e_i) & (np.abs(Wg - 6564.6) < 80), r_i / e_i, -np.inf)))
                if r_i[k] / e_i[k] > best[0]: best = (r_i[k] / e_i[k], i, k)
            ring = np.nan; flagged = np.nan
            if best[1] is not None:
                i, k = best[1], best[2]; n_i = d["n"][i].astype(float); e_i = d["e"][i].astype(float); r_i = n_i - (ns["fit_template"](n_i, e_i, tm) if tm is not None else 1.0)
                m = np.abs(Wg - Wg[k]) < 20; ring = float(-np.nanmin(r_i[m]) / max(r_i[k], 1e-6))
                sidp = os.path.join(D, "visit", sid[-4:-2], sid[-2:], f"mwmVisit-0.8.1-{sid}.fits"); mj = int(d["mjd"][i])
                with _fits.open(sidp) as h:
                    for hi in (1, 2):
                        if hi >= len(h) or h[hi].data is None or len(h[hi].data) == 0: continue
                        hd = h[hi].header; wg = 10 ** (hd["CRVAL"] + hd["CDELT"] * np.arange(hd["NPIXELS"]))
                        for row in h[hi].data:
                            if int(row["mjd"]) != mj: continue
                            v = float(row["xcsao_v_rad"]); w = wg * (1 + v / C) if (bool(row["in_stack"]) and np.isfinite(v)) else wg
                            pf = np.array(row["pixel_flags"]); mm = np.abs(w - Wg[k]) < 5; flagged = float((pf[mm] != 0).mean()) if mm.sum() else np.nan
            out[sid] = (round(zline(6564.6), 1), round(zline(6585.3), 1), round(zline(6549.9), 1), round(zline(6718.3), 1), round(ring, 3), round(flagged, 2) if np.isfinite(flagged) else np.nan)
        except Exception as ex: out[sid] = (np.nan, np.nan, np.nan, np.nan, np.nan, np.nan)
    return out
nf = nebular_flags(list(W.sdss_id)); W["z_ha_rest"] = [nf[s][0] for s in W.sdss_id]; W["z_nii6583"] = [nf[s][1] for s in W.sdss_id]; W["z_nii6548"] = [nf[s][2] for s in W.sdss_id]; W["z_sii6717"] = [nf[s][3] for s in W.sdss_id]
W["ring"] = [nf[s][4] for s in W.sdss_id]; W["flagged_core"] = [nf[s][5] for s in W.sdss_id]
W["nebular"] = (W.z_nii6583 > 4) & (W.z_ha_rest > 4); print("nebular-flagged:", int(W.nebular.sum()))
t1 = (W.n_vis_z3 >= 2) & (W.score > 1); t2 = ~t1 & ((W.n_vis_z3 >= 3) | ((W.n_vis_z3 >= 2) & (W.z_coadd > 8))); t3 = (W.nvis == 1) & (W.score > 1)
W["rank_class"] = np.where(W.nebular, "nebular", np.where(t1, "T1", np.where(t2, "T2", np.where(t3, "T3-single", "single-visit-feature"))))
W = W.sort_values(["rank_class", "score"], ascending=[True, False]); print(W.rank_class.value_counts().to_dict())
cols += ["z_ha_rest", "z_nii6583", "z_nii6548", "z_sii6717", "nebular", "ring", "flagged_core", "rank_class"]
W[cols].to_csv(os.path.join(D, "vet_list.csv"), index=False); print("vet list:", len(W), "of which MWDD emission types:", int((W.mwdd_type != "").sum()), "; variable:", int(W["var"].sum()))
pd.set_option("display.width", 260); pd.set_option("display.max_colwidth", 40)
P = W[W.rank_class == "T1"]; print(P[["sdss_id", "gaia", "cls", "G", "bprp", "MG", "nvis", "snr_c", "z_coadd", "v_coadd", "sig_coadd", "zb_coadd", "vb_coadd", "z_max", "n_vis_z3", "chi2_ew", "score", "ring", "mwdd_type"]].head(50).to_string(index=False))
if nplots:
    ids = ",".join(W[W.rank_class == "T1"].sdss_id.head(nplots)); os.system(f"{sys.executable} {os.path.join(D, 'plot_halpha.py')} x {ids} > /dev/null 2>&1"); print("plots written for", nplots)
