#!/usr/bin/env python3
"""Finish MetaMask onboarding (dismiss biometrics etc.) and verify address."""
import os
import re
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
EXPECTED = "0xf0f25c36ac70e9d787a108efb351626192c8107b"


def start_xvfb():
    sock = f"/tmp/.X11-unix/X{DISPLAY_NUM.lstrip(':')}"
    if os.path.exists(sock):
        return None
    proc = subprocess.Popen(
        ["Xvfb", DISPLAY_NUM, "-screen", "0", "1280x800x24"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    return proc


def main():
    from playwright.sync_api import sync_playwright
    xvfb = start_xvfb()
    os.environ["DISPLAY"] = DISPLAY_NUM
    try:
        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(
                PROFILE_DIR, executable_path=CHROME_BIN, headless=False,
                args=[f"--load-extension={EXT_DIR}",
                      f"--disable-extensions-except={EXT_DIR}",
                      "--no-sandbox", "--disable-dev-shm-usage",
                      "--disable-gpu", "--mute-audio"],
                viewport={"width": 1280, "height": 800})
            time.sleep(4)
            ext_id = "ocicphjefllmdjaioocoolnmfbjdlcfg"
            pg = ctx.new_page()
            pg.goto(f"chrome-extension://{ext_id}/home.html")
            pg.wait_for_timeout(4000)

            # Unlock if locked.
            try:
                pw = open(os.path.join(BASE, ".mm-pass")).read().strip()
                unlock_input = pg.locator(
                    'input[type="password"]').first
                if unlock_input.is_visible(timeout=5000):
                    unlock_input.fill(pw)
                    pg.get_by_role("button", name="Unlock").first.click()
                    print("[*] Vault unlocked.")
                    pg.wait_for_timeout(3000)
            except Exception as e:
                print(f"[*] Unlock step skipped/failed: {str(e)[:80]}")

            # "Help improve MetaMask": opt out of data collection, Continue.
            try:
                el = pg.get_by_text("Gather basic usage data",
                                    exact=False).first
                if el.is_visible(timeout=5000):
                    el.click()
                    print("[*] Opted out of usage data.")
                    pg.wait_for_timeout(1000)
            except Exception:
                pass

            # Dismiss optional screens.
            for _ in range(8):
                dismissed = False
                for t in ["Open wallet", "Maybe later", "Not now", "Skip",
                          "Got it", "OK", "Done", "No thanks", "Continue",
                          "Get started"]:
                    try:
                        el = pg.get_by_text(t, exact=False).first
                        if el.is_visible():
                            el.click()
                            print(f"[*] Dismissed: {t!r}")
                            dismissed = True
                            pg.wait_for_timeout(1500)
                            break
                    except Exception:
                        pass
                if not dismissed:
                    break

            pg.wait_for_timeout(3000)
            body = pg.inner_text("body")
            # Look for full or truncated address.
            m = re.search(r"0x[a-fA-F0-9]{40}", body)
            if m:
                addr = m.group(0)
                print(f"[*] Address on screen: {addr}")
                print("[OK] MATCH" if addr.lower() == EXPECTED
                      else "[WARN] MISMATCH")
            else:
                m2 = re.search(r"0x[a-fA-F0-9]{4}\.\.\.[a-fA-F0-9]{4}", body)
                print("[*] Truncated address:", m2.group(0) if m2 else None)
                print("[*] Body head:", body[:400].replace("\n", " | "))
            pg.screenshot(path=os.path.join(BASE, "wallet-ready.png"))
            print("[*] Screenshot: wallet-ready.png")
            ctx.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()


if __name__ == "__main__":
    main()
