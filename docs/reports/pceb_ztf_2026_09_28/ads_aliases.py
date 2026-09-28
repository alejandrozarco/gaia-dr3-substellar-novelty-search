"""ADS full-text search by every alias for the PCEB detections without a matching catalogued period (pceb_gated.csv rows with
match empty and not otherwise known). Aliases: WDJ name, Gaia DR3 id, SIMBAD main id, and the short Jhhmm+ddmm and Jhhmmss.s+ddmmss
forms. Writes ads_hits.csv (one row per alias hit: bibcode, year, title). A failed query is recorded as HOLE."""
import os, re, time, requests, pandas as pd
tok = open(os.path.expanduser("~/.config/ads/token")).read().strip(); H = {"Authorization": "Bearer " + tok}
m = pd.read_csv("pceb_gated.csv", dtype={"GaiaDR3": str}); m["match"] = m.match.fillna("")
known_extra = {"2521231599018864000", "4551159586948613888", "794184674743537152"}
rows = []
for _, r in m[(m.match == "") & ~m.GaiaDR3.isin(known_extra)].iterrows():
    w = re.match(r"WDJ(\d{2})(\d{2})(\d{2}\.\d+)([+-])(\d{2})(\d{2})(\d{2}\.\d+)", r.WDJname)
    names = [r.WDJname, f"Gaia DR3 {r.GaiaDR3}"]
    if w:
        h, mi, s, sg, d, dm, ds = w.groups()
        names += [f"J{h}{mi}{sg}{d}{dm}", f"J{h}{mi}{s[:4]}{sg}{d}{dm}{ds[:2]}", f"J{h}{mi}{s[:2]}{sg}{d}{dm}{ds[:2]}"]
    sb = str(r.simbad)
    if sb and sb != "nan" and not sb.startswith("Gaia DR3"): names.append(sb)
    for q in names:
        try:
            j = requests.get("https://api.adsabs.harvard.edu/v1/search/query", params=dict(q=f'full:"{q}"', fl="bibcode,title,year", rows=15), headers=H, timeout=60).json()
            docs = j.get("response", {}).get("docs", [])
            if not docs: rows.append(dict(GaiaDR3=r.GaiaDR3, WDJname=r.WDJname, alias=q, bibcode="", year="", title="(no hits)"))
            for d in docs: rows.append(dict(GaiaDR3=r.GaiaDR3, WDJname=r.WDJname, alias=q, bibcode=d["bibcode"], year=d.get("year", ""), title=(d.get("title") or [""])[0][:120]))
        except Exception as ex:
            rows.append(dict(GaiaDR3=r.GaiaDR3, WDJname=r.WDJname, alias=q, bibcode="HOLE", year="", title=type(ex).__name__))
        time.sleep(0.3)
    print(r.GaiaDR3, r.WDJname, "queried", len(names), "aliases", flush=True)
pd.DataFrame(rows).to_csv("ads_hits.csv", index=False)
h = pd.DataFrame(rows); print("done;", h.GaiaDR3.nunique(), "objects;", (h.bibcode == "HOLE").sum(), "holes;", (h.bibcode.str.len() > 4).sum(), "hits")
