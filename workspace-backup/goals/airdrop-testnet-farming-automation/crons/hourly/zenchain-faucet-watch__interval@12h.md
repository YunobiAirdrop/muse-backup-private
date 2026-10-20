---
id: zenchain-faucet-watch
title: Pantau faucet Zenchain (down 2026-10-19) + klaim otomatis
enabled: true
owner: goal:airdrop-testnet-farming-automation
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-21T02:28:56
  every: 12h
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
PANTAU FAUCET ZENCHAIN (dibuat 2026-10-20 — faucet.zenchain.io down "This deployment is temporarily paused" sejak 2026-10-19; klaim ZCX tertunda).

Konteks: user mengotorisasi alur penuh 2026-10-19 (tweet X sudah terposting: https://x.com/Yunobi_id/status/2112099557609980306; lalu "faucet Zenchain langsung diklaim"). Wallet farming: 0xf0f25C36AC70E9d787a108eFB351626192C8107b.

Tiap run:
1. Cek https://faucet.zenchain.io via BROWSER (buka halaman live, lihat apakah form klaim muncul atau masih "Deployment Paused"). JANGAN andalkan curl atau text-fetch saja — pernah memberi false positive dari cache.
2. Jika masih "Deployment Paused": DIAM, jangan kirim apa-apa. Biarkan cron jalan terus.
3. Jika situs HIDUP dan form klaim muncul:
   a. Isi alamat EVM: 0xf0f25C36AC70E9d787a108eFB351626192C8107b
   b. Tempel link tweet https://x.com/Yunobi_id/status/2112099557609980306 ke form klaim (alur: masukkan alamat → Share on X → tempel link post → Receive ZCX)
   c. Klik Receive/Klaim. JANGAN login ke akun apa pun. Jika ada CAPTCHA yang tidak bisa dilewati, berhenti dan laporkan ke chat.
   d. Jika klaim BERHASIL: kirim pesan singkat ke chat ("Klaim ZCX Zenchain berhasil: <jumlah> ZCX masuk wallet farming."), lalu NONAKTIFKAN cron ini via cron.update(enabled=false) — tugas selesai, jangan jalan lagi.
   e. Jika klaim GAGAL karena error situs: laporkan singkat ke chat, biarkan cron aktif untuk coba lagi 12 jam berikutnya.
