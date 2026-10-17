#!/bin/bash
# Single-pass assembly weird-en 2026-10-10 (pengganti 72-segmen, hemat slot antrean)
set -e
cd ~/workspace/youtube-otomatis/weird-en
Q=~/workspace/youtube-otomatis/ffmpeg-queue.sh
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf

# 1. daftar audio
> /tmp/audiolist_b10.txt
for i in $(seq 1 72); do printf "file '%s/workspace/youtube-otomatis/weird-en/audio/b10-beat-%03d.mp3'\n" "$HOME" "$i" >> /tmp/audiolist_b10.txt; done
$Q -y -f concat -safe 0 -i /tmp/audiolist_b10.txt -c:a libmp3lame -b:a 128k audio/b10-gabungan.mp3

# 2. daftar gambar + durasi per beat
python3 - <<'EOF'
import json
d=json.load(open('data/durasi-beat-2026-10-10.json'))
with open('/tmp/imglist_b10.txt','w') as f:
    for i in range(1,73):
        k=f'b10-beat-{i:03d}'
        f.write(f"file '{__import__('os').environ['HOME']}/workspace/youtube-otomatis/weird-en/gambar/{k}.webp'\n")
        f.write(f"duration {d[k]}\n")
    f.write(f"file '{__import__('os').environ['HOME']}/workspace/youtube-otomatis/weird-en/gambar/b10-beat-072.webp'\n")
print("imglist ok")
EOF

# 3. single-pass render: slideshow + drawtext overlay + grain
VF="scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=black"
add_dt() { # text start end fontsize yoff
  local t="$1" s="$2" e="$3" fs="$4" yo="$5"
  t=$(echo "$t" | sed "s/:/\\\\:/g")
  VF="$VF,drawtext=fontfile=$FONT:text='$t':fontsize=$fs:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2$yo:enable='between(t,$s,$e)'"
}
add_dt "YOUR BODY IS LYING TO YOU" 2 10 64 -40
add_dt "WAIT, WHAT?!" 99 107 72 -40
add_dt "TO THE SUN... AND BACK. 200X." 437 445 56 -40
add_dt "SUBSCRIBE!" 300 303 72 -40
add_dt "THE WINNER: YOUR BRAIN" 569 577 64 -40
VF="$VF,noise=alls=6:allf=t,format=yuv420p"

$Q -y -f concat -safe 0 -i /tmp/imglist_b10.txt -i audio/b10-gabungan.mp3 \
  -vf "$VF" -c:v libx264 -preset veryfast -crf 21 -c:a aac -b:a 128k \
  -shortest -movflags +faststart video/2026-10-10-final.mp4

echo "=== HASIL ==="
ls -la video/2026-10-10-final.mp4
ffprobe -v error -show_entries format=duration -show_entries stream=codec_name,width,height -of default=noprint_wrappers=1 video/2026-10-10-final.mp4
