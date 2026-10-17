"""
Yunobi-AI Auto-Reg — Interactive CLI (Multi Temp Mail)
========================================
Beautiful loader, no verbose output, instant next account, interactive count.
Auto-fallback across multiple temp mail providers.

Usage: python yunobi_autoreg.py
"""

import asyncio, json, time, random, re, sys, string, os, threading
from datetime import datetime
from pathlib import Path
import httpx
from camoufox import AsyncCamoufox

YUNOBI = "https://api.atria-asi.ai"
OUT    = Path(__file__).parent / "akun.txt"

# ═══════════════════════════════════════════════════
#  TEMP MAIL PROVIDERS (auto-fallback)
# ═══════════════════════════════════════════════════

class TempMailProvider:
    """Base class — semua provider harus implement ini."""
    name = "base"

    def create(self):
        """Return (client, token/sid, email). Raise kalau gagal."""
        raise NotImplementedError

    def fetch_messages(self, client, token, email):
        """Return list of message dicts. Raise kalau gagal."""
        raise NotImplementedError

    def close(self, client):
        try: client.close()
        except: pass


# ─── 1. TEMPIK (meowx) ──────────────────────────────
class TempikProvider(TempMailProvider):
    name = "tempik.meowx"
    BASE = "https://tempik.meowx.web.id"

    def create(self):
        c = httpx.Client(timeout=10)
        sid = c.get(f"{self.BASE}/api/session").json()["sessionId"]
        loc = "yunobi" + ''.join(random.choices(string.ascii_lowercase+string.digits, k=6))
        r = c.post(f"{self.BASE}/api/inboxes", json={"localPart": loc},
                   headers={"x-session-id": sid})
        r.raise_for_status()
        email = r.json()["address"]
        return c, sid, email

    def fetch_messages(self, client, token, email):
        r = client.get(f"{self.BASE}/api/inboxes/{email}/messages",
                       headers={"x-session-id": token}, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []


# ─── 2. MAIL.TM ─────────────────────────────────────
class MailTmProvider(TempMailProvider):
    name = "mail.tm"
    BASE = "https://api.mail.tm"

    def create(self):
        c = httpx.Client(timeout=10)
        dom = c.get(f"{self.BASE}/domains").json()["hydra:member"][0]["domain"]
        loc = "yunobi" + ''.join(random.choices(string.ascii_lowercase+string.digits, k=6))
        email = f"{loc}@{dom}"
        pwd = "Yunobi" + ''.join(random.choices(string.digits, k=8)) + "!"
        r = c.post(f"{self.BASE}/accounts", json={"address": email, "password": pwd})
        r.raise_for_status()
        tok = c.post(f"{self.BASE}/token",
                     json={"address": email, "password": pwd}).json()["token"]
        return c, tok, email

    def fetch_messages(self, client, token, email):
        r = client.get(f"{self.BASE}/messages",
                       headers={"Authorization": f"Bearer {token}"}, timeout=10)
        r.raise_for_status()
        return r.json().get("hydra:member", [])


# ─── 3. MAIL.GW ─────────────────────────────────────
class MailGwProvider(TempMailProvider):
    name = "mail.gw"
    BASE = "https://api.mail.gw"

    def create(self):
        c = httpx.Client(timeout=10)
        dom = c.get(f"{self.BASE}/domains").json()["hydra:member"][0]["domain"]
        loc = "yunobi" + ''.join(random.choices(string.ascii_lowercase+string.digits, k=6))
        email = f"{loc}@{dom}"
        pwd = "Yunobi" + ''.join(random.choices(string.digits, k=8)) + "!"
        r = c.post(f"{self.BASE}/accounts", json={"address": email, "password": pwd})
        r.raise_for_status()
        tok = c.post(f"{self.BASE}/token",
                     json={"address": email, "password": pwd}).json()["token"]
        return c, tok, email

    def fetch_messages(self, client, token, email):
        r = client.get(f"{self.BASE}/messages",
                       headers={"Authorization": f"Bearer {token}"}, timeout=10)
        r.raise_for_status()
        return r.json().get("hydra:member", [])


# ─── 4. 1SECMAIL ────────────────────────────────────
class OneSecMailProvider(TempMailProvider):
    name = "1secmail"
    BASE = "https://www.1secmail.com/api/v1/"

    def create(self):
        c = httpx.Client(timeout=10)
        r = c.get(f"{self.BASE}?action=genRandomMailbox&count=1")
        r.raise_for_status()
        email = r.json()[0]
        return c, None, email

    def fetch_messages(self, client, token, email):
        login, domain = email.split("@")
        r = client.get(f"{self.BASE}?action=getMessages&login={login}&domain={domain}",
                       timeout=10)
        r.raise_for_status()
        msgs = r.json()
        # 1secmail butuh fetch body tiap pesan
        detailed = []
        for m in msgs:
            mid = m.get("id")
            if not mid: continue
            d = client.get(f"{self.BASE}?action=readMessage&login={login}&domain={domain}&id={mid}",
                           timeout=10)
            if d.status_code == 200:
                detailed.append(d.json())
        return detailed


# ─── 5. MAILSLURP (butuh API key) ───────────────────
class MailSlurpProvider(TempMailProvider):
    name = "mailslurp"
    BASE = "https://api.mailslurp.com"
    API_KEY = os.environ.get("MAILSLURP_API_KEY", "")

    def create(self):
        if not self.API_KEY:
            raise RuntimeError("MAILSLURP_API_KEY tidak diset")
        c = httpx.Client(timeout=15)
        r = c.post(f"{self.BASE}/inboxes",
                   headers={"x-api-key": self.API_KEY})
        r.raise_for_status()
        data = r.json()
        return c, data["id"], data["emailAddress"]

    def fetch_messages(self, client, token, email):
        r = client.get(f"{self.BASE}/waitForLatestEmail",
                       params={"inboxId": token, "timeout": 8000},
                       headers={"x-api-key": self.API_KEY}, timeout=15)
        if r.status_code == 200 and r.text:
            return [r.json()]
        return []


# ─── REGISTRY ───────────────────────────────────────
PROVIDERS = [
    TempikProvider(),
    MailTmProvider(),
    MailGwProvider(),
    OneSecMailProvider(),
    # MailSlurpProvider(),  # uncomment kalau punya API key
]


# ─── OTP EXTRACTOR (multi-format) ───────────────────
def extract_otp(msgs):
    """Cari kode OTP 4-8 digit dari berbagai format pesan."""
    for m in msgs:
        # Gabung semua string value dari dict (handle nested)
        parts = []
        def walk(o):
            if isinstance(o, str):
                parts.append(o)
            elif isinstance(o, dict):
                for v in o.values(): walk(v)
            elif isinstance(o, list):
                for v in o: walk(v)
        walk(m)
        txt = " ".join(parts)

        # Prioritas: cari 6 digit dulu
        for pat in [r'\b(\d{6})\b', r'\b(\d{5})\b', r'\b(\d{4})\b', r'\b(\d{7,8})\b']:
            codes = re.findall(pat, txt)
            if codes:
                return codes[0]
    return None


# ─── LOADER ──────────────────────────────────────────
class Loader:
    def __init__(self, text="Processing"):
        self.text = text
        self.frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        self.running = False
        self.t = None

    def _spin(self):
        i = 0
        while self.running:
            frame = self.frames[i % len(self.frames)]
            sys.stdout.write(f"\r  {frame} {self.text}... ")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1

    def update(self, text):
        self.text = text

    def start(self, text=None):
        if text: self.text = text
        self.running = True
        self.t = threading.Thread(target=self._spin, daemon=True)
        self.t.start()

    def stop(self, ok=True):
        self.running = False
        if self.t: self.t.join(timeout=0.3)
        if ok:
            sys.stdout.write(f"\r  ✅ {self.text}\n")
        else:
            sys.stdout.write(f"\r  ❌ {self.text}\n")
        sys.stdout.flush()


# ─── CLEAR / HEADER ─────────────────────────────────
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def header():
    clear()
    print("""
  ╔══════════════════════════════════════════╗
  ║          YUNOBI AUTO-REG v2.0            ║
  ║     100M Token · Multi Temp Mail         ║
  ╚══════════════════════════════════════════╝
""")


# ─── CREATE MAIL (with fallback) ────────────────────
def create_mail(loader, idx, total):
    """Coba tiap provider berurutan sampai berhasil."""
    for prov in PROVIDERS:
        try:
            loader.update(f"[{idx}/{total}] Mail via {prov.name}...")
            c, tok, email = prov.create()
            if email:
                return prov, c, tok, email
        except Exception:
            continue
    return None, None, None, None


# ─── FETCH OTP (with fallback ke provider lain) ─────
def fetch_otp(loader, idx, total, prov, c, tok, email, max_wait=20):
    """Polling OTP. Kalau provider utama error, coba provider lain sebagai backup."""
    for sec in range(max_wait):
        time.sleep(1)
        try:
            msgs = prov.fetch_messages(c, tok, email)
            if msgs:
                otp = extract_otp(msgs)
                if otp:
                    return otp
        except Exception:
            # Provider utama error → coba provider cadangan (khusus email beda, skip)
            pass
    return None


# ─── RUN ONE ─────────────────────────────────────────
async def run_one(idx, total):
    loader = Loader(f"[{idx}/{total}] Preparing...")
    loader.start()

    # Bikin email (auto-fallback)
    prov, c, sid, email = create_mail(loader, idx, total)
    if not email:
        loader.stop(False)
        print(f"     ⚠️  Semua provider temp mail gagal")
        return None

    loader.stop()
    print(f"     📧 {email}  ({prov.name})")

    try:
        async with AsyncCamoufox(headless=True) as br:
            p = await br.new_page()

            # Sign-in
            loader.start(f"[{idx}/{total}] Solving Turnstile...")
            await p.goto(f"{YUNOBI}/sign-in", wait_until="networkidle", timeout=30000)
            await asyncio.sleep(4)

            # Register
            loader.update(f"[{idx}/{total}] Registering account...")
            await p.click('a:has-text("Create account")')
            await asyncio.sleep(3)
            await p.fill('input[name="identifier"]', email)
            await asyncio.sleep(0.3)

            # Kirim OTP
            loader.update(f"[{idx}/{total}] Sending OTP...")
            await p.click('button:has-text("Create account")')

            for _ in range(20):
                await asyncio.sleep(1)
                if "verification-code" in p.url: break

            # Polling OTP
            loader.update(f"[{idx}/{total}] Waiting OTP...")
            otp = None
            for _ in range(20):
                await asyncio.sleep(1)
                try:
                    msgs = prov.fetch_messages(c, sid, email)
                    if msgs:
                        otp = extract_otp(msgs)
                        if otp: break
                except Exception:
                    continue

            if not otp:
                loader.stop(False)
                print(f"     ⚠️  OTP timeout dari {prov.name}")
                return None

            # Isi OTP
            loader.update(f"[{idx}/{total}] Verifying OTP...")
            await asyncio.sleep(0.3)
            digs = await p.query_selector_all('input[type="number"],input[inputmode="numeric"]')
            if len(digs) >= 6:
                for i, d in enumerate(otp): await digs[i].fill(d)
            else:
                await p.keyboard.type(otp, delay=50)
            await asyncio.sleep(0.2)

            for t in ["Verify","Submit","Sign in","Create account","Continue"]:
                try:
                    b = await p.query_selector(f'button:has-text("{t}")')
                    if b and not await b.is_disabled(): await b.click(); break
                except: continue

            # Console
            loader.update(f"[{idx}/{total}] Creating API key...")
            for _ in range(15):
                await asyncio.sleep(1)
                if "console" in p.url or "callback" in p.url: break
            await p.goto(f"{YUNOBI}/console", wait_until="networkidle", timeout=15000)
            await asyncio.sleep(2)

            # Cookies
            cks = await p.context.cookies()
            cookies = {ck["name"]: ck["value"] for ck in cks
                       if "atria-asi.ai" in ck.get("domain","")}

        # API Key
        ck_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        r = httpx.post(f"{YUNOBI}/api/keys", json={"name":"default"},
                       headers={"Cookie": ck_str, "Content-Type":"application/json",
                                "Origin": YUNOBI}, timeout=20)

        if r.status_code != 201:
            loader.stop(False)
            return None

        data = r.json()
        key = data.get("key","") or data.get("apiKey","") or ""
        if not key:
            m = re.search(r'"?(atr_\w+)"?', json.dumps(data))
            if m: key = m.group(1)

        loader.stop()

        # Simpan
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(f"{key}\n")

        return {"email": email, "key": key, "provider": prov.name}

    except Exception:
        loader.stop(False)
        return None
    finally:
        prov.close(c)


# ─── MAIN ────────────────────────────────────────────
async def main():
    header()
    count = input("  How many accounts? [1] ").strip()
    count = int(count) if count.isdigit() and int(count) > 0 else 1
    print()

    results = []
    ok = 0
    start = time.time()

    for i in range(count):
        r = await run_one(i+1, count)
        if r:
            ok += 1
            results.append(r)
        await asyncio.sleep(1)  # jeda antar akun biar gak kena rate-limit

    elapsed = time.time() - start
    avg = elapsed / count if count > 0 else 0

    print(f"""
  ╔══════════════════════════════════════════╗
  ║              RESULTS                     ║
  ╠══════════════════════════════════════════╣
  ║  Total    : {ok}/{count} accounts              ║
  ║  Time     : {elapsed:.1f}s ({avg:.1f}s/acc)      ║
  ║  Tier     : 100M tokens each             ║
  ╚══════════════════════════════════════════╝
""")

    if results:
        print("  ─── ACCOUNTS ───")
        for i, r in enumerate(results, 1):
            print(f"  [{i}] {r['email']}  [{r['provider']}]")
            print(f"      🔑 {r['key']}")
            print()
        print(f"  💾 Saved to: {OUT}")

    input("\n  Press Enter to exit...")

if __name__ == "__main__":
    asyncio.run(main())