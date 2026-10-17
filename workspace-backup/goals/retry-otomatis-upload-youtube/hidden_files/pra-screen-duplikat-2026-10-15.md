# Pra-screen duplikat retry — run 2026-10-15 03:04 WIB

## Antrean (8 JSON, semua top-level; done/ & claimed/ diabaikan)
| file | channel | hasil cek_duplikat.py |
|---|---|---|
| inktime-2026-10-09.json | inktime | ERROR invalid_grant (via fallback mystery-en) |
| inktime-2026-10-13.json | inktime | ERROR invalid_grant (via fallback mystery-en) |
| inktime-2026-10-14-s1.json | inktime | ERROR "judul tidak ditemukan" (parser format "Judul (persis):") |
| inktime-2026-10-14-s2.json | inktime | ERROR "judul tidak ditemukan" |
| inktime-2026-10-14-s3.json | inktime | ERROR "judul tidak ditemukan" |
| macammacam-2026-10-14-hewan.json | macammacam | ERROR invalid_grant (via fallback mystery-en) — dicek via --judul manual |
| macammacam-truk-kartun-2026-10-12.json | macammacam | ERROR invalid_grant (via fallback mystery-en) |
| mystery-en-2026-10-13.json | mystery-en | ERROR invalid_grant (token langsung) |

## Tindakan
- Tidak ada JSON dipindah ke done/ (tidak ada hasil duplikat: true). Semua tetap di antrean.
- Tidak ada laporan ke chat per body (diam bila nihil).

## Diagnosa root cause
- Semua refresh token yt-growth expired/revoked. Token file diterbitkan 2026-10-08; refresh terakhir sukses 2026-10-14; pada 2026-10-15 semua refresh gagal invalid_grant.
- Pola persis = batas 7 hari refresh token untuk OAuth consent screen mode Testing.
- Verifikasi independen: token strangetales juga mati (yt_get langsung).
- inktime & macammacam tidak punya token file sendiri — selalu mengandalkan TOKEN_FALLBACK_SLUG=mystery-en (by design karena playlist uploads publik).

## Dampak
- Pra-screen anti-duplikat BUTA TOTAL sampai re-auth selesai.
- Semua alur API yt-growth ikut mati: upload API-first, yt-seo-refresh-mingguan, analytics, komentar.py, cek-video-sepi-3harian.

## Perbaikan dibutuhkan (butuh user — JANGAN lakukan diam-diam, aturan "mau login bilang dulu")
1. Pindahkan OAuth consent screen project yt-growth-510917 ke Production (agar refresh token tidak kedaluwarsa tiap 7 hari).
2. Re-auth per channel: `python auth.py auth-url SLUG` → user buka URL, pilih channel → `python auth.py exchange SLUG KODE`.
3. Patch opsional cek_duplikat.py: parser judul dukung format "Judul (persis):" / "Judul (persis, ...):" dengan judul di baris berikutnya (kasus inktime shorts).
