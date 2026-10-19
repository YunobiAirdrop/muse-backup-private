// Inject provider.js into page context
const script = document.createElement('script');
script.src = chrome.runtime.getURL('provider.js');
script.onload = function() { this.remove(); };
(document.head || document.documentElement).appendChild(script);

// Relay page -> background (dApp requests)
window.addEventListener('message', (event) => {
  if (event.source !== window) return;
  if (event.data && event.data.type === 'AUTOWALLET_REQUEST') {
    chrome.runtime.sendMessage({
      type: 'AUTOWALLET_REQUEST',
      id: event.data.id,
      method: event.data.method,
      params: event.data.params
    }, (response) => {
      window.postMessage({
        type: 'AUTOWALLET_RESPONSE',
        id: event.data.id,
        result: response && response.result,
        error: response && response.error
      }, '*');
    });
  }
});

// Relay background -> page (chain switches). The background service worker
// broadcasts AUTOWALLET_CHAIN_CHANGED to all tabs after wallet_switchEthereumChain
// / wallet_addEthereumChain; forward it so the injected provider updates
// provider.chainId immediately and emits the EIP-1193 chainChanged event.
chrome.runtime.onMessage.addListener((msg) => {
  if (msg && msg.type === 'AUTOWALLET_CHAIN_CHANGED') {
    window.postMessage({ type: 'AUTOWALLET_CHAIN_CHANGED', chainId: msg.chainId }, '*');
  }
});
