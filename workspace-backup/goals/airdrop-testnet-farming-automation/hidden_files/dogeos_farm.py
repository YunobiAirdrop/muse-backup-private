#!/usr/bin/env python3
"""DogeOS ChikyU daily farming: N small self-transfers with low gas.
Key read transiently from .privkey (600), never printed or logged."""
import json
import random
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/wallet-bot/venv/lib/python3.12/site-packages")
from web3 import Web3
from eth_account import Account

ADDR = "0xf0f25C36AC70E9d787a108eFB351626192C8107b"
RPC = "https://rpc.testnet.dogeos.com/"
N_TX = 5

with open("/home/hatch/workspace/wallet-bot/.privkey") as f:
    key = f.read().strip()
acct = Account.from_key(key)
assert acct.address.lower() == ADDR.lower(), "key/address mismatch"

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 20}))
nonce = w3.eth.get_transaction_count(acct.address)
sent = []
for i in range(N_TX):
    amount = random.randint(1000, 100000)  # tiny wei amounts, natural-looking
    try:
        fee = w3.eth.fee_history(1, "latest")
        base = fee["baseFeePerGas"][-1]
        max_fee = int(base * 1.1) + 1
        prio = 1
    except Exception:
        max_fee, prio = w3.to_wei(0.01, "gwei"), 1
    tx = {
        "to": acct.address, "value": amount,
        "gas": 21000,
        "maxFeePerGas": max_fee,
        "maxPriorityFeePerGas": prio,
        "nonce": nonce + i,
        "chainId": 6281971,
        "type": 2,
    }
    signed = acct.sign_transaction(tx)
    h = w3.eth.send_raw_transaction(signed.raw_transaction)
    sent.append(h.hex())
    print(json.dumps({"i": i + 1, "hash": h.hex(), "nonce": nonce + i}))
    time.sleep(random.randint(5, 20))

# wait for receipts
ok = 0
for h in sent:
    try:
        r = w3.eth.wait_for_transaction_receipt(h, timeout=120)
        if r["status"] == 1:
            ok += 1
    except Exception as e:
        print(json.dumps({"hash": h, "receipt_error": str(e)[:80]}))
print(json.dumps({"sent": len(sent), "confirmed": ok}))
