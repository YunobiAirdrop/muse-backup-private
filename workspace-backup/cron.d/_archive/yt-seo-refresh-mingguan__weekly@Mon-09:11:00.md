---
id: yt-seo-refresh-mingguan
title: Refresh SEO mingguan YouTube (17 channel)
enabled: true
mode: task
schedule:
  kind: weekly
  timezone: Asia/Jakarta
  time: 09:11:00
  dow: [Mon]
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC2179E68A7BE30CED8DC2CE39E0A3B3","conversation_id":"whatsapp_channel","provider":"whatsapp","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
YT-SEO REFRESH MINGGUAN (toolkit yt-growth gratis — analitik asli + refresh metadata).

TUJUAN: menaikkan CTR video lama yang underperform via refresh judul/deskripsi/tag berbasis data, bukan tebakan.

LANGKAH:
1. Cek token: `~/workspace/youtube-otomatis/yt-growth/.venv/bin/python ~/workspace/youtube-otomatis/yt-growth/auth.py status`. Jika 0 token → laporkan "setup OAuth yt-growth belum selesai" dan BERHENTI.
2. Untuk tiap channel yang punya token: `~/workspace/youtube-otomatis/yt-growth/.venv/bin/python ~/workspace/youtube-otomatis/yt-growth/analytics.py SLUG --days 28` → simpan JSON ke `~/workspace/youtube-otomatis/yt-growth/hidden_files/analytics-YYYY-MM-DD/{slug}.json` (buat foldernya).
3. Dari data: temukan video umur >90 hari dengan CTR di bawah median channel-nya (abaikan video <1000 impresi).
4. Untuk tiap kandidat (maks 5/channel): tulis proposal metadata baru memakai `~/workspace/youtube-otomatis/packaging-formulas.md` (pilih 1 formula judul, buat 3-5 varian, pakai terkuat; 150 karakter pertama deskripsi = hook + keyword utama). PROTEKSI: jangan hapus keyword/frasa yang sudah memberi traffic; judul tetap jujur (janjinya ditepati 30 detik pertama video).
5. Tulis proposal ke `~/workspace/youtube-otomatis/yt-growth/proposals/proposal-YYYY-MM-DD.md` (per channel: video ID + URL, judul lama → judul baru + alasan).
6. LAPORKAN ke user: ringkasan per channel + proposalnya. Minta persetujuan.
7. HANYA setelah user setuju (ketukan/pesan eksplisit), eksekusi via `~/workspace/youtube-otomatis/yt-growth/.venv/bin/python ~/workspace/youtube-otomatis/yt-growth/yt_push.py SLUG --video ID --title "..." --description "..." --tags "a,b,c" --apply`. Tanpa persetujuan: JANGAN push.
8. Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md.
