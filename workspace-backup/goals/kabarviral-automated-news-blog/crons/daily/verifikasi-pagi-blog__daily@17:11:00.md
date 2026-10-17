---
id: verifikasi-pagi-blog
title: Verifikasi pagi hasil posting blog
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 17:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  predicted_connector_permissions:
  - connector: gmail
    method: users.messages.list
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Laporan verifikasi harian hasil posting blog (goal kabarviral-automated-news-blog). User meminta laporan ringkas ini setiap hari.

Langkah kerja:
1. Jalankan `python3 ~/workspace/blog-otomatis/verifikasi_pagi.py` dan baca output JSON-nya: jumlah artikel per blog, selisih vs kemarin, dan judul yang baru terbit hari ini. Daftar blog dibaca dinamis dari config.json (ikut bertambah saat ekspansi).
2. Cek riwayat run terbaru cron `blog-otomatis-harian` (cron.runs, limit 3): apakah run pagi ini sukses, gagal, atau parsial, dan apa penyebabnya (mis. kuota AI habis, VM restart, error posting).
3. Cek Gmail 24 jam terakhir untuk notifikasi kegagalan posting Blogger (email mailer-daemon "Delivery Status Notification (Failure)" ke alamat *@blogger.com) memakai skill gmail.
4. Susun laporan ringkas Bahasa Indonesia untuk chat: tiap blog (artikel baru hari ini + total), blog yang tidak dapat artikel baru + kemungkinan penyebabnya, dan satu baris tindak lanjut HANYA jika ada yang butuh tindakan user.
5. Kirim laporan ke chat setiap hari, termasuk saat hasilnya nihil — ini laporan harian yang diminta user.

Jangan membuat file laporan per-run; snapshot pembanding sudah dikelola otomatis oleh script di hidden_files goal. Jangan edit MEMORY.md.
