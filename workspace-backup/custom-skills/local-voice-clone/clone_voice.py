#!/home/hatch/workspace/.venv-stt/bin/python
"""Voice cloning gratis via HuggingFace Spaces (XTTS-v2).

Satu perintah untuk generate suara clone dari sampel referensi.
Otomatis fallback ke Space cadangan kalau yang utama gagal.

Contoh:
  clone_voice.py --text "Halo, saya Yunobi." --out bumper.wav
  clone_voice.py --text "Hi, I'm Yunobi." --ref /path/suara.wav --lang English --out en.wav
  clone_voice.py --text "..." --ref https://example.com/suara.mp3 --out out.wav

Butuh: venv /home/hatch/workspace/.venv-stt (gradio_client), ffmpeg.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request

# Hapus no_proxy/NO_PROXY: nilai bawaan runtime mengandung IPv6 bracket
# ([::1]) yang merusak parsing URL di httpx lama dalam gradio_client.
for _v in ("no_proxy", "NO_PROXY"):
    os.environ.pop(_v, None)

from gradio_client import Client  # noqa: E402

# (space_id, api_name) — urutan = prioritas. Hanya yang pertama terverifikasi
# bekerja (2026-10-11); sisanya placeholder untuk ditambah setelah diverifikasi.
SPACES = [
    ("hasanbasbunar/voice-cloning-xtts-v2", "/voice_clone_synthesis"),
]

# Sampel suara default: suara asli owner (hasil denoise), persisten di workspace.
DEFAULT_REF = os.path.expanduser(
    "~/workspace/youtube-otomatis/dola-intro/suara-bersih-test.mp3"
)

BASE_HOST = "https://hasanbasbunar-voice-cloning-xtts-v2.hf.space"


def to_wav_24k(src_path):
    """Konversi referensi ke WAV 24kHz mono — format yang diterima space.
    (MP3 langsung DITOLAK ffmpeg di space: decoding failed.)"""
    dst = os.path.join(tempfile.gettempdir(), "vc_ref_24k.wav")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", src_path, "-ar", "24000", "-ac", "1", dst],
        check=True,
        timeout=120,
    )
    return dst


def fetch_url(url):
    dst = os.path.join(tempfile.gettempdir(), "vc_ref_dl")
    urllib.request.urlretrieve(url, dst)
    return dst


def upload_to_space(space_host, local_path):
    """Upload file ke /gradio_api/upload space; kembalikan file_url publik."""
    out = subprocess.run(
        ["curl", "-s", "--max-time", "120", "-F",
         f"files=@{local_path};type=audio/wav",
         f"{space_host}/gradio_api/upload"],
        capture_output=True, text=True, timeout=150,
    )
    paths = json.loads(out.stdout)
    return f"{space_host}/gradio_api/file={paths[0]}"


def host_of(space_id):
    return f"https://{space_id.replace('/', '-')}.hf.space"


def clone_once(space_id, api_name, text, ref_url, language):
    client = Client(space_id)
    return client.predict(
        text=text,
        reference_audio_url=ref_url,
        example_audio_name=None,  # WAJIB None kalau pakai reference_audio_url
        language=language,
        api_name=api_name,
    )


def main():
    ap = argparse.ArgumentParser(description="Voice cloning gratis via HF Spaces")
    ap.add_argument("--text", required=True, help="Teks yang diucapkan")
    ap.add_argument("--out", required=True, help="File output (.wav)")
    ap.add_argument("--ref", default=DEFAULT_REF,
                    help="Sampel suara: path lokal atau URL (default: suara owner)")
    ap.add_argument("--lang", default="English",
                    help="Bahasa (catatan: 'English' terbukti jalan untuk teks Indonesia)")
    args = ap.parse_args()

    # 1. Siapkan referensi lokal (download dulu kalau URL — URL langsung
    #    sering gagal di-decode di sisi server).
    ref = args.ref
    if ref.startswith(("http://", "https://")):
        print("Mengunduh sampel referensi ...", flush=True)
        ref = fetch_url(ref)
    if not os.path.isfile(ref):
        sys.exit(f"Referensi tidak ditemukan: {args.ref}")
    wav = to_wav_24k(ref)
    print(f"Referensi siap: {wav}", flush=True)

    # 2. Coba tiap space sampai berhasil.
    last_err = None
    for space_id, api_name in SPACES:
        host = host_of(space_id)
        try:
            print(f"Upload ke {space_id} ...", flush=True)
            file_url = upload_to_space(host, wav)
            print(f"Generate via {api_name} ...", flush=True)
            result = clone_once(space_id, api_name, args.text, file_url, args.lang)
            if result and os.path.isfile(result):
                shutil.copy(result, args.out)
                print(f"OK -> {args.out}")
                return 0
            last_err = f"hasil kosong dari {space_id}"
        except Exception as e:  # noqa: BLE001 — lanjut ke cadangan
            last_err = f"{space_id}: {type(e).__name__}: {str(e)[:200]}"
            print(f"Gagal: {last_err}", flush=True)
    sys.exit(f"Semua space gagal. Terakhir: {last_err}")


if __name__ == "__main__":
    main()
