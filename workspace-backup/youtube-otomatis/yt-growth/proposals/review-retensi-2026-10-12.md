# Review Retensi Mingguan — 2026-10-12

## Peringatan data (wajib dibaca dulu)

**Angka retensi asli TIDAK BISA diambil minggu ini.** YouTube Analytics API
(`youtubeanalytics.googleapis.com`) timeout total untuk semua 17 channel — uji 30 detik
(bawaan `analytics.py`) dan uji manual 90 detik sama-sama tanpa respons, sementara
Data API v3 normal. Karena itu:

- Tidak ada angka "% retensi di titik tengah" dan tidak ada angka "swiped away" Shorts
  minggu ini. Angka seperti itu tidak dikarang di dokumen ini.
- Yang disajikan di bawah adalah **pola menang vs pola kalah berbasis views per video**
  dari Data API v3 (snapshot 2026-10-12, video 28 hari terakhir yang terambil dari
  playlist uploads, maks 50/channel). Ini proksi distribusi, BUKAN retensi.
- Video yang tayang 2026-10-11/12 wajar masih 0 views — tidak dihitung sebagai "gagal"
  mutlak, hanya dicatat.

## Pola umum lintas channel (dari data views)

- **MENANG: Shorts spesifik-objek/kejadian tunggal.** Puncak views hampir selalu Shorts
  31–51 detik dengan satu objek/kejadian konkret di judul: Lima Misteri 1.306v,
  KisahPOV 1.088v, Tiny Builders 1.199v + 1.122v, Strange Tales 704v.
- **KALAH: long-form di channel yang masih 0–17 subscriber.** Long hampir selalu
  0–46 views (pengecualian: Space-En long 86v, Mind-En long 46v), dan beberapa long
  tercatat 0 views sama sekali (History-En semua 0). Di fase ini long belum dapat
  distribusi; Shorts yang menghidupi channel.
