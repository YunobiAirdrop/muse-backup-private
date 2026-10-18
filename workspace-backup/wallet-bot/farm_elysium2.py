#!/usr/bin/env python3
"""
Elysium onboarding v2 — more robust: click UI Connect button instead of
raw eth_requestAccounts evaluate.
"""
import os
import subprocess
import sys
import time
import traceback

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

ELYSIUM = {"chainId": 99801, "rpc": "https://testnet-rpc.elysium.kinetiq.xyz",
           "name": "Elysium Testnet",
           "explorer": "https://test-explorer.elysium.kinetiq.xyz"}
HYPEREVM = {"chainId": 998, "rpc": "https://rpc.hyperliquid-testnet.xyz/evm",
            "name": "HyperEVM Testnet",
            "explorer": "https://testnet.hyperliquid.xyz"}


def log(*a):
    print(*a, flush=True)


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


def clear_stale_locks():
    for f in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        try:
            os.remove(os.path.join(PROFILE_DIR, f))
        except Exception:
            pass


def unlock_mm(page):
    pw = open(PASS_FILE).read().strip()
    try:
        inp = page.locator('input[type="password"]').first
        if inp.is_visible(timeout=8000):
            inp.fill(pw)
            page.get_by_role("button", name="Unlock").first.click()
            log("[*] MetaMask unlocked.")
            page.wait_for_timeout(3000)
            return True
    except Exception as e:
        log(f"[*] Unlock skip: {str(e)[:60]}")
    return False


def mm_approve(ctx, kinds=("Next", "Connect", "Confirm", "Approve")):
    """Click through MetaMask popup windows."""
    done = False
    for w in ctx.pages:
        try:
            if not w.url.startswith(f"chrome-extension://{EXT_ID}"):
                continue
            log(f"[*] MM popup: {w.url[:90]}")
            w.wait_for_timeout(2500)
            try:
                for cb in w.locator('input[type="checkbox"]').all():
                    try:
                        if cb.is_visible() and not cb.is_checked():
                            cb.check()
                    except Exception:
                        pass
            except Exception:
                pass
            for t in kinds:
                try:
                    el = w.get_by_role("button", name=t).first
                    if el.is_visible(timeout=4000) and not el.is_disabled():
                        el.click()
                        log(f"[*] Clicked {t!r}")
                        w.wait_for_timeout(3000)
                        done = True
                        break
                except Exception:
                    pass
        except Exception:
            pass
    return done


def main():
    from playwright.sync_api import sync_playwright
    clear_stale_locks()
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
            time.sleep(5)

            mm = ctx.new_page()
            mm.goto(f"chrome-extension://{EXT_ID}/home.html")
            mm.wait_for_timeout(3000)
            unlock_mm(mm)
            mm.close()

            pg = ctx.new_page()
            try:
                pg.goto("https://elysium.kinetiq.xyz/testnet-faucet",
                        wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                log(f"[*] goto: {str(e)[:80]}")
            pg.wait_for_timeout(8000)
            log(f"[*] Title: {pg.title()}")

            # Click the page's Connect button (UI, not raw evaluate).
            try:
                btn = pg.get_by_role("button", name="Connect").first
                if btn.is_visible(timeout=10000):
                    btn.click()
                    log("[*] Clicked page Connect button")
                    pg.wait_for_timeout(4000)
            except Exception as e:
                log(f"[*] Connect click err: {str(e)[:80]}")

            # If a wallet-choice modal appeared, pick MetaMask/Injected.
            for t in ["MetaMask", "Injected", "Browser Wallet"]:
                try:
                    el = pg.get_by_text(t, exact=False).first
                    if el.is_visible(timeout=3000):
                        el.click()
                        log(f"[*] Picked {t!r}")
                        pg.wait_for_timeout(3000)
                        break
                except Exception:
                    pass

            # Approve MetaMask popup (may need two passes).
            mm_approve(ctx)
            pg.wait_for_timeout(3000)
            mm_approve(ctx)
            pg.wait_for_timeout(3000)
            pg.screenshot(path=os.path.join(BASE, "elysium-2-connected.png"))

            # Verify.
            try:
                accs = pg.evaluate(
                    """async () => await window.ethereum.request(
                        {method: 'eth_accounts'})""")
                log(f"[*] eth_accounts: {accs}")
            except Exception as e:
                log(f"[*] eth_accounts err: {str(e)[:80]}")

            # Add Elysium Testnet via the page button if present.
            for t in ["Add Elysium Testnet to wallet"]:
                try:
                    el = pg.get_by_text(t, exact=False).first
                    if el.is_visible(timeout=5000):
                        el.click()
                        log(f"[*] Clicked {t!r}")
                        pg.wait_for_timeout(3000)
                        mm_approve(ctx)
                        pg.wait_for_timeout(2000)
                        break
                except Exception as e:
                    log(f"[*] add-net err: {str(e)[:60]}")

            # Claim HYPE.
            claimed = False
            for t in ["Claim", "Request", "Get", "Drip", "Send"]:
                try:
                    els = pg.get_by_text(t, exact=False).all()
                    for el in els:
                        try:
                            txt = (el.inner_text() or "")[:40]
                            if el.is_visible() and el.is_enabled() and \
                                    "connect" not in txt.lower():
                                el.click()
                                log(f"[*] Clicked {t!r} ({txt!r})")
                                pg.wait_for_timeout(5000)
                                mm_approve(ctx,
                                           kinds=("Confirm", "Approve"))
                                claimed = True
                                break
                        except Exception:
                            pass
                    if claimed:
                        break
                except Exception:
                    pass
            pg.wait_for_timeout(4000)
            pg.screenshot(path=os.path.join(BASE, "elysium-3-claim.png"))
            try:
                body = pg.inner_text("body")[:500].replace("\n", " | ")
                log(f"[*] Page: {body}")
            except Exception:
                pass

            ctx.close()
    except Exception:
        traceback.print_exc()
    finally:
        if xvfb is not None:
            xvfb.terminate()
        if fwd is not None:
            fwd.terminate()
    log("[*] Done.")


if __name__ == "__main__":
    main()
