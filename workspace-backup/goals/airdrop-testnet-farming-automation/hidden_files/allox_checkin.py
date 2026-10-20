#!/usr/bin/env python3
"""AlloX daily checkin via curl (urllib through local proxy is flaky).
Token read from .allox-token, key read transiently, never printed."""
import json
import subprocess
import sys

sys.path.insert(0, "/home/hatch/workspace/wallet-bot/venv/lib/python3.12/site-packages")
from eth_account import Account
from eth_account.messages import encode_defunct

BASE = "/home/hatch/workspace/wallet-bot"
ADDR = "0xf0f25C36AC70E9d787a108eFB351626192C8107b"
API = "https://api.allox.ai"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

with open(f"{BASE}/.allox-token") as f:
    token = f.read().strip()
with open(f"{BASE}/.privkey") as f:
    priv = f.read().strip()
acct = Account.from_key(priv)
assert acct.address.lower() == ADDR.lower()
del priv


def curl(method, path, body=None):
    cmd = ["curl", "-s", "--max-time", "25", "-x", "http://127.0.0.1:3129",
           "-X", method, API + path,
           "-H", f"Authorization: Bearer {token}",
           "-H", f"User-Agent: {UA}",
           "-H", "Content-Type: application/json",
           "-H", "Accept: application/json"]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    try:
        return json.loads(out.stdout or "{}")
    except Exception:
        return {"_raw": (out.stdout or "")[:150], "_err": (out.stderr or "")[:100]}


me = curl("GET", "/auth/me")
s1 = me.get("season1", {}) if isinstance(me, dict) else {}
print("points_now:", s1.get("points"), "| eligible:", me.get("eligibility", {}).get("eligible") if isinstance(me, dict) else "?")
cs = curl("GET", "/checkin/status")
print("checkin_status:", json.dumps(cs)[:300])

msgs = [
    "Check in to AlloX",
    "AlloX Daily Check-in",
    f"Check in to AlloX\n\nAddress: {ADDR}",
    "Sign this message to check in to AlloX",
]
for msg in msgs:
    sig = acct.sign_message(encode_defunct(text=msg)).signature.hex()
    r = curl("POST", "/checkin", {"chain": "bnb", "signature": "0x" + sig, "message": msg})
    print("checkin", repr(msg[:40]), "->", json.dumps(r)[:250])
    if isinstance(r, dict) and (r.get("success") or "checkin" in json.dumps(r).lower()[:0] or r.get("points") is not None):
        break
