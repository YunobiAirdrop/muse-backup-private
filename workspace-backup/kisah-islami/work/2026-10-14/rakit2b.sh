#!/bin/bash
# Rakit LONG Jejak Islami 2026-10-15 — Ashabul Kahfi (QS Al-Kahfi 18:9-26)
# Melanjutkan run 2026-10-14 yang macet di assembly (narasi + klip sudah siap).
# Klip: 1 baru terverifikasi (c01 gua, CC BY) + 13 bank Commons terverifikasi (uNN).
# n04 DITOLAK (turis berpakaian tidak sopan); n01/n02/n05/n06 DITOLAK (lisensi tak terlacak).
# Narasi: 486.456 dtk. 22 slot x 23 dtk = 506 dtk -> final di-shortest ke narasi.
set -e
W=/home/hatch/workspace/kisah-islami/work/2026-10-14
WB=/home/hatch/workspace/kisah-islami/work/2026-10-11/pexels
FF=/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh
cd "$W"
mkdir -p segs

FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
VF="scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=25,eq=contrast=1.05:saturation=0.95,noise=alls=7:allf=t,format=yuv420p"

build() { # slot src dur [ssoffset]
  # Loop TERBATAS (bukan -1): -stream_loop tak terbatas pernah bikin ffmpeg hang ~30 mnt
  # setelah output selesai (kasus p12, 2026-10-15). Loop hanya bila sumber < durasi target.
  local slot="$1" src="$2" dur="$3" sso="${4:-0}"
  if [ -s "$W/segs/p$slot.mp4" ]; then echo "SKIP p$slot"; return; fi
  if [ "$sso" != "0" ]; then
    $FF -hide_banner -loglevel error -ss "$sso" -i "$src" -t "$dur" -vf "$VF" \
      -c:v libx264 -preset veryfast -crf 20 -an -y "$W/segs/p$slot.mp4"
  else
    local srcdur loopopt=""
    srcdur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$src" 2>/dev/null || echo "$dur")
    local loops=$(python3 -c "import math; sd=max(float('$srcdur'),0.1); print(max(0, math.ceil($dur/sd)-1))" 2>/dev/null || echo 0)
    [ "$loops" -gt 0 ] && loopopt="-stream_loop $loops"
    $FF -hide_banner -loglevel error $loopopt -i "$src" -t "$dur" -vf "$VF" \
      -c:v libx264 -preset veryfast -crf 20 -an -y "$W/segs/p$slot.mp4"
  fi
  echo "OK p$slot ($dur s)"
}
build 12 $WB/u19.mp4 23
build 13 $WB/u05.mp4 23
build 14 $WB/u20.mp4 23
build 15 $WB/u10.mp4 23 4
build 16 $WB/u09.mp4 23
build 17 $WB/u12.mp4 23
build 18 $WB/u13.mp4 23
build 19 $WB/u16.mp4 23 1
build 20 $WB/u07.mp4 23 1
build 21 $WB/u04.mp4 23
build 22 $WB/u19.mp4 23 1
