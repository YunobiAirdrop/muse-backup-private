---
id: retry-upload-empires-short3
title: Retry upload short 3 Lost Empires
enabled: true
owner: goal:channel-youtube-internasional-berbahasa-inggris
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-10-07T12:11:00
timeout_secs: 7200
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","origin_provider":"main","chat_kind":"direct","provider":"main","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Retry upload short ke-3 channel YouTube "Lost Empires" (@AncientEmpiresTV, akun khususstokyunobi@gmail.com) yang gagal pada 2026-10-06 karena batas upload harian YouTube. Dua shorts lainnya ("The City Carved Into a Cliff", "This Desert Hid a Lost Kingdom") sudah sukses terupload dan terjadwal 7 Okt 2026 07:00 WIB.

Langkah:
1. Spawn browser task via browser.spawn_task dengan file upload /home/hatch/workspace/youtube-otomatis/empires-en/shorts/2026-10-05-s3.mp4 (kirim lewat parameter files, bukan disebut sebagai path di task).
2. Instruksi task (self-contained): buka YouTube Studio (https://studio.youtube.com/), gunakan channel switcher untuk memilih channel "Lost Empires" (@AncientEmpiresTV) dan VERIFIKASI nama channel sebelum upload. Upload short: judul "The Treasury's 2,000-Year-Old Secret"; deskripsi "Watch the full story on Lost Empires.\n\n#shorts #history #archaeology"; tags: petra, shorts, history, archaeology; audiens "Not made for kids" / "Tidak Dibuat untuk Anak-Anak"; WAJIB centang AI disclosure ("Altered content / Ya, AI digunakan"); visibilitas Dijadwalkan 8 Oktober 2026 pukul 07:00 WIB (GMT+07:00); verifikasi waktu tayang di halaman detail video. Laporkan URL short hasil upload.
3. Sesi Google khususstokyunobi@gmail.com diperkirakan masih valid; jika muncul halaman login/password, laporkan sebagai blocker, jangan tebak password.
4. Jika upload sukses: verifikasi isi /home/hatch/workspace/youtube-otomatis/empires-en/upload-terakhir.txt adalah "shorts:2026-10-06".
5. Jika kena batas upload harian lagi: JANGAN buat cron baru sendiri; laporkan statusnya saja ke chat.
6. Upload butuh ketukan persetujuan user ("menunggu persetujuan") — siapkan semuanya dan tunggu.

Catatan: jangan edit MEMORY.md; observasi ke ~/memory/2026-10-07.md.
