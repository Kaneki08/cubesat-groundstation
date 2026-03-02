import asyncio
import json
import random
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
# IQ_PATH = BASE_DIR / "TestIQData.iq" # path to IQ file 
IQ_PATH = BASE_DIR / "test-noise-433.iq"
FFT_SIZE = 1024 # number of samples per FFT
HOP = FFT_SIZE # how far to move eahc fram
SEND_INTERVAL_S = 0.05 # 50 ms between each FFT packet sent to frontend

def make_fake_telemetry():
    """
    Generates one fake telemetry packet.
    Same structure you already use in the frontend.
    """
    return {
        "type": "telemetry",
        "timestamp": int(time.time()),
        "power": {
            "battery_voltage": round(random.uniform(7.2, 8.4), 2),
            "solar_current": round(random.uniform(0.0, 2.5), 2),
            "battery_temp_c": round(random.uniform(15.0, 35.0), 1),
        },
        "orientation": {
            "roll_deg": round(random.uniform(-10.0, 10.0), 1),
            "pitch_deg": round(random.uniform(-10.0, 10.0), 1),
            "yaw_deg": round(random.uniform(-180.0, 180.0), 1),
        },
        "radio": {
            "frequency_mhz": round(random.uniform(437.0, 437.5), 1),
            "rssi_dbm": random.randint(-120, -60),
            "snr_db": round(random.uniform(-5.0, 15.0), 1),
        },
        "mode": "downlink",
        "ground_station": "UCI",
    }

def load_iq_complex(path: str) -> np.ndarray:
    """
    reads interleaved float32 IQ: I0, Q0, I1, Q1, ...
    returns complex64 array: [I0 + jQ0, I1 + jQ1, ...]
    """
    raw = np.fromfile(path, dtype=np.float32)

    # Ensure even number of samples (I/Q pairs)
    raw = raw[: (raw.size // 2) * 2]

    i = raw[0::2]  # I samples
    q = raw[1::2]  # Q samples
    return (i + 1j * q).astype(np.complex64) # Convert to complex64 for smaller size

#load once at startup so we dont reread the file fro every WS message
IQ = load_iq_complex(IQ_PATH)
IQ_LEN = IQ.shape[0]

def spectrum_row(start_idx: int) -> np.ndarray:
    """
    Take FFT_SIZE complex samples starting at start_idx,
    run FFT, return half-spectrum magnitude in dB as float32 array.
    """
    x = IQ[start_idx : start_idx + FFT_SIZE]

    # Wrap-around if we hit end of file
    if x.size < FFT_SIZE:
        needed = FFT_SIZE - x.size
        x = np.concatenate([x, IQ[:needed]])

    X = np.fft.fft(x, n=FFT_SIZE)

    half = FFT_SIZE // 2
    mag = np.abs(X[:half]) + 1e-12       # avoid log(0)
    db = 20.0 * np.log10(mag)

    return db.astype(np.float32)


@app.get("/health")
def health():
    """
    Simple REST endpoint to check if the server is alive.
    """
    return {"status": "ok"}


@app.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket):
    """
    WebSocket endpoint that streams telemetry continuously.
    """
    await websocket.accept()

    try:
        while True:
            packet = make_fake_telemetry()
            await websocket.send_text(json.dumps(packet))
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Client disconnected")

@app.websocket("/ws/waterfall")
async def waterfall_ws(websocket: WebSocket):
    """
    Streams binary Float32 FFT rows for a waterfall plot.
    Each message = (FFT_SIZE/2) float32 values as raw bytes.
    """
    await websocket.accept()

    idx = 0
    try:
        while True:
            row = spectrum_row(idx)

            # advance pointer for next row
            idx = (idx + HOP) % IQ_LEN

            # send as bytes (frontend reads as Float32Array)
            await websocket.send_bytes(row.tobytes())

            await asyncio.sleep(SEND_INTERVAL_S)

    except WebSocketDisconnect:
        print("Waterfall client disconnected")


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
                "hint": "Run 'cd ui && npm run build' or use './dev.sh' from project root",
            },
        )

    requested = UI_DIST_DIR / full_path
    if full_path and requested.exists() and requested.is_file():
        return FileResponse(requested)

    return FileResponse(index_html)

