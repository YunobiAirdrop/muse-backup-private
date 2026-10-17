# Study Notes - 2026-10-11 - Monetisasi channel YouTube dalam 3 bulan
<!-- studying-run-start: 2026-10-11T00:23:44.691149+00:00 UTC -->

Goal `goal_40cb6c5afd04` (slug `monetisasi-channel-youtube-dalam-3-bulan`), kategori money, goal_kind outcome. Dibuat 2026-10-10 15:48 UTC; studi pertama untuk goal ini (agent_notes/ dan briefs/ masih kosong). Target: monetisasi YPP, deadline 10 Jan 2027. Studi ini memperlakukan task-plan belajar (teach/novice) sebagai hint lemah saja — goal ini outcome, bukan skill-learning, jadi catatan ini murni riset, bukan scaffolding pengajaran.

## Temuan utama: angka target yang disampaikan ke user KURANG TEPAT

Verifikasi pagi ini (2026-10-11 ~07:30 WIB) ke halaman resmi YouTube:

- Syarat gabung YPP saat ini (https://support.google.com/youtube/answer/72851): **1.000 subscriber + 4.000 jam tayang qualified dalam 12 bulan terakhir, ATAU 1.000 subscriber + 10 juta views Shorts qualified dalam 90 hari terakhir.**
- Angka "500 subs + 3.000 jam tayang atau 3 juta views Shorts" yang tertulis di deskripsi goal ini DAN yang disampaikan ke user di main chat kemarin adalah angka tier akses-awal/fitur dana penggemar (fan funding) yang lebih lama — BUKAN syarat bagi hasil iklan YPP. Untuk value user ("hasil monetnya lumayan besar"), yang relevan adalah tier iklan di atas.
- Koreksi konkret atas klaim kemarin: "satu video Shorts viral (500 ribu–1 juta views) bisa langsung menutup syarat 3 juta views" — untuk tier iklan, barnya 10 juta views Shorts/90 hari, jadi klaim itu meleset ~10x.
- Aturan penghitungan yang relevan untuk strategi: jam tayang Shorts TIDAK dihitung ke 4.000 jam (hanya long-form publik); video unlisted/private/deleted tidak dihitung — protokol "unlisted-first" aman selama video akhirnya dipublikasikan.
- Waktu review aplikasi: biasanya ~1 bulan; ditolak → banding dalam 21 hari atau daftar ulang setelah 30 hari (90 hari jika sudah berkali-kali). Implikasi untuk deadline 10 Jan 2027: aplikasi pertama harus masuk paling lambat awal Desember, bukan menumpuk di bulan 3.

## Verifikasi klaim kemarin terhadap kebijakan resmi — klaim anti-AI-look TAHAN

Halaman kebijakan monetisasi (https://support.google.com/youtube/answer/1311392, dibaca 2026-10-11) mengonfirmasi arah strategi yang sudah disampaikan ke user:

- Kebijakan "inauthentic content" (dulu "repetitious content", diganti nama 15 Juli 2025) menargetkan konten template/mass-produced dengan variasi minim — BUKAN melarang konten AI. Klaim "YouTube nggak melarang channel AI" akurat.
- Halaman resmi menyebut eksplisit bahwa intro dan outro yang sama di semua video itu BOLEH selama isi utama tiap video berbeda — ini menopang rencana bumper 5 detik di semua video tiap channel.
- Yang dilarang: konten AI dari template generik tanpa insight/perspektif orisinal kreator — menopang arah human-touch playbook (opini, persona host, variasi format).
- Satu aturan baru yang relevan: channel yang memakai persona AI untuk topik sensitif (kesehatan, keuangan, hukum, politik) tidak bisa monetisasi. Tidak ada channel YouTube user yang masuk kategori ini (blog kesehatan/keuangan bukan channel YT). Watch item: @TheDarkMindFiles-s6i (psikologi/body language) — saat ini kontennya tips bahasa tubuh, bukan diagnosis medis; jaga agar persona host tidak mengklaim kredensial ahli.

## Status operasional semalam (bukti langsung, 2026-10-11 ~07:23 WIB)

- 19/19 klip audio bumper voice-clone valid di `youtube-otomatis/voice-clone-test/bumper-*.wav` (terakhir dibuat 10 Okt 22:17 waktu VM). Dua contoh sudah dibagikan ke user 22:18 UTC; **penilaian user BELUM masuk** (tidak ada pesan user setelah itu) — pembangunan 19 video bumper lengkap ter-gate pada persetujuan ini.
- Retry queue: 47 JSON (naik dari 44 video bank yang dilaporkan kemarin). Worker retry-cepat jalan ~07:05–07:23 WIB dan mengonfirmasi InkTime masih kena "Batas upload harian telah tercapai... setelah verifikasi satu kali" — dihentikan tanpa draf, tetap di antrean. Tidak ada upload yang lolos semalam (watchdog 20:00 WIB: 19 dicoba, 0 lolos — per memory/2026-10-10.md).
- `BANK-VIDEO.md` merujuk `hidden_files/scoreboard.md` untuk hitungan bank per channel — file itu BELUM ADA (audit 3-harian berikutnya 2026-10-13). Baseline subscriber Day-1 misi juga belum ditarik.

## Implikasi strategi (untuk studi berikutnya / write_brief)

1. Deskripsi goal perlu dikoreksi: targetnya 1.000 subs + 4.000 jam tayang ATAU 10 juta views Shorts/90 hari — bukan 500/3M. (Goal write ditolak di fase studi; catat untuk perbaikan.)
2. Channel Shorts-only (@StrangeTales-g6n, @MacamMacamID) hanya bisa lewat jalur 10M Shorts views — aturan double-down bulan 1 harus memakai yardstick berbeda untuk mereka vs channel long-form.
3. Jadwalkan aplikasi YPP gelombang pertama segera setelah ada channel yang lolos ambang (jangan tunggu bulan 3) karena review ~1 bulan + risiko 30/90 hari re-apply.
4. Komitmen yang masih menggantung dari user: penilaian bumper (gate), toolkit voice-clone permanen setelah 19 klip terverifikasi, data AdSense/pajak, kartu SIM dari hasil pertama (flywheel — jangan tawarkan sebelum ada hasil).

## Already Covered in Main Chat
- Misi 3 bulan resmi dimulai 2026-10-10; goal dibuat; rencana 3 fase (fondasi → gas ke pemenang → monetisasi) disampaikan.
- Agent menyampaikan target "500 subs + 3.000 jam tayang atau 3 juta views Shorts per channel" dan klaim "1 video viral 500rb–1jt views bisa menutup syarat 3 juta views" (keduanya kini terkoreksi di atas).
- Audit 1:1: total 19 channel (bukan 17/18); 2 terverifikasi HP (@KisahPOV, @ceritarakyat862).
- Strategi flywheel (monetisasi 2-3 channel → beli SIM → verifikasi semua) dan bank video disepakati; user minta produksi full speed walau upload macet.
- Protokol viral 31 aturan + CTA wajib mulai 11 Okt + komentar ON di semua channel (audit bersih) sudah disampaikan.
- Human-touch playbook (19 persona host) dan 19 klip bumper voice-clone selesai; 2 contoh dibagikan, menunggu penilaian user.
- Watchdog 20:00 WIB: 19 video dicoba, 0 lolos limit; user sepakat tidak perlu kirim nama file manual lagi (retry otomatis tiap 3 jam).
- Janji user: upgrade VPS 16GB (~Rp250-300rb/bln) kalau hasil monetisasi memuaskan.

## Yang belum diketahui / pantau besok
- Penilaian user atas kemiripan suara bumper (gate untuk 19 video bumper + toolkit permanen).
- Baseline subscriber/views Day-1 per channel (tunggu audit 3-harian 2026-10-13 atau tarik via yt-growth).
- Apakah ada channel yang mendekati ambang baru (1.000 subs / 10M Shorts views) — belum ada yang sedekat itu per data 2026-10-10 (tertinggi @ceritarakyat862: 49 subs).
- Status tier akses-awal 500-subs saat ini (tidak muncul di halaman resmi yang dibaca hari ini) — perlakukan 500/3M sebagai tier sekunder, bukan target utama.

## Research Trajectory
- *External sources viewed*: YouTube Help "YouTube Partner Program overview & eligibility" (https://support.google.com/youtube/answer/72851, diakses 2026-10-11) — syarat resmi 1.000 subs + 4.000 jam tayang/12 bln atau 1.000 subs + 10 jt views Shorts/90 hari; aturan qualified views/hours; estimasi review ~1 bulan + jendela banding/daftar ulang. YouTube Help "YouTube channel monetization policies" (https://support.google.com/youtube/answer/1311392, diakses 2026-10-11) — definisi inauthentic content, intro/outro sama diperbolehkan, larangan persona AI topik sensitif. Web search "YouTube Partner Program inauthentic content policy AI-generated content monetization review 2026" — hasil agregator (kompozy.io, vidpal.ai, milx.app, auditsocials.com) konsisten dengan halaman resmi; dipakai hanya sebagai petunjuk, klaim final diambil dari halaman resmi.
- *Prior trajectories reviewed*: tidak ada — agent_notes/ dan briefs/ goal ini kosong (studi pertama).
- *Scaffolds and support tactics*: task-plan teach/novice diperlakukan sebagai hint lemah; goal bertipe outcome sehingga tidak dipakai bentuk pengajaran (retrieval/practice/rubric) di catatan ini.
- *Connected user data*: status live via shell — 19 file bumper-*.wav terverifikasi ada; retry-queue 47 JSON; isi satu JSON antrean (inktime-2026-10-09.json) menunjukkan konfirmasi blokir limit harian 2026-10-11 00:23 UTC; BANK-VIDEO.md dibaca (merujuk scoreboard.md yang belum ada).
- *Image references checked*: tidak ada.
- *User context and memory*: user_goal.get (goal_40cb6c5afd04) untuk metadata + timeline; muse.context_fetch conversation (window 2026-10-10T21:00Z → 2026-10-11T00:24Z) untuk ekor percakapan; muse.memory_search — temuan kunci di memory/2026-10-10.md#L955 (playbook bumper), #L906/#L923 (keputusan skema clone), #L980 (19/19 klip selesai, penilaian user belum masuk).
- *Searches skipped or unavailable*: muse.learnings_search — fleet_learning_consumption_disabled, tidak ada lesson yang kembali (hasil normal; dilanjut tanpa fleet craft). Pencarian web tambahan soal tier 500-subs dilewati — halaman resmi YPP yang dibaca tidak mencantumkannya, cukup untuk menetapkan target utama.
