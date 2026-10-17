---
id: retry-upload-tinybuilders-malam-2026-10-08
title: Retry upload Tiny Builders malam (4 video)
enabled: true
owner: goal:channel-youtube-internasional-berbahasa-inggris
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-10-08T22:00:00
timeout_secs: 3600
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"ACE378BA13DC6A8533376D8DD0B37014","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Retry upload 4 video Tiny Builders yang antre di ~/workspace/youtube-otomatis/retry-queue/ (tinybuilders-long + short1/2/3, gagal lagi 2026-10-08 14:33 karena batas harian YouTube belum kebuka).

Langkah:
1. Baca tiap file JSON antrean untuk video_path dan instruksi_path.
2. Coba upload via browser task ke channel Tiny Builders SESUAI aturan anti-mogok: jika gagal karena batas harian → tulis ulang antrean JSON (jangan retry langsung); jika gagal sebab lain → retry saat itu juga.
3. Upload butuh ketukan persetujuan user di aplikasi Muse (beri tahu user tiap tahap: "ketukan tersisa: X").
4. Pindahkan file JSON yang BERHASIL terupload ke retry-queue/done/.

Laporan ke user (Bahasa Indonesia, singkat): berapa video berhasil tayang + URL-nya, berapa yang masih antre dan sebabnya.
