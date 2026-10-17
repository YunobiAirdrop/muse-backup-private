#!/usr/bin/env python3
"""Upload LONG Jejak Islami 2026-10-14 (Ashabul Kahfi) via YouTube Data API v3.
Channel dicek via API: harus "Jejak Islami" (UC81zPJnIJbKU5lhTKx-6Hyg).
Jadwal tayang: 2026-10-15 19:00 WIB = 2026-10-15T12:00:00Z.
"""
import json
import os
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

W = "/home/hatch/workspace/kisah-islami/work/2026-10-14"
VIDEO = f"{W}/jejak-islami-2026-10-14-long.mp4"
THUMB = f"{W}/thumbnail.jpg"

TITLE = "Tidur 309 Tahun: Kisah Ashabul Kahfi"
DESCRIPTION = """Tujuh pemuda melarikan diri dari raja zalim, tertidur di dalam gua, lalu terbangun 309 tahun kemudian di dunia yang sama sekali berbeda. Ini kisah nyata Ashabul Kahfi yang diabadikan Al-Quran dalam surah Al-Kahfi ayat 9 sampai 26.

Yang membuat saya takjub: di zaman ketika beriman bisa berarti kematian, mereka justru memilih gua yang gelap daripada istana yang terang. Pelajaran besar buat kita semua.

Sumber: Al-Quran Surah Al-Kahfi (18): 9-26; riwayat yang masyhur.
Konten ini dibuat dengan bantuan AI (penulisan naskah & voiceover), berdasarkan sumber-sumber di atas.

Bab:
0:00 Tertidur 309 tahun lalu bangun
0:55 Kota Afsus di bawah Raja Dakyanus
1:57 Berdiri tegak di hadapan raja
2:48 Pelarian ke gua dan doa para pemuda
3:34 Tidur tiga abad lebih
4:44 Terbangun: sehari atau setengah hari?
5:29 Koin kuno menggemparkan kota
6:18 Pelajaran dari Ashabul Kahfi
7:26 Penutup

Kredit footage — semua klip dari Wikimedia Commons (lisensi bebas, aman komersial):
- "Postojna Cave (16872364368)" — CC BY 2.0 — https://commons.wikimedia.org/wiki/File:Postojna_Cave_(16872364368).ogv
- "Ephesus Efes Turkey 2015" oleh Klapi — CC BY-SA 4.0 — https://commons.wikimedia.org/wiki/File:Ephesus_Efes_Turkey_2015.webm
- "Grand Canyon National Park B-roll Video- Cape Royal Sunset - Time-lapse (8661965788)" — Public domain — https://commons.wikimedia.org/wiki/File:Grand_Canyon_National_Park_B-roll_Video-_Cape_Royal_Sunset_-_Time-lapse_(8661965788).webm
- "Valska Jama" oleh BojanM79 — CC0 — https://commons.wikimedia.org/wiki/File:Valska_Jama.webm
- "Teri sands" oleh L. Shyamal — CC0 — https://commons.wikimedia.org/wiki/File:Teri_sands.webm
- "The Milky Way over the Oasis of Mara (29954101654)" oleh Joshua Tree National Park — Public domain — https://commons.wikimedia.org/wiki/File:The_Milky_Way_over_the_Oasis_of_Mara_(29954101654).webm
- "Drone video above Yakima River Canyon (36963708885)" oleh BLM Oregon & Washington — Public domain — https://commons.wikimedia.org/wiki/File:Drone_video_above_Yakima_River_Canyon_(36963708885).webm
- "Time Lapse Clouds above Steens Mountain (36203941112)" oleh BLM Oregon & Washington — Public domain — https://commons.wikimedia.org/wiki/File:Time_Lapse_Clouds_above_Steens_Mountain_(36203941112).webm
- "2013-04-12 10-33-00-lampe-acetylene" oleh Thomas Bresson — CC BY 3.0 — https://commons.wikimedia.org/wiki/File:2013-04-12_10-33-00-lampe-acetylene.ogv
- "Mojave Desert Sunset (40480403760)" oleh blmcalifornia — Public domain — https://commons.wikimedia.org/wiki/File:Mojave_Desert_Sunset_(40480403760).webm
- "Dune du Pilat 2018" oleh Manuel Ramirez — CC BY 4.0 — https://commons.wikimedia.org/wiki/File:Dune_du_Pilat_2018.webm
- "Dark Skies (Timelapse HD)" oleh Daduxio — CC BY 3.0 — https://commons.wikimedia.org/wiki/File:Dark_Skies_(Timelapse_HD).webm
- "La Silla Timelapse 271109" oleh ESO/A.Santerne — CC BY 4.0 — https://commons.wikimedia.org/wiki/File:La_Silla_Timelapse_271109.ogv
- "Cloud timelapse in New Mexico" oleh John Fowler — CC BY 2.0 — https://commons.wikimedia.org/wiki/File:Cloud_timelapse_in_New_Mexico.webm
- "Visite de l'interieur de la mosquee de Mansourah, Tlemcen" oleh Riad Salih — CC BY-SA 4.0 — https://commons.wikimedia.org/wiki/File:Visite_de_l%27int%C3%A9rieur_de_la_mosqu%C3%A9e_de_Mansourah,_Tlemcen.webm
- "Eid al-Fitr prayer, Brazil Mosque, Sao Paulo - 17 July 2015 01" oleh Mesquita Brasil (SBM) — CC BY 3.0 — https://commons.wikimedia.org/wiki/File:Eid_al-Fitr_prayer,_Brazil_Mosque,_S%C3%A3o_Paulo_-_17_July_2015_01.webm

#foryou #kisahislami #ashabulkahfi #kisahnabi #guakahfi #ceritanabi #kisahnyata #mukjizat #sejarahislam #dakwah #islam"""
TAGS = ["kisah ashabul kahfi", "ashabul kahfi", "tujuh pemuda gua", "gua kahfi",
        "tidur 309 tahun", "kisah islami", "cerita nabi", "kisah para nabi",
        "surah al kahfi", "mukjizat", "kisah nyata islami", "sejarah islam",
        "dakwah islam", "cerita islami", "kajian islam", "pemuda beriman",
        "hikmah kisah nabi", "islam", "al quran", "kisah teladan"]
