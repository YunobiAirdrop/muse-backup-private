---
id: allox-checkin-harian
title: AlloX check-in harian
enabled: true
owner: goal:airdrop-testnet-farming-automation
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 08:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Check-in harian AlloX (https://app.allox.ai) — siklus 7 hari: 500/1000/1500/2000/2500/4000/5000 poin.

LANGKAH:
1. Jalankan script check-in: `cd ~/workspace/wallet-bot && ./venv/bin/python allox_checkin.py` (script dari allox_checkin_sig.py — auth SIWE via .privkey + POST /checkin, gasless).
2. Jika script gagal karena JWT expired: re-auth via `allox_api.py` (GET /auth/nonce → sign → POST /auth/verify → simpan ke .allox-token), lalu ulangi check-in.
3. Verifikasi: GET /auth/me atau /points — catat poin baru.
4. Update: ~/workspace/wallet-bot/allox-onboarding.json (poin, cycleDay, last_checkin) dan farming_status.json.
5. Jika check-in SUDAH dilakukan hari ini (cycleDay sama): diam, jangan kirim apa-apa.
6. Jika BERHASIL check-in baru: lapor singkat ke chat: "AlloX check-in day-N: +X poin, total Y poin."
7. Jika GAGAL (API down, auth gagal 3x): lapor errornya.

JANGAN edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md.
JANGAN ke sale.allox.ai (public sale BERBAYAR — bukan jalur farming).
