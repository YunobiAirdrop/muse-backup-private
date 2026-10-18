---
id: otpmurah-site-watch
title: Pantau situs OTPMurah (down 2026-10-18)
enabled: true
owner: goal:monetisasi-channel-youtube-dalam-3-bulan
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-18T15:31:51
  every: 1h
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","provider":"main","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
CEK KETERSEDIAAN SITUS OTPMURAH (watch — dibuat 2026-10-18 karena otpmurah.id NXDOMAIN/down total).
1. Cek: `curl -sI --max-time 20 https://otpmurah.id` dan catat hasilnya. Opsional: `nslookup otpmurah.id`.
2. Jika situs BISA diakses (ada respons HTTP, mis. 200/301/302): kirim pesan singkat ke chat: "Situs OTPMurah sudah bisa diakses lagi. Mau saya coba login ulang pakai akun stokwebyakis@gmail.com?" JANGAN login sendiri — tidak ada password yang tersimpan.
3. Jika masih tidak bisa diakses: diam, jangan kirim apa-apa.
4. Jangan memesan/membeli nomor apa pun. Ini hanya cek ketersediaan situs.
