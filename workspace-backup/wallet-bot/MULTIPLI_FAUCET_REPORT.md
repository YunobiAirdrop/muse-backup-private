# Multipli Testnet Faucet — Investigation Report

## Summary
**Status: BLOCKED** — The Multipli testnet faucet (USDC/USDT/BTC) cannot be claimed via pure RPC automation due to StarkNet-based authentication + reCAPTCHA requirements.

## What I Found

### Faucet Mechanism (API-based, NOT contract-based)
- **Endpoint**: `POST https://api-testnet.multipli.fi/multipli/v1/distribute-tokens/`
- **Auth**: Requires JWT (`Authorization: JWT <token>`)
- **Params**: `{"currency": "usdc"}` (or "usdt", "btc")
- **Check**: `GET /is-token-distributed/?currency=usdc` (also needs JWT)

### Auth Flow (Discovered)
1. **Get nonce**: `POST /multipli/v1/auth/nonce/` with `{"eth_address": "0x..."}`
   - ✅ WORKS — Returns: `"You're now signing into Multipli. Make sure the origin is https://testnet.multipli.fi (Login-code:XXX)"`
2. **Sign nonce**: With Ethereum private key (EIP-191 personal_sign)
   - ✅ WORKS — I signed it successfully with the farming wallet key
3. **Submit signature**: ??? — **NO WORKING ENDPOINT FOUND**
   - Tried: `/auth/login/`, `/auth/verify/`, `/auth/token/`, `/auth/confirm/` — all 404
   - The JS bundle references `/auth/login/` but it's not on the testnet API

### Full Signup Requirements (from `/wallet/signup/deterministic/`)
If the wallet is not registered, signup requires:
- `wallet_address` (Ethereum address)
- `dynamic_message_signature` (Ethereum signature)
- `stark_public_key` (StarkNet public key — **requires StarkEx key derivation from ETH key**)
- `static_message_signature` (another signature)
- `recaptcha_token` (**cannot be solved programmatically reliably**)

### Wallet Check Requirements
`POST /multipli/v1/auth/wallet-check/` requires:
- `eth_address`
- `user_signature`
- `stark_key` (StarkNet key)

## The Blocker
Multipli is built on **StarkEx (Brine)**. The authentication requires:
1. **StarkNet key derivation** — A StarkNet public/private keypair derived from the Ethereum key via StarkEx-specific algorithm. This is non-trivial and Brine-specific.
2. **reCAPTCHA** — The signup requires a valid reCAPTCHA token, which cannot be generated programmatically.

Even with the Ethereum private key, I cannot:
- Derive the correct StarkNet key (Brine-specific algorithm)
- Solve the reCAPTCHA

## Current Balances (verified via BSC Testnet RPC)
- **tBNB**: 0.010001 (sufficient for gas)
- **USDC (testnet)**: 0 (faucet not claimed)
- **USDT (testnet)**: 0 (faucet not claimed)
- **BTC (testnet)**: 0 (faucet not claimed)

## Recommendation
**Option A (Fastest)**: User claims the faucet manually on their phone:
1. Open `https://testnet.multipli.fi/?referral_code=6RUTJ` in MetaMask mobile browser
2. Connect wallet (already imported)
3. Complete signup (solves reCAPTCHA on phone)
4. Claim USDC/USDT/BTC from faucet UI
5. Time: ~2-3 minutes

**Option B**: Skip Multipli for now. The platform requires full StarkNet account setup which is not automatable. Focus on other opportunities (Elysium, Psy, Kalos) that don't have these barriers.

**Option C**: If the user has ALREADY signed up for Multipli (via phone), they can provide the JWT from their browser's localStorage, and I can use it to call the faucet API directly.

## Files
- `/tmp/multipli.js` — Downloaded JS bundle (3.9MB) for analysis
- `~/workspace/wallet-bot/find_faucet.py` — Faucet discovery script
- `~/workspace/wallet-bot/observe_auth.py` — Auth flow observer
- `/tmp/multipli_sig.txt` — Signed nonce (for reference)
