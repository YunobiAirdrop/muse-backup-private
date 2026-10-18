#!/usr/bin/env python3
"""
Independent Chromium + MetaMask automation environment.

SEPARATE from the runtime's managed browser (which has extensions blocked).
Everything lives under ~/workspace/wallet-bot/.

Usage:
    ./venv/bin/python launch.py            # launch, screenshot MetaMask onboarding, exit
    ./venv/bin/python launch.py --keep-alive  # launch and keep running (Ctrl+C to stop)

Profile persists at ~/workspace/wallet-bot/profile/ so the wallet import
(done later, manually) survives restarts. NO seed phrase or private key is
ever written by this script.
"""
import os
import re
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(BASE, "profile")
EXT_DIR = os.path.join(BASE, "ext", "metamask")
PROOF_PNG = os.path.join(BASE, "proof-metamask.png")
CHROME_BIN = os.path.expanduser(
    "~/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome"
)
DISPLAY_NUM = ":99"


def start_xvfb():
    """Start Xvfb on DISPLAY_NUM if not already running."""
    sock = f"/tmp/.X11-unix/X{DISPLAY_NUM.lstrip(':')}"
    if os.path.exists(sock):
        print(f"[x] Xvfb already running on {DISPLAY_NUM}")
        return None
    print(f"[x] Starting Xvfb on {DISPLAY_NUM} ...")
    proc = subprocess.Popen(
        ["Xvfb", DISPLAY_NUM, "-screen", "0", "1280x800x24"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    return proc


def find_extension_id(context, timeout=30):
    """Discover the loaded MetaMask extension id via service workers/pages,
    falling back to the profile's Preferences file."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        for sw in context.service_workers:
            m = re.match(r"chrome-extension://([a-p]{32})/", sw.url)
            if m:
                return m.group(1)
        for page in context.pages:
            m = re.match(r"chrome-extension://([a-p]{32})/", page.url)
            if m:
                return m.group(1)
        time.sleep(0.5)
    # Fallback: read from profile Preferences (id is stable per profile+path)
    try:
        import json

        prefs = json.load(
            open(os.path.join(PROFILE_DIR, "Default", "Preferences"))
        )
        for ext_id, info in (
            prefs.get("extensions", {}).get("settings", {}).items()
        ):
            if (info.get("path") or "").startswith(EXT_DIR):
                return ext_id
    except Exception:
        pass
    return None


def main():
    from playwright.sync_api import sync_playwright

    if not os.path.isdir(EXT_DIR):
        sys.exit(f"Extension dir missing: {EXT_DIR}")
    if not os.path.isfile(CHROME_BIN):
        sys.exit(f"Chromium binary missing: {CHROME_BIN}")

    os.makedirs(PROFILE_DIR, exist_ok=True)
    xvfb = start_xvfb()
    os.environ["DISPLAY"] = DISPLAY_NUM

    keep_alive = "--keep-alive" in sys.argv

    with sync_playwright() as p:
        print("[*] Launching Chromium (headed under Xvfb) with MetaMask ...")
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            executable_path=CHROME_BIN,
            headless=False,
            args=[
                f"--load-extension={EXT_DIR}",
                f"--disable-extensions-except={EXT_DIR}",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--mute-audio",
            ],
            viewport={"width": 1280, "height": 800},
            # Do NOT set a proxy: use the VM's direct egress.
            ignore_https_errors=False,
        )
        print("[*] Browser launched. Waiting for MetaMask ...")
        time.sleep(4)

        ext_id = find_extension_id(context)
        if not ext_id:
            print("[!] Could not detect MetaMask extension id; screenshotting first tab.")
            page = context.pages[0] if context.pages else context.new_page()
        else:
            print(f"[*] MetaMask extension id: {ext_id}")
            url = f"chrome-extension://{ext_id}/home.html"
            page = None
            for pg in context.pages:
                if pg.url.startswith(f"chrome-extension://{ext_id}"):
                    page = pg
                    break
            if page is None:
                page = context.new_page()
                page.goto(url)
            else:
                print(f"[*] MetaMask already open at: {page.url}")

        page.wait_for_timeout(3000)
        page.screenshot(path=PROOF_PNG)
        print(f"[*] Screenshot saved: {PROOF_PNG}")
        print(f"[*] Page title: {page.title()!r}  url: {page.url[:80]}")

        if keep_alive:
            print("[*] Keep-alive mode: browser stays open. Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(10)
            except KeyboardInterrupt:
                print("\n[*] Stopping ...")
        context.close()

    if xvfb is not None and not keep_alive:
        xvfb.terminate()
        print("[x] Xvfb stopped.")


if __name__ == "__main__":
    main()
