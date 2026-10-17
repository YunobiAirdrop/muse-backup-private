#!/bin/bash
# Crop roda PRESISI dari PNG keyed: kotak rapat di pusat roda terukur + masker lingkaran
# seukuran ban (radius r+3) agar tidak ada potongan bodi ikut berputar.
set -eu
Q=~/workspace/youtube-otomatis/ffmpeg-queue.sh
W=~/workspace/macam-macam/work/truk-kartun/work

cropwheel () { # $1=key png  $2=out  $3=S  $4=ox  $5=oy  $6=R
  $Q -y -v error -i "$W/$1" -vf "crop=$3:$3:$4:$5,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(gt(hypot(X-W/2,Y-H/2),$6),0,alpha(X,Y))'" "$W/$2"
}

# item00: wr(585,1043,r150) wf(1326,1041,r152)
cropwheel item00_key.png item00_wr.png 310 430 888 153
cropwheel item00_key.png item00_wf.png 314 1169 884 155
# item01: wr1(363,1011,r150) wr2(680,1014,r147) wf(1514,1012,r149)
cropwheel item01_key.png item01_wr1.png 310 208 856 153
cropwheel item01_key.png item01_wr2.png 304 528 862 150
cropwheel item01_key.png item01_wf.png 308 1360 858 152
# item03: wf(1444,1017,r118) wr1(905,1016,r119) wr2(635,1016,r119)
cropwheel item03_key.png item03_wf.png 246 1321 894 121
cropwheel item03_key.png item03_wr1.png 248 781 892 122
cropwheel item03_key.png item03_wr2.png 248 511 892 122
# item04: wr1(414,963,r136) wr2(680,965,r134) wf(1410,958,r139)
cropwheel item04_key.png item04_wr1.png 282 273 822 139
cropwheel item04_key.png item04_wr2.png 278 541 826 137
cropwheel item04_key.png item04_wf.png 288 1266 814 142
ls -la "$W"/item0*_w*.png
