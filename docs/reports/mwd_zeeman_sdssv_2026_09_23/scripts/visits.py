# Visit-level robustness check. Astra 0.8.1 resamples each BOSS visit to a "rest frame" using the XCSAO radial velocity
# (column xcsao_v_rad, "Barycentric rest frame radial velocity"), even when that velocity is meaningless for a white dwarf
# (WD 0745+365: +4212 km/s, which moves every Balmer line ~70-90 A to the blue in its mwmStar coadd). A coadd of visits with
# different spurious shifts could mimic split lines. Here: (1) list xcsao_v_rad per visit for every target, (2) undo the shift
# (lambda_bary = lambda_rest * (1 + v/c)), (3) fit the free-centre Zeeman triplet (zfit_free.fit) to every visit with S/N >= 8.
# Doppler copies scale as lambda (B_Hb/B_Ha = 1.35 in these units), Zeeman components as lambda^2 (ratio 1).
import sys, csv, os, subprocess, json, numpy as np, warnings
warnings.filterwarnings("ignore")
from astropy.io import fits
sys.argv = [sys.argv[0]]; import zfit_free as Z
SW = {r["gaia_dr3_source_id"]: r for r in csv.DictReader(open("sw_magnetic.csv"))}
ids = [l.split()[0] for f in ("vis_list.txt", "vis_list2.txt") for l in open(f) if l.strip() and not l.startswith("#")] + ["600396471902522624"]
c = 299792.458; out = {}
for g in dict.fromkeys(ids):
    s = SW[g]["sdss_id"]; fn = f"spec/mwmVisit-0.8.1-{s}.fits"
    if not os.path.exists(fn):
        subprocess.run(["curl", "-s", "-m", "180", "-o", fn, f"https://data.sdss.org/sas/dr20/spectro/astra/0.8.1/spectra/visit/{s[-4:-2]}/{s[-2:]}/mwmVisit-0.8.1-{s}.fits"])
    h = fits.open(fn); rows = []
    for i in (1, 2):
        if h[i].data is None or len(h[i].data) == 0: continue
        hd = h[i].header; lam_rest = 10 ** (hd["CRVAL"] + hd["CDELT"] * np.arange(hd["NPIXELS"]))
        for r in h[i].data:
            v = float(r["xcsao_v_rad"]); snr = float(r["snr"]); rec = dict(mjd=int(r["mjd"]), v_rad=v, snr=snr, in_stack=bool(r["in_stack"]))
            if snr >= 8 and np.isfinite(v):
                lam = lam_rest * (1 + v / c); f = np.array(r["flux"], float); iv = np.array(r["ivar"], float)
                for k in ("Ha", "Hb"):
                    m = (lam > Z.WIN[k][0]) & (lam < Z.WIN[k][1])
                    try:
                        p, C, chi2r, _, _ = Z.fit(lam[m], f[m], iv[m], Z.L0[k], 6.0 * Z.K[k])
                        rec[f"B_{k}"] = float((p[10] + p[11]) / 2 / Z.K[k]); rec[f"pi_shift_{k}"] = float(p[12]); rec[f"chi2r_{k}"] = float(chi2r)
                    except Exception as e: rec[f"B_{k}"] = None
            rows.append(rec)
    out[g] = rows
    print(g, " | ".join(f"MJD {x['mjd']} v {x['v_rad']:+.0f} S/N {x['snr']:.0f} stack {int(x['in_stack'])}" + (f" B(Ha) {x['B_Ha']:.2f} B(Hb) {x['B_Hb']:.2f} pi {x['pi_shift_Ha']:+.1f}/{x['pi_shift_Hb']:+.1f}A" if x.get('B_Ha') else "") for x in rows), flush=True)
json.dump(out, open("visits.json", "w"), indent=1)
