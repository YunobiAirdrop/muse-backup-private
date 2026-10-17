---
id: retry-upload-cepat
title: Retry upload cepat (3 jam)
enabled: true
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-09T03:55:14
  every: 3h
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC1A19182F60563D547FAFD991F185BC","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
**RETRY UPLOAD CEPAT (pendamping watchdog 20:00).** Tiap run:
1. List ~/workspace/youtube-otomatis/retry-queue/*.json (abaikan folder done/). Jika kosong → selesai diam-diam.
2. Untuk tiap antrean (urut gagal_pada paling lama): baca JSON + instruksi_path, verifikasi video_path ada. Umur = sekarang - gagal_pada. Jika < 23 jam → SKIP. Jika >= 23 jam → spawn browser task upload ke YouTube Studio sesuai instruksi_path (cek channel aktif benar, AI disclosure WAJIB dicentang, status Terjadwal ke slot_target; jika slot lewat/terisi pakai slot kosong terdekat).
3. SUKSES (terjadwal/tayang) → pindahkan JSON ke retry-queue/done/. GAGAL karena limit → biarkan di antrean. GAGAL sebab lain → biarkan + catat.
4. Jika ada yang SUKSES → laporkan singkat ke chat (judul + URL). Jika tidak ada yang eligible/tidak ada yang sukses → diam, jangan lapor.
Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md.
