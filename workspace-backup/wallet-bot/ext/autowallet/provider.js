// AutoWallet provider - injected into page context
(function() {
  const ADDRESS = '0xf0f25C36AC70E9d787a108eFB351626192C8107b';
  let chainId = '0x1'; // synced from background on load; updated on chainChanged

  const provider = {
    isMetaMask: true, // Pretend to be MetaMask for compatibility
    isAutoWallet: true,
    selectedAddress: ADDRESS,
    chainId: chainId,
    _events: {},

    request: async ({method, params}) => {
      // Forward to background script
      return new Promise((resolve, reject) => {
        const id = Math.random().toString(36).slice(2);
        const handler = (event) => {
          if (event.data && event.data.type === 'AUTOWALLET_RESPONSE' && event.data.id === id) {
            window.removeEventListener('message', handler);
            if (event.data.error) reject(new Error(event.data.error));
            else resolve(event.data.result);
          }
        };
        window.addEventListener('message', handler);
        window.postMessage({type: 'AUTOWALLET_REQUEST', id, method, params}, '*');
        // Timeout after 60s
        setTimeout(() => {
          window.removeEventListener('message', handler);
          reject(new Error('AutoWallet request timeout'));
        }, 60000);
      });
    },

    on: (event, callback) => {
      provider._events[event] = provider._events[event] || [];
      provider._events[event].push(callback);
    },
    removeListener: (event, callback) => {
      if (provider._events[event]) {
        provider._events[event] = provider._events[event].filter(cb => cb !== callback);
      }
    },
    // Legacy support
    send: (method, params) => provider.request({method, params}),
    sendAsync: (payload, callback) => {
      provider.request({method: payload.method, params: payload.params})
        .then(result => callback(null, {jsonrpc: '2.0', id: payload.id, result}))
        .catch(err => callback(err, null));
    },
    enable: () => provider.request({method: 'eth_requestAccounts', params: []}),
  };

  // Apply a new chainId locally and emit EIP-1193 chainChanged.
  function applyChainId(id) {
    if (!id || id === chainId) return;
    chainId = id;
    provider.chainId = id;
    (provider._events['chainChanged'] || []).slice().forEach((cb) => {
      try { cb(id); } catch (e) {}
    });
  }

  // Sync the persisted chain from the background on load. This fixes the
  // "chain resets to 0x1" bug: the MV3 service worker may restart and the
  // page context is fresh, so we always read the stored chainId.
  provider.request({method: 'eth_chainId', params: []})
    .then(applyChainId)
    .catch(() => {});

  // Background broadcasts chain switches -> update immediately.
  window.addEventListener('message', (event) => {
    if (event.source !== window) return;
    if (event.data && event.data.type === 'AUTOWALLET_CHAIN_CHANGED' && event.data.chainId) {
      applyChainId(event.data.chainId);
    }
  });

  // Inject as window.ethereum
  window.ethereum = provider;

  // Announce provider
  window.dispatchEvent(new Event('ethereum#initialized'));
})();
