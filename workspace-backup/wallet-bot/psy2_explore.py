#!/usr/bin/env python3
"""Explore Psy Psychonaut signup page structure."""
import os
import subprocess
import sys
import time

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
            try:
                pg.goto("https://psy.xyz/psychonaut?icode=A55VV7D8",
                        wait_until="domcontentloaded", timeout=90000)
            except Exception as e:
                print("[*] goto:", str(e)[:80], flush=True)
            pg.wait_for_timeout(10000)
            print("[*] Title:", pg.title(), flush=True)
            print("[*] URL:", pg.url[:120], flush=True)

            # Check ethereum injection
            has_eth = pg.evaluate(
                "() => typeof window.ethereum !== 'undefined'")
            print("[*] window.ethereum:", has_eth, flush=True)

            # Dump body text
            body = pg.inner_text("body")
            print("[*] Body:", body[:1500].replace("\n", " | "), flush=True)

            # Find buttons
            btns = pg.locator("button")
            print(f"[*] Buttons: {btns.count()}", flush=True)
            for i in range(min(15, btns.count())):
                try:
                    b = btns.nth(i)
                    print(f"  [{i}] {b.inner_text()[:60]!r} "
                          f"vis={b.is_visible()}", flush=True)
                except Exception:
                    pass

            pg.screenshot(path=os.path.join(BASE, "psy2-1-landing.png"))
            print("[*] Screenshot: psy2-1-landing.png", flush=True)

            # Look for wallet connect option - get page HTML for API endpoints
            html = pg.content()
            # Look for API URLs, contract addresses
            import re
            apis = re.findall(r'https?://[a-zA-Z0-9\-\.]+(?:\.[a-z]+)+(?::\d+)?(?:/[a-zA-Z0-9\-_\./\?=&%]*)?', html)
            interesting = [u for u in apis if any(k in u.lower() for k in
                           ['api', 'psychonaut', 'psy.xyz', 'auth', 'signin'])]
            print("[*] Interesting URLs:", flush=True)
            for u in list(dict.fromkeys(interesting))[:20]:
                print(f"    {u}", flush=True)

            ctx.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()
        if fwd is not None:
            fwd.terminate()
    print("[*] Done", flush=True)


if __name__ == "__main__":
    main()
