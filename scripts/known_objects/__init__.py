"""Known-object store + front-of-pipeline crossmatch filter.

Catch already-catalogued sources at the FRONT of a hunt (before vetting), not the
back. See README.md. Typical use in a hunt::

    from known_objects import KnownObjectStore
    store = KnownObjectStore()                      # loads the cached parquet
    cand = store.annotate(cand, ra_col="ra", dec_col="dec", id_col="id")
    fresh = cand[~cand["known"]]                    # vet only these
"""
from .store import KnownObjectStore, default_store_path, STORE_COLUMNS
from .reference_catalogs import CATALOGS, CatalogSpec, specs_for

__all__ = ["KnownObjectStore", "default_store_path", "STORE_COLUMNS",
           "CATALOGS", "CatalogSpec", "specs_for"]
