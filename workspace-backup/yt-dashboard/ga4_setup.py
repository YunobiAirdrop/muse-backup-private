#!/usr/bin/env python3
"""Setup GA4 via Admin API: 1 akun + 1 properti + 10 web data stream (10 blog).
Token di ~/.hermes/yt-ga4.json (600). Output: daftar Measurement ID."""
import json, os, sys, time, urllib.request, urllib.error, urllib.parse

TOK_FILE = "/home/hatch/.hermes/yt-ga4.json"
DEPLOY_CLIENT = "/home/hatch/.hermes/yt-dashboard-deploy.json"
BASE = "https://analyticsadmin.googleapis.com/v1beta"

BLOGS = [
    ("KabarViral", "https://kabarviralterkiniterbaru.blogspot.com"),
    ("TeknoPedia", "https://teknopedia-terbaru-dotcom.blogspot.com"),
    ("InfoKesehatan", "https://infokesehatan-hari-ini.blogspot.com"),
    ("EkonomiBisnis", "https://ekonomi-bisnis-info-terbaru.blogspot.com"),
    ("GayaHidup", "https://gaya-hidup-kekikinan.blogspot.com"),
    ("Olahraga", "https://olahraga-terbaru-terbaik.blogspot.com"),
    ("WisataIndo", "https://wisataindo-terbaru.blogspot.com"),
    ("KulinerNusantara", "https://kulinernusantara-terbaru.blogspot.com"),
    ("OtomotifInfo", "https://otomotifinfo-terbaru.blogspot.com"),
    ("PendidikanCerdas", "https://pendidikancerdas-terbaru.blogspot.com"),
]


def get_token():
    tok = json.load(open(TOK_FILE))
    if tok.get("expires_at", 0) > time.time() + 60:
        return tok["access_token"]
    client = json.load(open(DEPLOY_CLIENT))
    data = urllib.parse.urlencode({
        "client_id": client["client_id"], "client_secret": client["client_secret"],
        "refresh_token": tok["refresh_token"], "grant_type": "refresh_token"}).encode()
    nt = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", data, timeout=30))
    tok["access_token"] = nt["access_token"]
    tok["expires_at"] = int(time.time()) + nt.get("expires_in", 3600) - 60
    json.dump(tok, open(TOK_FILE, "w"))
    os.chmod(TOK_FILE, 0o600)
    return tok["access_token"]


def api(method, path, body=None):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {get_token()}", "Content-Type": "application/json"},
        method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} {path}: {e.read()[:400]}", flush=True)
        raise


def main():
    # 1. akun — pakai yang sudah ada (BeritaViral); POST /accounts 404 di v1beta
    acc_name = "accounts/410404756"
    print("account:", acc_name, flush=True)
    # 2. properti (industryCategory opsional; NEWS_AND_MEDIA bukan enum valid)
    prop = api("POST", "/properties", {
        "parent": acc_name, "displayName": "Yunobi Blogs",
        "timeZone": "Asia/Jakarta", "currencyCode": "IDR"})
    pname = prop["name"]
    print("property:", pname, flush=True)
    # 3. data streams
    ids = {}
    for name, url in BLOGS:
        ds = api("POST", f"/{pname}/dataStreams", {
            "displayName": name, "type": "WEB_DATA_STREAM",
            "webStreamData": {"defaultUri": url}})
        mid = ds.get("webStreamData", {}).get("measurementId")
        ids[name] = mid
        print(f"  {name}: {mid}", flush=True)
    json.dump({"property": pname, "account": acc_name, "streams": ids},
              open("/home/hatch/workspace/yt-dashboard/ga4_streams.json", "w"), indent=1)
    print("done")


if __name__ == "__main__":
    main()
