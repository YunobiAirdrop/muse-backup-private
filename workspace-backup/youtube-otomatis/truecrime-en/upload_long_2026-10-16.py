#!/usr/bin/env python3
"""Upload LONG truecrime-en 2026-10-16 via yt-growth API (slug truecrime-en).
1. Verifikasi channel via channels?mine=true (HARUS Dark Case Files UC2df1xY_WqWdX33oLqeXE2w)
2. Cek playlist uploads: judul identik -> BATAL (anti-duplikat)
3. Resumable upload, private + publishAt 2026-10-18T00:00:00Z (= 18 Okt 07:00 WIB)
AI disclosure TIDAK didukung API -> ada di deskripsi + dicentang manual di Studio menyusul."""
import json, os, sys

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

BASE = os.path.expanduser("~/workspace/youtube-otomatis/truecrime-en")
SLUG = "truecrime-en"
VIDEO = os.path.join(BASE, "video/2026-10-16.mp4")
PUBLISH_AT = "2026-10-18T00:00:00.000Z"

TITLE = "Max Headroom Hijacking: Chicago TV Taken Over (Unsolved)"

DESCRIPTION = """On November 22, 1987, someone hijacked Chicago television \u2014 twice in one night. A masked figure took over the airwaves for 90 seconds, and nearly 40 years later, nobody has ever been caught. This true crime documentary reopens the strangest broadcast intrusion in history.

At 9:14 PM, during WGN Channel 9's evening news, the screen went black \u2014 replaced by a silent figure in a Max Headroom mask. Two hours later, during Doctor Who on WTTW Channel 11, he returned: 90 seconds of humming, taunting, and chaos beamed into thousands of homes. The FBI and FCC investigated. The trail went cold. In my opinion, the scariest part isn't the mask \u2014 it's that someone rehearsed all of this, down to the second, and vanished without a trace.

Were you watching that night in 1987? Tell me your story in the comments \u2014 and tell me what YOU think the motive was: prank, protest, or something stranger?

CHAPTERS:
{chapters}

Sources: FCC/FBI investigative records on the 1987 Chicago broadcast signal intrusions (public reporting); WGN-TV and WTTW archival coverage; contemporary Chicago Tribune reporting.

AI Disclosure: Narration and illustrations in this video are AI-generated; the mid-video bumper uses the channel owner's cloned voice with permission. 'Altered content' will be declared in YouTube Studio. Content is presented for educational and documentary purposes.

Subscribe to Dark Case Files for a new case file every day.

#truecrime #maxheadroom #unsolvedmystery #chicago #broadcastintrusion #coldcase #documentary #1980s #fbi #mystery #truecrimedocumentary #hijacking #foryou"""

TAGS = ["max headroom incident", "max headroom hijacking", "chicago tv hijacking",
        "wgn hijack 1987", "wttw hijack", "broadcast signal intrusion",
        "unsolved mystery", "true crime documentary", "chicago unsolved",
        "tv hijacker never caught", "fcc investigation", "doctor who interruption",
        "stl override", "pirate tv signal", "dark case files",
        "unsolved true crime", "mystery documentary", "1980s mystery",
        "cold case files", "signal hijacking"]

def chapters_text():
    dj = json.load(open(os.path.join(BASE, "audio/durasi-beat-2026-10-16.json")))
    beats = json.load(open(os.path.join(BASE, "script/beats-2026-10-16.json")))
    durs = [float(dj[b["id"]]) for b in beats]
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    CH = [("beat-001", "The Night the Signal Died"),
          ("beat-007", "Who Was Max Headroom"),
          ("beat-013", "The First Hijack: WGN"),
          ("beat-022", "90 Seconds on WTTW"),
          ("beat-046", "How They Did It"),
          ("beat-062", "The Investigation"),
          ("beat-074", "Still Unsolved"),
          ("beat-082", "Your Turn")]
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
            sys.exit(f"BATAL: judul sudah ada di channel (videoId {it['snippet']['resourceId']['videoId']}) \u2014 anti-duplikat.")

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
