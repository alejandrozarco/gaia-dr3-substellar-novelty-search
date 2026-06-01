"""hunt_console.py — multi-hunt discovery console (Streamlit, thin layer).

A companion to scripts/web_tool/app.py.  Where app.py is a *single-source* deep
dive onto one Gaia DR3 object, this console operates one level up: it monitors,
browses, and triages the *output of whole hunts* (archival-discovery runs that
each scan thousands of sources and emit a ranked candidate list).

All disk I/O lives in ``hunt_data.py`` (pure python, no streamlit) — this file is
purely the view layer.  Conventions (cache_data with ttl, graceful degradation
on missing data, st.* widgets) mirror app.py.

Run:
    HUNT_RUNS_DIR=/tmp/hunt_runs streamlit run hunt_console.py

Six views (sidebar nav):
    1. Dashboard (LIVE)   — per-run progress cards + heartbeat/stale monitor
    2. Target Browser     — candidates.csv table with filters + row selection
    3. Target Findings    — findings.json + plots for the selected id + triage
    4. Sky map            — Aladin Lite v3 of the hunt's candidates (matplotlib fallback)
    5. Triage             — promote/flag/reject (lives on the Findings view)
    6. Cross-hunt search  — find a source id across every hunt
"""
from __future__ import annotations

import io
import time
from pathlib import Path

import pandas as pd
import streamlit as st

import hunt_data as hd
import object_panels as op

# ---------------------------------------------------------------------------
# Optional auto-refresh dependency.  streamlit_autorefresh is the nicest option;
# if it isn't installed we fall back to st.fragment(run_every=...) (Streamlit
# >=1.33), and failing that to a manual Refresh button.  Probed once at import.
# ---------------------------------------------------------------------------
try:
    from streamlit_autorefresh import st_autorefresh  # type: ignore
    _HAS_AUTOREFRESH = True
except Exception:  # noqa: BLE001
    st_autorefresh = None
    _HAS_AUTOREFRESH = False

_HAS_FRAGMENT = hasattr(st, "fragment")

REFRESH_SECONDS = 15

st.set_page_config(page_title="Hunt Console", page_icon="🔭", layout="wide")


# ---------------------------------------------------------------------------
# Cached reads (ttl small so live runs stay fresh; the data layer is cheap).
# Caching here — not in hunt_data — keeps the data layer streamlit-free.
# ---------------------------------------------------------------------------
@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def _runs() -> list[str]:
    return hd.list_runs()


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def _manifest(hid: str) -> dict:
    return hd.read_manifest(hid)


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def _progress(hid: str) -> dict | None:
    return hd.read_progress(hid)


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def _candidates_cached(hid: str) -> pd.DataFrame:
    return hd.read_candidates(hid)


def _candidates(hid: str) -> pd.DataFrame:
    # Never trust a *cached empty*: a live run flips empty->populated mid-session
    # and the ttl cache would otherwise pin a stale "no candidates" view until the
    # next interaction (the Perseus "0 in browser, 4 on disk" bug). A non-empty
    # read stays cached — fast and live-fresh within the ttl.
    df = _candidates_cached(hid)
    if df is None or df.empty:
        df = hd.read_candidates(hid)
    return df


# findings/plots change rarely; still ttl so an edited findings.json appears.
@st.cache_data(ttl=30, show_spinner=False)
def _findings(hid: str, tid: str) -> dict | None:
    return hd.read_findings(hid, tid)


@st.cache_data(ttl=30, show_spinner=False)
def _plots(hid: str, tid: str) -> list[str]:
    return hd.list_target_plots(hid, tid)


def _clear_caches() -> None:
    for fn in (_runs, _manifest, _progress, _candidates_cached, _findings, _plots):
        fn.clear()


def _fmt_runtime(started: str | None, ended: str | None) -> str:
    """Human runtime from ISO timestamps; '?' if unparseable."""
    def _parse(s):
        if not s:
            return None
        try:
            return pd.Timestamp(s).to_pydatetime().timestamp()
        except Exception:  # noqa: BLE001
            return None
    s = _parse(started)
    e = _parse(ended) or time.time()
    if s is None:
        return "?"
    secs = max(0, int(e - s))
    h, rem = divmod(secs, 3600)
    m, s2 = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m"
    if m:
        return f"{m}m{s2:02d}s"
    return f"{s2}s"


