---
id: blog-otomatis-harian
title: Berita otomatis harian multi-blog
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 09:11:00
timeout_secs: 36000
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC6289CBB87DE8347E4C5B807A581209","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Jalankan pipeline blog otomatis harian MULTI-BLOG (10 blog: KabarViral, TEKNO PEDIA, info kesehatan hari ini, ekonomi bisnis info, Gaya Hidup Kekinian, olahraga terbaru, WisataIndo, KulinerNusantara, OtomotifInfo, PendidikanCerdas).

VOLUME HEMAT KUOTA (aturan user 2026-10-04): 1 artikel per blog per hari, KECUALI KabarViral 4 artikel/hari. Total 13 artikel/hari. Evergreen & digest DINONAKTIFKAN sementara.

Perintah: `cd ~/workspace/blog-otomatis && ./jalan.sh` — script otomatis: fetch semua blog → trending.py → per blog: tulis_ulang.py (1 artikel berita; KabarViral 4) → baca_juga.py → posting_web.py (siapkan artikel + tulis instruksi lengkap ke data/webpost/instruksi-{blog}.txt).

PENTING — POSTING VIA WEB UI (API Blogger diblokir Google sejak 2026-10-03, Mail-to-Blogger tidak diproses):
posting_web.py TIDAK memposting langsung. Ia mencetak "SPAWN_BROWSER_TASK:{blog}:{n}" per blog dan menulis instruksi lengkap (artikel + HTML embedded) ke data/webpost/instruksi-{blog}.txt.
Setelah jalan.sh selesai, untuk SETIAP blog yang punya instruksi:
1. Baca data/webpost/instruksi-{blog}.txt
2. Spawn 1 browser task dengan isi file tersebut sebagai task (posting via blogger.com web UI, login khususstokyunobi@gmail.com)
3. Spawn maksimal 2 browser task paralel
4. Tunggu semua selesai; untuk artikel yang TERPOSTING: pindahkan data/artikel-{blog}.json → data/artikel_terkirim-{blog}.json

Estimasi: ~13 artikel × 2-10 menit = 1-2 jam total. Jika satu blog/artikel gagal, lanjut ke berikutnya.

Catatan:
- Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md
- Model gratis error (429/503): catat, jangan spam retry (budget 24 percobaan/artikel + backoff 20s sudah di tulis_ulang.py)
- Semua akun pakai khususstokyunobi@gmail.com

Laporan akhir (Bahasa Indonesia, singkat): per blog berapa artikel terposting + judulnya, atau alasan jika tidak ada.
