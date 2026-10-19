"""AlloX state dump + checkin probe. Key transient, never logged."""
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
                raw = e.read()[:600]
            except Exception:
                raw = b"<unreadable>"
            try:
                return e.code, json.loads(raw.decode())
            except Exception:
                last = (e.code, raw[:150] if isinstance(raw, bytes) else raw)
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
    out = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.localtime())}

    code, me = api("GET", "/auth/me", token=token)
    if code == 200:
        s1 = me.get("season1", {})
        out["points"] = s1.get("points")
        out["breakdown"] = s1.get("pointsBreakdown")
        out["claimed"] = s1.get("claimed")
        out["twitter_linked"] = me.get("twitter", {}).get("linked")
        out["telegram_linked"] = me.get("telegram", {}).get("linked")
        out["eligible"] = me.get("eligibility", {}).get("eligible")
        out["referral_code"] = me.get("referral", {}).get("code")

    code, r = api("GET", "/checkin/status", token=token)
    out["checkin_status"] = {"code": code, "body": r}

    # probe checkin POST without tx to learn requirements
    code, r = api("POST", "/checkin", {}, token=token)
    out["checkin_post_empty"] = {"code": code, "body": r}

    code, r = api("GET", "/chat/allox/status", token=token)
    out["chat_status"] = {"code": code, "body": r}

    code, r = api("GET", "/twitter/tasks", token=token)
    out["twitter_tasks"] = {"code": code, "body": str(r)[:400]}

    print(json.dumps(out, indent=1)[:4000])

    p = os.path.expanduser("~/workspace/wallet-bot/.allox-token")
    with open(p, "w") as f:
        f.write(token)
    os.chmod(p, 0o600)

if __name__ == "__main__":
    main()
