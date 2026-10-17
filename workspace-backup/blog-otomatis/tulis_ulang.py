#!/usr/bin/env python3
"""Tulis ulang berita antrean jadi artikel orisinal Bahasa Indonesia + SEO.
Memakai model gratis via 9Router. Output: data/artikel.json"""
import json, os, re, sys, time, argparse
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

def get_blog(nama):
    with open(os.path.join(BASE, "config.json")) as f:
        cfg = json.load(f)
    for b in cfg["blogs"]:
        if b["nama"] == nama:
            return b
    print("Blog tidak ada di config.json: " + nama)
    sys.exit(1)

_ap = argparse.ArgumentParser()
_ap.add_argument("--blog", default="kabarviral")
_blog = get_blog(_ap.parse_args().blog)
BLOG_NAMA = _blog["nama"]
NICHE = _blog.get("niche", "campuran")

ROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# langsung ke OpenRouter (bukan via 9Router) supaya tiap API key pakai kuota
# akunnya sendiri-sendiri. 9Router hanya kenal 1 key upstream.
def _load_proxy_env():
    try:
        with open("/etc/9router-proxy.env") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass
_load_proxy_env()
MODELS = [
    # 2026-10-04: reasoning model dinonaktifkan — nemotron reasoning pernah
    # membocorkan "Here's a thinking process" ke isi artikel (lihat AGENTS.md).
    # 2026-10-06: qwen3.8-27b:free DIHAPUS (404 — model dipensiunkan OpenRouter),
    # inkling:free DIHAPUS (403 Forbidden konsisten). Sisa 5 model.
    # 2026-10-08: gemma-4-26b dipindah ke depan — nemotron-3.5-lightning konsisten
    # return non-JSON dan menghabiskan budget 24 percobaan (2 blog gagal 8 Okt).
    # 2026-10-09: nemotron-3.5-lightning DIHAPUS — kembali return non-JSON dan
    # menghabiskan budget (kabarviral gagal 9 Okt). Sisa 4 model.
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "inclusionai/ling-3.0-flash-sante:free",
    "google/gemma-4-31b-it:free",
]

def get_api_keys():
    """Ambil semua OpenRouter key: OPENROUTER_KEYS (koma-pisah) atau fallback NINEROUTER_API_KEY."""
    env_path = os.path.expanduser("~/.hermes/.env")
    keys = []
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("OPENROUTER_KEYS="):
                keys = [k.strip().strip('"').strip("'") for k in line.split("=", 1)[1].split(",") if k.strip()]
            elif line.startswith("NINEROUTER_API_KEY=") and not keys:
                keys = [line.split("=", 1)[1].strip('"').strip("'")]
    if not keys:
        raise RuntimeError("Tidak ada API key ditemukan (OPENROUTER_KEYS / NINEROUTER_API_KEY)")
    return keys

def get_api_key():
    return get_api_keys()[0]

