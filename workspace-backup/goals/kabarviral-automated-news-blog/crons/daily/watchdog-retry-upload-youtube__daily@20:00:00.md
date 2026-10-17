---
id: watchdog-retry-upload-youtube
title: Watchdog retry upload YouTube (antrean batas harian)
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 20:00:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
**WATCHDOG RETRY UPLOAD YOUTUBE (aturan tetap user 2026-10-07: "jangan sampe mogok upload").**

Tiap run:
1. List ~/workspace/youtube-otomatis/retry-queue/*.json (abaikan folder done/).
2. Jika kosong → selesai, tidak perlu lapor.
3. Untuk tiap antrean (urutkan dari gagal_pada paling lama):
   a. Baca JSON + file instruksi_path. Verifikasi video_path ada di disk.
   b. Hitung umur = sekarang - gagal_pada. Jika < 23 jam → SKIP (limit YouTube rolling ±24 jam; coba besok).
   c. Jika >= 23 jam → spawn browser task: upload video ke YouTube Studio sesuai instruksi_path (cek channel aktif benar, judul, deskripsi, hashtag, thumbnail, AI disclosure WAJIB dicentang, status "Terjadwal" ke slot_target; jika slot_target sudah lewat/terisi, pakai slot kosong terdekat). Upload = approval user ("menunggu persetujuan", ketuk 20:00-23:00).
   d. SUKSES (terjadwal) → pindahkan JSON ke retry-queue/done/. GAGAL karena limit lagi → biarkan di antrean (dicoba besok). GAGAL sebab lain → catat di laporan, biarkan di antrean.
4. Laporkan: antrean diproses, yang berhasil (+URL), yang di-skip/masih antre + sebabnya.

**HEMAT TOKEN:** jangan baca file yang tak perlu. Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md.
