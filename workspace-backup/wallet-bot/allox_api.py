"""AlloX onboarding via direct API: SIWE nonce -> sign -> verify -> query state.
Reads private key transiently from .privkey; NEVER logs it."""
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
            raw = e.read()
            try:
                return e.code, json.loads(raw.decode())
            except Exception:
                last = (e.code, raw[:200])
        except Exception as e:
            last = ("exc", str(e)[:200])
        time.sleep(2)
    return 599, {"raw": str(last)}

def main():
    from eth_account import Account
    from eth_account.messages import encode_defunct

    with open(os.path.expanduser("~/workspace/wallet-bot/.privkey")) as f:
        priv = f.read().strip()
    acct = Account.from_key(priv)
    assert acct.address.lower() == ADDR.lower(), f"key mismatch: {acct.address}"
    del priv

    code, nonce = api("GET", f"/auth/nonce/{ADDR}")
    assert code == 200, nonce
    msg = nonce["message"]
    print("nonce message:", repr(msg))

    sig = acct.sign_message(encode_defunct(text=msg)).signature.hex()
    print("signed ok, sig len:", len(sig))

    code, v = api("POST", "/auth/verify",
                  {"address": ADDR, "signature": "0x" + sig, "walletProvider": "metamask"})
    print("verify:", code)
    if code != 200 or "token" not in v:
        print(json.dumps(v)[:800])
        return
    token = v["token"]
    print("token acquired (len %d). user:" % len(token), json.dumps(v.get("user"))[:400])

    code, me = api("GET", "/auth/me", token=token)
    print("me:", code, json.dumps(me)[:1500])

    for p in ["/season1/claim", "/checkin/status", "/twitter/tasks",
              "/twitter/status", "/chat/allox/status", "/telegram/status",
              "/referral/claim"]:
        code, r = api("GET", p, token=token)
        print(p, "->", code, json.dumps(r)[:600])

    with open("/tmp/allox-token.txt", "w") as f:
        os.chmod("/tmp/allox-token.txt", 0o600)
        f.write(token)
    print("token saved to /tmp/allox-token.txt (mode 600)")

if __name__ == "__main__":
    main()
