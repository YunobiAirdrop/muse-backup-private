#!/bin/bash
# Prep truk kartun: chromakey (item03/06/07 di-hflip dulu) + crop roda item00/01/03/04
set -eu
Q=~/workspace/youtube-otomatis/ffmpeg-queue.sh
D=~/workspace/macam-macam/work/truk-kartun
I=$D/img; W=$D/work
mkdir -p "$W"
KEY="colorkey=0xFC00F8:0.18:0.04"

# --- chromakey -> PNG transparan (canvas = ukuran asli) ---
$Q -y -v error -i "$I/item00.webp" -vf "format=rgba,$KEY" "$W/item00_key.png"
$Q -y -v error -i "$I/item01.webp" -vf "format=rgba,$KEY" "$W/item01_key.png"
$Q -y -v error -i "$I/item02.webp" -vf "format=rgba,$KEY" "$W/item02_key.png"
$Q -y -v error -i "$I/item03.webp" -vf "hflip,format=rgba,$KEY" "$W/item03_key.png"
$Q -y -v error -i "$I/item04.webp" -vf "format=rgba,$KEY" "$W/item04_key.png"
$Q -y -v error -i "$I/item05.webp" -vf "format=rgba,$KEY" "$W/item05_key.png"
$Q -y -v error -i "$I/item06.webp" -vf "hflip,format=rgba,$KEY" "$W/item06_key.png"
$Q -y -v error -i "$I/item07.webp" -vf "hflip,format=rgba,$KEY" "$W/item07_key.png"

# --- crop roda + mask lingkaran (geq: di luar lingkaran alpha=0) ---
MASK="format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(gt(hypot(X-W/2,Y-H/2),W/2-2),0,alpha(X,Y))'"
# item00 (1920x1280): R(528,1011) F(1200,1011) crop 300
$Q -y -v error -i "$W/item00_key.png" -vf "crop=300:300:378:861,$MASK" "$W/item00_wr.png"
$Q -y -v error -i "$W/item00_key.png" -vf "crop=300:300:1050:861,$MASK" "$W/item00_wf.png"
# item01: R1(317,1011) R2(624,1011) F(1411,1011) crop 330
$Q -y -v error -i "$W/item01_key.png" -vf "crop=330:330:152:846,$MASK" "$W/item01_wr1.png"
$Q -y -v error -i "$W/item01_key.png" -vf "crop=330:330:459:846,$MASK" "$W/item01_wr2.png"
$Q -y -v error -i "$W/item01_key.png" -vf "crop=330:330:1246:846,$MASK" "$W/item01_wf.png"
# item03 (sesudah hflip): F(1446,966) R1(937,966) R2(643,966) crop 245
$Q -y -v error -i "$W/item03_key.png" -vf "crop=245:245:1323:844,$MASK" "$W/item03_wf.png"
$Q -y -v error -i "$W/item03_key.png" -vf "crop=245:245:814:844,$MASK" "$W/item03_wr1.png"
$Q -y -v error -i "$W/item03_key.png" -vf "crop=245:245:520:844,$MASK" "$W/item03_wr2.png"
# item04: R1(413,922) R2(682,922) F(1392,922) crop 280
$Q -y -v error -i "$W/item04_key.png" -vf "crop=280:280:273:782,$MASK" "$W/item04_wr1.png"
$Q -y -v error -i "$W/item04_key.png" -vf "crop=280:280:542:782,$MASK" "$W/item04_wr2.png"
$Q -y -v error -i "$W/item04_key.png" -vf "crop=280:280:1252:782,$MASK" "$W/item04_wf.png"

# --- frame uji: item00 + roda di atas bg (skala tampil 920) ---
$Q -y -v error -i "$I/bg.webp" -i "$W/item00_key.png" -i "$W/item00_wr.png" -i "$W/item00_wf.png" -filter_complex "
[0:v]scale=5760:1920,crop=1080:1920:600:0[bg];
[1:v]scale=920:613[trk];
[2:v]scale=144:144[wr];
[3:v]scale=144:144[wf];
[bg][trk]overlay=80:1007[v1];
[v1][wr]overlay=261:1419[v2];
[v2][wf]overlay=583:1419" -frames:v 1 "$W/test_item00.jpg"

# --- frame uji: item01 + 3 roda ---
$Q -y -v error -i "$I/bg.webp" -i "$W/item01_key.png" -i "$W/item01_wr1.png" -i "$W/item01_wr2.png" -i "$W/item01_wf.png" -filter_complex "
[0:v]scale=5760:1920,crop=1080:1920:1200:0[bg];
[1:v]scale=920:613[trk];
[2:v]scale=158:158[wr1];
[3:v]scale=158:158[wr2];
[4:v]scale=158:158[wf];
[bg][trk]overlay=80:999[v1];
[v1][wr1]overlay=153:1405[v2];
[v2][wr2]overlay=300:1405[v3];
[v3][wf]overlay=677:1405" -frames:v 1 "$W/test_item01.jpg"

ls -la "$W"
