BASE="https://ssd.jpl.nasa.gov/api/horizons.api"
curl -s -G "$BASE" \
  --data-urlencode "format=text" \
  --data-urlencode "COMMAND=-48" \
  --data-urlencode "OBJ_DATA=NO" \
  --data-urlencode "MAKE_EPHEM=YES" \
  --data-urlencode "EPHEM_TYPE=VECTORS" \
  --data-urlencode "CENTER=500@399" \
  --data-urlencode "REF_PLANE=FRAME" \
  --data-urlencode "REF_SYSTEM=ICRF" \
  --data-urlencode "VEC_TABLE=1" \
  --data-urlencode "OUT_UNITS=KM-S" \
  --data-urlencode "TIME_TYPE=UT" \
  --data-urlencode "TLIST_TYPE=JD" \
  --data-urlencode "TLIST=2453857.857090 2453857.860793 2453857.864497 2453857.868201" \
  -o hst_vectors.txt -w "HTTP %{http_code}\n"
