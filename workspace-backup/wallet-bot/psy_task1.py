#!/usr/bin/env python3
"""
Task 1: Psychonaut Incubation Program signup.
https://psy.xyz/psychonaut?icode=A55VV7D8
- Connect EVM wallet via window.ethereum
- Email: khususstokyunobi@gmail.com if asked
- Handle: yunobi
- Complete available tasks, screenshot each step (psy-*.png)
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


def unlock_mm(ctx):
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


def approve_mm_popups(ctx, timeout_s=20):
    """Approve any MetaMask notification popups (connect/sign)."""
    deadline = time.time() + timeout_s
    approved = []
    while time.time() < deadline:
        found = False
        for w in ctx.pages:
            if w.url.startswith(f"chrome-extension://{EXT_ID}") and \
                    "notification" in w.url:
                found = True
                w.wait_for_timeout(1500)
                # Check account checkboxes.
                try:
                    for cb in w.locator('input[type="checkbox"]').all():
                        try:
                            if cb.is_visible() and not cb.is_checked():
                                cb.check()
                        except Exception:
                            pass
                except Exception:
                    pass
                # Click action buttons in order.
                for t in ["Next", "Connect", "Confirm", "Sign",
                          "Approve", "Switch network"]:
                    try:
                        el = w.get_by_role("button", name=t).first
                        if el.is_visible() and not el.is_disabled():
                            el.click()
                            approved.append(t)
                            print(f"[*] MM popup: clicked {t!r}", flush=True)
                            w.wait_for_timeout(2000)
                            break
                    except Exception:
                        pass
        if not found:
            break
        time.sleep(1)
    return approved


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
            unlock_mm(ctx)

            pg = ctx.new_page()
            try:
                pg.goto("https://psy.xyz/psychonaut?icode=A55VV7D8",
                        wait_until="domcontentloaded", timeout=90000)
            except Exception as e:
                print("[*] goto:", str(e)[:80], flush=True)
            pg.wait_for_timeout(8000)
            pg.screenshot(path=os.path.join(BASE, "psy-1-landing.png"))
            print("[*] Title:", pg.title(), flush=True)
            print("[*] Body:", pg.inner_text("body")[:700].replace("\n", " | "),
                  flush=True)

            # Step 1: Connect wallet. Look for Wallet button or use ethereum directly.
            has_eth = pg.evaluate(
                "() => typeof window.ethereum !== 'undefined'")
            print("[*] window.ethereum:", has_eth, flush=True)

            # Try clicking a "Wallet" connect option first.
            clicked = False
            for t in ["Wallet", "Connect Wallet", "Connect"]:
                try:
                    el = pg.get_by_text(t, exact=False).first
                    if el.is_visible(timeout=3000):
                        el.click()
                        print(f"[*] Clicked {t!r}", flush=True)
                        pg.wait_for_timeout(2500)
                        clicked = True
                        break
                except Exception:
                    pass
            pg.screenshot(path=os.path.join(BASE, "psy-2-connect.png"))

            # Direct ethereum request as backup/primary.
            try:
                accs = pg.evaluate(
                    """async () => await window.ethereum.request(
                        {method: 'eth_requestAccounts'})""")
                print("[*] eth_requestAccounts:", accs, flush=True)
            except Exception as e:
                print("[*] eth_requestAccounts:", str(e)[:100], flush=True)

            approve_mm_popups(ctx, timeout_s=25)
            pg.wait_for_timeout(3000)
            pg.screenshot(path=os.path.join(BASE, "psy-3-after-connect.png"))
            print("[*] After connect body:",
                  pg.inner_text("body")[:700].replace("\n", " | "), flush=True)

            # Check connected accounts.
            try:
                accs = pg.evaluate(
                    """async () => await window.ethereum.request(
                        {method: 'eth_accounts'})""")
                print("[*] eth_accounts:", accs, flush=True)
            except Exception as e:
                print("[*] eth_accounts err:", str(e)[:80], flush=True)

            # Step 2: Email if asked.
            try:
                email_inp = pg.locator(
                    'input[type="email"], input[placeholder*="mail" i]').first
                if email_inp.is_visible(timeout=5000):
                    email_inp.fill(EMAIL)
                    print("[*] Email filled.", flush=True)
                    pg.wait_for_timeout(1500)
                    pg.screenshot(path=os.path.join(BASE, "psy-4-email.png"))
                    # Look for verify/send code button.
                    for t in ["Verify", "Send code", "Send Code",
                              "Continue", "Next", "Submit"]:
                        try:
                            b = pg.get_by_role("button", name=t).first
                            if b.is_visible() and not b.is_disabled():
                                b.click()
                                print(f"[*] Clicked {t!r}", flush=True)
                                pg.wait_for_timeout(3000)
                                break
                        except Exception:
                            pass
                    print("[*] NOTE: email verification code may be needed "
                          "- check if code input appears.", flush=True)
                    pg.screenshot(path=os.path.join(BASE, "psy-5-email-sent.png"))
            except Exception as e:
                print("[*] Email step:", str(e)[:80], flush=True)

            # Step 3: Handle/username if asked.
            try:
                handle_inp = pg.locator(
                    'input[placeholder*="username" i], '
                    'input[placeholder*="handle" i], '
                    'input[name*="username" i]').first
                if handle_inp.is_visible(timeout=5000):
                    handle_inp.fill(HANDLE)
                    print("[*] Handle filled.", flush=True)
                    pg.wait_for_timeout(1500)
                    for t in ["Continue", "Next", "Submit", "Complete",
                              "Finish", "Save"]:
                        try:
                            b = pg.get_by_role("button", name=t).first
                            if b.is_visible() and not b.is_disabled():
                                b.click()
                                print(f"[*] Clicked {t!r}", flush=True)
                                pg.wait_for_timeout(3000)
                                break
                        except Exception:
                            pass
                    pg.screenshot(path=os.path.join(BASE, "psy-6-handle.png"))
            except Exception as e:
                print("[*] Handle step:", str(e)[:80], flush=True)

            # Step 4: Survey current state — tasks, check-in, etc.
            pg.wait_for_timeout(3000)
            pg.screenshot(path=os.path.join(BASE, "psy-7-dashboard.png"))
            body = pg.inner_text("body")
            print("[*] Dashboard:", body[:1000].replace("\n", " | "), flush=True)

            # Try daily check-in.
            for t in ["Check-in", "Check in", "Daily check-in"]:
                try:
                    b = pg.get_by_text(t, exact=False).first
                    if b.is_visible(timeout=3000):
                        b.click()
                        print(f"[*] Clicked {t!r}", flush=True)
                        pg.wait_for_timeout(3000)
                        approve_mm_popups(ctx, timeout_s=15)
                        break
                except Exception:
                    pass
            pg.screenshot(path=os.path.join(BASE, "psy-8-checkin.png"))

            print("[*] Task 1 script done.", flush=True)
            ctx.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()
        if fwd is not None:
            fwd.terminate()


if __name__ == "__main__":
    main()
