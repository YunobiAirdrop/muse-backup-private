# Laporan Cek Video Sepi Harian — 2026-10-19

## Ringkasan
- Video publik discan: 265 (20 channel) — file `sepi-2026-10-19.json`
- Masuk daftar sepi (shorts <50 / long <100 views, umur >24 jam): 199
- MENTOK (naik ≤2 views sejak scan 2026-10-18): **194** (0 baru-masuk-sepi; 5 video tumbuh >2 views)
- Diperbaiki metadatanya via API: **16** (9 judul, 7 deskripsi, 11 tags) — semua OK, 0 gagal
- Diset PRIVATE (duplikat persis 0 views): **1** — youtube-pov `F0Malo5MCoA`
  ("Dinding Bergetar... 200 Ribu Tentara Mengepungku!", shorts 0 views; kembaran long
  `-2qLmaLbPZo` 1 view tetap publik). Diverifikasi read-back: privacyStatus=private, 0 views.
- TIDAK diubah (172 audit ≥90): sepi faktor algoritma/umur channel.
- TIDAK diubah dengan alasan khusus: 5 (lihat "Tidak diubah + alasan").
- Total views daftar sepi: 1.723 (scan kemarin: 1.685 dari 199 video — naik tipis +38).

## Diagnosis
- `seo_audit.py` massal ke 194 video mentok: 172 skor ≥90, 22 skor <90, 0 error fetch.
- `retention.py` ke 3 video terburuk/channel (58 video): YouTube tidak memproses kurva
  retensi untuk video views sangat rendah — semua "TIDAK ADA DATA", dicatat apa adanya.
  (2 video gagal dipanggil karena ID diawali "-" — dicatat, bukan cacat video.)
- Duplikat judul dalam channel: 4 pasang. Yang memenuhi syarat private
  (persis sama + 0 views): 1 (F0Malo5MCoA, dieksekusi + diverifikasi).
  Pasangan jejakislami "Laut Terbelah Dua..." (3/1 views), macammacam
  "Macam-macam Jenis Truk (Part 1)" (5/10 views), truecrime-en "The $5,800 That
  Reopened..." (4/48 views) — semuanya ber-view, tidak disentuh.
- Pola kompetitor (competitor-2026-10-19.md, fresh hari ini): judul 33-58 karakter,
  angka + kata CAPS sesekali, hashtag spesifik per channel — judul kita sudah sejalan;
  masalah utama = algoritma/umur channel, bukan metadata.

