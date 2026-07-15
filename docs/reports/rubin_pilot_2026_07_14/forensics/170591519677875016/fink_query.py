import requests, json
oid = "170591519677875016"
tries = [
  ("https://api.fink-portal.org/api/v1/objects", {"objectId": oid, "output-format":"json"}),
]
for url, payload in tries:
    try:
        r = requests.post(url, json=payload, timeout=60)
        print(url, r.status_code, r.text[:300])
    except Exception as e:
        print(url, "EXC", e)
# discover endpoints
r = requests.get("https://api.fink-portal.org/api/v1/schema", timeout=30)
print("schema:", r.status_code, r.text[:200])
