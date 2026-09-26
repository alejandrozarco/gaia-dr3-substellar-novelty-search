# VarWISE J075330.99-004209.7 = Gaia DR3 3082614748370926848: NEOWISE censoring test.
# Frames covering the target ~ frames in which any other source within 90" was detected (same 47' frame). Missing target detections
# in those frames are non-detections (censored, faint). Do they cluster at the faint phase of P = 0.1053647 d?
import io, csv, json, subprocess, time, numpy as np
ra0, de0, pmra, pmde = 118.37915389890948, -0.7026847809804327, 8.3706, -8.7146
P = 0.1053647
def tap(q):
    for k in range(6):
        p = subprocess.run(["curl", "-s", "--max-time", "900", "--data-urlencode", f"QUERY={q}", "--data-urlencode", "FORMAT=csv",
                            "--data-urlencode", "LANG=ADQL", "--data-urlencode", "REQUEST=doQuery", "https://irsa.ipac.caltech.edu/TAP/sync"], capture_output=True, text=True)
        if p.stdout.startswith("scan_id") or p.stdout.startswith("mjd"): return list(csv.DictReader(io.StringIO(p.stdout)))
        time.sleep(30 * (k + 1))
    raise SystemExit("IRSA TAP failed")
rows = tap(f"SELECT scan_id, frame_num, mjd, ra, dec, w1mpro, w1sigmpro, w1snr, qual_frame, qi_fact, saa_sep, moon_masked, cc_flags, nb, na "
           f"FROM neowiser_p1bs_psd WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{ra0},{de0},{90/3600}))=1")
T, O = {}, {}
for q in rows:
    fk = q["scan_id"] + "_" + q["frame_num"]; t = float(q["mjd"])
    yr = (t - 57388.0) / 365.25; rap = ra0 + pmra * yr / 3.6e6 / np.cos(np.radians(de0)); dep = de0 + pmde * yr / 3.6e6
    sep = np.hypot((float(q["ra"]) - rap) * np.cos(np.radians(de0)), float(q["dec"]) - dep) * 3600
    good = float(q["qual_frame"]) > 0 and float(q["qi_fact"]) > 0 and float(q["saa_sep"]) > 0 and q["moon_masked"][0] == "0"
    if sep < 3: T[fk] = (t, float(q["w1mpro"]), float(q["w1snr"]) if q["w1snr"] else np.nan, good)
    elif sep > 10: O.setdefault(fk, []).append((t, good))
cover = {fk: v[0][0] for fk, v in O.items() if any(g for _, g in v)}          # frames with a good-quality detection of another source
print(f"target detections {len(T)}; frames covering (other sources detected, good quality) {len(cover)}; "
      f"target detected in {sum(fk in T for fk in cover)} of them; missing {sum(fk not in T for fk in cover)}")
bjd_off = 0.0  # phases only need a consistent time base; the barycentric correction varies < 0.006 d over a visit
ph_det = np.array([(((v[0] - 59000.0) / P) % 1) for fk, v in T.items() if fk in cover])
mag_det = np.array([v[1] for fk, v in T.items() if fk in cover])
ph_mis = np.array([(((t - 59000.0) / P) % 1) for fk, t in cover.items() if fk not in T])
# locate the faint phase from the detected magnitudes (sinusoid fit)
X = np.vstack([np.ones_like(ph_det), np.cos(2 * np.pi * ph_det), np.sin(2 * np.pi * ph_det)]).T
b, *_ = np.linalg.lstsq(X, mag_det, rcond=None); faint = (np.arctan2(b[2], b[1]) / (2 * np.pi)) % 1
d_det = np.abs(((ph_det - faint + 0.5) % 1) - 0.5); d_mis = np.abs(((ph_mis - faint + 0.5) % 1) - 0.5)
print(f"faint phase (fit to detections) {faint:.3f}; fraction within 0.25 cycles of the faint phase: detections {np.mean(d_det < 0.25):.2f} "
      f"(n={len(d_det)}), non-detections {np.mean(d_mis < 0.25):.2f} (n={len(d_mis)})")
# binned detection fraction vs phase
edges = np.linspace(0, 0.5, 6)
for lo, hi in zip(edges[:-1], edges[1:]):
    nd = np.sum((d_det >= lo) & (d_det < hi)); nm = np.sum((d_mis >= lo) & (d_mis < hi))
    print(f"   |phase - faint| {lo:.1f}-{hi:.1f}: detected {nd}, missing {nm}, detection fraction {nd / max(nd + nm, 1):.2f}")
json.dump(dict(n_det=int(len(T)), n_cover=len(cover), n_missing=int(len(ph_mis)), faint_phase=float(faint),
               frac_missing_near_faint=float(np.mean(d_mis < 0.25)) if len(d_mis) else None), open("j0753_censor.json", "w"), indent=1)
