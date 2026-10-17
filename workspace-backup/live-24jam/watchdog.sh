#!/bin/bash
# Watchdog stream 24/7 Yunobi Bercerita.
# Dipanggil cron tiap 15 menit. Jika proses ffmpeg RTMP tidak jalan, start ulang.
# Stream key diambil dari secure storage, tidak pernah ditulis ke log.
set -uo pipefail

DIR="/home/hatch/workspace/live-24jam"
PLAYLIST="$DIR/playlist.txt"
LOG="$DIR/stream.log"
PIDFILE="$DIR/stream.pid"

is_running() {
  # Cek ffmpeg yang sedang push ke RTMP YouTube untuk live ini
  pgrep -f "ffmpeg.*rtmp://a.rtmp.youtube.com/live2" > /dev/null 2>&1
}

if is_running; then
  exit 0
fi

echo "[$(date '+%F %T')] Watchdog: stream mati, restart..." >> "$LOG"

# shellcheck disable=SC1090
source "$HOME/.hermes/youtube-stream-keys.env"
RTMP_URL="${YUNOBI_BERCERITA_RTMP}/${YUNOBI_BERCERITA_KEY}"

# Start detached agar survive setelah cron selesai
setsid nohup "$HOME/workspace/youtube-otomatis/ffmpeg-queue.sh" \
  -re -f concat -safe 0 -stream_loop -1 -i "$PLAYLIST" \
  -map 0:v:0 -map 0:a:0 \
  -c:v libx264 -preset veryfast -tune zerolatency \
  -b:v 2500k -maxrate 2500k -bufsize 5000k \
  -vf "scale=1280:720,fps=30" -g 60 \
  -c:a aac -b:a 128k -ar 44100 -ac 2 \
  -f flv "$RTMP_URL" >> "$LOG" 2>&1 < /dev/null &
echo $! > "$PIDFILE"
echo "[$(date '+%F %T')] Watchdog: stream di-start (PID $(cat $PIDFILE))" >> "$LOG"
