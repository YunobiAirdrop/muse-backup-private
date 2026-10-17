#!/bin/bash
# Tunnel cloudflared untuk YT Dashboard.
# Menulis URL publik ke AKSES.txt setiap (re)start (URL quick tunnel berubah tiap restart).
set -u
ROOT="/home/hatch/workspace/yt-dashboard"
AKSES="$ROOT/AKSES.txt"
PORT=8765

# tunggu backend siap
for i in $(seq 1 30); do
  curl -s -o /dev/null "http://127.0.0.1:$PORT/api/has_password" && break
  sleep 2
done

log() { echo "[$(date '+%F %T')] $*" >> "$ROOT/tunnel.log"; }

# jalankan cloudflared, parse URL dari output
/usr/local/bin/cloudflared tunnel --no-autoupdate --url "http://127.0.0.1:$PORT" 2>&1 \
| stdbuf -oL grep -o 'https://[a-zA-Z0-9.-]*\.trycloudflare\.com' \
| grep -v 'api\.trycloudflare\.com' | while read -r url; do
    log "tunnel up: $url"
    cat > "$AKSES" <<EOF
YT DASHBOARD — AKSES
====================
URL (berlaku selama tunnel ini hidup): $url
Diperbarui: $(date '+%Y-%m-%d %H:%M:%S %Z')

CARA PAKAI:
1. Buka URL di atas di Chrome Android.
2. Saat pertama dibuka: buat password (min. 4 karakter) — cukup sekali,
   password tersimpan aman (hash) di server.
3. Install ke home screen: Chrome > menu ⋮ > "Add to Home screen"
   (atau "Install app") — jadi ikon kayak aplikasi asli.

CATATAN:
- URL di atas BERUBAH setiap tunnel restart. File ini selalu ditulis ulang
  otomatis oleh service tunnel, jadi cek file ini untuk URL terbaru.
- Jangan sebar URL ke orang lain (yang pegang URL + password = akses penuh
  ke 19 channel YouTube: lihat statistik + publish video).
- Backend: http://127.0.0.1:8765 (hanya dari VM ini).
EOF
    chmod 600 "$AKSES"
  done
