---
id: airdrop-hunter-x
title: Airdrop Hunter — cari peluang baru di X
enabled: true
owner: goal:airdrop-testnet-farming-automation
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 07:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
# Airdrop Hunter — Cari info airdrop baru di X/Twitter

TUGAS: Cari peluang airdrop testnet/mainnet baru dari X (Twitter), evaluasi, dan tambahkan yang layak ke sistem farming.

LANGKAH:
1. Cari di X via social.search dengan query seperti: "testnet airdrop", "airdrop farming", "new testnet launch airdrop", "crypto airdrop guide". Fokus ke post 7 hari terakhir yang ada panduan jelas (faucet link, langkah-langkah).

2. Untuk tiap peluang, catat: nama proyek + blockchain, link faucet (kalau testnet), link dApp/website resmi, syarat eligibility, estimasi effort.

3. FILTER — hanya ambil yang: testnet GRATIS (tidak butuh deposit mainnet), ada faucet yang bisa diakses (tidak butuh captcha berbayar/kyc), bukan scam (cek website resmi, twitter verified/follower banyak, bukan link phising), belum ada di ~/workspace/airdrop-farming/projects.json.

4. Untuk yang LOLOS filter (maksimal 3 per hari): tambahkan ke ~/workspace/airdrop-farming/projects.json dengan status "queued", tulis detail di ~/workspace/airdrop-farming/STATUS.md bagian "Peluang Baru YYYY-MM-DD". Kalau butuh faucet manual/captcha yang tidak bisa otomatis → catat sebagai "butuh tindakan user".

5. Update ~/memory/YYYY-MM-DD.md dengan ringkasan temuan.

LAPORAN ke chat (Indonesia, singkat): HANYA kalau ada peluang baru yang ditambahkan. Format: nama proyek + 1 baris kenapa menarik + link. Kalau tidak ada temuan baru: DIAM.
