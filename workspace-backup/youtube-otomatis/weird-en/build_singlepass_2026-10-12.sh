#!/bin/bash
set -e
cd ~/workspace/youtube-otomatis/weird-en
Q=~/workspace/youtube-otomatis/ffmpeg-queue.sh
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
VF="scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=black"
VF="$VF,drawtext=fontfile=$FONT:text='7 PLACES THAT LOOK FAKE':fontsize=64:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-40:enable='between(t,1.0,9.0)'"
VF="$VF,drawtext=fontfile=$FONT:text='A MIRROR THE SIZE OF A COUNTRY':fontsize=52:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-40:enable='between(t,0.0,4.0)'"
VF="$VF,drawtext=fontfile=$FONT:text='1 IN 3 PLANTS EXIST NOWHERE ELSE':fontsize=52:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-40:enable='between(t,89.8,93.8)'"
VF="$VF,drawtext=fontfile=$FONT:text='CRYSTALS AS LONG AS A BUS':fontsize=56:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-40:enable='between(t,270.1,274.1)'"
VF="$VF,drawtext=fontfile=$FONT:text='SUBSCRIBE!':fontsize=72:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-40:enable='between(t,277.6,280.6)'"
VF="$VF,drawtext=fontfile=$FONT:text='THE WORLDS LARGEST MIRROR':fontsize=56:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-40:enable='between(t,423.7,427.7)'"
VF="$VF,drawtext=fontfile=$FONT:text='280 LIGHTNING STRIKES AN HOUR':fontsize=52:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-40:enable='between(t,465.4,469.4)'"
VF="$VF,drawtext=fontfile=$FONT:text='STAY WEIRD!':fontsize=64:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-40:enable='between(t,564.3,567.3)'"
VF="$VF,noise=alls=6:allf=t,format=yuv420p"
$Q -y -c:v webp -f concat -safe 0 -i /tmp/imglist_b12.txt -i audio/gabungan-2026-10-12.mp3 -vf "$VF" -c:v libx264 -preset veryfast -crf 21 -c:a aac -b:a 128k -shortest -movflags +faststart video/2026-10-12-final.mp4
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height -of default=noprint_wrappers=1 video/2026-10-12-final.mp4
