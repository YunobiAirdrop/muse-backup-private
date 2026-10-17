# BANK VIDEO

Konsep (perintah user 2026-10-10): video yang tidak bisa diupload karena batas
harian YouTube TIDAK dibuang — disimpan sebagai **bank video** (stok konten siap
tayang) untuk diupload massal setelah verifikasi HP selesai dan limit naik.

## Cara kerja
- Folder ini (`retry-queue/`) ADALAH bank video. Tiap JSON = 1 video siap upload
  (video_path, judul, deskripsi, thumbnail, slot_target, instruksi upload).
- Produksi harian TETAP jalan full speed walau upload macet — setiap video yang
  gagal upload karena limit OTOMATIS masuk bank (ditulis worker, bukan retry langsung).
- Watchdog (20:00) + retry-cepat (tiap 3 jam) mengupload dari bank saat jendela
  limit terbuka — prioritas ke yang paling lama mengantre.
- Setelah verifikasi HP: bank dikuras via upload massal (antrean terlama dulu).

## Aturan
- JANGAN hapus file video yang masih punya JSON di bank.
- JSON yang sudah terupload → pindah ke `done/`.
- Verifikasi integritas bank: tiap audit 3-harian cek video_path masih ada.

## Status
Lihat `~/workspace/goals/monetisasi-channel-youtube-dalam-3-bulan/hidden_files/scoreboard.md`
untuk jumlah bank per channel.
