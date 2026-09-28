"""Novelty judge, snippet mode. For each candidate (CSV: gaia, name, measurement[, names]): (1) ADS full-text search by every alias
returns the papers that mention the object by name; (2) for each such paper with an arXiv id, the arXiv source is fetched (cached in
--src, one request per 4 s) and every passage within 600 characters of an alias is extracted (LaTeX stripped; table rows included);
(3) the TypeSafe System One model (Jev) reads the passages and answers, per paper: does the passage discuss this object; does it report
the same measurement as ours; how the value relates to ours. Papers without an arXiv source fall back to title + abstract.
ADS full text does not index most catalogue tables, so 'no paper mentions the object' is weak evidence, recorded as such.
Output CSV adds n_papers, n_with_text, p_reported (max over papers), best_bibcode, best_relation, status.
Usage: python novelty_snippets.py <in.csv> <out.csv> --src <arxiv source dir> [--cache refs.json] [--limit N]"""
import os, re, io, sys, json, time, gzip, tarfile, argparse, requests, pandas as pd, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--src", required=True); ap.add_argument("--cache", default="snippet_cache.json"); ap.add_argument("--limit", type=int, default=0)
A = ap.parse_args(); os.makedirs(A.src, exist_ok=True)
os.environ["TYPESAFE_API_KEY"] = open(os.path.expanduser("~/.config/typesafe/token")).read().strip()
ADS = {"Authorization": "Bearer " + open(os.path.expanduser("~/.config/ads/token")).read().strip()}
from typesafe_sdk import TypeSafeClient
cache = json.load(open(A.cache)) if os.path.exists(A.cache) else {}
def aliases(gaia, name, extra):
    names = [str(name), f"Gaia DR3 {gaia}", f"Gaia EDR3 {gaia}", str(gaia)] + [x.strip() for x in str(extra).split("|") if x.strip() and x.strip() != "nan"]
    w = re.match(r"(?:WDJ|J)(\d{2})(\d{2})(\d{2}(?:\.\d+)?)([+-])(\d{2})(\d{2})(\d{2}(?:\.\d+)?)", str(name))
    if w:
        h, mi, s, sg, d, dm, ds = w.groups(); names += [f"J{h}{mi}{sg}{d}{dm}", f"J{h}{mi}{s[:4]}{sg}{d}{dm}{ds[:2]}", f"J{h}{mi}{s[:2]}{sg}{d}{dm}{ds[:2]}", f"{h}{mi}{s[:2]}{sg}{d}{dm}{ds[:2]}"]
    seen = []; [seen.append(n) for n in names if n not in seen]; return seen
def ads_papers(names):
    q = "(" + " OR ".join(f'full:"{n}"' for n in names if len(n) > 5) + ") collection:astronomy"
    for k in range(3):
        try:
            j = requests.get("https://api.adsabs.harvard.edu/v1/search/query", params=dict(q=q, fl="bibcode,title,abstract,year,identifier", rows=15, sort="date desc"), headers=ADS, timeout=60).json()
            if "response" in j:
                out = []
                for d in j["response"]["docs"]:
                    arx = [i for i in d.get("identifier", []) if i.startswith("arXiv:")]
                    out.append(dict(bibcode=d["bibcode"], year=d.get("year", ""), title=(d.get("title") or [""])[0], abstract=(d.get("abstract") or "")[:1200], arxiv=arx[0].replace("arXiv:", "") if arx else ""))
                return out
        except Exception: pass
        time.sleep(5 * (k + 1))
    return None
def fetch_src(arx):
    p = os.path.join(A.src, arx.replace("/", "_") + ".tar")
    if os.path.exists(p) and os.path.getsize(p) > 1000: return p
    for k in range(3):
        try:
            r = requests.get(f"https://arxiv.org/e-print/{arx}", timeout=120, headers={"User-Agent": "novelty-snippets (astronomy literature check)"})
            if r.status_code == 200 and len(r.content) > 1000: open(p, "wb").write(r.content); time.sleep(4); return p
            if r.status_code in (403, 429): time.sleep(60)
        except Exception: time.sleep(20)
    return None
def texts(p):
    raw = open(p, "rb").read(); out = []
    try:
        with tarfile.open(fileobj=io.BytesIO(raw)) as t:
            for m in t.getmembers():
                if m.name.lower().endswith((".tex", ".txt", ".dat", ".csv")) and m.size < 8_000_000: out.append(t.extractfile(m).read().decode("utf-8", "ignore"))
    except tarfile.TarError:
        try: out.append(gzip.decompress(raw).decode("utf-8", "ignore"))
        except Exception: out.append(raw.decode("utf-8", "ignore"))
    return out
