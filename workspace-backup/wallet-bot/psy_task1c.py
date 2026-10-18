#!/usr/bin/env python3
"""
Task 1 (v3): Robust Psychonaut wallet connection.
- Better unlock verification
- Better wallet button detection
"""
import os
import subprocess
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


def unlock_mm(ctx):
    """Unlock MetaMask and VERIFY it's unlocked."""
    mm = ctx.new_page()
    mm.goto(f"chrome-extension://{EXT_ID}/home.html")
    mm.wait_for_timeout(4000)
    pw = open(PASS_FILE).read().strip()
    for attempt in range(3):
        try:
            # Check if already unlocked (no password input).
            inp = mm.locator('input[type="password"]').first
            if not inp.is_visible(timeout=3000):
                print("[*] MetaMask already unlocked.", flush=True)
                return mm  # Keep open for debugging.
            inp.fill(pw)
            mm.wait_for_timeout(1000)
            unlock_btn = mm.get_by_role("button", name="Unlock").first
            if unlock_btn.is_visible(timeout=3000):
                unlock_btn.click()
                print(f"[*] Unlock clicked (attempt {attempt+1}).", flush=True)
            mm.wait_for_timeout(4000)
            # Verify: password input should be gone.
            if not mm.locator('input[type="password"]').first.is_visible(
                    timeout=3000):
                print("[*] MetaMask unlocked (verified).", flush=True)
                return mm
        except Exception as e:
            print(f"[*] Unlock attempt {attempt+1}: {str(e)[:60]}", flush=True)
            mm.wait_for_timeout(2000)
    print("[!] Unlock may have failed.", flush=True)
    mm.screenshot(path=os.path.join(BASE, "psy-unlock-fail.png"))
    return mm


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
            mm_page = unlock_mm(ctx)

            pg = ctx.new_page()
            try:
                pg.goto("https://psy.xyz/psychonaut?icode=A55VV7D8",
                        wait_until="domcontentloaded", timeout=90000)
            except Exception as e:
                print("[*] goto:", str(e)[:80], flush=True)
            pg.wait_for_timeout(10000)
            pg.screenshot(path=os.path.join(BASE, "psy-v3-landing.png"))

            # Find Wallet button - wait and try multiple strategies.
            wallet_btn = None
            for attempt in range(5):
                try:
                    # Strategy 1: button with exact "Wallet" text.
                    btns = pg.locator("button").all()
                    print(f"[*] Found {len(btns)} buttons.", flush=True)
                    for b in btns:
                        try:
                            txt = b.inner_text().strip()
                            if txt == "Wallet":
                                wallet_btn = b
                                print("[*] Found Wallet button.", flush=True)
                                break
                        except Exception:
                            pass
                    if wallet_btn:
                        break
                    # Strategy 2: get_by_role.
                    try:
                        el = pg.get_by_role("button", name="Wallet").first
                        if el.is_visible(timeout=2000):
                            wallet_btn = el
                            print("[*] Found via role.", flush=True)
                            break
                    except Exception:
                        pass
                except Exception as e:
                    print(f"[*] Button search {attempt}: {str(e)[:40]}",
                          flush=True)
                pg.wait_for_timeout(2000)

            if wallet_btn:
                wallet_btn.click()
                print("[*] Wallet clicked.", flush=True)
                pg.wait_for_timeout(4000)
            else:
                print("[!] Wallet button not found after retries.", flush=True)
            pg.screenshot(path=os.path.join(BASE, "psy-v3-clicked.png"))

            # Approve MetaMask popup.
            print("[*] Approving popups...", flush=True)
            for _ in range(20):
                handled = False
                for w in ctx.pages:
                    url = w.url
                    if url.startswith(f"chrome-extension://{EXT_ID}") and \
                            "notification" in url:
                        print(f"[*] Popup: {url[:100]}", flush=True)
                        w.wait_for_timeout(2000)
                        try:
                            w.screenshot(path=os.path.join(
                                BASE, "psy-v3-popup.png"))
                        except Exception:
                            pass
                        # Select all accounts.
                        try:
                            for cb in w.locator(
                                    'input[type="checkbox"]').all():
                                try:
                                    if cb.is_visible(timeout=2000) and \
                                            not cb.is_checked():
                                        cb.check()
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        for t in ["Next", "Connect", "Confirm", "Sign"]:
                            try:
                                el = w.get_by_role("button", name=t).first
                                if el.is_visible(timeout=3000) and \
                                        not el.is_disabled():
                                    el.click()
                                    print(f"[*] Clicked {t!r}", flush=True)
                                    handled = True
                                    w.wait_for_timeout(3000)
                                    break
                            except Exception:
                                pass
                if not handled:
                    time.sleep(2)
                # Check connection.
                try:
                    accs = pg.evaluate(
                        """async () => await window.ethereum.request(
                            {method: 'eth_accounts'})""")
                    if accs:
                        print(f"[*] Connected: {accs}", flush=True)
                        break
                except Exception:
                    pass

            # Final verification.
            try:
                accs = pg.evaluate(
                    """async () => await window.ethereum.request(
                        {method: 'eth_accounts'})""")
                print("[*] Final eth_accounts:", accs, flush=True)
                if accs and accs[0].lower() == EXPECTED:
                    print("[OK] Farming wallet connected!", flush=True)
                else:
                    print("[!] Not connected or wrong account.", flush=True)
            except Exception as e:
                print("[!] eth_accounts failed:", str(e)[:80], flush=True)

            pg.screenshot(path=os.path.join(BASE, "psy-v3-final.png"))
            print("[*] Final body:", pg.inner_text("body")[:900].replace(
                "\n", " | "), flush=True)
            ctx.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()
        if fwd is not None:
            fwd.terminate()


if __name__ == "__main__":
    main()
