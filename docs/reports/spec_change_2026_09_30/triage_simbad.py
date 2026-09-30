"""SIMBAD main type, other types and reference count for every star with a pair score > 8 (2026-09-30).
Lookup by the identifier 'Gaia DR3 <id>' (TAP ident join). A star without a SIMBAD Gaia DR3 identifier is re-queried by a 3-arcsec
cone at its SDSS/DESI position. A failed TAP call is recorded as HOLE. Output: results/simbad_top.csv."""
import os, requests, numpy as np, pandas as pd, io, time
H = os.path.dirname(os.path.abspath(__file__)); ST = os.path.expanduser("~/claude_projects/spectra_store")
TAP = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync"
def tap(q):
    for k in range(3):
        try:
            r = requests.post(TAP, data=dict(request="doQuery", lang="adql", format="csv", query=q), timeout=120)
            if r.ok: return pd.read_csv(io.StringIO(r.text))
        except Exception: pass
        time.sleep(10)
    return None
P = pd.read_csv(os.path.join(H, "results", "pairs.csv"), dtype={"gaia": str}); G = P[P.score > 8].drop_duplicates("gaia")
ids = list(G.gaia); out = []
for k in range(0, len(ids), 80):
    lst = ",".join(f"'Gaia DR3 {g}'" for g in ids[k:k + 80])
    d = tap(f"SELECT i.id, b.main_id, b.otype, b.nbref, b.ra, b.dec, b.otypes FROM ident i JOIN basic b ON i.oidref=b.oid WHERE i.id IN ({lst})")
    if d is None:
        d = tap(f"SELECT i.id, b.main_id, b.otype, b.nbref, b.ra, b.dec FROM ident i JOIN basic b ON i.oidref=b.oid WHERE i.id IN ({lst})")
    if d is None: out += [dict(gaia=g, simbad="HOLE") for g in ids[k:k + 80]]; continue
    got = {r.id.replace("Gaia DR3 ", ""): r for r in d.itertuples()}
    for g in ids[k:k + 80]:
        r = got.get(g); out.append(dict(gaia=g, simbad="found" if r is not None else "no Gaia DR3 id", main_id=getattr(r, "main_id", ""), otype=getattr(r, "otype", ""), nbref=getattr(r, "nbref", np.nan), otypes=getattr(r, "otypes", "")))
S = pd.DataFrame(out)
M = pd.read_csv(os.path.join(ST, "sdss_dr17_wd", "matches.csv"), dtype={"gaia": str}).drop_duplicates("gaia").set_index("gaia")
C = pd.read_csv(os.path.join(ST, "desi_dr1_wd", "class_table.csv"), dtype={"edr3id": str}).drop_duplicates("edr3id").set_index("edr3id")
for i, r in S[S.simbad == "no Gaia DR3 id"].iterrows():
    ra, de = (M.loc[r.gaia, "ra"], M.loc[r.gaia, "dec"]) if r.gaia in M.index else (C.loc[r.gaia, "RA(deg)"], C.loc[r.gaia, "DEC(deg)"])
    d = tap(f"SELECT main_id, otype, nbref FROM basic WHERE CONTAINS(POINT('ICRS',ra,dec), CIRCLE('ICRS',{ra},{de},0.000833))=1")
    if d is None: S.loc[i, "simbad"] = "HOLE (cone)"
    elif len(d): S.loc[i, ["simbad", "main_id", "otype", "nbref"]] = ["cone 3 arcsec", d.main_id[0], d.otype[0], d.nbref[0]]
    else: S.loc[i, "simbad"] = "none (id and cone)"
S = G[["gaia", "score", "cls", "win_lo", "sign", "a", "b"]].merge(S, on="gaia"); S.to_csv(os.path.join(H, "results", "simbad_top.csv"), index=False)
print(S.simbad.value_counts()); print(S.otype.value_counts().head(25))
