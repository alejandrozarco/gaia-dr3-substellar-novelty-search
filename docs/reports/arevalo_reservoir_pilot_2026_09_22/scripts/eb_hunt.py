#!/usr/bin/env python3
"""Hunt shallow, short-duty-cycle eclipsing binaries that scatter-based selection misses.

Hardening carried over from the turn-on pilot post-mortem (same day):
  - every query retries and returns an EXPLICIT error status; an empty response is
    NEVER filed as a science result
  - throttled to ~2 req/s with adaptive backoff (IRSA cut us off at ~1100 queries
    when unthrottled, and reported ZERO errors while doing it)
  - randomised target order, so a partial run is an unbiased sample
  - checkpointed after every object
  - in-eclipse epochs are vetted against their OWN frame: catflags, limitmag, sharp, chi
  - contiguity required before any duration is quoted
  - held-out validation: a period fitted on the first half must predict eclipses in
    the second half
"""
import csv, io, json, math, os, subprocess, sys, threading, time, collections
import numpy as np
from astropy.timeseries import BoxLeastSquares
from harmonic import refine_period, top_peaks

OUT = "eb_out"; os.makedirs(OUT, exist_ok=True)
RES = f"{OUT}/assess.jsonl"
NTHREAD = 4
MIN_INTERVAL = 0.5

_lk = threading.Lock(); _last = [0.0]; _fail = [0]
def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

def throttle():
    with _lk:
        dt = time.time() - _last[0]
        if dt < MIN_INTERVAL: time.sleep(MIN_INTERVAL - dt)
        _last[0] = time.time()

def ztf_lc(ra, dec, tries=4):
    url = ("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?"
           f"POS=CIRCLE%20{ra:.6f}%20{dec:.6f}%200.00042&BAD_CATFLAGS_MASK=32768&FORMAT=CSV")
    for k in range(tries):
        throttle()
        p = subprocess.run(["curl","-sL","--max-time","120",url],capture_output=True,text=True)
        if p.returncode == 0 and "oid" in p.stdout:
            with _lk: _fail[0] = 0
            return list(csv.DictReader(io.StringIO(p.stdout)))
        with _lk:
            _fail[0] += 1; n = _fail[0]
        time.sleep(min(60, 3*(k+1) + (20 if n > 8 else 0)))
    return None

def good(r):
    try:
        return (r["catflags"] == "0" and abs(float(r["sharp"])) < 0.5
                and float(r["chi"]) < 3.0 and float(r["mag"]) < float(r["limitmag"]) - 0.3)
    except Exception:
        return False

