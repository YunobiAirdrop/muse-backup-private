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

ATURAN HEMAT (perintah user 2026-10-17): saldo wallet HARUS diirit-irit, jangan boros.
- Maksimal 5-10 transaksi per proyek per hari (jangan lebih)
- Pakai gas price rendah/standar, JANGAN buru-buru pakai gas mahal
- Skip transaksi yang gas-nya tidak wajar/mahal
- Prioritaskan transaksi yang paling penting buat eligibility (swap, stake)
- Kalau saldo gas menipis (< 0.01 ETH), STOP dan lapor user — jangan habiskan sampai 0

LANGKAH:
1. Cek saldo gas wallet farming 0xf0f25C36AC70E9d787a108eFB351626192C8107b di tiap jaringan SEBELUM mulai. Kalau kosong, skip proyek itu.
2. Jalankan: `python3 ~/workspace/airdrop-farming/farm.py` (tanpa --check-only).
   Ini membaca projects.json, mencatat run ke logs/farm-YYYY-MM-DD.log,
   dan mencetak ringkasan JSON (queued vs blocked).
3. Baca ringkasan JSON dari output. Untuk proyek yang QUEUED, lakukan interaksi dApp via browser task (MAKSIMAL 5-10 tx/proyek, hemat gas):
   - GTE/MegaETH: swap, earn, launch token di newton.xyz (pakai gas secukupnya)
   - Sahara AI: daily tasks (Gobi bear, blog via Galxe, kirim test token, claim shards)
   - Multipli: claim USDC/USDT/BTC, stake, earn tORBS
   - Mitosis: deposit, vault, trading
   Untuk proyek BLOCKED: JANGAN coba faucet captcha.
4. Private key wallet TIDAK ada di worker ini. Untuk transaksi yang butuh
   signing, ambil private key dari Secure Vault (jalur yang sudah disetujui user).
   JANGAN tulis private key / seed phrase ke file, log, atau chat.
5. Update ~/workspace/airdrop-farming/STATUS.md: tambahkan bagian "Run YYYY-MM-DD"
   berisi apa yang berhasil, apa yang gagal, dan saldo gas per jaringan.
6. Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md.

LAPORAN (Bahasa Indonesia, singkat): per proyek — berhasil/gagal/blocked +
satu baris tindak lanjut HANYA jika butuh tindakan user (mis. faucet manual,
saldo gas habis).
