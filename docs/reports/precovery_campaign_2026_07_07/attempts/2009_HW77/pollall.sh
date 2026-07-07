cd /tmp/precovery_recut/attempts/2009_HW77/
TAGS="2013 2014a 2014b 2015a 2015b 2015c 2016a 2019a 2019b NEG_2013 NEG_2014a NEG_2014b NEG_2015a NEG_2015b NEG_2015c"
for round in $(seq 1 120); do
  alldone=1
  for tag in $TAGS; do
    [ -f done_$tag ] && continue
    if [ -f jobNEG_${tag#NEG_}.url ] && [ "${tag#NEG_}" != "$tag" ]; then
      loc=$(cat jobNEG_${tag#NEG_}.url)
    else
      loc=$(cat job_$tag.url)
    fi
    ph=$(curl -s --max-time 15 "$loc/phase" 2>/dev/null)
    if [ "$ph" = "COMPLETED" ]; then
      curl -s --max-time 45 "$loc/results/result" -o meas_$tag.csv 2>/dev/null
      if head -1 meas_$tag.csv | grep -qi "html\|504\|gateway"; then
        rm -f meas_$tag.csv; alldone=0
      else
        touch done_$tag
        echo "$(date +%H:%M:%S) $tag COMPLETED rows=$(($(wc -l < meas_$tag.csv)-1))"
      fi
    elif [ "$ph" = "ERROR" ] || [ "$ph" = "ABORTED" ]; then
      echo "$(date +%H:%M:%S) $tag $ph"; touch done_$tag
    else
      alldone=0
    fi
  done
  [ "$alldone" = "1" ] && { echo "ALL DONE"; break; }
  sleep 15
done
echo "pollall finished"
