#!/bin/bash
# Rakit FYP tebak-tebakan 2026-10-09 v2: grain dibake ke gambar dulu (cepat), lalu zoompan, lalu mux audio
set -e
FQ=~/workspace/youtube-otomatis/ffmpeg-queue.sh
OUT=~/workspace/tiktok-shop-affiliate/output
cd "$OUT"
IMG1=media-generation-fyp-img1-20261009-0-c3cd11d9-8fab-44e8-8d9d-cde2e7fa9a4b.webp
IMG2=media-generation-fyp-img2-20261009-0-f99ccd80-6877-4035-830c-b972ca270464.webp
IMG3=media-generation-fyp-img3-20261009-0-c2cc66db-cbd1-409d-b1e9-4b8758b082ba.webp

# Bake film grain halus ke tiap gambar (1 frame saja -> cepat)
$FQ -y -i "$IMG1" -vf "noise=alls=14:allf=t" n1.png
$FQ -y -i "$IMG2" -vf "noise=alls=14:allf=t" n2.png
$FQ -y -i "$IMG3" -vf "noise=alls=14:allf=t" n3.png

# Segmen zoompan (9/11/12 dtk, arah zoom bervariasi)
$FQ -y -loop 1 -i n1.png -vf "scale=2160:3840,zoompan=z='min(1+0.12*on/270,1.12)':d=270:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30" -t 9 -c:v libx264 -preset veryfast -pix_fmt yuv420p seg1.mp4
$FQ -y -loop 1 -i n2.png -vf "scale=2160:3840,zoompan=z='max(1.12-0.10*on/330,1.02)':d=330:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30" -t 11 -c:v libx264 -preset veryfast -pix_fmt yuv420p seg2.mp4
$FQ -y -loop 1 -i n3.png -vf "scale=2160:3840,zoompan=z='min(1+0.10*on/360,1.10)':d=360:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30" -t 12 -c:v libx264 -preset veryfast -pix_fmt yuv420p seg3.mp4

printf "file 'seg1.mp4'\nfile 'seg2.mp4'\nfile 'seg3.mp4'\n" > concat.txt
$FQ -y -f concat -safe 0 -i concat.txt -c copy concat-raw.mp4
# Final: mux voiceover (video copy -> cepat)
$FQ -y -i concat-raw.mp4 -i fyp-vo-20261009.mp3 -c:v copy -c:a aac -b:a 128k -shortest -movflags +faststart fyp-tebak-20261009.mp4
echo "SELESAI:"; ls -la fyp-tebak-20261009.mp4; ffprobe -v error -show_entries format=duration -of csv=p=0 fyp-tebak-20261009.mp4
