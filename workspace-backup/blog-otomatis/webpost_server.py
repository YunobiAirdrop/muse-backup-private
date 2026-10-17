#!/usr/bin/env python3
"""HTTP server untuk menyajikan artikel ke browser task (posting via web UI).
Jalan di 127.0.0.1:8899, serve direktori data/webpost/.
"""
import http.server, os

BASE = os.path.dirname(os.path.abspath(__file__))
WEBDIR = os.path.join(BASE, "data", "webpost")
os.makedirs(WEBDIR, exist_ok=True)

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=WEBDIR, **kw)
    def log_message(self, *a):
        pass

if __name__ == "__main__":
    srv = http.server.HTTPServer(("127.0.0.1", 8899), H)
    print("webpost server di 127.0.0.1:8899")
    srv.serve_forever()
