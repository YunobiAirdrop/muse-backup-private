---
id: balas-komentar-youtube-malam
title: Balas komentar YouTube malam (13 channel)
enabled: true
owner: goal:channel-youtube-internasional-berbahasa-inggris
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 21:11:00
timeout_secs: 7200
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
# Balas komentar YouTube otomatis — MALAM (13 channel)

PERSETUJUAN USER: 2026-10-07 ("boleh") — auto-reply komentar 2x sehari (pagi + malam) di semua 13 channel. Balasan diposting sebagai channel, atas nama user.

13 CHANNEL (12 di akun khususstokyunobi@gmail.com + 1 di akun stokakunwebyunobi@gmail.com):
@ceritarakyat862 (ID), @KisahPOV (ID), @LimaMisteri (ID), @TrueCaseFilesTV (EN), @TalesOfDreadTV (EN), @MysteryShadowsTV (EN), @EchoesOfThePast-e9m (EN), @CosmosUnknownTV (EN), @TheDarkMindFiles-s6i (EN), @BizarreWorldDaily (EN), @AncientEmpiresTV (EN), @StrangeTales-g6n (EN), @tinybuilders-d5z (EN)

Baca dulu: ~/workspace/youtube-otomatis/comment-intel-playbook.md (tata cara menambang komentar untuk ide video & perbaikan).

LANGKAH:
1. Baca ~/workspace/youtube-otomatis/komentar-terbalas.json (buat {} jika belum ada) — berisi comment ID yang sudah ditangani. JANGAN balas komentar yang ID-nya sudah ada di sini.
2. Via browser ke YouTube Studio (sesi login sudah tersimpan — JANGAN login ulang / buat akun baru):
   - Untuk tiap channel: ganti channel via pemilih channel → menu "Komentar" → urutkan terbaru.
   - Ambil komentar BARU (belum ada di komentar-terbalas.json), maksimal 10 per channel, total maksimal 30 balasan per run (hindari deteksi spam YouTube — beri jeda ±10 detik antar balasan).
3. ATURAN BALASAN (ketat):
   - BOLEH dibalas: pertanyaan ringan, pujian, diskusi, saran topik, komentar lucu.
   - JANGAN DIBALAS (tandai dilewati): spam, link mencurigakan, ujaran kebencian/SARA, politik panas, promosi, komentar toxic. Jangan di-like juga.
   - JANGAN DIBALAS, CATAT UNTUK USER: komplain serius, pertanyaan sensitif/kontroversial, tuduhan — laporkan ke user, jangan ambil risiko.
   - Gaya balasan: KONTEKSTUAL (nyambung isi komentarnya), 1-2 kalimat, hangat & personal, bahasa = bahasa channel (ID/EN). Sesekali boleh 1 emoji, jangan tiap balasan. DILARANG template generik ("thanks for watching!").
   - Like komentar yang genuine & bagus.
4. PIN KOMENTAR: untuk video terbaru tiap channel yang belum ada pinned comment — posting 1 komentar pertanyaan mancing diskusi sebagai channel, lalu pin. (Contoh ID: "Menurut kalian bagian mana yang paling seram? 👇" / EN: "Which part shocked you the most? 👇")
5. COMMENT INTEL (wajib tiap run malam): saat membaca komentar, tandai yang masuk kategori playbook (ide-video, faq, keyword, koreksi, sentimen). Tulis ke ~/workspace/youtube-otomatis/comment-intel.json (append, format sesuai playbook). Koreksi produksi dari 1 channel → cek channel lain juga.
6. Update komentar-terbalas.json dengan semua ID yang ditangani + statusnya (dibalas/di-like/dilewati/dilaporkan).
7. JANGAN verifikasi HP, JANGAN ubah setting channel apa pun.

LAPORAN (Bahasa Indonesia, singkat): per channel — berapa dibalas, di-like, dilewati + DAFTAR komentar yang butuh perhatian user (kutip isi komentarnya). Tambahkan bagian "INTEL KOMENTAR": maksimal 5 temuan terbaik + aksi (mis. ide video masuk antrean topik / koreksi diterapkan). Jika 0 komentar baru di semua channel, cukup tulis "tidak ada komentar baru".
Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md
