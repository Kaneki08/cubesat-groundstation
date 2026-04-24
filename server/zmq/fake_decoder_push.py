import time
import random
import zmq

UPSTREAM_PUB = "tcp://127.0.0.1:6001"

def build_packet():
    sat_id = 1
    packet_type = random.choice([1, 2, 3])
    sequence = random.randint(0, 65535)
    timestamp = int(time.time())
    # Randomly choose one of several payloads to simulate different telemetry data
    payload_text = random.choice([
        "battery=7.8,rssi=-82,snr=12.1",
        "battery=7.5,rssi=-75,snr=9.8",
        "battery=8.1,rssi=-90,snr=5.2",
    ])
    # Encode payload and build header according to expected format
    payload_bytes = payload_text.encode("utf-8") #.encode("utf-8") to convert string to bytes
    payload_len = len(payload_bytes) # Get byte length of payload, not character count

    # Build header according to expected format
    header = bytearray()
    header.append(sat_id)
    header.append(packet_type)
    header.extend(sequence.to_bytes(2, "big"))
    header.extend(timestamp.to_bytes(4, "big"))
    header.extend(b"$")
    header.append(payload_len)

    return bytes(header) + payload_bytes

def main():
    ctx = zmq.Context.instance()
    pub = ctx.socket(zmq.PUB)
    pub.bind(UPSTREAM_PUB)

    print(f"[FAKE DECODER PUB] bound at {UPSTREAM_PUB}")

    # Give subscriber time to connect
    time.sleep(1)

    while True:
        packet = build_packet()
        pub.send(packet)
        print("[FAKE DECODER PUB] sent packet:", packet.hex())
        time.sleep(1)

if __name__ == "__main__":
    main()