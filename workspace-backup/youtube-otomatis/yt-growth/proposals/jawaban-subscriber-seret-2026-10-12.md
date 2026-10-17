# Jawaban berbasis data: kenapa subscriber seret? (2026-10-12)

Sumber: snapshot Data API v3 per channel 2026-10-12 di
`yt-growth/hidden_files/analytics-2026-10-12/*.data-api.json` + review
`review-retensi-2026-10-12.md`. Angka channel_stats = lifetime resmi channel.

## Kesimpulan utama
Bukan terutama kualitas video. Tiga penyebab terukur, dua di antaranya cacat
sistem yang bisa diperbaiki:

### 1. @ceritarakyat862 — "channel terdepan" itu ilusi angka
- 49 subscriber (terbanyak), tapi lifetime views cuma 100.
- 11 video POV baru (5–11 Okt) total cuma **16 views**; video terlarisnya
  "POV Gladiator" 10 views.
- Di playlist uploads masih ada video lama pra-pipeline (2 & 15–17 Sep:
  "Live Stream dealy vlog sumbul", "Asal Usul Berdirinya KKb Papua").
  Artinya 49 subs itu hampir pasti warisan kehidupan channel sebelumnya,
  BUKAN hasil konten POV baru. Jangan jadikan channel ini patokan "terdepan".

### 2. Upload duplikat dari retry — sinyal terbagi, duplikat 0 views
- @TalesOfDreadTV (horror-en): "She Had NO Reflection" tayang 7 Okt (6v),
  diunggah ulang 8 Okt (0v). "I Was Dead for 52 Years..." 7 Okt (34v),
  unggah ulang 8 Okt (0v).
- @TrueCaseFilesTV (truecrime-en): 3 Shorts D.B. Cooper 6 Okt (47v/42v/46v)
  diunggah ulang 11 Okt dengan judul sama — ketiganya 0 views.
- Pola ini konsisten dengan retry yang mengunggah ulang video yang ternyata
  SUDAH live. Tidak ditemukan guard anti-duplikat di dokumen retry-queue.
  Perbaikan yang dibutuhkan: sebelum retry upload, cek playlist uploads
  channel — judul/video yang sudah live dikeluarkan dari antrean, jangan
  diunggah lagi.

### 3. Konversi nonton→subscribe memang rendah, tapi beda-beda per channel
- Terbaik: @AncientEmpiresTV 11 subs / 718 views lifetime (±1,5%).
- @KisahPOV 17 / 3.937 (±0,4%); @LimaMisteri 8 / 2.589 (±0,3%).
- Terburuk: @tinybuilders — Shorts 1.199v dan 1.122v, subscriber cuma 1.
  Videonya ditonton, orangnya tidak tinggal. Ini masalah konversi spesifik
  channel demo miniatur, bukan bukti semua video jelek.
- Total semua channel: 102 subscriber, sesuai angka yang sudah dilaporkan.

### 4. Channel yang videonya belum live sama sekali
- @KisahDharma: videoCount resmi 0 — 5 file produksinya (8–11 Okt) masih
  semua di retry-queue, belum pernah tayang.
- @JejakBuddha & @KisahAlkitab: videoCount 0 di snapshot pagi 12 Okt.
  Belum bisa dipastikan penyebabnya: sebagian Shorts Kisah Alkitab memang
  terjadwal tayang 19:00 (belum premier saat snapshot), tapi Jejak Buddha
  juga punya file di retry-queue. Perlu verifikasi live di Studio.

## Yang BELUM terjawab (jangan dikarang)
Retensi asli (average view duration / % ditonton sampai tengah) tetap belum
ada: YouTube Analytics API timeout untuk semua 17 channel, dan percobaan
tarik ulang 12 Okt 12:2x WIB dari tahap riset diblokir kebijakan OAuth
(POST /token policy_denied untuk background). Tarik di tahap delivery/main:
`cd ~/workspace/youtube-otomatis/yt-growth && ./venv/bin/python analytics.py lima-misteri --days 28 --top 20`
lalu slug `horor` dan `tinybuilders`. Tanpa itu, vonis "penonton kabur di
tengah video" belum bisa diberikan.
