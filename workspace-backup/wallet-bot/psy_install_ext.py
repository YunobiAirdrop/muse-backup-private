#!/usr/bin/env python3
"""Install Psy Wallet extension from Chrome Web Store via browser."""
import os
import subprocess
import time

BASE = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(BASE, "profile")
EXT_DIR = os.path.join(BASE, "ext", "metamask")
CHROME_BIN = os.path.expanduser(
    "~/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome"
)
DISPLAY_NUM = ":99"

if not os.path.exists('/tmp/.X11-unix/X99'):
    subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1280x800x24'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
os.environ['DISPLAY'] = ':99'
try:
    import socket as _s
    _s.create_connection(('127.0.0.1', 3129), timeout=2).close()
except:
    subprocess.Popen([BASE+'/venv/bin/python', BASE+'/forwarder.py'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    # Don't use --disable-extensions-except so Web Store works.
    ctx = p.chromium.launch_persistent_context(
        PROFILE_DIR, executable_path=CHROME_BIN, headless=False,
        args=['--load-extension='+EXT_DIR,
              '--no-sandbox', '--disable-dev-shm-usage',
              '--disable-gpu', '--mute-audio',
              '--proxy-server=http://127.0.0.1:3129',
              '--ignore-certificate-errors'],
        viewport={'width': 1280, 'height': 800})
    time.sleep(3)
    pg = ctx.new_page()
    try:
        pg.goto('https://chromewebstore.google.com/detail/psy-wallet/gkjbpipdcdijofkbpoefkpgoaameonal',
                wait_until='domcontentloaded', timeout=60000)
    except Exception as e:
        print("goto:", str(e)[:80], flush=True)
    pg.wait_for_timeout(10000)
    print("title:", pg.title(), flush=True)
    pg.screenshot(path=BASE+'/psy-webstore2.png')
    # Find Add to Chrome.
    try:
        btn = pg.get_by_role("button", name="Add to Chrome").first
        vis = btn.is_visible(timeout=8000)
        print("Add to Chrome visible:", vis, flush=True)
        if vis:
            btn.click()
            print("clicked Add to Chrome", flush=True)
            pg.wait_for_timeout(5000)
            # Handle confirmation dialog.
            for t in ["Add extension", "Add Extension"]:
                try:
                    b = pg.get_by_role("button", name=t).first
                    if b.is_visible(timeout=5000):
                        b.click()
                        print(f"clicked {t}", flush=True)
                        pg.wait_for_timeout(5000)
                        break
                except:
                    pass
    except Exception as e:
        print("btn err:", str(e)[:60], flush=True)
    pg.screenshot(path=BASE+'/psy-webstore3.png')
    # Check installed extensions.
    pg.goto('chrome://extensions/')
    pg.wait_for_timeout(3000)
    print("extensions page:", pg.inner_text("body")[:500].replace("\n"," | "), flush=True)
    ctx.close()
print("done", flush=True)
