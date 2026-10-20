---
id: asentum-harian-yunobi-yapp
title: 'Asentum harian (akun yunobi_yapp): check-in + faucet'
enabled: true
owner: goal:airdrop-testnet-farming-automation
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 08:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Jalankan rutinitas harian Asentum untuk akun BARU user (bukan akun lama @Yunobi_id yang sudah diputus permanen).

AKUN: dashboard https://airdrop.asentum.com/dashboard — username "yunobi_ip", login X @Yunobi_yapp (akun Google stokyunobiads@gmail.com). Wallet utama tertaut: ase15n68dk4dnxxkthjptfrpw2nvynmkd2jk6d20pk (bot @AsentumBot, sudah ter-pairing ke dashboard + Auras).

LANGKAH:
1. Buka dashboard lewat browser task. Sesi login yunobi_ip seharusnya masih aktif. Bila sudah logout, JANGAN login ulang sendiri — laporkan singkat ke chat utama dan selesai.
2. Lakukan CHECK-IN harian bila tersedia (+15 XP, menjaga streak).
3. Klaim FAUCET ASE bila tombol klaim aktif. Bila masih countdown, catat kapan klaim berikutnya.
4. Kerjakan misi harian on-chain yang tersedia hari itu:
   - Swap di Auras: swap ±1 ASE ke token lain yang tersedia. Saat bot @AsentumBot meminta PIN untuk tanda tangan ("Reply with your PIN to sign and submit"), baca PIN dari file ~/workspace/wallet-bot/.asentum-pin lalu balas ke prompt bot itu. JANGAN menulis angka PIN di laporan, log, state, atau chat mana pun.
   - Kirim ASE: kirim 0,5 ASE dari bot ke ase1tydz4m3j3d0j9wrgga7ggax8ds88m5nq2wlnsw. Tanda tangani dengan PIN dari file yang sama bila diminta.
   - Jumlah transaksi JANGAN melebihi angka di atas.
5. Simpan state terakhir (tanggal, XP, rank, streak, saldo ASE, status check-in/faucet/misi) ke ~/workspace/goals/airdrop-testnet-farming-automation/hidden_files/asentum-yapp-state.json (tanpa PIN).
6. Laporkan RINGKAS ke chat utama (1-2 baris): check-in, faucet, misi yang selesai, XP/rank/saldo akhir.

LARANGAN KERAS:
- JANGAN PERNAH memasukkan seed phrase atau private key apa pun, di mana pun. PIN hanya boleh dibaca dari ~/workspace/wallet-bot/.asentum-pin dan hanya untuk menjawab prompt tanda tangan bot.
- JANGAN login ke akun Asentum lama (@Yunobi_id).
