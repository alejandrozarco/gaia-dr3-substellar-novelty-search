# Minimal ADS search helper: python ads.py '<query>' [rows]. Token read from ~/.config/ads/token (never printed).
import sys, os, requests, json
tok = open(os.path.expanduser("~/.config/ads/token")).read().strip()
def search(q, rows=30, fl="bibcode,title,year,first_author"):
    r = requests.get("https://api.adsabs.harvard.edu/v1/search/query", params=dict(q=q, rows=rows, fl=fl, sort="date desc"),
                     headers={"Authorization": "Bearer " + tok}, timeout=60)
    if r.status_code != 200: return None, r.status_code
    d = r.json()["response"]; return d["docs"], d["numFound"]
if __name__ == "__main__":
    docs, n = search(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 30)
    if docs is None: print("HOLE: HTTP", n); sys.exit(2)
    print("numFound", n)
    for d in docs: print(f"  {d['bibcode']}  {d.get('first_author','')[:25]:25s}  {d.get('title',[''])[0][:130]}")