- **KALAH: unggahan ganda judul sama.** Horror-En mengunggah judul yang sama pada
  2026-10-07 dan 2026-10-08 — versi kedua 0 views. TrueCrime-En pola serupa
  (versi #shorts 2026-10-11 masih 0). Duplikasi membagi sinyal, bukan menambahnya.

## Per channel — pola menang, pola kalah, rekomendasi

- **empires-en (@AncientEmpiresTV, 11 subs)** — Menang: Shorts tempat konkret
  ("The City Carved Into a Cliff" 271v, "60 Maya Cities Died in One Lifetime" 230v).
  Kalah: long/judul generik (temple 12.000 tahun 1v). Rekomendasi: gandakan Shorts
  satu-situs-satu-misteri berangka; tunda long sampai Shorts stabil >200v.
- **history-en (@EchoesOfThePast-e9m, 1 sub)** — Semua 3 video 0 views, termasuk long
  9–10 menit. Tidak ada pola menang yang terukur. Rekomendasi: hentikan long dulu,
  masuk lewat Shorts dari potongan long yang sudah ada; cek visibilitas video (0 views
  total di level channel perlu verifikasi tayang publik).
- **horor (@KisahPOV, 17 subs)** — Menang: seri "Pasar Malam Gaib" (1.088v + 888v) —
  seri bersambung dengan setting yang sama menang besar. Kalah: judul long tanpa seri
  (0v). Rekomendasi: gandakan format seri bersetting tetap; tiap Shorts baru tetap di
  seri yang sedang naik sebelum membuka seri baru.
- **horror-en (@TalesOfDreadTV, 1 sub)** — Menang: "He Wouldn't Open the Doors" 58v.
  Kalah: unggahan ulang judul sama keesokan hari (0v). Rekomendasi: satu judul satu
  kali unggah; fokus hook orang-pertama kalimat pendek.
- **jejakbuddha (@JejakBuddha, 0 subs)** — Baru 1 long (0v). Belum ada pola.
  Rekomendasi: tambahkan Shorts potongan long sebagai pintu masuk; jangan nilai long
  pertama sebagai kegagalan format.
- **jejakislami (@JejakIslami-h3d, 0 subs)** — Views 0–3 di semua format; Shorts kisah
  Yusuf sedikit lebih baik dari long-nya (3v vs 1v). Rekomendasi: lanjutkan seri satu
  kisah (long + 3 Shorts) sesuai pola channel agama lain, nilai lagi setelah 2 seri.
- **kisahalkitab (@KisahAlkitab-k9j, 0 subs)** — 3 Shorts baru tayang 2026-10-11, semua
  0v — terlalu dini dinilai. Rekomendasi: jangan ganti judul minggu ini; nilai setelah
  7 hari tayang.
- **kisahdharma (@KisahDharma, 0 subs)** — 0 video terambil dari playlist uploads.
  Rekomendasi: verifikasi apakah channel ini benar sudah tayang; tanpa video, tidak
  ada yang bisa dioptimasi.
- **lima-misteri (@LimaMisteri, 8 subs)** — Menang: Shorts penampakan lokal spesifik
  ("Gamelan Misterius Ini Menolak Direkam" 1.306v, tangisan kematian 1.264v). Kalah:
  long countdown perdana hanya 30v. Rekomendasi: pertahankan pola baru yang disetujui
  user (1 long + 3 Shorts/hari); Shorts adalah mesin views, long untuk watch-time.
- **mind-en (@TheDarkMindFiles-s6i, 6 subs)** — Menang: "Someone Is Controlling You
  Right Now" 284v — hook tuduhan langsung orang-kedua. Kalah: judul netral/informatif
  (0–31v). Rekomendasi: gandakan hook pola "someone is doing X to you"; hentikan judul
  bergaya daftar netral untuk Shorts.
- **mystery-en (@MysteryShadowsTV, 0 subs)** — Menang: detail fisik mengejutkan dari
  Dyatlov (tenda teriris dari dalam, 106v). Kalah: judul ringkasan kasus umum (1v).
  Rekomendasi: judul = satu detail paling aneh dari kasus, bukan nama kasusnya.
- **space-en (@CosmosUnknownTV, 2 subs)** — Menang relatif: long "Rogue Planets" 86v —
  long tertinggi di kelompok EN kecil. Kalah: Shorts "330 MILLION Light-Years of
  NOTHING" 0v (angka besar tanpa objek). Rekomendasi: pertahankan long objek-konsep
  tunggal; Shorts pakai objek bernama, bukan angka abstrak.
- **strangetales (@StrangeTales-g6n, 6 subs)** — Menang: objek mustahil + pertanyaan
  siapa/bagaimana (Stonehenge mini Amazon 704v; buku 600 tahun 472v; lubang api 50
  tahun 270v — video terakhir tayang hari ini, masih naik). Kalah: belum ada yang
  terukur (yang 0v baru tayang kemarin/hari ini). Rekomendasi: lanjutkan persis pola
  judul objek+pertanyaan ini; jangan ubah formula yang sedang bekerja.
- **tinybuilders (@tinybuilders-d5z, 1 sub)** — Menang telak: demo benda mini yang
  BENAR-BENAR bekerja dengan suara/aksi di judul ("PULL the Starter… ROARS" 1.199v,
  pompa bambu mengalirkan air asli 1.122v). Kalah: long build (0v) dan judul proses
  tanpa hasil (17v). Rekomendasi: judul Shorts selalu = aksi + hasil nyata yang
  terlihat/terdengar di detik pertama.
- **truecrime-en (@TrueCaseFilesTV, 0 subs)** — Tiga Shorts kasus D.B. Cooper semua
  42–47v (konsisten, tidak ada yang meledak). Kalah: pengulangan judul yang sama
  sebagai Shorts baru (0v sementara). Rekomendasi: satu kasus dibuat seri sudut
  berbeda (uangnya / lompatannya / buronannya), bukan judul sama diunggah ulang.
- **weird-en (@BizarreWorldDaily, 0 subs)** — Baru 1 long, 3 views. Belum ada pola.
  Rekomendasi: channel ini belum punya Shorts — mulai dari Shorts kasus aneh tunggal
  sebelum long berikutnya.
- **youtube-pov (@ceritarakyat862, 49 subs — subs terbanyak)** — Paradoks: subs
  tertinggi tapi views per video terendah (maks 10v, banyak 0v, total channel tercatat
  100 views). Menang relatif: POV Gladiator (10v + 7v). Tidak ada pola distribusi yang
  sehat terukur dari Data API. Rekomendasi: audit pertama justru di sini — periksa
  sumber trafik & visibilitas di Studio saat Analytics pulih; sementara gandakan POV
  tokoh/tempat bernama jelas (Gladiator) dan hentikan judul POV generik.

## Kesimpulan retensi

Retensi asli belum bisa disimpulkan minggu ini karena Analytics API tidak terjangkau.
Kesimpulan berbasis views: **Shorts satu-objek-konret dengan hook spesifik menang di
hampir semua channel; long-form dan unggahan-ulang judul sama kalah.** Rekomendasi
produksi minggu ini: prioritaskan Shorts pola pemenang per channel di atas, dan jadikan
pemulihan akses Analytics sebagai prasyarat review retensi yang sesungguhnya minggu
depan.
