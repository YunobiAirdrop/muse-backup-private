# PATCH: Watchdog + Retry-Cepat → API-first (siap tempel via cron.update dari chat WhatsApp asal)

Disiapkan 2026-10-12 20:23 WIB (proactivity research). Percobaan cron.update dari
konteks background DITOLAK runtime: jadwal yang delivery-nya ke chat layanan
eksternal (WhatsApp 7382e6cd-7263-4ede-983e-939bf507ecbf) hanya bisa diubah dari
chat asal itu. Agen utama: terapkan dari chat tersebut.

## Bukti kebutuhan
- Watchdog 2026-10-12 20:00 WIB: memeriksa 42 antrean, 2 ditutup (sudah live),
  sisanya berhenti di dialog "Verify it's you" Google — 39 antrean tak terproses.
- Definisi watchdog-retry-upload-youtube & retry-upload-cepat saat ini MASIH
  memerintahkan "spawn browser task upload ke YouTube Studio" — nol penyebutan API.
- Jalur API (yt-growth, token OAuth per channel) TERBUKTI berhasil hari yang sama:
  Weird World Daily (terjadwal 13 Okt 07:00, disclosure terverifikasi),
  Dark Case Files "Maura Murray" (terjadwal 13 Okt 07:00), 3 Shorts Jejak Buddha
  (terjadwal 13 Okt 19:00–19:10).
- Perbaikan yang sama sudah diterapkan permanen HANYA ke truecrime-en-harian &
  weird-en-harian (2026-10-12). Retry-cepat jalan lagi malam ini 21:55 WIB —
  tanpa patch, hampir pasti nabrak tembok verifikasi yang sama.

## Isi blok JALUR UPLOAD (sisipkan di awal body kedua cron, ganti langkah
## "spawn browser task" dengan "upload via API sesuai blok ini")

JALUR UPLOAD (perbaikan 2026-10-12 malam): upload WAJIB via API memakai
yt-growth (auth.py, token OAuth per channel; pola upload_video.py:
api_session(slug) → verifikasi channel mine=true cocok dengan channel JSON
antrean → resumable upload, privacyStatus private + publishAt ke slot_target /
slot kosong terdekat) — BUKAN browser Studio. Slug = field "channel" di JSON
antrean. Sebelum upload, cek daftar upload channel via API — bila judul sama
sudah ada, JANGAN dobel; tandai selesai. Slug tanpa token aktif (cek
auth.py status; token terkonfirmasi 17/17 per 2026-10-08, slug baru
inktime/macammacam belum terkonfirmasi) → fallback browser aturan lama; bila
modal verifikasi Google muncul → STOP item itu, jangan memicu login baru tanpa
kabari user dulu (aturan user 2026-10-11). Browser hanya untuk centang AI
disclosure SETELAH upload API; bila kepentok verifikasi, catat
"disclosure pending" di laporan — jangan paksa login.

Aturan lain TIDAK berubah: urut gagal_pada paling lama, skip <23 jam, sukses →
JSON pindah ke done/, gagal limit → tetap antre, hashtag minimal 3 termasuk
#foryou, thumbnail ditolak API (channel belum verifikasi HP) = catat saja.
