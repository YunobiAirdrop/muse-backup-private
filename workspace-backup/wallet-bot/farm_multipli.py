#!/usr/bin/env python3
"""
Claim Multipli testnet faucet (USDC/USDT/BTC) with the farming wallet.

Prereq: wallet already imported (see import_wallet.py).
Unlocks MetaMask via ~/workspace/wallet-bot/.mm-pass, connects to
testnet.multipli.fi, claims all available faucet tokens.
"""
import os
import re
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
    """Start the local TCP forwarder (127.0.0.1:3129 -> egress proxy)."""
    import socket as _s
    try:
        _s.create_connection(("127.0.0.1", 3129), timeout=2).close()
        print("[*] Forwarder already running.")
        return None
    except Exception:
        pass
    proc = subprocess.Popen(
        [os.path.join(BASE, "venv", "bin", "python"),
         os.path.join(BASE, "forwarder.py")],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    print("[*] Forwarder started.")
    return proc


def unlock_metamask(page):
    pw = open(PASS_FILE).read().strip()
    try:
        inp = page.locator('input[type="password"]').first
        if inp.is_visible(timeout=8000):
            inp.fill(pw)
            page.get_by_role("button", name="Unlock").first.click()
            print("[*] MetaMask unlocked.")
            page.wait_for_timeout(3000)
            return True
    except Exception as e:
        print(f"[*] Unlock not needed/failed: {str(e)[:60]}")
    return False


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

            # Unlock MetaMask in its own tab.
            mm = ctx.new_page()
            mm.goto(f"chrome-extension://{EXT_ID}/home.html")
            mm.wait_for_timeout(3000)
            unlock_metamask(mm)
            mm.close()

            # Open Multipli (tolerant of slow SPA load).
            pg = ctx.new_page()
            try:
                pg.goto("https://testnet.multipli.fi/?referral_code=6RUTJ",
                        wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print("[*] goto timeout (continuing):", str(e)[:80])
            pg.wait_for_timeout(8000)
            pg.screenshot(path=os.path.join(BASE, "multipli-1-home.png"))
            print("[*] Multipli loaded:", pg.title())

            # Connect wallet via direct ethereum call (more reliable).
            connected = False
            has_eth = pg.evaluate(
                "() => typeof window.ethereum !== 'undefined'")
            print("[*] window.ethereum:", has_eth)
            if has_eth:
                try:
                    accounts = pg.evaluate(
                        """async () => {
                            const accs = await window.ethereum.request(
                                {method: 'eth_requestAccounts'});
                            return accs;
                        }""")
                    print("[*] eth_requestAccounts:", accounts)
                except Exception as e:
                    print("[*] eth_requestAccounts error (popup?):",
                          str(e)[:120])

            # Approve connection in MetaMask popup.
            pg.wait_for_timeout(4000)
            for w in ctx.pages:
                if w.url.startswith(f"chrome-extension://{EXT_ID}"):
                    print("[*] MM window:", w.url[:100])
                    w.wait_for_timeout(2000)
                    # Check all checkboxes (account selection).
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
                    for t in ["Next", "Connect", "Confirm", "Approve"]:
                        try:
                            el = w.get_by_role("button", name=t).first
                            if el.is_visible() and not el.is_disabled():
                                el.click()
                                print(f"[*] Popup: clicked {t!r}")
                                w.wait_for_timeout(2500)
                                break
                        except Exception:
                            pass
            pg.wait_for_timeout(3000)

            # Verify connected accounts.
            try:
                accounts = pg.evaluate(
                    """async () => {
                        return await window.ethereum.request(
                            {method: 'eth_accounts'});
                    }""")
                print("[*] eth_accounts:", accounts)
                if accounts and accounts[0].lower() == EXPECTED:
                    print("[OK] Farming wallet connected.")
                    connected = True
            except Exception as e:
                print("[*] eth_accounts error:", str(e)[:80])
            pg.screenshot(path=os.path.join(BASE, "multipli-2-connected.png"))

            # Find and click faucet/claim buttons.
            claimed = []
            for _ in range(6):  # up to 6 claim actions
                found = False
                for t in ["Claim", "Faucet", "Get test tokens",
                          "Request tokens", "Mint"]:
                    try:
                        els = pg.get_by_text(t, exact=False).all()
                        for el in els:
                            if el.is_visible() and el.is_enabled():
                                el.click()
                                print(f"[*] Clicked {t!r}")
                                pg.wait_for_timeout(4000)
                                # Approve tx in MetaMask popup if any.
                                for w in ctx.pages:
                                    if w.url.startswith(
                                        f"chrome-extension://{EXT_ID}") \
                                            and "notification" in w.url:
                                        w.wait_for_timeout(2000)
                                        for ct in ["Confirm", "Approve"]:
                                            try:
                                                b = w.get_by_role(
                                                    "button",
                                                    name=ct).first
                                                if b.is_visible():
                                                    b.click()
                                                    print("[*] Tx confirmed.")
                                                    break
                                            except Exception:
                                                pass
                                claimed.append(t)
                                found = True
                                break
                        if found:
                            break
                    except Exception:
                        pass
                if not found:
                    break
                pg.wait_for_timeout(2000)

            pg.screenshot(path=os.path.join(BASE, "multipli-3-done.png"))
            print(f"[*] Claim actions attempted: {claimed}")
            print("[*] Done.")
            ctx.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()
        if fwd is not None:
            fwd.terminate()


if __name__ == "__main__":
    main()
