#!/bin/bash
# Download all PS1 i/r/z warp cutouts at the target position (skip already-downloaded)
cd /tmp/rubin_pilot/forensics/170591507978387512
mkdir -p cutouts
for lst in ps1_warps_i.txt ps1_warps_r.txt ps1_warps_z.txt; do
  band=$(echo $lst | sed 's/ps1_warps_\(.\).txt/\1/')
  tail -n +2 $lst | while read -r projcell subcell ra dec filter mjd type filename shortname badflag; do
    tag=$(basename "$filename" .fits | sed 's/rings.v3.skycell.1043.029.wrp.//' | tr '.' '_')
    out="cutouts/wrp_${tag}.fits"
    [ -s "$out" ] && continue
    curl -s --max-time 120 "https://ps1images.stsci.edu/cgi-bin/fitscut.cgi?ra=313.22651&dec=-14.84044&size=64&format=fits&red=${filename}" -o "$out"
    sleep 0.3
  done
done
ls cutouts/ | wc -l
echo DONE
