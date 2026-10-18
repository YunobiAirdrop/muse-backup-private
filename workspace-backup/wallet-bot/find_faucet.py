#!/usr/bin/env python3
"""Find the Multipli faucet contract by inspecting the site."""
import os
import re
import subprocess
import sys
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

    api_calls = []
    contracts = set()

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

            # Capture network requests that look like API/faucet calls.
            def on_request(req):
                url = req.url
                if any(k in url.lower() for k in
                       ["faucet", "claim", "drip", "api"]):
                    api_calls.append(f"{req.method} {url}")
                # Look for contract addresses in request bodies.
                try:
                    post = req.post_data or ""
                    for m in re.findall(r"0x[a-fA-F0-9]{40}", post):
                        contracts.add(m)
                except Exception:
                    pass

            pg.on("request", on_request)

            try:
                pg.goto("https://testnet.multipli.fi/?referral_code=6RUTJ",
                        wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print("[*] goto:", str(e)[:80], flush=True)
            pg.wait_for_timeout(10000)
            pg.screenshot(path=os.path.join(BASE, "multipli2-1-home.png"))

            # Dump page source for contract addresses and faucet hints.
            html = pg.content()
            for m in set(re.findall(r"0x[a-fA-F0-9]{40}", html)):
                contracts.add(m)

            # Look for faucet-related text/buttons.
            body = pg.inner_text("body")
            print("[*] Body has 'faucet':", "faucet" in body.lower(), flush=True)
            print("[*] Body has 'claim':", "claim" in body.lower(), flush=True)

            # Search all JS for faucet endpoints.
            scripts = pg.eval_on_selector_all(
                "script[src]", "els => els.map(e => e.src)")
            print(f"[*] {len(scripts)} external scripts", flush=True)

            # Check for faucet links/nav.
            for t in ["Faucet", "faucet", "Get Test Tokens", "Test Tokens"]:
                try:
                    el = pg.get_by_text(t, exact=False).first
                    if el.is_visible(timeout=3000):
                        print(f"[*] Found text: {t!r}", flush=True)
                        href = el.get_attribute("href")
                        if href:
                            print(f"    href: {href}", flush=True)
                except Exception:
                    pass

            print("\n[*] API-like calls:", flush=True)
            for c in api_calls[:20]:
                print("   ", c, flush=True)

            print("\n[*] Contract addresses found:", flush=True)
            for c in sorted(contracts):
                print("   ", c, flush=True)

            # Save full HTML for offline analysis.
            with open(os.path.join(BASE, "multipli2-page.html"), "w") as f:
                f.write(html)
            print("\n[*] HTML saved.", flush=True)

            ctx.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()
        if fwd is not None:
            fwd.terminate()


if __name__ == "__main__":
    main()
