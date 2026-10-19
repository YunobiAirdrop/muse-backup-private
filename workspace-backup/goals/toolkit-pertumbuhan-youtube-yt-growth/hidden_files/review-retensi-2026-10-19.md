# Review Retensi Mingguan — 2026-10-19 (kurva ASLI dari Analytics API)

Data: `retention.py` untuk 3 video teratas + 3 terbawah per channel (113 video, 20 channel).
Angka retensi RELATIF: 1.00 = rata-rata video sejenis di titik itu. 40 video berkurva
terisi; 73 kosong (video terlalu baru / views di bawah ambang proses YouTube — dicatat
apa adanya, tidak dikarang). Data mentah: `hidden_files/retensi-2026-10-19.json`.

## Pola umum lintas channel

- **Jurang 0:04–0:08 adalah pembunuh utama.** Di hampir semua video, 3 titik jatuh
  terbesar jatuh di detik 4–8 — penonton kabur SEBELUM hook selesai. Shorts yang menang
  (retensi 25% ≥ 0.8) semuanya menaruh klaim judul secara visual di 3 detik pertama.
- **MENANG: angka konkret + objek tunggal di judul.** history-en "Death Ships"
  (1.27/0.97/0.87/0.81 — terbaik se-jaringan), empires-en "60 Maya Cities Died in One
  Lifetime" (0.91), strangetales "This River Carved a PERFECT Ice Circle" (0.86),
  tinybuilders "Tiny DAM That Actually Works" (0.89), mind-en "Someone Is Controlling
  You Right Now" (0.95).
- **KALAH: judul menang klik tapi 5 detik pertama tidak menepati janji.**
  horror-en "The Figure Behind the Rock" (401v tapi retensi 0.31→0.04), space-en
  "Boötes Void" shorts (0.27→0.04), macammacam "Asam Lambungmu Bisa Hancurkan Logam"
  (1313v tapi 0.53→0.20). Views tinggi + retensi ambruk = distribusi akan mati.
- **KALAH: long dengan intro bertele-tele.** space-en Oumuamua long (382v, retensi
  0.08 DATAR — 30% penonton kabur di detik 16–21), youtube-pov "KKB Papua" long
  (0.10 datar — 30% kabur di detik 13–25). Keduanya long 8–21 menit tanpa payoff awal.
- **Channel rohani (jejakbuddha, jejakislami, kisahalkitab, kisahdharma) + fakta-bola-dunia:**
  nol kurva terisi — views di bawah ambang. Belum ada yang bisa direview; fokus ke
  distribusi dulu.

## Per channel — pola menang, pola kalah, rekomendasi produksi

- **empires-en** — Menang: "60 Maya Cities Died in One Lifetime" 0.91/0.67/0.55/0.34.
  Kalah: judul tanpa angka. Rekomendasi: tiap shorts baru WAJIB 1 angka + skala waktu
  di judul; format ini terbukti 2x lipat retensinya.
- **history-en** — Menang: "The Death Ships That Doomed a Continent" 1.27/0.97/0.87/0.81,
  TERBAIK se-jaringan. Kalah: long 9–10 menit (0 data, 1–2 views). Rekomendasi: tiru
  pola judulnya (bencana + skala benua) untuk semua shorts; tunda long sampai ada
  shorts yang stabil >500v.
- **horor (@KisahPOV)** — Menang: seri Pasar Malam Gaib (0.62/0.42). Kalah: "Kakinya
  Tidak Menyentuh Tanah" 0.45→0.17 (seri Orderan Tengah Malam). Rekomendasi: perketat
  5 detik pertama seri Orderan — tunjukkan penumpangnya langsung, jangan bangun suasana.
- **horror-en** — Menang: "He Wouldn't Open the Doors" 0.71/0.57. Kalah: "The Figure
  Behind the Rock" 0.31→0.04, kabur massal di 0:05–0:08. Rekomendasi: frame 0–3 detik
  HARUS menampilkan "figure" yang dijanjikan judul; sekarang visual awal tidak menepati janji.
