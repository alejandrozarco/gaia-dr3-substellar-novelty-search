# Parse DESI DR1 spectra embedded (bokeh ColumnDataSource, gzip+base64 ndarrays) in the Legacy Survey viewer page
# https://www.legacysurvey.org/viewer/desi-spectrum/dr1/targetid<TARGETID>. Returns dict name -> {field: array}.
import re, json, base64, gzip, numpy as np, sys
def decode(v):
    a = v["array"]; dt = v.get("dtype", "float64"); order = v.get("order", "little")
    raw = base64.b64decode(a["data"]) if isinstance(a, dict) else base64.b64decode(a)
    if raw[:2] == b"\x1f\x8b": raw = gzip.decompress(raw)
    arr = np.frombuffer(raw, dtype=np.dtype(dt).newbyteorder("<" if order == "little" else ">"))
    return arr.reshape(v.get("shape", arr.shape))
def sources(fn):
    h = open(fn).read(); b = re.findall(r'<script type="application/json"[^>]*>(.*?)</script>', h, re.S)[0]
    j = json.loads(b); out = {}
    def walk(o):
        if isinstance(o, dict):
            if o.get("name") == "ColumnDataSource" and "attributes" in o and "data" in o["attributes"]:
                nm = o["attributes"].get("name", o.get("id")); d = {}
                for k, v in o["attributes"]["data"].get("entries", []):
                    if isinstance(v, dict) and v.get("type") == "ndarray":
                        try: d[k] = decode(v)
                        except Exception as e: d[k] = f"ERR {e}"
                    elif isinstance(v, list): d[k] = np.array(v) if all(isinstance(x, (int, float)) for x in v) else v
                if d: out.setdefault(nm, d)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(j); return out
if __name__ == "__main__":
    s = sources(sys.argv[1])
    for k, d in s.items():
        print(k, {kk: (getattr(vv, "shape", None), str(getattr(vv, "dtype", ""))) for kk, vv in d.items()})
