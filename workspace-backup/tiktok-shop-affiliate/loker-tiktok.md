# Loker TikTok Bible — @ngeweb.yuk (mode kejar followers)

## Misi
600 followers (sekarang: 5). Konten = info lowongan kerja, 1 loker = 1 video.
Setelah user mengonfirmasi 600 followers → aktifkan kembali cron `tiktok-shop-review-harian` (mode review produk).

## Sumber loker (jangan mengarang)
`~/workspace/loker-otomatis/data/artikel-loker.json` — pilih artikel yang `slug`-nya BELUM ada di `loker-history.json`.
Prioritas: artikel terbaru, posisi populer (pabrik, retail, kurir, admin, BUMN).
DILARANG mengarang gaji/deadline/link — yang tidak ada di artikel tulis "cek info lengkapnya" tanpa angka palsu.

## Format video (1 video per run, 25-40 detik, vertical 9:16)
1 loker = 1 video. Struktur naskah:
- **0-3 dtk HOOK** (wajib, penentu FYP): gaji/posisi/perusahaan langsung — contoh: "Gaji 8 juta, lulusan SMA bisa daftar!" / "LOKER TERBARU! Garuda Indonesia buka lowongan awak kabin haji!" Jangan mulai dengan perkenalan/logo.
- **Isi**: syarat singkat (maks 3 poin), lokasi, cara melamar — padat, gaya ngobrol.
- **Teks on-screen ber-keyword** (TikTok 2026 membaca teks seperti mesin pencari): overlay besar "LOKER TANGERANG 2026", "LOKER PABRIK", "GAJI UMR" — sesuaikan dengan lokernya.
- **Anti-scam (wajib, verbal + teks)**: "Ingat ya — perusahaan asli TIDAK PERNAH minta uang atau biaya admin. Waspada penipuan!"
- **CTA akhir (pancing interaksi = bahan bakar FYP)**: "Link loker lengkapnya ada di bio! Komen domisili kamu, besok saya cariin loker daerah situ! Tag temanmu yang lagi cari kerja! Follow @ngeweb.yuk!" (teks overlay "LINK DI BIO 👆" di 3 detik terakhir)
- Komentar yang minta loker daerah tertentu → JADIKAN video berikutnya (loop konten dari penonton).

## Produksi (hemat token — TANPA klip AI video)
1. Tulis naskah Indonesia 25-40 detik (tanpa pola AI: tanpa "di era digital", tanpa list kaku).
2. 1 gambar AI per video: suasana kerja yang relevan (pabrik/kantor/kurir/retail sesuai loker), tanpa teks di gambar.
3. Rakit via `~/workspace/youtube-otomatis/ffmpeg-queue.sh`: gambar + efek zoompan (Ken Burns) + teks overlay BESAR (posisi, perusahaan, lokasi) + voiceover TTS Indonesia natural + film grain halus → `output/loker-{slug}-{YYYYMMDD}.mp4`.
4. Tulis caption → file .txt.
5. Posting via Taisly: `taisly posts:create --video <file> --platforms 6ac71c80572b2159e0a2f190 --description "<caption>"`. Cek via `taisly posts:status --id <historyId>`.
6. Update `loker-history.json`: {tanggal, slug, judul, file, status, taisly_history_id}.

## Caption
Baris 1 = hook + keyword (contoh: "Loker pabrik Tangerang gaji UMR, lulusan SMA bisa daftar!"). Baris 2 = CTA komen. Hashtag (maks 5, campuran besar+niche): #loker #infoloker #lowongankerja #fyp #tiktokindonesia — tambah 1 hashtag lokasi spesifik bila relevan (contoh #lokertangerang).

## Laporan ke user
Judul loker + status posting Taisly (ok/gagal + historyId). Akhiri SELALU dengan: "Followers sekarang berapa? Kabari saya kalau sudah 600 biar langsung mulai mode review produk. Oh iya — balas komentar yang masuk ya, itu bahan bakar FYP."

## Batasan
- JANGAN menyebut/mempromosikan produk afiliasi di konten ini (mode kejar followers murni).
- JANGAN retry posts:create buta setelah timeout — cek History dulu.
- 1 slug artikel = 1 video, jangan dipakai ulang.
