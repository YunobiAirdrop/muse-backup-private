#!/usr/bin/env python3
"""Claim DogeOS faucet via headless Chromium. No wallet, no signing —
just paste the public address, pick token, click claim."""
import json

from playwright.sync_api import sync_playwright

ADDR = "0xf0f25C36AC70E9d787a108eFB351626192C8107b"
URL = "https://faucet.testnet.dogeos.com"

result = {"ok": False}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"],
                                proxy={"server": "http://127.0.0.1:3129"})
    page = browser.new_page()
    try:
        page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(9000)

        # 1. isi address
        inp = page.locator('input[type="text"], input[placeholder*="address" i], input:not([type])').first
        if inp.count() == 0:
            result["error"] = "no address input"
        else:
            inp.fill(ADDR)
            page.wait_for_timeout(1200)

        # 2. pilih token Dogecoin (DOGE)
        try:
            picker = page.locator('button:has-text("Pick a Token")').first
            if picker.count():
                picker.click()
                page.wait_for_timeout(1800)
                opt = page.locator('[role="option"]:has-text("DOGE"), li:has-text("DOGE")').first
                if opt.count():
                    opt.click()
                    page.wait_for_timeout(1500)
        except Exception as e:
            print("picker:", str(e)[:100])

        page.screenshot(path="/tmp/faucet-2.png", full_page=True)
        page.wait_for_timeout(2000)

        # 3. daftar kandidat tombol klaim yang terlihat
        cands = page.eval_on_selector_all(
            'button, [role="button"], a',
            '''els => els.map(e => ({t: (e.innerText||"").trim().slice(0,80),
               vis: e.offsetParent !== null})).filter(x => x.vis && /get|claim/i.test(x.t))''')
        print("CANDIDATES:", json.dumps(cands))

        # 4. klik tombol "Get 42.069 DOGE" via beberapa selector
        clicked = None
        for sel in ['button:has-text("42.069")', '[role="button"]:has-text("42.069")',
                    'button:has-text("Get")', ':text("Get 42.069 DOGE")']:
            try:
                el = page.locator(sel).first
                if el.count() and el.is_visible():
                    el.scroll_into_view_if_needed()
                    el.click(timeout=8000)
                    clicked = sel
                    break
            except Exception as e:
                print("try", sel, "->", str(e)[:90])
        if not clicked:
            result["error"] = "no claim button found"
        else:
            print("CLICKED via", clicked)
            page.wait_for_timeout(12000)
            page.screenshot(path="/tmp/faucet-3.png", full_page=True)
            txt = page.inner_text("body")
            result["body_text"] = txt[:800]
            low = txt.lower()
            if any(k in low for k in ["success", "doge has been sent", "check your wallet", "transaction hash"]):
                result["ok"] = True
            elif any(k in low for k in ["already", "24 hours", "rate limit", "cooldown", "come back", "try again tomorrow"]):
                result["rate_limited"] = True
    except Exception as e:
        result["error"] = str(e)[:200]
    finally:
        browser.close()
print(json.dumps(result, indent=1))
