---
id: pantau-loker-fb
title: Pantau loker FB pagi
enabled: true
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 08:11:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"ACA1AA031928F6887BDE7B0EBA953A3B","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Pantau loker Facebook pagi ini untuk M. Abdul Aziez (cari kerja operator pabrik/gudang, area Tangerang, tanpa ijazah / syarat ringan).

1. Jalankan: python3 ~/workspace/loker-yunobi/pantau_loker.py (output JSON daftar postingan <=26 jam terakhir yang mengandung kata kunci operator/produksi/pabrik/gudang/helper/packing).
2. Baca ~/workspace/loker-yunobi/sudah-dilaporkan.json (kalau belum ada, anggap daftar kosong) — hanya proses postingan yang URL-nya BELUM ada di daftar itu.
3. Dari postingan baru, pilih yang merupakan TAWARAN kerja asli dengan posisi: operator produksi/pabrik, staff/helper gudang, packing/packer — area Tangerang dan sekitarnya (Cadas, Sepatan, Mauk, Kotabumi, Cikupa, Jatiuwung, Karawaci, Periuk, Pasar Kemis, Balaraja).
   LEWATI: postingan orang yang cari kerja ("info loker dong"), khusus perempuan, ART/babysitter/salon/kurir/sales/MLM, dan postingan tanpa info perusahaan yang jelas.
   WASPADA SCAM: baca komentar postingan via `facebook-cli post comments read --post-id <id>` — kalau rame bahas ADM/biaya/pungli atau dibilang hoax, tandai sebagai PERINGATAN dan jangan sarankan melamar.
4. Untuk tiap postingan baru yang layak: tulis ringkasan singkat (posisi, perusahaan, lokasi, syarat ringkas, cara melamar: email/WA/walk-in) + link postingannya.
5. Update ~/workspace/loker-yunobi/sudah-dilaporkan.json: tambahkan semua URL yang diproses run ini (termasuk yang dilewati, supaya tidak dilaporkan ulang).
6. Sampaikan ke chat ini dalam Bahasa Indonesia, singkat: daftar loker baru yang cocok. Kalau tidak ada yang baru/cocok, cukup satu baris: pantauan pagi ini tidak menemukan loker baru yang cocok.
7. JANGAN mengirim email lamaran otomatis. Kalau ada yang sangat cocok dan cara lamarnya via email, siapkan draft emailnya dan minta persetujuan Yunobi dulu sebelum mengirim.
