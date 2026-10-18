#!/usr/bin/env python3
"""Click Wallet button on Psy signup and observe the flow."""
import os
import subprocess
import sys
import time
import re

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
            time.sleep(4)
            pg = ctx.new_page()

            # Capture network requests to find the API.
            api_calls = []
            def on_request(req):
                url = req.url
                if any(k in url for k in
                       ['api', 'auth', 'signin', 'nonce', 'verify',
                        'psychonaut', 'wallet']):
                    api_calls.append(f"{req.method} {url}")
            pg.on("request", on_request)

            try:
                pg.goto("https://psy.xyz/psychonaut?icode=A55VV7D8",
                        wait_until="domcontentloaded", timeout=90000)
            except Exception as e:
                print("[*] goto:", str(e)[:80], flush=True)
            pg.wait_for_timeout(8000)

            # Click the Wallet button.
            wallet_btn = pg.get_by_text("Wallet", exact=True).first
            # There might be multiple "Wallet" texts; find the button one.
            # From screenshot, it's a button with wallet icon.
            # Let's try clicking via role.
            clicked = False
            for b in pg.get_by_role("button").all():
                try:
                    if "wallet" in b.inner_text().lower() and b.is_visible():
                        b.click()
                        print("[*] Clicked Wallet button", flush=True)
                        clicked = True
                        break
                except Exception:
                    pass
            if not clicked:
                print("[!] Wallet button not found", flush=True)

            pg.wait_for_timeout(8000)
            pg.screenshot(path=os.path.join(BASE, "psy2-2-wallet.png"))
            print("[*] Screenshot: psy2-2-wallet.png", flush=True)

            body = pg.inner_text("body")
            print("[*] Body after click:",
                  body[:1000].replace("\n", " | "), flush=True)

            print("[*] API calls captured:", flush=True)
            for c in list(dict.fromkeys(api_calls))[:30]:
                print(f"    {c}", flush=True)

            # Check for signature request in page JS.
            # Look for any modal or message.
            html = pg.content()
            # Find any SIWE-like message or signature prompt.
            if "sign" in html.lower():
                idx = html.lower().find("sign")
                print("[*] 'sign' context:",
                      html[max(0,idx-200):idx+300][:500], flush=True)

            ctx.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()
        if fwd is not None:
            fwd.terminate()
    print("[*] Done", flush=True)


if __name__ == "__main__":
    main()
