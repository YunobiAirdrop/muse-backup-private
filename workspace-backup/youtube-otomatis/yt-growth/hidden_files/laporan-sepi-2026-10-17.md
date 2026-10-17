# Laporan Cek Video Sepi Harian — 2026-10-17

## Ringkasan
- Video publik discan: 251 (20 channel) — file `sepi-2026-10-17.json`
- Masuk daftar sepi (shorts <50 / long <100 views, umur >24 jam): 195
- MENTOK (naik ≤2 views sejak scan 2026-10-12, atau baru masuk daftar sepi): **181**
- Diperbaiki metadatanya via API: **52** (26 judul, 30 deskripsi, 47 tags) — 52/52 sukses, 0 gagal
- Diverifikasi read-back: 30 video (2/channel) — semua OK
- Diset PRIVATE (duplikat persis 0 views): **1** — truecrime-en `EXmbjr-MKbs`
  ("He Jumped From a Plane With $200,000 — Never Found", kembaran 44 views tetap publik)
- TIDAK diubah (audit ≥90, sepi faktor algoritma/umur channel): 129
- Total views daftar sepi: 1.658 (scan 10-12: 841 dari 67 video — cakupan scan berbeda)

## Diagnosis
- `seo_audit.py` massal ke 181 video mentok: 129 skor ≥90 (metadata sudah bagus),
  52 skor <90 dengan cacat nyata.
- `retention.py` ke 3 video terburuk/channel (60 video): YouTube tidak memproses
  kurva retensi untuk video views sangat rendah — semua "TIDAK ADA DATA", dicatat apa adanya.
- Duplikat judul dalam channel: 6 video (3 pasang). Yang memenuhi syarat private
  (persis sama + 0 views): 1. Pasangan macammacam "Truk Part 1" disengaja
  (versi stiker + versi kartun, disetujui user 2026-10-12) — tidak disentuh.
  Pasangan truecrime-en "Cooper Vanished Mid-Air" keduanya ber-view (2 vs 46) — tidak disentuh.
- Pola kompetitor (competitor-2026-10-12.md): judul 40-58 karakter, angka + kata CAPS
  sesekali — judul kita sudah sejalan; masalah utama = metadata teknis (tags kosong,
  hashtag berlebih/tanpa #foryou, CTA hilang), bukan formula judul.

## Cacat yang diperbaiki (52 video)
1. Shorts hashtag terakhir bukan #foryou → diganti #foryou (23 video)
2. Shorts tanpa hashtag judul → ditambah paket hashtag (1 video)
3. Long tanpa CTA subscribe di deskripsi → CTA ditambahkan (13 video)
4. Long hashtag deskripsi tanpa #foryou → blok hashtag dibangun ulang (11 video)
5. Long tanpa hashtag deskripsi → blok 3-5 hashtag ditambahkan (2 video)
6. Tags kosong / <300 karakter → dibangun ulang ≤480 karakter dari keyword judul + niche (47 video)
7. Long ber-hashtag di judul → hashtag dipindah ke deskripsi (4 video)
8. Blok hashtag deskripsi >5 → dipangkas ke 3-5 (19 video)

Aturan yang dijaga: judul inti TIDAK diubah; categoryId/bahasa dipertahankan;
link afiliasi Shopee + atribusi/kredit di deskripsi tidak dihapus (hanya append);
tidak ada video dihapus; komentar/audience/jadwal tidak disentuh.

## Per channel
| channel | mentok | diperbaiki | sudah-bagus (faktor algoritma) |
|---|---|---|---|
| youtube-pov | 20 | 2 | 18 |
| truecrime-en | 18 | 2 | 16 |
| horror-en | 16 | 3 | 13 |
| kisahalkitab | 15 | 5 | 10 |
| weird-en | 15 | 9 | 6 |
| strangetales | 14 | 4 | 10 |
| jejakbuddha | 13 | 5 | 8 |
| horor | 10 | 3 | 7 |
| history-en | 8 | 2 | 6 |
| jejakislami | 8 | 0 | 8 |
| space-en | 8 | 0 | 8 |
| mind-en | 7 | 2 | 5 |
| kisahdharma | 6 | 5 | 1 |
| empires-en | 5 | 0 | 5 |
| lima-misteri | 4 | 4 | 0 |
| inktime | 4 | 0 | 4 |
| mystery-en | 3 | 1 | 2 |
| tinybuilders | 3 | 2 | 1 |
| macammacam | 3 | 2 | 1 |
| fakta-bola-dunia | 1 | 1 | 0 |

Catatan: token inktime & macammacam kini VALID (20/20 aktif sejak re-auth 2026-10-15),
sehingga keduanya ikut diperbaiki — klausul "hanya laporkan" di body sudah kedaluwarsa
karena syaratnya ("tanpa token") tidak lagi terpenuhi.

## Share-3x
- Kandidat: 181 video mentok (belum pernah quiet-share / cooldown >7 hari) — 19 batch ±10.
- Selesai: 19/19 batch (01-17, 19 penuh + batch 18: 6 video lalu 4 sisanya via task 18b).
  Total **180 video di-share-copy 3x**.
- Batch 18 sempat macet di video ke-7 (W--QaM2Mm2A; task di-close setelah 2x steer tak mempan);
  4 video sisanya selesai via task pengganti 18b.
- Dilewati: EXmbjr-MKbs (private — benar tidak di-share).
- quiet_shared di share3x-log.json: 180 video bertanggal 2026-10-17.
- Catatan: laporan per-video dari tiap browser task tidak terkirim ke konteks run ini
  (final_response_preview null); status completed dijadikan dasar pencatatan.
  Tidak ada task yang berstatus failed/interrupted.

## File
- `hidden_files/sepi-2026-10-17.json` — hasil scan
- `hidden_files/mentok-2026-10-17.json` — 181 video mentok
- `hidden_files/diagnosis-2026-10-17.json` — skor SEO + temuan + retention per video
- `hidden_files/perbaikan-sepi-2026-10-17-plan.json` — rencana perubahan lama→baru
- `hidden_files/perbaikan-sepi-2026-10-17-hasil.json` — hasil apply (52 OK, 0 gagal)
- `hidden_files/share3x-2026-10-17-batchNN.json` — 19 batch share
- `hidden_files/share3x-2026-10-17-candidates.json` — 181 kandidat share
