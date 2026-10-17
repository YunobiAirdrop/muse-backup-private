---
id: retry-artikel-bnn
title: Retry artikel BNN ke Blogspot
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-10-01T15:30:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  predicted_connector_permissions:
  - connector: gmail
    method: users.messages.send
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Kirim ulang SATU artikel yang gagal terbit ke blog KabarViral (terblokir rate-limit Blogger tadi siang).

Langkah:
1. `cd ~/workspace/blog-otomatis && ./venv/bin/python - <<'PYEOF'
import json
arts = json.load(open('data/artikel_terkirim.json'))
bnn = [a for a in arts if a['judul'].startswith('BNN Uji Kelayakan')]
json.dump(bnn, open('data/artikel.json', 'w'), ensure_ascii=False, indent=1)
print(len(bnn), 'artikel siap')
PYEOF`
2. `./venv/bin/python -u posting.py` — kirim ke Blogspot via Gmail.
3. Tunggu 5 menit, lalu verifikasi: `curl -sL 'https://kabarviralterkiniterbaru.blogspot.com/feeds/posts/default?max-results=10' | grep -o "BNN Uji Kelayakan"` — harus muncul di feed.
4. Cek juga tidak ada bounce baru: `hatch_gws_cli gmail +triage --query 'from:mailer-daemon@googlemail.com newer_than:1h' --max 5`.

Jika masih bounce/blocked: JANGAN retry lagi hari ini. Laporkan ke user bahwa Blogger rate-limit sedang ketat, artikel BNN dicoba lagi besok pagi bersama batch harian. Jangan edit MEMORY.md; observasi ke ~/memory/2026-10-01.md.

Laporan akhir ke user (Bahasa Indonesia, singkat): apakah artikel BNN akhirnya terbit atau masih kepental.
