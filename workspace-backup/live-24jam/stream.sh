#!/bin/bash
# 24/7 livestream loop untuk channel Yunobi Bercerita (@ceritarakyat862)
# Streaming via RTMP ke YouTube, playlist di-loop tanpa henti.
# Dijalankan via systemd service yunobi-live.service (auto-restart).
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$DIR/stream.log"

# Ambil stream key dari secure storage (600 perms)
# shellcheck disable=SC1090
source "$HOME/.hermes/youtube-stream-keys.env"

RTMP_URL="${YUNOBI_BERCERITA_RTMP}/${YUNOBI_BERCERITA_KEY}"

echo "[$(date '+%F %T')] Starting 24/7 stream..." >> "$LOG"

exec "$HOME/workspace/youtube-otomatis/ffmpeg-queue.sh" \
  -re -f concat -safe 0 -stream_loop -1 -i "$DIR/playlist.txt" \
  -map 0:v:0 -map 0:a:0 \
  -c:v libx264 -preset veryfast -tune zerolatency \
  -b:v 2500k -maxrate 2500k -bufsize 5000k \
  -vf "scale=1280:720,fps=30" -g 60 \
  -c:a aac -b:a 128k -ar 44100 -ac 2 \
  -f flv "$RTMP_URL" >> "$LOG" 2>&1
