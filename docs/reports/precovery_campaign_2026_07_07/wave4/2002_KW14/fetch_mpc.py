import requests, json, re
PY = "307251"  # numbered; also try designation
# MPC get-obs API (GET form)
url = "https://data.minorplanetcenter.net/api/get-obs"
out = None
for payload in [{"desigs":["2002 KW14"],"output_format":["OBS80"]},
                {"desigs":["307251"],"output_format":["OBS80"]}]:
    try:
        r = requests.get(url, json=payload, timeout=60)
        print("try", payload, r.status_code, len(r.text))
        if r.status_code==200 and r.text.strip().startswith(('[','{')):
            out = r.json(); 
            json.dump(out, open("mpc_getobs_raw.json","w"), indent=1)
            break
    except Exception as e:
        print("err", e)
print("got", type(out), None if out is None else len(out))
