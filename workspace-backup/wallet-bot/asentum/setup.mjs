import { AsentumClient, AsentumWallet, formatAse } from '@asentum/sdk';
import fs from 'fs';

const RPCS = ['https://testnet.asentum.com', 'https://explorer.asentum.com'];

let client = null;
for (const rpc of RPCS) {
  try {
    const c = new AsentumClient(rpc);
    const bn = await c.getBlockNumber();
    console.log(`RPC OK: ${rpc} (block ${bn})`);
    client = c;
    break;
  } catch (e) {
    console.log(`RPC FAIL: ${rpc}: ${e.message}`);
  }
}
if (!client) { console.error('NO RPC AVAILABLE'); process.exit(1); }

// Create new native wallet
const wallet = AsentumWallet.create(client);
console.log('address:', wallet.address);

// Save (600) — user-authorized storage
const data = {
  address: wallet.address,
  secretKeyHex: wallet.secretKeyHex,
  publicKeyHex: wallet.publicKeyHex,
  rpc: client.rpcUrl || 'https://testnet.asentum.com',
  created: new Date().toISOString(),
  network: 'asentum-testnet',
};
fs.writeFileSync(process.env.HOME + '/workspace/wallet-bot/.asentum-wallet.json', JSON.stringify(data, null, 2), { mode: 0o600 });
console.log('saved to ~/.asentum-wallet.json (600)');

// Faucet
console.log('requesting faucet...');
try {
  const faucetTx = await wallet.requestFaucet();
  console.log('faucet result:', JSON.stringify(faucetTx).slice(0, 300));
} catch (e) {
  console.log('faucet error:', e.message);
}

// Balance
await new Promise(r => setTimeout(r, 5000));
const bal = await wallet.getBalance();
console.log('balance (wei):', bal.toString());
console.log('balance (ASE):', formatAse(bal));
