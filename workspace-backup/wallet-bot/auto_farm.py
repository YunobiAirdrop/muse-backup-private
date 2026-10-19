#!/usr/bin/env python3
"""
auto_farm.py — daily self-transfer farming across testnets.

Sends small self-transfers (wallet -> own wallet) to build on-chain
activity history for airdrop farming. Randomized amounts and intervals
so the pattern looks natural, not bot-like.

Cron-safe: tracks per-day quota in a state file; re-runs resume the
remaining quota instead of doubling it. Exits when the daily quota is
done (does NOT run forever).

Usage:
    ./venv/bin/python auto_farm.py                  # normal run
    ./venv/bin/python auto_farm.py --check           # print config, exit
    ./venv/bin/python auto_farm.py --dry-run        # simulate, no network/tx
    ./venv/bin/python auto_farm.py --chain sepolia   # only one chain

All RPC traffic goes through the local forwarder (127.0.0.1:3129),
started automatically if not already running.
"""
import argparse
import datetime
import json
import os
import random
import socket
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE, "auto_farm_config.json")
PRIVKEY_FILE = os.path.join(BASE, ".privkey")
FARMING_ADDRESS = "0xf0f25C36AC70E9d787a108eFB351626192C8107b"
PROXY = "http://127.0.0.1:3129"

# --- HexSwap DEX on Elysium Testnet (chain 99801, Uniswap V2) ---
HEXSWAP_ROUTER = "0x9D02c1D684389D021bF2Cf73D1ba7C4652aB1F15"
HEXSWAP_WNATIVE = "0x8FEdA963AA318dC94403A413AA94271588B92d64"  # wrapped HYPE
HEXSWAP_HEX = "0x26aA352bD4324AA507C924AF9EdD65B2c7BDC1c2"      # 18 decimals
HEXSWAP_USDT = "0xF04e426488A8679D6888ec9FB4922a98Dd2c17b0"     # 6 decimals
HEXSWAP_SWAP_GAS = 300000  # swaps need more gas than self-transfers

ROUTER_ABI = [
    {"name": "swapExactETHForTokens", "type": "function",
     "stateMutability": "payable",
     "inputs": [{"type": "uint256"}, {"type": "address[]"},
                {"type": "address"}, {"type": "uint256"}],
     "outputs": [{"type": "uint256[]"}]},
    {"name": "swapExactTokensForETH", "type": "function",
     "stateMutability": "nonpayable",
     "inputs": [{"type": "uint256"}, {"type": "uint256"},
                {"type": "address[]"}, {"type": "address"},
                {"type": "uint256"}],
     "outputs": [{"type": "uint256[]"}]},
    {"name": "swapExactTokensForTokens", "type": "function",
     "stateMutability": "nonpayable",
     "inputs": [{"type": "uint256"}, {"type": "uint256"},
                {"type": "address[]"}, {"type": "address"},
                {"type": "uint256"}],
     "outputs": [{"type": "uint256[]"}]},
]
ERC20_ABI = [
    {"name": "approve", "type": "function", "stateMutability": "nonpayable",
     "inputs": [{"type": "address"}, {"type": "uint256"}],
     "outputs": [{"type": "bool"}]},
    {"name": "balanceOf", "type": "function",
     "stateMutability": "view",
     "inputs": [{"type": "address"}], "outputs": [{"type": "uint256"}]},
    {"name": "allowance", "type": "function",
     "stateMutability": "view",
     "inputs": [{"type": "address"}, {"type": "address"}],
     "outputs": [{"type": "uint256"}]},
]

DEFAULTS = {
    "tx_per_day": 25,
    "amount_min_wei": 1000,
    "amount_max_wei": 100000,
    "interval_min_sec": 300,
    "interval_max_sec": 1800,
    "min_balance_wei": 10 ** 16,  # 0.01 native token
    "log_file": "auto_farm.log",
    "state_file": "auto_farm_state.json",
    "chains": {},
}


def log(*a):
    print(*a, flush=True)


