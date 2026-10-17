#!/bin/bash
# Render 6 adegan demo Bimo (keyframe ffmpeg) + gabung + mix audio
set -eu
Q=~/workspace/youtube-otomatis/ffmpeg-queue.sh
D=~/workspace/kendaraan-anak-demo
W=$D/work; A=$D/audio
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
ENC="-c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -r 30"

# ---------- S0: LAGU — Bimo menyetir, background scroll ----------
$Q -y -v error -framerate 30 -loop 1 -t 11 -i "$D/img/bg.webp" -framerate 30 -loop 1 -t 11 -i "$W/bus_key.png" -framerate 30 -loop 1 -t 11 -i "$W/bus_wr.png" -framerate 30 -loop 1 -t 11 -i "$W/bus_wf.png" -filter_complex "
[0:v]scale=2987:1280,crop=720:1280:x='min(2150,6*n)':y=0[bg];
[1:v]scale=470:313[bus];
[2:v]scale=98:98,rotate=a='-4*t':c=none:ow=iw:oh=ih[wr];
[3:v]scale=98:98,rotate=a='-4*t':c=none:ow=iw:oh=ih[wf];
[bg][bus]overlay=x='130-610*exp(-1.1*t)':y='950+5*sin(13.8*t)'[v1];
[v1][wr]overlay=x='130-610*exp(-1.1*t)+99':y='950+5*sin(13.8*t)+199'[v2];
[v2][wf]overlay=x='130-610*exp(-1.1*t)+240':y='950+5*sin(13.8*t)+199'[v3];
[v3]drawtext=fontfile=$FONT:text='BIMO & ALAT BERAT':fontsize=70:fontcolor=yellow:borderw=6:bordercolor=black:x=(w-text_w)/2:y=105,
drawtext=fontfile=$FONT:text='Belajar Warna':fontsize=52:fontcolor=white:borderw=5:bordercolor=black:x=(w-text_w)/2:y=195,
drawtext=fontfile=$FONT:text='HIJAU':fontsize=92:fontcolor=0x37d93a:borderw=7:bordercolor=black:x=(w-text_w)/2:y=330:enable='between(t,0.5,3.4)'[out]" -map "[out]" -t 11 $ENC "$W/seg0.mp4"

# ---------- S1: HOOK — Bimo berhenti di depan lubang ----------
$Q -y -v error -framerate 30 -loop 1 -t 5.2 -i "$D/img/bg.webp" -framerate 30 -loop 1 -t 5.2 -i "$W/pothole.png" -framerate 30 -loop 1 -t 5.2 -i "$W/bus_key.png" -framerate 30 -loop 1 -t 5.2 -i "$W/bus_wr.png" -framerate 30 -loop 1 -t 5.2 -i "$W/bus_wf.png" -filter_complex "
[0:v]scale=2987:1280,crop=720:1280:900:0[bg];
[bg][1:v]overlay=400:1180[v0];
[2:v]scale=470:313[bus];
[3:v]scale=98:98,rotate=a='-4*min(t,1.9)':c=none:ow=iw:oh=ih[wr];
[4:v]scale=98:98,rotate=a='-4*min(t,1.9)':c=none:ow=iw:oh=ih[wf];
[v0][bus]overlay=x='40-520*exp(-1.6*t)':y='950+5*sin(13.8*min(t,1.9))'[v1];
[v1][wr]overlay=x='40-520*exp(-1.6*t)+99':y='950+5*sin(13.8*min(t,1.9))+199'[v2];
[v2][wf]overlay=x='40-520*exp(-1.6*t)+240':y='950+5*sin(13.8*min(t,1.9))+199'[v3];
[v3]drawtext=fontfile=$FONT:text='JALANNYA RUSAK!':fontsize=74:fontcolor=0xff3333:borderw=6:bordercolor=black:x=(w-text_w)/2:y=170:enable='between(t,0.4,5.2)'[out]" -map "[out]" -t 5.2 $ENC "$W/seg1.mp4"

