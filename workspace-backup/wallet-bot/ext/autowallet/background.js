// AutoWallet background service worker
const ADDRESS = '0xf0f25C36AC70E9d787a108eFB351626192C8107b';
const SIGN_SERVER = 'http://127.0.0.1:18743/sign';

// RPC endpoints with failover. The browser routes through the egress proxy,
// so public RPCs work here. NOTE: rpc.sepolia.org is unreliable from the VM —
// publicnode is primary for Sepolia.
const RPCS = {
  '0x1': ['https://eth.llamarpc.com', 'https://ethereum-rpc.publicnode.com'],
  '0xaa36a7': ['https://ethereum-sepolia-rpc.publicnode.com', 'https://rpc.sepolia.org'],
  '0x61': ['https://data-seed-prebsc-1-s1.binance.org:8545', 'https://bsc-testnet-rpc.publicnode.com'],
  '0x38': ['https://bsc-dataseed.binance.org', 'https://bsc-rpc.publicnode.com'],
  '0x185d9': ['https://testnet-rpc.elysium.kinetiq.xyz'], // Elysium testnet 99801
  '0x3e6': ['https://rpc.hyperliquid-testnet.xyz/evm'], // HyperEVM testnet 998
  '0x5fdaf3': ['https://rpc.testnet.dogeos.com/'], // DogeOS testnet 6281971
};

async function getChainId() {
  const data = await chrome.storage.local.get(['chainId']);
  return data.chainId || '0x1';
}

// Persist the chain AND push it to every open tab so injected page providers
// update immediately (provider.chainId + chainChanged event).
async function setChainId(chainId) {
  await chrome.storage.local.set({ chainId });
  try {
    const tabs = await chrome.tabs.query({});
    await Promise.all((tabs || []).map((t) => {
      if (t.id == null) return Promise.resolve();
      // Tab may not have our content script; swallow the error.
      return chrome.tabs.sendMessage(t.id, { type: 'AUTOWALLET_CHAIN_CHANGED', chainId })
        .catch(() => {});
    }));
  } catch (e) { /* tabs API unavailable in some contexts */ }
}

async function getRpcUrls(chainId) {
  const key = 'rpc_' + chainId;
  const custom = await chrome.storage.local.get([key]);
  const urls = [];
  if (custom[key]) urls.push(custom[key]); // from wallet_addEthereumChain
  urls.push(...(RPCS[chainId] || RPCS['0x1']));
  return urls;
}

// POST to the chain's RPC with failover across endpoints.
async function rpcFetch(chainId, method, params) {
  const urls = await getRpcUrls(chainId);
  let lastErr = null;
  for (const url of urls) {
    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', id: Date.now(), method, params }),
      });
      const data = await resp.json();
      if (data.error) throw new Error(data.error.message || JSON.stringify(data.error));
      return data.result;
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr || new Error('AutoWallet: all RPCs failed for ' + chainId);
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (!msg || msg.type !== 'AUTOWALLET_REQUEST') return;

  (async () => {
    const { method, params } = msg;

    try {
      let result;
      const chainId = await getChainId();

      switch (method) {
        case 'eth_requestAccounts':
        case 'eth_accounts':
          result = [ADDRESS];
          break;

        case 'eth_chainId':
          result = chainId;
          break;

        case 'net_version':
          result = parseInt(chainId, 16).toString();
          break;

        case 'wallet_switchEthereumChain': {
          const newChain = params && params[0] && params[0].chainId;
          if (!newChain) throw new Error('AutoWallet: missing chainId');
          await setChainId(newChain);
          result = null;
          break;
        }

        case 'wallet_addEthereumChain': {
          const p = (params && params[0]) || {};
          if (!p.chainId) throw new Error('AutoWallet: missing chainId');
          // Remember a custom RPC if the dApp supplied one.
          if (p.rpcUrls && p.rpcUrls[0]) {
            const key = 'rpc_' + p.chainId;
            await chrome.storage.local.set({ [key]: p.rpcUrls[0] });
          }
          await setChainId(p.chainId);
          result = null;
          break;
        }

        // Read-only calls proxied to the active chain's RPC.
        case 'eth_call':
        case 'eth_getBalance':
        case 'eth_blockNumber':
        case 'eth_gasPrice':
        case 'eth_getTransactionCount':
        case 'eth_getCode':
        case 'eth_estimateGas':
        case 'eth_getBlockByNumber':
        case 'eth_getTransactionReceipt':
        case 'eth_getTransactionByHash':
          result = await rpcFetch(chainId, method, params);
          break;

        // Sign + broadcast via local signing server.
        case 'eth_sendTransaction': {
          const txParams = Object.assign({}, params[0]);
          if (!txParams.nonce) {
            txParams.nonce = await rpcFetch(chainId, 'eth_getTransactionCount', [ADDRESS, 'pending']);
          }
          if (!txParams.chainId) txParams.chainId = chainId;
          txParams.from = ADDRESS;
          const signResp = await fetch(SIGN_SERVER, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tx: txParams }),
          });
          const signData = await signResp.json();
          if (signData.error) throw new Error('AutoWallet: sign failed: ' + signData.error);
          result = await rpcFetch(chainId, 'eth_sendRawTransaction', [signData.signedTx]);
          break;
        }

        case 'personal_sign':
        case 'eth_sign':
          throw new Error('AutoWallet: message signing not implemented yet.');

        case 'eth_signTypedData':
        case 'eth_signTypedData_v3':
        case 'eth_signTypedData_v4':
          throw new Error('AutoWallet: typed data signing not implemented yet.');

        default:
          // Best-effort proxy for anything else.
          try {
            result = await rpcFetch(chainId, method, params);
          } catch (e) {
            throw new Error('AutoWallet: unsupported method ' + method);
          }
      }

      sendResponse({ result });
    } catch (e) {
      sendResponse({ error: (e && e.message) || String(e) });
    }
  })();

  return true; // keep channel open for async
});
