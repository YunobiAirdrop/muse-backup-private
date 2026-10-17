#!/usr/bin/env python3
"""CLI for the OTPMurah.id REST API (https://otpmurah.id/api-docs).

Auth: stored connector `custom.otpmurah`, applied as X-API-Key header via
the dynamic_credentials surrogate helper. Never prints the raw key.

Subcommands:
  balance                  Check account balance (IDR)
  services                 List available services (codes)
  prices   --service CODE --country ID [--server s2|s1]
  get-number --service CODE [--country ID] [--server s2|s1]
                           Order a virtual number (POST). Deducts balance.
  status   --id ACTIVATION_ID
                           Check whether the OTP arrived (STATUS_WAIT_CODE / STATUS_OK)
  cancel   --id ACTIVATION_ID
                           Cancel activation; 100% refund if no OTP received.
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import (  # noqa: E402
    add_surrogate_to_request,
    read_json_response,
)

BASE = "https://otpmurah.id/api/"
CREDENTIAL = "custom.otpmurah"
HOSTS = ["otpmurah.id"]


def api(action, params=None, method="GET", data=None):
    q = {"action": action}
    q.update(params or {})
    url = BASE + "?" + urllib.parse.urlencode(q)
    body = urllib.parse.urlencode(data or {}).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    # Browser-like UA: Cloudflare (error 1010) blocks default Python-urllib UA
    req.add_header("User-Agent",
                   "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    req.add_header("Accept", "application/json")
    if body:
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    add_surrogate_to_request(req, CREDENTIAL, allowed_hosts=HOSTS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return read_json_response(resp)


def main():
    ap = argparse.ArgumentParser(description="OTPMurah.id API CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("balance")

    sub.add_parser("services")

    p = sub.add_parser("prices")
    p.add_argument("--service", default="go")
    p.add_argument("--country", default="6")
    p.add_argument("--server", default="s2")

    p = sub.add_parser("get-number")
    p.add_argument("--service", default="go",
                   help="Service code, e.g. go (Google), wa (WhatsApp)")
    p.add_argument("--country", default="6", help="Country ID, 6 = Indonesia")
    p.add_argument("--server", default="s2", help="s2 = Server Plus, s1 = Server Express")
    p.add_argument("--operator", default="any")

    p = sub.add_parser("status")
    p.add_argument("--id", required=True, dest="activation_id")

    p = sub.add_parser("cancel")
    p.add_argument("--id", required=True, dest="activation_id")

    args = ap.parse_args()

    try:
        if args.cmd == "balance":
            out = api("getBalance")
        elif args.cmd == "services":
            out = api("getServices")
        elif args.cmd == "prices":
            out = api("getPrices", {"service": args.service,
                                    "country": args.country,
                                    "server": args.server})
        elif args.cmd == "get-number":
            out = api("getNumber", method="POST", data={
                "service": args.service, "country": args.country,
                "operator": args.operator, "server": args.server})
        elif args.cmd == "status":
            out = api("getStatus", {"id": args.activation_id})
        elif args.cmd == "cancel":
            out = api("cancelActivation", method="POST",
                      data={"id": args.activation_id})
        print(json.dumps(out, indent=2, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")
            detail = json.loads(body)
        except Exception:  # noqa: BLE001
            detail = {"raw": body if "body" in dir() else ""}
        print(json.dumps({"success": False, "http": e.code,
                          "provider_error": detail}))
        sys.exit(1)
    except Exception as e:  # noqa: BLE001 - surface provider errors plainly
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
