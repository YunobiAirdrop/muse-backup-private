"""Try signature+message checkin path. Key transient, never logged."""
import json, os, urllib.request, urllib.error

PROXY = "http://127.0.0.1:3129"
os.environ["https_proxy"] = PROXY
os.environ["http_proxy"] = PROXY
BASE = "https://api.allox.ai"
ADDR = "0xf0f25C36AC70E9d787a108eFB351626192C8107b"
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
        try: raw = e.read()[:500]
        except Exception: raw = b"<unreadable>"
        try: return e.code, json.loads(raw.decode())
        except Exception: return e.code, {"raw": str(raw[:200])}

from eth_account import Account
from eth_account.messages import encode_defunct
with open(os.path.expanduser("~/workspace/wallet-bot/.privkey")) as f:
    priv = f.read().strip()
acct = Account.from_key(priv)
assert acct.address.lower() == ADDR.lower()
del priv

messages = [
    "Check in to AlloX",
    "AlloX Daily Check-in",
    f"Check in to AlloX\n\nAddress: {ADDR}",
    "Sign this message to check in to AlloX",
]
for msg in messages:
    sig = acct.sign_message(encode_defunct(text=msg)).signature.hex()
    code, r = api("POST", "/checkin", {"chain": "bnb", "signature": "0x"+sig, "message": msg})
    print(repr(msg[:45]), "->", code, json.dumps(r)[:250])