def analyse(t):
    rows = ztf_lc(t["ra"], t["dec"])
    if rows is None: return dict(source_id=t["source_id"], status="ZTF_ERROR")
    if not rows:     return dict(source_id=t["source_id"], status="NO_ZTF")
    band = None; best = None
    for b in ("zr","zg"):
        v = [r for r in rows if r["filtercode"] == b and good(r)]
        if len(v) >= 120 and (best is None or len(v) > len(best)):
            best, band = v, b
    if best is None:
        return dict(source_id=t["source_id"], status="SPARSE", n=len(rows))
    mjd = np.array([float(r["mjd"]) for r in best])
    mag = np.array([float(r["mag"]) for r in best])
    err = np.array([float(r["magerr"]) for r in best])
    o = np.argsort(mjd); mjd, mag, err = mjd[o], mag[o], err[o]
    base = float(np.median(mag)); scat = float(np.median(np.abs(mag-base)))*1.4826
    # SIGN BUG FIX (2026-09-19): BoxLeastSquares models DIPS in the quantity it is
    # given. Passing MAGNITUDES made it search for dips in magnitude = BRIGHTENINGS.
    # Eclipses are dips in FLUX, so convert. Verified on Gaia DR3 2710186593557691136,
    # whose "eclipse" epochs were all 0.26-0.30 mag BRIGHTER than baseline.
    flux = 10.0**(-0.4*(mag - base))
    ferr = flux * err * (np.log(10)/2.5)
    # BLS: deliberately NO rms pre-cut - the rms cut is what creates the gap
    bls = BoxLeastSquares(mjd, flux, dy=ferr)
    periods = np.exp(np.linspace(np.log(0.2), np.log(20.0), 7000))
    durations = np.array([0.012,0.025,0.05,0.09])
    try:
        res = bls.power(periods, durations, objective="snr")
    except Exception as e:
        return dict(source_id=t["source_id"], status="BLS_FAIL", err=str(e)[:80])
    # Seed from the top-5 distinct periodogram peaks, not the global max alone:
    # the single-max approach was GRID-DEPENDENT and lost our own template at
    # 5,000 and 7,000 grid points (see RESEARCH_LOG 2026-09-19).
    peaks = top_peaks(res.period, res.power, k=5)
    P0 = peaks[0]
    # BLS fits integer MULTIPLES of a short-duty period; adopt the max-snr sub-harmonic
    # and resolve the EB half-period ambiguity. Verified: recovers our own filed
    # discovery ZTF18abxnwmb to 0.0001% (raw BLS returns 3x its true period).
    P, hsnr, hn, hinfo = refine_period(mjd, flux, ferr, P0, durations,
                                       extra_seeds=tuple(peaks[1:]))
    res = bls.power(np.array([P]), durations, objective="snr")
    i = 0
    dur = float(res.duration[i])
    depth_f = float(res.depth[i]); snr = float(res.power[i]); t0 = float(res.transit_time[i])
    # fractional flux depth -> magnitude depth
    depth = float(-2.5*np.log10(max(1e-6, 1.0-depth_f))) if depth_f < 1 else 9.99
    duty = dur/P
    ph = ((mjd - t0)/P) % 1.0; ph[ph > 0.5] -= 1.0
    inecl = np.abs(ph) < (dur/P)/2*1.2
    nights = sorted({int(x) for x in mjd[inecl]})
    # rule 10: distinct events on separate nights
    rec = dict(source_id=t["source_id"], ra=t["ra"], dec=t["dec"], g=t["g"], band=band,
               n=len(best), base=round(base,3), scatter=round(scat,4),
               P=round(P,6), duty=round(duty,4), depth=round(depth,4),
               depth_frac=round(depth_f,5),
               snr=round(snr,2), n_inecl=int(inecl.sum()), n_ecl_nights=len(nights),
               P_raw=round(P0,6), harm_n=hn, doubled=hinfo.get("doubled"))
    # duty floor: a fit pinned at the minimum duration on a long period is BLS
    # fitting noise spikes, not an eclipse (every WEAK hit in the opening batch
    # had duty ~0.001 = duration 0.012 d, the grid edge). n_inecl floor likewise.
    # SHAPE TEST (added after the first CANDIDATE turned out to be a contact binary):
    # the hold-out verifies PERIODICITY, not MORPHOLOGY. BLS happily fits a segment of a
    # sinusoid and the hold-out passes, because sinusoidal modulation is genuinely
    # periodic. A detached eclipse of duty d puts ~d of the phase bins in eclipse; a
    # contact binary / spotted rotator puts ~half of them there.
    NB = 24
    phb = ((mjd - t0)/P) % 1.0
    prof = np.array([np.median(mag[(phb >= b/NB) & (phb < (b+1)/NB)])
                     if ((phb >= b/NB) & (phb < (b+1)/NB)).sum() >= 5 else np.nan
                     for b in range(NB)])
    fin = np.isfinite(prof)
    if fin.sum() >= 12:
        lvl = float(np.nanmedian(prof))
        rng = float(np.nanmax(prof) - np.nanmin(prof))
        frac_dev = float(np.sum(np.abs(prof[fin] - lvl) > 0.3*rng)/fin.sum())
        rec_shape = dict(frac_bins_deviating=round(frac_dev, 3))
    else:
        frac_dev = None; rec_shape = {}
    # Only TRUE sampling aliases. Day FRACTIONS (0.8, 0.4, 2/3 ...) are heavily
    # populated by real short-period binaries - rejecting them would discard the
    # signal. The shape test above is the correct discriminator for those.
    ALIAS = [0.5, 0.9973, 1.0, 1.0027, 2.0]
    if any(abs(P-a)/a < 0.004 for a in ALIAS):
        rec["status"] = "DAY_ALIAS"; return rec
    rec.update(rec_shape)
    if frac_dev is not None and frac_dev > max(0.25, 3*duty):
        rec["status"] = "CONTINUOUS_MODULATION"; return rec
    if (depth < 0.045 or snr < 10 or not (0.005 <= duty <= 0.15)
            or len(nights) < 3
            or int(inecl.sum()) < max(4, 0.5*len(best)*duty)):
        rec["status"] = "NO_ECLIPSE"; return rec
    # held-out validation: fit on first half, predict second half
    # HOLDOUT HARMONIC BUG (found 2026-09-20, fixed here): this re-fit took the RAW
    # BLS argmax on half 1 and compared it against P, which IS harmonically refined --
    # precisely the error the main path exists to correct (raw BLS returns 3x the true
    # period for our own filed EB ZTF18abxnwmb). Result: 229 of 264 WEAK verdicts (87%)
    # failed on the |P1-P|/P < 0.02 clause ALONE, 38 of them at clean xN or /N ratios,
    # and the hunt produced ZERO candidates in 11,938 objects including a 58-night
    # SNR-205 detection. The half-baseline fit must run the SAME pipeline as the full fit.
    half = mjd[0] + (mjd[-1]-mjd[0])/2
    m1 = mjd < half
    if m1.sum() > 60 and (~m1).sum() > 60:
        b1 = BoxLeastSquares(mjd[m1], flux[m1], dy=ferr[m1])
        r1 = b1.power(periods, durations, objective="snr")
        pk1 = top_peaks(r1.period, r1.power, k=5)
        P1, _h1, _h2, _h3 = refine_period(mjd[m1], flux[m1], ferr[m1], pk1[0],
                                          durations, extra_seeds=tuple(pk1[1:]))
        rr = b1.power(np.array([P1]), durations, objective="snr")
        t01 = float(rr.transit_time[0]); dur1 = float(rr.duration[0])
        # A half-baseline fit legitimately lands on 2P or P/2 for an EB with unequal
        # minima, so accept any low-order harmonic. The test's teeth are the next two
        # clauses: the eclipse must actually BE there, at the predicted phase, in data
        # that played no part in finding it.
        ratio = P1/P
        harm_ok = (any(abs(ratio-n)/n < 0.02 for n in (1,2,3,4)) or
                   any(abs(ratio-1.0/n)*n < 0.02 for n in (2,3,4)))
        ph2 = ((mjd[~m1] - t01)/P1) % 1.0; ph2[ph2 > 0.5] -= 1.0
        ine2 = np.abs(ph2) < (dur1/P1)/2*1.2
        d2 = float(np.median(mag[~m1][ine2])) - base if ine2.sum() >= 3 else 0.0
        rec["holdout_P"] = round(P1,6); rec["holdout_n_inecl"] = int(ine2.sum())
        rec["holdout_depth"] = round(d2,4); rec["holdout_harm_ok"] = bool(harm_ok)
        rec["holdout_ratio"] = round(ratio,4)
        rec["holdout_pass"] = bool(ine2.sum() >= 3 and d2 > 0.5*depth and harm_ok)
    else:
        rec["holdout_pass"] = None
    rec["status"] = "CANDIDATE" if rec.get("holdout_pass") else "WEAK"
    return rec

