#!/usr/bin/env python3
"""Koreksi otomatis audit 3-harian 2026-10-13.

Fase 1 (default): dry-run via yt_push.py -> log untuk review.
Fase 2 (--apply): eksekusi nyata re-title/deskripsi/tags.
Fase 3 (--playlists): masukkan video flop tanpa playlist ke playlist funnel.

Kriteria: video flop (retensi <40% atau views ~0), umur >48 jam, maks 3/channel.
Video yang SUDAH dapat views bagus (horor 238-353, tinybuilders 1000+, lima-misteri
1318) TIDAK di-re-title — hanya dimasukkan ke playlist.
"""
import json
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
HERE = HOME / "workspace/goals/monetisasi-channel-youtube-dalam-3-bulan/hidden_files"
AUD = HERE / "audit-2026-10-13"
GROWTH = HOME / "workspace/youtube-otomatis/yt-growth"
sys.path.insert(0, str(GROWTH))

APPLY = "--apply" in sys.argv
DO_PLAYLISTS = "--playlists" in sys.argv

# (slug, video_id, judul_baru, deskripsi_baru|None, tags_baru|None)
CORRECTIONS = [
 # empires-en — shorts Göbekli Tepe, 0% retensi
 ("empires-en", "QnxIQ8J16_M",
  "This Temple Is Older Than Farming Itself #shorts #history #archaeology #foryou",
  None, None),
 ("empires-en", "SVv6jFBOWkA",
  "12,000 Years Old \u2014 The Temple That Shouldn't Exist #shorts #history #archaeology #foryou",
  None, None),
 ("empires-en", "rmkMgiPdLCo",
  "G\u00f6bekli Tepe: The 12,000-Year-Old Temple Built Before Farming Existed",
  None, None),
 # history-en — long Pompeii
 ("history-en", "PFG-p8TNA4o",
  "Pompeii's Last Morning: A Living City Buried in 79 AD",
  None, None),
 # horror-en — long + 2 shorts (shorts tanpa hashtag/tags sama sekali)
 ("horror-en", "W-9_kjVUpuI",
  "The Last Bus to Black Hollow Never Came Back | Horror Story",
  None, None),
 ("horror-en", "7mkgmONd89o",
  "Dead for 52 Years \u2014 Then He Opened His Eyes #shorts #horror #scarystories #foryou",
  None, "horror stories,scary stories,tales of dread,creepy stories,horror narration"),
 ("horror-en", "jhDzosY_vj8",
  "Her Mirror Showed No Reflection. Then It Moved #shorts #horror #scarystories #foryou",
  None, "horror stories,scary stories,tales of dread,creepy stories,horror narration"),
 # jejakislami — 3 shorts kisah Nabi Yusuf
 ("jejakislami", "l3G0yeRWSN8",
  "Dibuang ke Sumur oleh Kakaknya Sendiri \u2014 Kisah Nabi Yusuf #shorts #islami #kisahnabi #foryou",
  None, None),
 ("jejakislami", "AjKco8l2Hf0",
  "Difitnah Lalu Dipenjara \u2014 Kisah Nabi Yusuf yang Menggetarkan #shorts #islami #kisahnabi #foryou",
  None, None),
 ("jejakislami", "bltnidaQ0ms",
  "Mimpi 11 Bintang Jadi Kenyataan \u2014 Kisah Nabi Yusuf #shorts #islami #kisahnabi #foryou",
  None, None),
 # mystery-en — long Dyatlov + shorts (tambah #foryou)
 ("mystery-en", "g900Smffbuo",
  "9 Hikers Died on the Dead Mountain \u2014 Science Still Can't Explain It",
  None, None),
 ("mystery-en", "teVuCq5mvqM",
  "Glowing Orbs Over the Dead Mountain \u2014 No One Can Explain It #shorts #mystery #unsolved #foryou",
  None, None),
 # truecrime-en — long D.B. Cooper
 ("truecrime-en", "b3KyDWsTyq0",
  "D.B. Cooper: America's Only Unsolved Skyjacking (1971)",
  None, None),
 # weird-en — long Emu War
 ("weird-en", "MnqiOkoot10",
  "Australia Went to War Against Birds \u2014 And Lost | The Great Emu War 1932",
  None, None),
 # youtube-pov — 2 shorts gladiator (tambah #foryou)
 ("youtube-pov", "4xtnfzI3_Zg",
  "Dijual Jadi Budak, Mati Sebagai Legenda | POV Gladiator #shorts #pov #sejarah #foryou",
  None, None),
 ("youtube-pov", "sLsyvHV4BVg",
  "Detik-Detik Terakhir Sebelum Masuk Arena Kematian | POV Gladiator #shorts #pov #sejarah #foryou",
  None, None),
 # strangetales — shorts ubur-ubur abadi (tambah #foryou)
 ("strangetales", "Y5nf99683ZE",
  "The Jellyfish That Refuses to Die \u2014 Immortal?! #shorts #weirdfacts #ocean #foryou",
  None, None),
 # mind-en — long dark psychology
 ("mind-en", "9s5iaAecFRw",
  "7 Manipulation Tricks Controlling You Right Now (Dark Psychology)",
  None, None),
 # lima-misteri — long 5 kejadian aneh
 ("lima-misteri", "r-66OqDWV4Q",
  "5 Kejadian Aneh Nyata Paling Bikin Merinding | Nomor 1 Terseram",
  None, None),
]

