cd /tmp/precovery_recut/attempts/2009_HW77/
TAGS="2013 2014a 2014b 2015a 2015b 2015c"
for round in $(seq 1 90); do
  alldone=1
  for tag in $TAGS; do
    [ -f done_$tag ] && continue
    loc=$(cat job_$tag.url)
    ph=$(curl -s --max-time 15 "$loc/phase" 2>/dev/null)
    if [ "$ph" = "COMPLETED" ]; then
      curl -s --max-time 50 "$loc/results/result" -o meas_$tag.csv 2>/dev/null
      if head -1 meas_$tag.csv | grep -qi "html\|504\|gateway"; then rm -f meas_$tag.csv; alldone=0
      else touch done_$tag; echo "$(date +%H:%M:%S) $tag COMPLETED rows=$(($(wc -l < meas_$tag.csv)-1))"; fi
    elif [ "$ph" = "ERROR" ] || [ "$ph" = "ABORTED" ]; then echo "$tag $ph"; touch done_$tag
    else alldone=0; fi
  done
  [ "$alldone" = "1" ] && { echo "ALL CORE DONE"; break; }
  sleep 15
done
echo "pollcore finished"