# ---------------------------------------------------------------------------
# View 1 — Dashboard (LIVE)
# ---------------------------------------------------------------------------

def _render_run_card(hid: str) -> None:
    """One card per run: status, progress bar, survivors, runtime, heartbeat."""
    man = _manifest(hid)
    prog = _progress(hid)
    status = man.get("status", "unknown")
    health = hd.run_health(man, prog)

    icon = {"live": "🟢", "starting": "🟢", "quiet": "🟡", "stale": "🔴",
            "done": "✅", "failed": "❌"}.get(health, "❔")
    with st.container(border=True):
        top = st.columns([6, 2, 2])
        top[0].markdown(f"### {icon} {man.get('title', hid)}")
        top[0].caption(f"`{hid}`  ·  lane: **{man.get('lane','?')}**")
        top[1].metric("Status", status.upper())
        top[2].metric("Runtime", _fmt_runtime(man.get("started_at"), man.get("ended_at")))

        # progress bar
        processed = (prog or {}).get("processed")
        total = (prog or {}).get("total") or man.get("total_planned")
        if isinstance(processed, (int, float)) and isinstance(total, (int, float)) and total:
            frac = max(0.0, min(1.0, processed / total))
            st.progress(frac, text=f"processed {int(processed):,} / {int(total):,}  ({frac*100:.0f}%)")
        elif total:
            st.progress(0.0, text=f"0 / {int(total):,}")
        else:
            st.caption("no progress data yet")

        cols = st.columns(4)
        survivors = (prog or {}).get("survivors")
        cols[0].metric("Survivors", survivors if survivors is not None else "—")
        cols[1].metric("Stage", (prog or {}).get("stage", "—"))

        # heartbeat freshness
        age = hd.heartbeat_age_s(prog)
        if age is None:
            cols[2].metric("Heartbeat", "none")
        else:
            cols[2].metric("Heartbeat", f"{int(age)} s ago")
        tcounts = hd.triage_counts(hid)
        cols[3].metric("Triaged", sum(tcounts.values()) if tcounts else 0)

        if health == "stale":
            st.warning(
                f"⚠️ STALE: status='running' but the last heartbeat was "
                f"{int(age) if age is not None else '∞'} s ago "
                f"(> {hd.STALE_HEARTBEAT_S}s). The worker may have died.",
                icon="⚠️",
            )
        elif health == "quiet":
            st.info(
                f"⏳ Working: quiet for {int(age) if age is not None else '?'} s — "
                "almost always mid long query (NEOWISE / Gaia archive), not a dead "
                f"worker. Flagged STALE only after {hd.STALE_HEARTBEAT_S}s of silence.",
                icon="⏳",
            )
        msg = (prog or {}).get("message")
        if msg:
            st.caption(f"💬 {msg}")
        if man.get("headline"):
            st.info(man["headline"], icon="📋")


def view_dashboard() -> None:
    st.header("🔭 Hunt Dashboard")
    st.caption(f"Runs directory: `{hd.runs_dir()}`")

    # --- auto-refresh controls (degrade gracefully) -----------------------
    ctrl = st.columns([1, 1, 4])
    live = ctrl[0].toggle("🔴 Live", value=False,
                          help=f"Auto-refresh every {REFRESH_SECONDS}s")
    if ctrl[1].button("🔄 Refresh", width="stretch"):
        _clear_caches()
        st.rerun()

    if live:
        _clear_caches()  # bypass the ttl cache so a live tick is truly fresh
        if _HAS_AUTOREFRESH:
            st_autorefresh(interval=REFRESH_SECONDS * 1000, key="dash_autorefresh")
            ctrl[2].caption("Auto-refresh via streamlit_autorefresh.")
        elif _HAS_FRAGMENT:
            ctrl[2].caption("Auto-refresh via st.fragment(run_every).")
            _dashboard_cards_fragment()
            return
        else:
            ctrl[2].caption("⚠️ No auto-refresh backend; use the Refresh button.")
    else:
        ctrl[2].caption("Live off — showing a cached snapshot (TTL "
                        f"{REFRESH_SECONDS}s). Toggle Live or hit Refresh.")

    _dashboard_cards()


