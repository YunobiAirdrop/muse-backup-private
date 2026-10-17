# Run log: loker-harian 2026-10-05

- Trigger: scheduled_for Mon 2026-10-05 12:47:49 WIB (user minta produksi dimulai sekarang)
- Pipeline ./jalan.sh selesai exit 0 (~53 menit)
- [1/3] Agregasi: gnews-loker 100 item, gnews-rekrutmen-bumn 100 item, gnews-loker-terbaru 77 item -> 10 loker masuk antrean (riwayat total 30)
- [2/3] Tulis artikel: 9/10 OK. 1 GAGAL: item 7/10 (Lowongan Kerja Ancol Oktober 2026, Ada 6 Posisi untuk D3 hingga S1) - semua model/key OpenRouter gagal dengan 429 (rate limit free-tier)
- [3/3] Posting prep: 9 artikel -> data/webpost/loker.json + instruksi-loker.txt
- Browser task (login khususstokyunobi@gmail.com, blog "Info Loker Terkini" 7121976229691283867): 9/9 TERPOSTING, terverifikasi "Dipublikasikan (19)", "Draf (0)". Minor: artikel 5 & 9 sempat gagal pengisian sekali, diulang berhasil, tidak duplikat.

Judul terposting:
1. Lowongan Kerja Alfamidi Tangerang 2026
2. Lowongan Kerja Subang 2026 – Ribuan Posisi Tersedia
3. Lowongan Kerja Ancol Fresh Graduate 2026
4. Lowongan Kerja Kemnaker Riset Data 2026
5. Lowongan Kerja BYD Oktober 2026: 46 Posisi untuk Fresh Graduate
6. Lowongan Kerja Teacher Coordinator Admin Social Media Bali 2026
7. Lowongan Kerja Emiten Prajogo Pangestu 2026
8. Lowongan Tentor 5 Mata Pelajaran Rumah Belajar Spirit 2026
9. Lowongan Kerja TPIA 2026 — 1.000 Formasi Dibuka

Catatan: loker_riwayat.json total 30 (10 kemarin + 10 hari ini masuk antrean baru hari ini? - riwayat 30 = 20 sebelumnya + 10 hari ini). Maks 10/hari terpenuhi (9 efektif).
