#!/usr/bin/env python3
"""Upload LONG truecrime-en 2026-10-14 via yt-growth API (slug truecrime-en).
1. Verifikasi channel via channels?mine=true (HARUS Dark Case Files UC2df1xY_WqWdX33oLqeXE2w)
2. Cek playlist uploads: judul identik -> BATAL (anti-duplikat)
3. Resumable upload, private + publishAt 2026-10-15T00:00:00Z (= 15 Okt 07:00 WIB = 14 Okt 19:00 US Eastern)
AI disclosure TIDAK didukung API -> dicatat manual di Studio menyusul."""
import json, os, sys

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

BASE = os.path.expanduser("~/workspace/youtube-otomatis/truecrime-en")
SLUG = "truecrime-en"
VIDEO = os.path.join(BASE, "video/2026-10-14.mp4")
PUBLISH_AT = "2026-10-15T00:00:00.000Z"

TITLE = "The Gardner Heist: $500M Stolen in 81 Minutes, Still Unsolved"

DESCRIPTION = """Two men dressed as Boston police knocked on a museum door at 1:24 AM — and walked out 81 minutes later with $500 million in art. The Isabella Stewart Gardner Museum heist is the biggest art theft in history, and 36 years later, it is still unsolved. This true crime documentary reopens the file.

On March 18, 1990, the thieves tied up two young guards, cut Rembrandt's "The Storm on the Sea of Galilee" and Vermeer's "The Concert" right out of their frames, and vanished into the night with 13 masterpieces. The empty frames still hang in the museum today. In 2013, the FBI announced they believe they know WHO did it — they just don't know WHERE the art is. Honestly, in my opinion, those paintings are still in Boston, rolled up in somebody's basement.

What do you think happened that night — the mob, an inside job, or something stranger? Tell me in the comments.

CHAPTERS:
{chapters}

Sources: FBI press releases on the Gardner Museum theft (2013 investigative update); Isabella Stewart Gardner Museum official case history; contemporary reporting by the Boston Globe.

AI Disclosure: Narration and illustrations in this video are AI-generated; the mid-video bumper uses the channel owner's cloned voice with permission. 'Altered content' will be declared in YouTube Studio. Content is presented for educational and documentary purposes.

Subscribe to Dark Case Files for a new case file every day.

#truecrime #gardnermuseum #artheist #unsolvedmystery #documentary #boston #fbi #coldcase #foryou"""

TAGS = ["gardner museum heist", "isabella stewart gardner", "art heist",
        "true crime documentary", "true crime documentary 2026", "unsolved mystery",
        "boston art theft", "vermeer the concert stolen", "rembrandt stolen painting",
        "biggest art theft in history", "dark case files", "fbi cold case",
        "1990 museum robbery", "empty frames gardner museum"]

def chapters_text():
    dj = json.load(open(os.path.join(BASE, "audio/durasi-beat-2026-10-14.json")))
    beats = json.load(open(os.path.join(BASE, "script/beats-2026-10-14.json")))
    durs = [float(dj[b["id"]]) for b in beats]
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    CH = [("beat-001", "The Fake Cops at 1:24 AM"),
          ("beat-006", "Isabella's Palace of Art"),
          ("beat-016", "The Night of March 17, 1990"),
          ("beat-024", "81 Minutes Alone in the Museum"),
          ("beat-036", "The Thirteen Masterpieces"),
          ("beat-055", "The Investigation Begins"),
          ("beat-065", "The FBI Knows Who"),
          ("beat-079", "Still Unsolved — Where Is the Art?")]
    idx = {b["id"]: i for i, b in enumerate(beats)}
    lines = []
    for bid, name in CH:
        t = int(cum[idx[bid]])
        lines.append(f"{t//60}:{t%60:02d} {name}")
    return "\n".join(lines)


def main():
    s = api_session(SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != "UC2df1xY_WqWdX33oLqeXE2w" or "Dark Case Files" not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif BUKAN Dark Case Files!")

    # anti-duplikat: cek judul di playlist uploads
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "contentDetails"}, timeout=30)
    r.raise_for_status()
    upl = r.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    r = s.get("https://www.googleapis.com/youtube/v3/playlistItems",
              params={"playlistId": upl, "part": "snippet", "maxResults": 25}, timeout=30)
    r.raise_for_status()
    for it in r.json().get("items", []):
        if it["snippet"]["title"].strip().lower() == TITLE.strip().lower():
            sys.exit(f"BATAL: judul sudah ada di channel (videoId {it['snippet']['resourceId']['videoId']}) — anti-duplikat.")

    body = {
        "snippet": {"title": TITLE,
                    "description": DESCRIPTION.format(chapters=chapters_text()),
                    "tags": TAGS,
                    "categoryId": "27",
                    "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(VIDEO))},
               timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:500])
        sys.exit(10)
    up_url = r.headers["Location"]
    print("upload session OK", flush=True)
    size = os.path.getsize(VIDEO)
    chunk = 8 * 1024 * 1024
    with open(VIDEO, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk)
            end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": f"bytes {offset}-{end}/{size}"},
                       timeout=300)
            if rr.status_code in (200, 201):
                vid = rr.json()
                print("UPLOAD SELESAI:", vid["id"])
                print("URL: https://youtu.be/" + vid["id"])
                print(json.dumps({"id": vid["id"], "url": "https://youtu.be/" + vid["id"]}))
                return
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                if rng:
                    offset = int(rng.split("-")[1]) + 1
                else:
                    offset = end + 1
                print(f"... {offset}/{size}", flush=True)
            else:
                print("UPLOAD GAGAL:", rr.status_code, rr.text[:500])
                sys.exit(11)

if __name__ == "__main__":
    main()
