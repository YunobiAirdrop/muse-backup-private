---
id: blog-otomatis-harian
title: Berita otomatis harian multi-blog
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 15:11:00
timeout_secs: 36000
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Jalankan pipeline blog otomatis harian MULTI-BLOG (10 blog: KabarViral, TEKNO PEDIA, info kesehatan hari ini, ekonomi bisnis info, Gaya Hidup Kekinian, olahraga terbaru, WisataIndo, KulinerNusantara, OtomotifInfo, PendidikanCerdas).

VOLUME HEMAT KUOTA (aturan user 2026-10-05): 6 artikel/hari total (turun dari 13, menyesuaikan kuota gratis OpenRouter 50 req/hari). Sistem rotasi: KabarViral SELALU dapat 1 artikel (blog utama), 5 artikel lainnya rotasi ke 5 blog berbeda tiap hari dari 9 blog sisanya. Cek file rotasi-blog.txt di workspace untuk tahu giliran hari ini, update setelah run. Evergreen & digest TETAP NONAKTIF.

Perintah: `cd ~/workspace/blog-otomatis && ./jalan.sh` — script otomatis: fetch semua blog → trending.py → per blog terpilih: tulis_ulang.py (1 artikel berita) → baca_juga.py → posting_web.py (siapkan artikel + tulis instruksi lengkap ke data/webpost/instruksi-{blog}.txt).

PENTING — POSTING VIA WEB UI (API Blogger diblokir Google sejak 2026-10-03, Mail-to-Blogger tidak diproses):
posting_web.py TIDAK memposting langsung. Ia mencetak "SPAWN_BROWSER_TASK:{blog}:{n}" per blog dan menulis instruksi lengkap (artikel + HTML embedded) ke data/webpost/instruksi-{blog}.txt.
Setelah jalan.sh selesai, untuk SETIAP blog yang punya instruksi:
1. Baca data/webpost/instruksi-{blog}.txt
2. Spawn 1 browser task dengan isi file tersebut sebagai task (posting via blogger.com web UI, login khususstokyunobi@gmail.com)
3. Spawn maksimal 2 browser task paralel
4. Tunggu semua selesai; untuk artikel yang TERPOSTING: pindahkan data/artikel-{blog}.json → data/artikel_terkirim-{blog}.json

Estimasi: ~6 artikel × 2-10 menit = 30-60 menit total. Jika satu blog/artikel gagal, lanjut ke berikutnya.

Catatan:
- Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md
- Model gratis error (429/503): catat, jangan spam retry (budget 24 percobaan/artikel + backoff 20s sudah di tulis_ulang.py)
- Semua akun pakai khususstokyunobi@gmail.com

Laporan akhir (Bahasa Indonesia, singkat): per blog berapa artikel terposting + judulnya, atau alasan jika tidak ada.
