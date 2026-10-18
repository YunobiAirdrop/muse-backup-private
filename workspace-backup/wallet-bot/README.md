# wallet-bot — Independent Chromium + MetaMask

Lingkungan browser **independen** untuk otomasi wallet/dApp, TERPISAH dari
browser terkelola runtime (yang ekstensinya diblokir). Jangan sentuh profil
browser runtime dari sini.

## Isi

| Path | Keterangan |
|---|---|
| `launch.py` | Launcher utama |
| `venv/` | Python venv (Playwright 1.64.0) |
| `profile/` | Profil Chromium PERSISTEN (wallet import tersimpan di sini) |
| `ext/metamask/` | MetaMask 13.52.0 resmi (GitHub Consensys, SHA256 terverifikasi) |
| `proof-metamask.png` | Bukti screenshot onboarding MetaMask |

## Cara pakai

```bash
cd ~/workspace/wallet-bot
./venv/bin/python launch.py              # buka, screenshot onboarding, tutup
./venv/bin/python launch.py --keep-alive # buka dan biarkan jalan (Ctrl+C berhenti)
```

Skrip otomatis:
1. Menyalakan Xvfb di `:99` (VM tidak punya display).
2. Meluncurkan Chromium headed (Playwright, profil persisten di `profile/`).
3. Memuat MetaMask via `--load-extension`.
4. Mendeteksi extension ID, membuka `home.html`, screenshot ke `proof-metamask.png`.

Extension ID MetaMask di profil ini: `ocicphjefllmdjaioocoolnmfbjdlcfg`
(dibangkitkan Chrome karena build GitHub tidak menyertakan `key`;
ID stabil selama path `ext/metamask/` dan `profile/` tidak berubah).

## Import wallet (nanti, manual)

Buka `chrome-extension://ocicphjefllmdjaioocoolnmfbjdlcfg/home.html`
lalu "I have an existing wallet". **JANGAN tulis seed phrase / private key
di file, chat, atau repo mana pun** — pakai sekali secara transient.

## Catatan / keterbatasan

- Chromium "Google Chrome for Testing" 156 via Playwright (`~/.cache/ms-playwright/`).
- Headless TIDAK dipakai: ekstensi hanya andal di mode headed + Xvfb.
- RAM VM ketat (~7GB, hampir penuh): jalankan SATU instance browser saja,
  tutup setelah selesai. Flag hemat: `--disable-dev-shm-usage`, `--no-sandbox`.
- `clients2.google.com` diblokir proxy egress VM → ekstensi diambil dari
  rilis resmi GitHub MetaMask (bukan Chrome Web Store). ID ekstensi beda
  dari versi Web Store (`nkbihfbeogaeaoehlefnkodbefgpgknn`) tapi kode identik.
- Jaringan: memakai egress langsung VM (tanpa proxy khusus).
- Jangan jalankan berbarengan dengan cron render video (risiko OOM).
