---
id: auto-farm-tx-harian
title: Auto-farm transaksi harian
enabled: true
owner: goal:airdrop-testnet-farming-automation
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 09:11:00
timeout_secs: 43200
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","provider":"main","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Jalankan auto-farming transaksi harian untuk airdrop.

Perintah: `cd ~/workspace/wallet-bot && ./venv/bin/python auto_farm.py`

Script ini:
- Mengirim self-transfer acak (jumlah & jeda random) ke Sepolia, Elysium (DogeOS dinonaktifkan karena sudah ditangani cron 08:00)
- Default 16 tx/hari (8 Sepolia + 8 Elysium), berhenti otomatis jika saldo < 0.01
- Mencatat semua tx ke auto_farm.log

Jika script error atau saldo di bawah ambang, laporkan ke chat. Jika sukses, diam (catat ke ~/memory/YYYY-MM-DD.md saja).