def ensure_forwarder():
    """Start the local TCP forwarder if port 3129 is not listening."""
    try:
        socket.create_connection(("127.0.0.1", 3129), timeout=2).close()
        return False
    except Exception:
        pass
    subprocess.Popen(
        [os.path.join(BASE, "venv", "bin", "python"),
         os.path.join(BASE, "forwarder.py")],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    log("[*] forwarder started on 127.0.0.1:3129")
    return True


def load_config(path):
    cfg = dict(DEFAULTS)
    if os.path.exists(path):
        with open(path) as f:
            user = json.load(f)
        for k, v in user.items():
            cfg[k] = v
    # fill per-chain tx_per_day from global default
    for name, ch in cfg["chains"].items():
        ch.setdefault("tx_per_day", cfg["tx_per_day"])
    return cfg


def load_privkey():
    with open(PRIVKEY_FILE) as f:
        key = f.read().strip()
    if key.startswith("0x"):
        key = key[2:]
    if len(key) != 64:
        raise ValueError("privkey file has unexpected length")
    return key  # NEVER log this value


def load_state(path):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_state(path, state):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=1)
    os.replace(tmp, path)


def append_log(path, entry):
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def make_w3(rpc_url):
    from web3 import Web3
    proxies = {"http": PROXY, "https": PROXY}
    return Web3(Web3.HTTPProvider(
        rpc_url, request_kwargs={"proxies": proxies, "timeout": 30}))


def build_fee_params(w3, chain):
    """Return fee fields for the tx dict, honoring chain quirks."""
    mode = chain.get("fee_mode", "eip1559")
    gas_limit = int(chain.get("gas_limit", 21000))
    params = {"gas": gas_limit}
    if mode == "legacy_1.5x_basefee":
        # Elysium (Arbitrum Orbit): fixed gas, gasPrice ~1.5x base fee.
        try:
            base = w3.eth.get_block("latest").baseFeePerGas
            gas_price = int(base * 1.5)
        except Exception:
            gas_price = int(w3.eth.gas_price * 1.5)
        params["gasPrice"] = gas_price
    elif mode == "legacy":
        params["gasPrice"] = w3.eth.gas_price
    else:  # eip1559
        try:
            base = w3.eth.get_block("latest").baseFeePerGas
            prio = w3.eth.max_priority_fee
            params["maxFeePerGas"] = base * 2 + prio
            params["maxPriorityFeePerGas"] = prio
        except Exception:
            # fallback to legacy if the chain lies about 1559 support
            params["gasPrice"] = w3.eth.gas_price
    return params


def build_swap_fee_params(w3, gas_limit=HEXSWAP_SWAP_GAS):
    """Fee fields for Elysium DEX swaps: legacy tx, gasPrice 1.5x base fee."""
    try:
        base = w3.eth.get_block("latest").baseFeePerGas
        gas_price = int(base * 1.5)
    except Exception:
        gas_price = int(w3.eth.gas_price * 1.5)
    return {"gas": gas_limit, "gasPrice": gas_price}


def get_token_balance(w3, token_addr, wallet_addr):
    """Return ERC-20 balance (wei) for wallet, 0 on error."""
    try:
        token = w3.eth.contract(address=token_addr, abi=ERC20_ABI)
        return int(token.functions.balanceOf(wallet_addr).call())
    except Exception:
        return 0


def send_raw_tx(w3, acct, tx, chain_id, log_path, label):
    """Sign + send a raw tx, wait for receipt, log it. Returns tx_hash hex or None."""
    tx["chainId"] = int(chain_id)
    tx["nonce"] = w3.eth.get_transaction_count(acct.address)
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
    status = receipt.get("status", 0)
    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "chain": "elysium",
        "kind": label,
        "to": tx.get("to"),
        "tx_hash": tx_hash.hex(),
        "status": status,
        "gas_used": receipt.get("gasUsed"),
    }
    # include value/amount info when present for debugging (never keys)
    if tx.get("value"):
        entry["value_wei"] = tx["value"]
    append_log(log_path, entry)
    log(f"[elysium-swap] {label}: {tx_hash.hex()[:18]}… status={status}")
    return tx_hash.hex() if status == 1 else None


