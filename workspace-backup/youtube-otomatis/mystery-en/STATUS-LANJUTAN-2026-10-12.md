## UPDATE 2026-10-13 (run 16:11 WIB)
- Produksi LONG Somerton Man SELESAI: video/2026-10-11.mp4 (626,5 dtk) + 3 shorts bank shorts/2026-10-11-s1..s3.mp4 (45 dtk, valid). Thumbnail A/B + upload-instruksi-2026-10-13.md siap (slot 2026-10-14 07:00 WIB).
- Upload via browser task ke channel BENAR (UCjxESFWyFPOkGTSpajK69Lw terverifikasi di URL) GAGAL — penyebab tidak terkonfirmasi (bukan limit harian; tidak tulis retry-queue). upload-terakhir.txt TETAP "shorts:2026-10-06".
- TINDAK LANJUT run berikut: retry upload LONG ini (file + instruksi siap), lalu tulis "long:2026-10-13" HANYA setelah upload berhasil terjadwal.
- KOREKSI (laporan browser tiba belakangan): penyebab TERKONFIRMASI = "Batas upload harian telah tercapai". Antrean ditulis: retry-queue/mystery-en-2026-10-13.json (slot_target 2026-10-15 07:00 WIB) — watchdog 20:00 kerjakan setelah >= 23 jam. Browser sempat mendarat di channel salah (Weird World Daily) tapi beralih benar ke Unsolved Shadows; tidak ada efek eksternal.

# STATUS LANJUTAN — Mystery EN (Unsolved Shadows) — per 2026-10-12 18:15 WIB

## Produksi hari ini: LONG "The Somerton Man / Tamam Shud" (produksi 2026-10-11 diselesaikan 12 Okt)
Pola: upload-terakhir.txt = "shorts:2026-10-06" → hari ini LONG. JANGAN ubah upload-terakhir sampai upload LONG ini BERHASIL terjadwal.

## Yang SUDAH selesai (jangan ulangi)
- Script: script/2026-10-11.txt (72 beat, ±10:27, ada opini/teori narator beat 63-65, CTA, hook detail fisik).
- Audio: audio/2026-10-11.mp3 (627,6 dtk) + audio/durasi-beat-2026-10-11.json (72 beat).
- Gambar: gambar/2026-10-11-clean/beat-001..072.webp LENGKAP 72/72.
  - Catatan: beat-060 memakai ulang gambar beat-012 (barang bukti incl. bungkus rokok) dan beat-061 memakai ulang beat-064 — prompt asli keduanya gagal digenerate (integrity_check_failed) dan TIDAK BOLEH diulang.
  - 7 gambar sempat gagal via subagent; berhasil digenerate ulang oleh parent dengan prompt dirumuskan ulang (adegan kosong/objek bukti, tanpa mayat): beat 001, 009, 010, 014, 035.