## Cacat yang diperbaiki (16 video, via perbaiki_sepi_191019.py --apply)
| video | channel | skor | tindakan |
|---|---|---|---|
| E-Jo0o3EMNI | history-en | 75 | judul: hashtag akhir #constantinople → #foryou; tags dibangun ulang (0→16) |
| aIsrA8upGUc | horor | 70 | deskripsi: +CTA subscribe ID + blok hashtag #foryou #horor #ceritahoror #viralindonesia |
| G8rB-4qSHJI | horror-en | 65 | deskripsi: +CTA subscribe EN + blok hashtag (8→4, diawali #foryou) |
| 2jWafMm6Fkg | jejakislami | 80 | deskripsi: +CTA subscribe ID + blok hashtag; tags 14→18 (enhance, bukan rebuild) |
| J1HEYCEkjQs | jejakislami | 80 | deskripsi: +CTA subscribe ID + blok hashtag; tags 13→16 (enhance, bukan rebuild) |
| yq4QOAdYsv0 | lima-misteri | 65 | deskripsi: +CTA subscribe ID + blok hashtag #foryou #mystery #misteri #viralindonesia |
| zWaf_UBaKG4 | truecrime-en | 85 | deskripsi: blok hashtag tanpa #foryou → #foryou #truecrime #mystery #crime |
| kJeu_cCr7nA | weird-en | 65 | deskripsi: +CTA subscribe EN + blok hashtag #foryou #weirdfacts #facts #didyouknow |
| DuO4SK10Kr0 | youtube-pov | 75 | judul shorts diakhiri #foryou; tags 4→19 |
| cbYxqOvGnGo | youtube-pov | 75 | judul shorts diakhiri #foryou; tags 4→20 |
| vBQf93ljy18 | youtube-pov | 75 | judul shorts diakhiri #foryou; tags 4→19 |
| Y7IJZ3M8OSQ | youtube-pov | 70 | judul shorts diakhiri #foryou (+buang sisa "#" putus); tags 7→19 |
| syLWsY3qAh4 | youtube-pov | 75 | judul shorts diakhiri #foryou; tags 7→19 |
| bIVfpvA7FW8 | youtube-pov | 70 | judul shorts diakhiri #foryou (+buang sisa "#" putus); tags 7→18 |
| 4qtGKOfpu9w | youtube-pov | 75 | judul shorts diakhiri #foryou; tags 4→19 |
| vkWKtzCUYQ4 | youtube-pov | 75 | judul shorts diakhiri #foryou; tags 4→19 |

Catatan: judul inti TIDAK diubah (hanya normalisasi hashtag); link afiliasi Shopee di
deskripsi youtube-pov tidak disentuh; categoryId/bahasa dipertahankan; tags jejakislami
di-enhance manual (tags lama sudah bagus, rebuild otomatis berisiko menurunkan kualitas).
Verifikasi read-back: 10/10 cocok (judul, deskripsi, tags — YouTube mengembalikan tags
terurut alfabetis, isi set identik; F0Malo5MCoA terkonfirmasi private).

## Tidak diubah + alasan
- inktime `Z550Mo9NmvI` (65), macammacam `9BRVEab044E` (70) & `bGBGROVZfZY` (85):
  channel tanpa token — hanya dilaporkan, tidak ditulis (aturan tetap).
- fakta-bola-dunia `KkIsmqjGOBo` (85): WARN-only; tags 18/185char sudah optimal
  (diteliti manual 2026-10-18, perbaikan otomatis menurunkan cakupan) — hindari churn.
- history-en `ZNR5JDGKtys` (85): WARN-only tanpa FAIL (CTA + #foryou lolos; hanya
  judul/deskripsi pendek & tanpa chapters yang tak bisa difabrikasi) — hindari churn.
- 172 video skor ≥90: metadata sudah bagus — sepi faktor algoritma/umur channel.
- 3 pasang duplikat ber-view: tidak memenuhi syarat private (0-view).

## Per channel (mentok | diperbaiki | private | catatan)
| channel | mentok | tindakan |
|---|---|---|
| truecrime-en | 19 | 1 metadata (zWaf_UBaKG4) |
| weird-en | 19 | 1 metadata (kJeu_cCr7nA) |
| horror-en | 18 | 1 metadata (G8rB-4qSHJI) |
| jejakbuddha | 16 | — |
| kisahalkitab | 16 | — |
| strangetales | 12 | — |
| youtube-pov | 12 | 8 metadata + 1 private (F0Malo5MCoA) |
| horor | 11 | 1 metadata (aIsrA8upGUc) |
| jejakislami | 11 | 2 metadata (2jWafMm6Fkg, J1HEYCEkjQs) |
| mind-en | 10 | — |
| history-en | 9 | 1 metadata (E-Jo0o3EMNI) |
| kisahdharma | 8 | — |
| space-en | 7 | — |
| empires-en | 5 | — |
| inktime | 5 | lapor saja (tanpa token) |
| lima-misteri | 4 | 1 metadata (yq4QOAdYsv0) |
| macammacam | 4 | lapor saja (tanpa token) |
| mystery-en | 4 | — |
| tinybuilders | 3 | — |
| fakta-bola-dunia | 1 | diteliti, tidak diubah (tags sudah optimal) |

## Share-3x
- Kandidat: 33 video mentok (160 dalam cooldown 7 hari; 1 dilewati karena di-private
  hari ini: youtube-pov F0Malo5MCoA).
- Batch: 4 (batch01–03: 10 video, batch04: 3 video) — SELESAI 33/33, tiap video
  Share→Copy 3x terkonfirmasi toast "Link copied to clipboard" (total 99 copy-link).
  Tanpa login/like/komentar/subscribe.
- quiet_shared di share3x-log.json: 33 video bertanggal 2026-10-19 (total quiet_shared: 224).

## File
- `hidden_files/sepi-2026-10-19.json` — hasil scan
- `hidden_files/mentok-2026-10-19.json` — 194 video mentok
- `hidden_files/diagnosis-2026-10-19.json` — skor SEO + temuan + retention per video
- `hidden_files/perbaikan-sepi-2026-10-19-plan.json` — rencana perbaikan
- `hidden_files/perbaikan-sepi-2026-10-19-hasil.json` — hasil apply API
- `hidden_files/share3x-2026-10-19-candidates.json` — kandidat share
- `hidden_files/share3x-2026-10-19-batch01..04.json` — batch share
- `diagnosis_harian_191019.py`, `perbaiki_sepi_191019.py` — skrip run hari ini
