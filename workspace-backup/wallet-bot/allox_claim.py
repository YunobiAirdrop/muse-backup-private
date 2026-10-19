"""AlloX follow-up: re-auth, POST /season1/claim, probe chat/checkin claim shapes.
Key material: transient from .privkey, NEVER logged."""
import json, os, time, urllib.request, urllib.error

PROXY = "http://127.0.0.1:3129"
os.environ["https_proxy"] = PROXY
os.environ["http_proxy"] = PROXY

BASE = "https://api.allox.ai"
ADDR = "0xf0f25C36AC70E9d787a108eFB351626192C8107b"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

def api(method, path, body=None, token=None, retries=3):
    last = None
    for i in range(retries):
        req = urllib.request.Request(
            BASE + path,
            data=json.dumps(body).encode() if body is not None else None,
            method=method,
            headers={"Content-Type": "application/json",
                     "User-Agent": UA,
                     "Accept": "application/json",
                     **({"Authorization": f"Bearer {token}"} if token else {})},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            try:
                raw = e.read()[:400]
            except Exception:
                raw = b"<unreadable>"
            try:
                return e.code, json.loads(raw.decode())
            except Exception:
                last = (e.code, raw[:120] if isinstance(raw, bytes) else raw)
        except Exception as e:
            last = ("exc", str(e)[:200])
        time.sleep(2)
    return 599, {"raw": str(last)}

def auth():
    from eth_account import Account
    from eth_account.messages import encode_defunct
    with open(os.path.expanduser("~/workspace/wallet-bot/.privkey")) as f:
        priv = f.read().strip()
    acct = Account.from_key(priv)
    assert acct.address.lower() == ADDR.lower()
    del priv
    code, nonce = api("GET", f"/auth/nonce/{ADDR}")
    assert code == 200, nonce
    sig = acct.sign_message(encode_defunct(text=nonce["message"])).signature.hex()
    code, v = api("POST", "/auth/verify",
                  {"address": ADDR, "signature": "0x" + sig, "walletProvider": "metamask"})
    assert code == 200 and "token" in v, v
    return v["token"]

def main():
    token = auth()
    print("auth ok")

    # 1. Welcome Bonus / season1 claim
    code, r = api("POST", "/season1/claim", token=token)
    print("POST /season1/claim ->", code, json.dumps(r)[:800])

    # 2. chat claim endpoints (probe candidates)
    for p in ["/chat/allox/claim", "/chat/claim", "/season1/claim-chat",
              "/chat/allox/activate"]:
        code, r = api("POST", p, token=token)
        print("POST", p, "->", code, json.dumps(r)[:300])

    # 3. checkin detail (contract + chain info?)
    code, r = api("GET", "/checkin/status", token=token)
    print("GET /checkin/status ->", code, json.dumps(r)[:1200])

    # 4. fresh points state
    code, r = api("GET", "/auth/me", token=token)
    if code == 200:
        s1 = r.get("season1", {})
        print("points now:", s1.get("points"),
              "| breakdown:", json.dumps(s1.get("pointsBreakdown"))[:300])
        print("chat claimed:", r.get("chatClaimed"), "| twitter linked:",
              r.get("twitter", {}).get("linked"))

    # persist token for cron follow-ups
    p = os.path.expanduser("~/workspace/wallet-bot/.allox-token")
    with open(p, "w") as f:
        f.write(token)
    os.chmod(p, 0o600)
    print("token saved to .allox-token (600)")

if __name__ == "__main__":
    main()
