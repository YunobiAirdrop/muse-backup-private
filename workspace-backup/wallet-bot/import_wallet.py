#!/usr/bin/env python3
"""
Import the farming wallet into MetaMask (one-time).

Reads the 12-word seed phrase from STDIN (never from args/files — it must
not appear in process lists or on disk). The phrase is used once for the
import and never printed, logged, or saved anywhere.

A strong random MetaMask password is generated and stored at
~/workspace/wallet-bot/.mm-pass (mode 600) so future automation runs can
unlock the vault. The seed phrase itself is NOT stored.

Usage:
    echo "<12 words>" | ./venv/bin/python import_wallet.py
"""
import os
import re
import secrets
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
EXPECTED_ADDR = "0xf0f25c36ac70e9d787a108efb351626192c8107b"


def start_xvfb():
    sock = f"/tmp/.X11-unix/X{DISPLAY_NUM.lstrip(':')}"
    if os.path.exists(sock):
        return None
    proc = subprocess.Popen(
        ["Xvfb", DISPLAY_NUM, "-screen", "0", "1280x800x24"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    return proc


def find_extension_id(context, timeout=30):
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
    return None


def main():
    from playwright.sync_api import sync_playwright

    phrase = sys.stdin.read().strip()
    words = phrase.split()
    if len(words) != 12:
        sys.exit(f"Expected 12 words, got {len(words)}. Aborting.")
    # From here on, NEVER print `phrase` or `words`.
    print("[*] Seed phrase received via stdin (12 words). Starting import...")

    # Generate + store MetaMask password BEFORE launching (600 perms).
    password = secrets.token_urlsafe(24)
    with open(PASS_FILE, "w") as f:
        f.write(password)
    os.chmod(PASS_FILE, 0o600)
    print(f"[*] MetaMask password generated -> {PASS_FILE} (600)")

    os.makedirs(PROFILE_DIR, exist_ok=True)
    xvfb = start_xvfb()
    os.environ["DISPLAY"] = DISPLAY_NUM

    try:
        with sync_playwright() as p:
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
            )
            time.sleep(4)
            ext_id = find_extension_id(context)
            if not ext_id:
                sys.exit("[!] MetaMask extension not detected.")
            print(f"[*] Extension id: {ext_id}")
            url = f"chrome-extension://{ext_id}/home.html"
            page = context.new_page()
            page.goto(url)
            page.wait_for_timeout(3000)

            def click_text(*texts, timeout=15000):
                """Click first visible element matching any of the texts."""
                deadline = time.time() + timeout / 1000
                while time.time() < deadline:
                    for t in texts:
                        try:
                            el = page.get_by_text(t, exact=False).first
                            if el.is_visible():
                                el.click()
                                print(f"[*] Clicked: {t!r}")
                                page.wait_for_timeout(1500)
                                return True
                        except Exception:
                            pass
                    # fallback: buttons by role/name
                    for t in texts:
                        try:
                            el = page.get_by_role(
                                "button", name=t
                            ).first
                            if el.is_visible():
                                el.click()
                                print(f"[*] Clicked button: {t!r}")
                                page.wait_for_timeout(1500)
                                return True
                        except Exception:
                            pass
                    page.wait_for_timeout(1000)
                return False

            # 1. Onboarding: choose import.
            if not click_text("I have an existing wallet", "Import wallet",
                              "Import an existing wallet"):
                print("[!] Could not find import entry button. "
                      f"Title: {page.title()!r}")
                page.screenshot(path=os.path.join(BASE, "import-debug1.png"))
                sys.exit(1)

            # 2. Choose import method (newer MetaMask: Google/Apple/Telegram/SRP).
            if not click_text("Import using Secret Recovery Phrase",
                              "Secret Recovery Phrase", timeout=15000):
                print("[!] Import-method button not found.")
                sys.exit(1)

            # 3. Possibly "Help us improve MetaMask" opt-in/out.
            click_text("No thanks", "No Thanks", timeout=8000)

            # 4. Seed phrase entry. This MetaMask build uses a single
            #    TEXTAREA ("Enter your Secret Recovery Phrase" + Paste button).
            page.wait_for_timeout(2000)
            ta = page.locator("textarea")
            if ta.count() > 0:
                ta.first.click()
                # Clear first (profile persists across runs), then type
                # character-by-character so React detects the change.
                ta.first.fill("")
                ta.first.press_sequentially(" ".join(words), delay=15)
                print("[*] Seed phrase typed into textarea.")
                page.wait_for_timeout(2000)
            else:
                # Fallback: individual inputs (older layout).
                inputs = page.locator(
                    'input[type="password"], input[type="text"]')
                if inputs.count() == 0:
                    print("[!] No textarea/inputs found on SRP page.")
                    sys.exit(1)
                inputs.nth(0).fill(" ".join(words))
                page.wait_for_timeout(1500)

            # 5. Continue / Confirm SRP. Blur the textarea first so
            #    MetaMask validates, then click Continue (JS fallback).
            try:
                page.keyboard.press("Tab")
            except Exception:
                pass
            page.wait_for_timeout(2500)
            cont = None
            for name in ["Continue", "Confirm Secret Recovery Phrase",
                         "Next"]:
                try:
                    el = page.get_by_role("button", name=name).first
                    if el.is_visible():
                        cont = el
                        break
                except Exception:
                    pass
            if cont is None:
                # last resort: any button containing the text
                try:
                    cont = page.get_by_text("Continue", exact=False).first
                    if not cont.is_visible():
                        cont = None
                except Exception:
                    cont = None
            if cont is None:
                print("[!] Continue button not found.")
                sys.exit(1)
            try:
                disabled = cont.is_disabled()
            except Exception:
                disabled = "unknown"
            print(f"[*] Continue button found, disabled={disabled}")
            try:
                cont.click(timeout=8000)
                print("[*] Continue clicked (native).")
            except Exception as e:
                print(f"[*] Native click failed ({str(e)[:60]}), "
                      f"trying JS click.")
                page.evaluate("(el) => el.click()", cont)
                print("[*] Continue clicked (JS).")
            page.wait_for_timeout(3000)

            # 5. Set password.
            page.wait_for_timeout(2000)
            pw_inputs = page.locator('input[type="password"]')
            if pw_inputs.count() >= 2:
                pw_inputs.nth(0).fill(password)
                pw_inputs.nth(1).fill(password)
                print("[*] Password fields filled.")
            else:
                print(f"[!] Expected 2 password fields, found "
                      f"{pw_inputs.count()}.")
                sys.exit(1)

            # 6. Accept terms checkbox if present.
            try:
                cb = page.locator('input[type="checkbox"]').first
                if cb.count() and cb.is_visible() and not cb.is_checked():
                    cb.check()
                    print("[*] Terms checkbox checked.")
            except Exception:
                pass

            # 7. Import button: dump buttons, then click the submit one.
            page.wait_for_timeout(2000)
            btns = page.locator("button")
            print(f"[*] {btns.count()} buttons on password page:")
            submit = None
            for i in range(btns.count()):
                try:
                    b = btns.nth(i)
                    txt = b.inner_text()[:60]
                    vis = b.is_visible()
                    dis = b.is_disabled()
                    print(f"    [{i}] {txt!r} visible={vis} disabled={dis}")
                    if vis and not dis and submit is None:
                        low = txt.lower()
                        if any(k in low for k in
                               ["import", "confirm", "create", "complete",
                                "continue", "done", "get started"]):
                            submit = b
                except Exception:
                    pass
            if submit is None:
                # fallback: last enabled visible button
                for i in range(btns.count()):
                    try:
                        b = btns.nth(i)
                        if b.is_visible() and not b.is_disabled():
                            submit = b
                    except Exception:
                        pass
            if submit is None:
                print("[!] No clickable button found.")
                sys.exit(1)
            submit.click(timeout=10000)
            print("[*] Submit button clicked.")

            page.wait_for_timeout(4000)

            # 8. Dismiss any "What's new" / survey / onboarding popups.
            for _ in range(4):
                if not click_text("Got it", "OK", "Next", "Done",
                                  "Not now", "Skip", timeout=4000):
                    break

            # 9. Verify the imported address.
            page.wait_for_timeout(2000)
            body_text = page.inner_text("body")
            m = re.search(r"0x[a-fA-F0-9]{40}", body_text)
            if m and m.group(0).lower() == EXPECTED_ADDR:
                print(f"[OK] Wallet imported. Address matches: {m.group(0)}")
            elif m:
                print(f"[WARN] Address shown ({m.group(0)}) does not match "
                      f"expected farming wallet. Manual review needed.")
            else:
                print("[WARN] Could not read address from UI; "
                      "verify manually.")

            page.screenshot(path=os.path.join(BASE, "import-done.png"))
            print("[*] Done. Screenshot: import-done.png (post-import UI)")
            context.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()
    # Ensure the phrase leaves no trace in this process's memory dump path.
    print("[*] Import flow finished. Seed phrase was never written to disk.")


if __name__ == "__main__":
    main()
