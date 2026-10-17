#!/usr/bin/env python3
"""Airdrop farming orchestrator — testnet.

Reads projects.json, logs planned actions for each project.
Actual dApp interactions (faucet claims, swaps, stakes) require a live
browser with wallet signing; those are delegated to the parent agent via
browser tasks. This script handles scheduling, logging, and status tracking.

Usage:
    python3 farm.py [--check-only] [--project <id>]

Wallet private key is NEVER stored here. It is supplied via Secure Vault
at transaction time by the parent agent.
"""
import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
WIB = timezone(timedelta(hours=7))


def load_projects():
    with open(BASE / "projects.json") as f:
        return json.load(f)


def log(msg, logfile):
    ts = datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts} WIB] {msg}"
    print(line)
    logfile.write(line + "\n")
    logfile.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true",
                    help="Only report status, don't queue actions")
    ap.add_argument("--project", default=None,
                    help="Only process this project id")
    args = ap.parse_args()

    data = load_projects()
    wallet = data["wallet_address"]
    projects = data["projects"]
    if args.project:
        projects = [p for p in projects if p["id"] == args.project]
        if not projects:
            print(f"Unknown project: {args.project}", file=sys.stderr)
            return 1

    logdir = BASE / "logs"
    logdir.mkdir(exist_ok=True)
    today = datetime.now(WIB).strftime("%Y-%m-%d")
    lf = open(logdir / f"farm-{today}.log", "a")

    log(f"=== Farm run start (wallet {wallet}) ===", lf)
    queued = []
    blocked = []
    for p in projects:
        faucet = p.get("faucet", {})
        needs_captcha = faucet.get("needs_captcha", False)
        needs_social = faucet.get("needs_social")
        needs_mainnet = faucet.get("needs_mainnet_balance")
        if needs_captcha or needs_social:
            reasons = []
            if needs_captcha:
                reasons.append("captcha")
            if needs_social:
                reasons.append(f"social:{needs_social}")
            if needs_mainnet:
                reasons.append(f"mainnet-balance:{needs_mainnet}")
            blocked.append((p["id"], ", ".join(reasons)))
            log(f"BLOCKED {p['id']} ({p['name']}): faucet needs "
                f"{', '.join(reasons)} — manual step required", lf)
        else:
            queued.append(p["id"])
            log(f"QUEUED  {p['id']} ({p['name']}): {p['frequency']} — "
                f"dapp: {p.get('dapp_url')}", lf)

    log(f"=== Summary: {len(queued)} queued, {len(blocked)} blocked ===", lf)
    for pid, reason in blocked:
        log(f"  blocked: {pid} [{reason}]", lf)
    log("=== Farm run end ===", lf)
    lf.close()

    # Machine-readable summary for the parent agent
    summary = {
        "date": today,
        "wallet": wallet,
        "queued": queued,
        "blocked": [{"id": pid, "reason": r} for pid, r in blocked],
        "note": "Queued projects still need live-browser dApp interaction "
                "by the parent agent (wallet signing).",
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
