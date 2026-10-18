---
id: mining-restart-retry-18okt
title: Retry restart mining PoW (janji 11:00-12:00 WIB 18 Okt)
enabled: true
owner: goal:airdrop-testnet-farming-automation
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-10-18T11:30:00
timeout_secs: 1800
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Tindak lanjut janji ke user tadi malam: coba restart sesi mining PoW Sepolia yang mati/zombie.

Konteks: 9 wallet mining (indeks 1-9 di ~/workspace/airdrop-farming/wallets-30.json) mining SepETH di sepolia-faucet.pk910.de sesi 12 jam. Jendela browser mereka tertutup → server menahan sesi zombie yang menolak sesi baru sampai sesi ~12 jam kedaluwarsa (~11:00–12:00 WIB 18 Okt 2026). Wallet #8 sempat masih hashing; yang lain tidak terverifikasi.

Alamat wallet mining (indeks 1-9, JANGAN pakai indeks 0 = wallet utama 0xD386112D6dD42cA5aaDE2cfc42339A3e8B209b74 yang dikecualikan karena CONCURRENCY_LIMIT):
1. 0xfaD4A10d74D74e90C4c042cCa832CfDdFf5689bf
2. 0x3D8b397a13a0b6b2DE1612Ceb2549083f2a56EF0
3. 0x5061680395FeECb710ca05FE278A649f972E7314
4. 0xFEF5C460B0e80A1d0Ab4D9B623EB77433d47f35E
5. 0x3Fea13885E6880E459977Bd92107838Ab7aBdAfB
6. 0xC4ED373933175B63c9a36f1bf2e48cc366D6bec4
7. 0x9bAEFd20cFd41fE9C38bdD957dDA17FE1b4B13eb
8. 0xcBaC8eA4464630e020214b599ab5BA654A0B51F9
9. 0xDd4fB99be3A66A3E06424155f9e76a117b6F9FB6

Langkah:
1. Untuk tiap wallet, buka sepolia-faucet.pk910.de di browser, masukkan alamat wallet, cek status sesi: kalau masih hashing, JANGAN diganggu; kalau mati/zombie/ditolak, coba mulai sesi mining baru.
2. ATURAN KERAS: jendela browser mining TIDAK BOLEH ditutup dan task browser TIDAK BOLEH auto-finish — jendela tertutup = sesi mati dan server bisa blokir restart ~12 jam.
3. Kalau server masih menolak semua (sesi zombie belum kedaluwarsa), catat dan berhenti — jangan spam retry.

Lapor singkat ke chat: berapa wallet berhasil restart, berapa masih zombie.
