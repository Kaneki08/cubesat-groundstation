import asyncio
import json
import time
import numpy as np
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Create the FastAPI application object
app = FastAPI()

# Waterfall / IQ config parameters
BASE_DIR = Path(__file__).resolve().parent
UI_DIST_DIR = BASE_DIR.parent / "ui" / "dist"
IQ_PATH = BASE_DIR / "test-noise-433.iq"
FFT_SIZE = 1024
HOP = FFT_SIZE
SEND_INTERVAL_S = 0.05

# Latest raw packet from listener
latest_packet = {
    "received_at": None,
    "raw_hex": "",
    "header": {},
    "content": "",
    "decoded_fields": {}
}

# Latest telemetry shown to UI
latest_telemetry = {
    "type": "telemetry",
    "timestamp": 0,
    "power": {
        "battery_voltage": None,
        "solar_current": None,
        "battery_temp_c": None,
    },
    "orientation": {
        "roll_deg": None,
        "pitch_deg": None,
        "yaw_deg": None,
    },
    "radio": {
        "frequency_mhz": None,
        "rssi_dbm": None,
        "snr_db": None,
    },
    "mode": None,
    "ground_station": "UCI",
}

def load_iq_complex(path: str) -> np.ndarray:
    raw = np.fromfile(path, dtype=np.float32)
    raw = raw[: (raw.size // 2) * 2]

    i = raw[0::2]
    q = raw[1::2]
    return (i + 1j * q).astype(np.complex64)

# Load IQ once
IQ = load_iq_complex(IQ_PATH)
IQ_LEN = IQ.shape[0]

def spectrum_row(start_idx: int) -> np.ndarray:
    x = IQ[start_idx : start_idx + FFT_SIZE]

    if x.size < FFT_SIZE:
        needed = FFT_SIZE - x.size
        x = np.concatenate([x, IQ[:needed]])

    X = np.fft.fft(x, n=FFT_SIZE)

    half = FFT_SIZE // 2
    mag = np.abs(X[:half]) + 1e-12
    db = 20.0 * np.log10(mag)

    return db.astype(np.float32)

# Receive data from listener
@app.post("/ingest")
async def ingest(payload: dict):
    global latest_packet, latest_telemetry

    # Store raw packet
    latest_packet = {
        "received_at": int(time.time()), # Unix timestamp in seconds
        "raw_hex": payload.get("raw_hex", ""), # Optional: Store raw hex for debugging
        "header": payload.get("header", {}),  # Store decoded header fields
        "content": payload.get("content", ""), # Store decoded content string
        "decoded_fields": payload.get("decoded_fields", {}) # Optional: Store any additional decoded fields for future use
    }

    # Update telemetry timestamp
    latest_telemetry["timestamp"] = int(time.time())

    header = latest_packet["header"]
    content = latest_packet["content"]

    # Map header info
    latest_telemetry["mode"] = header.get("packet_type")

    # Parse content string like: battery=7.5,rssi=-75,snr=9.8
    if isinstance(content, str):
        parts = content.split(",")

        for part in parts:
            if "=" not in part:
                continue

            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key == "battery":
                latest_telemetry["power"]["battery_voltage"] = float(value)

            elif key == "rssi":
                latest_telemetry["radio"]["rssi_dbm"] = int(value)

            elif key == "snr":
                latest_telemetry["radio"]["snr_db"] = float(value)

    print("Updated telemetry:", latest_telemetry)

    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Send telemetry to dashboard
@app.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            await websocket.send_text(json.dumps(latest_telemetry))
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Telemetry client disconnected")

# Optional debug raw packet
@app.websocket("/ws/packet")
async def packet_ws(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            await websocket.send_text(json.dumps(latest_packet))
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Packet client disconnected")

# Waterfall stream
@app.websocket("/ws/waterfall")
async def waterfall_ws(websocket: WebSocket):
    await websocket.accept()

    idx = 0
    try:
        while True:
            row = spectrum_row(idx)
            idx = (idx + HOP) % IQ_LEN

            await websocket.send_bytes(row.tobytes())
            await asyncio.sleep(SEND_INTERVAL_S)

    except WebSocketDisconnect:
        print("Waterfall client disconnected")

# Serve UI
if (UI_DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=UI_DIST_DIR / "assets"), name="assets")

@app.get("/{full_path:path}")
def serve_ui(full_path: str):
    index_html = UI_DIST_DIR / "index.html"

    if not index_html.exists():
        return JSONResponse(
            status_code=503,
            content={
                "error": "UI build not found",
                "hint": "Run 'cd ui && npm run build'",
            },
        )

    requested = UI_DIST_DIR / full_path
    if full_path and requested.exists() and requested.is_file():
        return FileResponse(requested)

    return FileResponse(index_html)