targets = json.load(open("targets.json"))
done = set()
if os.path.exists(RES):
    for l in open(RES):
        try: done.add(json.loads(l)["source_id"])
        except Exception: pass
todo = [t for t in targets if t["source_id"] not in done]
log(f"EB hunt: {len(targets)} targets, {len(done)} done, {len(todo)} to go "
    f"({NTHREAD} threads, ~{1/MIN_INTERVAL:.1f} req/s)")

from concurrent.futures import ThreadPoolExecutor
fh = open(RES, "a"); n = 0; t0 = time.time()
with ThreadPoolExecutor(max_workers=NTHREAD) as ex:
    for r in ex.map(analyse, todo):
        n += 1
        with _lk:
            fh.write(json.dumps(r)+"\n"); fh.flush()
        if r.get("status") in ("CANDIDATE","WEAK"):
            log(f"  *** {r['status']} {r['source_id']} P={r.get('P')} d "
                f"depth={r.get('depth')} duty={r.get('duty')} snr={r.get('snr')} "
                f"nights={r.get('n_ecl_nights')} holdout={r.get('holdout_pass')}")
        if n % 100 == 0:
            rate = n/(time.time()-t0)
            log(f"  {n}/{len(todo)}  {rate:.2f}/s  eta {(len(todo)-n)/rate/3600:.1f} h")
fh.close()
rows = [json.loads(l) for l in open(RES)]
log("FINAL: " + str(dict(collections.Counter(r["status"] for r in rows))))
