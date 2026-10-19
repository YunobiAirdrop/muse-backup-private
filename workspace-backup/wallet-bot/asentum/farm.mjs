// Run AFTER faucet is claimed. Does 2 self-transfers for XP (first tx = 100 XP).
import { AsentumClient, AsentumWallet, formatAse } from '@asentum/sdk';
import fs from 'fs';

const w = JSON.parse(fs.readFileSync(process.env.HOME + '/workspace/wallet-bot/.asentum-wallet.json', 'utf8'));
const client = new AsentumClient(w.rpc || 'https://testnet.asentum.com');
const wallet = AsentumWallet.fromSecretKey(client, w.secretKeyHex, w.publicKeyHex);

let bal = await wallet.getBalance();
console.log('balance:', formatAse(bal), 'ASE');
if (bal === 0n) { console.log('NO FUNDS — claim faucet first via airdrop.asentum.com'); process.exit(2); }

for (let i = 1; i <= 2; i++) {
  const tx = await wallet.sendTransfer({ to: wallet.address, amount: '0.01' });
  const receipt = await tx.wait();
  console.log(`tx${i} confirmed in block`, receipt.blockNumber);
}
bal = await wallet.getBalance();
console.log('final balance:', formatAse(bal), 'ASE');
