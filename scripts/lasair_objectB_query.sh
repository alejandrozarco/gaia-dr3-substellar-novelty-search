#!/bin/bash
# Lasair broker queries for Object B (Gaia DR3 3161546596480983040) + neighbour control.
# Token: put your Lasair API token (from your Lasair profile page after login) in
#   ~/.config/lasair/token   (chmod 600)
# then run:  bash scripts/lasair_objectB_query.sh
# Queries BOTH the ZTF instance (lasair-ztf) and the LSST instance (lasair-lsst).
set -euo pipefail
TOK="${LASAIR_TOKEN:-$(cat "$HOME/.config/lasair/token" 2>/dev/null || true)}"
: "${TOK:?no Lasair token: put it in ~/.config/lasair/token or set LASAIR_TOKEN}"

RA_B=112.335086;  DEC_B=9.868546     # Object B
RA_N=112.335198;  DEC_N=9.869864     # 4.76" neighbour (contamination control)
OUT=/tmp/lasair_objectB; mkdir -p "$OUT"

cone () {  # host ra dec label
  echo "--- $4 @ $1 ---"
  curl -s -m 30 --get "https://$1/api/cone/" \
    -H "Authorization: Token $TOK" \
    --data-urlencode "ra=$2" --data-urlencode "dec=$3" \
    --data-urlencode "radius=5" --data-urlencode "requestType=all" \
    | tee "$OUT/cone_$4_${1%%.*}.json" | head -c 500; echo
}

for HOST in lasair-ztf.lsst.ac.uk lasair-lsst.lsst.ac.uk; do
  cone "$HOST" "$RA_B" "$DEC_B" objectB
  cone "$HOST" "$RA_N" "$DEC_N" neighbour
done
echo
echo "Results in $OUT/. Empty lists = validated nulls (no alerts at the positions)."
echo "Next (web UI, optional): create a watchlist of the candidate roster on lasair-lsst"
echo "so future LSST alerts at these positions email you automatically."
