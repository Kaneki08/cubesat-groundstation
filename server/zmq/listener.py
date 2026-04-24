'''
DESCRIPTION: GNU Radio files will broadcast output as a ZMQ message. This
script will serve as the listerner that will suibscribe to this ZMQ message
and pull data to the server.
'''
import asyncio
import requests
import zmq
import numpy as np

FASTAPI_URL = "http://127.0.0.1:8000/ingest"
HEADER_SIZE = 10

timeout_ms = 1000

def decode_header(packet):
    if len(packet) < HEADER_SIZE:
        raise ValueError("Packet too short to contain full header")

    if packet[8:9] != b'$':
        raise ValueError("Missing $ marker in header")
    
    return {
        'sat_id': packet[0],
        'packet_type': packet[1],
        'sequence': int.from_bytes(packet[2:4], 'big'),
        'timestamp': int.from_bytes(packet[4:8], 'big'),
        'payload_len': packet[10]
    }

def decode_content(packet_data):
    return packet_data[HEADER_SIZE:]

def receive_once(sub):
    try:
        return sub.recv()
    except zmq.Again:
        return None
    
def main():
    ctx = zmq.Context()

    # Create a SUB (subscriber) socket
    sub = ctx.socket(zmq.SUB)

    # Connect to GNU Radio PUB (publisher) socket; Make sure port # matches what's in loraRX.py
    sub.connect("tcp://127.0.0.1:6001")

    # IMPORTANT: Subscribe to all topics
    sub.setsockopt_string(zmq.SUBSCRIBE, "")

    sub.setsockopt(zmq.RCVTIMEO, timeout_ms)

    print("Listening on port 6001...")

    # decode_header() and decode_content() expects hex values
    while True:
        data = sub.recv()

        header = decode_header(data)
        text = decode_content(data).decode("utf-8", errors="ignore")
        print(header)
        print(text)

        payload = {
            "header": header,
            "content": text
        }

        try:
            r = requests.post(FASTAPI_URL, json=payload, timeout=5)
        except requests.RequestException as e:
            print(f"Failed to send to FastAPI: {e}")

if __name__ == "__main__":
    main()

class HeartbeatMonitor:
    HEARTBEAT_TYPE = 0xAA

    def __init__(self):
        self.count = 0;
        self.last_seq = None;

    def process_heartbeat_packet(self, packet: bytes):
        header = decode_header(packet)
        content = decode_content(packet)

        if header['packet_type'] != self.HEARTBEAT_TYPE:
            raise False
        
        seq = header['sequence']
        self.count += 1
        self.last_seq = seq
        return True