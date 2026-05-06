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

# Packet type IDs (must match listener.py PacketType enum)
PACKET_IMU = 1
PACKET_TC  = 2
PACKET_BATT = 3  # update this int to match actual PacketType value

# Latest raw packet from listener
latest_packet = {
    "received_at": None,
    "header": {},
    "content": {},
}

# Latest telemetry shown to UI — all fields present so UI never gets KeyError
latest_telemetry = {
    "type": "telemetry",
    "timestamp": 0,
    "packet_type": None,   # "IMU" | "BATT" | "TC" — lets UI know which card is fresh

    # --- IMU packet (PACKET_IMU = 1) ---
    "imu": {
        # Gyroscope (raw int16, units: degrees/s)
        "gx_dps": None,
        "gy_dps": None,
        "gz_dps": None,
        # Accelerometer (raw int16, units: milli-g)
        "ax_mg": None,
        "ay_mg": None,
        "az_mg": None,
        # Quaternion (raw int16, scale TBD by firmware)
        "qi": None,
        "qj": None,
        "qk": None,
        "qr": None,
    },

    # --- Battery packet (PACKET_BATT / batt_combined_telemetry_1, 38 bytes) ---
    "battery": {
        "current_mA": None,
        "avg_current_mA": None,
        "voltage_mV": None,
        "average_voltage_mV": None,
        "cycle_count": None,
        # Temperatures in 0.1 K units from firmware; converted to °C on ingest
        "temperature_c": None,           # onboard cell temp
        "ext_temp1_c": None,
        "ext_temp2_c": None,
        "ext_temp3_c": None,
        "ext_temp4_c": None,
        "ext_temp5_c": None,
        "ext_temp6_c": None,
        "ext_temp7_c": None,
        "ext_temp8_c": None,
        # Individual cell voltages (mV)
        "cell_voltage1_mV": None,
        "cell_voltage2_mV": None,
        "cell_voltage3_mV": None,
        "cell_voltage4_mV": None,
    },

    # --- Thermocouple packet (PACKET_TC = 2, 8 bytes) ---
    "tc": {
        "tc_avg1": None,   # float, °C (or raw — match firmware)
        "tc_avg2": None,
    },

    "ground_station": "UCI",
}


def kelvin_01_to_celsius(val_01K: int) -> float:
    """Convert firmware 0.1 K units → °C  (e.g. 2981 → 25.0 °C)"""
    return round(val_01K / 10.0 - 273.15, 2)


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


# ---------------------------------------------------------------------------
# /ingest  — called by listener.py after it decodes a packet
#
# Expected JSON body from listener.py:
# {
#   "header": { "sat_id": int, "packet_type": int, "sequence": int,
#               "timestamp": int, "payload_len": int },
#   "content": { ... }   ← dict from decode_content()
# }
# ---------------------------------------------------------------------------
@app.post("/ingest")
async def ingest(payload: dict):
    global latest_packet, latest_telemetry

    header  = payload.get("header", {})
    content = payload.get("content", {})

    latest_packet = {
        "received_at": int(time.time()),
        "header": header,
        "content": content,
    }

    latest_telemetry["timestamp"]   = int(time.time())
    latest_telemetry["packet_type"] = header.get("packet_type")

    ptype = header.get("packet_type")

    # ---- IMU packet --------------------------------------------------------
    if ptype == PACKET_IMU and isinstance(content, dict):
        latest_telemetry["imu"] = {
            "gx_dps": content.get("gx_dps"),
            "gy_dps": content.get("gy_dps"),
            "gz_dps": content.get("gz_dps"),
            "ax_mg":  content.get("ax_mg"),
            "ay_mg":  content.get("ay_mg"),
            "az_mg":  content.get("az_mg"),
            "qi":     content.get("qi"),
            "qj":     content.get("qj"),
            "qk":     content.get("qk"),
            "qr":     content.get("qr"),
        }

    # ---- Battery packet ----------------------------------------------------
    elif ptype == PACKET_BATT and isinstance(content, dict):
        def c(key): return content.get(key)
        def k01(key):
            v = content.get(key)
            return kelvin_01_to_celsius(v) if v is not None else None

        latest_telemetry["battery"] = {
            "current_mA":         c("current_mA"),
            "avg_current_mA":     c("avg_current_mA"),
            "voltage_mV":         c("voltage_mV"),
            "average_voltage_mV": c("average_voltage_mV"),
            "cycle_count":        c("cycle_count"),
            "temperature_c":      k01("temperature_0_1K"),
            "ext_temp1_c":        k01("external_temp_sensor1_0_1K"),
            "ext_temp2_c":        k01("external_temp_sensor2_0_1K"),
            "ext_temp3_c":        k01("external_temp_sensor3_0_1K"),
            "ext_temp4_c":        k01("external_temp_sensor4_0_1K"),
            "ext_temp5_c":        k01("external_temp_sensor5_0_1K"),
            "ext_temp6_c":        k01("external_temp_sensor6_0_1K"),
            "ext_temp7_c":        k01("external_temp_sensor7_0_1K"),
            "ext_temp8_c":        k01("external_temp_sensor8_0_1K"),
            "cell_voltage1_mV":   c("cell_voltage1_mV"),
            "cell_voltage2_mV":   c("cell_voltage2_mV"),
            "cell_voltage3_mV":   c("cell_voltage3_mV"),
            "cell_voltage4_mV":   c("cell_voltage4_mV"),
        }

    # ---- Thermocouple packet -----------------------------------------------
    elif ptype == PACKET_TC and isinstance(content, dict):
        latest_telemetry["tc"] = {
            "tc_avg1": content.get("tc_avg1"),
            "tc_avg2": content.get("tc_avg2"),
        }

    else:
        print(f"[ingest] Unknown or malformed packet_type={ptype}, content={content}")

    print("Updated telemetry:", latest_telemetry)
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


# Send full telemetry blob to dashboard
@app.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_text(json.dumps(latest_telemetry))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Telemetry client disconnected")


# Debug: raw packet
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
            content={"error": "UI build not found", "hint": "Run 'cd ui && npm run build'"},
        )
    requested = UI_DIST_DIR / full_path
    if full_path and requested.exists() and requested.is_file():
        return FileResponse(requested)
    return FileResponse(index_html)