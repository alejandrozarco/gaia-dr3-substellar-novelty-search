"""Rich per-object dossier panels for the hunt console's Target Findings view.

Brings the console's object page closer to the single-source viewer (app.py):
identity + external links, known-object status (via the known_objects store),
an evidence metrics grid, an HR-diagram locus, an organised plot gallery, the
written dossier, cross-hunt appearances, and an optional *live* ZTF phase-fold
at a catalogued period ("where applicable / if possible").

Every panel is defensive: a missing field, an unreachable archive, or an absent
optional dependency degrades to a caption — it never raises into the UI.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# scripts/ on path so we can reuse the known-object store (scripts/known_objects)
_SCRIPTS = Path(__file__).resolve().parents[2]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))


# ---------------------------------------------------------------------------
# small value pluckers — findings has top-level keys + a freeform `evidence`
# dict; the candidate row (candidates.csv) carries lane extras. Try them all.
# ---------------------------------------------------------------------------
def pluck(findings: dict | None, crow: dict | None, *keys, contains: bool = False):
    """First non-empty value across findings (top + evidence) and crow, by key."""
    pools: list[dict] = []
    if findings:
        pools.append(findings)
        ev = findings.get("evidence")
        if isinstance(ev, dict):
            pools.append(ev)
    if crow:
        pools.append(crow)
    for pool in pools:
        if not isinstance(pool, dict):
            continue
        for k in keys:
            if not contains:
                if k in pool and pool[k] not in (None, "", []):
                    return pool[k]
            else:
                for pk, pv in pool.items():
                    if k.lower() in str(pk).lower() and pv not in (None, "", []):
                        return pv
    return None


def _num(v):
    try:
        f = float(v)
        if math.isnan(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def _coords(findings, crow):
    return _num(pluck(findings, crow, "ra", "RA", "ra_deg")), \
           _num(pluck(findings, crow, "dec", "DEC", "dec_deg"))


def source_id_of(tid, findings, crow):
    return str(pluck(findings, crow, "gaia_dr3_source_id", "source_id", "id") or tid)


# ---------------------------------------------------------------------------
# identity + external links
# ---------------------------------------------------------------------------
def external_links(source_id: str, ra: float | None, dec: float | None) -> str:
    """Per-source / per-position deep links (all verified to resolve, not homepages).

    ZTF *light curves* are available via the in-console live phase-fold panel, so we
    don't link the (non-existent) ZTF cutout page; the Gaia archive has no clean
    per-source web URL, so we link the per-source Gaia DR3 row at VizieR + ESA's
    own position viewer (ESASky) instead of the generic archive homepage.
    """
    sid = str(source_id) if source_id else ""
    links = []
    if sid.isdigit():
        links.append(f"[SIMBAD](https://simbad.cds.unistra.fr/simbad/sim-id?Ident=Gaia+DR3+{sid})")
        links.append(f"[Gaia DR3 row](https://vizier.cds.unistra.fr/viz-bin/VizieR-5?-source=I%2F355%2Fgaiadr3&Source={sid})")
    elif ra is not None and dec is not None:
        links.append(f"[SIMBAD](https://simbad.cds.unistra.fr/simbad/sim-coo?Coord={ra}+{dec}&Radius=5&Radius.unit=arcsec)")
    if ra is not None and dec is not None:
        links.append(f"[VizieR (all cats)](https://vizier.cds.unistra.fr/viz-bin/VizieR?-c={ra}+{dec}&-c.rs=5)")
        links.append(f"[ESASky](https://sky.esa.int/esasky/?target={ra}%20{dec}&fov=0.1&sci=true)")
        links.append(f"[Legacy Survey](https://www.legacysurvey.org/viewer?ra={ra}&dec={dec}&zoom=16&layer=ls-dr10)")
    return "  ·  ".join(links)


def identity_header(tid, crow, findings):
    sid = source_id_of(tid, findings, crow)
    ra, dec = _coords(findings, crow)
    names = (findings or {}).get("names") if findings else None
    primary = None
    if isinstance(names, dict) and names:
        # prefer a recognisable designation
        for k in ("simbad", "asassn", "vsx", "name", "gaia"):
            if names.get(k):
                primary = names[k]; break
        if primary is None:
            primary = next(iter(names.values()))
    title = primary or f"Gaia DR3 {sid}"
    st.markdown(f"## {title}")
    sub = [f"Gaia DR3 `{sid}`"]
    if ra is not None and dec is not None:
        sub.append(f"RA {ra:.5f}  Dec {dec:+.5f}")
    lane = (findings or {}).get("lane") or (crow or {}).get("lane")
    if lane:
        sub.append(f"lane **{lane}**")
    st.caption("  ·  ".join(sub))
    if isinstance(names, dict) and len(names) > 1:
        st.caption("aka " + ", ".join(f"{k}: {v}" for k, v in names.items() if v))
    if ra is not None and dec is not None:
        st.markdown(external_links(sid, ra, dec))


# ---------------------------------------------------------------------------
# known-object status (the front-filter, surfaced per object)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _known_store():
    try:
        from known_objects import KnownObjectStore
        s = KnownObjectStore()
        return s if len(s.df) else None
    except Exception:
        return None


def known_status_panel(tid, crow, findings):
    sid = source_id_of(tid, findings, crow)
    ra, dec = _coords(findings, crow)
    # 1) what the deep-vet itself recorded
    fk = (findings or {}).get("known_in_catalogs") if findings else None
    # 2) live lookup against the known-object store
    store_hits = []
    store = _known_store()
    if store is not None and ra is not None and dec is not None:
        try:
            store_hits = store.match(ra, dec, source_id=sid, radius_arcsec=3.0)
        except Exception:
            store_hits = []
    if fk or store_hits:
        cats = []
        if store_hits:
            for h in store_hits:
                tag = f"{h.get('catalog')}"
                if h.get("name"):
                    tag += f" ({h['name']})"
                cats.append(tag)
        msg = "**⚠️ Already catalogued** — this source matches the known-object store"
        if fk:
            msg += " / deep-vet record"
        st.warning(msg + ":\n\n" + "  ·  ".join(
            (list(fk) if isinstance(fk, list) else []) + cats), icon="📚")
    else:
        st.success("✓ Not found in the known-object store (CV/accretor catalogues). "
                   "Treat as uncatalogued pending a live SIMBAD/VizieR check.", icon="🔎")


# ---------------------------------------------------------------------------
# our own classification (the hunt's / deep-vet's inference) — the analogue of
# app.py's "Likely object type" panel, kept distinct from the *external* known
# status. Shown ONLY when there is an own-call to make.
# ---------------------------------------------------------------------------
def own_classification(findings: dict | None, crow: dict | None):
    """Extract the hunt's own classification, or None if there's nothing
    appropriate to assert (gates the panel). Looks at: the deep-vet's
    classification + subtype (+ optional confidence and a ranked likely-types
    list), and the pipeline verdict/score as the automated first-pass call."""
    f = findings or {}
    c = crow or {}
    cls = f.get("classification") or f.get("our_classification")
    verdict = c.get("verdict")
    if verdict in (None, "", "nan", "NaN", "none"):
        verdict = None
    ranked = None
    for key in ("likely_types", "classification_candidates", "object_type_spectrum", "alternatives"):
        v = f.get(key)
        if isinstance(v, list) and v:
            ranked = v
            break
    if not (cls or ranked or verdict):
        return None
    return {"classification": cls, "subtype": f.get("subtype"),
            "confidence": f.get("confidence"), "verdict": verdict,
            "score": c.get("score"), "ranked": ranked}


def our_classification_panel(findings, crow) -> bool:
    info = own_classification(findings, crow)
    if info is None:
        return False
    st.markdown("#### 🏷️ Our classification")
    if info["classification"]:
        line = f"**{info['classification']}**"
        if info["subtype"]:
            line += f"  —  {info['subtype']}"
        st.markdown(line)
    if info["confidence"]:
        st.caption(f"confidence: {info['confidence']}")
    if info["ranked"]:
        rows = []
        for item in info["ranked"]:
            if isinstance(item, dict):
                rows.append((str(item.get("label") or item.get("type") or "?"),
                             item.get("prob", item.get("probability", "")),
                             str(item.get("rationale") or item.get("reason") or "")))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                rows.append((str(item[0]), item[1], str(item[2]) if len(item) > 2 else ""))
        if rows:
            st.dataframe(pd.DataFrame(rows, columns=["type", "prob", "rationale"]),
                         hide_index=True, width="stretch")
    if info["verdict"]:
        cap = f"hunt pipeline verdict: **{info['verdict']}**"
        sc = _num(info["score"])
        if sc is not None:
            cap += f"  (score {sc:.2f})"
        st.caption(cap)
    return True


# ---------------------------------------------------------------------------
# evidence: metrics grid + key/value table (classification lives in its own panel)
# ---------------------------------------------------------------------------
# fields worth promoting to metric tiles, with label + format
_METRIC_FIELDS = [
    ("distance_pc", "Distance", "{:.0f} pc"),
    ("parallax_over_error", "ϖ S/N", "{:.1f}"),
    ("ruwe", "RUWE", "{:.2f}"),
    ("vtan_kms", "v_tan", "{:.0f} km/s"),
    ("Lx_erg_s_0p2_2p3keV", "L_X", "{:.2e}"),
    ("log_Fx_Fopt", "log Fx/Fopt", "{:.2f}"),
    ("M_G_quiescent", "M_G", "{:.2f}"),
    ("bp_rp_mean", "BP−RP", "{:.2f}"),
    ("gaia_G_amplitude_mag", "ΔG", "{:.2f} mag"),
    ("orbital_period_d", "P_orb", "{:.4f} d"),
    ("halpha_ew_espels_nm", "Hα EW", "{:.2f} nm"),
    ("galex_fuv", "GALEX FUV", "{:.2f}"),
    ("galex_nuv", "GALEX NUV", "{:.2f}"),
    ("score", "score", "{:.2f}"),
]


def evidence_panel(findings, crow):
    # (the classification line is rendered by our_classification_panel, above)
    # metric tiles for whichever known fields are present
    tiles = []
    for key, label, fmt in _METRIC_FIELDS:
        v = pluck(findings, crow, key)
        nv = _num(v)
        if nv is not None:
            try:
                tiles.append((label, fmt.format(nv)))
            except Exception:
                tiles.append((label, str(v)))
        elif v not in (None, "", []):
            tiles.append((label, str(v)))
    if tiles:
        cols = st.columns(min(4, len(tiles)))
        for i, (label, val) in enumerate(tiles):
            cols[i % len(cols)].metric(label, val)

    # full evidence dict as a tidy key/value table
    ev = (findings or {}).get("evidence") if findings else None
    if isinstance(ev, dict) and ev:
        with st.expander(f"All evidence ({len(ev)} fields)", expanded=False):
            rows = [(k, ("" if v is None else str(v))) for k, v in ev.items()]
            st.dataframe(pd.DataFrame(rows, columns=["field", "value"]),
                         width="stretch", hide_index=True)
    # legacy key_values schema (older findings)
    kv = (findings or {}).get("key_values") if findings else None
    if isinstance(kv, dict) and kv:
        st.dataframe(pd.DataFrame([(k, str(v)) for k, v in kv.items()],
                                  columns=["key", "value"]), width="stretch", hide_index=True)


# ---------------------------------------------------------------------------
# HR-diagram locus (matplotlib; from M_G + BP-RP, derived if needed)
# ---------------------------------------------------------------------------
def hr_diagram(crow, findings):
    bp_rp = _num(pluck(findings, crow, "bp_rp_mean", "bp_rp", "BP_RP"))
    mg = _num(pluck(findings, crow, "M_G_quiescent", "M_G", "abs_g", "absG"))
    if mg is None:
        g = _num(pluck(findings, crow, "phot_g_mean_mag", "G", "gmag", "gaia_G_median"))
        plx = _num(pluck(findings, crow, "parallax_mas", "parallax"))
        if g is not None and plx and plx > 0:
            mg = g + 5 * math.log10(plx) - 10
    if bp_rp is None or mg is None:
        return False
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return False
    fig, ax = plt.subplots(figsize=(4.2, 4.0))
    # schematic loci for orientation (no background sample needed)
    import numpy as np
    x = np.linspace(-0.5, 3.5, 50)
    ax.plot(x, 4.5 + 2.8 * x, color="0.7", lw=8, alpha=0.35, solid_capstyle="round",
            label="main sequence")
    ax.add_patch(plt.Rectangle((-0.6, 10), 1.6, 6, color="#6db3ff", alpha=0.18))
    ax.text(-0.5, 14.5, "white dwarfs", color="#1f6fd6", fontsize=7)
    ax.text(2.2, 2.0, "giants", color="0.5", fontsize=7)
    ax.text(0.55, 9.0, "CV gap /\nWD+MS", color="#b06", fontsize=6.5)
    ax.scatter([bp_rp], [mg], s=130, marker="*", color="#ff2b2b",
               edgecolor="k", zorder=5, label="this source")
    ax.annotate(f"  ({bp_rp:.2f}, {mg:.2f})", (bp_rp, mg), fontsize=7, va="center")
    ax.set_xlabel("BP − RP (mag)"); ax.set_ylabel("M_G (mag)")
    ax.set_xlim(-0.7, 3.6); ax.set_ylim(17, 0)   # mag axis inverted
    ax.legend(loc="upper right", fontsize=7, framealpha=0.6)
    ax.set_title("Gaia HR-diagram position", fontsize=9)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)
    return True


# ---------------------------------------------------------------------------
# plot gallery — organise the agent-generated PNGs by kind, with captions
# ---------------------------------------------------------------------------
def _kind(fname: str) -> str:
    f = fname.lower()
    if "phase" in f or "fold" in f:
        return "Phase fold"
    if "lightcurve" in f or "_lc" in f or "lcurve" in f:
        return "Light curve"
    if "sed" in f:
        return "SED"
    if "spectrum" in f or "spec" in f or "xp" in f:
        return "Spectrum"
    if "finder" in f or "cutout" in f or "image" in f:
        return "Finder"
    if "hr" in f or "kiel" in f:
        return "HR / Kiel"
    return "Other"


def plot_gallery(plots: list[str]):
    if not plots:
        return
    order = ["Phase fold", "Light curve", "Spectrum", "SED", "Finder", "HR / Kiel", "Other"]
    by_kind: dict[str, list[str]] = {}
    for p in plots:
        by_kind.setdefault(_kind(Path(p).name), []).append(p)
    st.subheader(f"Plots ({len(plots)})")
    for kind in order:
        items = by_kind.get(kind)
        if not items:
            continue
        st.markdown(f"**{kind}**")
        cols = st.columns(min(2, len(items)))
        for i, p in enumerate(items):
            cols[i % len(cols)].image(p, caption=Path(p).name, width="stretch")


# ---------------------------------------------------------------------------
# live ZTF phase-fold (opt-in; "where applicable / if possible")
# ---------------------------------------------------------------------------
def _period_days(findings, crow):
    p = _num(pluck(findings, crow, "orbital_period_d", "period_d", "P_d", "period_days"))
    if p:
        return p
    pmin = _num(pluck(findings, crow, "orbital_period_min", "period_min"))
    if pmin:
        return pmin / 1440.0
    return None


@st.cache_data(show_spinner="Fetching ZTF light curve (IRSA) …", ttl=3600)
def _fetch_ztf(ra: float, dec: float, radius_arcsec: float = 2.5):
    import io as _io
    import requests
    url = ("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves"
           f"?POS=CIRCLE%20{ra}%20{dec}%20{radius_arcsec/3600.0:.6f}"
           "&BAD_CATFLAGS_MASK=32768&FORMAT=CSV")
    r = requests.get(url, timeout=45)
    r.raise_for_status()
    df = pd.read_csv(_io.StringIO(r.text))
    return df


def live_phasefold_panel(crow, findings):
    ra, dec = _coords(findings, crow)
    P = _period_days(findings, crow)
    if ra is None or dec is None:
        return
    with st.expander("📈 Live ZTF light curve / phase-fold (IRSA, on demand)",
                     expanded=False):
        if P:
            st.caption(f"Catalogued period P = {P:.5f} d ({P*1440:.1f} min) — folds at this P.")
        else:
            st.caption("No catalogued period in findings — will show the raw light curve only.")
        if not st.button("Fetch ZTF light curve", key="ztf_fetch"):
            return
        try:
            df = _fetch_ztf(ra, dec)
        except Exception as e:
            st.error(f"ZTF fetch failed: {type(e).__name__}: {str(e)[:120]}")
            return
        if df is None or len(df) == 0 or "mjd" not in {c.lower() for c in df.columns}:
            st.info("No ZTF epochs returned for this position (outside ZTF footprint, or none pass quality cuts).")
            return
        df.columns = [c.lower() for c in df.columns]
        band_col = "filtercode" if "filtercode" in df.columns else None
        colors = {"zg": "#2ca02c", "zr": "#d62728", "zi": "#7f3f00"}
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import numpy as np
        except Exception:
            st.info("matplotlib unavailable.")
            return
        st.caption(f"{len(df)} ZTF epochs.")
        # raw light curve
        fig1, ax1 = plt.subplots(figsize=(6, 2.6))
        for band, sub in (df.groupby(band_col) if band_col else [("ztf", df)]):
            ax1.errorbar(sub["mjd"], sub["mag"], yerr=sub.get("magerr"),
                         fmt=".", ms=3, lw=0.5, color=colors.get(str(band), "k"), label=str(band))
        ax1.invert_yaxis(); ax1.set_xlabel("MJD"); ax1.set_ylabel("mag")
        ax1.legend(fontsize=7); ax1.set_title("ZTF light curve", fontsize=9)
        fig1.tight_layout(); st.pyplot(fig1, clear_figure=True)
        # phase fold
        if P:
            t0 = float(df["mjd"].min())
            fig2, ax2 = plt.subplots(figsize=(6, 2.8))
            for band, sub in (df.groupby(band_col) if band_col else [("ztf", df)]):
                ph = ((sub["mjd"] - t0) % P) / P
                for off in (0, 1):   # two cycles
                    ax2.errorbar(ph + off, sub["mag"], yerr=sub.get("magerr"),
                                 fmt=".", ms=3, lw=0.4, alpha=0.7,
                                 color=colors.get(str(band), "k"),
                                 label=str(band) if off == 0 else None)
            ax2.invert_yaxis(); ax2.set_xlabel("phase (P = %.5f d)" % P); ax2.set_ylabel("mag")
            ax2.legend(fontsize=7); ax2.set_title("ZTF phase-fold", fontsize=9)
            fig2.tight_layout(); st.pyplot(fig2, clear_figure=True)
            st.caption("Folded at the *catalogued* period (not re-fit here) — a coherent fold "
                       "corroborates the period; scatter does not refute it (ZTF cadence/aliasing).")


# ---------------------------------------------------------------------------
# written dossier (.md) + cross-hunt appearances
# ---------------------------------------------------------------------------
def dossier_md_panel(tid, findings, crow):
    sid = source_id_of(tid, findings, crow)
    candidates = [Path(f"/tmp/dossier_{sid}_2026_06_01.md"),
                  Path(f"/tmp/dossier_{sid}.md")]
    for d in sorted(Path("/tmp").glob(f"dossier_{sid}_*.md")):
        candidates.append(d)
    seen = set()
    for path in candidates:
        if path in seen or not path.exists():
            continue
        seen.add(path)
        try:
            text = path.read_text()
        except Exception:
            continue
        with st.expander(f"📄 Full dossier — {path.name}", expanded=False):
            st.markdown(text)
        return True
    return False


def cross_hunt_panel(tid, findings, crow, hd):
    sid = source_id_of(tid, findings, crow)
    try:
        hits = hd.cross_hunt_search(sid)
    except Exception:
        return
    others = [(h, row) for h, row in hits]
    if len(others) > 1:
        with st.expander(f"🔗 This source appears in {len(others)} hunts", expanded=False):
            for h, row in others:
                st.markdown(f"- **{h}** — verdict `{row.get('verdict','')}`"
                            + (f", triage `{row['_triage']}`" if row.get("_triage") else ""))
