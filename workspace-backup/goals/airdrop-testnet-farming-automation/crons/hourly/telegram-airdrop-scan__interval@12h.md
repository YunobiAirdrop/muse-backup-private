---
id: telegram-airdrop-scan
title: Scan info airdrop Telegram
enabled: true
owner: goal:airdrop-testnet-farming-automation
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-20T11:23:31
  every: 12h
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Scan channel-channel info airdrop di Telegram Web untuk peluang BARU.

KONTEKS: Sesi Telegram Web (web.telegram.org/k) sudah login di browser dan persist. User punya banyak channel info airdrop.

LANGKAH via browser.browse:
1. Buka Telegram Web, lihat daftar channel info airdrop
2. Baca pesan-pesan BARU (sejak scan terakhir — cek log di hidden_files/telegram-airdrop-scan-log.md untuk timestamp terakhir)
3. Identifikasi peluang airdrop BARU yang belum ada di log
4. Untuk tiap peluang baru: nilai kredibilitas (waspadai scam), catat nama/jenis/syarat/deadline/link
5. Update log dengan temuan baru + timestamp

ATURAN:
- JANGAN ikuti/klik link yang mencurigakan (pola referral scam, minta deposit, minta private key)
- JANGAN lakukan aksi apapun selain membaca dan mencatat
- Hanya LAPORKAN ke user jika ada peluang baru yang kredibel dan worth it (gratis, deadline jelas, proyek legitimate)
- Jika tidak ada yang baru: diam

LOG: ~/workspace/goals/airdrop-testnet-farming-automation/hidden_files/telegram-airdrop-scan-log.md