def do_approve(w3, acct, token_addr, spender, amount, chain_id,
               log_path, dry_run=False):
    """Approve spender for amount tokens. Returns True on success."""
    if dry_run:
        log(f"[elysium-swap] DRY-RUN approve {token_addr[:10]}… "
            f"-> {spender[:10]}… amount={amount}")
        return True
    token = w3.eth.contract(address=token_addr, abi=ERC20_ABI)
    data = token.encode_abi("approve", [spender, amount])
    tx = {"to": token_addr, "value": 0, "data": data}
    tx.update(build_swap_fee_params(w3, gas_limit=100000))
    try:
        result = send_raw_tx(w3, acct, tx, chain_id, log_path, "approve")
        return result is not None
    except Exception as e:
        log(f"[elysium-swap] approve failed: {str(e)[:150]}")
        return False


def do_swap_hype_to_token(w3, acct, token_out, amount_hype_wei,
                          chain_id, log_path, dry_run=False):
    """swapExactETHForTokens: HYPE -> token. Returns tx hash or None."""
    label = (f"swap HYPE->"
             f"{'HEX' if token_out == HEXSWAP_HEX else 'USDT'}")
    if dry_run:
        log(f"[elysium-swap] DRY-RUN {label} amount={amount_hype_wei} wei")
        return "dryrun"
    router = w3.eth.contract(address=HEXSWAP_ROUTER, abi=ROUTER_ABI)
    deadline = int(time.time()) + 600
    data = router.encode_abi("swapExactETHForTokens", [0, [HEXSWAP_WNATIVE, token_out], acct.address, deadline])
    tx = {"to": HEXSWAP_ROUTER, "value": amount_hype_wei, "data": data}
    tx.update(build_swap_fee_params(w3))
    try:
        return send_raw_tx(w3, acct, tx, chain_id, log_path, label)
    except Exception as e:
        log(f"[elysium-swap] {label} failed: {str(e)[:150]}")
        return None


def do_swap_token_to_hype(w3, acct, token_in, amount_in,
                          chain_id, log_path, dry_run=False):
    """approve + swapExactTokensForETH: token -> HYPE. Returns tx hash or None."""
    tname = 'HEX' if token_in == HEXSWAP_HEX else 'USDT'
    label = f"swap {tname}->HYPE"
    if dry_run:
        log(f"[elysium-swap] DRY-RUN approve+{label} amount={amount_in}")
        return "dryrun"
    # approve first (skip if allowance already covers it)
    try:
        token = w3.eth.contract(address=token_in, abi=ERC20_ABI)
        allowance = int(token.functions.allowance(
            acct.address, HEXSWAP_ROUTER).call())
    except Exception:
        allowance = 0
    if allowance < amount_in:
        if not do_approve(w3, acct, token_in, HEXSWAP_ROUTER,
                          amount_in, chain_id, log_path):
            return None
        time.sleep(3)  # let the approve propagate
    router = w3.eth.contract(address=HEXSWAP_ROUTER, abi=ROUTER_ABI)
    deadline = int(time.time()) + 600
    data = router.encode_abi("swapExactTokensForETH", [amount_in, 0, [token_in, HEXSWAP_WNATIVE],
              acct.address, deadline])
    tx = {"to": HEXSWAP_ROUTER, "value": 0, "data": data}
    tx.update(build_swap_fee_params(w3))
    try:
        return send_raw_tx(w3, acct, tx, chain_id, log_path, label)
    except Exception as e:
        log(f"[elysium-swap] {label} failed: {str(e)[:150]}")
        return None


