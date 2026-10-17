#!/bin/bash
# Rantai assembly horror-en 2026-10-12: tunggu rakit selesai -> sisip bumper -> ukur bumper -> potong shorts -> status
WS=/home/hatch/workspace/youtube-otomatis/horror-en
LOG=$WS/chain-2026-10-12.log
echo "[chain] mulai $(date -Is)" >> "$LOG"
# 1. tunggu video final dari rakit (log OK) maks ~6 jam
for i in $(seq 1 360); do
  if grep -q "^OK:" $WS/rakit-2026-10-12.log 2>/dev/null && [ -s $WS/video/2026-10-12.mp4 ]; then break; fi
  if ! pgrep -f rakit_2026-10-12.py > /dev/null && ! grep -q "^OK:" $WS/rakit-2026-10-12.log 2>/dev/null; then
    echo "[chain] rakit mati tanpa OK, coba resume $(date -Is)" >> "$LOG"
    python3 $WS/rakit_2026-10-12.py >> $WS/rakit-2026-10-12.log 2>&1
  fi
  sleep 60
done
if [ ! -s $WS/video/2026-10-12.mp4 ]; then echo "[chain] GAGAL: video tidak jadi" >> "$LOG"; exit 1; fi
PRE=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $WS/video/2026-10-12.mp4)
echo "[chain] video jadi, durasi pre-bumper $PRE" >> "$LOG"
# 2. sisip bumper
python3 $WS/sisip_bumper_2026-10-12.py >> "$LOG" 2>&1
POST=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $WS/video/2026-10-12.mp4)
BD=$(python3 -c "print(f'{$POST - $PRE:.2f}')")
echo "[chain] bumper aktual $BD dtk (post $POST)" >> "$LOG"
sed -i "s/^BUMPER_D = .*/BUMPER_D = $BD     # terukur dari sisip bumper/" $WS/potong_shorts_2026-10-12.py
# 3. potong shorts
python3 $WS/potong_shorts_2026-10-12.py >> "$LOG" 2>&1
echo "[chain] selesai $(date -Is)" >> "$LOG"
ls -lh $WS/video/2026-10-12.mp4 $WS/shorts/2026-10-12-s*.mp4 >> "$LOG" 2>&1
