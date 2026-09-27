#!/bin/bash
# Resilient driver: wait for the IRSA ZTF light-curve API, run the search (cached light curves are reused), repeat until no HOLE rows remain.
cd "$(dirname "$0")"; IN=$1; OUT=$2; LOG=$3
probe() { curl -s -m 60 "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20155.71%2016.2%200.00042&BANDNAME=g,r&FORMAT=csv" | head -c 3 | grep -q oid; }
for round in 1 2 3 4 5 6 7 8; do
  until probe; do echo "$(date +%H:%M) IRSA down" >> $LOG; sleep 240; done
  echo "$(date +%H:%M) round $round start" >> $LOG
  nice -n 10 python jestin_ztf.py $IN $OUT.tmp >> $LOG 2>&1
  n=$(grep -c ",HOLE" $OUT.tmp); echo "$(date +%H:%M) round $round done, holes $n" >> $LOG
  mv $OUT.tmp $OUT
  [ "$n" -eq 0 ] && break
  sleep 300
done
