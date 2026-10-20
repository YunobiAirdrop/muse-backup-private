#!/usr/bin/env python3
"""Konsolidasi mining PoW Sepolia -> wallet utama. Kirim 90% saldo wallet > 0.001 ETH."""
import json, sys
from web3 import Web3

MAIN = "0xf0f25C36AC70E9d787a108eFB351626192C8107b"
WALLETS = [
    "0xD386112D6dD42cA5aaDE2cfc42339A3e8B209b74",
    "0x3D8b397a13a0b6b2DE1612Ceb2549083f2a56EF0",
    "0x5061680395FeECb710ca05FE278A649f972E7314",
    "0xFEF5C460B0e80A1d0Ab4D9B623EB77433d47f35E",
    "0x3Fea13885E6880E459977Bd92107838Ab7aBdAfB",
    "0xC4ED373933175B63c9a36f1bf2e48cc366D6bec4",
    "0x9bAEFd20cFd41fE9C38bdD957dDA17FE1b4B13eb",
    "0xcBaC8eA4464630e020214b599ab5BA654A0B51F9",
    "0xDd4fB99be3A66A3E06424155f9e76a117b6F9FB6",
]
RPC = "https://ethereum-sepolia-rpc.publicnode.com"
PK_FILE = "/home/hatch/workspace/airdrop-farming/wallets-30-private.json"
THRESHOLD = int(0.001 * 10**18)

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))
if not w3.is_connected():
    print("ERROR: RPC tidak terhubung"); sys.exit(1)

pks = {e["address"]: e["private_key"] for e in json.load(open(PK_FILE))}
results = []
for addr in WALLETS:
    bal = w3.eth.get_balance(Web3.to_checksum_address(addr))
    entry = {"address": addr, "balance_eth": round(bal / 10**18, 6)}
    if bal <= THRESHOLD:
        entry["action"] = "skip (< 0.001 ETH)"
    else:
        gas_price = w3.eth.gas_price
        gas_fee = 21000 * gas_price
        amount = int(bal * 0.9)
        if amount + gas_fee > bal:
            amount = bal - gas_fee - int(0.00005 * 10**18)
        if amount <= 0:
            entry["action"] = "skip (gas lebih besar dari 90%)"
        else:
            tx = {
                "to": Web3.to_checksum_address(MAIN),
                "value": amount,
                "gas": 21000,
                "gasPrice": gas_price,
                "nonce": w3.eth.get_transaction_count(Web3.to_checksum_address(addr)),
                "chainId": 11155111,
            }
            signed = w3.eth.account.sign_transaction(tx, pks[addr])
            txh = w3.eth.send_raw_transaction(signed.raw_transaction)
            entry["action"] = f"kirim {amount/10**18:.6f} ETH, tx={txh.hex()}"
    results.append(entry)
    print(entry["address"][:12], entry["balance_eth"], "->", entry["action"])

total_sent = sum(float(r["action"].split("kirim ")[1].split(" ETH")[0])
                 for r in results if r["action"].startswith("kirim"))
sent_count = sum(1 for r in results if r["action"].startswith("kirim"))
print(f"\nWALLET_DIKONSOLIDASI={sent_count} TOTAL_TERKIRIM={total_sent:.6f} ETH")
