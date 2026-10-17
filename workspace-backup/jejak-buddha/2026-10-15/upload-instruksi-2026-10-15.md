# INSTRUKSI UPLOAD — Jejak Buddha 2026-10-15 (LONG)

## Video
- File: `/home/hatch/workspace/jejak-buddha/2026-10-15/jejak-buddha-2026-10-15-upload.mp4`
- Kisah: Pertapaan dan Jalan Tengah (pool #4)
- Durasi: ~9:29 (voiceover mudiwa 8 beat + bumper suara user setelah beat 3)
- Thumbnail lokal: `/home/hatch/workspace/jejak-buddha/2026-10-15/thumbnail.png` (teks "TEMUKAN JALAN TENGAH")

## Upload
- Channel: @JejakBuddha — WAJIB verifikasi ID `UC1PNEzhOmAH08p75vwp7n0A` sebelum upload (batal bila beda)
- Cara: YouTube Data API v3 (`upload_long_api.py`, sesi `jejakbuddha`)
- Status: **Tidak Publik (Unlisted) dulu via API** (`privacyStatus=private` + `publishAt`), rapikan metadata, lalu **Terjadwal Jumat 2026-10-16 19:00 WIB** (`2026-10-16T12:00:00.000Z`)

## Metadata (sudah di body API)
- Judul: `Ternyata Menyiksa Diri Tak Membawa Pencerahan`
- Deskripsi: hook 150 char + konteks + 8 chapters + CTA + video terkait + hashtag `#buddha #kebijaksanaan #jejakbuddha #sejarahbuddha #inspirasi #foryou` + blok atribusi footage Wikimedia Commons
- Tags: 19 tag (lihat upload_long_api.py)
- Kategori: 27 (Education), bahasa: id, bukan untuk anak-anak

## PENDING — dikerjakan di YouTube Studio (sesi browser, perlu persetujuan user)
1. **AI disclosure**: centang "Altered content" — API tidak mendukung field ini
2. **Thumbnail custom**: upload `thumbnail.png` via Studio (API kemungkinan 403 — akun belum verifikasi HP)
3. **Komentar**: pastikan setel eksplisit ke "Allow all comments" (Details → Show more)
4. **Auto-dubbing**: aktifkan dub Inggris di Subtitle → Audio
5. **End screen**: arahkan ke video long lama paling sepi yang relevan + 1 playlist (dengan verbal pitch di akhir video)
6. **Komentar pin**: formula keyword + chapter teaser + pertanyaan ("bagian mana yang paling menyentuh hati Anda?")
7. Masukkan video ke playlist tematik channel

## Persetujuan
- Upload via API BERHASIL 2026-10-15 ~18:40 WIB — video ID `sTwtnVn1pro` (https://youtu.be/sTwtnVn1pro), terjadwal Jumat 2026-10-16 19:00 WIB
- Thumbnail custom GAGAL via API (403) — perlu upload manual di Studio
- Status: MENUNGGU sesi Studio untuk AI disclosure + thumbnail + komentar + end screen (perlu persetujuan user)
