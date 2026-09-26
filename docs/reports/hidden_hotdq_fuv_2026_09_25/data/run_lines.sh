cd /tmp/hotdq/lane_hiddenDQ
tail -n +2 nonDB_outliers.csv | while IFS=, read sid gid cls resid snr; do
  f=/tmp/fanout/exotic_atm/visit/mwmVisit-0.8.1-$sid.fits
  [ -s $f ] || curl -sL --max-time 300 -o $f "https://data.sdss.org/sas/dr20/spectro/astra/0.8.1/spectra/visit/${sid: -4:2}/${sid: -2}/mwmVisit-0.8.1-$sid.fits"
  (cd /tmp/hotdq/dd && timeout 300 $HOME/claude_projects/ostinato/.venv/bin/python spec_lines_gen.py $sid FUV_$gid 2>/dev/null | grep -E "^== |coadd (C II|C I |He I|H I )" | tr '\n' ' '); echo " | $cls resid $resid"
done
echo ALLDONE
