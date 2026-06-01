"""Registry of the catalogues that define "already known" for the discovery lanes.

This is the programmatic companion to CATALOG_DEPENDENCIES.md: it lists, per
science class, the public catalogues a hunt should crossmatch a candidate against
BEFORE spending vetting effort on it. ``build.py`` pulls these into the local
known-object store; ``store.py`` matches candidates against the cached result.

Each entry is deliberately small/curated (dedicated CV / accretor / runaway-WD
catalogues + the variable-star net), not "every catalogue in VizieR" — the point
is to catch the objects that previously slipped through to the back of the
pipeline (e.g. ASASSN-14gb, ATO J103.1497-07.9895, both catalogued dwarf novae
re-flagged as "new" because the v1 eRASS1 gate only hit a null-prone SIMBAD field).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CatalogSpec:
    key: str                      # short stable id, used on the CLI and as provenance tag
    name: str                     # human description
    classes: tuple[str, ...]      # which lanes this is relevant to: 'cv','accretor','wd','runaway','variable'
    source: str                   # 'vizier' or 'gaia_tap'
    ident: str                    # VizieR catalogue/table id, or a TAP table name
    note: str = ""
    # column-name hints (build.py falls back to heuristics if these are absent)
    ra_hints: tuple[str, ...] = ("_RAJ2000", "RAJ2000", "RA_ICRS", "RAdeg", "ra")
    dec_hints: tuple[str, ...] = ("_DEJ2000", "DEJ2000", "DE_ICRS", "DEdeg", "dec")
    name_hints: tuple[str, ...] = ("Name", "GCVS", "SDSS", "OName", "Object", "ID")
    type_hints: tuple[str, ...] = ("Type", "VarType", "Class", "SpType", "otype")
    sourceid_hints: tuple[str, ...] = ("GaiaDR3", "DR3Name", "Source", "GaiaEDR3", "gaia_source_id")
    # optional VizieR column_filters (e.g. restrict VSX to cataclysmic types)
    column_filters: dict = field(default_factory=dict)


# --- the curated crossmatch set -------------------------------------------------
# VizieR ids verified in use this session (Ritter-Kolb, Downes) or surfaced by the
# deep-vet dossiers (Rodriguez+2025 J/PASP/137/A4201, eROSITA-CV J/A+A/698/A321).
CATALOGS: list[CatalogSpec] = [
    CatalogSpec(
        key="ritter_kolb",
        name="Ritter & Kolb — Catalogue of CVs, LMXBs and related objects",
        classes=("cv", "accretor"),
        source="vizier", ident="B/cb",
        note="The standard hand-curated CV/LMXB catalogue (Ritter & Kolb 2003, final ed.).",
    ),
    CatalogSpec(
        key="downes_cv",
        name="Downes et al. — Catalog of Cataclysmic Variables (living edition)",
        classes=("cv", "accretor"),
        source="vizier", ident="V/123A",
        note="Downes+ 2001-2006; broad historical CV identifications.",
    ),
    CatalogSpec(
        key="rodriguez2025_erass1_cv",
        name="Rodriguez+ 2025 — CVs & AM CVn in eRASS1 x Gaia",
        classes=("cv", "accretor"),
        source="vizier", ident="J/PASP/137/A4201",
        note="The PUBLISHED version of the eRASS1xGaia CV selection — decisive for this lane.",
    ),
    CatalogSpec(
        key="erass1_cv_cat",
        name="eROSITA-DE DR1 cataclysmic-variable content",
        classes=("cv", "accretor"),
        source="vizier", ident="J/A+A/698/A321",
        note="eRASS1 CV catalogue (the X-ray-selected CV population).",
    ),
    CatalogSpec(
        key="vsx_cataclysmic",
        name="AAVSO VSX — cataclysmic / eruptive subset",
        classes=("cv", "accretor", "variable"),
        source="vizier", ident="B/vsx",
        note="VSX restricted to CV/nova/eruptive types; the broad known-variable net.",
        # VizieR free-text filter: VSX Type strings for cataclysmic + eruptive classes
        column_filters={"Type": "UG|UGSU|UGSS|UGZ|UGWZ|NL|NA|NB|NC|NR|N|DN|AM|DQ|IP|ZAND|CBSS|SXPHE|CV|VY|UGER"},
    ),
    CatalogSpec(
        key="gaia_dr3_vari_cv",
        name="Gaia DR3 variability classification — CV class",
        classes=("cv", "accretor", "variable"),
        source="gaia_tap",
        ident="gaiadr3.vari_classifier_result",
        note="best_class_name='CV'; Gaia's own CV identifications (source_id-keyed).",
    ),
    # --- runaway / partly-burnt / hypervelocity WD samples (small, published) ---
    CatalogSpec(
        key="raddi2019_lp40",
        name="Raddi+ 2019 — LP 40-365 class partly-burnt SN survivors",
        classes=("runaway", "wd"),
        source="vizier", ident="J/MNRAS/489/1489",
        note="Partly-burnt thermonuclear-SN survivors (O/Ne-dominated).",
    ),
]

def specs_for(classes: tuple[str, ...] | list[str] | None = None) -> list[CatalogSpec]:
    """Return the catalogue specs relevant to the given lane classes (all if None)."""
    if not classes:
        return list(CATALOGS)
    want = set(classes)
    return [c for c in CATALOGS if want & set(c.classes)]