def _dashboard_cards() -> None:
    runs = _runs()
    if not runs:
        st.info("No runs found yet. Point HUNT_RUNS_DIR at your runs directory, "
                "or run `python ingest_run.py` to populate the demo.")
        return
    # running first, then everything else
    running = [h for h in runs if _manifest(h).get("status") == "running"]
    other = [h for h in runs if h not in running]
    if running:
        st.subheader(f"In progress ({len(running)})")
        for hid in running:
            _render_run_card(hid)
    if other:
        st.subheader(f"Completed / other ({len(other)})")
        for hid in other:
            _render_run_card(hid)


if _HAS_FRAGMENT:
    @st.fragment(run_every=REFRESH_SECONDS)
    def _dashboard_cards_fragment() -> None:
        # the fragment reruns in isolation every REFRESH_SECONDS; clear caches
        # so each tick re-reads the (possibly mid-write) progress files.
        _clear_caches()
        st.caption(f"⏱️ live tick @ {time.strftime('%H:%M:%S')}")
        _dashboard_cards()


# ---------------------------------------------------------------------------
# Shared: run picker
# ---------------------------------------------------------------------------

def _pick_run(key: str) -> str | None:
    runs = _runs()
    if not runs:
        st.info("No runs available. Run `python ingest_run.py` to populate the demo.")
        return None
    labels = {h: f"{_manifest(h).get('title', h)}  ({h})" for h in runs}
    chosen = st.selectbox("Hunt", runs, format_func=lambda h: labels[h], key=key)
    return chosen


# ---------------------------------------------------------------------------
# View 2 — Target Browser
# ---------------------------------------------------------------------------

def view_browser() -> None:
    st.header("📋 Target Browser")
    hid = _pick_run("browser_run")
    if not hid:
        return
    df = _candidates(hid)
    if df.empty:
        st.warning("This run has no readable candidates.csv yet.")
        return

    # join the current triage verdict onto the table
    triage = hd.read_triage(hid)
    df = df.copy()
    df["triage"] = df["id"].map(lambda i: (triage.get(i, {}) or {}).get("verdict", ""))

    # --- filters ----------------------------------------------------------
    with st.expander("Filters", expanded=True):
        fcols = st.columns([2, 3])
        smin, smax = float(df["score"].min(skipna=True) or 0), float(df["score"].max(skipna=True) or 1)
        if smin == smax:
            smax = smin + 1e-6
        lo, hi = fcols[0].slider("Score range", smin, smax, (smin, smax))
        verdicts = sorted(v for v in df["verdict"].dropna().unique() if v != "")
        chosen_v = fcols[1].multiselect("Verdict", verdicts, default=verdicts)
        only_triaged = st.checkbox("Only show triaged rows", value=False)

    mask = df["score"].between(lo, hi) | df["score"].isna()
    if chosen_v:
        mask &= df["verdict"].isin(chosen_v)
    if only_triaged:
        mask &= df["triage"] != ""
    fdf = df[mask].reset_index(drop=True)

    st.caption(f"{len(fdf)} / {len(df)} candidates shown. "
               "**Click any row to open its dossier** in Target Findings.")

    have_findings = set(hd.list_targets_with_findings(hid))
    fdf = fdf.copy()
    fdf.insert(0, "📊", fdf["id"].map(lambda i: "📊" if i in have_findings else ""))

    # column ordering: put the contract cols + helpers first
    lead = ["📊", "id", "score", "verdict", "triage", "ra", "dec"]
    cols = [c for c in lead if c in fdf.columns] + [c for c in fdf.columns if c not in lead]

    event = st.dataframe(
        fdf[cols],
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "📊": st.column_config.TextColumn("📊", help="has findings/plots", width="small"),
            "score": st.column_config.NumberColumn("score", format="%.3f"),
            "ra": st.column_config.NumberColumn("ra", format="%.5f"),
            "dec": st.column_config.NumberColumn("dec", format="%.5f"),
        },
        height=460,
        key="browser_table",
    )

    sel = event.get("selection", {}).get("rows", []) if hasattr(event, "get") else []
    if sel:
        chosen_id = str(fdf.iloc[sel[0]]["id"])
        st.session_state["selected_hunt"] = hid
        st.session_state["selected_id"] = chosen_id
        # Click-through: a NEW row selection opens that object's dossier directly in
        # Target Findings. Guard on the last-opened (hunt, id) so that returning to
        # the Browser — where the clicked row stays highlighted — doesn't bounce
        # straight back out; clicking a *different* row still navigates.
        if st.session_state.get("_browser_opened") != [hid, chosen_id]:
            st.session_state["_browser_opened"] = [hid, chosen_id]
            st.session_state["_pending_target"] = {"hunt": hid, "id": chosen_id}
            st.session_state["_pending_nav"] = "Target Findings"
            st.rerun()
        # Already the open row — offer an explicit re-open (also covers Streamlit's
        # deselect-on-reclick quirk for single-row dataframes).
        st.caption(f"**{chosen_id}** is open in Target Findings.")
        if st.button(f"➡️ Re-open {chosen_id}", type="primary"):
            st.session_state["_pending_target"] = {"hunt": hid, "id": chosen_id}
            st.session_state["_pending_nav"] = "Target Findings"
            st.rerun()