def do_swap_token_to_token(w3, acct, token_in, token_out, amount_in,
                           chain_id, log_path, dry_run=False):
    """approve + swapExactTokensForTokens. Returns tx hash or None."""
    in_name = 'HEX' if token_in == HEXSWAP_HEX else 'USDT'
    out_name = 'HEX' if token_out == HEXSWAP_HEX else 'USDT'
    label = f"swap {in_name}->{out_name}"
    if dry_run:
        log(f"[elysium-swap] DRY-RUN approve+{label} amount={amount_in}")
        return "dryrun"
    try:
        token = w3.eth.contract(address=token_in, abi=ERC20_ABI)
        allowance = int(token.functions.allowance(
            acct.address, HEXSWAP_ROUTER).call())
    except Exception:
        allowance = 0
    if allowance < amount_in:
        if not do_approve(w3, acct, token_in, HEXSWAP_ROUTER,
                          amount_in, chain_id, log_path):
            return None
        time.sleep(3)
    router = w3.eth.contract(address=HEXSWAP_ROUTER, abi=ROUTER_ABI)
    deadline = int(time.time()) + 600
    data = router.encode_abi("swapExactTokensForTokens", [amount_in, 0, [token_in, token_out],
              acct.address, deadline])
    tx = {"to": HEXSWAP_ROUTER, "value": 0, "data": data}
    tx.update(build_swap_fee_params(w3))
    try:
        return send_raw_tx(w3, acct, tx, chain_id, log_path, label)
    except Exception as e:
        log(f"[elysium-swap] {label} failed: {str(e)[:150]}")
        return None


def farm_elysium_swaps(w3, acct, chain, swap_cfg, state_today,
                       log_path, cfg, dry_run=False):
    """Run Elysium's daily HexSwap quota. Returns swaps completed.

    Plan per day (7 swaps): 2x HYPE->HEX, 2x HYPE->USDT, 1x HEX->HYPE,
    1x HEX->USDT, 1x USDT->HYPE (spare). Token->X swaps check the
    wallet's token balance first and are skipped when empty.
    """
    target = int(swap_cfg.get("swaps_per_day", 7))
    done = int(state_today.get("elysium_swaps", {}).get("done", 0))
    remaining = max(0, target - done)
    chain_id = int(chain["chain_id"])
    min_bal = int(cfg["min_balance_wei"])
    if remaining == 0:
        log(f"[elysium-swap] quota already met ({done}/{target}), skipping")
        return 0

    # Build the day's swap plan, then shuffle for natural ordering.
    # HYPE->token swaps are balance-independent; token->X need balances.
    plan = [
        ("hype_to_token", HEXSWAP_HEX, None),
        ("hype_to_token", HEXSWAP_HEX, None),
        ("hype_to_token", HEXSWAP_USDT, None),
        ("hype_to_token", HEXSWAP_USDT, None),
        ("token_to_hype", HEXSWAP_HEX, None),
        ("token_to_token", HEXSWAP_HEX, HEXSWAP_USDT),
        ("token_to_hype", HEXSWAP_USDT, None),
    ]
    plan = plan[:target]
    random.shuffle(plan)

    amt_min = int(swap_cfg.get("amount_min_hype_wei", 5 * 10**14))
    amt_max = int(swap_cfg.get("amount_max_hype_wei", 2 * 10**15))

    sent = 0
    for i, action in enumerate(plan):
        if done + sent >= target:
            break
        kind = action[0]

        if dry_run:
            d = {"hype_to_token": lambda: do_swap_hype_to_token(
                    None, acct, action[1],
                    random.randint(amt_min, amt_max),
                    chain_id, log_path, dry_run=True),
                 "token_to_hype": lambda: do_swap_token_to_hype(
                    None, acct, action[1],
                    random.randint(10**15, 10**17),
                    chain_id, log_path, dry_run=True),
                 "token_to_token": lambda: do_swap_token_to_token(
                    None, acct, action[1], action[2],
                    random.randint(10**15, 10**17),
                    chain_id, log_path, dry_run=True)}[kind]()
            if d:
                sent += 1
                state_today.setdefault("elysium_swaps", {})["done"] = \
                    done + sent
            continue

        # HYPE balance gate before every swap
        try:
            hype_bal = w3.eth.get_balance(acct.address)
        except Exception as e:
            log(f"[elysium-swap] balance check failed: {str(e)[:80]} — "
                f"stopping swaps")
            break
        if hype_bal < min_bal:
            log(f"[elysium-swap] LOW HYPE BALANCE "
                f"({hype_bal} wei < {min_bal} wei min) — stopping swaps, "
                f"quota {done + sent}/{target}")
            break

        ok = None
        if kind == "hype_to_token":
            amount = random.randint(amt_min, amt_max)
            # don't overspend: keep at least min_bal HYPE in wallet
            spendable = hype_bal - min_bal
            if spendable <= 0:
                log("[elysium-swap] no spendable HYPE above floor — "
                    "stopping swaps")
                break
            amount = min(amount, spendable)
            ok = do_swap_hype_to_token(w3, acct, action[1], amount,
                                       chain_id, log_path)
        elif kind == "token_to_hype":
            bal = get_token_balance(w3, action[1], acct.address)
            if bal == 0:
                log(f"[elysium-swap] no "
                    f"{'HEX' if action[1] == HEXSWAP_HEX else 'USDT'} "
                    f"balance — skipping swap {done + sent + 1}/{target}")
                continue
            ok = do_swap_token_to_hype(w3, acct, action[1], bal,
                                       chain_id, log_path)
        elif kind == "token_to_token":
            bal = get_token_balance(w3, action[1], acct.address)
            if bal == 0:
                log(f"[elysium-swap] no "
                    f"{'HEX' if action[1] == HEXSWAP_HEX else 'USDT'} "
                    f"balance — skipping swap {done + sent + 1}/{target}")
                continue
            ok = do_swap_token_to_token(w3, acct, action[1], action[2],
                                        bal, chain_id, log_path)

        if ok:
            sent += 1
            state_today.setdefault("elysium_swaps", {})["done"] = done + sent
            log(f"[elysium-swap] progress {done + sent}/{target}")
        else:
            log(f"[elysium-swap] swap failed, continuing to next…")

        if done + sent < target:
            wait = random.randint(int(cfg["interval_min_sec"]),
                                  int(cfg["interval_max_sec"]))
            log(f"[elysium-swap] sleeping {wait}s before next swap…")
            time.sleep(wait)

    return sent


