import json, re, io, os, sys, requests, pandas as pd
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
from astropy.coordinates import SkyCoord
W = os.path.dirname(os.path.abspath(__file__))
L = [(n, sp, ra, de) for n, sp, ra, de, g in json.load(open(f"{W}/lit/uhe2021.json"))]
t2 = open(f"{W}/lit/2307.03721/BrightBlue.tex").read().replace("$-$", "-").replace("$+$", "+").replace("$", "")
for s in sorted(set(re.findall(r"WDJ\d{6}\.\d{2}[+-]\d{6}\.\d{2}", t2))):
    h, mi, se, sg, dd, dm, ds = re.match(r"WDJ(\d\d)(\d\d)(\d\d\.\d\d)([+-])(\d\d)(\d\d)(\d\d\.\d\d)", s).groups()
    c = SkyCoord(f"{h}h{mi}m{se}s {sg}{dd}d{dm}m{ds}s"); L.append((s, "Reindl+2023 sample", c.ra.deg, c.dec.deg))
print(len(L), "objects")
rows = []
for n, sp, ra, de in L:
    q = f"SELECT TOP 1 source_id, DISTANCE(POINT({ra},{de}), POINT(ra,dec))*3600 AS sep FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT(ra,dec), CIRCLE({ra},{de},0.0014)) ORDER BY sep"
    r = requests.post("https://gea.esac.esa.int/tap-server/tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=120)
    x = pd.read_csv(io.StringIO(r.text), dtype={"source_id": str})
    rows.append(dict(name=n, sp=sp, ra=ra, dec=de, gaia=x.source_id.iloc[0] if len(x) else None))
R = pd.DataFrame(rows); R.to_csv(f"{W}/uhe_known_gaia.csv", index=False)
sw = sdssv.snowwhite([g for g in R.gaia if g]); print(sw if not hasattr(sw, "to_string") else sw.to_string())
