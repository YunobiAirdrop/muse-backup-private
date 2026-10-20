#!/usr/bin/env python3
"""QMS Testnet: swap 0.5 QMS->USDC, approve, add LP 0.5 QMS + USDC. Signs locally, never prints key."""
import time, sys, json
from web3 import Web3
from eth_account import Account

RPC = "https://rpc.testnet.qms.finance"
WALLET = Web3.to_checksum_address("0xf0f25C36AC70E9d787a108eFB351626192C8107b")
ROUTER = Web3.to_checksum_address("0x93AFF45f28e5DF1b55f5AEFEfB807De843b12619")
WQMS = Web3.to_checksum_address("0x9AA510295aC664A3d5A3182a3eFe959DE2B12c34")
USDC = Web3.to_checksum_address("0xDfF68E53a0A8275212927c12017f5aB5f1842a04")
PAIR = Web3.to_checksum_address("0x07e2fc733B75e8107342b58fb49aE311C4DB0643")
PK = open("/home/hatch/workspace/wallet-bot/.privkey").read().strip()

ROUTER_ABI = json.loads("""[
{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},
{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"}
]""")
ERC20_ABI = json.loads("""[
{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}
]""")

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))
assert w3.is_connected(), "RPC not connected"
acct = Account.from_key(PK)
assert acct.address.lower() == WALLET.lower()
router = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)
usdc = w3.eth.contract(address=USDC, abi=ERC20_ABI)
pair = w3.eth.contract(address=PAIR, abi=ERC20_ABI)

def send(fn, value=0, gas_fallback=300000):
    nonce = w3.eth.get_transaction_count(WALLET)
    gp = w3.eth.gas_price or w3.to_wei(20, "gwei")
    try:
        gas = int(fn.estimate_gas({"from": WALLET, "value": value}) * 1.3)
    except Exception as e:
        print("  estimate_gas failed, fallback:", str(e)[:120])
        gas = gas_fallback
    tx = fn.build_transaction({"chainId": 19480, "nonce": nonce, "from": WALLET,
                               "value": value, "gas": gas, "gasPrice": gp})
    signed = acct.sign_transaction(tx)
    h = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("  TX:", "0x" + h.hex())
    r = w3.eth.wait_for_transaction_receipt(h, timeout=300)
    print("  status:", r.status, "block:", r.blockNumber, "gasUsed:", r.gasUsed)
    if r.status != 1:
        raise RuntimeError(f"tx reverted: 0x{h.hex()}")
    return "0x" + h.hex(), r

deadline = int(time.time()) + 1200
usdc_before = usdc.functions.balanceOf(WALLET).call()
print("USDC before:", usdc_before / 10**6)

print("STEP A: swap 0.5 QMS -> USDC")
swap_hash, _ = send(router.functions.swapExactETHForTokens(0, [WQMS, USDC], WALLET, deadline),
                    value=w3.to_wei(0.5, "ether"))
usdc_after = usdc.functions.balanceOf(WALLET).call()
got = usdc_after - usdc_before
print("USDC received:", got / 10**6, f"({got} raw)")

print("STEP B: approve USDC to router")
appr_hash, _ = send(usdc.functions.approve(ROUTER, got), gas_fallback=80000)

print("STEP C: add LP 0.5 QMS + USDC")
lp_hash, _ = send(router.functions.addLiquidityETH(USDC, got, 0, 0, WALLET, deadline),
                  value=w3.to_wei(0.5, "ether"))

qms_bal = w3.eth.get_balance(WALLET)
usdc_bal = usdc.functions.balanceOf(WALLET).call()
lp_bal = pair.functions.balanceOf(WALLET).call()
print("=== FINAL ===")
print("swap_hash:", swap_hash)
print("approve_hash:", appr_hash)
print("lp_hash:", lp_hash)
print("QMS:", qms_bal / 10**18)
print("USDC:", usdc_bal / 10**6)
print("LP token:", lp_bal / 10**18)
print("nonce:", w3.eth.get_transaction_count(WALLET))