def farm_chain(w3, acct, chain_name, chain, cfg, state_today,
               log_path, dry_run=False):
    """Run this chain's remaining daily quota. Returns txs sent."""
    target = int(chain.get("tx_per_day", cfg["tx_per_day"]))
    done = int(state_today.get(chain_name, {}).get("done", 0))
    remaining = max(0, target - done)
    symbol = chain.get("symbol", "native")
    if remaining == 0:
        log(f"[{chain_name}] quota already met ({done}/{target}), skipping")
        return 0

    if dry_run:
        # simulate the loop with no network access at all
        for i in range(remaining):
            amount = random.randint(int(cfg["amount_min_wei"]),
                                    int(cfg["amount_max_wei"]))
            log(f"[{chain_name}] DRY-RUN tx {done + i + 1}/{target}: "
                f"self-transfer {amount} wei")
            state_today.setdefault(chain_name, {})["done"] = done + i + 1
        return remaining

    # connectivity + balance gate
    try:
        got_chain = w3.eth.chain_id
    except Exception as e:
        log(f"[{chain_name}] RPC unreachable: {str(e)[:100]} — skipping chain")
        return 0
    if got_chain != int(chain["chain_id"]):
        log(f"[{chain_name}] chain id mismatch: got {got_chain}, "
            f"want {chain['chain_id']} — skipping chain")
        return 0

    min_bal = int(cfg["min_balance_wei"])
    sent = 0
    for i in range(remaining):
        try:
            balance = w3.eth.get_balance(acct.address)
        except Exception as e:
            log(f"[{chain_name}] balance check failed: {str(e)[:80]} — "
                f"stopping chain")
            break
        if balance < min_bal:
            log(f"[{chain_name}] LOW BALANCE "
                f"({balance} wei < {min_bal} wei min) — stopping chain, "
                f"quota {done + sent}/{target}")
            break

        amount = random.randint(int(cfg["amount_min_wei"]),
                                int(cfg["amount_max_wei"]))
        tx = {
            "to": acct.address,  # self-transfer
            "value": amount,
            "nonce": w3.eth.get_transaction_count(acct.address),
            "chainId": int(chain["chain_id"]),
        }
        tx.update(build_fee_params(w3, chain))

        try:
            signed = acct.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
            status = receipt.get("status", 0)
            entry = {
                "ts": datetime.datetime.now(
                    datetime.timezone.utc).isoformat(),
                "chain": chain_name,
                "to": acct.address,
                "amount_wei": amount,
                "tx_hash": tx_hash.hex(),
                "status": status,
                "gas_used": receipt.get("gasUsed"),
            }
            append_log(log_path, entry)
            sent += 1
            state_today.setdefault(chain_name, {})["done"] = done + sent
            log(f"[{chain_name}] tx {done + sent}/{target}: "
                f"{tx_hash.hex()[:18]}… amount={amount} wei "
                f"status={status}")
        except Exception as e:
            log(f"[{chain_name}] tx failed: {str(e)[:150]} — stopping chain")
            break

        # random interval before next tx (not after the last one)
        if i < remaining - 1:
            wait = random.randint(int(cfg["interval_min_sec"]),
                                  int(cfg["interval_max_sec"]))
            log(f"[{chain_name}] sleeping {wait}s before next tx…")
            time.sleep(wait)

    return sent


