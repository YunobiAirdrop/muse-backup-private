#!/usr/bin/env python3
"""Read-only balance check for farming wallet across testnet networks.
No signing, no transactions. Uses venv web3. Prints JSON."""
import json
import sys

sys.path.insert(0, "/home/hatch/workspace/wallet-bot/venv/lib/python3.12/site-packages")
from web3 import Web3

ADDR = "0xf0f25C36AC70E9d787a108eFB351626192C8107b"

CHAINS = [
    ("sepolia", 11155111, "https://ethereum-sepolia-rpc.publicnode.com", "ETH"),
    ("dogeos", 6281971, "https://rpc.testnet.dogeos.com/", "DOGE"),
    ("bsc_testnet", 97, "https://data-seed-prebsc-1-s1.binance.org:8545/", "tBNB"),
    ("elysium", 99801, "https://testnet-rpc.elysium.kinetiq.xyz", "HYPE"),
    ("arbitrum_sepolia", 421614, "https://sepolia-rollup.arbitrum.io/rpc", "ETH"),
    ("base_sepolia", 84532, "https://sepolia.base.org", "ETH"),
    ("megaeth_mainnet", 1618, "https://rpc.megaeth.com", "ETH"),
    ("sahara", 313313, "https://rpc.saharalabs.ai", "SAH"),
]

out = {}
for name, cid, rpc, sym in CHAINS:
    try:
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 15}))
        bal = w3.eth.get_balance(Web3.to_checksum_address(ADDR))
        out[name] = {"ok": True, "balance": float(Web3.from_wei(bal, "ether")),
                     "symbol": sym, "wei": bal}
    except Exception as e:
        out[name] = {"ok": False, "error": str(e)[:120]}
print(json.dumps({"address": ADDR, "balances": out}, indent=1))
