const ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = (event) => {
  document.getElementById("clock").textContent = event.data;
};

ws.onopen = () => console.log("WebSocket connected");
ws.onclose = () => console.log("WebSocket closed");