# ---------- S2: EXCAVATOR kuning menggali ----------
$Q -y -v error -framerate 30 -loop 1 -t 4.7 -i "$D/img/bg.webp" -framerate 30 -loop 1 -t 4.7 -i "$W/pothole.png" -framerate 30 -loop 1 -t 4.7 -i "$W/excavator_key.png" -filter_complex "
[0:v]scale=2987:1280,crop=720:1280:300:0[bg];
[bg][1:v]overlay=430:1180[v0];
[2:v]scale=500:333[eks];
[v0][eks]overlay=x='170+560*exp(-1.5*t)+4*sin(20*t)*between(t,1.2,4.2)':y='920+8*sin(8.8*t)*between(t,1.2,4.2)+3*sin(13.8*t)*lt(t,1.2)'[v1];
[v1]drawtext=fontfile=$FONT:text='KUNING':fontsize=96:fontcolor=0xffd21a:borderw=7:bordercolor=black:x=(w-text_w)/2:y=170:enable='between(t,0.8,4.7)'[out]" -map "[out]" -t 4.7 $ENC "$W/seg2.mp4"

# ---------- S3: TRUK merah membawa pasir ----------
$Q -y -v error -framerate 30 -loop 1 -t 4.5 -i "$D/img/bg.webp" -framerate 30 -loop 1 -t 4.5 -i "$W/pothole.png" -framerate 30 -loop 1 -t 4.5 -i "$W/truck_key.png" -framerate 30 -loop 1 -t 4.5 -i "$W/truck_wr.png" -framerate 30 -loop 1 -t 4.5 -i "$W/truck_wf.png" -filter_complex "
[0:v]scale=2987:1280,crop=720:1280:1500:0[bg];
[bg][1:v]overlay=90:1180[v0];
[2:v]scale=500:333[trk];
[3:v]scale=135:135,rotate=a='-4*min(t,1.8)':c=none:ow=iw:oh=ih[wr];
[4:v]scale=135:135,rotate=a='-4*min(t,1.8)':c=none:ow=iw:oh=ih[wf];
[v0][trk]overlay=x='70-580*exp(-1.5*t)':y='927+4*sin(13.8*min(t,1.8))+if(gt(t,2.3),-16*exp(-1.8*(t-2.3))*sin(5*(t-2.3)),0)'[v1];
[v1][wr]overlay=x='70-580*exp(-1.5*t)+75':y='927+4*sin(13.8*min(t,1.8))+183'[v2];
[v2][wf]overlay=x='70-580*exp(-1.5*t)+283':y='927+4*sin(13.8*min(t,1.8))+183'[v3];
[v3]drawtext=fontfile=$FONT:text='MERAH':fontsize=96:fontcolor=0xff4040:borderw=7:bordercolor=black:x=(w-text_w)/2:y=170:enable='between(t,0.8,4.5)'[out]" -map "[out]" -t 4.5 $ENC "$W/seg3.mp4"

# ---------- S4: BULLDOZER biru meratakan (lubang memudar -> tambalan) ----------
$Q -y -v error -framerate 30 -loop 1 -t 5 -i "$D/img/bg.webp" -framerate 30 -loop 1 -t 5 -i "$W/pothole.png" -framerate 30 -loop 1 -t 5 -i "$W/patch.png" -framerate 30 -loop 1 -t 5 -i "$W/bulldozer_key.png" -filter_complex "
[0:v]scale=2987:1280,crop=720:1280:600:0[bg];
[1:v]fade=t=out:st=2.2:d=1.2:alpha=1[ph];
[2:v]fade=t=in:st=2.6:d=1.0:alpha=1[pt];
[bg][ph]overlay=430:1180[v0];
[v0][pt]overlay=430:1180[v1];
[3:v]scale=520:347[doz];
[v1][doz]overlay=x='-540+198*t':y='922+2*sin(13.8*t)'[v2];
[v2]drawtext=fontfile=$FONT:text='BIRU':fontsize=96:fontcolor=0x3a9bff:borderw=7:bordercolor=black:x=(w-text_w)/2:y=170:enable='between(t,0.8,5.0)'[out]" -map "[out]" -t 5 $ENC "$W/seg4.mp4"

