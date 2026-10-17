---
id: ekspansi-blog-2mingguan
title: Ekspansi 10 blog baru tiap 2 minggu
enabled: true
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-17T02:13:38
  every: 336h
timeout_secs: 86400
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC6F1E0500BE4C0D5D687445FE06D39D","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Ekspansi jaringan blog otomatis — buat 10 blog baru tiap 2 minggu.

LANGKAH:
1. Baca ~/workspace/blog-otomatis/niche-rotasi.json — ambil 10 niche pertama dari "antrean" yang belum terpakai. Jika sisa kurang dari 10, buat niche baru yang belum ada (pikirkan niche Indonesia yang punya RSS feed aktif).
2. Via browser (login Google sudah tersimpan): buat 10 blog di blogger.com satu per satu dengan jeda ~30 detik. Format nama: {Nama} dan URL {nama-lower}-terbaru.blogspot.com. Jika alamat dipakai, tambah angka.
3. Untuk tiap blog baru: buat varian tema dari tema master (~/workspace/blog-otomatis/tema-kabarviral-v1.19.xml atau backup terbaru) dengan warna aksen + tagline sesuai niche. Upload via browser ke halaman tema masing-masing blog.
4. Update ~/workspace/blog-otomatis/config.json: tambah 10 blog (nama, tampil, blog_id dari API, url, niche, artikel_per_hari: 10, feeds).
5. Tambah prompt niche baru di tulis_ulang.py (_PROMPT_INTRO) jika niche belum ada.
6. Buat 4 halaman statis (Tentang Kami, Kontak, Kebijakan Privasi, Disclaimer) via Blogger API untuk tiap blog baru.
7. Update niche-rotasi.json: pindahkan 10 niche ke "terpakai".
8. Verifikasi: cek 1-2 blog baru bisa diakses.

BATAS KEAMANAN: Jika Blogger menolak pembuatan blog (captcha berulang, pesan suspend, atau error rate-limit), BERHENTI dan laporkan — jangan paksakan. Keamanan akun lebih penting dari jumlah blog.

Laporan akhir (Bahasa Indonesia): daftar 10 blog baru + URL + status tema, atau alasan jika berhenti.
