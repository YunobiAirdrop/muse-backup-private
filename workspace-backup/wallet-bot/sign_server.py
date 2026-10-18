#!/usr/bin/env python3
"""Local signing server for AutoWallet extension.
Receives unsigned tx params, signs with farming wallet private key, returns signed tx.
Runs on 127.0.0.1:18743. Only accessible locally.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from eth_account import Account

PRIVKEY_PATH = '/home/hatch/workspace/wallet-bot/.privkey'

with open(PRIVKEY_PATH) as f:
    PRIVKEY = f.read().strip()
ACCT = Account.from_key(PRIVKEY)
ADDRESS = ACCT.address
print(f"Signing server for {ADDRESS}", flush=True)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/sign':
            self.send_response(404); self.end_headers(); return
        try:
            length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(length))
            tx = body['tx']  # unsigned tx params from extension
            # Fill in defaults
            if 'from' not in tx:
                tx['from'] = ADDRESS
            if 'nonce' not in tx or tx['nonce'] is None:
                # Extension should provide nonce via eth_getTransactionCount
                raise ValueError("nonce required")
            # Sign
            signed = ACCT.sign_transaction(tx)
            resp = {'signedTx': signed.raw_transaction.hex()}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, *a):
        pass  # Quiet

if __name__ == '__main__':
    srv = HTTPServer(('127.0.0.1', 18743), Handler)
    print("Signing server on 127.0.0.1:18743", flush=True)
    srv.serve_forever()