# ---------------------------------------------------------------------------
# View 3 — Target Findings  (+ View 5 Triage lives here)
# ---------------------------------------------------------------------------

# Per-lane renderer hook: lane -> callable(findings, candidate_row) -> None.
# Add a lane-specific layout by registering it here; otherwise the generic
# renderer below is used.
def _render_ir_nova(findings: dict, crow: dict | None) -> None:
    kv = findings.get("key_values", {})
    cols = st.columns(4)
    cols[0].metric("W2 (Vega)", _num(kv.get("W2_mag")))
    cols[1].metric("W1 − W2", _num(kv.get("W1_minus_W2")))
    cols[2].metric("W1 rise σ", _num(kv.get("W1_rise_significance_sigma")))
    cols[3].metric("NEOWISE epochs", _num(kv.get("neowise_n_epochs"), fmt="{:.0f}"))
    c2 = st.columns(3)
    c2[0].metric("DASCH plates", _num(kv.get("dasch_plates"), fmt="{:.0f}"))
    c2[1].metric("POSS-I SNR", _num(kv.get("poss1_snr")))
    c2[2].metric("POSS-II SNR", _num(kv.get("poss2_snr")))
    if kv.get("simbad_id"):
        st.caption(f"SIMBAD: **{kv['simbad_id']}** ({kv.get('simbad_otype','?')})")
    else:
        st.caption("SIMBAD: no counterpart — optical blank stands.")


LANE_RENDERERS = {
    "ir_nova": _render_ir_nova,
}


def _num(v, fmt: str = "{:.3f}") -> str:
    try:
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return "—"
        return fmt.format(float(v))
    except (TypeError, ValueError):
        return str(v)


def _render_generic_findings(findings: dict, crow: dict | None) -> None:
    # the rich renderer (classification banner + metric tiles + evidence table)
    # handles the deep-vet schema (names / evidence / known_in_catalogs) as well
    # as the legacy key_values shape.
    op.evidence_panel(findings, crow)


