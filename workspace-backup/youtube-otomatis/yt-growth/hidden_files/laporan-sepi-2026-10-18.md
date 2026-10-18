# Laporan Cek Video Sepi Harian — 2026-10-18

## Ringkasan
- Video publik discan: 280 (20 channel) — file `sepi-2026-10-18.json`
- Masuk daftar sepi (shorts <50 / long <100 views, umur >24 jam): 178
- MENTOK (naik ≤2 views sejak scan 2026-10-17): **164** (0 baru-masuk-sepi)
- Diperbaiki metadatanya via API: **0** — 163/164 skor SEO ≥90 (metadata sudah bagus);
  satu-satunya skor 85 (fakta-bola-dunia KkIsmqjGOBo) diteliti manual: tags-nya
  sudah mencakup semua keyword judul + niche (18 tags, 168 char), perbaikan otomatis
  justru MENURUNKAN cakupan (11 tags, ~110 char) — tidak diubah (hindari churn).
- Diset PRIVATE (duplikat persis 0 views): **1** — truecrime-en `EXmbjr-MKbs`
  ("He Jumped From a Plane With $200,000 — Never Found", kembaran 45 views tetap publik).
  CATATAN: run kemarin melaporkan video ini sudah di-private, tapi verifikasi API hari ini
  menunjukkan statusnya masih PUBLIC — penyebabnya tidak diketahui (kemungkinan write
  kemarin tidak tersimpan). Hari ini di-set private ulang dan DIVERIFIKASI read-back:
  privacyStatus=private, 0 views.
- TIDAK diubah (audit ≥90 / tanpa cacat nyata): 163 → sepi faktor algoritma/umur channel.
- Total views daftar sepi: 1.680 (scan kemarin: 1.624 dari 194 video).

## Diagnosis
- `seo_audit.py` massal ke 164 video mentok: 163 skor ≥90, 1 skor 85.
- `retention.py` ke 3 video terburuk/channel (55 video): YouTube tidak memproses
  kurva retensi untuk video views sangat rendah — semua "TIDAK ADA DATA", dicatat apa adanya.
- Duplikat judul dalam channel: 3 pasang. Yang memenuhi syarat private
  (persis sama + 0 views): 1 (EXmbjr-MKbs, dieksekusi). Pasangan jejakislami
  "Laut Terbelah Dua..." (w6iwcZqpV1E 3 views / xpGwk_bdxZ8 1 view) dan pasangan
  truecrime-en "The $5,800 That Reopened..." (PrEE5W4ZxrI 4 views / zItf87bPxvU 48 views)
  keduanya ber-view — tidak disentuh.
- Pola kompetitor (competitor-2026-10-12.md): judul 40-58 karakter, angka + kata CAPS
  sesekali — judul kita sudah sejalan; masalah utama = algoritma/umur channel, bukan metadata.

## Cacat yang diperbaiki
Tidak ada (0 video). Satu-satunya kandidat (fakta-bola-dunia KkIsmqjGOBo, skor 85)
ditolak perbaikannya setelah verifikasi manual — tags sudah optimal, churn dihindari.

## Per channel (mentok | sudah-bagus | tindakan)
| channel | mentok | tindakan |
|---|---|---|
| kisahalkitab | 16 | — |
| truecrime-en | 16 | 1 private (EXmbjr-MKbs) |
| horror-en | 15 | — |
| weird-en | 15 | — |
| jejakbuddha | 13 | — |
| strangetales | 12 | — |
| horor | 11 | — |
| jejakislami | 9 | — |
| kisahdharma | 8 | — |
| mind-en | 8 | — |
| space-en | 7 | — |
| youtube-pov | 7 | — |
| empires-en | 5 | — |
| history-en | 5 | — |
| lima-misteri | 4 | — |
| mystery-en | 4 | — |
| tinybuilders | 4 | — |
| inktime | 4 | — |
| fakta-bola-dunia | 1 | diteliti, tidak diubah (tags sudah optimal) |
| macammacam | 0 | — |

## Share-3x
- Kandidat: 11 video mentok (152 dalam cooldown 7 hari sejak share kemarin; 1 dilewati karena private).
- Batch: 2 (batch01: 6 video, batch02: 5 video) — SELESAI 11/11, tiap video Share→Copy 3x
  terkonfirmasi toast "Link copied to clipboard". Tanpa login/like/komentar/subscribe.
- quiet_shared di share3x-log.json: 11 video bertanggal 2026-10-18 (total quiet_shared: 191).

## File
- `hidden_files/sepi-2026-10-18.json` — hasil scan
- `hidden_files/mentok-2026-10-18.json` — 164 video mentok
- `hidden_files/diagnosis-2026-10-18.json` — skor SEO + temuan + retention per video
- `hidden_files/share3x-2026-10-18-batch01.json`, `-batch02.json` — batch share
- `hidden_files/share3x-2026-10-18-candidates.json` — 11 kandidat share
