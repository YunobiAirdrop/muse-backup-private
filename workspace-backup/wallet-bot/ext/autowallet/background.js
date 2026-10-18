// AutoWallet background service worker
const ADDRESS = '0xf0f25C36AC70E9d787a108eFB351626192C8107b';

// Use storage for chainId persistence across service worker restarts
async function getChainId() {
  const data = await chrome.storage.local.get(['chainId']);
  return data.chainId || '0x1';
}
async function setChainId(chainId) {
  await chrome.storage.local.set({chainId});
}

// RPC URLs for chain ID lookup (for eth_call, etc. if needed)
const RPCS = {
  '0x1': 'https://eth.llamarpc.com',
  '0xaa36a7': 'https://rpc.sepolia.org', // Sepolia 11155111
  '0x61': 'https://data-seed-prebsc-1-s1.binance.org:8545', // BSC Testnet 97
  '0x38': 'https://bsc-dataseed.binance.org', // BSC Mainnet 56
  '0x26571': 'https://testnet-rpc.elysium.kinetiq.xyz', // Elysium 99801
  '0x3e6': 'https://rpc.hyperliquid-testnet.xyz/evm', // HyperEVM 998
};

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type !== 'AUTOWALLET_REQUEST') return;

  (async () => {
    const {method, params} = msg;

    try {
      let result;

      switch (method) {
        case 'eth_requestAccounts':
        case 'eth_accounts':
          result = [ADDRESS];
          break;

        case 'eth_chainId':
          result = (await getChainId());
          break;

        case 'net_version':
          result = parseInt((await getChainId()), 16).toString();
          break;

        case 'wallet_switchEthereumChain': {
          const newChain = params[0]?.chainId;
          if (newChain) {
            await setChainId(newChain);
            result = null;
          } else {
            throw new Error('Missing chainId');
          }
          break;
        }

        case 'wallet_addEthereumChain': {
          const newChain = params[0]?.chainId;
          if (newChain) {
            await setChainId(newChain);
            result = null;
          } else {
            throw new Error('Missing chainId');
          }
          break;
        }

        // For read-only calls, proxy to RPC
        case 'eth_call':
        case 'eth_getBalance':
        case 'eth_blockNumber':
        case 'eth_gasPrice':
        case 'eth_getTransactionCount':
        case 'eth_getCode':
        case 'eth_estimateGas': {
          const rpc = RPCS[(await getChainId())] || RPCS['0x1'];
          const resp = await fetch(rpc, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({jsonrpc: '2.0', id: 1, method, params})
          });
          const data = await resp.json();
          if (data.error) throw new Error(data.error.message);
          result = data.result;
          break;
        }

        // Signing methods - via local signing server
        case 'eth_sendTransaction': {
          const txParams = params[0];
          // Get nonce if not provided
          if (!txParams.nonce) {
            const rpc = RPCS[(await getChainId())] || RPCS['0x1'];
            const nonceResp = await fetch(rpc, {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({jsonrpc: '2.0', id: 1, method: 'eth_getTransactionCount', params: [ADDRESS, 'pending']})
            });
            const nonceData = await nonceResp.json();
            txParams.nonce = nonceData.result;
          }
          // Ensure chainId
          if (!txParams.chainId) {
            txParams.chainId = (await getChainId());
          }
          // Ensure from
          txParams.from = ADDRESS;
          // Sign via local server
          const signResp = await fetch('http://127.0.0.1:18743/sign', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({tx: txParams})
          });
          const signData = await signResp.json();
          if (signData.error) throw new Error('Sign failed: ' + signData.error);
          // Broadcast via RPC
          const rpc = RPCS[(await getChainId())] || RPCS['0x1'];
          const sendResp = await fetch(rpc, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({jsonrpc: '2.0', id: 1, method: 'eth_sendRawTransaction', params: [signData.signedTx]})
          });
          const sendData = await sendResp.json();
          if (sendData.error) throw new Error(sendData.error.message);
          result = sendData.result; // tx hash
          break;
        }

        case 'personal_sign':
        case 'eth_sign':
          throw new Error('AutoWallet: Message signing not implemented yet.');

        case 'eth_signTypedData':
        case 'eth_signTypedData_v3':
        case 'eth_signTypedData_v4':
          throw new Error('AutoWallet: Typed data signing not implemented yet.');

        default:
          // Try to proxy unknown methods to RPC
          const rpc = RPCS[(await getChainId())] || RPCS['0x1'];
          try {
            const resp = await fetch(rpc, {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({jsonrpc: '2.0', id: 1, method, params})
            });
            const data = await resp.json();
            if (data.error) throw new Error(data.error.message);
            result = data.result;
          } catch (e) {
            throw new Error(`AutoWallet: Unsupported method ${method}`);
          }
      }

      sendResponse({result});
    } catch (e) {
      sendResponse({error: e.message});
    }
  })();

  return true; // Keep channel open for async
});
