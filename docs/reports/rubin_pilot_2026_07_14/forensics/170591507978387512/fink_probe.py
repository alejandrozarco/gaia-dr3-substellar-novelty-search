import requests, json
# Probe Fink LSST/Rubin API endpoints (verify current ones)
for base in ["https://api.lsst.fink-portal.org", "https://fink-portal.org/api/v1", "https://api.fink-portal.org"]:
    try:
        r = requests.get(base + "/api/v1/objects" if "api/v1" not in base else base + "/objects", timeout=20)
        print(base, r.status_code, r.text[:200].replace("\n"," "))
    except Exception as e:
        print(base, "ERR", repr(e)[:120])