PUBLISH_AT = "2026-10-15T12:00:00Z"  # = 2026-10-15 19:00 WIB
PIN_COMMENT = "Kalau kamu yang terbangun setelah 309 tahun, apa hal pertama yang kamu cari? Tulis di komentar ya."
YT = "https://www.googleapis.com/youtube/v3"
UP = "https://www.googleapis.com/upload/youtube/v3"


def main():
    s = api_session("jejakislami")

    r = s.get(f"{YT}/channels", params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        sys.exit("GAGAL: tidak ada channel pada kredensial ini")
    title, cid = items[0]["snippet"]["title"], items[0]["id"]
    print(f"Channel terverifikasi: {title} (id={cid})", flush=True)
    if "jejak islami" not in title.lower() or cid != "UC81zPJnIJbKU5lhTKx-6Hyg":
        sys.exit(f"GAGAL: channel bukan Jejak Islami: {title} ({cid})")

    if not os.path.exists(VIDEO):
        sys.exit(f"GAGAL: video tidak ada: {VIDEO}")
    if len(TITLE) > 100:
        sys.exit("GAGAL: judul >100 karakter")

    body = {
        "snippet": {"title": TITLE, "description": DESCRIPTION, "tags": TAGS,
                    "categoryId": "27", "defaultLanguage": "id", "defaultAudioLanguage": "id"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False, "embeddable": True},
    }
    r = s.post(f"{UP}/videos", params={"uploadType": "resumable", "part": "snippet,status"},
               json=body, timeout=60)
    r.raise_for_status()
    session_uri = r.headers["Location"]
    print("Resumable session OK", flush=True)

    size = os.path.getsize(VIDEO)
    chunk = 8 * 1024 * 1024
    offset = 0
    with open(VIDEO, "rb") as f:
        while offset < size:
            data = f.read(chunk)
            end = offset + len(data) - 1
            for attempt in range(8):
                try:
                    rr = s.put(session_uri,
                               headers={"Content-Length": str(len(data)),
                                        "Content-Range": f"bytes {offset}-{end}/{size}"},
                               data=data, timeout=300)
                    break
                except Exception as e:
                    print(f"chunk retry {attempt+1}: {e}", flush=True)
                    time.sleep(5 * (attempt + 1))
            else:
                sys.exit("GAGAL upload chunk setelah 8x percobaan")
            if rr.status_code in (200, 201):
                resp = rr.json()
                break
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
                print(f"Upload {int(offset/size*100)}%", flush=True)
                continue
            else:
                sys.exit(f"GAGAL: HTTP {rr.status_code}: {rr.text[:300]}")
    vid = resp["id"]
    print(f"UPLOAD OK: videoId={vid}", flush=True)

    try:
        with open(THUMB, "rb") as tf:
            r = s.post(f"{UP}/thumbnails/set", params={"videoId": vid},
                       files={"media": ("thumbnail.jpg", tf, "image/jpeg")}, timeout=120)
        r.raise_for_status()
        print("THUMBNAIL OK", flush=True)
    except Exception as e:
        print(f"THUMBNAIL GAGAL (mungkin 403 - belum verifikasi HP): {e}", flush=True)

    try:
        r = s.post(f"{YT}/commentThreads", params={"part": "snippet"}, json={
            "snippet": {"videoId": vid, "topLevelComment": {"snippet": {
                "textOriginal": PIN_COMMENT}}}}, timeout=30)
        r.raise_for_status()
        print("KOMENTAR OK (pin manual via Studio)", flush=True)
    except Exception as e:
        print(f"KOMENTAR GAGAL: {e}", flush=True)

    url = f"https://www.youtube.com/watch?v={vid}"
    print(f"URL: {url}")
    print("STATUS: private, terjadwal tayang 2026-10-15 19:00 WIB")
    with open(f"{W}/upload-result.json", "w") as f:
        json.dump({"videoId": vid, "url": url, "publishAt": PUBLISH_AT,
                   "channel": title, "channelId": cid, "title": TITLE}, f, indent=2)


if __name__ == "__main__":
    main()