_PROMPT_INTRO = {
"keuangan": """Kamu jurnalis keuangan Indonesia yang menulis untuk blog finansial. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya santai tapi informatif seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang berguna bagi pembaca: tips investasi, perbandingan produk keuangan, penjelasan dampak bagi keuangan pribadi/bisnis, atau panduan praktis. Selipkan kata kunci bernilai komersial secara natural (contoh: investasi, saham, reksa dana, asuransi, KPR, kartu kredit, pinjaman, tabungan, deposito, teknologi finansial).""",
"teknologi": """Kamu jurnalis teknologi Indonesia yang menulis untuk blog tekno. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya santai tapi informatif seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang berguna bagi pembaca: review singkat, perbandingan gadget, tips memilih produk teknologi, penjelasan tren AI/digital, atau panduan praktis. Selipkan kata kunci bernilai komersial secara natural (contoh: smartphone, laptop, gadget, AI, aplikasi, software, internet, hosting, VPN).""",
"kesehatan": """Kamu jurnalis kesehatan Indonesia yang menulis untuk blog gaya hidup sehat. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya santai tapi informatif seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang berguna bagi pembaca: tips kesehatan praktis, penjelasan medis dengan bahasa awam, pola hidup sehat, nutrisi, atau olahraga. Selipkan kata kunci bernilai komersial secara natural (contoh: kesehatan, suplemen, vitamin, diet, olahraga, asuransi kesehatan, rumah sakit, obat).""",
"campuran": """Kamu jurnalis Indonesia yang menulis untuk blog berita campuran (keuangan, teknologi, dan umum). Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya santai tapi informatif seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Untuk berita keuangan/teknologi, fokus pada sudut yang berguna: tips investasi, perbandingan produk keuangan, dampak bagi keuangan pribadi/bisnis, atau panduan praktis — selipkan kata kunci bernilai komersial secara natural (investasi, saham, reksa dana, asuransi, KPR, kartu kredit, pinjaman, tabungan, deposito). Untuk berita umum, tulis dengan gaya jurnalistik yang menarik dan informatif.""",
"hiburan": """Kamu jurnalis hiburan Indonesia yang menulis untuk blog gaya hidup kekinian. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya santai, seru, dan kekinian seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang menarik bagi pembaca: kabar artis, tren viral, film/musik, tips gaya hidup, atau rekomendasi hiburan. Selipkan kata kunci populer secara natural (contoh: artis, viral, film, musik, drama korea, fashion, traveling, kuliner).""",
"olahraga": """Kamu jurnalis olahraga Indonesia yang menulis untuk blog berita olahraga. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya semangat dan informatif seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang menarik bagi pembaca: hasil pertandingan, profil atlet, analisis taktik, jadwal pertandingan, atau tips olahraga. Selipkan kata kunci populer secara natural (contoh: sepak bola, liga indonesia, timnas, motogp, bulutangkis, skor, transfer pemain).""",
"wisata": """Kamu penulis travel Indonesia yang menulis untuk blog wisata. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya santai dan inspiratif seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang berguna bagi pembaca: rekomendasi destinasi, tips traveling hemat, itinerary, kuliner khas daerah, atau info tiket/penginapan. Selipkan kata kunci populer secara natural (contoh: wisata, liburan, pantai, gunung, hotel, tiket pesawat, itinerary).""",
"kuliner": """Kamu food blogger Indonesia yang menulis untuk blog kuliner. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya santai dan menggugah selera seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang menarik bagi pembaca: review makanan, resep, rekomendasi tempat makan, kuliner viral, atau tips masak. Selipkan kata kunci populer secara natural (contoh: kuliner, resep, makanan viral, restoran, street food, masakan padang).""",
"otomotif": """Kamu jurnalis otomotif Indonesia yang menulis untuk blog otomotif. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya informatif dan antusias seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang berguna bagi pembaca: review kendaraan, perbandingan mobil/motor, tips perawatan, info harga, atau teknologi otomotif. Selipkan kata kunci populer secara natural (contoh: mobil, motor, harga mobil, review, modifikasi, servis, oli).""",
"pendidikan": """Kamu penulis pendidikan Indonesia yang menulis untuk blog edukasi. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya jelas dan memotivasi seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang berguna bagi pembaca: tips belajar, info beasiswa, panduan kuliah/sekolah, atau perkembangan dunia pendidikan. Selipkan kata kunci populer secara natural (contoh: beasiswa, kuliah, sekolah, SNBP, CPNS, tips belajar).""",

"properti": """Kamu jurnalis properti Indonesia yang menulis untuk blog properti. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya santai tapi informatif seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang berguna bagi pembaca: tips beli rumah pertama, info KPR, tren harga properti, panduan investasi tanah/kost, atau legalitas sertifikat. Selipkan kata kunci bernilai komersial secara natural (contoh: KPR, rumah subsidi, investasi properti, harga tanah, apartemen, sertifikat tanah, developer).""",
"parenting": """Kamu penulis parenting Indonesia yang menulis untuk blog keluarga. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya hangat dan bersahabat seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang berguna bagi pembaca: tips mengasuh anak, tumbuh kembang, pola asuh positif, pendidikan anak, atau kesehatan keluarga. Selipkan kata kunci populer secara natural (contoh: parenting, tumbuh kembang anak, MPASI, pola asuh, pendidikan anak, imunisasi).""",
"fashion": """Kamu fashion writer Indonesia yang menulis untuk blog fashion. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya kekinian dan seru seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang menarik bagi pembaca: tren fashion, mix and match outfit, rekomendasi brand lokal, tips belanja fashion, atau gaya hijab. Selipkan kata kunci populer secara natural (contoh: fashion, outfit, OOTD, tren fashion, brand lokal, hijab style, sneakers).""",
"gaming": """Kamu jurnalis game Indonesia yang menulis untuk blog gaming. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya santai dan seru seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang menarik bagi pembaca: review game, berita rilis, tips main, rekomendasi game mobile/PC, atau info esports. Selipkan kata kunci populer secara natural (contoh: game, mobile legend, free fire, game android, esports, rilis game, konsol).""",
"karier": """Kamu penulis karier Indonesia yang menulis untuk blog pengembangan diri profesional. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya jelas dan memotivasi seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang berguna bagi pembaca: tips lolos interview, info lowongan kerja, panduan CV, negosiasi gaji, atau pengembangan skill/freelance. Selipkan kata kunci populer secara natural (contoh: lowongan kerja, CPNS, interview kerja, CV, gaji, freelance, skill digital).""",
"kecantikan": """Kamu beauty writer Indonesia yang menulis untuk blog kecantikan. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya akrab dan informatif seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang berguna bagi pembaca: tips skincare, rekomendasi produk, tutorial makeup, perawatan kulit bermasalah, atau tren kecantikan. Selipkan kata kunci bernilai komersial secara natural (contoh: skincare, serum, sunscreen, makeup, glowing, jerawat, toner, moisturizer).""",
"hewan": """Kamu penulis hewan Indonesia yang menulis untuk blog pecinta hewan peliharaan. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya hangat dan bersahabat seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang berguna bagi pembaca: tips merawat hewan peliharaan, kesehatan hewan, panduan adopsi, rekomendasi pakan, atau fakta unik hewan. Selipkan kata kunci populer secara natural (contoh: kucing, anjing, hewan peliharaan, pakan kucing, vaksin hewan, adopsi).""",
"musik": """Kamu penulis musik Indonesia yang menulis untuk blog musik. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya seru dan kekinian seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang menarik bagi pembaca: lagu viral, review album, kabar musisi, jadwal konser, atau rekomendasi playlist. Selipkan kata kunci populer secara natural (contoh: musik, lagu viral, konser, playlist, musisi indonesia, album, lirik lagu).""",
"film": """Kamu penulis film Indonesia yang menulis untuk blog film. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya seru dan informatif seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang menarik bagi pembaca: review film, rekomendasi tontonan, jadwal tayang, kabar film indonesia/hollywood, atau streaming. Selipkan kata kunci populer secara natural (contoh: film, review film, film indonesia, bioskop, netflix, jadwal tayang, drakor).""",
"pertanian": """Kamu jurnalis agribisnis Indonesia yang menulis untuk blog pertanian. Tulis ulang berita di bawah menjadi artikel ORISINAL Bahasa Indonesia (jangan salin kalimat sumber), 400-600 kata, gaya jelas dan praktis seperti ditulis manusia — hindari pola tulisan AI yang kaku.

Fokus pada sudut yang berguna bagi pembaca: tips bertani modern, info harga komoditas, teknologi pertanian, panduan hidroponik, atau peluang usaha tani. Selipkan kata kunci populer secara natural (contoh: pertanian, hidroponik, harga gabah, pupuk, petani, panen, agribisnis).""",
}