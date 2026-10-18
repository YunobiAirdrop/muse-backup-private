#!/usr/bin/env python3
"""
Local TCP forwarder: 127.0.0.1:3129 -> hatch-egress-proxy:3128.

Chromium has issues with the egress proxy directly (IPv6/DNS quirk);
forwarding through localhost sidesteps it. Transparent byte pipe —
does not inspect or log traffic.
"""
import socket
import threading

LISTEN = ("127.0.0.1", 3129)
TARGET = ("hatch-egress-proxy", 3128)


def pipe(a, b):
    try:
        while True:
            data = a.recv(65536)
            if not data:
                break
            b.sendall(data)
    except Exception:
        pass
    finally:
        try:
            a.close()
        except Exception:
            pass
        try:
            b.close()
        except Exception:
            pass


def handle(client):
    try:
        upstream = socket.create_connection(TARGET, timeout=10)
    except Exception:
        client.close()
        return
    t1 = threading.Thread(target=pipe, args=(client, upstream), daemon=True)
    t2 = threading.Thread(target=pipe, args=(upstream, client), daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(LISTEN)
    srv.listen(50)
    print(f"[*] Forwarder {LISTEN} -> {TARGET}", flush=True)
    while True:
        client, _ = srv.accept()
        threading.Thread(target=handle, args=(client,), daemon=True).start()


if __name__ == "__main__":
    main()
