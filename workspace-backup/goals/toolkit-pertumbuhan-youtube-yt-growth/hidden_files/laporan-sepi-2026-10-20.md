# Laporan Cek Video Sepi — 2026-10-20

## Ringkasan
- Scan 13:12 WIB: GAGAL total — kuota YouTube Data API habis (`quotaExceeded`,
  20/20 channel 403). Bukan token expired. Dugaan: upload API-first produksi
  pagi ini (videos.insert = 1600 unit/upload). Kuota reset 14:00 WIB (tengah malam PT).
- Scan ulang 14:01 WIB: SUKSES — 289 video publik, 190 sepi (umur >24j,
  shorts <50 / long <100 views). Total views daftar sepi: 1684 (scan malam: 1620, +64).
- Mentok (publik >24j, sepi, delta views vs scan malam ≤2): **186 video**
  (178 mentok_lama + 8 baru).
- Diperbaiki: **1** (private duplikat). Tidak diubah: 7 (alasan di bawah).
- Share-3x: 6 kandidat baru → 1 batch browser (status: DALAM PROSES saat laporan ditulis).

## Perbaikan (1)
| Channel | Video | Aksi | Alasan |
|---|---|---|---|
| jejakbuddha | I_B9oy4U9TI "6 Tahun Menyiksa Diri…" (shorts, 0 views, 75,5j) | **set PRIVATE** (read-back terverifikasi) | Duplikat persis judul+deskripsi dari HrI_hj6jGXQ SEKALIGUS durasi 0 dtk = upload gagal. Kembaran ber-view (1 view, 59 dtk) tetap publik. |

## Tidak diubah (7) + alasan
| Channel | Video | Skor SEO | Alasan |
|---|---|---|---|
| history-en | OUqXvjS37ug "Hiroshima 1945…" (long, 1v) | 100 | Metadata sempurna; sepi faktor algoritma/umur channel. Retensi: belum ada data. |
| inktime | cM7N7Y63WNM "90 Plays Written…" (shorts, 10v) | 90 (2 WARN ringan: judul 33 krk, tanpa tags) | Tanpa token — hanya laporkan. |
| inktime | DtXgq3MDQmk "The Library of Alexandria…" (shorts, 15v) | 95 (WARN: tanpa tags) | Tanpa token — hanya laporkan. |
| jejakbuddha | HrI_hj6jGXQ "6 Tahun Menyiksa Diri…" (shorts, 1v) | 100 | Kembaran ber-view, tetap publik; metadata sempurna. |
| jejakislami | J1HEYCEkjQs "Dibakar Hidup-Hidup…" (long, 0v) | 95 (WARN: 14 hashtag di deskripsi) | ≥90 tanpa FAIL → jangan diubah. Satu-satunya copy publik (2 kembaran lama tidak ditemukan di API — kemungkinan sudah dihapus/private). |
| mind-en | WMgXhpcyLsw "7 Mind Tricks…" (long, 2v) | 100 | Metadata sempurna; sepi faktor algoritma. |
| weird-en | U4UwccK9vdI "7 Foods So Weird…" (long, 0v) | 95 (WARN: judul inti 39 krk) | ≥90 tanpa FAIL → jangan diubah. |

Catatan retensi: untuk semua 8 video baru, kurva retensi kosong/belum ada data
(video terlalu baru / views terlalu kecil) — dicatat apa adanya, tidak dikarang.

## Mentok per channel (186)
- empires-en 5 · fakta-bola-dunia 2 · history-en 8 (1 baru) · horor 11 · horror-en 18
- inktime 8 (2 baru) · jejakbuddha 16 (2 baru) · jejakislami 10 (1 baru)
- kisahalkitab 16 · kisahdharma 8 · lima-misteri 4 · macammacam 4 · mind-en 12 (1 baru)
- mystery-en 4 · space-en 6 · strangetales 8 · tinybuilders 4 · truecrime-en 17
- weird-en 17 (1 baru) · youtube-pov 8

## Share-3x
- Kandidat: 6 video mentok baru yang belum pernah di-share (182 lainnya masih dalam cooldown 7 hari):
  mNb8Dz2S7TE, OUqXvjS37ug, WMgXhpcyLsw, DtXgq3MDQmk, cM7N7Y63WNM, U4UwccK9vdI.
- Batch: 1 (6 video) via browser task — Share → Copy link 3x per video, tanpa login/like/komentar/subscribe.
- Hasil: browser task selesai — **6/6 video OK 3/3**, tiap copy dikonfirmasi toast
  "Link disalin ke papan klip"; tanpa login/like/komentar/subscribe.
  (Konfirmasi sempat tertunda ~20 menit; sempat disimpan ke pending file lalu dihapus
  setelah konfirmasi tiba.)
- quiet_shared di share3x-log.json: +6 video bertanggal 2026-10-20 (total 236).

## Perbaikan sampingan (bug)
- `NO_TOKEN` di `scan_sepi.py`, `scan_sepi_malam.py`, `diagnosis_malam_191019.py`
  pernah tertimpa string literal `"<redacted>"` (korup, bikin `in` check selalu False)
  — dipulihkan ke `{"inktime", "macammacam"}` dan terverifikasi via import.

## File
- `hidden_files/sepi-2026-10-20.json` — hasil scan (14:01 WIB)
- `hidden_files/mentok-2026-10-20.json` — 186 video mentok
- `hidden_files/diagnosis-2026-10-20.json` — diagnosis 8 video baru
- `hidden_files/perbaikan-sepi-2026-10-20-hasil.json` — hasil private + read-back
- `hidden_files/share3x-2026-10-20-candidates.json` — 6 kandidat share
- `banding_sepi_20261020.py`, `diagnosis_sepi_20261020.py` — skrip run hari ini
