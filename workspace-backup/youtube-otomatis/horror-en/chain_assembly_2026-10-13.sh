#!/bin/bash
# Rantai assembly horror-en 2026-10-13: tunggu rakit selesai -> sisip bumper -> potong shorts
WS=/home/hatch/workspace/youtube-otomatis/horror-en
LOG=$WS/chain-2026-10-13.log
echo "[chain] mulai $(date -Is)" >> "$LOG"
# 1. tunggu video final dari rakit (log OK) maks ~8 jam
for i in $(seq 1 480); do
  if grep -q "^OK:" $WS/rakit-2026-10-13.log 2>/dev/null && [ -s $WS/video/2026-10-13.mp4 ]; then break; fi
  if ! pgrep -f rakit_2026-10-13.py > /dev/null && ! grep -q "^OK:" $WS/rakit-2026-10-13.log 2>/dev/null; then
    echo "[chain] rakit mati tanpa OK, coba resume $(date -Is)" >> "$LOG"
    python3 $WS/rakit_2026-10-13.py >> $WS/rakit-2026-10-13.log 2>&1
  fi
  sleep 60
done
if [ ! -s $WS/video/2026-10-13.mp4 ]; then echo "[chain] GAGAL: video tidak jadi" >> "$LOG"; exit 1; fi
PRE=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $WS/video/2026-10-13.mp4)
echo "[chain] video jadi, durasi pre-bumper $PRE" >> "$LOG"
# 2. sisip bumper
python3 $WS/sisip_bumper_2026-10-13.py >> "$LOG" 2>&1 || { echo "[chain] GAGAL sisip bumper" >> "$LOG"; exit 1; }
POST=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $WS/video/2026-10-13.mp4)
echo "[chain] bumper tersisip (post $POST)" >> "$LOG"
# 3. potong shorts
python3 $WS/potong_shorts_2026-10-13.py >> "$LOG" 2>&1 || { echo "[chain] GAGAL potong shorts" >> "$LOG"; exit 1; }
# 4. thumbnail: teks "DO NOT PICK UP" di atas base image
BASE=$WS/media-generation-thumb-2026-10-13-base-0-f1d66cab-111c-48d9-b718-9376c90a7404.jpg
/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh -y -i "$BASE" \
  -vf "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='DO NOT PICK UP':fontsize=84:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=60" \
  -q:v 3 $WS/thumbnail-2026-10-13.jpg >> "$LOG" 2>&1
echo "[chain] thumbnail OK" >> "$LOG"
echo "[chain] selesai $(date -Is)" >> "$LOG"
ls -lh $WS/video/2026-10-13.mp4 $WS/shorts/2026-10-13-s*.mp4 $WS/thumbnail-2026-10-13.jpg >> "$LOG" 2>&1
