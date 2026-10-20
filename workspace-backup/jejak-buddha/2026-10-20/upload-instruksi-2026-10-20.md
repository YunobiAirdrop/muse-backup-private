# INSTRUKSI UPLOAD — Jejak Buddha 2026-10-20 (LONG)

## Video
- Kisah: **Khotbah pertama di Taman Rusa Isipatana** (pool #6)
- Naskah: `naskah-beats.md` (1007 kata, 8 beat, mudiwa + bumper suara user setelah beat 3)
- File video final: DIHAPUS dari lokal setelah upload sukses (aturan user) — YouTube jadi arsip

## Metadata terpasang via API
- Judul: Khotbah Pertama Sang Buddha yang Melahirkan Sebuah Agama
- Deskripsi: hook + konteks + 8 chapters + CTA + video terkait + 5 hashtag + atribusi footage (lihat upload_long_api.py)
- Hashtag: #butifyourcloseyoureyesmeme #buddha #khotbahbuddha #sarnath #foryou
- Tags: 20 tag relevan · Kategori 27 (Education) · Bahasa id · Bukan untuk anak-anak

## Hasil upload (via API, sesi 'jejakbuddha')
- Channel terverifikasi: UC1PNEzhOmAH08p75vwp7n0A (@JejakBuddha) ✓
- Video ID: **uQ5n9Coygt0** — https://youtu.be/uQ5n9Coygt0
- Status: private, **terjadwal tayang Rabu 2026-10-21 19:00 WIB** ✓
- Durasi di API masih P0D (video sedang diproses YouTube saat upload — normal)
- Hasil JSON: `upload-hasil-long.json`

## PENDING — kerjakan manual di YouTube Studio
1. **AI disclosure**: centang "Altered content" (API tidak mendukung field ini).
2. **Thumbnail custom**: upload `thumbnail.png` via Studio (API 403 — akun belum verifikasi HP; jangan retry via API).
3. **Komentar**: set "Allow all comments" (aturan wajib: komentar ON di semua video).
4. **End screen**: tambahkan end screen → video long paling sepi channel (cek Studio).
5. **Komentar pin**: pin komentar berisi link video terkait (https://youtu.be/JDELqvSXPGc).
6. **Playlist**: masukkan ke playlist tematik "Kisah Sang Buddha" (buat bila belum ada).

## Catatan produksi
- Footage: 17 klip Wikimedia Commons REUSE dari 2026-10-18 (0 klip baru), tiap klip maks 2x, verifikasi kemarin. Atribusi CC BY/SA di deskripsi.
- Render: 21 segmen via ffmpeg-queue.sh, sukses semua; verifikasi per-stream: video 433.87 dtk / audio 433.90 dtk.
- Durasi final: 433.9 dtk = 7:14.
- File video final dihapus dari lokal pasca-upload (aturan user). concat.mp4 + segmen + voiceover-full.mp3 masih ada untuk kebutuhan potong shorts besok.
