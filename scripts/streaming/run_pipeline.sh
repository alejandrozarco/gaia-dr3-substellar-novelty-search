#!/bin/bash
# Orchestrator for the streaming hunt pipeline.
#
# Launches in order:
#   1. consumer (background) — watches data/raw_chunks/
#   2. producer (foreground or background)
#
# Both write to disk; the consumer picks up new chunks via watchdog.
# Run `dashboard.py` in another terminal to see live status.
#
# Usage:
#   bash run_pipeline.sh main         # main hunt + consumer
#   bash run_pipeline.sh wider        # wider hunt + consumer
#   bash run_pipeline.sh main --enable-ml   # also start River online learning
#   bash run_pipeline.sh both         # main + wider + 2 consumers

set -e
ROOT=/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27
PY=/Users/legbatterij/claude_projects/ostinato/.venv/bin/python
MODE="${1:-main}"
shift || true
EXTRA_FLAGS="$@"

cd "$ROOT"
mkdir -p data/raw_chunks data/derived logs

run_one() {
    local m=$1
    local consumer_args="--mode $m --catchup"
    if [[ "$EXTRA_FLAGS" == *"--enable-ml"* ]]; then
        consumer_args="$consumer_args --enable-ml"
    fi
    echo "[$(date +%H:%M:%S)] launching consumer for mode=$m ..."
    nohup $PY -u scripts/streaming/consumer.py $consumer_args \
        > logs/consumer_$m.log 2>&1 &
    echo "  consumer pid=$!"
    sleep 1

    echo "[$(date +%H:%M:%S)] launching producer for mode=$m ..."
    nohup $PY -u scripts/streaming/producer.py --mode $m \
        > logs/producer_$m.log 2>&1 &
    echo "  producer pid=$!"
}

if [[ "$MODE" == "both" ]]; then
    run_one main
    run_one wider
else
    run_one $MODE
fi

echo
echo "Pipeline running in background. Watch progress with:"
echo "  python $ROOT/scripts/streaming/dashboard.py --mode $MODE"
echo "Or tail logs:"
echo "  tail -f logs/producer_$MODE.log"
echo "  tail -f logs/consumer_$MODE.log"