- Thumbnail: thumbnail-2026-10-12.jpg ("TAMAM SHUD") + thumbnail-2026-10-12-b.jpg ("NO NAME NO CAUSE") untuk Test & Compare.
- Instruksi upload LENGKAP: upload-instruksi-2026-10-12.md (judul "A Dead Man, No Name — Only Two Words: Tamam Shud", deskripsi 6 bagian + chapters + #foryou, AI disclosure, komentar Allow all, Unlisted dulu → Terjadwal 2026-10-13 07:00 WIB — sesuaikan slot ke hari tayang berikutnya saat upload benar-benar terjadi).

## Yang SEDANG berjalan (background, setsid, PID python 140152 per 18:15 WIB)
- batch_rakit.py (BATCHN=12): python3 batch_rakit.py gambar/2026-10-11-clean audio/2026-10-11.mp3 video/2026-10-11-base.mp4 audio/durasi-beat-2026-10-11.json
- Log: /tmp/mystery-batch12-20261012.log — batch-00.mp4 SELESAI (124 dtk) di video/_tmp_batch/; batch 1-5 antre slot ffmpeg-queue.
- Script ini RESUME-SAFE: batch yang sudah valid dilewati. Kalau python mati, jalankan ulang perintah yang sama (BATCHN=12, setsid nohup, redirect ke log yang sama).
- Penyebab lambat: ffmpeg-queue (maks 2 render se-fleet) jenuh total sejak 16:11 — 19 channel produksi bareng + backlog; slot dipegang render panjang channel lain (kisah-alkitab ±1 jam). BUKAN macet: slot stale sempat dibersihkan 1x (slot2 PID 27054 mati → rm -rf sesuai AGENTS.md).

## Langkah berikutnya (run lanjutan / besok)
1. Cek log + video/_tmp_batch/ sampai muncul "OK: video/2026-10-11-base.mp4". Kalau python mati → relaunch (lihat di atas).
2. Final assembly: python3 final_assembly_2026-10-11.py video/2026-10-11-base.mp4 video/2026-10-11.mp4 (subtitle terbakar + overlay 5 momen + CTA 50% + bumper clone di tengah).
3. Potong 3 shorts: python3 potong_shorts_today.py video/2026-10-11.mp4 audio/2026-10-11.durations.txt shorts 2026-10-11 2 46 63 → shorts/2026-10-11-s1..s3.mp4 (BANK untuk hari shorts, judul di upload-instruksi-2026-10-12.md).
4. Upload LONG via browser task mengikuti upload-instruksi-2026-10-12.md (CEK channel @MysteryShadowsTV; JANGAN login ulang/ubah setelan tanpa izin user; sesi tersimpan). Jadwalkan 07:00 WIB hari berikutnya (= 19:00 US Eastern). Berhasil → tulis "long:2026-10-12" ke upload-terakhir.txt (atau tanggal run lanjutan). Kena batas harian → tulis antrean retry-queue sesuai format di instruksi/anti-mogok.
5. Antrian LAMA yang masih pending (bukan bagian run ini): retry-queue/mystery-en-2026-10-07.json (Mary Celeste, slot 2026-10-12 07:00 sudah lewat) — urusan watchdog-retry-upload-youtube; jangan duplikat.

## UPDATE 2026-10-14 (run 16:11 WIB) — produksi LONG baru "The Greenbrier Ghost (1897)"
- Keputusan pola: upload-terakhir.txt="shorts:2026-10-06" → jalur LONG (praktik run 10-12/10-13). LONG Somerton Man (video/2026-10-11.mp4) SUDAH di retry-queue/mystery-en-2026-10-13.json — milik watchdog 20:00 WIB malam ini (umur >=23 jam per 16:06; file+instruksi terverifikasi ada). Run ini TIDAK menyentuh upload Somerton (hindari duplikat/konflik ketukan).
- Produksi baru: script/2026-10-14.txt (58 beat, ~1100 kata, opini pribadi beat 49-51, CTA beat 35 & 58, hook ghost-di-pengadilan). Audio: audio/2026-10-14.mp3 (622 dtk / 10,4 mnt) + durations.txt SELESAI. Voice Magnus EN.
- Gambar: 3 subagent paralel (beat 1-20 / 21-39 / 40-58) → gambar/2026-10-14/, nama dinormalisasi ke beat-NNN.webp setelah selesai.
- Instruksi upload: upload-instruksi-2026-10-14.md (judul "A Ghost Testified in Court — And the Jury Believed Her", chapters terisi, slot 2026-10-17 07:00 WIB, Test & Compare A/B).
- Assembly: batch_rakit.py (BATCHN=12) → final_assembly_2026-10-14.py (subtitle+5 overlay+CTA 50%+bumper) → potong 3 shorts → thumbnail A/B. Dijalankan setelah gambar lengkap.
- riwayat-topik.json: dilengkapi (Mary Celeste 10-07, Somerton 10-11, Greenbrier 10-14).
- Urutan tayang: 10-15 = Somerton LONG (watchdog) → 10-16 = 3 shorts Somerton (run besok) → 10-17 = Greenbrier LONG.

## UPDATE 2026-10-15 (run 16:11 WIB)
- Run 10-14 GAGAL di tengah (runtime restart drain): Greenbrier terhenti di batch assembly (batch-00/01 saja).
- Run ini: resume batch_rakit.py (BATCHN=12) → batch 0 skip, batch 1-4 render OK (58 gambar). Concat+mux (video/2026-10-14-base.mp4) antre slot ffmpeg ~50 mnt (jam 16:11: 19 channel + ~13 waiter, 2 slot) — normal, bukan macet.
- Orkestrator background: mystery-en/orkestrator_2026-10-14.py (setsid nohup, log /tmp/mystery-final-20261015.log) — tunggu base → final_assembly_2026-10-14.py ke TEMP + verifikasi durasi |d-622|<10 → move ke video/2026-10-14.mp4 → potong 3 shorts (beat 22/29/42 = head-turn/autopsy/guilty) → verifikasi 40-50 dtk.
- Thumbnail Greenbrier A/B SELESAI: thumbnail-2026-10-14.jpg ("GHOST TESTIFIED") + thumbnail-2026-10-14-b.jpg ("DEAD WITNESS") — visual dicek OK.
- Upload Somerton LONG: 3x browser.spawn_task GAGAL SEMUA — terminal_reason browser_vm_lease_unavailable (infrastruktur browser/VM down, BUKAN limit harian, BUKAN login; tidak ada halaman termuat → NOL risiko duplikat/parsial). JANGAN spawn lagi hari ini.
- retry-queue/mystery-en-2026-10-13.json TETAP (milik watchdog); slot_target + instruksi (langkah 3) diupdate 2026-10-15 → 2026-10-16 07:00 WIB.
- upload-terakhir.txt TETAP "shorts:2026-10-06" (belum ada upload sukses).
- TINDAK LANJUT run 10-16: (1) cek video/2026-10-14.mp4 + shorts/2026-10-14-s1..s3.mp4 (orkestrator); (2) cek status watchdog — kalau Somerton LONG sudah tayang/terjadwal → upload 3 shorts Somerton (bank shorts/2026-10-11-s1..s3.mp4, judul di upload-instruksi-2026-10-13.md) lalu tulis "shorts:2026-10-16"; kalau Somerton BELUM tayang → retry upload LONG Somerton via browser (jangan duplikat: cek Studio > Konten dulu).
- Urutan tayang: Somerton LONG (watchdog) → 3 shorts Somerton → Greenbrier LONG (slot 2026-10-17 07:00, upload-instruksi-2026-10-14.md).
