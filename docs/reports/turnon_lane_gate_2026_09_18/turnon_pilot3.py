#!/usr/bin/env python3
"""Turn-on pilot v2 — rebuilt after the v1 post-mortem (2026-09-18).

v1 defects fixed here:
  1. curl failures returned '' and were silently filed NO_ZTF. IRSA cut the client
     off after ~1,100 queries and the remaining ~3,300 were never really checked.
     -> retries, explicit ZTF_ERROR status, adaptive backoff, modest concurrency.
  2. Selection was artifact-dominated (9/13 blends, 3/13 sub-threshold noise,
     1/13 cosmic ray). The three artifact channels are now rejected IN-PIPELINE:
       - blends       : ZTF per-epoch centroid must sit within 1.0" of the target
       - noise        : each epoch must be >=0.3 mag brighter than its frame limitmag
       - cosmic rays  : catflags==0, |sharp|<0.3, chi<2, and >=2 distinct nights
       - constants    : duty cycle < 0.9 (a constant ZTF source is a blend)
"""
import csv, io, json, math, os, random, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

OUT = "turnon_out"
RES = f"{OUT}/ztf_assess3_dated.jsonl"
CAND = f"{OUT}/candidates_delta.csv"
NTHREAD = 3
MIN_INTERVAL = 0.45          # seconds between request starts (~2.2 req/s global)

_lk = threading.Lock()
_last = [0.0]
_consec_fail = [0]

def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

def throttle():
    with _lk:
        dt = time.time() - _last[0]
        if dt < MIN_INTERVAL: time.sleep(MIN_INTERVAL - dt)
        _last[0] = time.time()

def ztf_at(ra, dec, rad_deg=0.00083, tries=4):
    """Return list-of-rows, or None on hard failure. Never conflates the two."""
    url = ("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?"
           f"POS=CIRCLE%20{ra:.6f}%20{dec:.6f}%20{rad_deg}"
           "&BAD_CATFLAGS_MASK=32768&FORMAT=CSV")
    for k in range(tries):
        throttle()
        p = subprocess.run(["curl", "-sL", "--max-time", "150", url],
                           capture_output=True, text=True)
        if p.returncode == 0 and "oid" in p.stdout:
            with _lk: _consec_fail[0] = 0
            return list(csv.DictReader(io.StringIO(p.stdout)))
        with _lk:
            _consec_fail[0] += 1
            n = _consec_fail[0]
        # adaptive backoff: a run of failures means we are being throttled
        time.sleep(min(60, 3 * (k + 1) + (20 if n > 8 else 0)))
    return None

def good_epoch(r):
    """Reject the artifact channels at epoch level."""
    try:
        m, lim = float(r["mag"]), float(r["limitmag"])
        if r["catflags"] != "0":        return False
        if abs(float(r["sharp"])) >= 0.3: return False
        if float(r["chi"]) >= 2.0:      return False
        if m > lim - 0.3:               return False   # sub-threshold noise
        return True
    except Exception:
        return False

