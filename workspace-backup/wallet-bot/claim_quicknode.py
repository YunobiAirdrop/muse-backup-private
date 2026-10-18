#!/usr/bin/env python3
"""
Claim tBNB from QuickNode faucet (no mainnet balance required).
https://faucet.quicknode.com/binance-smart-chain/bnb-testnet
"""
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
WALLET = "0xf0f25C36AC70E9d787a108eFB351626192C8107b"


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

            # Unlock MetaMask.
            mm = ctx.new_page()
            mm.goto(f"chrome-extension://{EXT_ID}/home.html")
            mm.wait_for_timeout(3000)
            try:
                pw = open(PASS_FILE).read().strip()
                inp = mm.locator('input[type="password"]').first
                if inp.is_visible(timeout=8000):
                    inp.fill(pw)
                    mm.get_by_role("button", name="Unlock").first.click()
                    print("[*] MetaMask unlocked.", flush=True)
                    mm.wait_for_timeout(3000)
            except Exception as e:
                print("[*] Unlock skip:", str(e)[:60], flush=True)
            mm.close()

            pg = ctx.new_page()
            try:
                pg.goto("https://faucet.quicknode.com/binance-smart-chain/bnb-testnet",
                        wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print("[*] goto issue:", str(e)[:80], flush=True)
            pg.wait_for_timeout(8000)
            pg.screenshot(path=os.path.join(BASE, "qn-1.png"))
            print("[*] QuickNode loaded:", pg.title(), flush=True)

            # Find address input and fill.
            filled = False
            for sel in ['input[placeholder*="address" i]',
                        'input[placeholder*="0x" i]',
                        'input[type="text"]']:
                try:
                    inp = pg.locator(sel).first
                    if inp.is_visible(timeout=5000):
                        inp.fill(WALLET)
                        print(f"[*] Address filled via {sel}", flush=True)
                        filled = True
                        break
                except Exception:
                    pass
            if not filled:
                print("[!] Address input not found.", flush=True)
                pg.screenshot(path=os.path.join(BASE, "qn-noinput.png"))
            else:
                pg.wait_for_timeout(3000)
                pg.screenshot(path=os.path.join(BASE, "qn-2-filled.png"))
                # Look for submit/claim button.
                for t in ["Send", "Claim", "Drip", "Request", "Submit",
                          "Get tokens", "Continue"]:
                    try:
                        btn = pg.get_by_role("button", name=t).first
                        if btn.is_visible() and not btn.is_disabled():
                            btn.click()
                            print(f"[*] Clicked {t!r}", flush=True)
                            pg.wait_for_timeout(5000)
                            break
                    except Exception:
                        pass
                pg.screenshot(path=os.path.join(BASE, "qn-3-after.png"))
                body = pg.inner_text("body")
                print("[*] Result:", body[:500].replace("\n", " | "),
                      flush=True)
            ctx.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()
        if fwd is not None:
            fwd.terminate()


if __name__ == "__main__":
    main()