def detex(s):
    s = re.sub(r"%.*", "", s); s = re.sub(r"\\(?:object|textit|textbf|emph|text|mbox)\{([^}]*)\}", r"\1", s); s = re.sub(r"\\cite[tp]?\*?(?:\[[^\]]*\])?\{[^}]*\}", "[ref]", s)
    s = re.sub(r"\$([^$]*)\$", r"\1", s); s = s.replace("\\,", " ").replace("~", " ").replace("--", "-").replace("\\&", "&").replace("&", " | "); s = re.sub(r"\\[a-zA-Z]+\*?", " ", s); s = re.sub(r"[{}]", "", s)
    return re.sub(r"\s+", " ", s).strip()
def snippets(p, names):
    out = []
    pats = [re.compile(re.escape(n).replace(r"\ ", r"\s*").replace(r"\+", r"\s*[+\\]?\s*\+?").replace(r"\-", r"\s*[-\u2212]\s*"), re.I) for n in names if len(n) > 5]
    for tx in texts(p):
        for pat in pats:
            for m in pat.finditer(tx):
                s = detex(tx[max(0, m.start() - 600): m.end() + 600])
                if s and s not in out: out.append(s[:1500])
                if len(out) >= 6: return out
    return out
D = pd.read_csv(A.inp, dtype={"gaia": str})
if A.limit: D = D.head(A.limit)
rows = []; t0 = time.time()
with TypeSafeClient() as client:
    for i, r in D.iterrows():
        rec = dict(r); names = aliases(r.gaia, r["name"], r.get("names", ""))
        papers = cache.get(r.gaia)
        if papers is None:
            papers = ads_papers(names)
            if papers is not None: cache[r.gaia] = papers; json.dump(cache, open(A.cache, "w"))
        if papers is None: rec.update(status="HOLE"); rows.append(rec); continue
        rec["n_papers"] = len(papers)
        if not papers: rec.update(status="no_mentions", n_with_text=0, p_reported=0.0, best_bibcode="", best_relation=""); rows.append(rec); continue
        ev = []
        for pp in papers:
            sn = []
            if pp["arxiv"]:
                src = fetch_src(pp["arxiv"])
                if src: sn = snippets(src, names)
            ev.append(dict(id=f"paper_{len(ev)}", bibcode=pp["bibcode"], year=pp["year"], title=pp["title"], passages=sn if sn else [], abstract=("" if sn else pp["abstract"])))
        rec["n_with_text"] = sum(1 for e in ev if e["passages"])
        state = {"object": {"aliases": names[:8]}, "our_measurement": str(r.measurement), "papers": [{"id": e["id"], "year": e["year"], "title": e["title"], "passages": e["passages"][:6], "abstract": e["abstract"]} for e in ev]}
        qs = {}
        for k, e in enumerate(ev):
            qs[f"same_{k}"] = {"type": "noul", "instructions": f"Do the `papers[{k}].passages` (or its abstract) discuss the object in `object` (any alias, allowing different name formats for the same coordinates)?", "criteria": {"true": "the text discusses this object", "false": "the text only mentions another object or nothing about this one"}}
            qs[f"reports_{k}"] = {"type": "noul", "instructions": f"Does `papers[{k}]` report, for this object, the same kind of measurement as `our_measurement` (a period, a companion, a variability class or a spectral classification)?", "criteria": {"true": "that measurement is reported for this object", "false": "not reported, or reported for a different object"}}
            qs[f"relation_{k}"] = {"type": "choice", "instructions": f"How does the value reported in `papers[{k}]` for this object relate to `our_measurement`?", "criteria": {"same_value": "the same value within rounding or unit conversion", "different_value": "a different value for the same quantity", "not_reported": "no such value is given for this object"}}
        try:
            a = client.system_one(state=state, questions=qs)
            pr = [(a.nouls[f"reports_{k}"].noul * a.nouls[f"same_{k}"].noul, k) for k in range(len(ev))]; pmax, kb = max(pr)
            rec.update(status="ok", p_reported=round(pmax, 3), best_bibcode=ev[kb]["bibcode"], best_title=ev[kb]["title"][:90], best_relation=a.choices[f"relation_{kb}"].choice,
                       p_same_best=round(a.nouls[f"same_{kb}"].noul, 3), tokens=getattr(getattr(a, "usage", None), "input_tokens", None))
        except Exception as ex:
            rec.update(status=f"ERR {type(ex).__name__}")
        rows.append(rec); print(i + 1, r["name"], rec.get("status"), "papers", rec.get("n_papers"), "with text", rec.get("n_with_text"), "p", rec.get("p_reported"), rec.get("best_relation", ""), flush=True)
        if (i + 1) % 10 == 0: pd.DataFrame(rows).to_csv(A.out, index=False)
O = pd.DataFrame(rows); O.to_csv(A.out, index=False); print("done", len(O), O.status.value_counts().to_dict())
