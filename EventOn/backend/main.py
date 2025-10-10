from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi_sse import EventSourceResponse
from signalr_client import broadcast_to_signalr
from sse_manager import sse_manager

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Real-time backend is running"}

@app.get("/sse")
async def sse_endpoint(request: Request):
    return EventSourceResponse(sse_manager.stream(request))

@app.post("/update-status")
async def update_status(payload: dict):
    status = payload.get("status")
    await broadcast_to_signalr(status)
    await sse_manager.push(status)
    return {"message": "Status broadcasted"}