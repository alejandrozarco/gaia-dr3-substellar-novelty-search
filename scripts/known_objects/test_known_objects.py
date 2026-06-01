"""Self-contained tests for the known-object store/filter (no network, no files).

    PYTHONPATH=scripts/known_objects python scripts/known_objects/test_known_objects.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from store import KnownObjectStore  # noqa: E402

N_PASS = N_FAIL = 0


def check(label, cond, extra=""):
    global N_PASS, N_FAIL
    if cond:
        N_PASS += 1; print(f"[PASS] {label}")
    else:
        N_FAIL += 1; print(f"[FAIL] {label} {extra}")


# A synthetic store: a known CV (with Gaia id) + a known WD (no id, positional only)
store_df = pd.DataFrame([
    {"source_id": "6048007439673413760", "ra": 250.55517, "dec": -23.22049,
     "name": "ASASSN-14gb", "otype": "CV:UGSU", "catalog": "session_deflated", "pulled_utc": "x"},
    {"source_id": pd.NA, "ra": 10.00000, "dec": 41.00000,
     "name": "SomeKnownVar", "otype": "NL", "catalog": "vsx_cataclysmic", "pulled_utc": "x"},
])
store = KnownObjectStore(df=store_df)

# candidates: [0] exact-id match, [1] positional match (2" off), [2] clean/new,
#             [3] positional but high-PM so id matches though 30" away
cand = pd.DataFrame([
    {"id": "9999999999999999999", "ra": 250.55517, "dec": -23.22049},   # same pos as ASASSN (cone)
    {"id": "1111111111111111111", "ra": 10.0005, "dec": 41.0000},        # ~1.4" from SomeKnownVar
    {"id": "2222222222222222222", "ra": 200.0, "dec": 5.0},              # nothing nearby -> new
    {"id": "6048007439673413760", "ra": 250.56,  "dec": -23.23},         # id match, ~36" away (PM)
])
ann = store.annotate(cand, ra_col="ra", dec_col="dec", id_col="id", radius_arcsec=3.0)

check("cone match flags the co-located source known", bool(ann.loc[0, "known"]))
check("cone match records the catalogue", ann.loc[0, "known_catalogs"] == "session_deflated")
check("positional match within 3\" flagged", bool(ann.loc[1, "known"]))
check("positional match names the VSX object", ann.loc[1, "known_name"] == "SomeKnownVar")
check("clean source is NOT flagged known", not bool(ann.loc[2, "known"]))
check("clean source has empty catalogues", ann.loc[2, "known_catalogs"] == "")
check("exact Gaia source_id match catches a high-PM star a cone misses",
      bool(ann.loc[3, "known"]) and "session_deflated" in ann.loc[3, "known_catalogs"])

# match() single-object API
m = store.match(250.55517, -23.22049, source_id="6048007439673413760")
check("match() returns the ASASSN row", any(r["name"] == "ASASSN-14gb" for r in m))
m2 = store.match(123.0, 45.0)
check("match() empty for a clean position", len(m2) == 0)

# append dedupes
n1 = store.append(pd.DataFrame([{"source_id": "6048007439673413760", "ra": 250.55517,
                                 "dec": -23.22049, "name": "ASASSN-14gb", "otype": "CV",
                                 "catalog": "session_deflated"}]))
check("append of an identical row dedupes to 0 added", n1 == 0)
n2 = store.append(pd.DataFrame([{"source_id": pd.NA, "ra": 300.0, "dec": -10.0,
                                 "name": "New", "otype": "CV", "catalog": "ritter_kolb"}]))
check("append of a genuinely new row adds 1", n2 == 1)

# empty store is safe
empty = KnownObjectStore(df=pd.DataFrame(columns=["source_id", "ra", "dec", "name", "otype", "catalog", "pulled_utc"]))
ann_e = empty.annotate(cand)
check("annotate against an empty store flags nothing / no crash", not ann_e["known"].any())

print(f"\n{'='*48}\n{N_PASS} passed, {N_FAIL} failed\n{'='*48}")
sys.exit(1 if N_FAIL else 0)
