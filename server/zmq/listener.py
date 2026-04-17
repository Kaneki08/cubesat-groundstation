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
HEADER_SIZE = 9

def decodeHeader(header_data):
    if len(header_data) < HEADER_SIZE:
        raise ValueError(f"Packet too short: {len(header_data)} < {HEADER_SIZE}")
    
    return {
        'sat_id': header_data[0].decode('utf-8', errors='ignore'),
        'packet_type': header_data[1].decode('utf-8', errors='ignore'),
        'sequence': header_data[2].decode('utf-8', errors='ignore'),
        'timestamp': header_data[3].decode('utf-8', errors='ignore'),
        'payload_len': header_data[4].decode('utf-8', errors='ignore')
    }

# @TODO: Need to edit this to check length of packet first for validity
def decodeContent(packet_data):
    return packet_data[10:29].decode('utf-8', errors='ignore')


def main():
    ctx = zmq.Context()

    # Create a SUB (subscriber) socket
    sub = ctx.socket(zmq.SUB)

    # Connect to GNU Radio PUB (publisher) socket; Make sure port # matches what's in loraRX.py
    sub.connect("tcp://127.0.0.1:6001")

    # IMPORTANT: Subscribe to all topics
    sub.setsockopt_string(zmq.SUBSCRIBE, "")

    print("Listening on port 6001...")

    # decodeHeader() and decodeContent() expects hex values
    while True:
        data = sub.recv()

        header = decodeHeader(data)
        text = decodeContent(data)
        print(header)
        print(text)

        payload = {
            "header": header,
            "content": text
        }

        try:
            r = requests.post(FASTAPI_URL, json=payload, timeout=5)
            print(f"Forwarded: {payload['hex']} -> {r.status_code}")
        except requests.RequestException as e:
            print(f"Failed to send to FastAPI: {e}")

if __name__ == "__main__":
    main()