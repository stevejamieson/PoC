import os
from azure.signalr import SignalRClient

client = SignalRClient(connection_string=os.getenv("AZURE_SIGNALR_CONNECTION_STRING"))

async def broadcast_to_signalr(message: str):
    await client.send("statusHub", "newStatus", {"text": message})