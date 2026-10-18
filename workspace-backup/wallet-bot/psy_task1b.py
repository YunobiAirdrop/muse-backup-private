#!/usr/bin/env python3
"""
Task 1 (fixed): Psychonaut signup without blocking on eth_requestAccounts.
- Click the site's Wallet button (non-blocking)
- Poll for MetaMask popup and approve
- Verify via eth_accounts
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
EMAIL = "khususstokyunobi@gmail.com"
HANDLE = "yunobi"


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
                pg.goto("https://psy.xyz/psychonaut?icode=A55VV7D8",
                        wait_until="domcontentloaded", timeout=90000)
            except Exception as e:
                print("[*] goto:", str(e)[:80], flush=True)
            pg.wait_for_timeout(8000)

            has_eth = pg.evaluate(
                "() => typeof window.ethereum !== 'undefined'")
            print("[*] window.ethereum:", has_eth, flush=True)

            # Click the site's Wallet button (non-blocking).
            # Find the Wallet button specifically (not the text in OR section).
            wallet_btn = None
            try:
                # The Wallet option is a button with wallet icon.
                btns = pg.locator("button").all()
                for b in btns:
                    try:
                        txt = b.inner_text().strip()
                        if txt == "Wallet":
                            wallet_btn = b
                            break
                    except Exception:
                        pass
            except Exception:
                pass

            if wallet_btn:
                wallet_btn.click()
                print("[*] Clicked Wallet button.", flush=True)
            else:
                print("[!] Wallet button not found.", flush=True)
            pg.wait_for_timeout(3000)
            pg.screenshot(path=os.path.join(BASE, "psy-2b-wallet-click.png"))

            # Poll for MetaMask popup and approve (up to 60s).
            print("[*] Waiting for MetaMask popup...", flush=True)
            approved = False
            for _ in range(30):
                for w in ctx.pages:
                    url = w.url
                    if url.startswith(f"chrome-extension://{EXT_ID}"):
                        print(f"[*] MM page: {url[:110]}", flush=True)
                        if "notification" in url:
                            w.wait_for_timeout(2000)
                            # Screenshot the popup.
                            try:
                                w.screenshot(path=os.path.join(
                                    BASE, "psy-popup.png"))
                            except Exception:
                                pass
                            # Checkboxes.
                            try:
                                for cb in w.locator(
                                        'input[type="checkbox"]').all():
                                    try:
                                        if cb.is_visible() and not cb.is_checked():
                                            cb.check()
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                            # Buttons.
                            for t in ["Next", "Connect", "Confirm",
                                      "Sign", "Approve"]:
                                try:
                                    el = w.get_by_role("button", name=t).first
                                    if el.is_visible(timeout=3000) and \
                                            not el.is_disabled():
                                        el.click()
                                        print(f"[*] Approved: {t!r}",
                                              flush=True)
                                        approved = True
                                        w.wait_for_timeout(2500)
                                        break
                                except Exception:
                                    pass
                # Check if popup is gone (approved).
                popup_gone = True
                for w in ctx.pages:
                    if w.url.startswith(f"chrome-extension://{EXT_ID}") and \
                            "notification" in w.url:
                        popup_gone = False
                        break
                if popup_gone and approved:
                    print("[*] Popup resolved.", flush=True)
                    break
                time.sleep(2)

            # Final check via async evaluate.
            try:
                accs = pg.evaluate(
                    """async () => await window.ethereum.request(
                        {method: 'eth_accounts'})""")
                print("[*] eth_accounts:", accs, flush=True)
                if accs and accs[0].lower() == EXPECTED:
                    print("[OK] Wallet connected.", flush=True)
            except Exception as e:
                print("[*] eth_accounts:", str(e)[:80], flush=True)

            pg.screenshot(path=os.path.join(BASE, "psy-3-connected.png"))
            print("[*] Body:", pg.inner_text("body")[:800].replace("\n", " | "),
                  flush=True)
            ctx.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()
        if fwd is not None:
            fwd.terminate()


if __name__ == "__main__":
    main()
