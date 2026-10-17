#!/bin/bash
# Generate semua clip TTS demo Bimo (Mudiwa, id) + catat durasi
set -u
A=~/workspace/kendaraan-anak-demo/audio
TTS=/opt/hatch/bin/tts
V=avocado_v2:mudiwa

gen() { # nama speed teks
  "$TTS" speak --voice "$V" --language id --speed "$2" --output "$A/$1.mp3" --text "$3" >/dev/null 2>&1 \
    && echo "$1 OK" || echo "$1 GAGAL"
}

gen lagu1 112 'Bimo! Bimo! Bus kecil hijau!'
gen lagu2 112 'Bimo! Bimo! Selalu ceria!'
gen lagu3 112 'Ayo bekerja bersama alat berat!'
gen lagu4 112 'Bantu teman, hati gembira!'
gen hook  105 'Wah, jalannya rusak! Siapa yang bisa membantu?'
gen eks   105 'Aku excavator kuning! Aku menggali tanah!'
gen truk  105 'Aku truk merah! Aku membawa pasir!'
gen buldo 105 'Aku bulldozer biru! Aku meratakan jalan!'
gen hore  105 'Hore! Jalannya sudah bagus! Terima kasih, teman-teman!'
gen pamit 108 'Sampai jumpa lagi, teman-teman!'
gen cta   105 'Jangan lupa subscribe ya, teman-teman!'

echo "--- durasi ---" > "$A/durations.txt"
for f in "$A"/*.mp3; do
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  echo "$(basename "$f") $d" >> "$A/durations.txt"
done
cat "$A/durations.txt"
