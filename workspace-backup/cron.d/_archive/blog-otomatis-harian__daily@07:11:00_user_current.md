---
id: blog-otomatis-harian
title: Berita otomatis harian KabarViral
enabled: true
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 07:11:00
timeout_secs: 7200
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  predicted_connector_permissions:
  - connector: gmail
    method: users.messages.send
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC0BA2446C02D36469D73ACF395D064D","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Jalankan pipeline berita otomatis harian untuk blog KabarViral (https://kabarviralterkiniterbaru.blogspot.com/).

Langkah-langkah (WAJIB berurutan, berhenti jika ada langkah gagal):
1. `cd ~/workspace/blog-otomatis && ./venv/bin/python -u fetch_berita.py` — ambil 5 berita terbaru dari RSS (CNN Indonesia, Okezone, SindoNews, JPNN, Republika). Cek output: harus ada berita baru yang diambil (dedup via data/seen.json).
2. `./venv/bin/python -u tulis_ulang.py` — tulis ulang tiap berita jadi artikel orisinal + SEO via 9Router (model gratis yunobi/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free). LANGKAH INI LAMBAT: tiap artikel bisa 2-10 menit, total bisa 30-60 menit. Jangan dibatalkan, tunggu sampai selesai. Jika satu artikel gagal setelah retry, lanjutkan ke artikel berikutnya (jangan gagalkan seluruh run).
3. `./venv/bin/python -u posting.py` — kirim artikel jadi ke Blogspot via Gmail ke alamat rahasia di config.json. Cek output "TERPOSTING".

Catatan penting:
- Jangan edit MEMORY.md; observasi run tulis ke ~/memory/YYYY-MM-DD.md (daily log).
- Jika 9Router/model gratis sedang error (429/402), catat di laporan dan JANGAN spam retry — laporkan saja.
- Jika tidak ada berita baru (semua sudah di seen.json), itu normal — laporkan "tidak ada berita baru hari ini".
- Jangan membuat file laporan per-run di workspace; cukup sampaikan hasil akhir lewat pesan.

Laporan akhir ke user (Bahasa Indonesia, singkat): berapa artikel berhasil terposting hari ini + judul-judulnya, atau alasan jika tidak ada yang terposting.