def view_findings() -> None:
    st.header("🎯 Target Findings")

    # run + id selection (defaulting to whatever the Browser selected)
    runs = _runs()
    if not runs:
        st.info("No runs available.")
        return
    # Apply a pending selection from the Browser / Cross-hunt search. Widget
    # KEYS must be set *before* the selectboxes are instantiated — Streamlit
    # ignores index= once a keyed widget has a stored value (the bug that made
    # Findings always show the same target).
    pend = st.session_state.pop("_pending_target", None)
    if pend and pend.get("hunt") in runs:
        st.session_state["findings_run"] = pend["hunt"]
        if pend.get("id") is not None:
            st.session_state["_pending_findings_id"] = str(pend["id"])
    if st.session_state.get("findings_run") not in runs:
        st.session_state["findings_run"] = runs[0]
    hid = st.selectbox("Hunt", runs,
                       format_func=lambda h: f"{_manifest(h).get('title', h)} ({h})",
                       key="findings_run")

    # every candidate is inspectable; list the ones with a findings dir first
    ids_with = [str(i) for i in hd.list_targets_with_findings(hid)]
    all_ids = [str(i) for i in _candidates(hid)["id"].tolist()]
    seen = set(ids_with)
    id_options = ids_with + [i for i in all_ids if i not in seen]
    if not id_options:
        st.warning("No targets to inspect in this run.")
        return
    pend_id = st.session_state.pop("_pending_findings_id", None)
    if pend_id is not None and pend_id in id_options:
        st.session_state["findings_id"] = pend_id
    if st.session_state.get("findings_id") not in id_options:
        st.session_state["findings_id"] = id_options[0]
    tid = st.selectbox("Target id", id_options, key="findings_id")
    if ids_with and tid not in ids_with:
        st.caption("(no findings dir for this id — showing candidate row only)")

    st.session_state["selected_hunt"] = hid
    st.session_state["selected_id"] = tid

    crow = hd.candidate_row(hid, tid)
    findings = _findings(hid, tid)
    man = _manifest(hid)

    # --- triage bar (View 5) ----------------------------------------------
    _render_triage_bar(hid, tid)
    st.divider()

    if findings is None and crow is None:
        st.warning(f"No findings.json and no candidate row for `{tid}`.")
        return

    # --- 1) identity + external links -------------------------------------
    op.identity_header(tid, crow, findings)
    # --- 2) OUR classification (the hunt's own inference) — only when apt ---
    op.our_classification_panel(findings, crow)
    # --- 3) already-catalogued? (the known-object front-filter, per object) -
    op.known_status_panel(tid, crow, findings)
    st.divider()

    # --- 4) evidence metric tiles + full evidence table + lane-specific extra
    if findings:
        op.evidence_panel(findings, crow)
        lane = findings.get("lane") or man.get("lane")
        extra = LANE_RENDERERS.get(lane)
        if extra is not None and extra is not _render_generic_findings:
            extra(findings, crow)
        if findings.get("flags"):
            st.write("**Flags:** " + "  ".join(f"`{f}`" for f in findings["flags"]))
        if findings.get("notes"):
            st.markdown(f"> {findings['notes']}")
    else:
        st.info("No findings.json for this target — showing HR position + candidate row below.")

    # --- 4) HR-diagram locus ----------------------------------------------
    op.hr_diagram(crow, findings)

    # --- 5) plot gallery (organised: phase-fold / LC / spectrum / SED / finder)
    plots = _plots(hid, tid)
    op.plot_gallery(plots)
    if not plots and findings:
        st.caption("No PNG plots in this target's directory.")

    # --- 6) live ZTF light curve / phase-fold (opt-in, where a period exists)
    op.live_phasefold_panel(crow, findings)

    # --- 7) written dossier + cross-hunt appearances ----------------------
    op.dossier_md_panel(tid, findings, crow)
    op.cross_hunt_panel(tid, findings, crow, hd)

    # --- raw expanders + single-source deep-dive pointer ------------------
    if crow:
        with st.expander("Candidate row (candidates.csv)"):
            kv = pd.DataFrame(
                {"value": {k: ("" if v is None else str(v)) for k, v in crow.items()}}
            )
            st.dataframe(kv, width="stretch")
    if findings:
        with st.expander("Raw findings.json"):
            st.json(findings)

    st.caption(
        "🔬 For the NSS-cascade single-source work-up (photocentric mass function, "
        "HGCA / Kervella PMa, tier ladder), open this Gaia DR3 source_id in the "
        "per-source viewer `scripts/web_tool/app.py`."
    )