# (slug, video_id, pola_judul_playlist) — video flop tanpa playlist
PLAYLIST_ADDS = [
 ("horor", "EepzwSQli1E", "Cerita Horor Terseram"),
 ("horor", "4JmORt_5CP0", "Cerita Horor Terseram"),
 ("horor", "5H9DWXm1aIs", "Cerita Horor Terseram"),
 ("tinybuilders", "uiTYVHzYzjU", "Miniature Builds"),
 ("tinybuilders", "-iDVbSSaoHU", "Miniature Builds"),
 ("tinybuilders", "GKvuJopBwcY", "Miniature Builds"),
 ("lima-misteri", "DENDsv-ujPg", "Kejadian Aneh"),
 ("horror-en", "7mkgmONd89o", "Scariest Horror"),
 ("horror-en", "jhDzosY_vj8", "Scariest Horror"),
]

# deskripsi: tambah hashtag block yang hilang (None = tidak diubah)
DESC_FIX = {
 ("horror-en", "7mkgmONd89o"): "\n\n#shorts #horror #scarystories #foryou",
 ("horror-en", "jhDzosY_vj8"): "\n\n#shorts #horror #scarystories #foryou",
 ("mystery-en", "teVuCq5mvqM"): " #foryou",
 ("strangetales", "Y5nf99683ZE"): " #foryou",
 ("youtube-pov", "4xtnfzI3_Zg"): " #foryou",
 ("youtube-pov", "sLsyvHV4BVg"): " #foryou",
}


def get_current_desc(slug, video_id):
    a = json.loads((AUD / f"{slug}.json").read_text())
    for v in a["analytics"].get("videos", []):
        if v["video_id"] == video_id:
            return v.get("description", "")
    return ""


def fix_desc(slug, vid, current):
    """Sisipkan #foryou ke blok hashtag (bukan tempel di akhir bila akhir = URL)."""
    if (slug, vid) == ("mystery-en", "teVuCq5mvqM"):
        return current.replace("#dyatlovpass", "#dyatlovpass #foryou")
    return current + DESC_FIX[(slug, vid)]


def find_playlist_id(slug, pattern):
    a = json.loads((AUD / f"{slug}.json").read_text())
    for p in a.get("playlists", []):
        if pattern.lower() in p["title"].lower():
            return p["id"], p["title"]
    return None, None


def main():
    log = []
    if not DO_PLAYLISTS:
        for slug, vid, title, desc, tags in CORRECTIONS:
            new_desc = desc
            if (slug, vid) in DESC_FIX:
                new_desc = fix_desc(slug, vid, get_current_desc(slug, vid))
            cmd = [str(GROWTH / ".venv/bin/python3"), str(GROWTH / "yt_push.py"),
                   slug, "--video", vid, "--title", title]
            if new_desc is not None:
                cmd += ["--description", new_desc]
            if tags is not None:
                cmd += ["--tags", tags]
            if APPLY:
                cmd += ["--apply"]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            out = f"$ {' '.join(cmd[:6])} ...\n{r.stdout}\n{r.stderr}"
            log.append(out)
            status = "APPLIED" if APPLY else "DRYRUN"
            print(f"[{status}] {slug}/{vid}: rc={r.returncode}")
        (HERE / ("corrections-apply.log" if APPLY else "corrections-dryrun.log")
         ).write_text("\n".join(log), encoding="utf-8")
    else:
        from auth import api_session, yt_get
        results = []
        for slug, vid, pattern in PLAYLIST_ADDS:
            pid, ptitle = find_playlist_id(slug, pattern)
            if not pid:
                results.append(f"{slug}/{vid}: playlist '{pattern}' TIDAK DITEMUKAN")
                print(results[-1])
                continue
            # cek duplikat
            items = yt_get(slug, "/playlistItems",
                           {"playlistId": pid, "part": "contentDetails",
                            "maxResults": 50}).get("items", [])
            existing = {it["contentDetails"]["videoId"] for it in items}
            if vid in existing:
                results.append(f"{slug}/{vid}: sudah ada di '{ptitle}' — skip")
                print(results[-1])
                continue
            if not APPLY:
                results.append(f"{slug}/{vid}: [DRYRUN] akan ditambah ke '{ptitle}'")
                print(results[-1])
                continue
            s = api_session(slug)
            rr = s.post("https://www.googleapis.com/youtube/v3/playlistItems",
                        params={"part": "snippet"},
                        json={"snippet": {"playlistId": pid,
                                          "resourceId": {"kind": "youtube#video",
                                                         "videoId": vid}}},
                        timeout=60)
            if rr.status_code == 200:
                results.append(f"{slug}/{vid}: OK ditambah ke '{ptitle}'")
            else:
                results.append(f"{slug}/{vid}: GAGAL {rr.status_code} {rr.text[:200]}")
            print(results[-1])
        (HERE / ("playlists-apply.log" if APPLY else "playlists-dryrun.log")
         ).write_text("\n".join(results), encoding="utf-8")


if __name__ == "__main__":
    main()
