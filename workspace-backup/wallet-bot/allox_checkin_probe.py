"""Probe checkin chain values. Key transient, never logged."""
import json, os, time, urllib.request, urllib.error

PROXY = "http://127.0.0.1:3129"
os.environ["https_proxy"] = PROXY
os.environ["http_proxy"] = PROXY
BASE = "https://api.allox.ai"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

def api(method, path, body=None, token=None):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Content-Type": "application/json", "User-Agent": UA,
                 "Accept": "application/json",
                 **({"Authorization": f"Bearer {token}"} if token else {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: raw = e.read()[:400]
        except Exception: raw = b"<unreadable>"
        try: return e.code, json.loads(raw.decode())
        except Exception: return e.code, {"raw": str(raw[:120])}
    except Exception as e:
        return 599, {"raw": str(e)[:120]}

token = open(os.path.expanduser("~/workspace/wallet-bot/.allox-token")).read().strip()
for chain in ["bnb", "ethereum", "base", "BNB", "bsc"]:
    code, r = api("POST", "/checkin", {"chain": chain}, token=token)
    print(chain, "->", code, json.dumps(r)[:300])
    time.sleep(1)
