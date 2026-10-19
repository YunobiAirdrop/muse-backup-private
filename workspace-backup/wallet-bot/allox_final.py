"""Final AlloX state. Key transient, never logged."""
import json, os, urllib.request, urllib.error
PROXY = "http://127.0.0.1:3129"
os.environ["https_proxy"] = PROXY
os.environ["http_proxy"] = PROXY
BASE = "https://api.allox.ai"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
token = open(os.path.expanduser("~/workspace/wallet-bot/.allox-token")).read().strip()
def api(method, path, body=None):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Content-Type": "application/json", "User-Agent": UA,
                 "Accept": "application/json", "Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: raw = e.read()[:400]
        except Exception: raw = b"<unreadable>"
        try: return e.code, json.loads(raw.decode())
        except Exception: return e.code, {"raw": str(raw[:150])}
code, me = api("GET", "/auth/me")
s1 = me.get("season1", {})
print(json.dumps({
    "points": s1.get("points"),
    "breakdown": s1.get("pointsBreakdown"),
    "claimed": s1.get("claimed"),
    "eligible": me.get("eligibility", {}).get("eligible"),
    "twitter": me.get("twitter"),
    "telegram": me.get("telegram"),
    "referral": me.get("referral"),
}, indent=1))
code, cs = api("GET", "/checkin/status")
print("checkin:", json.dumps(cs.get("rewards", [])[:2]), "| lifetime:", cs.get("lifetimeCheckIns"))
