# Sequential, polite batch download of mwmStar files for a list of sdss_ids (csv with column sdss_id); logs failures as HOLES.
import sys, csv, time
sys.path.insert(0, "/tmp/fanout/exotic_atm/scripts"); from common import fetch
ids = [r["sdss_id"] for r in csv.DictReader(open(sys.argv[1]))]
kind = sys.argv[2] if len(sys.argv) > 2 else "star"
log = open(sys.argv[1].replace(".csv", f"_{kind}_dl.log"), "w")
ok = bad = 0; t0 = time.time()
for i, s in enumerate(ids):
    fn = fetch(s, kind)
    if fn: ok += 1
    else: bad += 1; log.write(f"HOLE {s}\n"); log.flush()
    if i % 100 == 0: print(i, ok, bad, round(time.time() - t0), flush=True)
    time.sleep(0.05)
print("done", ok, bad, round(time.time() - t0), flush=True); log.write(f"done ok={ok} bad={bad}\n")