# ---------- S5: FINALE — semua berjajar + reprise + CTA ----------
$Q -y -v error -framerate 30 -loop 1 -t 14.5 -i "$D/img/bg.webp" -framerate 30 -loop 1 -t 14.5 -i "$W/patch.png" -framerate 30 -loop 1 -t 14.5 -i "$W/excavator_key.png" -framerate 30 -loop 1 -t 14.5 -i "$W/truck_key.png" -framerate 30 -loop 1 -t 14.5 -i "$W/bus_key.png" -framerate 30 -loop 1 -t 14.5 -i "$W/bulldozer_key.png" -filter_complex "
[0:v]scale=2987:1280,crop=720:1280:1900:0[bg];
[bg][1:v]overlay=210:1190[v0];
[2:v]scale=300:200[eks];
[3:v]scale=310:207[trk];
[4:v]scale=320:213[bus];
[5:v]scale=330:220[doz];
[v0][eks]overlay=x='15-340*exp(-2.2*t)':y='905+3*sin(9*t)'[v1];
[v1][trk]overlay=x='395+360*exp(-2.2*t)':y='905+3*sin(9*t+1.5)'[v2];
[v2][bus]overlay=x='25-380*exp(-2.2*max(t-0.15,0))':y='1035+3*sin(9*t+3)'[v3];
[v3][doz]overlay=x='370+390*exp(-2.2*max(t-0.15,0))':y='1030+3*sin(9*t+4.5)'[v4];
[v4]drawtext=fontfile=$FONT:text='HORE! JALANNYA BAGUS!':fontsize=62:fontcolor=yellow:borderw=6:bordercolor=black:x=(w-text_w)/2:y=120:enable='between(t,0.3,5.6)',
drawtext=fontfile=$FONT:text='TERIMA KASIH!':fontsize=84:fontcolor=white:borderw=6:bordercolor=black:x=(w-text_w)/2:y=110:enable='between(t,5.8,9.2)',
drawtext=fontfile=$FONT:text='JANGAN LUPA':fontsize=68:fontcolor=white:borderw=6:bordercolor=black:x=(w-text_w)/2:y=105:enable='between(t,9.6,14.5)',
drawtext=fontfile=$FONT:text='SUBSCRIBE!':fontsize=88:fontcolor=0xff4040:borderw=7:bordercolor=black:x=(w-text_w)/2:y=190:enable='between(t,9.6,14.5)'[out]" -map "[out]" -t 14.5 $ENC "$W/seg5.mp4"

# ---------- gabung video ----------
printf "file '%s'\n" "$W/seg0.mp4" "$W/seg1.mp4" "$W/seg2.mp4" "$W/seg3.mp4" "$W/seg4.mp4" "$W/seg5.mp4" > "$W/concat.txt"
$Q -y -v error -f concat -safe 0 -i "$W/concat.txt" -c copy "$W/video_bisu.mp4"

# ---------- mix audio: musik + chant + narasi ----------
$Q -y -v error -stream_loop -1 -i "$W/musik.wav" \
 -i "$A/lagu1.mp3" -i "$A/lagu2.mp3" -i "$A/lagu3.mp3" -i "$A/lagu4.mp3" \
 -i "$A/hook.mp3" -i "$A/eks.mp3" -i "$A/truk.mp3" -i "$A/buldo.mp3" \
 -i "$A/hore.mp3" -i "$A/lagu1.mp3" -i "$A/pamit.mp3" -i "$A/cta.mp3" -filter_complex "
[0:a]atrim=0:44.9,volume='if(lt(t,11),0.30,if(lt(t,30.4),0.13,0.26))':eval=frame[mus];
[1:a]adelay=300|300[v1];[2:a]adelay=3100|3100[v2];[3:a]adelay=6200|6200[v3];[4:a]adelay=8500|8500[v4];
[5:a]adelay=11200|11200[v5];[6:a]adelay=16400|16400[v6];[7:a]adelay=21100|21100[v7];[8:a]adelay=25600|25600[v8];
[9:a]adelay=30600|30600[v9];[10:a]adelay=36400|36400[v10];[11:a]adelay=39300|39300[v11];[12:a]adelay=41900|41900[v12];
[mus][v1][v2][v3][v4][v5][v6][v7][v8][v9][v10][v11][v12]amix=inputs=13:normalize=0,alimiter=limit=0.95[aout]" \
 -map "[aout]" -t 44.9 -c:a aac -b:a 160k "$W/audio_mix.m4a"

# ---------- mux final ----------
$Q -y -v error -i "$W/video_bisu.mp4" -i "$W/audio_mix.m4a" -c:v copy -c:a copy -shortest "$D/demo-keyframe-2026-10-12.mp4"
ffprobe -v error -show_entries format=duration -show_entries stream=codec_type,codec_name,width,height -of default=noprint_wrappers=1 "$D/demo-keyframe-2026-10-12.mp4"
