---
id: faucet-sepolia-harian
title: Faucet Sepolia harian (Google Cloud)
enabled: true
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 09:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Klaim otomatis harian dari Google Cloud Sepolia faucet untuk wallet farming 0xf0f25C36AC70E9d787a108eFB351626192C8107b.

Langkah:
1. Buka https://cloud.google.com/application/web3/faucet/ethereum/sepolia via browser task
2. Pastikan jaringan "Ethereum Sepolia" terpilih (akun Google khususstokyunobi@gmail.com sudah login di browser)
3. Masukkan alamat 0xf0f25C36AC70E9d787a108eFB351626192C8107b ke kolom wallet
4. Klik tombol "Get 0.05 Sepolia ETH"
5. Catat hasil: sukses (dapat 0.05 ETH) atau kena cooldown 24 jam (normal, coba lagi besok)

Tidak perlu lapor ke user kecuali ada error yang tidak biasa (mis. akun Google logout, halaman berubah). Jika sukses atau cooldown normal, diam saja (catat ke ~/memory/YYYY-MM-DD.md).
