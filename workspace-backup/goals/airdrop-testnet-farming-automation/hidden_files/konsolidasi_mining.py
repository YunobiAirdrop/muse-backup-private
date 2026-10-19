#!/usr/bin/env python3
"""Konsolidasi mining harian: cek saldo Sepolia ETH wallet index 1-10,
kirim 90% saldo (>0.001 ETH) ke wallet utama. Tidak menyentuh browser."""
import json, sys, time
from web3 import Web3

MAIN = "0xf0f25C36AC70E9d787a108eFB351626192C8107b"
RPC = "https://ethereum-sepolia-rpc.publicnode.com"
THRESHOLD = Web3.to_wei(0.001, "ether")
CHAIN = 11155111
OUT = "/home/hatch/workspace/goals/airdrop-testnet-farming-automation/hidden_files/konsolidasi-mining-log.jsonl"

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))
if not w3.is_connected():
    print("RPC_UNREACHABLE"); sys.exit(2)

privs = json.load(open("/home/hatch/workspace/airdrop-farming/wallets-30-private.json"))
by_idx = {it["index"]: it for it in privs}

results = []
for idx in range(1, 11):
    it = by_idx[idx]
    addr = Web3.to_checksum_address(it["address"])
    bal = w3.eth.get_balance(addr)
    entry = {"index": idx, "address": addr, "balance_eth": float(w3.from_wei(bal, "ether"))}
    if bal > THRESHOLD:
        acct = w3.eth.account.from_key(it["private_key"])
        if acct.address != addr:
            entry["error"] = "KEY_MISMATCH"
        else:
            gas_price = w3.eth.gas_price
            amount = bal * 9 // 10
            gas_cost = 21000 * gas_price
            if amount + gas_cost >= bal:
                amount = bal - gas_cost - 1000
            nonce = w3.eth.get_transaction_count(addr)
            tx = {"to": Web3.to_checksum_address(MAIN), "value": amount,
                  "gas": 21000, "gasPrice": gas_price, "nonce": nonce, "chainId": CHAIN}
            try:
                signed = acct.sign_transaction(tx)
                txh = w3.eth.send_raw_transaction(signed.raw_transaction)
                entry["sent_eth"] = float(w3.from_wei(amount, "ether"))
                entry["tx"] = txh.hex()
                entry["gas_price_gwei"] = float(w3.from_wei(gas_price, "gwei"))
            except Exception as e:
                entry["error"] = f"SEND_FAIL: {type(e).__name__}: {e}"
            time.sleep(1)
    results.append(entry)

with open(OUT, "a") as f:
    f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "run": results}) + "\n")

print(json.dumps(results, indent=2))