def _render_triage_bar(hid: str, tid: str) -> None:
    """View 5 — promote / flag / reject, persisted via hunt_data.write_triage."""
    current = hd.get_triage_verdict(hid, tid)
    badge = {"promote": "⭐ PROMOTED", "flag": "🚩 FLAGGED", "reject": "🗑️ REJECTED"}
    head = st.columns([3, 5])
    head[0].markdown(f"#### `{tid}`")
    if current:
        head[1].markdown(f"### {badge.get(current, current.upper())}")
    else:
        head[1].markdown("### _untriaged_")

    note = st.text_input("Triage note (optional)", key=f"note_{hid}_{tid}",
                         placeholder="e.g. queue for RV follow-up")
    b = st.columns(4)

    def _do(verdict: str) -> None:
        hd.write_triage(hid, tid, verdict, note=note)
        _findings.clear()  # triage_counts in dashboard reads fresh next render
        st.toast(f"{tid} → {verdict}", icon="✅")
        st.rerun()

    if b[0].button("⭐ Promote", width="stretch", type="primary"):
        _do("promote")
    if b[1].button("🚩 Flag", width="stretch"):
        _do("flag")
    if b[2].button("🗑️ Reject", width="stretch"):
        _do("reject")
    if b[3].button("↩️ Clear", width="stretch", disabled=current is None):
        _do("clear")


# ---------------------------------------------------------------------------
# View 4 — Sky map
# ---------------------------------------------------------------------------

def view_skymap() -> None:
    st.header("🗺️ Sky Map")
    hid = _pick_run("sky_run")
    if not hid:
        return
    df = _candidates(hid)
    df = df.dropna(subset=["ra", "dec"])
    if df.empty:
        st.warning("No candidates with RA/Dec to map.")
        return
    st.caption(f"{len(df)} candidates with coordinates. Markers are labelled by id; "
               "verdict drives colour where supported.")

    use_aladin = st.toggle("Aladin Lite v3 (interactive)", value=True,
                           help="Uncheck for a static matplotlib RA/Dec scatter "
                                "(use this if the CDN/JS is blocked).")
    if use_aladin:
        _render_aladin(df)
        st.caption("If the sky view above is blank (CDN blocked / offline), "
                   "uncheck the toggle for the matplotlib fallback.")
    else:
        _render_scatter(df)


def _render_aladin(df: pd.DataFrame) -> None:
    import json as _json
    ra0 = float(df["ra"].mean())
    dec0 = float(df["dec"].mean())
    # build marker payload (cap to keep the embed light)
    cap = df.head(2000)
    markers = [
        {"ra": float(r["ra"]), "dec": float(r["dec"]),
         "id": str(r["id"]), "verdict": str(r.get("verdict", ""))}
        for _, r in cap.iterrows()
    ]
    payload = _json.dumps(markers)
    html = f"""
    <div id="aladin-lite-div" style="width:100%;height:600px;"></div>
    <script src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js" charset="utf-8"></script>
    <script>
      let markers = {payload};
      function initAladin() {{
        A.init.then(() => {{
          let aladin = A.aladin('#aladin-lite-div', {{
              survey: 'P/DSS2/color',
              fov: 2.5,
              target: '{ra0} {dec0}',
              cooFrame: 'ICRS'
          }});
          var cat = A.catalog({{name: 'candidates', sourceSize: 12, color: '#ff4b4b'}});
          aladin.addCatalog(cat);
          var srcs = markers.map(function(m) {{
              return A.marker(m.ra, m.dec, {{popupTitle: m.id,
                  popupDesc: 'verdict: ' + m.verdict + '<br/>RA/Dec: ' + m.ra.toFixed(5) + ' ' + m.dec.toFixed(5)}});
          }});
          cat.addSources(srcs);
        }});
      }}
      // load-guard: wait until aladin.js has defined the global A, then init
      (function waitForA() {{
        if (window.A && A.init) {{ initAladin(); }}
        else {{ setTimeout(waitForA, 100); }}
      }})();
    </script>
    """
    st.components.v1.html(html, height=620, scrolling=False)


def _render_scatter(df: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # noqa: BLE001
        st.error(f"matplotlib unavailable for fallback scatter: {exc}")
        st.dataframe(df[["id", "ra", "dec", "verdict"]], width="stretch")
        return
    fig, ax = plt.subplots(figsize=(9, 6))
    # colour by verdict
    verdicts = df["verdict"].fillna("")
    cats = sorted(verdicts.unique())
    cmap = plt.get_cmap("tab10")
    for i, c in enumerate(cats):
        sub = df[verdicts == c]
        ax.scatter(sub["ra"], sub["dec"], s=28, color=cmap(i % 10),
                   label=(c or "(none)"), alpha=0.8, edgecolor="k", linewidth=0.3)
    ax.invert_xaxis()  # RA increases to the left
    ax.set_xlabel("RA (deg)")
    ax.set_ylabel("Dec (deg)")
    ax.set_title("Candidate positions")
    ax.grid(alpha=0.3)
    if len(cats) <= 12:
        ax.legend(fontsize=8, loc="best")
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=110)
    plt.close(fig)
    st.image(buf.getvalue(), width="stretch")


