#!/bin/bash
# Chunk multi-input untuk sisa segmen Jejak Islami 2026-10-15 (Ashabul Kahfi).
# Alasan: antrean ffmpeg-queue macet parah (19 channel render bareng, 16:11).
# 4 job multi-input (= 4x antre) menggantikan 11 job satuan (= 11x antre).
# Sudah ada (valid 23 dtk): p01-p09, p12, p13. Sisa: p10,p11,p14,p15,p16,p17,p18,p19,p20,p21,p22.
set -e
W=/home/hatch/workspace/kisah-islami/work/2026-10-14
WB=/home/hatch/workspace/kisah-islami/work/2026-10-11/pexels
FF=/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh
cd "$W"
mkdir -p segs

VF="scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=25,eq=contrast=1.05:saturation=0.95,noise=alls=7:allf=t,format=yuv420p,trim=0:23,setpts=PTS-STARTPTS"

chunk() { # name total_dur ; sisa arg = input options + file, dipisah '|'
  local name="$1" total="$2"; shift 2
  local out="$W/segs/$name.mp4"
  if [ -s "$out" ]; then echo "SKIP $name"; return; fi
  local n=0 fc="" inputs=()
  for spec in "$@"; do
    local opts="${spec%%|*}"; local file="${spec#*|}"
    # shellcheck disable=SC2086
    inputs+=($opts -i "$file")
    fc="${fc}[$n:v]$VF[s$n];"
    n=$((n+1))
  done
  local concat_in=""
  for i in $(seq 0 $((n-1))); do concat_in="${concat_in}[s$i]"; done
  fc="${fc}${concat_in}concat=n=$n:v=1:a=0[v]"
  # shellcheck disable=SC2086
  $FF -hide_banner -loglevel error "${inputs[@]}" \
    -filter_complex "$fc" -map "[v]" -t "$total" \
    -c:v libx264 -preset veryfast -crf 20 -an -y "$out"
  echo "OK $name ($total s)"
}

# chunkA = p10(u16) + p11(u09 loop1) = 46 dtk
chunk chunkA 46 \
  "|$WB/u16.mp4" \
  "-stream_loop 1|$WB/u09.mp4"

# chunkB = p14(u20) + p15(u10 ss=4) = 46 dtk
chunk chunkB 46 \
  "|$WB/u20.mp4" \
  "-ss 4|$WB/u10.mp4"

# chunkC = p16(u09 loop1) + p17(u12 loop1) + p18(u13) + p19(u16 ss=1) = 92 dtk
chunk chunkC 92 \
  "-stream_loop 1|$WB/u09.mp4" \
  "-stream_loop 1|$WB/u12.mp4" \
  "|$WB/u13.mp4" \
  "-ss 1|$WB/u16.mp4"

# chunkD = p20(u07 ss=1) + p21(u04 loop3) + p22(u19 ss=1) = 69 dtk
chunk chunkD 69 \
  "-ss 1|$WB/u07.mp4" \
  "-stream_loop 3|$WB/u04.mp4" \
  "-ss 1|$WB/u19.mp4"

echo "--- verifikasi chunk ---"
for c in chunkA chunkB chunkC chunkD; do
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$W/segs/$c.mp4")
  echo "$c: ${d}s"
done
echo "--- CHUNK SELESAI ---"
