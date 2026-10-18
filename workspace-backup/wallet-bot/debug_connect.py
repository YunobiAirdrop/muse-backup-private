#!/usr/bin/env python3
"""Debug the Multipli Connect Wallet flow."""
import os
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(BASE, "profile")
EXT_DIR = os.path.join(BASE, "ext", "metamask")
PASS_FILE = os.path.join(BASE, ".mm-pass")
CHROME_BIN = os.path.expanduser(
    "~/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome"
)
DISPLAY_NUM = ":99"
EXT_ID = "ocicphjefllmdjaioocoolnmfbjdlcfg"


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
            mm = ctx.new_page()
            mm.goto(f"chrome-extension://{EXT_ID}/home.html")
            mm.wait_for_timeout(3000)
            try:
                pw = open(PASS_FILE).read().strip()
                inp = mm.locator('input[type="password"]').first
                if inp.is_visible(timeout=8000):
                    inp.fill(pw)
                    mm.get_by_role("button", name="Unlock").first.click()
                    mm.wait_for_timeout(3000)
                    print("[*] Unlocked")
            except Exception as e:
                print("[*] Unlock skip:", str(e)[:60])
            mm.close()

            pg = ctx.new_page()
            pg.goto("https://testnet.multipli.fi/?referral_code=6RUTJ")
            pg.wait_for_timeout(5000)

            # Check if window.ethereum is injected.
            has_eth = pg.evaluate(
                "() => typeof window.ethereum !== 'undefined'")
            print("[*] window.ethereum injected:", has_eth)

            # Click Connect Wallet (the main one, top right).
            btns = pg.get_by_text("Connect Wallet", exact=False)
            print("[*] Connect buttons:", btns.count())
            btns.first.click()
            print("[*] Clicked first Connect Wallet")
            pg.wait_for_timeout(3000)
            pg.screenshot(path=os.path.join(BASE, "dbg-modal.png"))

            # Dump visible modal text.
            body = pg.inner_text("body")
            print("[*] Modal body:", body[:800].replace("\n", " | "))
            ctx.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()
        if fwd is not None:
            fwd.terminate()


if __name__ == "__main__":
    main()
