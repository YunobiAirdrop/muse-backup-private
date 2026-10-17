#!/bin/bash
# Prep aset demo Bimo: chromakey kendaraan + crop roda + layer lubang/tambalan
set -eu
Q=~/workspace/youtube-otomatis/ffmpeg-queue.sh
D=~/workspace/kendaraan-anak-demo
W=$D/work
KEY="colorkey=0xFE1991:0.22:0.05"


# --- chromakey kendaraan -> PNG transparan (canvas tetap 1920x1280) ---
$Q -y -v error -i "$D/img/bus.webp"       -vf "format=rgba,$KEY" "$W/bus_key.png"
$Q -y -v error -i "$D/img/excavator.webp" -vf "format=rgba,$KEY" "$W/excavator_key.png"
$Q -y -v error -i "$D/img/truck.webp"     -vf "hflip,format=rgba,$KEY" "$W/truck_key.png"
$Q -y -v error -i "$D/img/bulldozer.webp" -vf "format=rgba,$KEY" "$W/bulldozer_key.png"

# --- crop roda dari PNG keyed + mask lingkaran ---
# geq: paksa alpha jadi lingkaran penuh (di luar lingkaran = transparan)
MASK="format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(gt(hypot(X-W/2,Y-H/2),W/2-2),0,alpha(X,Y))'"
# roda bus: pusat belakang (605,1011) depan (1181,1011), crop 400x400
$Q -y -v error -i "$W/bus_key.png" -vf "crop=400:400:405:811,$MASK" "$W/bus_wr.png"
$Q -y -v error -i "$W/bus_key.png" -vf "crop=400:400:981:811,$MASK" "$W/bus_wf.png"
# roda truk (sesudah hflip): pusat belakang (547,960) depan (1344,960), crop 520x520
$Q -y -v error -i "$W/truck_key.png" -vf "crop=520:520:287:700,$MASK" "$W/truck_wr.png"
$Q -y -v error -i "$W/truck_key.png" -vf "crop=520:520:1084:700,$MASK" "$W/truck_wf.png"

# --- layer lubang jalan (elips pipih 2 lapis) + tambalan (aspal muda) ---
$Q -y -v error -f lavfi -i "color=c=black:s=300x90:d=1" -vf "format=rgba,geq=r='if(lt(pow((X-150)/148,2)+pow((Y-45)/43,2),0.45),12,58)':g='if(lt(pow((X-150)/148,2)+pow((Y-45)/43,2),0.45),12,58)':b='if(lt(pow((X-150)/148,2)+pow((Y-45)/43,2),0.45),12,58)':a='if(lt(pow((X-150)/148,2)+pow((Y-45)/43,2),1),255,0)'" -frames:v 1 "$W/pothole.png"
$Q -y -v error -f lavfi -i "color=c=0x8f8f8f:s=300x90:d=1" -vf "format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(lt(pow((X-150)/148,2)+pow((Y-45)/43,2),1),255,0)'" -frames:v 1 "$W/patch.png"

# --- frame uji komposit: bus di atas jalan (cek keying) ---
$Q -y -v error -i "$D/img/bg.webp" -i "$W/bus_key.png" -filter_complex \
 "[0:v]scale=2987:1280,crop=720:1280:900:0[bg];[1:v]scale=470:-1[bus];[bg][bus]overlay=130:951" \
 -frames:v 1 "$W/test_key.jpg"
ls -la "$W"/*.png "$W/test_key.jpg"