- **inktime** — Semua video ambruk di 50% (0.17–0.41); yang terbaik "Scientists Found It
  Buried in Ice" 0.71/0.41. Rekomendasi: taruh fakta paling mengejutkan di detik 5–15,
  bukan di akhir — penonton tidak sampai ke sana.
- **lima-misteri** — Menang: "Tangisannya Berarti Kematian" 0.79/0.56/0.45/0.34
  (format "X berarti Y"). Kalah: "Gamelan Menolak Direkam" 0.47 — klaim tidak terbukti
  di awal. Rekomendasi: buktikan klaim judul dalam 3 detik pertama (tunjukkan "menolak
  direkam"-nya), lalu jelaskan.
- **macammacam** — "Asam Lambungmu Bisa Hancurkan Logam" 1313v tapi retensi 0.53→0.20;
  "Pembuluh Darahmu 2x Keliling Bumi" 0.66→0.30. Rekomendasi: fakta tubuh menang klik —
  tambah payoff visual (ilustrasi/animasi) di detik 8–12 agar penonton tidak kabur
  setelah hook.
- **mind-en** — Menang: "Someone Is Controlling You Right Now" 0.95/0.72/0.64/0.51.
  Kalah: long "7 Body Language Signals" 0.24→0.04. Rekomendasi: tiru pola "kamu" +
  ancaman langsung untuk semua shorts; long jangan dibuka dengan daftar — buka dengan
  1 kasus nyata.
- **mystery-en** — Menang: Dyatlov Pass 0.83/0.64/0.50/0.28. Rekomendasi: gandakan
  misteri bernama + detail spesifik (nama tempat + fakta aneh); itu formula yang jalan.
- **space-en** — Kalah berat: Oumuamua long 0.08 DATAR (382v sia-sia), Boötes Void
  shorts 0.27→0.04. Rekomendasi: potong 20 detik pertama long Oumuamua — langsung ke
  klaim "alien visitor"; untuk shorts, jangan ulang pola judul tanpa payoff visual awal.
- **strangetales** — Menang: pola "This X — HOW?!" retensi 0.77–0.86 di 3 video
  teratas (1200v/1076v/1054v). Rekomendasi: JANGAN ganti format — ini formula juara
  channel; variasikan objeknya saja.
- **tinybuilders** — Menang: "Tiny DAM That Actually Works" 0.89/0.49. Kalah: "Bamboo
  Pump" 0.55→0.19 (hasil air mengalir telat muncul). Rekomendasi: hasil/aksi fisik
  (air mengalir, mesin menyala) HARUS terlihat sebelum detik 8.
- **truecrime-en** — Retensi solid: ketiganya 0.71–0.79 di 25%, akhir 0.35–0.50
  (terbaik: "$5,800 That Reopened America's Greatest Mystery" akhir 0.50).
  Rekomendasi: pertahankan pola angka + misteri tak terpecahkan; tambah kadens —
  channel ini paling siap scale.
- **weird-en** — "Stomach Dissolve METAL?!" 0.60 tapi drop -0.20 tepat di 0:05.
  Rekomendasi: sinkronkan visual 0–3 detik dengan kalimat hook yang diucapkan —
  sekarang penonton dengar klaim tapi tidak melihat buktinya.
- **youtube-pov** — "KKB Papua" long 0.10 datar, 30% kabur di detik 13–25.
  Rekomendasi: judul baru (lihat proposal) WAJIB ditepati dalam 15 detik pertama —
  atau edit ulang opening videonya; tanpa itu refresh judul tidak akan menolong.
- **jejakbuddha / jejakislami / kisahalkitab / kisahdharma / fakta-bola-dunia** —
  Belum ada kurva (views di bawah ambang). Rekomendasi: fokus distribusi
  (share 3x, hook judul); review retensi menyusul saat views masuk.
