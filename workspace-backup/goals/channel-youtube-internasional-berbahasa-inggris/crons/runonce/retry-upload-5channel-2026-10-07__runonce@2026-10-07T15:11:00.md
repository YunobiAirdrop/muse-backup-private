---
id: retry-upload-5channel-2026-10-07
title: Retry upload 5 channel (batas harian YouTube)
enabled: true
owner: goal:channel-youtube-internasional-berbahasa-inggris
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-10-07T15:11:00
timeout_secs: 14400
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC00E527C90CD516F97C16548FF53301","conversation_id":"whatsapp_channel","provider":"whatsapp","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
# RETRY UPLOAD — 4 channel yang kena batas upload harian YouTube 2026-10-06

KONTEKS: Pada 2026-10-06 malam, akun Google khususstokyunobi@gmail.com mencapai BATAS UPLOAD HARIAN YouTube (12 video terupload hari itu) — semua upload setelah ~21:25 WIB ditolak dengan pesan "Batas upload harian telah tercapai". Login Google sudah pulih (kata sandi baru tersimpan di vault). Batas harian YouTube reset tengah malam waktu Pasifik (= 14:00 WIB). Job ini jalan ~15:00 WIB 2026-10-07, seharusnya batas sudah reset.

INSTRUKSI UMUM (berlaku untuk semua upload di bawah):
- Login YouTube Studio (studio.youtube.com) dengan akun khususstokyunobi@gmail.com. Kata sandi tersimpan di vault — pakai credential_fill, JANGAN tebak sandi.
- SEBELUM upload pertama: coba buka dialog upload. Jika masih muncul "Batas upload harian telah tercapai", HENTIKAN SEMUA — laporkan batas belum reset, jangan spam percobaan.
- Setiap upload: VERIFIKASI channel aktif via pemilih channel (JANGAN upload ke channel yang salah).
- Setiap upload: isi judul + deskripsi + tag persis seperti di bawah, audiens "Tidak dibuat untuk anak-anak", WAJIB centang AI disclosure "konten yang diubah" = Ya, cek tab Pemeriksaan (copyright), lalu Visibilitas = "Terjadwal" pada waktu yang ditentukan (zona Asia/Jakarta).
- Upload SATU PER SATU secara berurutan (jangan paralel — satu sesi browser). Setelah tiap upload, catat URL-nya.
- Jika butuh file di VM: minta via browser-input grant seperti biasa.

## 1. LOST EMPIRES (@AncientEmpiresTV) — 1 short
- File: /home/hatch/workspace/youtube-otomatis/empires-en/shorts/2026-10-05-s3.mp4
- Judul: The Treasury's 2,000-Year-Old Secret
- Deskripsi: "Watch the full story on Lost Empires.\n\n#shorts #history #archaeology"
- Tag: petra, shorts, history, archaeology
- Jadwal: 8 Okt 2026 07:00 WIB

## 2. STRANGE TALES (@StrangeTales-g6n) — 3 shorts
File & metadata lengkap di /home/hatch/workspace/youtube-otomatis/strange-tales/2026-10-06/ (baca scripts.md untuk judul/deskripsi/tag tiap short):
- short 1: strange-tales-2026-10-06-tardigrade.mp4 — jadwal 8 Okt 2026 03:00 WIB
- short 2: strange-tales-2026-10-06-jellyfish.mp4 — jadwal 8 Okt 2026 07:00 WIB
- short 3: strange-tales-2026-10-06-dancing-plague.mp4 — jadwal 8 Okt 2026 21:00 WIB

## 3. LIMA MISTERI (@LimaMisteri) — 1 video panjang
- File: /home/hatch/workspace/lima-misteri/video/video-2026-10-06.mp4
- Thumbnail kustom: /home/hatch/workspace/lima-misteri/thumbnail-2026-10-06.jpg
- Judul, deskripsi, tag: baca /home/hatch/workspace/lima-misteri/upload-instruksi-2026-10-06.md (ABAIKAN tanggal jadwal di file itu — pakai yang di bawah)
- Jadwal: 8 Okt 2026 19:00 WIB

## 4. ECHOES OF HISTORY (@EchoesOfThePast-e9m) — 1 video panjang
- File: /home/hatch/workspace/youtube-otomatis/history-en/video/2026-10-06.mp4
- Thumbnail kustom: /home/hatch/workspace/youtube-otomatis/history-en/thumbnail-2026-10-06.jpg
- Judul, deskripsi, tag: baca /home/hatch/workspace/youtube-otomatis/history-en/upload-2026-10-06.json (ABAIKAN tanggal jadwal di file itu — pakai yang di bawah)
- Jadwal: 8 Okt 2026 07:00 WIB

LAPORAN AKHIR (WAJIB): daftar tiap video — channel, judul, URL, status terjadwal (tanggal+jam), konfirmasi AI disclosure. Jika ada yang gagal, sebutkan penyebab persisnya. Setelah semua selesai, tulis ringkasan ke /home/hatch/workspace/youtube-otomatis/retry-2026-10-07.md.
