---
id: cek-blackdeath-2100
title: Cek render Black Death + upload
enabled: true
owner: goal:channel-youtube-internasional-berbahasa-inggris
execution:
  kind: main_agent
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-10-12T21:00:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","origin_provider":"main","chat_kind":"direct","provider":"main","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
TUGAS UNTUK AGEN UTAMA (jalankan sendiri di chat ini): cek render ulang video long Echoes of History "Black Death" dan tuntaskan sampai upload.

STATUS TERAKHIR (12 Okt ±19:57 WIB): agen render error (proses latarnya hilang dari pantauan runtime), TETAPI build-nya ternyata masih hidup sebagai proses terlepas (nohup): `rakit_singlepass_2026-10-11.py` + ffmpeg-queue sedang encode ke ~/workspace/youtube-otomatis/history-en/video/2026-10-11.mp4 (filter lengkap: 70 beat + bumper tengah + 5 overlay + CTA; target durasi ±619 dtk). Ada juga proses rakit_3step lama yang menulis video/_silent-2026-10-11.mp4 — biarkan, jangan dibunuh. Paket upload siap: upload-instruksi-2026-10-12.md + upload-2026-10-12.json (judul "The Black Death Came on Ships — Europe Was Never the Same", hashtag deskripsi ditutup #foryou, slot 13 Okt 07:00 WIB).

LANGKAH:
1. Cek video/2026-10-11.mp4: ada? ffprobe durasi ±619 dtk, 1280x720, ada audio? Ukuran wajar (>150MB)?
2. BILA SELESAI: spawn subagent untuk (a) potong 3 shorts bank shorts/2026-10-11-s1/s2/s3.mp4 (ikuti shorts-plan-2026-10-11.json / potong_shorts_2026-10-11.py), verifikasi tiap file; (b) upload long via API yt-growth slug "history-en" — cek anti-dobel dulu (judul sama sudah ada? jangan dobel), private publishAt 2026-10-13T00:00:00Z, metadata dari upload-2026-10-12.json, coba thumbnail-2026-10-11.jpg (tolak = catat saja). Sesudah videoId didapat: spawn browser task centang AI disclosure di Studio (channel @EchoesOfThePast-e9m — verifikasi channel ID dari paket instruksi; STOP bila ada tantangan verifikasi Google, jangan picu login). Laporkan hasil lengkap ke user di chat ini.
3. BILA BELUM SELESAI tapi proses encode masih hidup (cek ps untuk rakit_singlepass/ffmpeg history-en): laporkan singkat ke user bahwa render masih jalan, lalu buat cron runonce baru +45 menit dengan isi tugas yang sama persis (id baru: cek-blackdeath-lanjut-<jam>).
4. BILA proses mati DAN file tidak ada/korup: spawn subagent render ulang (build_package_2026-10-11.py → rakit_singlepass_2026-10-11.py, ffmpeg wajib via ffmpeg-queue.sh, verifikasi ffprobe di sesi yang sama), lalu laporkan ke user bahwa render diulang dan upload menyusul sebelum slot 13 Okt 07:00 WIB; buat runonce pengecekan lagi +60 menit.
Jangan edit MEMORY.md; observasi ke ~/memory/2026-10-12.md bila perlu.
