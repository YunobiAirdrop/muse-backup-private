---
id: konsolidasi-mining-harian
title: Konsolidasi hasil mining ke wallet utama
enabled: true
owner: goal:airdrop-testnet-farming-automation
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 11:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Konsolidasi hasil mining PoW faucet ke wallet utama.

9 wallet mining (dari ~/workspace/airdrop-farming/wallets-30.json index 1-9):
- 0xD386112D6dD42cA5aaDE2cfc42339A3e8B209b74
- 0x3D8b397a13a0b6b2DE1612Ceb2549083f2a56EF0
- 0x5061680395FeECb710ca05FE278A649f972E7314
- 0xFEF5C460B0e80A1d0Ab4D9B623EB77433d47f35E
- 0x3Fea13885E6880E459977Bd92107838Ab7aBdAfB
- 0xC4ED373933175B63c9a36f1bf2e48cc366D6bec4
- 0x9bAEFd20cFd41fE9C38bdD957dDA17FE1b4B13eb
- 0xcBaC8eA4464630e020214b599ab5BA654A0B51F9
- 0xDd4fB99be3A66A3E06424155f9e76a117b6F9FB6

Private keys: ~/workspace/airdrop-farming/wallets-30-private.json
Wallet utama: 0xf0f25C36AC70E9d787a108eFB351626192C8107b

Langkah:
1. Cek saldo Sepolia ETH tiap 9 wallet via RPC https://ethereum-sepolia-rpc.publicnode.com
2. Untuk wallet yang saldonya > 0.001 ETH: kirim 90% saldo ke wallet utama (sisakan buat gas) via web3 Python memakai private key dari wallets-30-private.json
3. Catat ke ~/memory/YYYY-MM-DD.md: berapa wallet dikonsolidasi, total ETH terkirim

Jangan ganggu sesi mining yang masih berjalan di browser. Tidak perlu lapor ke user kecuali ada error.
