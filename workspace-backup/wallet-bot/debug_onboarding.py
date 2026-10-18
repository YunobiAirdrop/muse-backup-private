#!/usr/bin/env python3
"""Debug MetaMask onboarding page structure (no secrets involved)."""
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
            context = p.chromium.launch_persistent_context(
                PROFILE_DIR, executable_path=CHROME_BIN, headless=False,
                args=[f"--load-extension={EXT_DIR}",
                      f"--disable-extensions-except={EXT_DIR}",
                      "--no-sandbox", "--disable-dev-shm-usage",
                      "--disable-gpu", "--mute-audio"],
                viewport={"width": 1280, "height": 800})
            time.sleep(4)
            ext_id = None
            for sw in context.service_workers:
                m = re.match(r"chrome-extension://([a-p]{32})/", sw.url)
                if m:
                    ext_id = m.group(1)
                    break
            print("ext_id:", ext_id)
            page = context.new_page()
            page.goto(f"chrome-extension://{ext_id}/home.html")
            page.wait_for_timeout(3000)
            print("STEP0 title:", page.title())
            page.screenshot(path=os.path.join(BASE, "dbg-0-home.png"))

            # click import
            for t in ["I have an existing wallet", "Import wallet"]:
                try:
                    el = page.get_by_text(t, exact=False).first
                    if el.is_visible():
                        el.click(); print("clicked:", t); break
                except Exception as e:
                    print("click fail:", t, str(e)[:60])
            page.wait_for_timeout(2500)
            print("STEP1 title:", page.title())
            print("STEP1 url:", page.url[:100])
            page.screenshot(path=os.path.join(BASE, "dbg-1-after-import-click.png"))

            # try dismiss opt-in
            for t in ["No thanks", "No Thanks"]:
                try:
                    el = page.get_by_text(t, exact=False).first
                    if el.is_visible():
                        el.click(); print("clicked:", t); break
                except Exception:
                    pass
            page.wait_for_timeout(2500)
            # click Import using Secret Recovery Phrase
            for t in ["Import using Secret Recovery Phrase"]:
                try:
                    el = page.get_by_text(t, exact=False).first
                    if el.is_visible():
                        el.click(); print("clicked:", t); break
                except Exception as e:
                    print("click fail:", t, str(e)[:60])
            page.wait_for_timeout(3000)
            print("STEP2 title:", page.title())
            print("STEP2 url:", page.url[:120])
            body = page.inner_text("body")[:800]
            print("STEP2 body head:", body.replace("\n", " | "))
            print("inputs:", page.locator("input").count())
            print("textareas:", page.locator("textarea").count())
            print("buttons:", page.locator("button").count())
            for i in range(min(8, page.locator("button").count())):
                try:
                    print("  btn", i, ":",
                          page.locator("button").nth(i).inner_text()[:60])
                except Exception:
                    pass
            page.screenshot(path=os.path.join(BASE, "dbg-2-srp.png"))
            context.close()
    finally:
        if xvfb is not None:
            xvfb.terminate()


if __name__ == "__main__":
    main()

def debug_password_page():
    pass
