# Streaming hunt pipeline

A chunked, resumable, live-classifying replacement for the monolithic
`companions_hunt_*.py` script. Lets you start downstream analysis the
moment the first RA chunk lands instead of waiting ~30 min for the full
pull to finish.

## Architecture

```
                                                  ┌──────────────────┐
       Gaia archive                                │  dashboard.py    │
              │                                    │  (text UI)        │
              ↓                                    └──────────────────┘
       producer.py                                          ↑
       (12× RA chunks                                       │
        atomic writes to                                    │  reads JSON
        data/raw_chunks/                                    │
        *.parquet + STATE)                                  │
              │                                             │
              ↓ (fs event)                                  │
       consumer.py                              ┌────────────────────┐
       (watchdog handler:                       │ data/derived/      │
        - derive M_2 + class                    │   {mode}_hunt_     │
        - filter #30 / #31 flags                │   derived.parquet  │
        - update defensible BH/NS               │   {mode}_def_*.pq  │
        - update live_stats.json                │   live_stats_*.json│
        - forward to River)                     │   {mode}_ml_*.json │
              │                                 └────────────────────┘
              ↓                                          ↑
       river_ml.RiverClassifier                          │
       (online prequential learning,                     │
        AdaptiveRandomForest)              ┌─────────────┴──────┐
                                            │ duckdb_views.py    │
                                            │ (ad-hoc SQL on the │
                                            │  growing parquet)  │
                                            └────────────────────┘
```

## Files

| File | Role |
|---|---|
| `producer.py` | Chunked Gaia fetcher. Writes `data/raw_chunks/{mode}_RA{NNN}.parquet` atomically + maintains `STATE_{mode}.json`. Resumable on kill/restart. |
| `consumer.py` | watchdog-based filesystem watcher. On each new chunk file: derive M_2 + class, append to derived parquet, update stats, forward to River. |
| `river_ml.py` | Online ML — `RiverClassifier` learns one row at a time from each chunk. Held-out-M_2 multi-class problem (same as our sklearn experiment, now streaming). Saves model + metric checkpoints. |
| `duckdb_views.py` | DuckDB views over `data/raw_chunks/*.parquet` and `data/derived/`. Ad-hoc SQL queries against growing dataset. |
| `dashboard.py` | Text-mode live dashboard reading STATE + live_stats + ML stats. No Streamlit needed. |
| `run_pipeline.sh` | Orchestrator. Launches consumer + producer (and optionally River ML) in background. |

## Quickstart

```bash
# Launch main-hunt pipeline (producer + consumer + ML)
bash scripts/streaming/run_pipeline.sh main --enable-ml

# In another terminal, live status
python scripts/streaming/dashboard.py --mode main

# In yet another terminal, ad-hoc SQL
python scripts/streaming/duckdb_views.py --preset class_dist_main
python scripts/streaming/duckdb_views.py --query "SELECT * FROM main_derived WHERE class='dormant_BH_candidate' AND filter31='PASS' ORDER BY significance DESC LIMIT 10"
```

## What you get on chunk 1 (~2 min)

After the first RA chunk lands (~4000 sources) the consumer immediately:
- Derives M_2 and class
- Writes `data/derived/main_hunt_derived.parquet` (4000 rows)
- Writes `main_defensible_bh.parquet`, `main_defensible_ns.parquet`
- Updates `live_stats_main.json` with class distribution
- Forwards rows to River — first ~4000 learn-one calls
- Dashboard shows partial state

By chunk 6/12 (~15 min) you have half the candidates triaged, the River
model has seen ~25k rows and the per-class accuracy converges. By chunk
12/12 (~30 min) the full hunt is done and the model is fully trained.

## Resumability

If the producer dies mid-chunk (Gaia timeout, network hiccup, OOM):

```bash
# Just rerun it. STATE_main.json records completed chunks, so it picks up
# at the next not-yet-done chunk.
python scripts/streaming/producer.py --mode main
```

Atomic writes (`.tmp` → `rename`) guarantee no partial-chunk corruption.

To force a from-scratch re-fetch:

```bash
python scripts/streaming/producer.py --mode main --restart
```

## River ML notes

The held-out-M_2 multi-class problem we did earlier with sklearn:
- target = cascade-derived `class` label (multi-class)
- features = everything EXCEPT M_2 and fM (cascade's defining quantities)

In the sklearn batch run on 10k rows we saw:
- BD_candidate recall = 0.028 (≈ unrecoverable from non-M_2 features)
- M_dwarf 0.90, WD 0.77, NS 0.22

River reproduces this online + lets us watch how the per-class accuracy
evolves as more data flows in. The streaming-mode question is whether
the BD recall stays at ~0.03 throughout or shifts as the model sees more
diverse data. (Hypothesis: stays low — confirms the structural finding.)

To refit a saved model from scratch on the full derived parquet:

```bash
python scripts/streaming/river_ml.py --mode main --refit
```

## DuckDB queries that auto-update

The view layer auto-discovers new parquet files in `data/raw_chunks/`:

```sql
-- This query returns more rows each time you run it as more chunks land
SELECT class, COUNT(*) FROM main_derived GROUP BY 1 ORDER BY 2 DESC;

-- Find surviving candidates after Filter #29 + #30 + #31
SELECT source_id, significance, M2_msun, G, filter31
FROM main_derived
WHERE class IN ('dormant_BH_candidate', 'dormant_NS_candidate')
  AND NOT in_sb2 AND NOT cbias_risk AND filter31 = 'PASS'
ORDER BY significance DESC;
```

## When to use what

| Need | Tool |
|---|---|
| Track producer progress | `dashboard.py` |
| Ad-hoc analytical query | `duckdb_views.py` |
| Restart after Gaia stall | `producer.py` (just rerun) |
| Refit ML from full data | `river_ml.py --refit` |
| Watch live model accuracy | `dashboard.py` (auto-refresh) |
