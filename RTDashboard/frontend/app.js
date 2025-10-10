const statusDiv = document.getElementById("status");

// SSE connection
const eventSource = new EventSource("/sse");
eventSource.onmessage = (event) => {
  statusDiv.textContent = `🔄 Status: ${event.data}`;
};

// WebSocket fallback (optional)
const socket = new WebSocket("wss://https://rtsignalrfree.service.signalr.net");
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  statusDiv.textContent = `⚡ Status: ${data.text}`;
};