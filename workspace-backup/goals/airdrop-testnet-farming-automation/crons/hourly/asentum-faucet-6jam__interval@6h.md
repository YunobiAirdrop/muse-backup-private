---
id: asentum-faucet-6jam
title: Asentum faucet tiap 6 jam
enabled: false
owner: goal:airdrop-testnet-farming-automation
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-20T04:40:30
  every: 6h
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","provider":"main","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Klaim faucet testnet Asentum (5 ASE per 6 jam) via browser.

LANGKAH:
1. Gunakan browser.browse (task_id: "new") untuk buka https://airdrop.asentum.com/dashboard
2. Sesi login X (@Yunobi_id via Privy) seharusnya masih persist. Jika sudah logout, JANGAN coba login ulang sendiri — laporkan saja.
3. Verifikasi wallet Telegram masih tertaut (ase1tydz4m3j3d0j9wrgga7ggax8ds88m5nq2wlnsw)
4. Klik tombol "GET 5 TEST ASE"
5. Jika tombol masih cooldown (belum 6 jam), catat dan selesai — bukan error.
6. Konfirmasi pesan sukses ("Sent 5 ASE to your linked wallet").

LAPOR: singkat saja — berhasil/gagal/cooldown + jumlah ASE yang diklaim. Jika gagal 2x berturut-turut, beri tahu user.
