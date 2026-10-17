#!/bin/bash
# Rakit demo miniatur pompa air: 8 gambar x 7 detik Ken Burns -> 56 detik
set -e
cd ~/workspace/miniatur-ai
Q=~/workspace/youtube-otomatis/ffmpeg-queue.sh
D=210
Y='ih/2-(ih/zoom/2)'
XC='iw/2-(iw/zoom/2)'

kb() { # $1=scene letter, $2=mode
  local img=$(ls media-generation-scene-$1-0-*.jpg | head -1)
  local z x
  case "$2" in
    zin)  z="min(1+0.15*on/$D,1.15)"; x="$XC" ;;
    zout) z="max(1.15-0.15*on/$D,1.0)"; x="$XC" ;;
    panr) z="1.15"; x="(iw-iw/zoom)*on/$D" ;;
    panl) z="1.15"; x="(iw-iw/zoom)*(1-on/$D)" ;;
  esac
  echo "== segmen $1 ($2): $img"
  $Q -y -loop 1 -i "$img" \
    -vf "scale=1600:900:force_original_aspect_ratio=increase,crop=1600:900,zoompan=z='$z':d=$D:x='$x':y='$Y':s=1280x720:fps=30" \
    -t 7 -c:v libx264 -preset veryfast -pix_fmt yuv420p "seg-$1.mp4"
}

kb a zin
kb b panr
kb c zout
kb d zin
kb e panl
kb f zin
kb g zout
kb h zin

printf "file 'seg-%s.mp4'\n" a b c d e f g h > concat.txt
echo "== concat"
$Q -y -f concat -safe 0 -i concat.txt -c copy concat.mp4

echo "== mux audio + faststart"
$Q -y -i concat.mp4 -i voiceover.mp3 \
  -c:v copy -c:a aac -b:a 128k -map 0:v:0 -map 1:a:0 \
  -movflags +faststart -t 56 demo-mini-pompa-air.mp4

echo "== verifikasi"
ffprobe -v error -show_entries stream=width,height,codec_name,codec_type -show_entries format=duration,size -of default=noprint_wrappers=1 demo-mini-pompa-air.mp4
echo "SELESAI: demo-mini-pompa-air.mp4"