def build_swap_plan(target):
    """Return a shuffled list of swap actions for the day.

    Each action is a tuple: ("hype_to_token", token_out, None),
    ("token_to_hype", token_in, None), or
    ("token_to_token", token_in, token_out).
    """
    plan = [
        ("hype_to_token", HEXSWAP_HEX, None),
        ("hype_to_token", HEXSWAP_HEX, None),
        ("hype_to_token", HEXSWAP_USDT, None),
        ("hype_to_token", HEXSWAP_USDT, None),
        ("token_to_hype", HEXSWAP_HEX, None),
        ("token_to_token", HEXSWAP_HEX, HEXSWAP_USDT),
        ("token_to_hype", HEXSWAP_USDT, None),
    ]
    plan = plan[:max(0, int(target))]
    random.shuffle(plan)
    return plan


def do_one_self_transfer(w3, acct, chain, cfg, state_today,
                         log_path, chain_name, dry_run=False):
    """Execute a single self-transfer. Returns True if sent."""
    if dry_run:
        amount = random.randint(int(cfg["amount_min_wei"]),
                                int(cfg["amount_max_wei"]))
        log(f"[{chain_name}] DRY-RUN self-transfer {amount} wei")
        return True
    min_bal = int(cfg["min_balance_wei"])
    try:
        balance = w3.eth.get_balance(acct.address)
    except Exception as e:
        log(f"[{chain_name}] balance check failed: {str(e)[:80]}")
        return False
    if balance < min_bal:
        log(f"[{chain_name}] LOW BALANCE — stopping")
        return False
    amount = random.randint(int(cfg["amount_min_wei"]),
                            int(cfg["amount_max_wei"]))
    tx = {
        "to": acct.address,
        "value": amount,
        "nonce": w3.eth.get_transaction_count(acct.address),
        "chainId": int(chain["chain_id"]),
    }
    tx.update(build_fee_params(w3, chain))
    try:
        signed = acct.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        status = receipt.get("status", 0)
        append_log(log_path, {
            "ts": datetime.datetime.now(
                datetime.timezone.utc).isoformat(),
            "chain": chain_name,
            "kind": "self-transfer",
            "to": acct.address,
            "amount_wei": amount,
            "tx_hash": tx_hash.hex(),
            "status": status,
            "gas_used": receipt.get("gasUsed"),
        })
        log(f"[{chain_name}] self-transfer {tx_hash.hex()[:18]}… "
            f"amount={amount} wei status={status}")
        return status == 1
    except Exception as e:
        log(f"[{chain_name}] transfer failed: {str(e)[:150]}")
        return False


