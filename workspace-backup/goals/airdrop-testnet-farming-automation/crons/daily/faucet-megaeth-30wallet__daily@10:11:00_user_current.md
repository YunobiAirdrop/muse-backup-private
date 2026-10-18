---
id: faucet-megaeth-30wallet
title: Faucet MegaETH 30 wallet harian
enabled: false
owner: goal:airdrop-testnet-farming-automation
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 10:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Klaim harian MegaETH faucet untuk 30 wallet farming (PARALEL, bukan 1:1), lalu konsolidasi ke wallet utama.

Wallet list: ~/workspace/airdrop-farming/wallets-30.json (30 alamat)
Private keys: ~/workspace/airdrop-farming/wallets-30-private.json
Wallet utama: 0xf0f25C36AC70E9d787a108eFB351626192C8107b

Langkah (kerjakan PARALEL dalam batch, mis. 5-6 wallet per batch):
1. Untuk tiap dari 30 alamat di wallets-30.json:
   - Buka https://testnet.megaeth.com/ via browser task (boleh beberapa browser task paralel)
   - Masukkan alamat ke kolom faucet, selesaikan verifikasi Turnstile, klik "GET TESTNET TOKENS"
   - Catat yang berhasil vs yang kena cooldown 24 jam
2. Untuk wallet yang berhasil dapat token: kirim seluruh saldo ETH (minus gas) ke 0xf0f25C36AC70E9d787a108eFB351626192C8107b menggunakan private key dari wallets-30-private.json via script Python (web3). Bisa batch via script.
3. Catat ringkasan ke ~/memory/YYYY-MM-DD.md: berapa wallet berhasil claim, total ETH terkonsolidasi

Tidak perlu lapor ke user kecuali ada error sistem (bukan cooldown normal).
