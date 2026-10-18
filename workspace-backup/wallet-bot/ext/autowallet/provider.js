// AutoWallet provider - injected into page
(function() {
  const ADDRESS = '0xf0f25C36AC70E9d787a108eFB351626192C8107b';
  let chainId = '0x1'; // default, can be switched

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

  // Inject as window.ethereum
  if (!window.ethereum) {
    window.ethereum = provider;
  } else {
    // If MetaMask already exists, override it
    window.ethereum = provider;
  }

  // Announce provider
  window.dispatchEvent(new Event('ethereum#initialized'));
})();
