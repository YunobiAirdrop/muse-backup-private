# Airdrop testnet farming automation

Goal ID: goal_ab070d2583e5
Goal slug: airdrop-testnet-farming-automation

## Description
Yunobi asked the assistant to farm testnet airdrops as automatically as possible: a fresh dedicated wallet (0xf0f25C36AC70E9d787a108eFB351626192C8107b) was created and 7 projects selected (GTE on MegaETH, Neptune Protocol, Variational, Plaza Finance, Zenchain, Sahara AI, Multipli.fi), targeting 5-10 varied daily transactions per project after Yunobi warned that low transaction counts made him ineligible in past airdrops. Faucet claims stay manual (captchas and mainnet-balance requirements block automation) while automated dApp interactions run daily, and mainnet/TGE announcements are monitored every Monday and Thursday with alerts to Yunobi. SepETH mining runs on 10 wallets via sepolia-faucet.pk910.de in 12-hour sessions; on 17 Oct the main wallet's session got stuck on the faucet server while 9 others mined normally, and the stuck session expires within 12 hours.
