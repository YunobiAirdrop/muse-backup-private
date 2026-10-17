---
id: airdrop-farming-harian
title: Airdrop farming harian (7 testnet)
enabled: true
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 08:00:00
metadata:
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
# Airdrop Farming Harian — Testnet (7 proyek)

Jalankan orkestrasi farming harian untuk 7 testnet airdrop.

LANGKAH:
1. Jalankan: `python3 ~/workspace/airdrop-farming/farm.py` (tanpa --check-only).
   Ini membaca projects.json, mencatat run ke logs/farm-YYYY-MM-DD.log,
   dan mencetak ringkasan JSON (queued vs blocked).
2. Baca ringkasan JSON dari output. Untuk proyek yang QUEUED (plaza, sahara,
   multipli), lakukan interaksi dApp via browser task:
   - Plaza: claim test tokens di testnet.plaza.finance, lalu Earn (Zell swap),
     Leverage buy/sell sesuai langkah di projects.json.
   - Sahara AI: kerjakan daily tasks (Gobi bear, blog via Galxe, kirim test
     token, claim shards) + social quests.
   - Multipli: claim USDC/USDT/BTC, stake, earn tORBS.
   Untuk proyek BLOCKED (gte, neptune, variational, zenchain): JANGAN coba
   faucet captcha. Untuk gte/neptune/variational, interaksi dApp-nya tetap bisa
   jalan KALAU wallet sudah ada gas — cek saldo dulu via browser, skip kalau kosong.
3. Private key wallet TIDAK ada di worker ini. Untuk transaksi yang butuh
   signing, ambil private key dari Secure Vault (jalur yang sudah disetujui user).
   JANGAN tulis private key / seed phrase ke file, log, atau chat.
4. Update ~/workspace/airdrop-farming/STATUS.md: tambahkan bagian "Run YYYY-MM-DD"
   berisi apa yang berhasil, apa yang gagal, dan saldo gas per jaringan.
5. Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md.

LAPORAN (Bahasa Indonesia, singkat): per proyek — berhasil/gagal/blocked +
satu baris tindak lanjut HANYA jika butuh tindakan user (mis. faucet manual,
saldo gas habis).
