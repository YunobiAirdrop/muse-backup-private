#!/usr/bin/env python3
"""Deploy firebase-pwa.html ke Firebase Hosting (yt-dashboard-yunobi.web.app).

Alur REST API (pelajaran 2026-10-15):
versions.create -> :populateFiles (hash = SHA256 file yg SUDAH di-gzip)
-> upload gzip ke {uploadUrl}/{hash} -> PATCH finalize -> POST releases (query param).
"""
import gzip, hashlib, json, sys, time, urllib.request, urllib.error, urllib.parse

SITE = "yt-dashboard-yunobi"
BASE = "https://firebasehosting.googleapis.com/v1beta1"
TOK_FILE = "/home/hatch/.hermes/yt-firebase-hosting.json"
DEPLOY_CLIENT = "/home/hatch/.hermes/yt-dashboard-deploy.json"
HTML = "/home/hatch/workspace/yt-dashboard/firebase-pwa.html"


def get_token():
    tok = json.load(open(TOK_FILE))
    if tok.get("expires_at", 0) > time.time() + 60:
        return tok["access_token"]
    # refresh
    client = json.load(open(DEPLOY_CLIENT))
    data = urllib.parse.urlencode({
        "client_id": client["client_id"], "client_secret": client["client_secret"],
        "refresh_token": tok["refresh_token"], "grant_type": "refresh_token"}).encode()
    r = urllib.request.urlopen("https://oauth2.googleapis.com/token", data, timeout=30)
    nt = json.load(r)
    tok["access_token"] = nt["access_token"]
    tok["expires_at"] = int(time.time()) + nt.get("expires_in", 3600) - 60
    json.dump(tok, open(TOK_FILE, "w"))
    import os; os.chmod(TOK_FILE, 0o600)
    return tok["access_token"]


def api(method, path, body=None, raw=None, headers=None):
    token = get_token()
    h = {"Authorization": f"Bearer {token}"}
    if body is not None:
        h["Content-Type"] = "application/json"
        raw = json.dumps(body).encode()
    if headers:
        h.update(headers)
    req = urllib.request.Request(BASE + path, data=raw, headers=h, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} {path}: {e.read()[:300]}", flush=True)
        raise


def main():
    files = {
        "/index.html": gzip.compress(open(HTML, "rb").read(), compresslevel=9),
        "/sw.js": gzip.compress(open("/home/hatch/workspace/yt-dashboard/static/sw.js", "rb").read(), compresslevel=9),
    }
    hashes = {p: hashlib.sha256(gz).hexdigest() for p, gz in files.items()}
    for p, gz in files.items():
        print(f"file {p}: {len(gz)} bytes gz, sha256 {hashes[p][:12]}...", flush=True)

    ver = api("POST", f"/sites/{SITE}/versions", {"config": {"headers": [
        {"glob": "/sw.js", "headers": {"Cache-Control": "no-cache, no-store, must-revalidate"}},
        {"glob": "**", "headers": {"Cache-Control": "max-age=3600"}},
    ]}})
    vname = ver["name"]
    print("version:", vname, flush=True)

    pop = api("POST", f"/{vname}:populateFiles",
              {"files": {p: h for p, h in hashes.items()}})
    import subprocess, tempfile, os
    for p, gz in files.items():
        h = hashes[p]
        upurl = pop["uploadUrl"] + "/" + h
        print(f"uploading {p}...", flush=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gz") as tf:
            tf.write(gz)
            tmp = tf.name
        # upload via curl (urllib kena 411 Length Required di env ini)
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                            "-X", "POST", upurl,
                            "-H", f"Authorization: Bearer {get_token()}",
                            "-H", "Content-Type: application/octet-stream",
                            "--data-binary", "@" + tmp],
                           capture_output=True, text=True, timeout=120)
        os.unlink(tmp)
        if r.stdout.strip() != "200":
            raise RuntimeError(f"upload {p} gagal: HTTP {r.stdout} {r.stderr[:200]}")
        print(f"upload {p} OK", flush=True)

    api("PATCH", f"/{vname}?updateMask=status", {"status": "FINALIZED"})
    print("finalized", flush=True)

    rel = api("POST", f"/sites/{SITE}/releases?versionName=" + urllib.parse.quote(vname, safe=""), {})
    print("released:", rel["name"], flush=True)
    print(f"\nLIVE: https://{SITE}.web.app")


if __name__ == "__main__":
    main()