def do_one_swap_step(w3, acct, action, swap_cfg, chain_id,
                     log_path, dry_run=False):
    """Execute a single swap action tuple. Returns True if sent, 'skip'
    if skipped for empty token balance, False on failure."""
    kind = action[0]
    amt_min = int(swap_cfg.get("amount_min_hype_wei", 5 * 10**14))
    amt_max = int(swap_cfg.get("amount_max_hype_wei", 2 * 10**15))
    if kind == "hype_to_token":
        amount = random.randint(amt_min, amt_max)
        ok = do_swap_hype_to_token(w3, acct, action[1], amount,
                                   chain_id, log_path, dry_run=dry_run)
        return bool(ok)
    if dry_run:
        # token->X dry-run path (no balance to check)
        if kind == "token_to_hype":
            return bool(do_swap_token_to_hype(
                None, acct, action[1], 10**16, chain_id,
                log_path, dry_run=True))
        return bool(do_swap_token_to_token(
            None, acct, action[1], action[2], 10**16, chain_id,
            log_path, dry_run=True))
    bal = get_token_balance(w3, action[1], acct.address)
    if bal == 0:
        tname = 'HEX' if action[1] == HEXSWAP_HEX else 'USDT'
        log(f"[elysium-swap] no {tname} balance — skipping this swap")
        return "skip"
    if kind == "token_to_hype":
        return bool(do_swap_token_to_hype(w3, acct, action[1], bal,
                                          chain_id, log_path))
    return bool(do_swap_token_to_token(w3, acct, action[1], action[2],
                                       bal, chain_id, log_path))


def farm_elysium_mixed(w3, acct, chain, swap_cfg, cfg, state_today,
                       log_path, dry_run=False):
    """Elysium daily farming: self-transfers + HexSwap swaps interleaved
    in random order. Returns total actions completed."""
    chain_id = int(chain["chain_id"])
    t_target = int(chain.get("tx_per_day", cfg["tx_per_day"]))
    t_done = int(state_today.get("elysium", {}).get("done", 0))
    s_target = int(swap_cfg.get("swaps_per_day", 7))
    s_done = int(state_today.get("elysium_swaps", {}).get("done", 0))
    t_rem = max(0, t_target - t_done)
    s_rem = max(0, s_target - s_done)

    if t_rem == 0 and s_rem == 0:
        log("[elysium] transfer + swap quotas already met, skipping")
        return 0

    if not dry_run:
        try:
            got = w3.eth.chain_id
        except Exception as e:
            log(f"[elysium] RPC unreachable: {str(e)[:100]} — skipping")
            return 0
        if got != chain_id:
            log(f"[elysium] chain id mismatch: got {got} — skipping")
            return 0

    # Interleaved action list: transfers and swaps in random order
    actions = (["xfer"] * t_rem) + (["swap"] * s_rem)
    random.shuffle(actions)
    swap_plan = build_swap_plan(s_rem)
    swap_idx = 0

    completed = 0
    for step, act in enumerate(actions):
        last = (step == len(actions) - 1)
        if act == "xfer":
            ok = do_one_self_transfer(w3, acct, chain, cfg, state_today,
                                      log_path, "elysium", dry_run=dry_run)
            if ok:
                t_done += 1
                state_today.setdefault("elysium", {})["done"] = t_done
                completed += 1
            else:
                log("[elysium] transfer failed/stopped — ending mixed run")
                break
        else:
            if swap_idx >= len(swap_plan):
                continue
            action = swap_plan[swap_idx]
            swap_idx += 1
            res = do_one_swap_step(w3, acct, action, swap_cfg, chain_id,
                                   log_path, dry_run=dry_run)
            if res == "skip":
                continue  # empty token balance: try next action
            if res:
                s_done += 1
                state_today.setdefault("elysium_swaps", {})["done"] = s_done
                completed += 1
            else:
                log("[elysium] swap failed — continuing to next action")
        if not last and not dry_run:
            wait = random.randint(int(cfg["interval_min_sec"]),
                                  int(cfg["interval_max_sec"]))
            log(f"[elysium] mixed progress "
                f"({completed}/{t_rem + s_rem}) — sleeping {wait}s…")
            time.sleep(wait)

    log(f"[elysium] mixed run done: {completed} actions "
        f"(transfers {t_done}/{t_target}, swaps {s_done}/{s_target})")
    return completed


