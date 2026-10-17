# Instruksi Upload YouTube — Horor Harian 2026-10-10
Target tayang TERJADWAL: 2026-10-11 19:00 WIB (prime time). Ketukan persetujuan user: malam ini 20:00-22:00 WIB.
HARI INI: upload 1 LONG VIDEO SAJA (pola bergantian; kemarin 2026-10-09 upload 3 SHORTS dari video 2026-10-08 yang tayang hari ini 2026-10-10 19:00 WIB). TIDAK ada shorts baru hari ini.

## LANGKAH 0 — WAJIB: CEK CHANNEL AKTIF
Buka YouTube Studio (studio.youtube.com). Pastikan channel yang AKTIF adalah:
- Nama: "Kisah Horor"
- Handle: @KisahPOV
- Akun Google: khususstokyunobi@gmail.com
JANGAN upload ke @ceritarakyat862. PERNAH terjadi: Studio terbuka di channel SALAH "Midnight Dread Tales" — verifikasi ulang sebelum upload. Kalau channel aktif salah, ganti channel dulu. Kalau tidak bisa ganti, HENTIKAN dan laporkan.

## PENTING — AI DISCLOSURE
WAJIB centang opsi "Altered content / konten yang diubah AI" (label konten AI wajib YouTube).

## ATURAN HASHTAG KHUSUS LONG
Hashtag ditaruh di DESKRIPSI (bukan di judul). Judul long TANPA hashtag.

## LONG VIDEO (12,1 menit — "Suster Ngesot di Rumah Sakit Tua")
File video: /home/hatch/workspace/horor-otomatis/video/2026-10-10-youtube.mp4
File thumbnail: /home/hatch/workspace/horor-otomatis/thumbnail-2026-10-10.jpg
Judul: Suster Ngesot Itu Nyuruh Aku Gantian Jaga Shift!
Deskripsi:
Malam pertama jaga shift di rumah sakit tua yang mau tutup, Dimas diganggu suster tanpa kaki yang katanya meninggal 20 tahun lalu. Tapi ternyata suster itu masih "jaga shift"... dan dia menyelamatkan seorang pasien dari kesalahan dosis obat. Sampai akhirnya Dimas menemukan satu nama di daftar korban kebakaran 2004 yang bikin darahnya berhenti mengalir: namanya sendiri. Cerita ini bikin saya mikir ulang soal siapa yang sebenarnya masih hidup.
Kalau kamu suka cerita horor kayak gini, subscribe channel Kisah Horor — tiap hari ada cerita baru yang bikin merinding.
Rekomendasi:
🛒 ThePods Gen 4 TWS Bluetooth ANC - Rp339.520: https://s.shopee.co.id/8AWYYltgKB
🛒 Puzzle Kayu Edukasi Montessori - Rp21.890: https://s.shopee.co.id/9pemZScr45
Subscribe channel Kisah Horor untuk cerita horor tiap hari.
#horor #ceritahoror #misteri #susterngesot #rumahsakitangker
Tag YouTube: cerita horor, hantu indonesia, suster ngesot, rumah sakit angker, kisah horor
Thumbnail: upload thumbnail-2026-10-10.jpg sebagai thumbnail kustom (channel sudah verifikasi HP → thumbnail kustom aktif).
Visibilitas: Terjadwal → 2026-10-11 19:00 WIB. PERHATIAN: Studio di VM bisa memakai zona waktu berbeda — periksa kolom "Jadwalkan untuk" dan sesuaikan offset-nya supaya video tayang tepat 2026-10-11 19:00 WIB (Asia/Jakarta).

## ANTI-MOGOK UPLOAD
- Gagal karena "Batas upload harian telah tercapai" (atau pesan limit harian lain): JANGAN retry saat itu juga. Tulis antrean JSON ke /home/hatch/workspace/youtube-otomatis/retry-queue/Kisah Horor-2026-10-10.json format {"channel":"Kisah Horor","video_path":"/home/hatch/workspace/horor-otomatis/video/2026-10-10-youtube.mp4","instruksi_path":"/home/hatch/workspace/horor-otomatis/upload-instruksi-2026-10-10.md","slot_target":"2026-10-11 19:00 WIB","gagal_pada":"<timestamp>","sebab":"..."} — watchdog harian akan mengerjakannya.
- Gagal karena sebab LAIN: perbaiki dan retry SEGERA saat itu juga.

## LAPORAN YANG DIHARAPKAN
- Nama channel aktif yang terverifikasi di YouTube Studio
- Status video (scheduled + URL)
- Kendala apa pun (login 2FA, approval tertunda/"menunggu persetujuan", batas upload harian, dsb.)
