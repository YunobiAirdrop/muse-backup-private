# Laporan Cek Video Sepi — Malam 2026-10-19 (run ke-2)

## Ringkasan
- Video publik discan: 253 (20 channel) — file `sepi-2026-10-19-malam.json`
- Masuk daftar sepi (shorts <50 / long <100 views, umur >24 jam): 182
- MENTOK (naik ≤2 views sejak scan pagi): **182** — 174 sudah ditangani run pagi,
  **8 baru mentok** (tumbuh >2 views pagi-vs-18 Okt, kini macet)
- Diperbaiki metadatanya via API: **3** (3 judul, 3 deskripsi, 2 tags) — semua OK,
  read-back 3/3 cocok
- Diset PRIVATE: **0**
- TIDAK diubah (5 video baru skor ≥90): sepi faktor algoritma/umur channel
- TIDAK diubah dengan alasan khusus: 2 (inktime & macammacam — tanpa token, lapor saja)
- Total views daftar sepi: 1.620 (pagi: 1.723 dari 199 video)

## Diagnosis (8 video baru)
- `seo_audit.py`: 5 skor ≥90, 3 skor <90, 0 error fetch.
- `retention.py`: hanya 1 video baru yang masuk 3 terburuk channelnya
  (uIGWlXfMQJ4) — "TIDAK ADA DATA" (views 0, YouTube tidak memproses kurva).
- Duplikat judul: 1 temuan — shorts jejakislami `uIGWlXfMQJ4` 0 views berjudul
  persis sama dengan `J1HEYCEkjQs` dan `P0XCx7rCbNA`.
- Pola kompetitor (competitor-2026-10-19.md): judul kita sudah sejalan.

## Temuan penting: 2 video "Dibakar..." di-private di luar run ini
- `J1HEYCEkjQs` (long, diperbaiki metadatanya pagi ini saat masih publik) dan
  `P0XCx7rCbNA` kini berstatus **private**, 0 views — perubahan terjadi antara
  run pagi dan run malam, BUKAN oleh otomasi (tidak ada skrip yang mem-private
  video; kemungkinan diubah manual dari Studio/HP).
- `uIGWlXfMQJ4` (shorts, 0 views, judul persis sama) masih publik.
- Keputusan: TIDAK mem-private `uIGWlXfMQJ4` — kembarannya sudah private semua
  sehingga aturan "kembaran ber-view tetap publik" tidak terpenuhi (tidak ada
  copy ber-view); mem-private copy terakhir akan menghapus topik dari publik
  sepenuhnya. Hanya metadata yang diperbaiki. Perlu konfirmasi user bila
  topik ini memang ingin dihapus dari publik.

## Cacat yang diperbaiki (3 video, via perbaiki_malam_191019.py --apply)
| video | channel | skor | tindakan |
|---|---|---|---|
| 0xG5W7rbDt4 | jejakbuddha | 65 | judul: hashtag keluar dari judul (aturan long); deskripsi +CTA subscribe ID + blok 5 hashtag (#butifyourcloseyoureyesmeme #foryou #buddha #buddhism #inspirasi); tags 0→15 |
| w_riNbyiOW8 | mind-en | 80 | judul: 5 hashtag diakhiri #foryou (#butifyourcloseyoureyesmeme #shorts #psychology #mindset #foryou); deskripsi: blok hashtag dinormalisasi; tags 0→10 |
| uIGWlXfMQJ4 | jejakislami | 85 | judul +5 hashtag (#butifyourcloseyoureyesmeme #shorts #islami #kisahislami #foryou); deskripsi +CTA subscribe ID + #butifyourcloseyoureyesmeme di blok hashtag; tags (13) sudah bagus, tidak diubah |

Verifikasi read-back: 3/3 judul + deskripsi cocok; tags 3/3 cocok sebagai set
(0xG5W7rbDt4 sempat mismatch urutan sesaat setelah update, verifikasi ulang
15/15 identik). categoryId/bahasa dipertahankan; atribusi footage CC di
deskripsi uIGWlXfMQJ4 tidak disentuh.

## Tidak diubah + alasan
- inktime `8KqJ8z3D5rQ` (skor 95), macammacam `hwuWzHPyDl0` (skor 90):
  channel tanpa token — hanya dilaporkan, tidak ditulis (aturan tetap).
- fakta-bola-dunia `n8YVG3b09is` (90), mind-en `Mn02xdeZHlQ` (95),
  tinybuilders `kCoM5sT9q40` (100): metadata sudah bagus — sepi faktor
  algoritma/umur channel.
- 174 video mentok_lama: sudah didiagnosis & ditangani run pagi (16 diperbaiki,
  1 di-private); tidak di-churn ulang.

## Per channel (mentok malam | baru | tindakan malam)
| channel | mentok | baru | tindakan |
|---|---|---|---|
| horror-en | 18 | 0 | — |
| truecrime-en | 17 | 0 | — |
| kisahalkitab | 16 | 0 | — |
| weird-en | 16 | 0 | — |
| jejakbuddha | 14 | 1 | 1 metadata (0xG5W7rbDt4) |
| mind-en | 12 | 2 | 1 metadata (w_riNbyiOW8) |
| horor | 11 | 0 | — |
| jejakislami | 10 | 1 | 1 metadata (uIGWlXfMQJ4, tidak di-private — lihat temuan) |
| strangetales | 10 | 0 | — |
| kisahdharma | 8 | 0 | — |
| youtube-pov | 8 | 0 | — |
| history-en | 7 | 0 | — |
| space-en | 6 | 0 | — |
| inktime | 6 | 1 | lapor saja (tanpa token) |
| empires-en | 5 | 0 | — |
| lima-misteri | 4 | 0 | — |
| mystery-en | 4 | 0 | — |
| tinybuilders | 4 | 1 | — (skor 100) |
| macammacam | 4 | 1 | lapor saja (tanpa token) |
| fakta-bola-dunia | 2 | 1 | — (skor 90) |

## Share-3x
- Kandidat: 6 video mentok (76 dalam cooldown 7 hari; 100 sudah pernah di-share
  sebagai upload baru).
- Batch: 1 (malam-batch01: 6 video) — SELESAI 6/6, tiap video Share→Copy 3x
  terkonfirmasi toast "Link disalin ke papan klip" (total 18 copy-link).
  Tanpa login/like/komentar/subscribe.
- quiet_shared di share3x-log.json: +6 video bertanggal 2026-10-19
  (total quiet_shared: 230).

## File
- `hidden_files/sepi-2026-10-19-malam.json` — hasil scan malam
- `hidden_files/mentok-2026-10-19-malam.json` — 182 video mentok (174 lama + 8 baru)
- `hidden_files/diagnosis-2026-10-19-malam.json` — diagnosis 8 video baru
- `hidden_files/perbaikan-sepi-2026-10-19-malam-plan.json` — rencana perbaikan
- `hidden_files/perbaikan-sepi-2026-10-19-malam-hasil.json` — hasil apply + read-back
- `hidden_files/share3x-2026-10-19-malam-candidates.json` — kandidat share
- `hidden_files/share3x-2026-10-19-malam-batch01.json` — hasil batch share
- `scan_sepi_malam.py`, `banding_malam_191019.py`, `diagnosis_malam_191019.py`,
  `perbaiki_malam_191019.py` — skrip run malam ini