# ---------------------------------------------------------------------------
# View 6 — Cross-hunt search
# ---------------------------------------------------------------------------

def view_cross_search() -> None:
    st.header("🔎 Cross-hunt Source Search")
    st.caption("Look up one source id across every hunt's candidate list.")
    sid = st.text_input("Source id", placeholder="e.g. 3152p454_b0-000375")
    if not sid.strip():
        # offer a quick pick from the available ids to make the demo discoverable
        runs = _runs()
        sample = []
        for h in runs:
            ids = _candidates(h)["id"].tolist()
            sample.extend(ids[:3])
        if sample:
            st.caption("Try one of: " + ", ".join(f"`{s}`" for s in sample[:6]))
        return

    hits = hd.cross_hunt_search(sid.strip())
    if not hits:
        st.warning(f"No hunt contains a candidate with id `{sid.strip()}`.")
        return
    st.success(f"Found in {len(hits)} hunt(s).")
    rows = []
    for hk, row in hits:
        man = _manifest(hk)
        rows.append({
            "hunt": hk,
            "title": man.get("title", hk),
            "lane": man.get("lane"),
            "status": man.get("status"),
            "score": row.get("score"),
            "verdict": row.get("verdict"),
            "triage": row.get("_triage") or "",
            "ra": row.get("ra"),
            "dec": row.get("dec"),
        })
    out = pd.DataFrame(rows)
    st.dataframe(
        out, width="stretch", hide_index=True,
        column_config={
            "score": st.column_config.NumberColumn(format="%.3f"),
            "ra": st.column_config.NumberColumn(format="%.5f"),
            "dec": st.column_config.NumberColumn(format="%.5f"),
        },
    )
    if st.button("➡️ Open first hit in Target Findings"):
        st.session_state["_pending_target"] = {"hunt": hits[0][0], "id": sid.strip()}
        st.session_state["_pending_nav"] = "Target Findings"
        st.rerun()


# ---------------------------------------------------------------------------
# Sidebar nav + dispatch
# ---------------------------------------------------------------------------
VIEWS = {
    "Dashboard (LIVE)": view_dashboard,
    "Target Browser": view_browser,
    "Target Findings": view_findings,
    "Sky map": view_skymap,
    "Cross-hunt search": view_cross_search,
}


def main() -> None:
    st.sidebar.title("🔭 Hunt Console")
    st.sidebar.caption("Monitor · browse · triage archival-discovery hunts")

    # allow programmatic nav: buttons set st.session_state['_pending_nav'];
    # apply it to the widget key BEFORE the radio is instantiated (Streamlit
    # forbids mutating a widget's key after the widget exists).
    if "_pending_nav" in st.session_state:
        st.session_state["nav"] = st.session_state.pop("_pending_nav")
    if "nav" not in st.session_state:
        st.session_state["nav"] = "Dashboard (LIVE)"
    options = list(VIEWS)
    choice = st.sidebar.radio("View", options, key="nav")

    st.sidebar.divider()
    runs = _runs()
    st.sidebar.metric("Hunts", len(runs))
    n_running = sum(1 for h in runs if _manifest(h).get("status") == "running")
    if n_running:
        st.sidebar.metric("In progress", n_running)
    st.sidebar.caption(f"Runs dir:\n`{hd.runs_dir()}`")
    if st.sidebar.button("🔄 Reload from disk", width="stretch"):
        _clear_caches()
        st.rerun()
    st.sidebar.divider()
    st.sidebar.caption("Sibling of the single-source dossier viewer "
                       "(`scripts/web_tool/app.py`).")

    VIEWS[choice]()


if __name__ == "__main__":
    main()
