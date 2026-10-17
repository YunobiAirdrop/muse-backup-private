# Antrean Retry Upload YouTube

Worker cron channel yang uploadnya GAGAL karena batas harian YouTube menulis satu file
JSON per video ke folder ini. Watchdog harian (`watchdog-retry-upload-youtube`,
20:00 WIB) mengerjakan antrean: upload ulang video yang gagal_pada-nya sudah
>= 23 jam lalu, lalu memindahkan JSON ke `done/`.

## Format JSON

Nama file: `{channel}-YYYY-MM-DD.json` (satu file per video gagal; jika channel
yang sama gagal lagi di hari berbeda, pakai tanggal gagal yang baru).

```json
{
  "channel": "mystery-en",
  "video_path": "/home/hatch/workspace/youtube-otomatis/mystery-en/video/2026-10-07.mp4",
  "instruksi_path": "/home/hatch/workspace/youtube-otomatis/mystery-en/upload-instruksi-2026-10-07.md",
  "slot_target": "2026-10-09 07:00 WIB",
  "gagal_pada": "2026-10-07T21:30:00+07:00",
  "sebab": "Batas upload harian telah tercapai"
}
```

- `video_path` dan `instruksi_path`: path absolut. File instruksi berisi judul,
  deskripsi, hashtag, thumbnail, AI disclosure, dan channel tujuan — lengkap
  seperti instruksi upload normal.
- `slot_target`: slot tayang kosong terdekat saat antrean ditulis (watchdog boleh
  menggeser ke slot kosong yang lebih baru jika slot ini sudah terisi).
- `gagal_pada`: waktu kegagalan (WIB, ISO 8601). Watchdog hanya mengerjakan
  entri yang umurnya >= 23 jam agar tidak menabrak limit 24 jam yang rolling.
- Jangan tulis antrean untuk kegagalan BUKAN limit harian (itu di-retry segera
  oleh worker saat itu juga).

## Guard anti-duplikat (disetujui user 2026-10-14)

Sebelum video di antrean diunggah ulang, judulnya dicek ke playlist uploads
channel via `yt-growth/cek_duplikat.py` (API resmi). Kalau judulnya SUDAH live,
JSON dipindah ke `done/` dan video TIDAK diunggah ulang — mencegah duplikat
0-views seperti kasus TalesOfDreadTV & TrueCaseFilesTV (Okt 2026).

Implementasi: cron `pra-screen-duplikat-retry` (tiap 1 jam, dari main chat)
menyapu antrean dan menyingkirkan yang sudah live. Dipisah dari cron watchdog
karena watchdog/retry-cepat dimiliki chat WhatsApp dan bodinya hanya bisa
diubah dari sana.
