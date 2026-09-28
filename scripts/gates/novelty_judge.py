"""Novelty judge: for each candidate, gather the papers whose ADS full text mentions any of its names (the WDJ/catalogue name, the
Gaia DR3 id, the short Jhhmm+ddmm and Jhhmmss.s+ddmmss forms, and any names in an optional pipe-separated 'names' column; most recent
12, titles and abstracts) and ask the TypeSafe System One model (Jev) whether any of them already reports our measurement for the
object. Code does the retrieval and the numeric matching elsewhere; the model only reads. (SIMBAD reference lists were the first
design; ADS full text by alias replaces them - it also catches papers SIMBAD has not indexed.) Input CSV columns: gaia, name,
measurement[, names, source, ...] - extra columns are passed through.
Output CSV adds n_refs, p_any (probability that a listed reference already reports the measurement), p_max_ref, best_bibcode,
best_title, status (ok / no_refs / HOLE / ERR ...). Reference lookups are cached in --cache (JSON) so reruns cost nothing.
Credentials: ~/.config/typesafe/token and ~/.config/ads/token (read at run time, never printed).
Usage: python novelty_judge.py <in.csv> <out.csv> [--cache refs_cache.json] [--limit N]"""
import os, sys, json, time, argparse, requests, pandas as pd, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--cache", default="refs_cache.json"); ap.add_argument("--limit", type=int, default=0)
A = ap.parse_args()
os.environ["TYPESAFE_API_KEY"] = open(os.path.expanduser("~/.config/typesafe/token")).read().strip()
ADS = {"Authorization": "Bearer " + open(os.path.expanduser("~/.config/ads/token")).read().strip()}
from typesafe_sdk import TypeSafeClient
cache = json.load(open(A.cache)) if os.path.exists(A.cache) else {}
import re
def aliases(gaia, name, extra):
    names = [str(name), f"Gaia DR3 {gaia}"] + [x.strip() for x in str(extra).split("|") if x.strip() and x.strip() != "nan"]
    w = re.match(r"(?:WDJ|J)(\d{2})(\d{2})(\d{2}(?:\.\d+)?)([+-])(\d{2})(\d{2})(\d{2}(?:\.\d+)?)", str(name))
    if w:
        h, mi, s, sg, d, dm, ds = w.groups(); names += [f"J{h}{mi}{sg}{d}{dm}", f"J{h}{mi}{s[:4]}{sg}{d}{dm}{ds[:2]}", f"J{h}{mi}{s[:2]}{sg}{d}{dm}{ds[:2]}"]
    seen = []; [seen.append(n) for n in names if n not in seen]; return seen
def ads_by_alias(names):
    q = "(" + " OR ".join(f'full:"{n}"' for n in names) + ") collection:astronomy"
    for k in range(3):
        try:
            j = requests.get("https://api.adsabs.harvard.edu/v1/search/query", params=dict(q=q, fl="bibcode,title,abstract,year", rows=12, sort="date desc"), headers=ADS, timeout=60).json()
            if "response" in j:
                return [dict(bibcode=d["bibcode"], year=d.get("year", ""), title=(d.get("title") or [""])[0], abstract=(d.get("abstract") or "")[:1500]) for d in j["response"]["docs"]]
        except Exception: pass
        time.sleep(5 * (k + 1))
    return None
def evidence(sid, name, extra):
    if sid in cache: return cache[sid]
    lit = ads_by_alias(aliases(sid, name, extra))
    if lit is not None: cache[sid] = lit; json.dump(cache, open(A.cache, "w"))
    return lit
D = pd.read_csv(A.inp, dtype={"gaia": str})
if A.limit: D = D.head(A.limit)
out = []; t0 = time.time()
with TypeSafeClient() as client:
    for i, r in D.iterrows():
        rec = dict(r); lit = evidence(r.gaia, r["name"], r.get("names", ""))
        if lit is None: rec.update(status="HOLE", n_refs=-1); out.append(rec); continue
        rec["n_refs"] = len(lit)
        if not lit: rec.update(status="no_refs", p_any=0.0, p_max_ref=0.0, best_bibcode="", best_title=""); out.append(rec); continue
        refs = [dict(id=f"ref_{k}", **x) for k, x in enumerate(lit)]
        state = {"object": {"aliases": aliases(r.gaia, r["name"], r.get("names", ""))}, "our_measurement": str(r.measurement), "references": refs}
        qs = {f"reports_{x['id']}": {"type": "noul", "instructions": f"Does reference `references[{k}]` (its title and abstract) already report, for this object or for a catalogue sample that includes it, the same measurement as `our_measurement` (the same period, companion, variability class or spectral classification)?",
                                     "criteria": {"true": "the reference reports that measurement for this object, or is a catalogue of exactly that measurement covering this object", "false": "the reference is about other objects, other quantities, or only lists the object without that measurement"}} for k, x in enumerate(refs)}
        qs["any_reported"] = {"type": "noul", "instructions": "Does at least one entry of `references` already report `our_measurement` for `object`?", "criteria": {"true": "the measurement is already in the listed literature", "false": "none of the listed references reports it"}}
        qs["best_ref"] = {"type": "choice", "instructions": "Which entry of `references` most likely already contains `our_measurement` for `object`, or none?", "criteria": {**{x["id"]: x["title"][:80] for x in refs}, "none": "no listed reference contains it"}}
        try:
            a = client.system_one(state=state, questions=qs)
            bt = {x["id"]: x for x in refs}; best = a.choices["best_ref"].choice
            rec.update(status="ok", p_any=round(a.nouls["any_reported"].noul, 3), p_max_ref=round(max(v.noul for k, v in a.nouls.items() if k.startswith("reports_")), 3),
                       best_bibcode=bt[best]["bibcode"] if best in bt else "", best_title=bt[best]["title"][:90] if best in bt else "",
                       best_conf=round(float(getattr(a.choices["best_ref"], "confidence", np.nan)), 2), tokens=getattr(getattr(a, "usage", None), "input_tokens", None))
        except Exception as ex:
            rec.update(status=f"ERR {type(ex).__name__}")
        out.append(rec)
        if (i + 1) % 25 == 0: print(f"{i + 1}/{len(D)} {time.time() - t0:.0f}s", flush=True); pd.DataFrame(out).to_csv(A.out, index=False)
O = pd.DataFrame(out); O.to_csv(A.out, index=False)
print("done", len(O), O.status.value_counts().to_dict(), "| tokens", int(O.get("tokens", pd.Series(dtype=float)).fillna(0).sum()))
