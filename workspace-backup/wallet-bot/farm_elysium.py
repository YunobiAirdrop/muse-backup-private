#!/usr/bin/env python3
"""
Onboard farming wallet to Elysium testnet (Kinetiq L2, Hyperliquid ecosystem).

Steps:
1. Claim testnet HYPE from https://elysium.kinetiq.xyz/testnet-faucet
2. Add Elysium Testnet (99801) + HyperEVM Testnet (998) to MetaMask
3. Bridge small HYPE via https://elysium.kinetiq.xyz/testnet-bridge
4. Do 2-3 self-transfers on Elysium for activity history
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

# Network details (verified via web, 2026-10-19)
ELYSIUM = {"chainId": 99801, "rpc": "https://testnet-rpc.elysium.kinetiq.xyz",
           "name": "Elysium Testnet",
           "explorer": "https://test-explorer.elysium.kinetiq.xyz"}
HYPEREVM = {"chainId": 998, "rpc": "https://rpc.hyperliquid-testnet.xyz/evm",
            "name": "HyperEVM Testnet",
            "explorer": "https://testnet.hyperliquid.xyz"}


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


def unlock_metamask(page):
    pw = open(PASS_FILE).read().strip()
    try:
        inp = page.locator('input[type="password"]').first
        if inp.is_visible(timeout=8000):
            inp.fill(pw)
            page.get_by_role("button", name="Unlock").first.click()
            print("[*] MetaMask unlocked.", flush=True)
            page.wait_for_timeout(3000)
            return True
    except Exception as e:
        print(f"[*] Unlock skip: {str(e)[:60]}", flush=True)
    return False


def approve_mm_popup(ctx, action="connect"):
    """Approve MetaMask notification popup (connect or tx confirm)."""
    approved = False
    for w in ctx.pages:
        try:
            if not w.url.startswith(f"chrome-extension://{EXT_ID}"):
                continue
            if "notification" not in w.url and "popup" not in w.url \
                    and "home.html" not in w.url:
                continue
            w.wait_for_timeout(2500)
            # account checkboxes
            try:
                for cb in w.locator('input[type="checkbox"]').all():
                    try:
                        if cb.is_visible() and not cb.is_checked():
                            cb.check()
                    except Exception:
                        pass
            except Exception:
                pass
            names = ["Next", "Connect"] if action == "connect" \
                else ["Confirm", "Approve", "Sign"]
            for t in names:
                try:
                    el = w.get_by_role("button", name=t).first
                    if el.is_visible(timeout=3000) and not el.is_disabled():
                        el.click()
                        print(f"[*] MM popup: clicked {t!r}", flush=True)
                        w.wait_for_timeout(3000)
                        approved = True
                        break
                except Exception:
                    pass
        except Exception:
            pass
    return approved


def connect_wallet(pg, ctx):
    """Connect via window.ethereum, approve popup, verify."""
    has_eth = pg.evaluate(
        "() => typeof window.ethereum !== 'undefined'")
    print(f"[*] window.ethereum: {has_eth}", flush=True)
    if not has_eth:
        return False
    try:
        accs = pg.evaluate(
            """async () => await window.ethereum.request(
                {method: 'eth_requestAccounts'})""")
        print(f"[*] eth_requestAccounts: {accs}", flush=True)
    except Exception as e:
        print(f"[*] requestAccounts popup?: {str(e)[:100]}", flush=True)
    pg.wait_for_timeout(3000)
    approve_mm_popup(ctx, "connect")
    pg.wait_for_timeout(3000)
    approve_mm_popup(ctx, "connect")  # second pass for multi-step
    try:
        accs = pg.evaluate(
            """async () => await window.ethereum.request(
                {method: 'eth_accounts'})""")
        print(f"[*] eth_accounts: {accs}", flush=True)
        return bool(accs and accs[0].lower() == EXPECTED)
    except Exception as e:
        print(f"[*] eth_accounts err: {str(e)[:60]}", flush=True)
        return False


def add_network(pg, net):
    """Add custom network via wallet_addEthereumChain."""
    try:
        res = pg.evaluate(
            """async (net) => await window.ethereum.request({
                method: 'wallet_addEthereumChain',
                params: [{
                    chainId: '0x' + net.chainId.toString(16),
                    chainName: net.name,
                    nativeCurrency: {name: 'HYPE', symbol: 'HYPE',
                                     decimals: 18},
                    rpcUrls: [net.rpc],
                    blockExplorerUrls: [net.explorer]
                }]
            })""", net)
        print(f"[*] add {net['name']}: {res}", flush=True)
        return True
    except Exception as e:
        print(f"[*] add {net['name']} err: {str(e)[:100]}", flush=True)
        return False


def main():
    from playwright.sync_api import sync_playwright
    xvfb = start_xvfb()
    fwd = ensure_forwarder()
    os.environ["DISPLAY"] = DISPLAY_NUM
    report = {"faucet": "not attempted", "networks": [],
              "bridge_tx": None, "extra_txs": [], "docs": ""}
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
            unlock_metamask(mm)
            mm.close()

            # ---- 1. FAUCET ----
            pg = ctx.new_page()
            try:
                pg.goto("https://elysium.kinetiq.xyz/testnet-faucet",
                        wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print(f"[*] faucet goto: {str(e)[:80]}", flush=True)
            pg.wait_for_timeout(8000)
            pg.screenshot(path=os.path.join(BASE, "elysium-1-faucet.png"))
            print(f"[*] Faucet title: {pg.title()}", flush=True)

            if connect_wallet(pg, ctx):
                print("[OK] Wallet connected on faucet page.", flush=True)
            pg.wait_for_timeout(3000)
            pg.screenshot(path=os.path.join(BASE, "elysium-2-connected.png"))

            # Click claim / request buttons.
            claimed = False
            for t in ["Claim", "Request", "Get testnet HYPE", "Get HYPE",
                      "Send", "Drip"]:
                try:
                    els = pg.get_by_text(t, exact=False).all()
                    for el in els:
                        try:
                            if el.is_visible() and el.is_enabled():
                                el.click()
                                print(f"[*] Clicked {t!r}", flush=True)
                                pg.wait_for_timeout(5000)
                                approve_mm_popup(ctx, "tx")
                                claimed = True
                                break
                        except Exception:
                            pass
                    if claimed:
                        break
                except Exception:
                    pass
            pg.wait_for_timeout(4000)
            pg.screenshot(path=os.path.join(BASE, "elysium-3-claimed.png"))
            body = pg.inner_text("body")[:600].replace("\n", " | ")
            print(f"[*] Faucet result: {body}", flush=True)
            report["faucet"] = f"attempted={claimed}; page says: {body[:200]}"

            # ---- 2. ADD NETWORKS ----
            for net in (ELYSIUM, HYPEREVM):
                if add_network(pg, net):
                    pg.wait_for_timeout(2000)
                    approve_mm_popup(ctx, "connect")
                    pg.wait_for_timeout(2000)
                    report["networks"].append(
                        f"{net['name']} ({net['chainId']})")

            # ---- 3. BRIDGE ----
            try:
                pg.goto("https://elysium.kinetiq.xyz/testnet-bridge",
                        wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print(f"[*] bridge goto: {str(e)[:80]}", flush=True)
            pg.wait_for_timeout(8000)
            pg.screenshot(path=os.path.join(BASE, "elysium-4-bridge.png"))
            print(f"[*] Bridge title: {pg.title()}", flush=True)
            body = pg.inner_text("body")[:800].replace("\n", " | ")
            print(f"[*] Bridge page: {body}", flush=True)
            report["bridge_page"] = body[:300]

            ctx.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()
        if fwd is not None:
            fwd.terminate()
    print("[REPORT]", report, flush=True)


if __name__ == "__main__":
    main()
