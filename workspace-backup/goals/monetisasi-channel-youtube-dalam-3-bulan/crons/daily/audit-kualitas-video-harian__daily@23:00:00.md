---
id: audit-kualitas-video-harian
title: Audit kualitas video harian (5/channel, hapus yang jelek)
enabled: true
owner: goal:monetisasi-channel-youtube-dalam-3-bulan
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 23:00:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":4,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"ACA667F41D741CA79DEAF8377018C13F","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
AUDIT KUALITAS VIDEO HARIAN — perintah user 2026-10-19: cek semua channel 1:1, TONTON FULL tiap video (bukan sample), video jelek DIHAPUS (bukan private), duplikat DIHAPUS.

CARA KERJA:
1. Baca progres: ~/workspace/youtube-otomatis/hidden_files/audit-progres.json
2. Untuk tiap channel (20 channel), ambil 5 video BERIKUTNYA yang belum dicek (lanjutkan dari "terakhir_cek", mulai dari yang terbaru)
3. Untuk tiap video, TONTON FULL (download video lengkap, bukan 60 detik):
   a. Download FULL video via yt-dlp atau YouTube API
   b. Ekstrak frame tiap 10 detik → review SEMUA frame: kualitas visual konsisten? ada frame rusak/hitam? text overlay muncul di semua bagian penting?
   c. Analisa FULL audio: volume konsisten? ada bagian bisu? voiceover jelas dari awal sampe akhir?
   d. Cek alur cerita: hook di 3 detik pertama kuat? ada CTA tengah + akhir? pacing bagus atau monoton?
   e. Thumbnail → nilai: menarik? teks kebaca? (skor 1-5)
   f. Judul → hook kuat? ≤100 char? (skor 1-5)
   g. Views & umur → video >30 hari dengan <5 views = sinyal jelek
   h. Duplikat → judul sama dengan video lain di channel yang sama
4. KEPUTUSAN (berdasarkan tontonan FULL):
   - Video menarik dari awal sampe akhir, kualitas konsisten → PERTAHANKAN
   - Video membosankan, kualitas jelek di tengah, ATAU duplikat → HAPUS via API (videos.delete, BUKAN private)
   - Ragu → tonton 1x lagi bagian yang diragukan, lalu putuskan
5. Update audit-progres.json: terakhir_cek, total_cek, dihapus, dipertahankan per channel
6. Tulis log detail: ~/workspace/youtube-otomatis/hidden_files/audit-log-YYYY-MM-DD.json (catat alasan tiap video yang dihapus)

Gunakan yt-growth auth.py untuk API. Channel mapping di ~/workspace/youtube-otomatis/channels.yaml.

LAPORAN: ringkasan per channel (dihapus X, dipertahankan Y, contoh video yang dihapus + alasannya). JANGAN hapus video yang views >100 kecuali duplikat persis.
