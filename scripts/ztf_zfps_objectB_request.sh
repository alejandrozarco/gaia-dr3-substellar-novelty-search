#!/bin/bash
# ZTF Forced Photometry (ZFPS) batch request — Object B (Gaia DR3 3161546596480983040)
# Position: ledger-canonical 112.335086 +9.868546 (docs/object_journals/3161546596480983040.md)
# Window: full ZTF survey (2018-03-17 .. now). Queue can take 7+ days; results emailed.
#
# Run (password from Joahan's 2026-06-12 email; email field is CASE-SENSITIVE):
#   ZFPS_PASS='<userpass>' bash scripts/ztf_zfps_objectB_request.sh
#
# Docs: https://irsa.ipac.caltech.edu/data/ZTF/docs/ztf_forced_photometry.pdf
set -euo pipefail
: "${ZFPS_PASS:?set ZFPS_PASS to the ZFPS userpass from the IPAC email}"

JDSTART=2458194.5      # 2018-03-17 (ZTF survey start)
JDEND=2461204.5        # ~2026-06-12 (now)
EMAIL="alexander@ch.tudelft.nl"   # case-sensitive per IPAC

# TWO positions: Object B + the 4.76" neighbour (Gaia DR3 3161546630842185984, G=13.8,
# itself a close double: ipd_mp=91, RUWE 19). The neighbour curve is the CONTAMINATION
# CONTROL: any "variability" at Object B's position must NOT correlate with the
# neighbour's own variability leaking through the difference-image PSF wings.
submit () {  # ra dec label
  wget --http-user=ztffps --http-passwd=dontgocrazy \
    -O "/tmp/zfps_submit_${3}.html" \
    "https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi?ra=${1}&dec=${2}&jdstart=${JDSTART}&jdend=${JDEND}&email=${EMAIL}&userpass=${ZFPS_PASS}"
  echo "--- ${3} response ---"
  grep -oiE "(success|error|exceed|invalid)[^<]*" "/tmp/zfps_submit_${3}.html" || cat "/tmp/zfps_submit_${3}.html"
}

# The wget HTTP basic-auth pair (ztffps/dontgocrazy) is the PUBLIC service login
# documented in the ZFPS PDF; the personal credential is the email+userpass params.
submit 112.335086 9.868546 objectB
submit 112.335198 9.869864 neighbour   # Gaia DR3 3161546630842185984 (Gaia-verified 2026-06-12)

echo
echo "Submitted both positions, full survey window. Results arrive by email (can take 7+ days)."
