"""Pull every ZTF object whose top-ranked ALeRCE class is CV/Nova (probability >= 0.3) from two classifiers.
Output: alerce_cvnova.csv (oid, meanra, meandec, ndet, firstmjd, lastmjd, classifier, probability). Failed pages are retried; a page that still fails is recorded in failed_pages.txt (a hole, not a null)."""
import requests, time, pandas as pd, sys
B = "https://api.alerce.online/ztf/v1/objects"; rows = []; failed = []
for clf in ("lc_classifier", "lc_classifier_BHRF_forced_phot"):
    page = 1
    while True:
        p = {"classifier": clf, "class": "CV/Nova", "probability": 0.3, "ranking": 1, "page_size": 1000, "page": page, "count": "false", "order_by": "oid", "order_mode": "ASC"}
        for k in range(5):
            try:
                r = requests.get(B, params=p, timeout=300)
                if r.ok: j = r.json(); break
            except Exception: pass
            time.sleep(10 * (k + 1))
        else:
            failed.append((clf, page)); print("FAILED", clf, page, flush=True); page += 1; 
            if len(failed) > 5: break
            continue
        it = j.get("items", [])
        for i in it: rows.append({k: i.get(k) for k in ("oid", "meanra", "meandec", "ndet", "ndethist", "firstmjd", "lastmjd", "g_r_mean_corr", "stellar", "probability")} | {"classifier": clf})
        print(clf, "page", page, len(it), "total rows", len(rows), flush=True)
        if len(it) < 1000: break
        page += 1; time.sleep(0.5)
pd.DataFrame(rows).to_csv("alerce_cvnova.csv", index=False); open("failed_pages.txt", "w").write("\n".join(map(str, failed)))
print("done", len(rows), "rows;", pd.DataFrame(rows).oid.nunique(), "unique oids; failed pages", failed)
