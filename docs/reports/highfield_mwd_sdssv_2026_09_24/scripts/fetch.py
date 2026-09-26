# Download SDSS-V DR20 Astra 0.8.1 mwmStar (or mwmVisit) files for a list of sdss_ids; append every attempt to a manifest
# (HTTP status, bytes, UTC time) so that failed downloads are recorded as HOLES, never silently skipped.
# usage: python fetch.py star|visit <sdss_id> [<sdss_id> ...]
import sys, os, subprocess, datetime
kind = sys.argv[1]; ids = sys.argv[2:]
os.makedirs("spec", exist_ok=True)
man = open("download_manifest.tsv", "a")
for s in ids:
    s = str(int(float(s)))
    fn = f"spec/mwm{'Star' if kind == 'star' else 'Visit'}-0.8.1-{s}.fits"
    if os.path.exists(fn) and os.path.getsize(fn) > 10000:
        print("have", fn); continue
    url = f"https://data.sdss.org/sas/dr20/spectro/astra/0.8.1/spectra/{'star' if kind == 'star' else 'visit'}/{s[-4:-2]}/{s[-2:]}/{os.path.basename(fn)}"
    r = subprocess.run(["curl", "-s", "-m", "240", "-o", fn, "-w", "%{http_code} %{size_download}", url], capture_output=True, text=True)
    code, size = (r.stdout.split() + ["?", "?"])[:2]
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    man.write(f"{ts}\t{kind}\t{s}\t{code}\t{size}\t{url}\n"); man.flush()
    if code != "200":
        print("HOLE", s, code); os.path.exists(fn) and os.remove(fn)
    else:
        print("ok", s, size)
