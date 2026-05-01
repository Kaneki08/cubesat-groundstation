'''
DESCRIPTION: GNU Radio files will broadcast output as a ZMQ message. This
script will serve as the listerner that will suibscribe to this ZMQ message
and pull data to the server.
'''
import asyncio
import requests
import zmq
import numpy as np
from enum import IntEnum

class PacketType(IntEnum):
    PACKET_IMU = 1
    PACKET_TC = 2

FASTAPI_URL = "http://127.0.0.1:8000/ingest"
HEADER_SIZE = 10

timeout_ms = 1000

def size_of_packet_type(packet_type):
    if packet_type == PacketType.PACKET_IMU:
        return 20
    elif PacketType == PacketType.PACKET_TC:
        return 8
    return 0


def decode_header(packet):
    if len(packet) < HEADER_SIZE:
        raise ValueError("Packet too short to contain full header")

    if packet[8:9] != b'$':
        raise ValueError("Missing $ marker in header")

    raw_packet_type = packet[1]

    try:
        packet_type = PacketType(raw_packet_type)
    except ValueError:
        packet_type = raw_packet_type  # unknown packet type, keep the number

    return {
        'sat_id': packet[0],
        'packet_type': packet_type,
        'sequence': int.from_bytes(packet[2:4], 'little'),
        'timestamp': int.from_bytes(packet[4:8], 'little'),
        'payload_len': packet[9]
    }

def decode_content(packet_data, packet_type):
    if len(packet_data) != size_of_packet_type(packet_type):
        raise ValueError("Packet wrong size")

    if packet_type == PacketType.PACKET_IMU:
        imu_packet = {
            "gx_dps": int.from_bytes(packet_data[0:2], "little", signed=True),
            "gy_dps": int.from_bytes(packet_data[2:4], "little", signed=True),
            "gz_dps": int.from_bytes(packet_data[4:6], "little", signed=True),

            "ax_mg": int.from_bytes(packet_data[6:8], "little", signed=True),
            "ay_mg": int.from_bytes(packet_data[8:10], "little", signed=True),
            "az_mg": int.from_bytes(packet_data[10:12], "little", signed=True),

            "qi": int.from_bytes(packet_data[12:14], "little", signed=True),
            "qj": int.from_bytes(packet_data[14:16], "little", signed=True),
            "qk": int.from_bytes(packet_data[16:18], "little", signed=True),
            "qr": int.from_bytes(packet_data[18:20], "little", signed=True)
        }
        return imu_packet
    return 0



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
        data = receive_once(sub)
        
        if data is None:
            continue

        try:
            header = decode_header(data)
            content = decode_content(data, header['packet_type'])
            print(header)

            for k, v in content.items():
                print(k, v)

            payload = {
                "header": header,
                "content": content
            }

            try:
                r = requests.post(FASTAPI_URL, json=payload, timeout=5)
            except requests.RequestException as e:
                print(f"Failed to send to FastAPI: {e}")
        except ValueError as e:
            print(f"Failed to decode packet: {e}")

if __name__ == "__main__":
    main()

class HeartbeatMonitor:
    HEARTBEAT_TYPE = 0xAA

    def __init__(self):
        self.count = 0
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