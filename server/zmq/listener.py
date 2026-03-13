'''
DESCRIPTION: GNU Radio files will broadcast output as a ZMQ message. This
script will serve as the listerner that will suibscribe to this ZMQ message
and pull data to the server.
'''
import asyncio
import requests
import zmq
import numpy as np

FASTAPI_URL = "http://127.0.0.1/8000/ingest"

def main():
    ctx = zmq.Context()

    # Create a SUB (subscriber) socket
    sub = ctx.socket(zmq.SUB)

    # Connect to GNU Radio PUB (publisher) socket; Make sure port # matches what's in loraRX.py
    sub.connect("tcp://127.0.0.1:6001")

    # IMPORTANT: Subscribe to all topics
    sub.setsockopt_string(zmq.SUBSCRIBE, "")

    print("Listening on port 6001...")

    # Listerner is set to interperet raw IQ values. This might change upon further testing
    while True:
        data = sub.recv()

        payload = {
            "hex": " ".join(f"{b:02X}" for b in data),
            "length": len(data)
        }

        try:
            r = requests.post(FASTAPI_URL, json=payload, timeout=5)
            print(f"Forwarded: {payload['hex']} -> {r.status_code}")
        except requests.RequestException as e:
            print(f"Failed to send to FastAPI: {e}")

if __name__ == "__main__":
    main()