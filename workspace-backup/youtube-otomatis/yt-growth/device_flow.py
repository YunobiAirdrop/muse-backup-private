#!/usr/bin/env python3
"""OAuth Device Flow untuk yt-growth — tanpa browser VM, tanpa baca address bar.

Alur per channel:
  1. python device_flow.py start            -> tampilkan user_code + URL verifikasi
  2. User buka google.com/device di HP, masukkan kode, PILIH CHANNEL yang
     diminta (bukan akun utama), klik Allow.
  3. python device_flow.py poll SLUG        -> tunggu persetujuan, simpan token
     ke ~/.hermes/yt-growth/tokens/{slug}.json (600).

Device flow tidak butuh client_secret (installed app) dan tidak butuh PKCE.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path.home() / ".hermes" / "yt-growth"
CLIENT_SECRETS = BASE / "client_secret.json"
TOKENS_DIR = BASE / "tokens"
PENDING = BASE / "device_pending.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
DEVICE_CODE_URL = "https://oauth2.googleapis.com/device/code"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def _post(url, data):
    req = urllib.request.Request(
        url, data=urllib.parse.urlencode(data).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r), None
    except urllib.error.HTTPError as e:
        return None, json.load(e)


def _client_id():
    return json.load(open(CLIENT_SECRETS))["installed"]["client_id"]


def start():
    body, err = _post(DEVICE_CODE_URL, {
        "client_id": _client_id(),
        "scope": " ".join(SCOPES),
    })
    if err:
        sys.exit(f"Gagal minta device code: {err}")
    PENDING.write_text(json.dumps({
        "device_code": body["device_code"],
        "expires_at": time.time() + body.get("expires_in", 1800),
    }))
    os.chmod(PENDING, 0o600)
    print("INSTRUKSI UNTUK USER (kirim via chat):")
    print(f"  1. Buka {body['verification_url']} di HP")
    print(f"  2. Masukkan kode: {body['user_code']}")
    print("  3. Pilih CHANNEL sesuai instruksi (JANGAN akun Google utama)")
    print("  4. Klik Allow/Izinkan, lalu balas 'udah'")
    print(f"(kode kedaluwarsa {body.get('expires_in', 1800)//60} menit)")


def poll(slug, timeout=600):
    if not PENDING.exists():
        sys.exit("Tidak ada device flow aktif. Jalankan: python device_flow.py start")
    pending = json.loads(PENDING.read_text())
    if time.time() > pending["expires_at"]:
        sys.exit("Device code kedaluwarsa. Jalankan start lagi.")
    client_id = _client_id()
    deadline = time.time() + timeout
    interval = 5
    while time.time() < deadline:
        body, err = _post(TOKEN_URL, {
            "client_id": client_id,
            "device_code": pending["device_code"],
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        })
        if body and "refresh_token" in body:
            return _save(slug, body, client_id)
        if err:
            code = err.get("error", "")
            if code in ("authorization_pending", "slow_down"):
                interval = int(err.get("interval", interval or 5))
                time.sleep(interval)
                continue
            if code == "access_denied":
                sys.exit("User MENOLAK otorisasi di HP.")
            if code == "expired_token":
                sys.exit("Device code kedaluwarsa.")
            sys.exit(f"Error token: {err}")
        time.sleep(interval)
    sys.exit("Timeout: user belum menyelesaikan verifikasi.")


def _save(slug, body, client_id):
    from auth import SCOPES as AUTH_SCOPES
    TOKENS_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(TOKENS_DIR, 0o700)
    creds = {
        "token": body["access_token"],
        "refresh_token": body["refresh_token"],
        "token_uri": TOKEN_URL,
        "client_id": client_id,
        "client_secret": json.load(open(CLIENT_SECRETS))["installed"]["client_secret"],
        "scopes": AUTH_SCOPES,
    }
    p = TOKENS_DIR / f"{slug}.json"
    p.write_text(json.dumps(creds, indent=1))
    os.chmod(p, 0o600)
    try:
        PENDING.unlink()
    except FileNotFoundError:
        pass
    print(f"OK, token tersimpan: {p}")
    return p


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "start":
        start()
    elif cmd == "poll" and len(sys.argv) == 3:
        poll(sys.argv[2])
    elif cmd == "poll" and len(sys.argv) == 4:
        poll(sys.argv[2], int(sys.argv[3]))
    else:
        print("Pakai: device_flow.py start | device_flow.py poll SLUG [timeout_detik]")
