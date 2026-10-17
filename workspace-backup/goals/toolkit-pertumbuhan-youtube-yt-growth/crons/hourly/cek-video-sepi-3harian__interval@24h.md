---
id: cek-video-sepi-3harian
title: Cek + perbaiki + share video sepi harian (semua channel)
enabled: true
owner: goal:toolkit-pertumbuhan-youtube-yt-growth
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-16T13:09:41
  every: 24h
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
CEK VIDEO SEPI HARIAN + PERBAIKAN OTOMATIS + SHARE 3X (otorisasi tetap user 2026-10-12 untuk perbaikan metadata tanpa persetujuan per-run; otorisasi user 2026-10-15: setiap video mentok/sepi di-share-copy 3x).

TOOLKIT: ~/workspace/youtube-otomatis/yt-growth/ (python: ./venv/bin/python dari folder itu).
LOG SHARE: ~/workspace/youtube-otomatis/yt-growth/hidden_files/share3x-log.json (format: {"upload_shared": [videoId...], "quiet_shared": {"videoId": "YYYY-MM-DD"}}). Cooldown: satu video tidak di-share ulang dalam 7 hari (anti penalti manipulasi engagement).

LANGKAH:
1. SCAN: jalankan `scan_sepi.py` → output hidden_files/sepi-<tanggal-hari-ini>.json (semua channel: status, umur, views).
2. BANDINGKAN dengan scan sebelumnya (file sepi-*.json tertua kedua di hidden_files/): video MENTOK = publik, umur >24 jam, masuk daftar sepi (shorts <50 views / long <100 views) DAN kenaikan views sejak scan lalu ≤2. Video yang baru pertama kali masuk daftar sepi juga kandidat.
3. DIAGNOSIS per video mentok (kerahkan analisis penuh):
   a. `seo_audit.py video SLUG VIDEO_ID` — cacat metadata (hashtag, struktur deskripsi, tags).
   b. Untuk 3 video terburuk per channel: `retention.py SLUG VIDEO_ID` — titik jatuh penonton (bila Analytics timeout/kosong, catat apa adanya, jangan mengarang).
   c. Cek duplikat: judul sama/persis mirip di channel yang sama.
   d. Bandingkan pola judul dengan file competitor terbaru di ~/workspace/blog-otomatis/data/competitor-*.md bila ada.
4. PERBAIKI via API (yt_put, pola yt_push.py — pertahankan categoryId/bahasa, JANGAN hapus link afiliasi/atribusi/kredit di deskripsi):
   - Judul: formula packaging-formulas.md; SHORTS ditutup #foryou (maks 4 hashtag, pendamping = hashtag paling rame relevan dari protokol-viral.md bagian 14); LONG tanpa hashtag di judul.
   - Deskripsi: shorts tambahkan link ke long pasangannya bila jelas; long pastikan hook 150 karakter pertama + CTA subscribe + baris hashtag minimal 3 (#foryou + 2 trending relevan).
   - Tags: bangun ulang ≤480 karakter dari keyword judul + niche.
   - Duplikat persis dengan 0 views → set PRIVATE (kembaran ber-view tetap publik). Tidak ada video yang dihapus.
   - Video yang metadatanya SUDAH bagus (audit ≥90 & tidak ada cacat nyata): JANGAN diubah-ubah — catat sebagai "sepi faktor algoritma/umur channel".
5. BATAS: jangan sentuh video <24 jam, jangan ubah jadwal/visibilitas (selain duplikat 0-view), audience, atau setelan komentar. Channel tanpa token (inktime, macammacam): hanya laporkan, jangan menulis.
6. SIMPAN laporan lengkap ke hidden_files/laporan-sepi-<tanggal>.md (per channel: video mentok, diagnosis, perubahan lama→baru, yang tidak diubah + alasannya). Verifikasi read-back 2 video acak per channel yang diubah.
7. SHARE-3X: untuk setiap video mentok dari langkah 2 yang statusnya PUBLIC dan (belum pernah di-share ATAU quiet_shared >7 hari lalu): via browser task, buka URL video → klik tombol Share → Copy link → ulangi 3x per video. Batch ±10 video per browser task. Video private/unlisted: lewati. Setelah selesai update quiet_shared di share3x-log.json dengan tanggal hari ini.
8. LAPORKAN ke user SINGKAT: berapa video discan, berapa mentok, berapa diperbaiki, berapa di-share 3x, sorotan per channel (maks 1 baris/channel), total views daftar sepi vs scan sebelumnya. Jujur bila tidak ada yang bisa diperbaiki.
9. Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md.
