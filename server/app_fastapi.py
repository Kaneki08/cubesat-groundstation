import asyncio
import json
import random
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# Create the FastAPI application object
app = FastAPI()


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