def main():
    ap = argparse.ArgumentParser(description="daily auto-farm self-transfers")
    ap.add_argument("--config", default=CONFIG_FILE)
    ap.add_argument("--check", action="store_true",
                    help="print effective config and exit")
    ap.add_argument("--dry-run", action="store_true",
                    help="simulate without network or transactions")
    ap.add_argument("--chain", default=None,
                    help="farm only this chain (must exist in config)")
    ap.add_argument("--tx-per-day", type=int, default=None,
                    help="override per-chain daily quota")
    args = ap.parse_args()

    # proxy for every RPC call (requests honors these env vars too)
    os.environ.setdefault("http_proxy", PROXY)
    os.environ.setdefault("https_proxy", PROXY)

    cfg = load_config(args.config)
    log_path = os.path.join(BASE, cfg["log_file"])
    state_path = os.path.join(BASE, cfg["state_file"])

    if args.check:
        log("effective config:")
        log(json.dumps(cfg, indent=2))
        return 0

    if args.chain and args.chain not in cfg["chains"]:
        log(f"unknown chain {args.chain!r}; available: "
            f"{sorted(cfg['chains'])}")
        return 2

    # never log the key itself
    privkey = load_privkey()
    from eth_account import Account
    acct = Account.from_key(privkey)
    assert acct.address.lower() == FARMING_ADDRESS.lower(), \
        "privkey does not match farming wallet address"
    log(f"[*] wallet: {acct.address} (verified)")

    today = datetime.date.today().isoformat()
    state = load_state(state_path)
    state_today = state.setdefault(today, {})

    # prune old dates (keep 7 days)
    for d in sorted(state.keys()):
        if d < today and len([k for k in state if k <= today]) > 7:
            state.pop(d, None)

    chain_names = [n for n, c in cfg["chains"].items()
                   if c.get("enabled", True)]
    if args.chain:
        chain_names = [args.chain]
    random.shuffle(chain_names)  # natural ordering

    if not args.dry_run:
        ensure_forwarder()

    total = 0
    swap_cfg = cfg.get("elysium_swaps", {})
    swaps_enabled = bool(swap_cfg.get("enabled", False))
    for idx, name in enumerate(chain_names):
        chain = cfg["chains"][name]
        if args.tx_per_day is not None:
            chain = dict(chain, tx_per_day=args.tx_per_day)
        log(f"[*] === chain {name} (id {chain['chain_id']}) ===")
        w3 = None if args.dry_run else make_w3(chain["rpc"])
        if name == "elysium" and swaps_enabled:
            # Elysium: self-transfers + HexSwap swaps interleaved randomly
            total += farm_elysium_mixed(w3, acct, chain, swap_cfg, cfg,
                                        state_today, log_path,
                                        dry_run=args.dry_run)
        else:
            total += farm_chain(w3, acct, name, chain, cfg, state_today,
                                log_path, dry_run=args.dry_run)
        save_state(state_path, state)
        if idx < len(chain_names) - 1 and not args.dry_run:
            gap = random.randint(60, 300)
            log(f"[*] inter-chain gap: sleeping {gap}s…")
            time.sleep(gap)

    save_state(state_path, state)
    log(f"[*] done: {total} actions today across {len(chain_names)} chains")
    return 0


if __name__ == "__main__":
    sys.exit(main())
