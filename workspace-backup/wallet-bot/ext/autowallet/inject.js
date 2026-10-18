// Inject provider.js into page context
const script = document.createElement('script');
script.src = chrome.runtime.getURL('provider.js');
script.onload = function() { this.remove(); };
(document.head || document.documentElement).appendChild(script);

// Relay messages between page and background
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
        result: response?.result,
        error: response?.error
      }, '*');
    });
  }
});
