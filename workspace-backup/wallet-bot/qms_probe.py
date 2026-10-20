#!/usr/bin/env python3
"""QMS Testnet probe: self-transfer 0.01 QMS via official RPC. Signs locally, never prints key."""
import time, sys
from web3 import Web3
from eth_account import Account

RPC = "https://rpc.testnet.qms.finance"
WALLET = Web3.to_checksum_address("0xf0f25C36AC70E9d787a108eFB351626192C8107b")
PK = open("/home/hatch/workspace/wallet-bot/.privkey").read().strip()

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))
assert w3.is_connected(), "RPC not connected"
acct = Account.from_key(PK)
assert acct.address.lower() == WALLET.lower(), "key/address mismatch"

nonce = w3.eth.get_transaction_count(WALLET)
bal = w3.eth.get_balance(WALLET)
gp = w3.eth.gas_price
if gp == 0:
    gp = w3.to_wei(20, "gwei")
print(f"nonce={nonce} balance={bal/10**18} QMS gasPrice={w3.from_wei(gp,'gwei')} gwei")

tx = {
    "chainId": 19480,
    "nonce": nonce,
    "to": WALLET,
    "value": w3.to_wei(0.01, "ether"),
    "gas": 21000,
    "gasPrice": gp,
}
signed = acct.sign_transaction(tx)
txhash = w3.eth.send_raw_transaction(signed.raw_transaction)
print("PROBE_HASH:", txhash.hex())
try:
    r = w3.eth.wait_for_transaction_receipt(txhash, timeout=180)
    print("RECEIPT status:", r.status, "block:", r.blockNumber, "gasUsed:", r.gasUsed)
    print("nonce_now:", w3.eth.get_transaction_count(WALLET))
    print("balance_now:", w3.eth.get_balance(WALLET) / 10**18)
except Exception as e:
    print("NO_RECEIPT within 180s:", type(e).__name__, str(e)[:200])
    print("nonce_now:", w3.eth.get_transaction_count(WALLET))
    sys.exit(2)
