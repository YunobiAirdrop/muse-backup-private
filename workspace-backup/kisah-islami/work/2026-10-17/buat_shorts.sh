#!/bin/bash
# Potong 3 SHORTS vertikal 1080x1920 dari LONG Ibrahim 2026-10-17
set -e
W=/home/hatch/workspace/kisah-islami/work/2026-10-17
FF=/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh
LONG="$W/jejak-islami-2026-10-17-long.mp4"
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
mkdir -p "$W/shorts"

mkshort() { # name start dur hooktext
  local name="$1" start="$2" dur="$3" hook="$4"
  local out="$W/shorts/$name.mp4"
  if [ -s "$out" ]; then echo "SKIP $name"; return; fi
  local endct=$((dur - 3))
  $FF -hide_banner -loglevel error -ss "$start" -i "$LONG" -t "$dur" \
    -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920,fps=30,noise=alls=6:allf=t,format=yuv420p,drawtext=fontfile=$FONT:text='$hook':fontsize=58:fontcolor=#FFD700:borderw=3:bordercolor=black@0.9:x=(w-text_w)/2:y=140:enable='between(t,0,4)',drawtext=fontfile=$FONT:text='SUBSCRIBE!':fontsize=64:fontcolor=white:borderw=3:bordercolor=black@0.9:x=(w-text_w)/2:y=h-260:enable='between(t,$endct,$dur)'" \
    -c:v libx264 -preset veryfast -crf 23 -c:a aac -b:a 128k -movflags +faststart -y "$out"
  echo "OK $name"
}

[ -s "$LONG" ] || { echo "LONG belum ada"; exit 1; }
mkshort s1 193 45 "DILEMPAR KE API RAKSASA"
mkshort s2 111 45 "BERHALA DIHANCURKAN DENGAN KAPAK"
mkshort s3 31 45 "NEGERI YANG MENYEMBAH BERHALA"
echo "SELESAI"
