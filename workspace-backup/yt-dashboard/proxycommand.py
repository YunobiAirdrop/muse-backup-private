#!/usr/bin/env python3
"""ProxyCommand untuk ssh: CONNECT melalui egress proxy berautentikasi VM,
lalu sambungkan stdin/stdout ke socket. Pakai: ProxyCommand python3 proxycommand.py %h %p"""
import base64
import os
import socket
import sys

proxy_host = "hatch-egress-proxy"
proxy_port = 3128
user = "hatch-runtime"
pw = None
for var in ("https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY"):
    v = os.environ.get(var, "")
    if v and "@" in v:
        from urllib.parse import urlparse
        u = urlparse(v)
        proxy_host, proxy_port = u.hostname, u.port or 3128
        user, pw = u.username, u.password
        break

target_host, target_port = sys.argv[1], int(sys.argv[2])

s = socket.create_connection((proxy_host, proxy_port), timeout=20)
auth = ""
if user and pw:
    auth = "Proxy-Authorization: Basic " + base64.b64encode(f"{user}:{pw}".encode()).decode() + "\r\n"
req = (f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
       f"Host: {target_host}:{target_port}\r\n{auth}\r\n")
s.sendall(req.encode())
resp = b""
while b"\r\n\r\n" not in resp:
    chunk = s.recv(4096)
    if not chunk:
        sys.exit("proxy CONNECT gagal: koneksi ditutup")
    resp += chunk
if b" 200 " not in resp.split(b"\r\n", 1)[0]:
    sys.exit(f"proxy CONNECT ditolak: {resp[:120]!r}")

# bridge stdin/stdout <-> socket
import threading
def pipe(a, b):
    try:
        while True:
            d = a.read(65536) if a is sys.stdin.buffer else a.recv(65536)
            if not d:
                break
            (b.write if b is sys.stdout.buffer else b.sendall)(d)
    except Exception:
        pass
    finally:
        try: s.shutdown(socket.SHUT_RDWR)
        except Exception: pass

t = threading.Thread(target=pipe, args=(sys.stdin.buffer, s), daemon=True)
t.start()
pipe(s, sys.stdout.buffer)
