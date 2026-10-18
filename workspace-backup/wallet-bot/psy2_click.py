#!/usr/bin/env python3
"""Click Wallet via JS and capture all network requests."""
import os
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

            # Capture ALL requests.
            reqs = []
            def on_request(req):
                # Skip static assets.
                url = req.url
                if any(x in url for x in
                       ['.js', '.css', '.png', '.woff', '.ico',
                        'google-analytics', 'web3modal.org']):
                    return
                reqs.append(f"{req.method} {url}")
            pg.on("request", on_request)

            try:
                pg.goto("https://psy.xyz/psychonaut?icode=A55VV7D8",
                        wait_until="domcontentloaded", timeout=90000)
            except Exception as e:
                print("[*] goto:", str(e)[:80], flush=True)
            pg.wait_for_timeout(8000)

            # Find and click Wallet via JS.
            result = pg.evaluate("""() => {
                const els = document.querySelectorAll('*');
                for (const el of els) {
                    const t = (el.innerText || '').trim();
                    if (t === 'Wallet' && el.children.length <= 2) {
                        const r = el.getBoundingClientRect();
                        if (r.width > 50 && r.width < 300 &&
                            r.height > 30 && r.height < 150) {
                            el.click();
                            return 'clicked: ' + el.tagName + ' ' +
                                   el.className.substring(0, 50);
                        }
                    }
                }
                return 'not found';
            }""")
            print(f"[*] Click result: {result}", flush=True)
            pg.wait_for_timeout(10000)
            pg.screenshot(path=os.path.join(BASE, "psy2-3-afterclick.png"))

            print("[*] Network requests:", flush=True)
            for r in list(dict.fromkeys(reqs))[:40]:
                print(f"    {r}", flush=True)

            body = pg.inner_text("body")
            print("[*] Body:", body[:800].replace("\n", " | "), flush=True)

            ctx.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()
        if fwd is not None:
            fwd.terminate()
    print("[*] Done", flush=True)


if __name__ == "__main__":
    main()
