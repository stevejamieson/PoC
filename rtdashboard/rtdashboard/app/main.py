from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import requests
import os
import base64, hmac, hashlib, time
from urllib.parse import quote



app = FastAPI()
connected_clients = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in connected_clients:
                await client.send_text(f"[{websocket.client.host}] {data}")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

        
@app.get("/")
def read_root():
    return {"message": "Welcome to RTDashboard!"}

def broadcast_message(message: str):
    endpoint = "https://rtsignalrfree.service.signalr.net"
    hub_name = "dashboard"
    token = generate_signalr_token(endpoint, os.getenv("AZURE_SIGNALR_ACCESS_KEY"), hub_name)
    url = f"{endpoint}/api/v1/hubs/{hub_name}/messages"
    headers = {"Authorization": token}
    requests.post(url, json={"target": "newMessage", "arguments": [message]}, headers=headers)

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    with open("dashboard.html", "r") as f:
        return f.read()


@app.get("/negotiate")
def negotiate():
    endpoint = "https://rtsignalrfree.service.signalr.net"
    access_key = os.getenv("AZURE_SIGNALR_ACCESS_KEY")
    hub_name = "dashboard"
    token = generate_signalr_token(endpoint, access_key, hub_name)
    return {
        "accessToken": token,
        "url": f"{endpoint}/client/?hub={hub_name}"
    }


def generate_signalr_token(endpoint, access_key, hub_name, user_id=None):
    audience = f"{endpoint}/client/?hub={hub_name}"
    expiry = int(time.time()) + 3600  # 1 hour
    payload = f"{audience}\n{expiry}"
    signature = base64.b64encode(
        hmac.new(base64.b64decode(access_key), payload.encode(), hashlib.sha256).digest()
    ).decode()
    token = f"SharedAccessSignature sr={quote(audience)}&sig={quote(signature)}&se={expiry}"
    return token
