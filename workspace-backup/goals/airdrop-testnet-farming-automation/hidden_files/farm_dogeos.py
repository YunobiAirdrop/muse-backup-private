#!/usr/bin/env python3
"""Daily DogeOS activity txs for the farming wallet.
Reads privkey from the wallet-bot vault (600, user-authorized 2026-10-19),
never prints it. Sends N self-transfer (0 value) txs with network gas price.
Chain 6281971 (DogeOS Chikyū testnet). Usage: farm_dogeos.py [N]
Run with: ~/workspace/wallet-bot/venv/bin/python farm_dogeos.py 3
"""
import json, sys, time, urllib.request

PRIVKEY_PATH = "/home/hatch/workspace/wallet-bot/.privkey"
EXPECTED = "0xf0f25c36ac70e9d787a108efb351626192c8107b"
RPC = "https://rpc.testnet.dogeos.com/"
CHAIN_ID = 6281971
N_TX = int(sys.argv[1]) if len(sys.argv) > 1 else 3

from eth_account import Account

with open(PRIVKEY_PATH) as f:
    key = f.read().strip()
acct = Account.from_key(key)
addr = acct.address
assert addr.lower() == EXPECTED, f"address mismatch: {addr}"
print(f"wallet OK: {addr}", flush=True)

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "method": method,
                       "params": params, "id": 1}).encode()
    req = urllib.request.Request(
        RPC, data=body,
        headers={"Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0"})
    r = urllib.request.urlopen(req, timeout=30)
    d = json.loads(r.read())
    if "error" in d:
        raise RuntimeError(d["error"])
    return d["result"]

gas_price = int(rpc("eth_gasPrice", []), 16)
print(f"gasPrice: {gas_price} wei ({gas_price/1e9:.4f} gwei)", flush=True)
nonce = int(rpc("eth_getTransactionCount", [addr, "latest"]), 16)
print(f"start nonce: {nonce}", flush=True)

sent = []
for i in range(N_TX):
    tx = {
        "chainId": CHAIN_ID,
        "from": addr,
        "to": addr,               # self-transfer, 0 value (activity only)
        "value": 0,
        "gas": 21000,
        "gasPrice": gas_price,
        "nonce": nonce + i,
    }
    signed = acct.sign_transaction(tx)
    raw = signed.raw_transaction.hex()
    txhash = rpc("eth_sendRawTransaction", ["0x" + raw])
    sent.append(txhash)
    print(f"tx {i+1}/{N_TX} sent: {txhash}", flush=True)

for h in sent:
    for _ in range(20):
        rc = rpc("eth_getTransactionReceipt", [h])
        if rc:
            print(f"{h[:14]}... status={rc.get('status')} "
                  f"gasUsed={int(rc.get('gasUsed','0x0'),16)}", flush=True)
            break
        time.sleep(3)
    else:
        print(f"{h[:14]}... receipt timeout (sent, unconfirmed)", flush=True)

bal = int(rpc("eth_getBalance", [addr, "latest"]), 16) / 1e18
print(f"balance now: {bal:.6f} DOGE", flush=True)
