# INSTRUKSI UPLOAD — Jejak Buddha 2026-10-18 (LONG)

## Video
- File: `/home/hatch/workspace/jejak-buddha/2026-10-18/jejak-buddha-2026-10-18-upload.mp4` (223 MB, 420.19 dtk = 7:00)
- Kisah: **Pencerahan di bawah pohon Bodhi** (pool #5)
- Naskah: `naskah-beats.md` (1001 kata, 8 beat, mudiwa + bumper setelah beat 3)
- Thumbnail: `thumbnail.png` (frame siluet Borobudur fajar + teks "MALAM PENCERAHAN")

## Metadata terpasang via API
- Judul: Satu Malam di Bawah Pohon Ini Mengubah Sejarah Manusia
- Deskripsi: hook + konteks + 8 chapters + CTA + 2 video terkait + 5 hashtag + atribusi footage (lihat upload_long_api.py)
- Hashtag: #butifyourcloseyoureyesmeme #buddha #kebijaksanaan #sejarahbuddha #foryou
- Tags: 20 tag relevan · Kategori 27 (Education) · Bahasa id · Bukan untuk anak-anak

## Hasil upload (via API, sesi 'jejakbuddha')
- Channel terverifikasi: UC1PNEzhOmAH08p75vwp7n0A (@JejakBuddha) ✓
- Video ID: **JDELqvSXPGc** — https://youtu.be/JDELqvSXPGc
- Status: private, **terjadwal tayang Senin 2026-10-19 19:00 WIB** ✓
- Durasi di API masih P0D (video sedang diproses YouTube saat upload — normal)
- Hasil JSON: `upload-hasil-long.json`

## PENDING — kerjakan manual di YouTube Studio
1. **AI disclosure**: centang "Altered content" (API tidak mendukung field ini).
2. **Thumbnail custom**: upload `thumbnail.png` via Studio (API 403 — akun belum verifikasi HP; jangan retry via API).
3. **Komentar**: set "Allow all comments" (aturan wajib: komentar ON di semua video).
4. **End screen**: tambahkan end screen → video long paling sepi channel (cek Studio).
5. **Komentar pin**: pin komentar berisi link video terkait (https://youtu.be/sTwtnVn1pro).
6. **Playlist**: masukkan ke playlist tematik "Kisah Sang Buddha" (buat bila belum ada).

## Catatan produksi
- Footage: 18 klip Wikimedia Commons (8 baru + 10 reuse ≤2x), verifikasi 1 frame/klip manual, lisensi CC0/PD/CC BY/CC BY-SA. Laporan: `footage/LAPORAN.md`.
- 6 klip ditolak verifikasi (watermark/kerumunan/rumah ibadah lain) dan dihapus.
- Render: 21 segmen via ffmpeg-queue.sh; antrean padat (~8 render channel lain) — total render ±1 jam; skrip resumable, 1x proses induk mati di tengah (14/21) lalu dilanjutkan tanpa kehilangan progres.
- Upload: 1x gagal karena python sistem tanpa modul google → pakai venv yt-growth (aturan AGENTS.md), lalu sukses.
- File video final JANGAN dihapus (dibutuhkan run besok untuk potong 3 shorts; cron hapus-video yang mengurus).
