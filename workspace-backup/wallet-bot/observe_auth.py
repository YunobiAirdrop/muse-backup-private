#!/usr/bin/env python3
"""Observe Multipli auth flow via network interception."""
import os
import subprocess
import time
import json

BASE = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(BASE, "profile")
EXT_DIR = os.path.join(BASE, "ext", "metamask")
CHROME_BIN = os.path.expanduser(
    "~/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome"
)
DISPLAY_NUM = ":99"


def start_xvfb():
    sock = f"/tmp/.X11-unix/X{DISPLAY_NUM.lstrip(':')}"
    if os.path.exists(sock):
        return None
    proc = subprocess.Popen(
        ["Xvfb", DISPLAY_NUM, "-screen", "0", "1280x800x24"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    return proc


def ensure_forwarder():
    import socket as _s
    try:
        _s.create_connection(("127.0.0.1", 3129), timeout=2).close()
        return None
    except Exception:
        pass
    proc = subprocess.Popen(
        [os.path.join(BASE, "venv", "bin", "python"),
         os.path.join(BASE, "forwarder.py")],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    return proc


def main():
    from playwright.sync_api import sync_playwright
    xvfb = start_xvfb()
    fwd = ensure_forwarder()
    os.environ["DISPLAY"] = DISPLAY_NUM

    requests_log = []

    try:
        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(
                PROFILE_DIR, executable_path=CHROME_BIN, headless=False,
                args=[f"--load-extension={EXT_DIR}",
                      f"--disable-extensions-except={EXT_DIR}",
                      "--no-sandbox", "--disable-dev-shm-usage",
                      "--disable-gpu", "--mute-audio",
                      "--proxy-server=http://127.0.0.1:3129",
                      "--ignore-certificate-errors"],
                viewport={"width": 1280, "height": 800})
            time.sleep(3)

            pg = ctx.new_page()

            def on_request(req):
                if "api-testnet.multipli.fi" in req.url:
                    body = ""
                    try:
                        body = (req.post_data or "")[:500]
                    except Exception:
                        pass
                    requests_log.append({
                        "method": req.method,
                        "url": req.url,
                        "body": body,
                    })
                    print(f"[API] {req.method} {req.url[:100]}",
                          flush=True)

            def on_response(resp):
                if "api-testnet.multipli.fi" in resp.url:
                    try:
                        text = resp.text()[:500]
                        print(f"[RESP] {resp.status} {resp.url[:80]}",
                              flush=True)
                        print(f"       {text[:200]}", flush=True)
                    except Exception:
                        pass

            pg.on("request", on_request)
            pg.on("response", on_response)

            try:
                pg.goto("https://testnet.multipli.fi/?referral_code=6RUTJ",
                        wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print("[*] goto:", str(e)[:80], flush=True)
            pg.wait_for_timeout(12000)
            pg.screenshot(path=os.path.join(BASE, "multipli2-1-home.png"))

            # Try clicking Connect Wallet and see what API calls happen
            print("\n[*] Looking for Connect Wallet...", flush=True)
            try:
                btns = pg.get_by_text("Connect Wallet", exact=False)
                print(f"[*] Found {btns.count()} connect buttons", flush=True)
                if btns.count() > 0:
                    btns.first.click(timeout=10000)
                    print("[*] Clicked Connect Wallet", flush=True)
                    pg.wait_for_timeout(5000)
                    pg.screenshot(
                        path=os.path.join(BASE, "multipli2-2-modal.png"))
            except Exception as e:
                print("[*] Connect click:", str(e)[:100], flush=True)

            print("\n[*] API requests captured:", flush=True)
            for r in requests_log:
                print(f"  {r['method']} {r['url']}", flush=True)
                if r['body']:
                    print(f"    body: {r['body'][:200]}", flush=True)

            # Save log
            with open(os.path.join(BASE, "multipli2-api.json"), "w") as f:
                json.dump(requests_log, f, indent=2)

            ctx.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()
        if fwd is not None:
            fwd.terminate()


if __name__ == "__main__":
    main()