def assess(c):
    cid = c["id"]; ra, dec = float(c["ra"]), float(c["dec"])
    rows = ztf_at(ra, dec)
    if rows is None:  return dict(id=cid, status="ZTF_ERROR")
    if not rows:      return dict(id=cid, status="NO_ZTF")
    ok = [r for r in rows if good_epoch(r)]
    if len(ok) < 3:   return dict(id=cid, status="ZTF_SPARSE", n_raw=len(rows), n_good=len(ok))

    best = None
    for band in ("zr", "zg"):
        v = [r for r in ok if r["filtercode"] == band]
        if len(v) < 3: continue
        mags = sorted(float(r["mag"]) for r in v)
        bright = mags[max(0, int(0.05 * len(mags)))]
        thr = bright + 1.0
        nights = {}
        for r in v: nights.setdefault(int(float(r["mjd"])), []).append(float(r["mag"]))
        bn = [n for n, ms in nights.items() if min(ms) < thr]
        bright_ep = [r for r in v if float(r["mag"]) < thr]
        # centroid of the bright state -> is ZTF measuring OUR star?
        cra = sorted(float(r["ra"]) for r in bright_ep)[len(bright_ep)//2]
        cdec = sorted(float(r["dec"]) for r in bright_ep)[len(bright_ep)//2]
        off = 3600 * math.hypot((cra-ra)*math.cos(math.radians(dec)), cdec-dec)
        rec = dict(band=band, n=len(v), bright=round(bright, 3), faint=round(mags[-1], 3),
                   nights=len(nights), bright_nights=len(bn),
                   duty=round(len(bn)/len(nights), 3), offset_as=round(off, 2),
                   span=round(max(float(r["mjd"]) for r in bright_ep) -
                              min(float(r["mjd"]) for r in bright_ep), 2))
        if best is None or rec["bright"] < best["bright"]: best = rec
    if best is None: return dict(id=cid, status="ZTF_SPARSE", n_raw=len(rows), n_good=len(ok))

    # v3: amplitude from the DATED pre-ZTF r-band mean (nsc_dr2.meas), not the
    # object-table average. The object columns aggregate over all bands and all
    # epochs; r_pre is the mean of r measurements with mjd < 58119 only.
    r_archival = float(c.get("r_pre") or c["rmag"])
    amp = r_archival - best["bright"]
    out = dict(id=cid, ra=ra, dec=dec, nsc_r=r_archival, nsc_r_obj=float(c["rmag"]),
               n_r_pre=int(float(c.get("n_r_pre") or 0)), nsc_g=float(c["gmag"]),
               amp=round(amp, 2), **best)
    # --- the gauntlet -----------------------------------------------------
    # NOTE (external review, 2026-09-18): duty>0.9 was previously a VETO. That was a
    # self-inflicted blindness - a turn-on that completed BEFORE ZTF began is constant
    # THROUGHOUT ZTF (duty=1.0), i.e. the veto rejected the lane's primary target class.
    # Blends also have duty~1.0, but blends are already removed by the centroid test
    # above, which runs first. Duty is now a BRANCH LABEL, never a rejection.
    if best["offset_as"] > 1.0:        out["status"] = "BLEND"
    elif best["bright_nights"] < 2:    out["status"] = "SINGLE_NIGHT"
    elif amp <= 2.5:                   out["status"] = "NO_TURNON"
    elif best["span"] <= 30 and best["duty"] <= 0.9:
                                       out["status"] = "SHORT_SPAN"
    elif best["duty"] > 0.9:           out["status"] = "CANDIDATE_SUSTAINED"
    else:                              out["status"] = "CANDIDATE_OUTBURST"
    return out

cands = list(csv.DictReader(open(CAND)))
done = set()
if os.path.exists(RES):
    for l in open(RES):
        try: done.add(json.loads(l)["id"])
        except Exception: pass
todo = [c for c in cands if c["id"] not in done]
# v1's fatal bias: positions were processed in tile order, so when the archive cut
# us off the completed set was one tile, and that looked like sky structure.
# Shuffling means ANY partial run is an unbiased sample of the whole footprint.
random.seed(20260918); random.shuffle(todo)
log(f"pilot v2: {len(cands)} total, {len(done)} already done, {len(todo)} to go "
    f"({NTHREAD} threads, ~{1/MIN_INTERVAL:.1f} req/s)")

fh = open(RES, "a")
n = 0; t0 = time.time()
with ThreadPoolExecutor(max_workers=NTHREAD) as ex:
    for r in ex.map(assess, todo):
        n += 1
        with _lk:
            fh.write(json.dumps(r) + "\n"); fh.flush()
        if str(r.get("status","")).startswith("CANDIDATE"):
            log(f"  *** {r['status']} {r['id']} RA {r['ra']:.5f} Dec {r['dec']:+.5f} "
                f"r={r['nsc_r']:.2f} -> {r['band']} {r['bright']:.2f} amp={r['amp']} "
                f"off={r['offset_as']}\" duty={r['duty']} nights={r['bright_nights']}")
        if r.get("status") == "ZTF_ERROR":
            log(f"  ZTF_ERROR {r['id']} (recorded, not silently filed NO_ZTF)")
        if n % 100 == 0:
            rate = n / (time.time() - t0)
            log(f"  {n}/{len(todo)}  {rate:.2f}/s  eta {(len(todo)-n)/rate/60:.0f} min")
fh.close()

rows = [json.loads(l) for l in open(RES)]
import collections
log("FINAL: " + str(dict(collections.Counter(r["status"] for r in rows))))
cand = [r for r in rows if str(r["status"]).startswith("CANDIDATE")]
json.dump(cand, open(f"{OUT}/turnon_candidates3_dated.json", "w"), indent=1)
log(f"wrote {len(cand)} candidates to turnon_candidates3_dated.json")
