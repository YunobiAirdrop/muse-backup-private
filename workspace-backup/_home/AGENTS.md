# AGENTS.md

Your operating manual for this workspace, written by you. Your main instructions cover how you work in general. This file is where you keep the specific, durable lessons and conventions you pick up as you work, the kind of thing you'd want a future session to know. It's not about the user (that goes in `USER.md` and your memory) or your personality (that's `SOUL.md`); it's about how you get work done here.

## Conventions
- **channels.yaml: JANGAN ada key duplikat** (2026-10-15): YAML pakai value TERAKHIR untuk key duplikat — file pernah punya `channel_id` 4x per channel dengan yang terakhir `""`, bikin semua channel_id kebaca kosong dan dashboard nampilin "error" (channel_info fallback ke /search yang flaky). Selalu tulis SATU channel_id per channel; verifikasi via `channels.list(mine=true)` per token.
Add an entry whenever you work something out worth keeping, for example:
- a convention you've settled on ("keep data exports in `workspace/exports/` and clean them up monthly")
- a tool or site quirk worth remembering ("site X hides its form behind a cookie banner; dismiss it first")
- a workflow that worked, or a mistake not to repeat

It starts empty and is meant to grow slowly. Don't pad it; a short, accurate file beats a long, stale one.

## Blog pipeline — share scripts need artikel-{blog}.json
share_ig.py reads `artikel-{blog}.json` from the pipeline ROOT (not data/); video_script.py and thread_gen.py glob `data/artikel-*.json` (excluding *terkirim*/*pending*). Neither jalan.sh nor tulis_ulang.py produces these — without them all share scripts silently find 0 articles. Before any evening share run, aggregate the day's rewritten batch files (cp-*.json, sh-*.json, tk-*.json, mini-*.json) into artikel-{blog}.json in BOTH locations, skipping failed rewrites (judul "...") and test posts.
## Model reasoning leak in video_script/thread_gen output
nemotron reasoning models dump "Here's a thinking process" into the output file. Regenerate affected sections with non-reasoning models first (gemma-4-26b, qwen3.8-27b, ling-3.0-flash, gemma-4-31b), a system prompt forbidding internal monologue, and validation that rejects outputs containing "thinking process" or X/Y placeholders.
## IG/FB/Threads writes need user approval even on cron runs
instagram-cli post-feed (and facebook-cli/threads-cli writes) trigger runtime user-approval on detached runs and stall forever (pending_user_confirmation). Treat as "menunggu persetujuan", never bypass; use --dry-run to list the queued titles for the report.
## Video assembly OOM (2026-10-05)
rakit_video.py (scale 1600x900 + zoompan 30fps) gets SIGKILLed ~2/3 through a 75-segment build on this 8GB/2CPU VM. For long builds use the lighter pipeline (scale=1280:720 direct, -preset veryfast) — see youtube-otomatis/history-en/resume_rakit.py which also resumes from existing _tmp_segs/sNNN.mp4 segments instead of starting over.
## Render concurrency limit — ffmpeg-queue.sh (2026-10-06)
VM only has 7.7GB RAM; 11 channels rendering at once risks OOM kills. ALL video scripts must call ffmpeg via `~/workspace/youtube-otomatis/ffmpeg-queue.sh` instead of bare `ffmpeg` (17 scripts patched 2026-10-06: all of youtube-otomatis + video-weirdworld + blog-otomatis/video_gen.py). The wrapper is a transparent semaphore (atomic mkdir, max 2 concurrent, stale-slot cleanup via PID liveness check) — queued renders wait automatically, no user approval involved. New video scripts: use the wrapper path, never bare "ffmpeg".
## drawtext '%' = teks hilang (2026-10-11)
ffmpeg drawtext di VM ini me-render teks yang mengandung '%' (bahkan '%%') sebagai KOSONG total — hanya warning "Stray %" lalu overlay tidak muncul sama sekali. Jangan pakai '%' di teks drawtext; tulis "PERSEN" atau kalimat ulang tanpa persen. (Ditemukan saat hook "73% POSISI MASIH KOSONG!" hilang dari video loker TikTok.)
## drawtext apostrof + enable between = filtergraph rusak (2026-10-13)
Apostrof (') di dalam teks drawtext dikombinasi `enable='between(t,0,3)'` merusak filtergraph ("No such filter: '0'") — filter gagal total. Buang apostrof dari teks drawtext (hook_esc), atau hindari pola enable between dengan teks berapostrof. (Ditemukan saat hook shorts horror-en s1.)
## ffmpeg-queue stale slot — bersihkan manual (2026-10-11)
Stale-slot cleanup wrapper TIDAK selalu jalan: slot di /tmp/ffmpeg-slots/slotN bisa macet dipegang PID yang sudah mati (kasus: slot1 dipegang PID 19762 yang mati, render horor-otomatis nunggu 40+ menit dengan CPU 0%). Kalau render macet (CPU 0%, segmen tidak bertambah): cek `for s in /tmp/ffmpeg-slots/slot*; do echo "$s: $(cat $s/pid)"; done` lalu `ps -p <PID>` — kalau PID mati, `rm -rf /tmp/ffmpeg-slots/slotN` (aman, setara cleanup otomatis wrapper). Jangan edit wrapper saat render berjalan.
## Pexels Cloudflare-blocked dari VM — pakai Wikimedia Commons (2026-10-12)
Unduh klip Pexels dari VM ini kena blokir Cloudflare (penyebab produksi Jejak Islami sempat beralih ke Mixkit Restricted — yang dilarang user). Jalur yang lolos: API pencarian Wikimedia Commons via curl (respons JSON normal) + host upload.wikimedia.org. Lisensi dicek PER FILE (hanya CC0/PD/CC BY/CC BY-SA; tolak NC/ND), klip CC BY/SA wajib blok atribusi di deskripsi video. Format .ogv/.webm ditranscode pipeline seperti biasa. Strange Tales sudah memakai jalur ini.
## Verifikasi frame Pexels SEBELUM assembly — channel rohani (2026-10-08)
Search Pexels keyword "church"/"bible" mengembalikan KUIL HINDU/BUDDHA (Bali, Vietnam, dsb) — browser task tidak sadar konteks agama. Untuk channel rohani (Kisah Alkitab dkk): WAJIB ekstrak 1 frame per klip dan LIHAT manual sebelum assembly; klip rumah ibadah agama lain = buang, jangan dipakai. Keyword aman: alam/gurun/langit/lilin saja. Aturan anti-macet mengizinkan 1 klip dipakai 2x (urutan beda) bila klip bersih kurang dari 18.

## Penamaan file media.generate_video via subagent (2026-10-08)
Tool menambah prefix "media-generation-" sendiri ke param `name` dan memotong nama panjang: name="media-generation-seg1-gamis-karina" jadi file "media-generation-media-generation-seg1-gamis-ka-<uuid>.mp4". Pola glob rakit (`media-generation-{seg}-{slug}-*.mp4`) jadi tidak cocok. Sesudah generate: salin/normalisasi ke pola yang diharapkan, dan saat dua slug berawalan sama (gamis-karina vs gamis-kayla) verifikasi pemetaan via session jsonl subagent (`/home/hatch/agents/agent-<id>/sessions/`) — jangan tebak dari mtime.
## Resume posting promo yang ter-SIGTERM (2026-10-08)
posting_promo_YYYYMMDD.py retry SEMUA slot non-TERPOSTING saat dijalankan ulang (by design) — kalau run mati di tengah (SIGTERM/service restart), jangan jalankan ulang mentah-mentah (duplikat entri + buang waktu). Pakai skrip _lanjutan khusus hanya untuk slot yang belum pernah dicoba, lalu dedupe report per (produk, akun).
## Anti "full-AI look" untuk monetisasi (2026-10-07, permintaan user; DIPERKUAT 2026-10-10)
Konten AI berisiko ditolak monetisasi YouTube kalau dinilai mass-produced/tanpa sentuhan manusia (kebijakan "inauthentic content" 15 Juli 2025). Riset komunitas kreator 2026-10-10 menegaskan: YouTube TIDAK melarang channel AI — yang ditolak = template tanpa jejak keputusan manusia.
- Visual: tambah film grain halus (ffmpeg noise filter) + variasi durasi shot, jangan semua klip exactly 10 dtk dan terlalu "sempurna". Warna natural, hindari look plastik-AI.
- Audio: SFX rekaman ASLI (bukan sintesis), disinkronkan ke gambar; tiap sumber suara yang kelihatan harus terdengar.
- Struktur manusiawi: title card pembuka, chapter/beat cerita orisinal tiap video (jangan template berulang), pacing variatif.
- Metadata: deskripsi ditulis bergaya personal + atribusi SFX CC BY; AI disclosure WAJIB dicentang saat upload.
- Diterapkan di tahap assembly (post-production), bukan saat generate klip.
- PLAYBOOK LENGKAP: ~/workspace/youtube-otomatis/human-touch-playbook.md — 7 jurus wajib (naskah opini-first, host persona tetap per 19 channel, rotasi 3 format/channel, read-aloud test, riset disebut sumbernya, visual scene-by-scene beda, pre-application audit + appeal asset). Dibaca 19 cron tiap produksi mulai 2026-10-11.
## Browser upload YouTube — verifikasi channel via ID, bukan nama (2026-10-11)
Browser task upload ke Studio pernah nyasar ke channel lain (UC1c8WpKGhFKpUOp5AqVueEg bukan @LimaMisteri) karena cuma cek nama channel. Instruksi browser task HARUS mencantumkan Channel ID eksplisit + kewajiban verifikasi URL Studio mengandung ID itu sebelum Create → Upload. Sesudah spawn, peek_task 1x untuk memastikan channel benar; kalau salah, steer_task dengan koreksi channel ID.
## JANGAN `python script.py --help` untuk cek usage (2026-10-13)
Skrip upload/lama (mis. yt-growth/upload_video.py) TIDAK punya argparse — `--help` diabaikan dan `main()` langsung jalan. Kasus nyata: cek `--help` malah mengupload video 60MB ke channel empires-en (jadi PUBLIC karena publishAt basi) — harus dihapus manual via API (videos.delete, 204). Mau cek usage: baca source-nya (head), JANGAN dieksekusi.

## ffmpeg concat playlist — pakai ABSOLUTE path (2026-10-11)
Kasus inktime: alist.txt berisi relative path ("file '../audio/beat-01.mp3'") me-resolve ke direktori playlist (video/tmp/ -> video/audio/ yang tidak ada) — hasilnya afull.mp3 cuma 2,5 dtk (hanya silence.mp3 yang memang ada di tmp/) DENGAN exit code 0, tanpa error. Video final 444 dtk ke-mux dengan audio 2,5 dtk + -shortest -> file 3 dtk, nyaris lolos tanpa sadar. Skema relative yang SAMA kemarin (rakit_536.py) berhasil — jadi jangan andalkan. SELALU tulis absolute path di playlist concat. Verifikasi afull/vconcat (ffprobe durasi) SEBELUM final mux.

## Render script — slides dari TIMELINE audio, bukan durasi speech (2026-10-15)
Render pertama space-en GAGAL assert: video 539 dtk vs audio 563 dtk — slides dihitung dari `beat_durs` (speech-only) sehingga jeda antar-beat + bumper tidak tercakup. Hitung durasi slide dari gap timeline audio: `slide_k = starts[k+1] - starts[k]` (pakai timestamp mulai tiap beat dari hasil concat/gabung audio). Selalu assert |durasi video − durasi audio| kecil SEBELUM final.

## Render script — JANGAN timpa video final tanpa backup + cek durasi (2026-10-14)
Kasus space-en: build 2026-10-13 menimpa video/2026-10-11.mp4 (457 dtk, terverifikasi QC) dengan file TERPOTONG 81 dtk tanpa error — skrip tidak cek durasi output, tidak ada backup. Aturan baru: SEMUA skrip rakit WAJIB tulis ke file TEMP dulu, verifikasi durasi (assert |durasi-expected| < 5 dtk) via ffprobe, BARU pindahkan (shutil.move) ke path final. Gagal verifikasi = file final TIDAK ditimpa, temp disimpan untuk diagnosa.

## drawtext ':' (colon) di teks = filtergraph rusak (2026-10-14)
Colon di dalam `text='...'` drawtext DIPARSE sebagai pemisah opsi filter meski di dalam quote — error "No option name near '...'" lalu "Error opening output files: Invalid argument". Escape colon jadi `\:` (contoh: `text='HARVARD\: COULD IT BE ALIEN TECH'`). Ditemukan saat build Oumuamua space-en gagal 2x.

## subtitles force_style — MarginV BUKAN piksel, warna &H bikin hilang (2026-10-14)
Burn-in subtitle via filter `subtitles=...:force_style='...'` di ffmpeg 8.1.2 VM ini: (1) `MarginV` memakai koordinat play-res SRT (384x288), BUKAN piksel — MarginV=320 melempar teks keluar layar; pakai MarginV=45 (≈300px dari bawah di 1080x1920). (2) Kode warna `&H...` membuat subtitle hilang total — jangan pakai warna kustom, pakai default. Style final yang terbukti jalan: `FontName=DejaVu Sans,FontSize=22,BorderStyle=1,Outline=2,Alignment=2,MarginV=45`. (Ditemukan saat testing clipper-bot.)

## ffmpeg `-stream_loop -1` bisa hang ~30 menit (2026-10-15)
`-stream_loop -1` (loop tak terbatas) + `-t` sebagai opsi output pernah bikin ffmpeg SELESAI nulis file tapi proses tidak exit ~30 menit (CPU ~4%, file tidak bertambah, slot ffmpeg-queue macet). Pakai loop TERBATAS: hitung `loops = ceil(dur_target/dur_sumber)-1`, hanya bila sumber < target; kalau sumber >= target jangan pakai loop sama sekali. (Kasus: Jejak Islami p12, u19.mp4 24 dtk untuk slot 23 dtk.)

## komentar.py WAJIB pakai venv yt-growth (2026-10-14)
System python3 VM tidak punya `google-auth` — fetch komentar.py gagal total (ModuleNotFoundError) kalau dijalankan dengan python3 biasa. Selalu jalankan dengan `~/workspace/youtube-otomatis/yt-growth/venv/bin/python komentar.py fetch|post|seed malam`.

## OAuth picker — channel utama tampil sebagai nama akun Google (2026-10-15)
Di halaman pemilih channel OAuth Google, channel UTAMA/personal akun tampil dengan NAMA AKUN GOOGLE (mis. "Akun Utama yunobi"), BUKAN nama channel YouTube-nya (kasus: @ceritarakyat862 tidak muncul di daftar — ternyata dia = item "Akun Utama yunobi"). Kalau channel yang dicari tidak ada di daftar brand, coba otorisasi item nama-akun itu lalu verifikasi via API `channels.list(mine=True)` channel apa yang terikat.

## Share-3x — fallback pending saat browser mati (2026-10-15)
scan_share3x.py otomatis menggabung `share3x-pending-*.json` dari goals/toolkit-pertumbuhan-youtube-yt-growth/hidden_files/ (dedupe vs log 24h). Kalau browser task gagal total, SIMPAN daftar video baru ke file pending di sana — JANGAN tulis videoId gagal ke share3x-log.json (bikin run besok skip mereka selamanya).

## Konversi still-image JANGAN via ffmpeg-queue (2026-10-17)
Konversi webp→jpg (PIL, 2 detik, RAM kecil) via ffmpeg-queue ikut antre di belakang render video channel lain (kasus: 4 worker truecrime-en macet 15 menit menunggu 2 slot yang dipegang render horror-en + space-en). Aturan "semua via ffmpeg-queue" tujuannya cegah OOM RENDER video — konversi still-image via PIL tidak melanggar semangatnya. Render video tetap WAJIB via wrapper.
## cek_duplikat.py gagal parse 2 format judul (2026-10-15)
Script judul_dari_instruksi() TIDAK membaca format "Judul (persis, ...):" (inktime shorts txt) dan "## JUDUL" markdown (kisah-islami md) — keluar {"error": "judul tidak ditemukan"} (exit 2). BUKAN tanda duplikat. Workaround pra-screen: ekstrak judul manual dari file instruksi, ulangi dengan `--judul`. Format yang lolos parse: "Judul: ..." (satu baris), "=== N. JUDUL ===", "Varian ... (DIPILIH):".
